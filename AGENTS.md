# Generic Agent Entry Point

This repository supports local coding agents, browser/repository agents, connected-app agents, and other environments.

Start with the committed canonical rules:

- `.claude/guide-standards.md` — source requirements, guide shape, review gates, invalidation, and completion rules.
- `.claude/agents/guide-author.md` — author/generation/correction role.
- `.claude/agents/guide-reviewer-structural.md` — structural review role.
- `.claude/agents/guide-reviewer.md` — Japanese-source accuracy review role.
- `.claude/workflows/guide-review.md` — orchestration/lifecycle reference.

Use the capabilities available in the current environment; shell and `gh` examples are not requirements.

If the caller/orchestrator explicitly specifies where review state or findings must be recorded, that transport instruction takes precedence over the default direct-agent PR workflow.

Do not combine author and reviewer roles in one session.
