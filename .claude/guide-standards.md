# VN Guide Standards

These are the canonical, environment-neutral rules for guide generation and review.

Agents may work through a checkout, repository API, connected app, browser, or another execution environment. Shell and `gh` examples elsewhere in the repo are examples only. Use whatever file, web, issue, and repository capabilities are available while preserving the same state transitions and role boundaries.

A local `prompt.md`, when present, is an optional runtime supplement. It may add game-generation detail but must not weaken or replace these committed standards.

## Roles

Keep these roles independent:

1. **Author** — researches, generates, and fixes guide content.
2. **Structural reviewer** — checks route-file flow only. Does not fetch walkthroughs or edit guide content.
3. **Accuracy reviewer** — independently checks the guide against Japanese sources. Does not fix route content.
4. **Review orchestrator** — may coordinate fresh role sessions and update review state after a clean pass.

Do not combine author and reviewer roles in one session.

## Research/source gate

Do not generate route content until the research gate passes.

A game requires **two independent Japanese verification sets**:

- **Set A** should be the detailed primary walkthrough used for exact step/save text.
- **Set B** must independently cover the full route structure: every route-defining decision, route prerequisite/unlock, and ending used by the guide.
- A verification set may be one page or multiple Japanese pages. If multiple pages are needed, document every component in `research.json` and explain what each component covers.
- A translation, derivative guide, or page that merely cites Set A does not count as an independent Set B.
- A source that cannot be directly inspected does not count toward the gate. It may be listed for provenance only.
- If the two-set gate cannot be satisfied, stop after research and document the blocker. Do not invent or infer missing guide content.

"Cross-validate" means reconcile the two sets, not require identical coverage of every formatting detail. Every route choice, prerequisite/unlock, and ending must be independently supported by both sets. A save point or repeated UI action may appear in only one set; in that case include it only when explicitly documented and mark the other source field as not documented rather than fabricating text.

## Source fields

Every route step must have **non-empty** `jpGuide1` and `jpGuide2`.

- `jpGuide1` must be exact verbatim text from Set A for that step.
- Set A is the detailed primary walkthrough. If a required guide step has no exact Set-A text, the source assignment is insufficient: find a directly inspectable Set-A source that documents the step or stop and document the blocker. Never leave `jpGuide1` empty and never invent a Set-A placeholder.
- `jpGuide2` must be exact verbatim text from Set B when that exact step is printed there.
- If Set B independently supports the surrounding route/ending but does not print that exact step, use exactly `（第二ガイドに記載なし）`.
- `（第二ガイドに記載なし）` is the only permitted missing-source placeholder.
- Never copy Set A text into `jpGuide2`.
- Preserve whitespace and punctuation exactly when quoting a source.

## Route step semantics

- `badEndPath` marks the first wrong choice of a bad-end detour.
- `isLoad: true` is reserved **only** for the load that terminates a `badEndPath` detour and returns to the main route.
- A normal instruction to load a save created in an earlier route is a plain step. Its `simpleJp` may say `セーブNにロード`, but it must **not** have `isLoad: true`.
- Save slot numbers are sequential across the recommended play order.
- Do not invent saves. Include a save when at least one primary set explicitly documents it.

### Bad-end completeness

Every bad end documented by the Japanese verification sets must be actively included before continuing the main route.

For each documented bad end:

- insert the save before the branch when a source documents one;
- mark the **first wrong choice** with `badEndPath`;
- use the exact bad-end label documented by the source;
- include every subsequent step needed to reach the bad-end terminal;
- immediately follow the terminal with the matching `isLoad: true` load-back step;
- then continue with the good/main choice;
- if multiple bad ends branch from the same save, include every documented bad-end detour before continuing;
- never add `badEndPath` where no Japanese source documents a bad end;
- never invent a bad-end label or terminal.

## Review feedback destination

Keep review feedback consolidated when possible, but do not make the feedback transport itself a second approval-state system.

### When an open PR exists for the work

For direct/manual agent review, put structural and accuracy findings on the existing PR instead of creating per-route review issues. Keep each route/type clearly identified in the comment so the author and re-reviewer can follow the thread.

- Clean review: leave a concise PASS comment for that route/type.
- Findings: leave one detailed CHANGES REQUESTED comment for that route/type.
- Author corrections: reply/comment on the same PR with what changed.
- Re-review: confirm the findings are resolved on the same PR, or state precisely what remains.

Do not launch multiple reviewers of the same type against the same route concurrently.

PR comments are an audit trail and collaboration surface; they are **not** a machine-readable replacement for `reviewed` or for whatever persistence mechanism an automated orchestrator already uses.

### When no open PR exists

Use the existing issue workflow:

- at most one open `route-structure` issue per route;
- at most one open `route-accuracy` issue per route;
- clean first passes create no issue;
- findings are fixed by the author and closed only by the owning reviewer after re-verification.

Before creating an issue, check for an existing one and re-check immediately before creation.

### Automated orchestrators

An automated runner may keep its existing transport/persistence mechanism. It must still enforce the same role separation, review gates, evidence requirements, and `reviewed` semantics. These standards do not require a particular shell command, API, issue format, or local process.

## Review lifecycle

For each unreviewed route:

1. Structural reviewer performs a fresh structural review.
2. If structural findings exist, the author fixes them and the structural reviewer independently re-verifies.
3. Accuracy reviewer independently verifies both Japanese verification sets.
4. If accuracy findings exist, the author fixes them and the accuracy reviewer re-fetches sources and independently re-verifies.
5. Once both route gates are clean, the accuracy stage/orchestrator sets `reviewed: true`.

Use the open PR for direct-agent feedback when one exists; otherwise use the existing issue workflow. Automated runners may retain their own transport.

The author and structural reviewer never set `reviewed: true`.

## Review invalidation

When already-reviewed content changes, invalidate only the gates affected:

| Change | Set reviewed:false? | Structural re-review | Accuracy re-review |
| --- | --- | --- | --- |
| Route step order, `badEndPath`, `isLoad`, save/load structure | Yes, affected route | Yes | Yes |
| Route choice/source text/save position/ending content without structural change | Yes, affected route | No | Yes |
| Research source basis, prerequisites, unlocks, or route-order claims | Yes, affected routes | No unless route files changed structurally | Yes |
| Portrait/title/display-only metadata | No | No | No |
| Issue labels/comments/duplicate cleanup only | No | No | No |

If uncertain whether a route-content change is structural, rerun structural review.

## Completion gate

A route is complete only when:

- its structural review is clean,
- its accuracy review is clean against both Japanese verification sets,
- all reviewer findings for the active review have been independently re-verified as resolved, and
- `reviewed: true`.

A game is fully reviewed only when every route satisfies that gate.
