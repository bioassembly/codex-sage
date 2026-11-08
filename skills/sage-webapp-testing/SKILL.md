---
name: sage-webapp-testing
description: Verify browser behavior and reproduce UI regressions using the project test stack.
---

Use existing browser tooling or the project's Playwright tests. Inspect scripts,
server ports, fixtures, and authentication setup before starting another server.
Reuse an available browser plugin when sufficient; MCP is optional, not a required
second installation. Avoid mixing native browser and test-runner state blindly.
Wait on a meaningful readiness signal and use stable role/label/test-id selectors.
Test the actual user path, loading/error states, and relevant viewport behavior.
Capture console/network failures and inspect screenshots when layout is material.
For a bug, obtain a failing reproduction before a fix where practical. Avoid
sleep-based flakiness and tests that merely mirror component internals. Clean up
only processes created by this test; leave unrelated services running.
Do not use real customer data or submit external forms outside the task's scope.
Report browser/version, command, assertions, and artifacts that were inspected.
