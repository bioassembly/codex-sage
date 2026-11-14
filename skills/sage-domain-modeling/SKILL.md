---
name: sage-domain-modeling
description: Clarify domain vocabulary, state transitions, and invariants when conflicting concepts or terminology obstruct a design.
---

Trace terms through real examples, stored data, interfaces, and callers. Separate
concepts with different lifecycles or ownership; distinguish synonyms from distinct
entities. Establish units, identity, cardinality, valid states, transitions, and
invariants before proposing names or types. Use counterexamples to expose a model
that merges different concepts.
Keep a small glossary in the project's existing location when the terminology
will be reused. Record only consequential trade-offs in its ADR format, including
the chosen option, alternatives, consequences, and evidence. Update examples and
contracts that actually depend on the decision. Avoid creating glossary or ADR
scaffolding for a routine edit. Ask the user only about domain choices that cannot
be established from available evidence.
