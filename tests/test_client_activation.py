import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'ports'))
path = ROOT / 'scripts/install_client.py'
if not path.exists():
    path = ROOT / 'ports/install_client.py'
spec = importlib.util.spec_from_file_location('client_install', path)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class ClientActivationTests(unittest.TestCase):
    def setUp(self):
        capture = patch('sys.stdout', new_callable=io.StringIO)
        capture.start()
        self.addCleanup(capture.stop)
        temp = tempfile.TemporaryDirectory(prefix='sage-client-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def prepare(self, client):
        repo = self.root / client
        source = repo / ('reference' if client == 'opencode' else 'config')
        source.mkdir(parents=True)
        skills = source / 'skills' if client == 'opencode' else repo / 'skills'
        (skills / 'example').mkdir(parents=True)
        (skills / 'example/SKILL.md').write_text('new public skill')
        for group in (('agents', 'commands') if client == 'opencode' else ()):
            (source / group).mkdir()
        if client == 'antigravity':
            (repo / 'agents').mkdir()
            (source / 'settings.json').write_text('{}')
        (source / 'AGENTS.md').write_text('New shared rules.\n')
        (source / 'legacy-AGENTS.md').write_text('Old shared rules.\n')
        key = 'mcp' if client == 'opencode' else 'mcpServers'
        old = {key: {'docs': {'command': ['docs@1'], 'enabled': True}, 'hybrid-sage': {'command': ['hybrid'], 'enabled': True}}}
        new = {key: {'docs': {'command': ['docs@2'], 'enabled': True}}, 'model': 'default-model'}
        (source / 'legacy-mcp.json').write_text(json.dumps(old))
        (source / ('opencode.template.json' if client == 'opencode' else 'mcp_config.json')).write_text(json.dumps(new))
        home = self.root / (client + '-home')
        target = home / ('.config/opencode' if client == 'opencode' else '.gemini/config')
        target.mkdir(parents=True)
        config = target / ('opencode.json' if client == 'opencode' else 'mcp_config.json')
        personal = {**old, 'model': 'chosen-model', 'provider': {'private': {'key': 'test-sentinel'}}}
        config.write_text(json.dumps(personal))
        (target / 'AGENTS.md').write_text('Personal note.\nOld shared rules.\n')
        (target / 'skills/example').mkdir(parents=True)
        (target / 'skills/example/SKILL.md').write_text('old public skill')
        (target / 'skills/example/private-note.md').write_text('personal')
        return repo, home, target, config

    def test_both_clients_preserve_user_data_disable_hybrid_and_restore(self):
        for client in ('antigravity', 'opencode'):
            with self.subTest(client=client):
                repo, home, target, config = self.prepare(client)
                original = config.read_bytes()
                journal = installer.install(repo, home, client, disable_hybrid=True)
                actual = json.loads(config.read_text())
                key = 'mcp' if client == 'opencode' else 'mcpServers'
                self.assertEqual(actual['model'], 'chosen-model')
                self.assertEqual(actual['provider']['private']['key'], 'test-sentinel')
                self.assertEqual(actual[key]['docs']['command'], ['docs@2'])
                if client == 'opencode':self.assertFalse(actual[key]['hybrid-sage']['enabled'])
                else:self.assertTrue(actual[key]['hybrid-sage']['disabled'])
                self.assertIn('Personal note.', (target / 'AGENTS.md').read_text())
                self.assertNotIn('Old shared rules.', (target / 'AGENTS.md').read_text())
                self.assertEqual((target / 'skills/example/private-note.md').read_text(), 'personal')
                installer.harness.restore(journal)
                self.assertEqual(config.read_bytes(), original)
                self.assertEqual((target / 'skills/example/SKILL.md').read_text(), 'old public skill')

    def test_reinstall_and_dry_run_preserve_personal_skill_trees(self):
        repo, home, target, config = self.prepare('opencode')
        before = config.read_bytes()
        self.assertIsNone(installer.install(repo, home, 'opencode', dry_run=True))
        self.assertEqual(config.read_bytes(), before)
        self.assertFalse((target / 'sage').exists())
        first = installer.install(repo, home, 'opencode')
        content = (target / 'AGENTS.md').read_text()
        second = installer.install(repo, home, 'opencode')
        self.assertEqual((target / 'AGENTS.md').read_text(), content)
        installer.harness.restore(second)
        installer.harness.restore(first)

    def test_machine_local_override_survives_reinstall(self):
        repo, home, target, config = self.prepare('opencode')
        # Fresh target: original installers also support local overrides by name.
        import shutil
        shutil.rmtree(target / 'skills/example')
        local = repo / 'reference/skills.local/example'
        local.mkdir(parents=True)
        (local / 'SKILL.md').write_text('private local skill')
        first = installer.install(repo, home, 'opencode')
        second = installer.install(repo, home, 'opencode')
        self.assertEqual((target / 'skills/example').resolve(), local.resolve())
        installer.harness.restore(second)
        installer.harness.restore(first)

    def test_disable_retires_only_hybrid_autoload_plugins_and_restores_them(self):
        for client in ('antigravity', 'opencode'):
            repo, home, target, config = self.prepare(client)
            path = target / ('plugins/hybrid-sage.mjs' if client == 'opencode' else 'plugins/hybrid-sage/plugin.json')
            path.parent.mkdir(parents=True)
            path.write_text('managed hybrid fixture')
            personal = target / 'plugins/personal.mjs'
            personal.parent.mkdir(parents=True, exist_ok=True)
            personal.write_text('personal plugin')
            journal = installer.install(repo, home, client, disable_hybrid=True)
            self.assertFalse(path.exists())
            self.assertTrue(personal.exists())
            installer.harness.restore(journal)
            self.assertEqual(path.read_text(), 'managed hybrid fixture')


if __name__ == '__main__':
    unittest.main()
