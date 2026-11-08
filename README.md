# Codex SAGE

A Codex harness for frontier planning and review, free OpenCode worker orchestration,
and scientific engineering: focused skills, specialist agents, optional MCP tools,
and reversible installation.

SAGE adapts the useful workflows from
[antigravity-sage](https://github.com/bioassembly/antigravity-sage) and
[opencode-sage](https://github.com/bioassembly/opencode-sage) to Codex's native
configuration, skill discovery, and agent system. It adds procedures and tool
access; it does not change model weights or claim benchmark gains without evaluation.

## Install

Requires Python 3.11+, Bash, and Codex CLI 0.167 or newer with file-based profiles
and standalone custom agent definitions. The native smoke test was run on 0.167.0.

```bash
git clone https://github.com/bioassembly/codex-sage.git
cd codex-sage
bash scripts/activate.sh
codex-sage
```

For the full cross-harness workflow, clone
[hybrid-sage](https://github.com/bioassembly/hybrid-sage) alongside this checkout:

```bash
bash scripts/activate.sh --with-hybrid ../hybrid-sage --mcp context7 --mcp deepwiki
codex-sage
```

The installer links 15 skills into `~/.agents/skills`, installs three agent files
under `$CODEX_HOME/agents`, merges a marked section into `$CODEX_HOME/AGENTS.md`,
and writes `$CODEX_HOME/sage.config.toml`. `$CODEX_HOME` defaults to `~/.codex`.
It also installs `codex-sage` and `codex-sage-doctor` into `~/.local/bin`; ensure
that directory is on `PATH`. Keep this checkout in place because skills link to it.

Launch with `codex --profile sage` or `codex-sage` to load the profile's live web
search, agent concurrency, and selected MCP servers. Skills, global instructions,
and personal agent definitions are discoverable after restarting Codex even
without the profile. The profile inherits your model, reasoning effort, plugins,
and permissions. The installer does not replace `config.toml` or touch `auth.json`.
Existing user-configured MCP servers also remain inherited.

## Frontier planner, worker execution, frontier review

With Hybrid SAGE connected, Codex owns problem framing, decomposition, consequential
decisions, and final review. OpenCode workers perform bounded implementation and
test loops using an explicitly permitted free model. Independent tasks can run
as asynchronous jobs; overlapping edits need isolated worktrees.

1. Inspect `fleet_status` and `list_worker_models`; verify the worker's model and
   free/local policy rather than treating an installed CLI as a healthy model.
2. Give `delegate_local` a concrete task, owned paths, acceptance checks, and an
   artifact/output location. Keep complete output on disk and return a short summary.
3. Poll the job to completion. Codex inspects the actual diff and artifacts, runs
   checks, and requests revisions or accepts the result. Worker confidence is not
   a quality gate.
4. Use `consult_codex` from another harness for a frontier consultation, or
   `escalate_task` for Antigravity when available. Child workers must not recursively
   dispatch back into the fleet.

Free service availability and rate limits belong to the provider; SAGE cannot
guarantee unlimited capacity. Free hosted models are not private local models.
Unavailable workers fall back to direct execution without a silent paid-model swap.
See Hybrid SAGE's fleet policy for model allowlists and privacy handling.

## Included skills

| Area | Skills |
| --- | --- |
| Engineering | `sage-debug`, `sage-design`, `sage-spec`, `sage-tickets`, `sage-review` |
| Scientific work | `sage-genomics`, `sage-sequence-analysis`, `sage-scientific-report`, `sage-results-package` |
| Investigation | `sage-security-audit`, `sage-binary-inspection`, `sage-webapp-testing`, `sage-overnight` |
| Continuity and evaluation | `sage-checkpoint`, `sage-harness-eval` |

Skills load their detailed instructions when relevant. Names use a `sage-` prefix
to coexist with personal and plugin skills. Invoke explicitly with, for example,
`$sage-genomics`, `$sage-checkpoint`, or `$sage-review`.

The agents are `sage-reviewer`, `sage-skeptic`, and `sage-bioinformatician`. They
inherit the parent model and permissions. Reviewer/skeptic instructions prohibit
edits; this is an instruction-level constraint, not a separate OS sandbox. For
enforced consultation isolation, use Hybrid's restricted Codex consultation path.

## MCP choices

No new MCP server starts in the minimal installation. Add only the capabilities
you use; repeated `--mcp` flags select the installed profile's complete optional set.

| Integration | Enable | Purpose |
| --- | --- | --- |
| Hybrid SAGE | `--with-hybrid ../hybrid-sage` | OpenCode workers, Codex/Antigravity consultation, handoffs and scoped lessons |
| Context7 | `--mcp context7` | Library-specific documentation retrieval |
| DeepWiki | `--mcp deepwiki` | Repository architecture research |
| OpenAI Docs | `--mcp openai-docs` | Official OpenAI documentation search and retrieval |

Native reasoning replaces sequential-thinking MCP. Native web tools and connected
plugins cover ordinary search/fetch. Project files/checkpoints and available native
memory cover continuity without a second global memory service. Use existing
Playwright tooling or browser plugins for UI work; add a browser MCP separately
when that environment needs it. Serena can be useful for large semantic refactors,
but is not a dependency of ordinary search and editing. REA stays an on-demand CLI
option rather than a standing large tool catalog or an automatic package install.

## Check and restore

```bash
python3 scripts/harness.py check
python3 -m unittest discover -s tests -v
python3 scripts/smoke_native.py
codex-sage-doctor --native
```

The native smoke test uses temporary homes, checks actual skill/agent discovery and
strict native config parsing, then restores its installation. It makes no model
request. Tests cover preservation of user config, authentication, and unrelated
skills; optional MCP; custom paths; interrupted restore; rollback after a failed
write; and retirement of unchanged installer-owned entries.

Each installation prints its exact restore command. Snapshots live under
`$CODEX_HOME/sage/backups` with private file permissions. Restore leaves subsequent
user edits alone and reports conflicts; interrupted restores can be resumed.
For an isolated install or preview:

```bash
bash scripts/activate.sh --dry-run
bash scripts/activate.sh --codex-home /path/to/codex --skills-dir /path/to/skills --bin-dir /path/to/bin
python3 scripts/harness.py restore /path/from/the/install/output.json
```

A custom skills directory is useful for testing or repository-scoped discovery;
Codex must actually scan that location. An existing `AGENTS.override.md` takes
precedence over global `AGENTS.md` and is reported by diagnostics.

See [design and source mapping](docs/design.md), [provenance](REGISTRY.md), and
[behavioral evaluation cases](docs/evaluation.md). MIT licensed; see [LICENSE](LICENSE).
