#!/usr/bin/env python3
"""Install and inspect SAGE using only Python 3.11+ standard library."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
import uuid

REPO = Path(__file__).resolve().parents[1]
START = "<!-- codex-sage:start -->"
END = "<!-- codex-sage:end -->"


def read_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def snapshot(path: Path) -> dict:
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if path.is_file():
        return {"kind": "file", "data": base64.b64encode(path.read_bytes()).decode(),
                "mode": path.stat().st_mode & 0o777}
    if path.exists():
        raise ValueError(f"Refusing to replace a directory or special file: {path}")
    return {"kind": "absent"}


def file_state(text: str, mode: int = 0o600) -> dict:
    return {"kind": "file", "data": base64.b64encode(text.encode()).decode(), "mode": mode}


def fingerprint(state: dict) -> str:
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


def apply_state(path: Path, state: dict) -> None:
    if state["kind"] == "absent":
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".sage-", dir=path.parent)
    staged = Path(tmp)
    try:
        with os.fdopen(fd, "wb") as stream:
            if state["kind"] == "file":
                stream.write(base64.b64decode(state["data"]))
                os.fchmod(stream.fileno(), state["mode"])
        if state["kind"] == "symlink":
            staged.unlink()
            staged.symlink_to(state["target"])
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def merge_instructions(current: str, instructions: str) -> str:
    block = START + "\n" + instructions.rstrip() + "\n" + END
    if START in current or END in current:
        if current.count(START) != 1 or current.count(END) != 1:
            raise ValueError("Malformed SAGE markers in global AGENTS.md")
        a, b = current.index(START), current.index(END)
        if a > b:
            raise ValueError("Reversed SAGE markers in global AGENTS.md")
        return current[:a] + block + current[b + len(END):]
    return current + ("\n\n" if current and not current.endswith("\n\n") else "") + block + "\n"


def check() -> None:
    for path in sorted(REPO.rglob("*.toml")):
        read_toml(path)
    for path in sorted((REPO / "agents").glob("*.toml")):
        data = read_toml(path)
        if data.get("name") != path.stem or not all(data.get(k) for k in ("description", "developer_instructions")):
            raise ValueError(f"Invalid agent: {path}")
        # These would not enforce isolation in current Codex custom agent files.
        if {"sandbox_mode", "approval_policy", "mcp_servers", "model_provider"} & data.keys():
            raise ValueError(f"Unsupported per-agent permission/provider override: {path}")
    for path in sorted((REPO / "skills").glob("*/SKILL.md")):
        text = path.read_text()
        front = text.split("---", 2)
        if len(front) != 3 or not re.search(rf"^name: {re.escape(path.parent.name)}$", front[1], re.M):
            raise ValueError(f"Invalid skill name/frontmatter: {path}")
        if not re.search(r"^description: .+", front[1], re.M):
            raise ValueError(f"Missing skill description: {path}")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in target and not target.startswith("#"):
                if not (path.parent / target.split("#")[0]).exists():
                    raise ValueError(f"Broken skill reference in {path}: {target}")
    print("Harness TOML, agents, and skill references valid.")


def install(args: argparse.Namespace) -> Path | None:
    check()
    codex_home = args.codex_home.resolve()
    config = codex_home / "config.toml"
    if config.exists():
        read_toml(config)  # Fail before mutation if existing config is malformed.
    profile = (REPO / "config/sage.config.toml").read_text()
    for name in sorted(set(args.mcp)):
        profile += "\n" + (REPO / "config/mcp" / f"{name}.toml").read_text()
    if args.with_hybrid:
        server = args.with_hybrid.resolve() / "plugins/mcp_server.py"
        if not server.is_file():
            raise ValueError(f"Hybrid SAGE server missing: {server}")
        # JSON quoted strings are also valid TOML basic strings.
        profile += '\n[mcp_servers.hybrid-sage]\ncommand = "python3"\nargs = [' + json.dumps(str(server)) + ']\n'
    tomllib.loads(profile)
    global_agents = codex_home / "AGENTS.md"
    current = global_agents.read_text() if global_agents.exists() else ""
    plans = {
        codex_home / "sage.config.toml": file_state(profile),
        global_agents: file_state(merge_instructions(current, (REPO / "config/AGENTS.md").read_text())),
    }
    for skill in sorted((REPO / "skills").iterdir()):
        if (skill / "SKILL.md").is_file():
            plans[args.skills_dir.resolve() / skill.name] = {"kind": "symlink", "target": str(skill)}
    for agent in sorted((REPO / "agents").glob("*.toml")):
        plans[codex_home / "agents" / agent.name] = file_state(agent.read_text())
    wrapper = '#!/usr/bin/env bash\nset -euo pipefail\nexport CODEX_HOME=' + shlex.quote(str(codex_home)) + '\nexec codex --profile sage "$@"\n'
    plans[args.bin_dir.resolve() / "codex-sage"] = file_state(wrapper, 0o755)
    doctor = ('#!/usr/bin/env bash\nset -euo pipefail\nexec python3 '
              + shlex.quote(str(REPO / "scripts/harness.py")) + ' doctor --codex-home '
              + shlex.quote(str(codex_home)) + ' --skills-dir '
              + shlex.quote(str(args.skills_dir.resolve())) + ' "$@"\n')
    plans[args.bin_dir.resolve() / "codex-sage-doctor"] = file_state(doctor, 0o755)
    # Retire only unchanged entries recorded by this installer, never other skills.
    latest = codex_home / "sage/latest.json"
    previous = json.loads(latest.read_text()) if latest.exists() else {}
    for name, installed_hash in previous.items():
        path = Path(name)
        if path not in plans and fingerprint(snapshot(path)) == installed_hash:
            plans[path] = {"kind": "absent"}
    entries = [{"path": str(p), "before": snapshot(p), "after": state} for p, state in plans.items()]
    if args.dry_run:
        for entry in entries:
            print(f"Would install: {entry['path']}")
        return None
    # Save the journal before any installed file changes. No auth files are read.
    entries.append({"path": str(latest), "before": snapshot(latest), "after": file_state(json.dumps({
        str(p): fingerprint(state) for p, state in plans.items() if state["kind"] != "absent"
    }, indent=2) + "\n")})
    backup_dir = codex_home / "sage/backups"
    backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    backup = backup_dir / f"{uuid.uuid4().hex}.json"
    apply_state(backup, file_state(json.dumps({"entries": entries}, indent=2) + "\n"))
    applied = []
    try:
        for entry in entries:
            apply_state(Path(entry["path"]), entry["after"])
            applied.append(entry)
    except Exception:
        for entry in reversed(applied):
            apply_state(Path(entry["path"]), entry["before"])
        raise
    print(f"Installed {len(plans)} entries. Restart Codex to discover skills and agents.")
    print("Launch profile: codex --profile sage (or codex-sage)")
    print(f"Restore: python3 {shlex.quote(str(REPO / 'scripts/harness.py'))} restore {shlex.quote(str(backup))}")
    return backup


def restore(backup: Path) -> None:
    entries = json.loads(backup.read_text())["entries"]
    # Check all destinations first so conflicts leave the whole installation alone.
    for entry in entries:
        if snapshot(Path(entry["path"])) not in (entry["after"], entry["before"]):
            raise ValueError(f"Changed since installation; preserve edits before restoring: {entry['path']}")
    for entry in reversed(entries):
        if snapshot(Path(entry["path"])) != entry["before"]:
            apply_state(Path(entry["path"]), entry["before"])
    print(f"Restored installation snapshot: {backup}")


def doctor(args: argparse.Namespace) -> None:
    check()
    home = args.codex_home.resolve()
    profile = read_toml(home / "sage.config.toml")
    if (home / "config.toml").exists():
        read_toml(home / "config.toml")
    latest = json.loads((home / "sage/latest.json").read_text())
    drift = [p for p, digest in latest.items() if fingerprint(snapshot(Path(p))) != digest]
    if drift:
        raise ValueError("Installed entries changed or missing: " + ", ".join(drift))
    for path in args.skills_dir.resolve().glob("sage-*"):
        if path.is_symlink() and not path.exists():
            raise ValueError(f"Broken skill link: {path}")
    if (home / "AGENTS.override.md").exists():
        print("Notice: AGENTS.override.md takes precedence over the installed global AGENTS.md.")
    print(f"Installation intact. Profile MCP servers: {', '.join(profile.get('mcp_servers', {})) or 'none'}")
    if args.native:
        binary = shutil.which("codex")
        if not binary:
            raise ValueError("Codex CLI not found on PATH")
        result = subprocess.run([binary, "--profile", "sage", "mcp", "list", "--json"],
                                env={**os.environ, "CODEX_HOME": str(home)}, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError("Native config validation failed; run codex --profile sage mcp list")
        print("Installed Codex loaded the profile and MCP configuration.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Validate repository assets without installing")
    for name in ("install", "doctor"):
        command = sub.add_parser(name)
        command.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
        command.add_argument("--skills-dir", type=Path, default=Path.home() / ".agents/skills")
        if name == "install":
            command.add_argument("--bin-dir", type=Path, default=Path.home() / ".local/bin")
            command.add_argument("--mcp", action="append", choices=["context7", "deepwiki", "openai-docs"], default=[])
            command.add_argument("--with-hybrid", type=Path, metavar="REPO", help="Register a local hybrid-sage checkout")
            command.add_argument("--dry-run", action="store_true")
        else:
            command.add_argument("--native", action="store_true", help="Also ask installed Codex to validate the profile")
    sub.add_parser("restore").add_argument("backup", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "install":
            install(args)
        elif args.command == "restore":
            restore(args.backup)
        elif args.command == "doctor":
            doctor(args)
        else:
            check()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
