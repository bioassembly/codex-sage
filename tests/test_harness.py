import argparse
import importlib.util
import json
import io
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/harness.py"
spec = importlib.util.spec_from_file_location("harness", SCRIPT)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        output = patch('sys.stdout', new_callable=io.StringIO)
        output.start()
        self.addCleanup(output.stop)
        self.temp = tempfile.TemporaryDirectory(prefix="sage-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.args = argparse.Namespace(codex_home=self.root / "codex",
                                       skills_dir=self.root / "skills",
                                       bin_dir=self.root / "bin", mcp=[],
                                       with_hybrid=None, dry_run=False)
        self.args.codex_home.mkdir()
        self.config = self.args.codex_home / "config.toml"
        self.config.write_text('# Keep this comment\nmodel = "user-selected"\n[features]\napps = true\n')
        self.original = self.config.read_bytes()

    def test_install_preserves_user_config_and_other_skills_then_restores(self):
        self.args.skills_dir.mkdir()
        unrelated = self.args.skills_dir / "my-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("private skill")
        agents = self.args.codex_home / "AGENTS.md"
        agents.write_text("Personal instructions.\n")
        auth = self.args.codex_home / "auth.json"
        auth.write_text('"test auth sentinel"')
        backup = harness.install(self.args)
        config = tomllib.loads(self.config.read_text())
        for key, value in tomllib.loads(self.original.decode()).items():
            self.assertEqual(config[key], value)
        self.assertIn('# Keep this comment', self.config.read_text())
        self.assertEqual(auth.read_text(), '"test auth sentinel"')
        self.assertTrue((self.args.skills_dir / "sage-genomics" / "SKILL.md").is_file())
        self.assertNotIn("mcp_servers", config)
        self.assertNotIn("approval_policy", config)
        self.assertEqual(config['web_search'], 'live')
        self.assertEqual(config['agents']['max_concurrent_threads_per_session'], 3)
        harness.restore(backup)
        self.assertEqual(agents.read_text(), "Personal instructions.\n")
        self.assertFalse((self.args.codex_home / "sage.config.toml").exists())
        self.assertEqual(self.config.read_bytes(), self.original)
        self.assertFalse((self.args.skills_dir / "sage-genomics").is_symlink())
        self.assertEqual((unrelated / "SKILL.md").read_text(), "private skill")

    def test_reinstallation_is_idempotent_and_restorable_in_order(self):
        first = harness.install(self.args)
        agents = self.args.codex_home / "AGENTS.md"
        content = agents.read_bytes()
        second = harness.install(self.args)
        self.assertEqual(agents.read_bytes(), content)
        self.assertEqual(agents.read_text().count(harness.START), 1)
        harness.restore(second)
        harness.restore(first)
        self.assertFalse(agents.exists())

    def test_optional_mcp_and_hybrid_paths_are_valid_toml(self):
        hybrid = self.root / 'hybrid "quoted" path'
        server = hybrid / "plugins/mcp_server.py"
        server.parent.mkdir(parents=True)
        server.write_text("# fixture")
        self.args.with_hybrid = hybrid
        self.args.mcp = ["deepwiki", "context7", "context7", "openai-docs"]
        harness.install(self.args)
        config = tomllib.loads(self.config.read_text())
        self.assertEqual(len(config["mcp_servers"]), 4)
        self.assertEqual(config["mcp_servers"]["hybrid-sage"]["args"], [str(server)])

    def test_restore_preserves_post_install_edits_without_partial_restore(self):
        backup = harness.install(self.args)
        agents = self.args.codex_home / "AGENTS.md"
        agents.write_text(agents.read_text() + "New personal instruction.\n")
        with self.assertRaisesRegex(ValueError, "Changed since installation"):
            harness.restore(backup)
        self.assertEqual(tomllib.loads(self.config.read_text())['web_search'], 'live')
        self.assertIn("New personal instruction", agents.read_text())

    def test_invalid_existing_toml_fails_before_installation(self):
        self.config.write_text("[invalid")
        with self.assertRaises(ValueError):
            harness.install(self.args)
        self.assertFalse(self.args.skills_dir.exists())
        self.assertFalse((self.args.codex_home / "sage").exists())

    def test_real_directory_collision_is_preserved(self):
        collision = self.args.skills_dir / "sage-genomics"
        collision.mkdir(parents=True)
        (collision / "SKILL.md").write_text("User authored")
        with self.assertRaisesRegex(ValueError, "directory"):
            harness.install(self.args)
        self.assertEqual((collision / "SKILL.md").read_text(), "User authored")
        self.assertEqual(self.config.read_bytes(), self.original)

    def test_failed_write_rolls_back_previous_writes(self):
        original_apply = harness.apply_state
        failed = False

        def fail_once(path, state):
            nonlocal failed
            if path.name == "AGENTS.md" and not failed:
                failed = True
                raise OSError("simulated full disk")
            original_apply(path, state)

        with patch.object(harness, "apply_state", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "full disk"):
                harness.install(self.args)
        self.assertEqual(self.config.read_bytes(), self.original)
        self.assertEqual(self.config.read_bytes(), self.original)

    def test_dry_run_creates_no_runtime_files(self):
        self.args.dry_run = True
        harness.install(self.args)
        self.assertEqual(list(self.args.codex_home.iterdir()), [self.config])
        self.assertFalse(self.args.skills_dir.exists())

    def test_retire_only_previously_managed_unchanged_entries(self):
        harness.install(self.args)
        retired = self.args.skills_dir / "old-sage-link"
        retired.symlink_to(harness.REPO / "skills/sage-genomics")
        modified = self.args.skills_dir / "modified-old-link"
        modified.write_text("my replacement")
        latest = self.args.codex_home / "sage/latest.json"
        manifest = json.loads(latest.read_text())
        manifest[str(retired)] = harness.fingerprint(harness.snapshot(retired))
        manifest[str(modified)] = harness.fingerprint({"kind": "absent"})
        latest.write_text(json.dumps(manifest))
        backup = harness.install(self.args)
        self.assertFalse(retired.is_symlink())
        self.assertEqual(modified.read_text(), "my replacement")
        harness.restore(backup)
        self.assertTrue(retired.is_symlink())

    def test_reversed_markers_fail_and_outside_content_survives(self):
        with self.assertRaises(ValueError):
            harness.merge_instructions(harness.END + harness.START, "new")
        current = "prefix\n" + harness.START + "\nold\n" + harness.END + "\nsuffix"
        merged = harness.merge_instructions(current, "new")
        self.assertEqual(merged, "prefix\n" + harness.START + "\nnew\n" + harness.END + "\nsuffix")

    def test_restore_can_resume_after_interruption(self):
        backup = harness.install(self.args)
        original_apply = harness.apply_state
        calls = 0

        def interrupt(path, state):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("interrupted restore")
            original_apply(path, state)

        with patch.object(harness, "apply_state", side_effect=interrupt):
            with self.assertRaises(OSError):
                harness.restore(backup)
        harness.restore(backup)
        harness.restore(backup)  # Already restored is safe too.
        self.assertFalse((self.args.codex_home / "sage.config.toml").exists())

    def test_wrappers_use_installed_custom_paths(self):
        harness.install(self.args)
        fake_bin = self.root / "fake-bin"
        fake_bin.mkdir()
        fake_codex = fake_bin / "codex"
        fake_codex.write_text('#!/bin/sh\nprintf "%s\\n" "$CODEX_HOME" "$@"\n')
        fake_codex.chmod(0o755)
        result = subprocess.run([str(self.args.bin_dir / "codex-sage"), "test argument"],
                                capture_output=True, text=True, check=True,
                                env={**os.environ, "CODEX_HOME": "/wrong/home",
                                     "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"]})
        self.assertEqual(result.stdout.splitlines(), [str(self.args.codex_home), "test argument"])
        result = subprocess.run([str(self.args.bin_dir / "codex-sage-doctor")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Installation intact", result.stdout)

    def test_passive_merge_preserves_complex_user_configuration(self):
        original = '''# User-owned comment
model = "chosen-model"
model_reasoning_effort = "xhigh"
approval_policy = "never"
[agents]
default_subagent_model = "my-worker"
[tui]
status_line = ["model", "context-remaining"]
[plugins."my.plugin"]
enabled = true
[mcp_servers.private_docs]
url = "https://example.com/mcp"
bearer_token_env_var = "MY_DOCS_TOKEN"
[[skills.config]]
name = "disabled-skill"
enabled = false
'''
        self.config.write_text(original)
        harness.install(self.args)
        merged = tomllib.loads(self.config.read_text())
        expected = harness.merge_settings(tomllib.loads(original), {
            'web_search': 'live', 'agents': {'enabled': True, 'max_concurrent_threads_per_session': 3}})
        self.assertEqual(merged, expected)
        self.assertIn('# User-owned comment', self.config.read_text())
        self.assertFalse((self.args.codex_home / 'sage.config.toml').exists())

    def test_doctor_allows_unrelated_user_setting_changes(self):
        harness.install(self.args)
        self.config.write_text(self.config.read_text().replace('user-selected', 'new-user-model'))
        self.args.native = False
        harness.doctor(self.args)

    def test_migration_retires_only_unchanged_owned_profile(self):
        harness.install(self.args)
        legacy = self.args.codex_home / 'sage.config.toml'
        legacy.write_text('web_search = "cached"\n')
        latest = self.args.codex_home / 'sage/latest.json'
        recorded = json.loads(latest.read_text())
        recorded[str(legacy)] = harness.fingerprint(harness.snapshot(legacy))
        latest.write_text(json.dumps(recorded))
        backup = harness.install(self.args)
        self.assertFalse(legacy.exists())
        harness.restore(backup)
        self.assertEqual(legacy.read_text(), 'web_search = "cached"\n')

    def test_native_writer_failure_does_not_change_live_files(self):
        with patch.object(harness, 'stage_config', side_effect=ValueError('native write failed')):
            with self.assertRaisesRegex(ValueError, 'native write failed'):
                harness.install(self.args)
        self.assertEqual(self.config.read_bytes(), self.original)
        self.assertFalse(self.args.skills_dir.exists())

    def test_concurrent_user_config_edit_is_not_overwritten(self):
        def concurrent_edit(current, settings):
            self.config.write_text('model = "edited-during-install"\n')
            return current  # Simulate a user edit while the native writer was staging.

        with patch.object(harness, 'stage_config', side_effect=concurrent_edit):
            with self.assertRaisesRegex(ValueError, 'changed while staging'):
                harness.install(self.args)
        self.assertEqual(self.config.read_text(), 'model = "edited-during-install"\n')
        self.assertFalse(self.args.skills_dir.exists())

    def test_reinstallation_keeps_previously_selected_servers_managed(self):
        self.args.mcp = ['context7']
        harness.install(self.args)
        self.args.mcp = []
        harness.install(self.args)
        desired = json.loads((self.args.codex_home / 'sage/managed-config.json').read_text())
        self.assertEqual(desired['mcp_servers']['context7']['url'], 'https://mcp.context7.com/mcp')
        self.args.native = False
        harness.doctor(self.args)


if __name__ == "__main__":
    unittest.main()
