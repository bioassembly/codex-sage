---
name: grill-me
description: Interview the user about unresolved plan or design decisions when they request grilling, a requirements interview, or a design stress test.
---

Investigate facts in the codebase and environment before asking the user.
Separate decisions from facts and map which decisions depend on earlier answers.
Ask a short round of independent, currently answerable questions. Give each a
concrete recommendation and explain a material trade-off. Wait for answers before
asking dependent questions; continue independent investigation meanwhile.
Use the client's question tool when available and keep each round manageable.

Update the decision tree after each answer. Stop when remaining uncertainty no
longer changes the plan, rather than inventing questions to visit every possible
branch. Capture agreed scope, assumptions, acceptance checks, and consequential
trade-offs in existing project documentation when useful.
An interview request alone does not authorize implementation. If implementation
is already authorized, preserve that authorization and follow the user's requested
sequence; ask for confirmation only for an unresolved decision that needs it.
Do not turn ordinary implementation tasks into interviews.

Adapted from the sibling grill-me workflow and
[Matt Pocock's grilling](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling).
See [third-party notices](../../THIRD_PARTY_NOTICES.md).
