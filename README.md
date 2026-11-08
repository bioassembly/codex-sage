# Codex SAGE

**Codex SAGE (State-of-the-Art Agentic Genomics & Engineering Harness)** — a
reproducible, high-performance configuration harness for OpenAI Codex, engineered
to match and exceed the capabilities of modern agentic coding and bioinformatics
harnesses: frontier planning and review, free OpenCode worker orchestration,
focused skills, specialist agents, optional MCP tools, and reversible installation.

SAGE adapts the useful workflows from
[antigravity-sage](https://github.com/bioassembly/antigravity-sage) and
[opencode-sage](https://github.com/bioassembly/opencode-sage) to Codex's native
configuration, skill discovery, and agent system. It adds procedures and tool
access; it does not change model weights or claim benchmark gains without evaluation.

## Install

Requires Python 3.11+, Bash, and Codex CLI 0.167 or newer with standalone custom
agent definitions. The native smoke test was run on 0.167.0.

```bash
git clone https://github.com/bioassembly/codex-sage.git
cd codex-sage
bash scripts/activate.sh
codex
```

For the full cross-harness workflow, clone
[hybrid-sage](https://github.com/bioassembly/hybrid-sage) alongside this checkout:

```bash
bash scripts/activate.sh --with-hybrid ../hybrid-sage --mcp context7 --mcp deepwiki
codex
```

The installer links 15 skills into `~/.agents/skills`, installs three agent files
under `$CODEX_HOME/agents`, merges a marked section into `$CODEX_HOME/AGENTS.md`,
and merges selected SAGE defaults and any requested MCP servers into the ordinary
`$CODEX_HOME/config.toml`, preserving your unrelated model, reasoning, UI,
provider, plugin, and permission settings. `$CODEX_HOME` defaults to `~/.codex`.
It also installs `codex-sage-doctor` into `~/.local/bin`, and keeps `codex-sage`
as a compatibility alias that simply runs plain `codex`; ensure that directory is
on `PATH`. Keep this checkout in place because skills link to it.

Launch plain `codex` — no extra profile or wrapper launch is required. The merged
config adds live web search, agent concurrency, and the selected MCP servers
alongside your existing settings, including user-configured MCP servers. The
installer uses Codex's native TOML writer to preserve unrelated settings and
comments, does not touch `auth.json`, and snapshots originals under `$CODEX_HOME/sage/backups` for
restore. A `sage.config.toml` profile installed by older versions is retired
only if unchanged.

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

### Choose an assistant or disable hybrid mode

Install Hybrid SAGE's CLI once with `bash ../hybrid-sage/install.sh`, then:

```bash
sage models --provider opencode
sage model opencode/glm-5.3-flash-free
sage hybrid off
sage hybrid on
sage hybrid status
```

The choice persists across Codex, Antigravity, and OpenCode. Disabling hybrid mode
stops new worker jobs and cross-harness consultations; the frontier model continues
directly, and running jobs remain available to poll. Re-enabling retains your
selected assistant. Paid or unknown-price model selection requires an explicit
`--allow-paid`; there is no silent paid fallback. You can also ask the assistant
to list models, select one, or turn hybrid mode off/on through `configure_fleet`.

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

No new MCP server starts in the minimal installation. Add the capabilities you
use with repeated `--mcp` flags. Existing servers remain configured; omitting a
flag on a later install does not remove a server you already enabled.

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
