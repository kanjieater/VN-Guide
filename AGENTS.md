# Agent entry point

VN Guide is maintained primarily by repository/browser agents working directly with files, web sources, pull requests, comments, and issues.

Read these in order:

1. [agents/guide-standards.md](agents/guide-standards.md) — canonical source, schema, review, invalidation, and completion rules.
2. [agents/guide-author.md](agents/guide-author.md) — research, authoring, and correction role.
3. [agents/guide-reviewer-structural.md](agents/guide-reviewer-structural.md) — independent route-flow review.
4. [agents/guide-reviewer-accuracy.md](agents/guide-reviewer-accuracy.md) — independent Japanese-source accuracy review.
5. [agents/guide-review.md](agents/guide-review.md) — orchestration and handoff rules.

Use the capabilities available in the current environment. Shell commands are conveniences, not workflow requirements.

Keep author, structural-review, and accuracy-review work in separate contexts. Do not self-approve.

When `games.json` or shared templates change, run `bun run generate` (or make exactly equivalent deterministic updates if Bun is unavailable). CI runs `bun run generate:check` to ensure tracked generated artifacts are synchronized.
