# VN Guide Review Workflow

The canonical rules are in `.claude/guide-standards.md`. This file describes orchestration.

The workflow is environment-neutral: a role may use a checkout, repository API, connected app, browser, or other available tooling. Command examples are optional conveniences; the required state transitions are what matter.

## Review destination

Before reviewing a route, determine whether the current work has an open pull request.

- **Open PR, direct/manual agent review:** put review findings and author fixes on that PR instead of creating route-review issue spam.
- **No open PR:** use the existing issue workflow.
- **Automated runner:** it may retain its existing persistence/issue mechanism; this PR does not redesign the local runner.

## Per-route lifecycle

```
Author generates/corrects route
        ↓
reviewed: false
        ↓
Structural reviewer (fresh context)
        ↓
findings? ── yes → PR feedback or fallback issue
   │                     ↓
   no                 Author fixes + reports
   │                     ↓
   │              Structural reviewer re-verifies
   ↓
Accuracy reviewer (fresh context)
        ↓
findings? ── yes → PR feedback or fallback issue
   │                     ↓
   no                 Author fixes + reports
   │                     ↓
   │               Accuracy reviewer re-fetches
   │               sources and re-verifies
   ↓
No open structural/accuracy blocker
        ↓
Accuracy stage/orchestrator sets reviewed: true
```

For direct PR review, a clean pass can be recorded with a concise PASS comment. In issue fallback mode, a clean first pass creates no issue.

## Concurrency

Review routes one at a time per review type.

Never run two structural reviewers or two accuracy reviewers concurrently for the same route. Before creating a fallback blocking issue, check for an existing open issue of that type and re-check immediately before creation.

This prevents duplicate issue races and keeps one canonical thread per gate.

## Author/reviewer ownership

- Author creates/fixes route content and comments on findings.
- Structural reviewer owns structural verification and resolution of structural findings.
- Accuracy reviewer owns source verification and resolution of accuracy findings.
- In issue fallback mode, only the owning reviewer closes the issue.
- Author and structural reviewer never set `reviewed: true`.

## Re-review scope

Use the invalidation matrix in `.claude/guide-standards.md`.

In particular:

- structural route changes invalidate structural + accuracy;
- factual/source changes invalidate accuracy only unless structure also changed;
- research source-basis/prerequisite/order changes invalidate accuracy for affected routes;
- portrait/title/display-only metadata does not invalidate review.

Do not rerun structural review merely because source metadata changed if no route structure changed.

## Pre-merge consistency check

Before a guide change is considered complete, verify tracked generated artifacts are synchronized with their source data.

For example, if `games.json` changes `has_guide` or other landing-visible metadata, root `index.html` must be regenerated or equivalently synchronized according to `scripts/generate.py` and the landing template. This applies even when the reviewing/authoring agent cannot execute the local Python runner.

This is a repository-consistency check, not a reason to redesign the local orchestration.

## Automated orchestration

`scripts/review.py` remains unchanged by this workflow refactor. It is one local implementation of the same author → structural review → accuracy review gates and may continue using its existing issue-based persistence.

The portable Markdown rules govern quality and role behavior across environments; they do not require browser/repository agents to execute the local Python runner.
