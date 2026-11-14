---
name: sage-test-design
description: Design behavior-focused tests, regression coverage, or a requested test-first implementation loop.
---

Identify observable contracts, failure modes, and the existing test stack. For a
bug, reproduce the failure before editing. When a test-first loop is appropriate,
write the smallest test that fails for the intended reason, make the behavior
pass, then simplify while retaining coverage. Verify that the failure is not a
broken fixture, import, or environment.
Test behavior at a stable boundary rather than private structure or copied
implementation logic. Include relevant empty, boundary, malformed, and recovery
cases. Mock external side effects where necessary while retaining a realistic
contract. Use an integration test when unit isolation would conceal the defect.
Keep assertions specific enough to catch the bug and loose enough to permit a
correct refactor. Run the relevant checks and report their actual outcomes.
Scale coverage to impact; avoid adding tests solely to enforce prose, formatting,
or a reversible trivial edit.
