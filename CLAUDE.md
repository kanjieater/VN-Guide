# VN Guide — Agent Instructions

Read `.claude/guide-standards.md` first. It is the committed source of truth for guide generation, source requirements, review roles, review transport, invalidation, and completion gates.

`prompt.md` may be injected by the local generation runner as additional generation guidance. The committed `.claude/guide-standards.md` remains the portable workflow/source-quality contract for agents that do not have access to that local file; local guidance must not weaken it.

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
- For direct agent review, use an existing PR for feedback instead of creating route-review issue spam; automated runners may retain their existing review transport.
- `reviewed: true` is set only after the structural and accuracy gates are clean.
- When reviewed content changes, apply the invalidation matrix in `.claude/guide-standards.md` rather than blindly rerunning or preserving every gate.

Shell commands in repository docs are examples, not requirements. Use the repository, web, file, PR/review, and issue capabilities available in the current environment while preserving the required role boundaries and quality gates.
