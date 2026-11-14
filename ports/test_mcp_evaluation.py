import ast
import asyncio
import copy
import json
from pathlib import Path
import time
import traceback
from types import SimpleNamespace
import unittest


class ParallelEvaluationTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_tool_requests_get_results_even_if_one_fails(self):
        root = Path(__file__).resolve().parents[1]
        path = root / 'skills/mcp-builder/scripts/evaluation.py'
        if not path.exists():
            path = root / 'reference/skills/mcp-builder/scripts/evaluation.py'
        tree = ast.parse(path.read_text())
        function = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'agent_loop')
        module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), function], type_ignores=[])
        globals_ = dict(asyncio=asyncio, json=json, time=time, traceback=traceback, EVALUATION_PROMPT='fixture')
        exec(compile(ast.fix_missing_locations(module), str(path), 'exec'), globals_)
        responses = [SimpleNamespace(stop_reason='tool_use', content=[
            SimpleNamespace(type='tool_use', name='first', input={}, id='use_1'),
            SimpleNamespace(type='tool_use', name='second', input={}, id='use_2')]),
            SimpleNamespace(stop_reason='end_turn', content=[SimpleNamespace(type='text', text='done')])]
        calls, requests = [], []
        def create(**kwargs):
            requests.append(copy.deepcopy(kwargs['messages']))
            return responses.pop(0)
        async def call_tool(name, args):
            calls.append(name)
            if name == 'first':
                raise RuntimeError('fixture failure')
            return {'ok': True}
        client = SimpleNamespace(messages=SimpleNamespace(create=create))
        result, metrics = await globals_['agent_loop'](client, 'fixture-model', 'fixture', [], SimpleNamespace(call_tool=call_tool))
        self.assertEqual(calls, ['first', 'second'])
        self.assertEqual([r['tool_use_id'] for r in requests[1][-1]['content']], ['use_1', 'use_2'])
        self.assertIn('fixture failure', requests[1][-1]['content'][0]['content'])
        self.assertEqual(result, 'done')
        self.assertEqual(metrics['second']['count'], 1)


if __name__ == '__main__':
    unittest.main()
