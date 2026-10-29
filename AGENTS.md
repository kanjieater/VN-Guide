# Agent entry point

VN Guide is maintained primarily by repository/browser agents working directly with files, web sources, pull requests, comments, and issues.

Read these in order:

1. [agents/guide-standards.md](agents/guide-standards.md) — canonical source, schema, review, invalidation, and completion rules.
2. [agents/guide-author.md](agents/guide-author.md) — research, authoring, and correction role.
3. [agents/authoring-contracts.md](agents/authoring-contracts.md) — concrete research/route JSON shapes and phase/output boundaries.
4. [agents/guide-reviewer-structural.md](agents/guide-reviewer-structural.md) — independent route-flow review.
5. [agents/guide-reviewer-accuracy.md](agents/guide-reviewer-accuracy.md) — independent Japanese-source accuracy review.
6. [agents/guide-review.md](agents/guide-review.md) — orchestration and handoff rules.

Use the capabilities available in the current environment. Shell commands are conveniences, not workflow requirements.

Keep author, structural-review, and accuracy-review work in separate contexts. Do not self-approve.

For new games, create `<slug>/catalog.json` beside `guide.json` (see README). Do not edit `games.json`, the root `index.html`, or generated per-game HTML/manifests in guide PRs. CI generates these at build/deployment time. `games.json` remains a compatibility catalog for existing entries. Run `bun run generate` locally to preview, but generated artifacts are not PR-owned.
