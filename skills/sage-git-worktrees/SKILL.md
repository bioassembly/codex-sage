---
name: sage-git-worktrees
description: Create or reuse an isolated Git worktree for concurrent work or a requested separate checkout.
---

Inspect repository instructions, current branch/status, and `git worktree list`
before selecting a path and base ref. Reuse a suitable existing worktree. Choose
the base from the task, not an assumed default branch; uncommitted changes are
not copied. Keep independent writers in separate worktrees or disjoint files.

Use a writable, unoccupied location. If the path is inside the repository, ensure
it is ignored before creating the worktree. Record its path, branch, and base
commit. Use the project's normal dependency setup and run the relevant baseline
checks before interpreting new failures. Do not copy credentials or unrelated
runtime state into another checkout.
Integrate through the repository's normal review/merge flow. Before cleanup,
inspect for uncommitted work and ensure required commits remain reachable.
Never force-remove a dirty worktree or prune unrelated work to complete the task.
