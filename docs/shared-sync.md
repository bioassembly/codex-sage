# Shared upstream refresh and client integration

The harness uses original Ponytail, grill-with-docs, and its full grilling and
domain-modeling dependencies. Grill-with-docs replaces the plain grill-me wrapper
and records resolved terminology and consequential design decisions as it interviews.
Their instructions and invocation policies are unchanged. Native loader mapping
lives in global guidance rather than replacing upstream workflow text.

`third_party/lock.json` is the per-client inventory of original files and reviewed
revisions. Its aliases and patches fields identify every compatibility change.
The update checked Ponytail, Matt Pocock, Trail of Bits, Vercel, Superpowers,
Anthropic, and K-Dense sources. Locally maintained SAGE workflows do not have an
independent upstream release and retain their own names and scope.

| Capability | Codex | Antigravity / OpenCode |
| --- | --- | --- |
| Minimal complete implementation | Original ponytail | Same original package; duplicate OpenCode injector retired |
| Design interview with documents | Original grill-with-docs + grilling + domain-modeling | Same originals; native skill-loader bridge |
| Domain design/spec/tickets | sage-design, sage-domain-modeling, sage-spec, sage-tickets | Refreshed original domain-modeling, codebase-design, to-spec, to-tickets, setup dependency |
| Debugging/testing/isolation | sage-debug, sage-test-design, sage-git-worktrees | Refreshed original Superpowers packages |
| Scientific work | Scoped sage-* workflows | Refreshed K-Dense packages plus retained local scientific validation notes |
| MCP/browser development | sage-mcp-builder, sage-webapp-testing | Refreshed Anthropic packages |
| Security variants and diff review | Original Trail of Bits packages | Same originals |
| React/Next.js | Original Vercel package | Same original files |
| Continuity and context | sage-checkpoint, sage-token-efficiency | Updated checkpoint/token-efficiency; same Codex-log audit utility |
| Binary/PDF work | Task-scoped investigation and true-redaction distinction | Scoped entrypoint with retained detailed REA guide; PDF removal/cosmetic distinction |
| Git/repository/report workflows | Focused SAGE skills | Existing native git-commit, repository, first-principles, FAIR and results procedures |

The siblings retain their native configuration/agent/command formats. They do not
load Codex agent TOML or Codex hook JSON. RTK uses upstream Antigravity plugin
manifests and the upstream OpenCode dual-interface TypeScript plugin. Its binary
version and release checksums are pinned separately.

## Recorded compatibility fixes

- The grill-with-docs wrapper loads both `grilling` and `domain-modeling`; clients
  without the upstream `Skill` tool use their native skill loader or read both
  installed dependencies. Its original explicit-only invocation policy is retained.
- Some Nextflow supporting documents refer to `references/...` from package root.
  The validator resolves these package-root paths without editing upstream text.
- Three links in Vercel's compiled guide omit `rules/`. Declared file aliases make
  those exact paths available while preserving all upstream files.
- Anthropic's evaluation helper handled only the first `tool_use` in a response.
  A recorded patch supplies every result, including failures, before continuing.
  Its regression test uses stubs; installation never launches a paid model or
  requires an Anthropic API key.
- Matt Pocock project settings may be stored in CLAUDE.md. Native guidance locates
  the configured files and verifies required issue labels before an authorized
  publication. Installing the packages does not initialize arbitrary projects.

## Install and restore

```bash
# Codex
bash scripts/activate.sh --disable-mcp hybrid-sage
python3 scripts/install_rtk.py

# Antigravity repository
bash install.sh --disable-hybrid
bash scripts/install-rtk.sh

# OpenCode repository (2.x configuration)
bash scripts/activate.sh --disable-hybrid
bash scripts/install-rtk.sh
```

Each installer prints a private restore journal. Restore multiple installs in
reverse order using the printed commands. User models, provider keys, permission
choices, unrelated plugins, local skill overrides, and personal notes are retained.
Only recorded files are retired; updates do not delete entire personal skill
trees, prune old backups, auto-install REA, or run Hybrid's installer.

`--disable-hybrid` also retires known auto-discovered Hybrid plugin entrypoints
through the journal. Otherwise an old filesystem plugin could remain active even
after disabling its MCP entry. No model processes are stopped.

For isolated activation checks, pass `--home /temporary/user-root` (or set
`SAGE_USER_HOME`) to sibling installers. This redirects every installation target
without changing the shell's HOME or accessing live provider credentials.

The copied token audit reads **Codex JSONL counters**; it is not a generic billing
meter for Gemini or OpenCode. Use each client's own accounting for its usage.
Packaging/integrity tests establish installation behavior, not smarter reasoning
or guaranteed end-to-end token savings.
