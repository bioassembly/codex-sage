#!/usr/bin/env python3
"""Route session skills from workspace markers and prompt intent via routing.json."""
from __future__ import annotations

import argparse
from collections import deque
from fnmatch import fnmatch
import json
import os
from pathlib import Path
import re
import sys
import time

IGNORE_DIRS = {'.git', '.hg', 'node_modules', '.venv', 'venv', '__pycache__', 'target', 'dist', 'build', '.next', 'work', '.cache'}
MANIFEST_NAMES = ('package.json', 'pyproject.toml', 'environment.yml', 'environment.yaml', 'Cargo.toml', 'go.mod', 'CMakeLists.txt')


def resolve_catalog_dir(script_path: Path, client: str) -> Path:
    env = os.environ.get('SAGE_ROUTER_CATALOG')
    if env:
        return Path(env)
    script_abs = Path(os.path.abspath(str(script_path)))
    if client == 'antigravity':
        candidate = script_abs.parents[2] / 'skills-catalog'
        if candidate.is_dir():
            return candidate
        return Path(os.environ.get('SAGE_USER_HOME', str(Path.home()))) / '.gemini/config/skills-catalog'
    candidate = script_abs.parents[1] / 'skills-catalog'
    if candidate.is_dir():
        return candidate
    return Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills-catalog'


def load_routing(catalog_dir: Path) -> dict:
    path = catalog_dir / 'routing.json'
    if not path.is_file():
        return {'version': 1, 'core': [], 'rules': []}
    return json.loads(path.read_text())


def collect_workspace_signals(roots: list[Path], max_depth: int = 2, max_entries: int = 400) -> tuple[set[str], set[str], str]:
    files: set[str] = set()
    rel_paths: set[str] = set()
    manifests: list[str] = []
    seen_roots: set[Path] = set()
    seen_count = 0
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if not resolved.is_dir() or resolved in seen_roots:
            continue
        seen_roots.add(resolved)
        stack = deque([(resolved, 0)])
        while stack and seen_count < max_entries:
            directory, depth = stack.popleft()
            try:
                entries = sorted(directory.iterdir(), key=lambda p: p.name)
            except OSError:
                continue
            for entry in entries:
                if seen_count >= max_entries:
                    break
                name = entry.name
                if name in IGNORE_DIRS or (name.startswith('.') and name not in ('.semgrep.yml', '.semgrep.yaml', '.github')):
                    continue
                seen_count += 1
                rel = entry.relative_to(resolved).as_posix()
                rel_paths.add(rel)
                if entry.is_dir():
                    if depth < max_depth:
                        stack.append((entry, depth + 1))
                else:
                    files.add(name)
                    if depth == 0 and (name in MANIFEST_NAMES or (name.startswith('requirements') and name.endswith('.txt'))):
                        try:
                            manifests.append(entry.read_text(errors='ignore')[:16384].lower())
                        except OSError:
                            pass
    return files, rel_paths, '\n'.join(manifests)


def match_workspace(roots: list[Path], rules: list[dict]) -> list[str]:
    files, rel_paths, manifest_text = collect_workspace_signals(roots)
    matched: list[str] = []
    for rule in rules:
        hit = any(fnmatch(name, pat) for pat in rule.get('files', []) for name in files)
        if not hit:
            hit = any(rel == d or rel.startswith(d + '/') for d in rule.get('dirs', []) for rel in rel_paths)
        if not hit and manifest_text:
            hit = any(re.search(r'(?:^|[^a-z0-9_-])' + re.escape(dep.lower()) + r'(?:$|[^a-z0-9_-])', manifest_text)
                      for dep in rule.get('deps', []))
        if hit:
            matched.append(rule['skill'])
    return resolve_companions(matched, rules)


def match_prompt(text: str, rules: list[dict]) -> list[str]:
    if not text.strip():
        return []
    matched = [
        rule['skill']
        for rule in rules
        if any(re.search(pat, text, re.IGNORECASE) for pat in rule.get('patterns', []))
    ]
    return resolve_companions(matched, rules)


def resolve_companions(skills: list[str], rules: list[dict]) -> list[str]:
    by_name = {rule['skill']: rule for rule in rules}
    ordered: list[str] = []
    seen: set[str] = set()
    queue = list(skills)
    while queue:
        name = queue.pop(0)
        if name in seen or name not in by_name:
            continue
        seen.add(name)
        ordered.append(name)
        for companion in by_name[name].get('companions', []):
            if companion not in seen:
                queue.append(companion)
    return ordered


