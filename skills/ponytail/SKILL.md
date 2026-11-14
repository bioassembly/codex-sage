---
name: ponytail
description: Find the smallest complete implementation when adding features, choosing dependencies, or simplifying code; supports Ponytail lite, full, and ultra.
---

Inspect the affected code, callers, and existing solutions before adding anything.
Prefer, in order: avoid unnecessary work, reuse the project's implementation,
use a platform or standard-library feature, use an installed dependency, then
write the smallest clear implementation that finishes the requested behavior.
Keep existing conventions and complete required caller, configuration, and test
changes. Preserve validation, error handling, accessibility, and data integrity.
A shorter diff is useful only when it remains understandable and correct.
Add a focused behavior check for meaningful new logic or a regression; trivial
edits do not need invented tests. Avoid speculative options and abstractions.

Default `full` applies this approach. `lite` implements the requested design and
mentions a useful smaller alternative. `ultra` also challenges unsupported scope,
while respecting explicit requirements and authorization. Honor an explicit level
or off request; never persist a mode outside this conversation without a request.
Report the resulting behavior, actual validation, and material remaining limits.

Adapted for Codex from [Ponytail](https://github.com/DietrichGebert/ponytail).
Attribution and license: [third-party notices](../../THIRD_PARTY_NOTICES.md).
