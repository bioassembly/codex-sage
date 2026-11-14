# Codex SAGE

A reproducible Codex harness with 31 skills, three specialist agents,
optional MCP integrations, and reversible installation. Work executes in Codex
by default. Hybrid SAGE is optional and never enabled by the standard install.

## Install

Requires Python 3.11+, Bash, and Codex CLI 0.169+. Native validation and CI use
0.169.0. Model, reasoning effort, authentication, plugins, and permissions remain
user-controlled.

```bash
git clone https://github.com/bioassembly/codex-sage.git
cd codex-sage
bash scripts/activate.sh
codex
```

For documentation and semantic code navigation, with Hybrid disabled:

```bash
bash scripts/activate.sh --mcp context7 --mcp deepwiki --mcp openai-docs --mcp serena --disable-mcp hybrid-sage
```

The installer links skills into `~/.agents/skills`, installs agent files under
`$CODEX_HOME/agents`, replaces only its marked global guidance, and merges selected
settings into `$CODEX_HOME/config.toml` using Codex's native TOML writer.
`$CODEX_HOME` defaults to `~/.codex`. Keep this checkout in place: skill links point
to it. Launch plain `codex`; no profile or wrapper is required.

Existing explicit defaults and MCP on/off choices survive updates, including a
disabled Hybrid server. Omitted MCP flags do not remove registered servers.
Previously selected templates refresh from the tracked source on reinstall.
`--mcp` registers a capability; it does not override an existing disabled choice.
To enable a deliberately disabled server, explicitly edit its `enabled` setting.
`--disable-mcp` is repeatable and harmless when the server is absent. Unchanged,
installer-owned Hybrid skill links retire when Hybrid is disabled.

## Skills

| Workflow | Skills |
| --- | --- |
| Scope and decisions | `ponytail`, `grill-me`, `sage-design`, `sage-domain-modeling`, `sage-spec`, `sage-tickets` |
| Engineering | `sage-debug`, `sage-test-design`, `sage-review`, `sage-mcp-builder`, `sage-repo-maintenance` |
| Git | `sage-git-worktrees`, `sage-git-commit` |
| Scientific work | `sage-genomics`, `sage-sequence-analysis`, `sage-scientific-report`, `sage-results-package`, `sage-fair-data` |
| Investigation and documents | `sage-security-audit`, `sage-binary-inspection`, `sage-webapp-testing`, `sage-web-scraping`, `sage-pdf-editing`, `sage-explain` |
| Continuity and evaluation | `sage-checkpoint`, `sage-overnight`, `sage-harness-eval`, `sage-token-efficiency` |
| Upstream packages | `variant-analysis`, `differential-review`, `vercel-react-best-practices` |

Invoke a skill with `$ponytail`, `$grill-me`, or another name, or let Codex match
its description. Skill bodies load when selected; the discovery catalog contains
names, descriptions, and paths. Adding skills still has a metadata cost.
Ponytail and grill-me are concise Codex adaptations with attribution, not their
complete upstream plugins. Grill-me applies to requested interviews; it does not
add confirmation gates to routine work. See [workflow mapping](REGISTRY.md).

The three upstream packages above are complete, unmodified skill directories,
including their supporting references and assets. Their file hashes and source
revisions are in [third_party/lock.json](third_party/lock.json), checked by the
harness validator. Trail of Bits content uses CC-BY-SA-4.0; Vercel's skill declares
MIT in its upstream metadata. See [third-party notices](THIRD_PARTY_NOTICES.md).

Agents are `sage-reviewer`, `sage-skeptic`, and `sage-bioinformatician`. They
inherit the parent model. Their read-only constraints are instructions, not a
separate OS security boundary. Use them for bounded work when it warrants the cost.

## MCP choices

No new server starts in the minimal install. Each template omits tools from the
initial direct-tool surface while leaving deferred discovery and Code Mode
available. This is a loading choice, not an access-control boundary.

| Flag | Capability | Dependencies |
| --- | --- | --- |
| `--mcp context7` | Library documentation | Network |
| `--mcp deepwiki` | Public repository research | Network |
| `--mcp openai-docs` | Official OpenAI documentation | Network |
| `--mcp serena` | Symbol navigation and semantic edits | uvx; pinned serena-agent 2.1.0 |
| `--mcp playwright` | Browser interaction when the client lacks it | Node/npx; pinned 0.0.85; browser installation |
| `--mcp memory` | Optional independent knowledge graph | Node/npx; pinned 2.1.1 |

