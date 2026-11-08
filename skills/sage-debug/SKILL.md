---
name: sage-debug
description: Diagnose failing tests, runtime errors, races, and regressions through a reproducible root cause.
---

Capture the exact failing command, environment, expected behavior, and observed
failure. Inspect the closest implementation, callers, and recent relevant changes.
Reduce to a small reproducer and state a falsifiable hypothesis before patching.
Change one causal variable, then rerun the reproducer. For intermittent behavior,
record seeds, ordering, timing, and resource conditions; passing once is weak evidence.
After two unsuccessful fixes, revisit assumptions and isolate a smaller case or
seek a bounded independent diagnosis. Do not keep stacking speculative fixes.
Add a regression test at the observable interface when it protects useful behavior.
Run the relevant suite and inspect the final diff. Report the cause, fix, actual
validation, and unresolved uncertainty. Never weaken an assertion to hide a bug.
