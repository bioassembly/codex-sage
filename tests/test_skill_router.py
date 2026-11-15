import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ROUTER_PATH = ROOT / 'ports/route_skills.py'
if not ROUTER_PATH.is_file():
    ROUTER_PATH = ROOT / 'plugins/sage-skill-router/route_skills.py'
SPEC = importlib.util.spec_from_file_location('route_skills', ROUTER_PATH)
route_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(route_skills)


class SkillRoutingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='sage-router-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.catalog = self.root / 'skills-catalog'
        self.catalog.mkdir()
        for name in ('nextflow', 'fair-data', 'pdf-edit'):
            skill = self.catalog / name
            skill.mkdir()
            (skill / 'SKILL.md').write_text(f'# {name}\n')
        self.routing = {
            'version': 1,
            'core': ['agentic-coding'],
            'rules': [
                {
                    'skill': 'nextflow',
                    'category': 'bio',
                    'summary': 'Nextflow workflows',
                    'files': ['*.nf'],
                    'deps': ['nextflow'],
                    'patterns': ['\\bnextflow\\b'],
                    'companions': ['fair-data'],
                },
                {
                    'skill': 'fair-data',
                    'category': 'science',
                    'summary': 'FAIR metadata',
                    'patterns': ['\\bfair data\\b'],
                },
                {
                    'skill': 'pdf-edit',
                    'category': 'docs',
                    'summary': 'PDF editing',
                    'patterns': ['\\bpdf\\b'],
                },
            ],
        }
        (self.catalog / 'routing.json').write_text(json.dumps(self.routing))

    def test_repo_routing_covers_all_public_skills(self):
        config_dir = ROOT / ('reference' if (ROOT / 'reference').is_dir() else 'config')
        skills_dir = ROOT / ('reference/skills' if (ROOT / 'reference/skills').is_dir() else 'skills')
        routing = json.loads((config_dir / 'skill-routing.json').read_text())
        core = routing.get('core', [])
        rule_names = [r['skill'] for r in routing.get('rules', [])]
        actual = {p.parent.name for p in skills_dir.glob('*/SKILL.md')}
        self.assertEqual(len(core), len(set(core)))
        self.assertEqual(len(rule_names), len(set(rule_names)))
        self.assertEqual(set(core) & set(rule_names), set())
        self.assertEqual(set(core) | set(rule_names), actual)

    def test_routes_workspace_companions_and_dedups_per_conversation(self):
        workspace = self.root / 'proj'
        workspace.mkdir()
        (workspace / 'main.nf').write_text('nextflow.enable.dsl=2\n')
        fake_script = self.root / 'plugins/sage-skill-router/route_skills.py'
        fake_script.parent.mkdir(parents=True)
        fake_script.write_text('#!/usr/bin/env python3\n')

        first = route_skills.route_hook(
            {'common': {'workspacePaths': [str(workspace)], 'conversationId': 'conv-1', 'lastUserInput': ''}},
            'antigravity',
            False,
            fake_script,
        )
        msg1 = first['injectSteps'][0]['systemMessage']['systemMessage']
        self.assertIn('nextflow', msg1)
        self.assertIn('fair-data', msg1)
        self.assertIn('[SAGE On-Demand Catalog]', msg1)

        repeat = route_skills.route_hook(
            {'common': {'workspacePaths': [str(workspace)], 'conversationId': 'conv-1', 'lastUserInput': 'check log'}},
            'antigravity',
            True,
            fake_script,
        )
        self.assertEqual(repeat, {})

        second = route_skills.route_hook(
            {'common': {'workspacePaths': [str(workspace)], 'conversationId': 'conv-1', 'lastUserInput': 'redact this pdf'}},
            'antigravity',
            True,
            fake_script,
        )
        msg2 = second['injectSteps'][0]['systemMessage']['systemMessage']
        self.assertIn('pdf-edit', msg2)
        self.assertNotIn('nextflow', msg2)
        self.assertNotIn('[SAGE On-Demand Catalog]', msg2)

    def test_symlinked_antigravity_plugin_resolves_target_catalog(self):
        repo_plugin = self.root / 'repo/plugins/sage-skill-router'
        repo_plugin.mkdir(parents=True)
        real_script = repo_plugin / 'route_skills.py'
        real_script.write_text('#!/usr/bin/env python3\n')
        target_plugins = self.root / 'plugins'
        target_plugins.mkdir(exist_ok=True)
        (target_plugins / 'sage-skill-router').symlink_to(repo_plugin)
        symlinked_script = target_plugins / 'sage-skill-router/route_skills.py'
        out = route_skills.route_hook(
            {'common': {'workspacePaths': [], 'conversationId': 'sym-1', 'lastUserInput': 'redact pdf'}},
            'antigravity',
            False,
            symlinked_script,
        )
        msg = out['injectSteps'][0]['systemMessage']['systemMessage']
        self.assertIn('pdf-edit', msg)

    def test_codex_hook_output_format(self):
        fake_script = self.root / 'sage/route_skills.py'
        fake_script.parent.mkdir(parents=True)
        fake_script.write_text('#!/usr/bin/env python3\n')
        out = route_skills.route_hook(
            {'cwd': str(self.root), 'session_id': 'codex-1', 'hook_event_name': 'SessionStart', 'prompt': 'redact pdf'},
            'codex',
            False,
            fake_script,
        )
        hook_out = out['hookSpecificOutput']
        self.assertEqual(hook_out['hookEventName'], 'SessionStart')
        self.assertIn('pdf-edit', hook_out['additionalContext'])


if __name__ == '__main__':
    unittest.main()
