---
name: sage-design
description: Design or refactor module interfaces and stress-test consequential architecture decisions.
---

Read existing interfaces, callers, glossary, and decision records before designing.
Prefer a small interface that hides real complexity and keeps related knowledge
local. Include ordering, failure semantics, invariants, and performance in the
interface contract. Introduce an abstraction where behavior actually varies.
For consequential choices, sketch materially different options and compare them
against the user's constraints, migration cost, test seams, and rollback path.
Ask only for decisions that cannot be inferred or investigated. If the user requests
an interview or /grill-me, work through unresolved decisions in short rounds with
recommended defaults; otherwise proceed using documented assumptions.
Keep domain terminology consistent. Record durable trade-offs in the project's
existing ADR format when useful. Avoid architecture work that expands a routine fix.
