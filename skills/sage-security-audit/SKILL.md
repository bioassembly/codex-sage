---
name: sage-security-audit
description: Perform a requested security review or investigate a concrete trust-boundary defect.
---

Scope the target, attacker capabilities, assets, and permitted testing. Trace input
from entry points through authentication/authorization, storage, execution, and
external calls. Check tenant/object ownership, injection, secrets exposure, unsafe
file paths, dependency boundaries, and partial-failure behavior as relevant.
For each candidate issue establish prerequisites, an actual code path, impact,
and a minimal permitted reproduction. Use controlled fixtures; avoid live-user
records, destructive payloads, or unapproved production scanning.
Prioritize exploitable defects over generic checklists. Recommend a fix at the
trust boundary and a behavioral regression check. Report uncertainty and separate
confirmed issues from hypotheses. Do not claim the whole application is secure
because the selected paths produced no findings.
