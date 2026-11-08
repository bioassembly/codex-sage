---
name: sage-review
description: Review a working diff or pull request for concrete defects and regression risks.
---

Establish the base and target diff, read repository guidance, and follow changed
behavior into callers and tests. Review correctness, security boundaries, partial
failures, concurrency, data compatibility, and meaningful missing tests as relevant.
Use sage-reviewer for an independent bounded pass when delegation is available and
appropriate; do not give it the desired conclusion. Avoid simultaneous writes.
Return only actionable findings supported by a concrete trigger and consequence,
with file and line. Distinguish introduced regressions from existing issues.
Do not edit during a review-only request or publish review comments without scope
for that action. If no findings survive inspection, say so and identify validation
limits. A clean static review does not imply tests ran or behavior is proven.
