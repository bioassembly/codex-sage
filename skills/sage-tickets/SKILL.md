---
name: sage-tickets
description: Split an approved specification into implementable vertical slices with explicit dependencies.
---

Read the spec and relevant code. Divide by independently demonstrable behavior,
starting with the smallest end-to-end slice that tests the key assumption.
For each ticket give the outcome, included scope, acceptance checks, blocking
relationships, and relevant implementation entry points. Avoid horizontal tickets
that leave every layer unfinished. Use expand-contract sequencing for migrations.
Keep testing with its behavior change rather than assigning a final testing phase.
Save drafts locally unless issue creation was requested. When publication is
requested, use the connected tracker, preserve its template, and return created
links. Do not create duplicates when retries encounter existing matching issues.
