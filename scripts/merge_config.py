#!/usr/bin/env python3
"""Merge sibling client JSON defaults without replacing user preferences."""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import tempfile


def defaults(template, current):
    if not isinstance(template, dict) or not isinstance(current, dict):
        return copy.deepcopy(current)
    result = copy.deepcopy(template)
    for key, value in current.items():
        result[key] = defaults(result[key], value) if key in result else copy.deepcopy(value)
    return result


def merge(template, current, previous, client, disable_hybrid=False):
    result = defaults(template, current)
    key = 'mcp' if client == 'opencode' else 'mcpServers'
    servers = copy.deepcopy(current.get(key, {}))
    for name, incoming in template.get(key, {}).items():
        old = previous.get(key, {}).get(name)
        live = servers.get(name)
        if live is None:
            servers[name] = copy.deepcopy(incoming)
        elif isinstance(live, dict) and isinstance(old, dict) and all(live.get(k) == old.get(k) for k in ('type', 'command', 'args', 'url')):
            server = {**copy.deepcopy(live), **copy.deepcopy(incoming)}
            server['enabled' if client == 'opencode' else 'disabled'] = live.get(
                'enabled' if client == 'opencode' else 'disabled', client == 'opencode')
            for field in ('enabled', 'disabled'):
                if field in live:
                    server[field] = live[field]
            for field in ('env', 'environment', 'headers'):
                if field in live:
                    server[field] = defaults(incoming.get(field, {}), live[field])
            servers[name] = server
        # A custom registration sharing a template name is not adopted.
    if disable_hybrid and isinstance(servers.get('hybrid-sage'), dict):
        servers['hybrid-sage']['enabled' if client == 'opencode' else 'disabled'] = client != 'opencode'
    result[key] = servers
    if client == 'opencode':
        plugins = []
        for entry in template.get('plugins', []) + current.get('plugins', []) + current.get('plugin', []):
            if isinstance(entry, list) and len(entry) == 2:
                entry = {'package': entry[0], 'options': entry[1]}
            name = entry.get('package', '') if isinstance(entry, dict) else str(entry)
            if name == '@dietrichgebert/ponytail':
                continue  # Original native skill replaces this old unpinned injector.
            if disable_hybrid and re.search(r'(?:^|[/@:])hybrid-sage(?=$|[/@]|\.(?:mjs|cjs|js|ts)(?:$|[?#]))', name):
                continue
            if entry not in plugins:
                plugins.append(entry)
        result.pop('plugin', None)
        result['plugins'] = plugins
    return result


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.sage-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(text)
            os.fchmod(stream.fileno(), 0o600)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def render(value, replacements):
    if isinstance(value, dict):
        return {k: render(v, replacements) for k, v in value.items()}
    if isinstance(value, list):
        return [render(v, replacements) for v in value]
    return replacements.get(value, value) if isinstance(value, str) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=['antigravity', 'opencode'], required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--legacy', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--key')
    parser.add_argument('--base-url')
    parser.add_argument('--disable-hybrid', action='store_true')
    parser.add_argument('--with-rea', action='store_true')
    args = parser.parse_args()
    original = args.target.read_text() if args.target.exists() else None
    current = json.loads(original) if original is not None else {}
    replacements = {'__UNSLOTH_API_KEY__': args.key or 'local-opencode',
                    '__BASE_URL__': args.base_url or 'http://127.0.0.1:8080/v1',
                    '__MEMORY_PATH__': str(args.home / '.config/opencode/memory.json')}
    template = render(json.loads(args.template.read_text().replace('${HOME}', str(args.home))), replacements)
    old_path = args.state if args.state.exists() else args.legacy
    previous = render(json.loads(old_path.read_text().replace('${HOME}', str(args.home))), replacements)
    result = merge(template, current, previous, args.client, args.disable_hybrid)
    if args.client == 'opencode':
        for option, value in (('apiKey', args.key), ('baseURL', args.base_url)):
            if value is not None:
                result.setdefault('provider', {}).setdefault('strata', {}).setdefault('options', {})[option] = value
    if args.with_rea:
        key = 'mcp' if args.client == 'opencode' else 'mcpServers'
        rea = {'command': ['npx', '--yes', 'rea-agents@6.4.0', 'mcp'], 'type': 'local', 'enabled': True,
               'environment': {'REA_MCP_INPUT_SCHEMA_PROFILE': 'compact'}} if args.client == 'opencode' else {
               'command': 'npx', 'args': ['--yes', 'rea-agents@6.4.0', 'mcp'],
               'env': {'REA_MCP_INPUT_SCHEMA_PROFILE': 'compact'}}
        result.setdefault(key, {}).setdefault('rea', rea)
    if (args.target.read_text() if args.target.exists() else None) != original:
        raise ValueError('Client configuration changed while staging; retry with current content')
    atomic_write(args.target, json.dumps(result, indent=2) + '\n')
    # Only public MCP defaults are recorded, not provider keys or arbitrary user data.
    key = 'mcp' if args.client == 'opencode' else 'mcpServers'
    atomic_write(args.state, json.dumps({key: template.get(key, {})}, indent=2) + '\n')
    print('Config JSON valid. User settings and disabled integrations preserved.')


if __name__ == '__main__':
    main()
