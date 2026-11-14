---
name: sage-git-commit
description: Prepare authorized commits or pushes with repository-specific history, scoped staging, and verification.
---

Inspect instructions, branch/upstream, recent commit subjects, and the complete
working diff. Infer the established commit style; do not impose Conventional
Commits where the project uses another format. Stage only the intended files or
hunks. Inspect the staged diff for accidental scope, generated state, credentials,
and private data. Run required checks before committing and report what ran.

Describe the concrete change and its purpose in the subject and, where useful,
the body. Respect existing user edits. A request to commit authorizes that commit;
a request to push authorizes the associated normal push. Verify the result and
remote branch afterward. Do not amend shared history, force-push, or change Git
identity/remotes as a routine workaround. Keep multiline messages in a file or a
structured argument to preserve literal content safely.
