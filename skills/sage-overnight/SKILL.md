---
name: sage-overnight
description: Run a bounded unattended exploration of a codebase, dataset, benchmark, or research question.
---

Establish the objective, time/resource budget, allowed mutations, and stop condition
from the request. Choose useful independent hypotheses, keep a queue, and pivot
when an avenue lacks signal. Do not infer unlimited compute from unattended work.
Discover installed tools, data provenance, active jobs, and resource availability.
Preserve raw inputs; write scripts and results to isolated scratch/analysis space.
For each finding record the claim, exact evidence, an attempted falsification,
limitations, and the next useful action. Seek independent evidence for major
claims; label single-source leads as provisional. Log refuted hypotheses too.
Checkpoint after each material branch with sage-checkpoint so interruptions preserve
progress. Deliver FINDINGS_REPORT.md and ANALYSIS_METHODS.md (or existing project
equivalents) containing ranked supported findings and reproducible commands.
Do not publish, spend beyond the agreed budget, alter live services, or silently
continue cloud escalation when the user requested local/free computation.
