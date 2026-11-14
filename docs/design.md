# Design and source mapping

This harness spends frontier attention on decisions and acceptance. It exposes
useful execution capabilities without making every task pay for every workflow.

| Source feature | Codex adaptation |
| --- | --- |
| Global agent protocol | A small marked section in the existing global AGENTS.md |
| OpenCode agent/command Markdown | Standalone Codex agent TOML and discoverable skills |
| Local inference model/provider settings | Inherit user selection; no Qwen endpoint or temperature forced into Codex |
| Automatic skill acquisition on every gap | Consult docs; acquire only for a demonstrated reusable need within scope |
| Mandatory TDD/worktree/interview on all work | Match validation and isolation to behavior and risk |
| Automatic large binary tool installation | Task-relevant static inspection with installed tools; optional REA |
| Always-connected reasoning/fetch/memory MCP | Native tools, plugins, project notes, and optional distinct integrations |
| Fixed frontier implementation loop | Direct Codex execution; delegation only when requested |
| Large copied scientific skill manuals | Small scientific workflows linked to canonical documentation |
| Destructive global synchronization | Installer-owned paths, preflight validation, private journals, resumable restore |

## Configuration boundaries

Selected SAGE defaults are merged into the ordinary `$CODEX_HOME/config.toml`
beside your existing settings. SAGE supplies live web search, a tool-history budget,
and up to three concurrent native agent threads only where unset; it neither selects a model nor weakens
permissions, and unrelated model, reasoning, UI, provider, plugin, and
permission settings are preserved. A separate `sage.config.toml` profile
installed by older versions is retired only if its recorded state is unchanged,
and the legacy `codex-sage` wrapper remains as a compatibility alias to plain
`codex`. A session can still have fewer tools because of managed policy,
account availability, or client capabilities. A skill cannot grant a missing tool.

Skills link from the maintained source tree into a native discovery location.
Custom agent files contain the current required `name`, `description`, and
`developer_instructions` fields. They do not pretend a custom agent can override
the parent's sandbox, provider, or MCP configuration.

The installer merges only selected defaults and MCP fields into `$CODEX_HOME/config.toml` and
does not modify shell startup files, authentication, plugin registrations,
active model servers, or scheduler jobs. It refuses real directory collisions
instead of replacing personal skill trees. It records only the paths it
installs, preserves unrelated entries, and retires old installer-owned entries
only when their recorded state is unchanged.

Configuration changes are staged through Codex's native `config/batchWrite` API
in a temporary home. The installer checks that every unrelated parsed value is
preserved before touching the live configuration; the native writer also keeps
comments. A concurrent edit to the live file aborts installation. Diagnostics
check managed fields while allowing later user changes to model, UI, default
preferences, and MCP enabled states. Reinstalls refresh selected templates and
preserve live enabled states. An explicit disable flag takes precedence. Hybrid
skills retire only when unchanged and the integration is disabled or absent.

## Official references

- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
  for `config.toml` entries, web search, MCP tables, and concurrency.
- [Build skills](https://learn.chatgpt.com/docs/build-skills) for native discovery,
  symlink support, and progressive loading.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) for
  standalone custom-agent fields and inherited settings.
- [AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md/) for
  instruction discovery and overrides.

These formats were checked against Codex CLI 0.169.0 on 2026-11-14. Run the native
smoke test after upgrading; configuration formats can change.
