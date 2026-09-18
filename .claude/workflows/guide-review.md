# VN Guide Review Workflow

The canonical rules are in `.claude/guide-standards.md`. This file describes orchestration.

The workflow is environment-neutral: a role may use a checkout, repository API, connected app, browser, or other available tooling. Command examples are optional conveniences; the required state transitions are what matter.

## Review destination

Before reviewing a route, determine whether the current work has an open pull request.

- **Open PR:** use that single PR as the review ledger for every route. Structural and accuracy reviewers post marked status comments there; authors post marked fix comments there. Do not create route review issues.
- **No open PR:** use the fallback issue workflow.

In PR mode, the latest marked comment for a route/type is authoritative. `CHANGES_REQUESTED` blocks; `PASS` and `RESOLVED` are clean.

## Per-route lifecycle

```
Author generates/corrects route
        ↓
reviewed: false
        ↓
Structural reviewer (fresh context)
        ↓
findings? ── yes → one route-structure issue
   │                     ↓
   no                 Author fixes + comments
   │                     ↓
   │              Structural reviewer re-verifies
   │                     ↓
   │                 reviewer closes
   ↓
Accuracy reviewer (fresh context)
        ↓
findings? ── yes → one route-accuracy issue
   │                     ↓
   no                 Author fixes + comments
   │                     ↓
   │               Accuracy reviewer re-fetches
   │               sources and re-verifies
   │                     ↓
   │                 reviewer closes
   ↓
No open structural/accuracy blocker
        ↓
Accuracy stage/orchestrator sets reviewed: true
```

In PR mode, a clean first pass posts a marked `PASS` comment so the PR contains an auditable review ledger. In issue fallback mode, a clean first pass creates no issue.

## Concurrency

Review routes one at a time per review type.

Never run two structural reviewers or two accuracy reviewers concurrently for the same route. Before creating a blocking issue, check for an existing open issue of that type and re-check immediately before creation.

This prevents duplicate issue races and keeps one canonical thread per gate.

## Author/reviewer ownership

- Author creates/fixes route content and comments on findings.
- Structural reviewer owns structural verification and closing structural issues.
- Accuracy reviewer owns source verification and closing accuracy issues.
- Author never closes review issues.
- Author and structural reviewer never set `reviewed: true`.

## Re-review scope

Use the invalidation matrix in `.claude/guide-standards.md`.

In particular:

- structural route changes invalidate structural + accuracy;
- factual/source changes invalidate accuracy only unless structure also changed;
- research source-basis/prerequisite/order changes invalidate accuracy for affected routes;
- portrait/title/display-only metadata does not invalidate review.

Do not rerun structural review merely because source metadata changed if no route structure changed.

## Automated orchestration

`scripts/review.py` implements the same lifecycle with fresh role invocations.

Useful scoping variables:

```bash
GUIDE_REVIEW_VID=v1715 python3 scripts/review.py
GUIDE_REVIEW_VID=v1715 GUIDE_REVIEW_ROUTE=okita python3 scripts/review.py
GUIDE_REVIEW_PR=123 GUIDE_REVIEW_VID=v1715 python3 scripts/review.py
```

`GUIDE_REVIEW_PR` explicitly binds the local orchestrator to an open PR when branch-based PR discovery is unavailable (for example, a detached checkout).

These are convenience examples for environments with the local runner. Other environments should perform the same role transitions with their available repository and issue tools.
