---
name: sage-checkpoint
description: Save or resume long-running task state across compaction, interruptions, or sessions.
---

Keep a task-specific checkpoint in the project's existing notes location, or
`.state/<task>.md` when none exists. Merge existing notes; keep unrelated notes.
Record the requested outcome, constraints, branch/worktree, changed files,
decisions with reasons, failed approaches, exact verification commands and results,
remaining work, and the next executable step. Use paths and identifiers that can
be looked up again. Keep it brief enough to read on resumption.
On resume, inspect Git status and the referenced files before trusting old state.
Distinguish executed work from plans. Do not store credentials, patient identifiers,
or large tool dumps. Persist reusable conventions in existing project docs only
when they are established; a temporary hypothesis does not become a global rule.
Report the path written. If no task exists, do not create an empty checkpoint.
