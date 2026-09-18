# VN Guide Review Workflow

The canonical rules are in `.claude/guide-standards.md`. This file describes orchestration.

The workflow is environment-neutral: a role may use a checkout, repository API, connected app, browser, or other available tooling. Command examples are optional conveniences; the required state transitions are what matter.

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

A clean first-pass reviewer **does not create a PASS issue**. The absence of a blocking issue plus the completed reviewer run is the clean result.

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
```

These are convenience examples for environments with the local runner. Other environments should perform the same role transitions with their available repository and issue tools.
