# Skill provenance

The `sage-*` skills are concise, independently written adaptations of workflows
already configured in the owner's sibling harnesses. No external skill installer
or vendored executable is run during installation. Public documentation links
are retrieval entry points, not copied manuals or claims of executed validation.

Reviewed 2026-11-08 against the local clean source checkouts before adaptation:

- [antigravity-sage](https://github.com/bioassembly/antigravity-sage/tree/9cf97f110b91b246a15ac0d5b6fdd619f922080e)
- [opencode-sage](https://github.com/bioassembly/opencode-sage/tree/ed79b38ee1d005cfabbcb8eecef13ce95eebbd6a)

| Codex skill | Source workflow or inspiration |
| --- | --- |
| sage-checkpoint | Antigravity checkpoint; OpenCode structured task notes |
| sage-debug | systematic-debugging; evidence-gated verification |
| sage-design | codebase-design, domain-modeling, grill-me |
| sage-spec | to-spec; scope-preserving local drafting |
| sage-tickets | to-tickets; vertical slices and blocking edges |
| sage-review | reviewer persona and review workflow |
| sage-genomics | nextflow and bioinformatician; official Nextflow/nf-core documentation |
| sage-sequence-analysis | biopython and pysam; official package documentation and hts-specs |
| sage-scientific-report | statistical-data-visualization, first-principles-explainer, FAIR provenance |
| sage-results-package | pipeline-sketch-results; separate client and reproducible research deliverables |
| sage-binary-inspection | reverse-engineer-anything; task-relevant static inspection without automatic installs |
| sage-overnight | overnight-explorer; bounded experiments, falsification, reproducible methods |
| sage-security-audit | security-audit; concrete threat paths and evidence |
| sage-webapp-testing | webapp-testing; existing browser infrastructure first |
| sage-harness-eval | skill-evaluation and OpenCode evaluation loop |

The source registries credit obra/superpowers, mattpocock/skills, K-Dense-AI,
anthropics/skills, and self-authored procedures. This repository ships rewritten
procedural guidance rather than their large manuals or code bundles. Codex's
built-in skill creator/installer and OpenAI documentation skills remain authoritative
for their native workflows; SAGE does not install duplicates of them.
