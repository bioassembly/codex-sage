#!/usr/bin/env python3
"""Install shared SAGE capabilities in a native sibling client, with rollback."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import uuid

import client_state as harness
import merge_config


def install(repo, user_home, client, key=None, base_url=None, with_rea=False, disable_hybrid=False, dry_run=False):
    repo, user_home = repo.resolve(), user_home.resolve()
    source = repo / ('reference' if client == 'opencode' else 'config')
    target = user_home / ('.config/opencode' if client == 'opencode' else '.gemini/config')
    config_name = 'opencode.json' if client == 'opencode' else 'mcp_config.json'
    template_name = 'opencode.template.json' if client == 'opencode' else 'mcp_config.json'
    config = target / config_name
    before_config = harness.snapshot(config)
    current = json.loads(config.read_text()) if config.exists() else {}
    replacements = {'__UNSLOTH_API_KEY__': key or 'local-opencode', '__BASE_URL__': base_url or 'http://127.0.0.1:8080/v1',
                    '__MEMORY_PATH__': str(target / 'memory.json')}
    template = merge_config.render(json.loads((source / template_name).read_text().replace('${HOME}', str(user_home))), replacements)
    state = target / 'sage/source-template.json'
    latest = target / 'sage/latest.json'
    previous_files = json.loads(latest.read_text()) if latest.exists() else {}
    previous = json.loads((state if state.exists() else source / 'legacy-mcp.json').read_text().replace('${HOME}', str(user_home)))
    previous = merge_config.render(previous, replacements)
    settings = merge_config.merge(template, current, previous, client, disable_hybrid)
    if client == 'opencode':
        for option, value in (('apiKey', key), ('baseURL', base_url)):
            if value is not None:
                settings.setdefault('provider', {}).setdefault('strata', {}).setdefault('options', {})[option] = value
    if with_rea:
        table = settings.setdefault('mcp' if client == 'opencode' else 'mcpServers', {})
        table.setdefault('rea', {'type': 'local', 'command': ['npx', '--yes', 'rea-agents@6.4.0', 'mcp'], 'enabled': True,
                         'environment': {'REA_MCP_INPUT_SCHEMA_PROFILE': 'compact'}} if client == 'opencode' else {
                         'command': 'npx', 'args': ['--yes', 'rea-agents@6.4.0', 'mcp'], 'env': {'REA_MCP_INPUT_SCHEMA_PROFILE': 'compact'}})
    mcp_key = 'mcp' if client == 'opencode' else 'mcpServers'
    plans = {config: harness.file_state(json.dumps(settings, indent=2) + '\n'),
             state: harness.file_state(json.dumps({mcp_key: template.get(mcp_key, {})}, indent=2) + '\n')}
    global_rules = target / 'AGENTS.md'
    rules = global_rules.read_text() if global_rules.exists() else ''
    legacy = (source / 'legacy-AGENTS.md').read_text()
    if legacy and legacy in rules:
        rules = rules.replace(legacy, '', 1)
    plans[global_rules] = harness.file_state(harness.merge_instructions(rules, (source / 'AGENTS.md').read_text()))

    def add_tree(directory, destination, override=False):
        if destination.is_symlink():
            owned = previous_files.get(str(destination)) == harness.fingerprint(harness.snapshot(destination))
            if destination.resolve() != directory.resolve() and not (override or owned):
                raise ValueError(f'Unowned directory link preserved: {destination}')
            plans[destination] = {'kind': 'symlink', 'target': str(directory)}
        elif not destination.exists():
            plans[destination] = {'kind': 'symlink', 'target': str(directory)}
        elif destination.is_dir():
            for src in directory.rglob('*'):
                if src.is_file():
                    dst = destination / src.relative_to(directory)
                    if any(parent.is_symlink() for parent in dst.parents if parent != destination and destination in parent.parents):
                        raise ValueError(f'Nested personal directory link preserved: {dst}')
                    plans[dst] = harness.snapshot(src)
        else:
            raise ValueError(f'Personal path collision preserved: {destination}')

    skill_source = repo / ('reference/skills' if client == 'opencode' else 'skills')
    selected = {skill.name: (skill, False) for skill in skill_source.iterdir() if (skill / 'SKILL.md').is_file()}
    local = repo / ('reference/skills.local' if client == 'opencode' else 'skills.local')
    if local.exists():
        for skill in local.iterdir():
            if (skill / 'SKILL.md').is_file():
                selected[skill.name] = (skill.resolve(), True)
    for name, (skill, local_override) in sorted(selected.items()):
        add_tree(skill, target / 'skills' / name, override=local_override)
    if client == 'opencode':
        for group, name in (('agents', 'agent'), ('commands', 'command')):
            for src in (source / group).glob('*.md'):
                plans[target / name / src.name] = harness.snapshot(src)
    else:
        for agent in (repo / 'agents').iterdir():
            if agent.is_dir():
                add_tree(agent, target / 'agents' / agent.name)
        settings_path = user_home / '.gemini/antigravity-cli/settings.json'
        personal = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        plans[settings_path] = harness.file_state(json.dumps(merge_config.defaults(
            json.loads((source / 'settings.json').read_text()), personal), indent=2) + '\n')
    if (source / 'shared').exists():
        add_tree(source / 'shared', target / 'shared')
    for path, digest in previous_files.items():
        path = Path(path)
        if not path.is_relative_to(target):
            continue
        if path not in plans and harness.fingerprint(harness.snapshot(path)) == digest:
            plans[path] = {'kind': 'absent'}
    if disable_hybrid:
        for name in ('model-router', 'sage'):
            path = target / 'skills' / name
            if path.is_symlink() and 'hybrid-sage' in str(path.resolve()):
                plans[path] = {'kind': 'absent'}
        if client == 'opencode':
            for directory in ('plugin', 'plugins'):
                for extension in ('mjs', 'cjs', 'js', 'ts'):
                    path = target / directory / ('hybrid-sage.' + extension)
                    if path.exists() or path.is_symlink():
                        plans[path] = {'kind': 'absent'}
        else:
            path = target / 'plugins/hybrid-sage/plugin.json'
            if path.exists() or path.is_symlink():
                plans[path] = {'kind': 'absent'}
    if harness.snapshot(config) != before_config:
        raise ValueError('Client config changed while staging; no files were installed')
    entries = [{'path': str(path), 'before': harness.snapshot(path), 'after': value} for path, value in plans.items()]
    if dry_run:
        print(f'Validated {len(entries)} native {client} entries; dry run made no changes.')
        return None
    entries.append({'path': str(latest), 'before': harness.snapshot(latest), 'after': harness.file_state(json.dumps({
        str(p): harness.fingerprint(value) for p, value in plans.items() if p != config and value['kind'] != 'absent'
    }, indent=2) + '\n')})
    backup = target / 'sage/backups' / f'{uuid.uuid4().hex}.json'
    backup.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    harness.apply_state(backup, harness.file_state(json.dumps({'entries': entries}, indent=2) + '\n'))
    applied = []
    try:
        for entry in entries:
            harness.apply_state(Path(entry['path']), entry['after'])
            applied.append(entry)
    except Exception:
        for entry in reversed(applied):
            harness.apply_state(Path(entry['path']), entry['before'])
        raise
    print(f'Config JSON valid. Installed {client} skills and native configuration; restart the client.')
    print(f'Restore: python3 {shlex.quote(str(repo / "scripts/harness.py"))} restore {shlex.quote(str(backup))}')
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', required=True, choices=['antigravity', 'opencode'])
    parser.add_argument('--home', type=Path, default=Path(os.environ.get('SAGE_USER_HOME', str(Path.home()))))
    parser.add_argument('--key')
    parser.add_argument('--base-url')
    parser.add_argument('--with-rea', action='store_true')
    parser.add_argument('--disable-hybrid', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    subprocess.run(['python3', str(repo / 'scripts/validate-skills.py')], check=True)
    install(repo, args.home, args.client, args.key, args.base_url, args.with_rea, args.disable_hybrid, args.dry_run)


if __name__ == '__main__':
    main()
