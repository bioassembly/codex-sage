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
| Fixed frontier implementation loop | Hybrid workers execute; frontier plans, inspects artifacts, and accepts revisions |
| Large copied scientific skill manuals | Small scientific workflows linked to canonical documentation |
| Destructive global synchronization | Installer-owned paths, preflight validation, private journals, resumable restore |

## Configuration boundaries

`sage.config.toml` is a file-based profile. It adds live search and allows up to
three concurrent spawned native agent threads. It neither selects a model nor
weakens permissions. A session can still have fewer tools because of managed policy,
account availability, or client capabilities. A skill cannot grant a missing tool.

Skills link from the maintained source tree into a native discovery location.
Custom agent files contain the current required `name`, `description`, and
`developer_instructions` fields. They do not pretend a custom agent can override
the parent's sandbox, provider, or MCP configuration.

The installer does not modify the base TOML, shell startup files, authentication,
plugin registrations, active model servers, or scheduler jobs. It refuses real
directory collisions instead of replacing personal skill trees. It records only
the paths it installs, preserves unrelated entries, and retires old installer-owned
entries only when their recorded state is unchanged.

## Official references

- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
  for profile files, web search, MCP tables, and concurrency.
- [Build skills](https://learn.chatgpt.com/docs/build-skills) for native discovery,
  symlink support, and progressive loading.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) for
  standalone custom-agent fields and inherited settings.
- [AGENTS.md guidance](https://developers.openai.com/codex/guides/agents-md/) for
  instruction discovery and overrides.

These formats were checked against Codex CLI 0.167.0 on 2026-11-08. Run the native
smoke test after upgrading; configuration formats can change.
