#!/usr/bin/env python3
"""Validate pinned upstream files and explicitly recorded compatibility changes."""
import hashlib
import json
from pathlib import Path


def validate(repo: Path, skills: Path) -> list[str]:
    errors = []
    manifest = json.loads((repo / 'third_party/lock.json').read_text())
    for spec in manifest['skills']:
        root = skills / spec['name']
        actual = {str(p.relative_to(root)) for p in root.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts}
        if actual != set(spec['files']) | set(spec.get('aliases', {})):
            errors.append(f"{spec['name']}: pinned file list differs")
            continue
        for name, expected in spec['files'].items():
            data = (root / name).read_bytes()
            digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if digest != spec.get('patches', {}).get(name, expected):
                errors.append(f"{spec['name']}/{name}: unrecorded upstream modification")
        for alias, target in spec.get('aliases', {}).items():
            if (root / alias).read_bytes() != (root / target).read_bytes():
                errors.append(f"{spec['name']}/{alias}: compatibility alias differs")
    return errors


if __name__ == '__main__':
    repo = Path(__file__).resolve().parents[1]
    skills = repo / ('skills' if (repo / 'skills').exists() else 'reference/skills')
    errors = validate(repo, skills)
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Pinned upstream skills and recorded compatibility changes valid.')
