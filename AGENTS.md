# Working on codex-sage

This repository packages a Codex CLI harness. `config/`, `agents/`, and
`skills/` are the source of truth; `scripts/harness.py` installs them.

Preserve the user's base config, authentication, plugins, model choice, and
permissions. Keep runtime data and machine paths out of Git. Use Python 3.11+
standard library for installation. MCP integrations are optional and must have
an actual capability advantage over native tools. Do not add blanket skill,
subagent, package installation, or approval requirements to routine tasks.

Before committing, run `python3 -m unittest discover -s tests -v` and
`python3 scripts/harness.py check`. Changes to installation also need a temporary
home smoke test with the installed Codex CLI, followed by a restore. Never test
by overwriting authentication or changing a live inference server.
