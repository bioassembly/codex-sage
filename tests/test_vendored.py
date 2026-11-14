import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import harness


class VendoredIntegrityTests(unittest.TestCase):
    def test_modified_or_missing_original_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'skills/original/SKILL.md'
            skill.parent.mkdir(parents=True)
            content = 'Original upstream text.\r\n'.encode()
            skill.write_bytes(content)
            digest = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
            (root / 'third_party').mkdir()
            (root / 'third_party/lock.json').write_text(json.dumps({'skills': [
                {'name': 'original', 'files': {'SKILL.md': digest}}]}))
            with patch.object(harness, 'REPO', root):
                harness.check_vendored()
                skill.write_text('Shortened adaptation.\n')
                with self.assertRaisesRegex(ValueError, 'was modified'):
                    harness.check_vendored()
                skill.unlink()
                with self.assertRaisesRegex(ValueError, 'file list differs'):
                    harness.check_vendored()


if __name__ == '__main__':
    unittest.main()
