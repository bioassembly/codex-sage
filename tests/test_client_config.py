import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('merge_client', Path(__file__).resolve().parents[1] / 'scripts/merge_config.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ClientConfigTests(unittest.TestCase):
    def test_disabled_pin_update_preserves_preferences_and_private_headers(self):
        old = {'mcp': {'docs': {'type': 'local', 'command': ['npx', 'docs@1'], 'enabled': True}}}
        new = {'model': 'template-model', 'permission': {'bash': 'allow'}, 'mcp': {
            'docs': {'type': 'local', 'command': ['npx', 'docs@2'], 'enabled': True}}}
        current = {'model': 'chosen-model', 'permission': {'bash': 'ask'}, 'mcp': {
            'docs': {'type': 'local', 'command': ['npx', 'docs@1'], 'enabled': False, 'headers': {'Private': 'sentinel'}}}}
        result = module.merge(new, current, old, 'opencode')
        self.assertEqual(result['model'], 'chosen-model')
        self.assertEqual(result['permission']['bash'], 'ask')
        self.assertEqual(result['mcp']['docs']['command'], ['npx', 'docs@2'])
        self.assertFalse(result['mcp']['docs']['enabled'])
        self.assertEqual(result['mcp']['docs']['headers'], {'Private': 'sentinel'})

    def test_custom_server_is_not_adopted_and_hybrid_can_be_disabled(self):
        old = {'mcp': {'docs': {'url': 'https://public.example/mcp'}}}
        current = {'mcp': {'docs': {'command': ['private-docs']}, 'hybrid-sage': {'command': ['python', 'server'], 'enabled': True}},
                   'plugins': ['personal', 'file:///repo/hybrid-sage/plugin.ts', '@dietrichgebert/ponytail',
                               'file:///config/plugins/hybrid-sage.mjs', 'hybrid-sage@1.0.0', 'my-hybrid-sage-tools']}
        result = module.merge(old, current, old, 'opencode', True)
        self.assertEqual(result['mcp']['docs'], {'command': ['private-docs']})
        self.assertFalse(result['mcp']['hybrid-sage']['enabled'])
        self.assertEqual(result['plugins'], ['personal', 'my-hybrid-sage-tools'])

    def test_antigravity_preserves_disabled_and_other_settings(self):
        old = {'mcpServers': {'s': {'command': 'uvx', 'args': ['old']}}}
        new = {'mcpServers': {'s': {'command': 'uvx', 'args': ['new']}}}
        current = {'mcpServers': {'s': {'command': 'uvx', 'args': ['old'], 'disabled': True}}, 'ui': {'custom': True}}
        result = module.merge(new, current, old, 'antigravity')
        self.assertTrue(result['mcpServers']['s']['disabled'])
        self.assertEqual(result['mcpServers']['s']['args'], ['new'])
        self.assertEqual(result['ui'], {'custom': True})

    def test_v1_plugins_migrate_without_losing_options(self):
        result = module.merge({}, {'plugin': [['personal', {'flag': True}]]}, {}, 'opencode')
        self.assertNotIn('plugin', result)
        self.assertEqual(result['plugins'], [{'package': 'personal', 'options': {'flag': True}}])


if __name__ == '__main__':
    unittest.main()
