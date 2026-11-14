#!/usr/bin/env python3
"""Install and inspect SAGE using only Python 3.11+ standard library."""
from __future__ import annotations

import argparse
import asyncio
import base64
import copy
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


def merge_settings(current: dict, additions: dict) -> dict:
    if not isinstance(current, dict):
        raise ValueError("An existing scalar conflicts with a SAGE configuration table")
    merged = copy.deepcopy(current)
    for key, value in additions.items():
        if isinstance(value, dict):
            merged[key] = merge_settings(merged.get(key, {}), value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def respect_user_choices(settings: dict, current: dict) -> dict:
    """Defaults and MCP on/off switches never override explicit user choices."""
    result = copy.deepcopy(settings)

    def preserve(target: dict, defaults: dict, live: dict) -> None:
        for key, value in defaults.items():
            if key not in live:
                continue
            if isinstance(value, dict):
                if isinstance(live[key], dict) and isinstance(target.get(key), dict):
                    preserve(target[key], value, live[key])
            else:
                target[key] = copy.deepcopy(live[key])

    preserve(result, read_toml(REPO / 'config/defaults.toml'), current)
    for name, server in result.get('mcp_servers', {}).items():
        live = current.get('mcp_servers', {}).get(name)
        if isinstance(live, dict) and ('enabled' in live or 'enabled' in server):
            server['enabled'] = live.get('enabled', True)
    return result


def mcp_templates() -> dict:
    return {path.stem: read_toml(path) for path in sorted((REPO / 'config/mcp').glob('*.toml'))}


def stage_config(current: str, settings: dict) -> str:
    """Use Codex's native TOML writer in isolation, before changing live files."""
    binary = shutil.which("codex")
    if not binary:
        raise ValueError("Codex CLI 0.169+ is required to merge configuration safely")
    edits = []

    def flatten(values: dict, prefix: str = "") -> None:
        for key, value in values.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flatten(value, path)
            else:
                edits.append({"keyPath": path, "value": value, "mergeStrategy": "replace"})

    flatten(settings)
    expected = merge_settings(tomllib.loads(current), settings)

    async def write(staged: Path) -> None:
        proc = await asyncio.create_subprocess_exec(
            binary, "app-server", "--stdio", cwd=staged.parent,
            env={**os.environ, "CODEX_HOME": str(staged.parent)},
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL)

        async def request(identifier: int, method: str, params: dict) -> None:
            proc.stdin.write((json.dumps({"id": identifier, "method": method, "params": params}) + "\n").encode())
            await proc.stdin.drain()
            while True:
                line = await proc.stdout.readline()
                if not line:
                    raise ValueError("Codex config writer exited before returning a result")
                result = json.loads(line)
                if result.get("id") == identifier:
                    if "error" in result:
                        raise ValueError("Codex rejected the staged configuration update")
                    return

        try:
            await asyncio.wait_for(request(1, "initialize", {
                "clientInfo": {"name": "codex-sage-installer", "version": "1"}}), timeout=30)
            await asyncio.wait_for(request(2, "config/batchWrite", {
                "filePath": str(staged), "edits": edits, "reloadUserConfig": False}), timeout=30)
        finally:
            proc.stdin.close()
            try:
                await asyncio.wait_for(proc.wait(), timeout=3)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()

    with tempfile.TemporaryDirectory(prefix="codex-sage-config-") as temp:
        staged = Path(temp) / "config.toml"
        staged.write_text(current)
        try:
            asyncio.run(write(staged))
        except TimeoutError as error:
            raise ValueError("Codex's native config writer timed out; live configuration was not changed") from error
        output = staged.read_text()
    if tomllib.loads(output) != expected:
        raise ValueError("Native config merge changed an unrelated setting; installation stopped")
    return output


def check() -> None:
    for path in sorted(REPO.rglob("*.toml")):
        read_toml(path)
    sources = json.loads((REPO / 'sources.lock.json').read_text())
    for source in sources['sources']:
        if not re.fullmatch(r'[0-9a-f]{40}', source['revision']):
            raise ValueError(f"Invalid reviewed source revision: {source['repository']}")
    package_args = {arg for template in mcp_templates().values()
                    for server in template['mcp_servers'].values() for arg in server.get('args', [])}
    for package, version in sources['mcp_packages'].items():
        if not {f'{package}@{version}', f'{package}=={version}'} & package_args:
            raise ValueError(f"MCP package pin differs from sources.lock.json: {package}")
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
    config_before = snapshot(config)
    live_config = read_toml(config) if config.exists() else {}
    managed_path = codex_home / "sage/managed-config.json"
    settings = json.loads(managed_path.read_text()) if managed_path.exists() else {}
    selected = set(args.mcp)
    templates = mcp_templates()
    # Refresh previously selected templates on update, while honoring live toggles.
    for name, template in templates.items():
        managed_servers = settings.get('mcp_servers', {})
        if any({'url', 'command'} & managed_servers.get(server_id, {}).keys()
               for server_id in template['mcp_servers']):
            selected.add(name)
    settings = merge_settings(settings, read_toml(REPO / 'config/defaults.toml'))
    for name in sorted(selected):
        template = copy.deepcopy(templates[name])
        if name == 'memory':
            template['mcp_servers']['memory']['env']['MEMORY_FILE_PATH'] = str(codex_home / 'sage/memory.json')
        settings = merge_settings(settings, template)
    if args.with_hybrid:
        server = args.with_hybrid.resolve() / "plugins/mcp_server.py"
        if not server.is_file():
            raise ValueError(f"Hybrid SAGE server missing: {server}")
        settings = merge_settings(settings, {'mcp_servers': {'hybrid-sage': {
            'command': sys.executable, 'args': [str(server)]}}})
    settings = respect_user_choices(settings, live_config)
    for name in getattr(args, 'disable_mcp', []):
        server_id = next(iter(templates[name]['mcp_servers'])) if name in templates else name
        if server_id in settings.get('mcp_servers', {}) or server_id in live_config.get('mcp_servers', {}):
            settings.setdefault('mcp_servers', {}).setdefault(server_id, {})['enabled'] = False
    global_agents = codex_home / "AGENTS.md"
    current = global_agents.read_text() if global_agents.exists() else ""
    plans = {
        config: file_state(stage_config(config.read_text() if config.exists() else "", settings)),
        codex_home / "sage/managed-config.json": file_state(json.dumps(settings, indent=2) + "\n"),
        global_agents: file_state(merge_instructions(current, (REPO / "config/AGENTS.md").read_text())),
    }
    for skill in sorted((REPO / "skills").iterdir()):
        if (skill / "SKILL.md").is_file():
            plans[args.skills_dir.resolve() / skill.name] = {"kind": "symlink", "target": str(skill)}
    hybrid_state = settings.get('mcp_servers', {}).get('hybrid-sage',
                        live_config.get('mcp_servers', {}).get('hybrid-sage'))
    hybrid_enabled = hybrid_state is not None and hybrid_state.get('enabled', True)
    if args.with_hybrid and hybrid_enabled:
        for name in ('model-router', 'sage'):
            skill = args.with_hybrid.resolve() / 'skills' / name
            if not (skill / 'SKILL.md').is_file():
                raise ValueError(f"Hybrid SAGE skill missing; update the checkout: {skill}")
            plans[args.skills_dir.resolve() / name] = {'kind': 'symlink', 'target': str(skill)}
    for agent in sorted((REPO / "agents").glob("*.toml")):
        plans[codex_home / "agents" / agent.name] = file_state(agent.read_text())
    wrapper = '#!/usr/bin/env bash\nset -euo pipefail\nexport CODEX_HOME=' + shlex.quote(str(codex_home)) + '\nexec codex "$@"\n'
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
        if (hybrid_enabled and path.parent == args.skills_dir.resolve()
                and path.name in ('sage', 'model-router') and path not in plans
                and fingerprint(snapshot(path)) == installed_hash):
            plans[path] = snapshot(path)
        if path not in plans and fingerprint(snapshot(path)) == installed_hash:
            plans[path] = {"kind": "absent"}
    if snapshot(config) != config_before:
        raise ValueError("config.toml changed while staging; retry with the updated configuration")
    entries = [{"path": str(p), "before": snapshot(p), "after": state} for p, state in plans.items()]
    if args.dry_run:
        for entry in entries:
            action = 'remove' if entry['after']['kind'] == 'absent' else 'install'
            print(f"Would {action}: {entry['path']}")
        return None
    # Save the journal before any installed file changes. No auth files are read.
    entries.append({"path": str(latest), "before": snapshot(latest), "after": file_state(json.dumps({
        str(p): fingerprint(state) for p, state in plans.items() if state["kind"] != "absent" and p != config
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
    print("SAGE loads automatically on ordinary Codex launches. Restart Codex; no wrapper or profile is required.")
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
    config = read_toml(home / "config.toml")
    managed = json.loads((home / "sage/managed-config.json").read_text())
    if merge_settings(config, respect_user_choices(managed, config)) != config:
        raise ValueError("SAGE settings changed in config.toml; review the passive configuration")
    latest = json.loads((home / "sage/latest.json").read_text())
    drift = [p for p, digest in latest.items() if fingerprint(snapshot(Path(p))) != digest]
    if drift:
        raise ValueError("Installed entries changed or missing: " + ", ".join(drift))
    for path in args.skills_dir.resolve().glob("sage-*"):
        if path.is_symlink() and not path.exists():
            raise ValueError(f"Broken skill link: {path}")
    if (home / "AGENTS.override.md").exists():
        print("Notice: AGENTS.override.md takes precedence over the installed global AGENTS.md.")
    servers = config.get('mcp_servers', {})
    enabled = [name for name in managed.get('mcp_servers', {}) if servers.get(name, {}).get('enabled', True)]
    disabled = [name for name in servers if not servers[name].get('enabled', True)]
    print(f"Installation intact. Enabled SAGE MCP servers: {', '.join(enabled) or 'none'}")
    print(f"Disabled MCP servers: {', '.join(disabled) or 'none'}")
    if args.native:
        binary = shutil.which("codex")
        if not binary:
            raise ValueError("Codex CLI not found on PATH")
        result = subprocess.run([binary, "mcp", "list", "--json"],
                                env={**os.environ, "CODEX_HOME": str(home)}, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError("Native config validation failed; run codex mcp list")
        print("Ordinary Codex loaded the passive MCP configuration.")


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
            command.add_argument("--mcp", action="append", choices=sorted(mcp_templates()), default=[])
            command.add_argument("--disable-mcp", action="append", choices=sorted(mcp_templates()) + ['hybrid-sage'], default=[],
                                 help="Keep a registered server disabled; harmless when absent")
            command.add_argument("--with-hybrid", type=Path, metavar="REPO", help="Register a local hybrid-sage checkout")
            command.add_argument("--dry-run", action="store_true")
        else:
            command.add_argument("--native", action="store_true", help="Also ask ordinary Codex to validate its configuration")
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
    except (OSError, ValueError, KeyError, TimeoutError, subprocess.SubprocessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
