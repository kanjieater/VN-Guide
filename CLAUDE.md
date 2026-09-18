# VN Guide — Agent Instructions

Read `.claude/guide-standards.md` first. It is the committed source of truth for guide generation, source requirements, review roles, review transport, invalidation, and completion gates.

A local `prompt.md`, if present, is an optional runtime supplement. It is not required to understand the repository workflow and must not override the committed standards.

## Roles

- **Guide Author:** `.claude/agents/guide-author.md`
- **Structural Reviewer:** `.claude/agents/guide-reviewer-structural.md`
- **Accuracy Reviewer:** `.claude/agents/guide-reviewer.md`
- **Workflow:** `.claude/workflows/guide-review.md`

Keep author, structural-review, and accuracy-review work in separate sessions/contexts.

## Non-negotiable gates

- Research must satisfy the two-independent-Japanese-verification-set gate before route generation.
- Authors never self-approve or resolve reviewer-owned blockers.
- `isLoad: true` is only for terminating a bad-end detour; ordinary cross-route load instructions are plain steps.
- Do not run concurrent reviewers of the same type for the same route.
- When an open PR exists, review state is recorded on that PR; route review issues are fallback-only.
- `reviewed: true` is set only after the structural and accuracy gates are clean.
- When reviewed content changes, apply the invalidation matrix in `.claude/guide-standards.md` rather than blindly rerunning or preserving every gate.

Shell commands in repository docs are examples, not requirements. Use the repository, web, file, PR/review, and issue capabilities available in the current environment while preserving the required workflow state.
