import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import harness
import install_rtk


class RtkInstallationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='sage-rtk-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.home = self.root / 'codex "quoted" home'
        self.bin = self.root / 'bin with spaces'
        self.home.mkdir()
        (self.home / 'AGENTS.md').write_text('Personal instructions.\n')
        (self.home / 'config.toml').write_text('model_reasoning_effort = "max"\n')
        (self.home / 'hooks.json').write_text(json.dumps({'hooks': {'SessionStart': [
            {'hooks': [{'type': 'command', 'command': 'personal-hook'}]}]}}))
        self.original = {p.name: p.read_bytes() for p in self.home.iterdir()}
        self.fixture = (f'#!{sys.executable}\n' + '''import json,os,pathlib,sys
if '--version' in sys.argv:
 print('rtk 1.2.0');sys.exit(0)
home=pathlib.Path(os.environ['CODEX_HOME'])
p=home/'hooks.json'
data=json.loads(p.read_text()) if p.exists() else {'hooks':{}}
groups=data['hooks'].setdefault('PreToolUse',[])
if not any(h.get('command')=='rtk hook codex' for g in groups for h in g.get('hooks',[])):
 groups.append({'matcher':'Bash','hooks':[{'type':'command','command':'rtk hook codex'}]})
p.write_text(json.dumps(data))
ref='@'+str(home/'RTK.md')
agents=home/'AGENTS.md'
text=agents.read_text() if agents.exists() else ''
if ref not in text:text+='\\n'+ref+'\\n'
agents.write_text(text)
(home/'RTK.md').write_text('upstream awareness fixture')
''').encode()
        output = patch('sys.stdout', new_callable=io.StringIO)
        output.start()
        self.addCleanup(output.stop)

    def test_install_preserves_personal_hooks_and_config_and_restores(self):
        latest = self.home / 'sage/latest.json'
        latest.parent.mkdir()
        original_manifest = {str(self.home / 'AGENTS.md'): 'old-fingerprint', 'other': 'unchanged'}
        latest.write_text(json.dumps(original_manifest))
        backup = install_rtk.install(self.fixture, self.home, self.bin, '1.2.0')
        hooks = json.loads((self.home / 'hooks.json').read_text())
        self.assertEqual(hooks['hooks']['SessionStart'][0]['hooks'][0]['command'], 'personal-hook')
        self.assertIn(str(self.bin / 'rtk'), hooks['hooks']['PreToolUse'][0]['hooks'][0]['command'])
        self.assertEqual((self.home / 'config.toml').read_bytes(), self.original['config.toml'])
        self.assertTrue((self.home / 'AGENTS.md').read_text().startswith('Personal instructions.'))
        recorded = json.loads(latest.read_text())
        self.assertEqual(recorded['other'], 'unchanged')
        self.assertEqual(recorded[str(self.home / 'AGENTS.md')], harness.fingerprint(harness.snapshot(self.home / 'AGENTS.md')))
        harness.restore(backup)
        self.assertFalse((self.bin / 'rtk').exists())
        self.assertEqual(json.loads(latest.read_text()), original_manifest)
        for name, content in self.original.items():
            self.assertEqual((self.home / name).read_bytes(), content)

    def test_reinstall_has_one_hook_and_reference_and_restores_in_order(self):
        first = install_rtk.install(self.fixture, self.home, self.bin, '1.2.0')
        second = install_rtk.install(self.fixture, self.home, self.bin, '1.2.0')
        hooks = json.loads((self.home / 'hooks.json').read_text())
        self.assertEqual(len(hooks['hooks']['PreToolUse']), 1)
        self.assertEqual((self.home / 'AGENTS.md').read_text().count('@' + str(self.home / 'RTK.md')), 1)
        harness.restore(second)
        harness.restore(first)
        self.assertEqual((self.home / 'AGENTS.md').read_bytes(), self.original['AGENTS.md'])

    def test_wrong_version_or_unowned_binary_leaves_live_files_alone(self):
        with self.assertRaisesRegex(ValueError, 'version differs'):
            install_rtk.install(self.fixture, self.home, self.bin, '999.0.0')
        self.bin.mkdir()
        (self.bin / 'rtk').write_bytes(b'personal tool')
        with self.assertRaisesRegex(ValueError, 'unowned or modified'):
            install_rtk.install(self.fixture, self.home, self.bin, '1.2.0')
        self.assertEqual((self.bin / 'rtk').read_bytes(), b'personal tool')
        for name, content in self.original.items():
            self.assertEqual((self.home / name).read_bytes(), content)

    def test_archive_checksum_and_no_filesystem_extraction(self):
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w:gz') as archive:
            entry = tarfile.TarInfo('../rtk')
            entry.size = 3
            archive.addfile(entry, io.BytesIO(b'bin'))
        data = stream.getvalue()
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            install_rtk.verify_archive(data, '0' * 64)
        self.assertEqual(install_rtk.verify_archive(data, hashlib.sha256(data).hexdigest()), b'bin')


if __name__ == '__main__':
    unittest.main()
