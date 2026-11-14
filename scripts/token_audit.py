#!/usr/bin/env python3
"""Summarize local Codex usage counters; never print transcript contents."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path

TOKEN_KEYS = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')


def audit_files(paths: list[Path]) -> dict:
    totals = Counter()
    models, efforts = Counter(), Counter()
    updates = compactions = invalid_lines = tool_chars = large_outputs = max_input = 0
    for path in paths:
        previous = None
        with path.open() as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except ValueError:
                    invalid_lines += 1
                    continue
                if not isinstance(event, dict):
                    invalid_lines += 1
                    continue
                payload = event.get('payload', {})
                if not isinstance(payload, dict):
                    continue
                kind = event.get('type')
                if kind == 'turn_context':
                    if payload.get('model'):
                        models[str(payload['model'])] += 1
                    if payload.get('effort'):
                        efforts[str(payload['effort'])] += 1
                elif kind == 'compacted':
                    compactions += 1
                elif kind == 'response_item' and payload.get('type') in (
                        'function_call_output', 'custom_tool_call_output'):
                    output = payload.get('output', '')
                    size = len(output) if isinstance(output, str) else len(json.dumps(output))
                    tool_chars += size
                    large_outputs += size > 30000
                elif kind == 'event_msg' and payload.get('type') == 'token_count':
                    info = payload.get('info') or {}
                    current = info.get('total_token_usage')
                    if not isinstance(current, dict) or current == previous:
                        continue  # Rate-limit notifications may repeat the same totals.
                    last = info.get('last_token_usage') or {}
                    if previous is None:
                        # Forks/resumes may start with an inherited cumulative total.
                        delta = last or current
                    elif any(current.get(k, 0) < previous.get(k, 0) for k in TOKEN_KEYS):
                        delta = current  # A new counter epoch after a reset.
                    else:
                        delta = {k: current.get(k, 0) - previous.get(k, 0) for k in TOKEN_KEYS}
                    totals.update({k: delta.get(k, 0) for k in TOKEN_KEYS})
                    max_input = max(max_input, last.get('input_tokens', 0))
                    updates += 1
                    previous = current
    return {
        'sessions': len(paths), 'usage_updates': updates,
        **{k: totals[k] for k in TOKEN_KEYS},
        'uncached_input_tokens': max(0, totals['input_tokens'] - totals['cached_input_tokens']),
        'cached_input_percent': round(100 * totals['cached_input_tokens'] / totals['input_tokens'], 2)
        if totals['input_tokens'] else None,
        'reasoning_share_of_output_percent': round(100 * totals['reasoning_output_tokens'] / totals['output_tokens'], 2)
        if totals['output_tokens'] else None,
        'max_request_input_tokens': max_input, 'compactions': compactions,
        'tool_output_characters': tool_chars, 'tool_outputs_over_30000_characters': large_outputs,
        'invalid_json_lines': invalid_lines,
        'model_turn_contexts': dict(models), 'effort_turn_contexts': dict(efforts),
        'note': 'Recorded counters, not billing or a subscription-quota calculation. '
                'Output may include reasoning; do not add reasoning to output again. '
                'Forked histories and incomplete logs can overlap or omit usage.',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    parser.add_argument('--sessions-dir', type=Path, default=home / 'sessions')
    parser.add_argument('--limit', type=int, default=20, help='Most recent session logs; 0 means all')
    args = parser.parse_args()
    if args.limit < 0:
        parser.error('--limit must be nonnegative')
    paths = sorted(args.sessions_dir.rglob('*.jsonl'), key=lambda p: p.stat().st_mtime, reverse=True)
    if args.limit:
        paths = paths[:args.limit]
    if not paths:
        parser.error('No session logs found')
    print(json.dumps(audit_files(paths), indent=2))


if __name__ == '__main__':
    main()
