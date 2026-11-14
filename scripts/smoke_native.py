#!/usr/bin/env python3
"""Exercise installation, native parsing/discovery, and restore without a model call."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import harness


def main():
    binary = shutil.which("codex")
    if not binary:
        raise SystemExit("Codex CLI is required for the native smoke test")
    with tempfile.TemporaryDirectory(prefix="codex-sage-smoke-") as temp:
        root = Path(temp)
        args = argparse.Namespace(codex_home=root / "codex", skills_dir=root / ".agents/skills",
                                  bin_dir=root / "bin", mcp=list(harness.mcp_templates()),
                                  with_hybrid=None, disable_mcp=['hybrid-sage'], dry_run=False, native=True)
        backup = harness.install(args)
        try:
            harness.doctor(args)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            env = {**os.environ, "CODEX_HOME": str(args.codex_home)}
            command = [binary, "debug", "prompt-input"]
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr)
            json.loads(result.stdout)
            assert "sage-genomics" in result.stdout, "Native skill discovery failed"
            for name in ('ponytail', 'grill-me', 'sage-mcp-builder', 'sage-token-efficiency'):
                assert name in result.stdout, f"Native skill discovery failed: {name}"
            assert "sage-reviewer" in result.stdout, "Native custom agent discovery failed"
            print("Ordinary Codex discovered the installed skills and custom agents without a profile.")
            result = subprocess.run([binary, "app-server", "--strict-config", "--print-startup-config"],
                                    env=env,
                                    capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr)
            json.loads(result.stdout)
            print("Native Codex accepted the passive configuration with strict validation.")
        finally:
            harness.restore(backup)
    print("Native smoke test passed; no model requests were made.")


if __name__ == "__main__":
    main()
