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

- `jpGuide1` is verbatim text from Set A.
- `jpGuide2` is verbatim text from Set B when that exact step is printed there.
- If Set B supports the route/ending semantically but does not print that exact step, use exactly `（第二ガイドに記載なし）`.
- Never copy Set A text into `jpGuide2`.
- Preserve whitespace and punctuation exactly when quoting a source.

## Route step semantics

- `badEndPath` marks the first wrong choice of a bad-end detour.
- `isLoad: true` is reserved **only** for the load that terminates a `badEndPath` detour and returns to the main route.
- A normal instruction to load a save created in an earlier route is a plain step. Its `simpleJp` may say `セーブNにロード`, but it must **not** have `isLoad: true`.
- Save slot numbers are sequential across the recommended play order.
- Do not invent saves. Include a save when at least one primary set explicitly documents it.

## Review destination and blocking state

Prefer one review ledger over per-route issue spam.

### When an open PR exists for the work

Use that PR for all structural and accuracy review records. Do **not** create route review issues.

Each reviewer posts a top-level PR comment containing a stable machine-readable marker:

```
<!-- vn-guide-review:<type>:<slug>:<route_id> -->
Status: PASS
```

where `<type>` is `structural` or `accuracy`.

Allowed statuses:

- `PASS` — clean first pass.
- `CHANGES_REQUESTED` — blocking findings follow in the same comment.
- `RESOLVED` — a previous `CHANGES_REQUESTED` record was independently re-verified after an author fix.

For a route/type pair, the **latest marked PR comment is authoritative**.

The author reports a fix on the same PR using:

```
<!-- vn-guide-fix:<type>:<slug>:<route_id> -->
Fixed: <concise summary>
```

The author never posts `PASS` or `RESOLVED`.

When a later edit invalidates a completed gate according to the invalidation matrix, record that on the same PR:

```
<!-- vn-guide-invalidate:<type>:<slug>:<route_id> -->
Reason: <what changed>
```

A review record is valid only when it is newer than the latest invalidation marker for that route/type. Structural changes invalidate both structural and accuracy review; factual/source changes invalidate accuracy only.

Do not run multiple reviewers of the same type against the same route concurrently.

### When no open PR exists

Fall back to the issue workflow:

- at most one open `route-structure` issue per route;
- at most one open `route-accuracy` issue per route;
- clean first passes create no issue;
- findings are fixed by the author and closed only by the owning reviewer after re-verification.

Before creating a fallback issue, check for an existing one and re-check immediately before creation.

### Blocking definition

- In PR mode, `CHANGES_REQUESTED` is blocking; `PASS` or `RESOLVED` is clean.
- In issue fallback mode, an open issue of the corresponding review type is blocking.

## Review lifecycle

For each unreviewed route:

1. Structural reviewer performs a fresh structural review.
2. Record the result on the open PR when one exists; otherwise use issue fallback for findings.
3. If structural changes are requested, the author fixes them and reports the fix to the same review destination.
4. Structural reviewer independently re-verifies and records `RESOLVED` on the PR or closes the fallback issue.
5. Accuracy reviewer independently verifies both Japanese verification sets.
6. Record the result on the open PR when one exists; otherwise use issue fallback for findings.
7. If accuracy changes are requested, the author fixes them and reports the fix to the same review destination.
8. Accuracy reviewer re-fetches sources, re-verifies, and records `RESOLVED` on the PR or closes the fallback issue.
9. Once both route gates are clean, the accuracy stage/orchestrator sets `reviewed: true`.

The author and structural reviewer never set `reviewed: true`.

If an old fallback review issue already exists when PR mode begins, do not silently ignore an unresolved finding. Carry any unresolved finding into the PR review record and resolve/close the legacy issue before final approval.

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
- its active review destination has no blocker (`CHANGES_REQUESTED` in PR mode, or an open fallback issue),
- no unresolved legacy review issue remains, and
- `reviewed: true`.

A game is fully reviewed only when every route satisfies that gate.
