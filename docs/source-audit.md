# Source audit and optional additions

Reviewed 2026-11-14. Source revisions are recorded in
[sources.lock.json](../sources.lock.json); workflow coverage is in
[REGISTRY.md](../REGISTRY.md). The sibling repositories remain unchanged.
This is a source/configuration audit, not a model-performance benchmark.

## Token overhead and changes

- **Repeated large results:** full listings, page dumps, and duplicate text plus
  structured MCP results accumulate in history. Retrieve paths/symbols first,
  process structured results once, and retain full logs outside the prompt.
  The new unset-only 6,000-token history default bounds individual results;
  expand targeted retrieval when evidence is missing.
- **Global orchestration:** the previous always-loaded guidance described worker
  catalogs, routing, polling, and fallback loops. The global block now keeps only
  the direct-execution default and authorization boundary. Hybrid remains optional.
- **Disabled-state regression:** an older managed `enabled = true` could overwrite
  a subsequent user `false` on reinstall. A regression test reproduces this and
  protects preservation of the live choice. Explicit disable flags are recorded;
  unused unchanged Hybrid skill links retire.
- **Catalog overhead:** skill metadata and tool schemas still cost context.
  Short skills and MCP `omit_tools_from = ["direct"]` keep detailed workflows and
  schemas available through the appropriate discovery surfaces. Installing more
  skills is not inherently a token optimization.
- **Client/plugin baseline:** client-provided instructions and native/plugin tool
  definitions can outweigh the SAGE block. Removing unused app/plugin integrations
  may reduce this fixed cost, but it changes available capabilities and remains a
  user choice. Trimming SAGE alone does not remove the client's baseline prompt.
- **Reasoning effort:** high/max effort can spend substantial reasoning tokens.
  A skill cannot guarantee the same reasoning with fewer tokens. The installer
  preserves the selected model and effort; changing either needs a separate
  quality/latency comparison and user choice.
- **Worker totals:** isolating a transcript can reduce parent context while
  increasing total model work, especially if the parent must repair the result.
  Disabled Hybrid is respected; no worker experiments run as part of this update.

Use `python3 scripts/token_audit.py --limit 20` for local aggregate counters.
It does not print prompt/tool contents or upload logs. Cached input is separate
from uncached input, and output may already include reasoning. Forked histories,
incomplete logs, and subscription accounting limit what these totals establish.
See [OpenAI's guidance on concise skills and global instructions](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra),
[skill disclosure](https://learn.chatgpt.com/docs/build-skills), and
[configuration fields](https://learn.chatgpt.com/docs/config-file/config-reference).

## Existing skills and MCP improvements

| Finding | Codex adaptation / follow-up |
| --- | --- |
| Ponytail is an OpenCode plugin entry, not an installed Codex skill | Added a concise Codex core skill, retaining attribution and scope/validation requirements. No OpenCode hooks run in Codex. |
| Upstream grill-me now wraps `grilling` under `skills/productivity/` | Added a self-contained Codex interview skill. The sibling's older self-contained version is not broken merely because the upstream layout changed. Directly copying the new wrapper would refer to a foreign `Skill` tool. |
| Sibling token-efficiency favors Serena first and makes broad retrieval claims | Codex chooses rg or semantic navigation to fit the task, reads callers/control flow, and measures before claiming savings. |
| Sibling small-model guidance includes sequential-thinking and fixed context budgets | These do not transfer directly to a frontier Codex configuration. Native reasoning/web tools cover ordinary reasoning/fetch; no extra server is enabled for those. |
| Serena launch is unpinned in the sibling configurations | Added pinned `serena-agent==2.1.0`, validated `codex` context/CLI options, no automatic home-directory indexing. Its optional REPL interface remains an evaluation candidate. |
| Sibling Playwright pin is 0.0.79; registry latest is 0.0.85 | Added an optional pinned 0.0.85 template with an isolated headless session, preserving normal browser sandbox behavior. |
| Sibling memory pin is 2026.7.4; registry latest tag is 2.1.1 | Added an optional 2.1.1 template with a separate Codex store. The old release still exists; a lower-looking version number does not establish release order. No sibling graph is migrated. |
| Sibling PDF workflow presents byte substitution as anonymization | Codex separates visual edits from actual content removal and checks relevant hidden content/metadata. The specialized raster/byte-swap helper is not copied or represented as a general redaction solution. |
| Older manifests cite changing star counts and broad quality labels | Provenance now uses reviewed revisions and concrete capabilities. Popularity is a discovery signal, not evidence of intelligence or token savings. |
| Duplicate creator/installer/review wrappers | Native skills and specialist agents cover these without another wrapper catalog. |

The scientific procedures are maintained adaptations, not synchronized copies of
package manuals. Retrieve official version-specific Nextflow, pysam, and Biopython
documentation for actual work. Source age alone does not establish that a workflow
is incorrect. No unrun scientific accuracy improvement is claimed.

Package metadata was checked against [PyPI Serena](https://pypi.org/project/serena-agent/),
[Playwright MCP](https://www.npmjs.com/package/@playwright/mcp), and
[MCP memory](https://www.npmjs.com/package/@modelcontextprotocol/server-memory).
Ponytail and grilling sources and their notices are pinned in the source manifest.

## Optional additions for the user to choose

These were researched but are **not installed**. They add distinct task-specific
value; none guarantees lower total tokens or greater intelligence.

| Candidate | Potential value | Suggested trial |
| --- | --- | --- |
| [RTK](https://github.com/rtk-ai/rtk) | Compresses common command output and provides a Codex hook integration. It is a CLI, not a skill. | First compare explicit read-only RTK commands with raw output on a representative test/review task. Keep raw logs and check errors/exit status. Author savings are command-output benchmarks, not measured savings for this harness. |
| [Trail of Bits variant-analysis](https://github.com/trailofbits/skills/tree/main/plugins/variant-analysis) | Searches a codebase for other instances of a known root cause; a more specific capability than a generic security review. | Use on a known bug with known additional instances; compare recall, false positives, and effort. Scope installation to security work. |
| [Trail of Bits differential-review](https://github.com/trailofbits/skills/tree/main/plugins/differential-review) | Adds history, caller impact, and test-coverage analysis for security-sensitive changes. | Use for a consequential diff rather than every commit; its multi-phase workflow and mandatory report add work. Check the repository's CC-BY-SA terms before adaptation. |
| [Vercel React best practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) | Framework-specific guidance for React/Next.js data fetching, rendering, and bundles. | Install in a relevant frontend project; validate with its own tests and performance measurements. It adds little to unrelated genomics work. |

RTK's [Codex integration notes](https://github.com/rtk-ai/rtk/blob/develop/hooks/codex/README.md)
explain that command rewriting interacts with native approval classification.
Review this behavior before enabling a global hook; the hook was not added here.

Prefer one candidate at a time on a fixed model/effort and a small set of real
tasks. Compare correctness, evidence quality, uncached input, output/reasoning,
calls, elapsed time, and unexpected side effects. Keep a candidate only when its
actual benefit outweighs the context and execution cost.
