import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('token_audit', Path(__file__).resolve().parents[1] / 'scripts/token_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def usage(input_tokens, cached=0, output=0, reasoning=0, last=None):
    total = dict(zip(audit.TOKEN_KEYS, (input_tokens, cached, output, reasoning)))
    return {'type': 'event_msg', 'payload': {'type': 'token_count', 'info': {
        'total_token_usage': total, 'last_token_usage': last or total}}}


class TokenAuditTests(unittest.TestCase):
    def summarize(self, events):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'session.jsonl'
            path.write_text('\n'.join(json.dumps(e) for e in events) + '\ninvalid partial line\n')
            return audit.audit_files([path])

    def test_repeated_counters_and_reasoning_are_not_counted_twice(self):
        one = usage(100, 80, 20, 5)
        result = self.summarize([one, one, usage(160, 130, 30, 8)])
        self.assertEqual(result['usage_updates'], 2)
        self.assertEqual(result['input_tokens'], 160)
        self.assertEqual(result['uncached_input_tokens'], 30)
        self.assertEqual(result['output_tokens'], 30)
        self.assertEqual(result['reasoning_output_tokens'], 8)
        self.assertEqual(result['invalid_json_lines'], 1)

    def test_counter_reset_and_inherited_initial_usage(self):
        inherited = usage(1000, 900, 100, 20, last=dict(zip(audit.TOKEN_KEYS, (100, 80, 10, 2))))
        result = self.summarize([inherited, usage(1100, 980, 120, 25), usage(30, 10, 5, 1)])
        self.assertEqual(result['input_tokens'], 230)
        self.assertEqual(result['cached_input_tokens'], 170)
        self.assertEqual(result['output_tokens'], 35)
        self.assertEqual(result['reasoning_output_tokens'], 8)

    def test_tool_size_metrics_do_not_disclose_contents(self):
        secret = 'private-sentinel-' * 3000
        result = self.summarize([
            {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output', 'output': secret}},
            {'type': 'response_item', 'payload': {'type': 'function_call_output', 'output': 'ok'}},
            {'type': 'event_msg', 'payload': {'type': 'token_count', 'info': None}},
            {'type': 'turn_context', 'payload': {'model': 'fixture-model', 'effort': 'max'}},
        ])
        self.assertEqual(result['tool_output_characters'], len(secret) + 2)
        self.assertEqual(result['tool_outputs_over_30000_characters'], 1)
        self.assertNotIn('private-sentinel', json.dumps(result))
        self.assertIsNone(result['cached_input_percent'])


if __name__ == '__main__':
    unittest.main()