Serena starts without indexing a home directory. Activate the actual task
repository with its `activate_project` tool before symbol operations.
The browser template uses an isolated headless session; install its browser with
the server's supported browser-install workflow if needed. It does not inherit
the sibling harness's blanket browser sandbox bypass.
Memory uses `$CODEX_HOME/sage/memory.json`, not the sibling OpenCode store. Prefix
facts with project scope and verify retrieved facts before relying on them.

Native reasoning/web tools replace sequential-thinking and fetch in Codex.
Existing project browser tests remain useful alongside an optional browser MCP.
REA remains an on-demand reverse-engineering option through
`sage-binary-inspection`; a standing large server catalog is unnecessary.

To register an optional Hybrid checkout, use `--with-hybrid ../hybrid-sage`.
A previously disabled server remains disabled. Delegation requires a user request;
its controls and worker policy live in that repository. Nothing here starts
worker jobs during installation or validation.

## Token overhead

The global instructions keep orchestration detail out of ordinary tasks.
A 6,000-token tool-history limit is added only when the user has not set one;
use bounded retrieval and retain complete logs before a large result is truncated.
Model and reasoning effort remain unchanged. Deferred tools and focused skills
reduce unnecessary loading; they do not establish benchmark or billing savings.

Inspect local recorded counters without exposing transcript contents:

```bash
python3 scripts/token_audit.py --limit 20
```

Cached input is reported separately. Repeated cumulative notifications are
deduplicated and counter resets handled. Reasoning is not added to output twice.
Forked histories/incomplete logs can overlap or omit usage. These are recorded
counters, not a subscription-quota formula or a cost invoice.
See [source audit and optional additions](docs/source-audit.md).

## RTK command-output compression

The approved RTK installation uses the OSS edition: the upstream hook core and
command filters, without the optional pipeline engine. Version 1.2.0 release
assets are pinned by SHA-256 for supported Linux/macOS architectures.

```bash
python3 scripts/install_rtk.py
```

This installs `~/.local/bin/rtk`, stages upstream `rtk init -g --codex` in an
isolated temporary home, preserves existing global instructions/hooks, and installs
the resulting Codex hook and upstream `RTK.md`. It prints an exact restore command.
No trust records, model, permission, authentication, or MCP settings are changed.
Keep the binary directory on the Codex process's `PATH`: upstream rewrites invoke
`rtk` by name, including when the hook itself uses an absolute executable path.

Restart Codex and review/trust the RTK command through `/hooks` to enable automatic
rewriting. Codex requires this review for new non-managed hooks. Until trusted,
explicit commands such as `rtk git status` work independently of the hook. Use
`rtk bypass <command>` when raw output is needed. Actual savings depend on workload;
command-output compression is not a guarantee of equivalent task performance.
See the [official hook trust flow](https://learn.chatgpt.com/docs/hooks) and
[RTK's Codex integration](https://github.com/rtk-ai/rtk/blob/v1.2.0/hooks/codex/README.md).

## Update, validate, and restore

```bash
git pull --ff-only
bash scripts/activate.sh --disable-mcp hybrid-sage
python3 scripts/install_rtk.py  # when RTK is part of this installation
python3 scripts/harness.py check
python3 -m unittest discover -s tests -v
python3 scripts/smoke_native.py
codex-sage-doctor --native
```

Updating source does not fetch arbitrary new skills. Review upstream changes
against [sources.lock.json](sources.lock.json), update adaptations and package
pins deliberately, run checks, then reinstall. A source pin records what was
reviewed; it does not lock every optional package's transitive dependencies.
Vendored skill changes must also update the reviewed upstream file manifest.
RTK updates use its separate checksum-pinned installer; restore multiple
installations in reverse order using their printed journals.

The native smoke test uses temporary homes, validates all templates, checks skill
and agent discovery, and restores. It makes no model request and does not prove
live service access or browser availability. Installation prints an exact restore
command; private snapshots live under `$CODEX_HOME/sage/backups`. Restore preserves
later edits by reporting conflicts before changing anything.

```bash
bash scripts/activate.sh --dry-run
bash scripts/activate.sh --codex-home /path/to/codex --skills-dir /path/to/skills --bin-dir /path/to/bin
python3 scripts/harness.py restore /path/printed/by/install.json
```

Custom skills directories must be scanned by the chosen client. Diagnostics
report an `AGENTS.override.md` that overrides global guidance.
See [design](docs/design.md), [evaluation](docs/evaluation.md),
[provenance](REGISTRY.md), and [third-party notices](THIRD_PARTY_NOTICES.md).
SAGE code is MIT licensed; third-party material retains its own license. See
[LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
