"""Shared reversible file installation primitives, maintained from Codex SAGE."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

REPO = Path(__file__).resolve().parents[1]
START = "<!-- sage-harness:start -->"
END = "<!-- sage-harness:end -->"

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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['restore'])
    parser.add_argument('journal', type=Path)
    args = parser.parse_args()
    restore(args.journal)
