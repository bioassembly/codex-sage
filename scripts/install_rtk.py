#!/usr/bin/env python3
"""Install pinned RTK OSS and its upstream Codex hook with a restore journal."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import tarfile
import tempfile
import urllib.request
import uuid

import harness


def release_asset(lock: dict, system: str, machine: str) -> dict:
    targets = {
        ('Linux', 'x86_64'): 'x86_64-unknown-linux-musl',
        ('Linux', 'aarch64'): 'aarch64-unknown-linux-gnu',
        ('Darwin', 'x86_64'): 'x86_64-apple-darwin',
        ('Darwin', 'arm64'): 'aarch64-apple-darwin',
    }
    target = targets.get((system, machine))
    if target is None:
        raise ValueError('Unsupported RTK platform; use the upstream installation instructions')
    return lock['assets'][f'rtk-oss-{target}.tar.gz']


def verify_archive(data: bytes, expected: str) -> bytes:
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('RTK release checksum mismatch; nothing was installed')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        entries = [m for m in archive.getmembers() if m.isfile() and Path(m.name).name == 'rtk']
        if len(entries) != 1:
            raise ValueError('Unexpected RTK archive layout')
        return archive.extractfile(entries[0]).read()


def bytes_state(data: bytes) -> dict:
    import base64
    return {'kind': 'file', 'data': base64.b64encode(data).decode(), 'mode': 0o755}


def install(binary_data: bytes, codex_home: Path, bin_dir: Path, version: str) -> Path:
    codex_home, bin_dir = codex_home.resolve(), bin_dir.resolve()
    targets = [codex_home / name for name in ('AGENTS.md', 'hooks.json', 'RTK.md')]
    latest = codex_home / 'sage/latest.json'
    binary = bin_dir / 'rtk'
    marker = codex_home / 'sage/rtk-install.json'
    paths = [*targets, latest, binary, marker]
    before = {path: harness.snapshot(path) for path in paths}
    if binary.exists() and binary.read_bytes() != binary_data:
        previous = json.loads(marker.read_text()) if marker.exists() else {}
        if previous.get('binary_fingerprint') != harness.fingerprint(before[binary]):
            raise ValueError('An unowned or modified rtk binary exists; preserve it or choose another --bin-dir')

    with tempfile.TemporaryDirectory(prefix='codex-sage-rtk-') as temp:
        root = Path(temp)
        executable = root / 'rtk'
        executable.write_bytes(binary_data)
        executable.chmod(0o755)
        stage_home = root / 'codex'
        stage_home.mkdir()
        for path in targets:
            if path.exists():
                content = path.read_text()
                if path.name == 'AGENTS.md':
                    content = content.replace('@' + str(codex_home / 'RTK.md'), '@' + str(stage_home / 'RTK.md'))
                elif path.name == 'hooks.json':
                    staged_hooks = json.loads(content)
                    for group in staged_hooks.get('hooks', {}).get('PreToolUse', []):
                        for hook in group.get('hooks', []):
                            if shlex.split(hook.get('command', '')) == [str(binary), 'hook', 'codex']:
                                hook['command'] = 'rtk hook codex'
                    content = json.dumps(staged_hooks, indent=2) + '\n'
                (stage_home / path.name).write_text(content)
        env = {**os.environ, 'CODEX_HOME': str(stage_home),
               'XDG_CONFIG_HOME': str(root / 'config'), 'XDG_DATA_HOME': str(root / 'data'),
               'XDG_STATE_HOME': str(root / 'state')}
        result = subprocess.run([str(executable), '--version'], env=env, cwd=root,
                                capture_output=True, text=True, check=True, timeout=15)
        if result.stdout.strip() != f'rtk {version}':
            raise ValueError('Downloaded RTK version differs from the source manifest')
        result = subprocess.run([str(executable), 'init', '-g', '--codex'], env=env, cwd=root,
                                input='', capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError('RTK refused the staged integration: ' + (result.stderr or result.stdout).strip())
        hooks = json.loads((stage_home / 'hooks.json').read_text())
        found = False
        for group in hooks.get('hooks', {}).get('PreToolUse', []):
            for hook in group.get('hooks', []):
                command = hook.get('command', '')
                if shlex.split(command) == ['rtk', 'hook', 'codex']:
                    hook['command'] = shlex.join([str(binary), 'hook', 'codex'])
                    found = True
        if not found:
            raise ValueError('Upstream init did not produce the expected Codex hook')
        plans = {binary: bytes_state(binary_data),
                 codex_home / 'hooks.json': harness.file_state(json.dumps(hooks, indent=2) + '\n'),
                 codex_home / 'RTK.md': harness.file_state((stage_home / 'RTK.md').read_text()),
                 codex_home / 'AGENTS.md': harness.file_state((stage_home / 'AGENTS.md').read_text().replace(
                     '@' + str(stage_home / 'RTK.md'), '@' + str(codex_home / 'RTK.md')))}
    # Keep the existing SAGE diagnostics consistent with this authorized AGENTS update.
    if latest.exists():
        recorded = json.loads(latest.read_text())
        if str(codex_home / 'AGENTS.md') in recorded:
            recorded[str(codex_home / 'AGENTS.md')] = harness.fingerprint(plans[codex_home / 'AGENTS.md'])
            plans[latest] = harness.file_state(json.dumps(recorded, indent=2) + '\n')
    plans[marker] = harness.file_state(json.dumps({
        'version': version, 'edition': 'oss', 'binary': str(binary),
        'binary_fingerprint': harness.fingerprint(plans[binary]),
    }, indent=2) + '\n')
    for path, state in before.items():
        if harness.snapshot(path) != state:
            raise ValueError(f'File changed while staging RTK; installation stopped: {path}')
    entries = [{'path': str(path), 'before': before[path], 'after': state} for path, state in plans.items()]
    backup_dir = codex_home / 'sage/backups'
    backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    backup = backup_dir / f'rtk-{uuid.uuid4().hex}.json'
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
    print(f'Installed RTK OSS {version}: {binary}')
    print('Codex requires review/trust of new hooks through /hooks before automatic rewriting.')
    print('No hook-trust records, model, permission, or authentication settings were changed.')
    print(f'Restore: python3 {shlex.quote(str(harness.REPO / "scripts/harness.py"))} restore {shlex.quote(str(backup))}')
    return backup


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    parser.add_argument('--bin-dir', type=Path, default=Path.home() / '.local/bin')
    args = parser.parse_args()
    lock = json.loads((harness.REPO / 'third_party/lock.json').read_text())['rtk']
    asset = release_asset(lock, platform.system(), platform.machine())
    with urllib.request.urlopen(asset['url'], timeout=60) as response:
        archive = response.read(20 * 1024 * 1024 + 1)
    if len(archive) > 20 * 1024 * 1024:
        raise ValueError('RTK archive exceeded the expected size limit')
    binary_data = verify_archive(archive, asset['sha256'])
    install(binary_data, args.codex_home, args.bin_dir, lock['version'])


if __name__ == '__main__':
    main()
