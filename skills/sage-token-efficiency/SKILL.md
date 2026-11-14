---
name: sage-token-efficiency
description: Diagnose excessive token usage or reduce context overhead in a harness or long task.
---

Measure before changing behavior. The [local audit script](../../scripts/token_audit.py)
summarizes recorded usage without exposing prompt contents; its totals are not a
bill or subscription-quota formula. Distinguish input, cached input, output, and
reasoning. Do not double-count repeated cumulative usage events.
Preserve the user's model and reasoning level unless they request a change.
Target unnecessary work: repeated retrieval, large unfiltered outputs, duplicate
tool representations, oversized global instructions, and irrelevant skill loads.
Search paths/symbols first, read the needed implementation and callers, and expand
when control flow requires it. Use Serena when semantic references add value;
ordinary text/configuration often needs only rg. Keep full logs on disk and return
bounded evidence; do not hide a test failure by truncating the only copy.
Use concise skill metadata and defer MCP tools where supported. Keep useful
capabilities available. Checkpoint long tasks and verify state on resumption.
Delegate only when the bounded result justifies the extra model work; fewer tokens
in the parent context do not necessarily mean fewer total tokens. Compare the
same task and correctness checks before claiming savings.