def format_catalog_index(rules: list[dict]) -> str:
    grouped: dict[str, list[str]] = {}
    for rule in rules:
        grouped.setdefault(rule.get('category', 'other'), []).append(rule['skill'])
    return '; '.join(f"{cat}: {', '.join(names)}" for cat, names in grouped.items())


def state_file(target_base: Path, conversation_id: str) -> Path | None:
    if not conversation_id:
        return None
    safe = re.sub(r'[^a-zA-Z0-9._-]', '_', conversation_id)[:80]
    state_dir = target_base / 'sage/router-state'
    state_dir.mkdir(parents=True, exist_ok=True)
    # Keep state dir tiny.
    entries = sorted(state_dir.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    for stale in entries[40:]:
        stale.unlink(missing_ok=True)
    return state_dir / f'{safe}.json'


def save_session_state(path: Path | None, skills: set[str], intro_sent: bool) -> None:
    if not path:
        return
    try:
        path.write_text(json.dumps({'ts': time.time(), 'intro': intro_sent, 'skills': sorted(skills)}))
    except OSError:
        pass


def build_message(matched: list[str], catalog_dir: Path, rules: list[dict], include_intro: bool, client: str) -> str:
    lines: list[str] = []
    if matched:
        lines.append('[SAGE Auto-Skill Router] Auto-selected relevant session skills (read & apply now):')
        by_name = {r['skill']: r for r in rules}
        for name in matched:
            skill_md = catalog_dir / name / 'SKILL.md'
            if skill_md.is_file():
                summary = by_name.get(name, {}).get('summary', '')
                suffix = f' — {summary}' if summary else ''
                lines.append(f'- `{name}`: {skill_md}{suffix}')
    if include_intro and rules:
        acquire_hint = (
            '`skill-acquisition`'
            if client == 'antigravity'
            else 'the local skill installer / `sage-repo-maintenance`'
        )
        lines.append(
            f'[SAGE On-Demand Catalog] Full index under {catalog_dir}/<name>/SKILL.md '
            f'({format_catalog_index(rules)}). Read any matching skill directly when needed. '
            f'If a reusable workflow gap lacks a Core or Catalog skill, automatically run {acquire_hint} '
            'to vet and install one into the local skills overlay before improvising.'
        )
    return '\n'.join(lines)


def route_hook(payload: dict, client: str, prompt_only: bool, script_path: Path) -> dict:
    catalog_dir = resolve_catalog_dir(script_path, client)
    routing = load_routing(catalog_dir)
    rules = routing.get('rules', [])
    target_base = catalog_dir.parent
    common = payload.get('common') or {}
    conv_id = common.get('conversationId') or payload.get('session_id') or payload.get('sessionId') or ''
    sfile = state_file(target_base, conv_id) if conv_id else None
    state_data = {}
    if sfile and sfile.is_file():
        try:
            state_data = json.loads(sfile.read_text())
        except (OSError, json.JSONDecodeError):
            state_data = {}
    fresh_state = time.time() - state_data.get('ts', 0) < 86400
    sent = set(state_data.get('skills', [])) if fresh_state else set()
    intro_sent = bool(state_data.get('intro')) if fresh_state else False

    raw_roots = list(common.get('workspacePaths') or [])
    cwd = common.get('cwd') or payload.get('cwd')
    if cwd:
        raw_roots.append(cwd)
    roots = [Path(p) for p in raw_roots if isinstance(p, str) and p]
    prompt_text = common.get('lastUserInput') or payload.get('prompt') or payload.get('user_prompt') or ''

    selected: list[str] = []
    if (not prompt_only or not sent) and roots:
        selected.extend(match_workspace(roots, rules))
    selected.extend(match_prompt(prompt_text, rules))

    core = set(routing.get('core', []))
    fresh = []
    for name in resolve_companions(selected, rules):
        if name not in core and name not in sent and (catalog_dir / name / 'SKILL.md').is_file():
            fresh.append(name)

    include_intro = not intro_sent
    if not fresh and not include_intro:
        return {}

    text = build_message(fresh, catalog_dir, rules, include_intro, client)
    if not text:
        return {}
    sent.update(fresh)
    save_session_state(sfile, sent, True)

    if client == 'antigravity':
        return {'injectSteps': [{'systemMessage': {'systemMessage': text, 'renderInfo': {'hidden': True}}}]}
    return {'hookSpecificOutput': {'hookEventName': payload.get('hook_event_name', 'SessionStart'), 'additionalContext': text}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=['antigravity', 'codex'], default='antigravity')
    parser.add_argument('--prompt', action='store_true')
    args = parser.parse_args()
    raw = sys.stdin.read().strip()
    payload = json.loads(raw) if raw else {}
    result = route_hook(payload, args.client, args.prompt, Path(__file__))
    if result:
        print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
