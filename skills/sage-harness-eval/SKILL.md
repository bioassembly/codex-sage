---
name: sage-harness-eval
description: Evaluate whether a skill, MCP integration, routing policy, or harness change improves agent behavior.
---

State the proposed behavioral improvement and the cost it adds. Freeze the harness
revision, model, effort, task fixtures, and expected observable outcomes.
Run the baseline and candidate on the same bounded tasks in fresh sessions where
practical. Include a matching task, an adjacent task that should not trigger the
skill, and a failure/recovery case. Distinguish unavailable tests from failures.
Measure correctness first, then tool calls, wall time, context use, and unexpected
mutations. Validate output artifacts rather than scoring confident explanations.
For acquisition, inspect the instructions and bundled executables, source revision,
license, maintenance, and required data access. Stars alone do not prove quality.
Use the built-in skill-creator/installer for actual Codex skill work when available.
Record the outcome and limitations, including null results. Keep only additions
with a demonstrated capability or clear workflow benefit; do not call a larger
catalog smarter without evidence.
