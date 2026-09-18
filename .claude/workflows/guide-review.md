# VN Guide Review Workflow

The canonical rules are in `.claude/guide-standards.md`. This file describes orchestration.

The workflow is environment-neutral: a role may use a checkout, repository API, connected app, browser, or other available tooling. Command examples are optional conveniences; the required state transitions are what matter.

## Review destination

Before reviewing a route, first honor any review transport explicitly specified by the caller/orchestrator.

If none is specified:

- **Open PR, direct/manual agent review:** put review findings and author fixes on that PR instead of creating route-review issue spam.
- **No open PR:** use the existing issue workflow.

The local automated runner explicitly requests issue-based review, so its issue transport takes precedence over the direct-agent PR default.

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
Did accuracy-stage fixes change route structure?
   │ yes
   └────────────→ rerun Structural → Accuracy
   │ no
   ↓
Both gates clean for the same route content
        ↓
Accuracy stage/orchestrator sets reviewed: true
```

For direct PR review, a clean pass can be recorded with a concise PASS comment. In issue fallback mode, a clean first pass creates no issue.

## Direct PR review content binding

PR feedback is an audit surface, so clean direct/manual review records must identify the exact content reviewed.

- Structural PASS/resolution records include the current route-file blob SHA/content hash.
- Accuracy PASS/resolution records include the current route-file blob SHA/content hash **and** current `research.json` blob SHA/content hash.
- Before final approval, fetch current identifiers again. Any mismatch invalidates the corresponding earlier clean record and requires re-review.
- Final `reviewed: true` requires structural and accuracy clean records that both apply to the current route content, and an accuracy record that applies to the current research content.

This prevents stale browser-agent PASS comments from surviving later commits without turning PR comments into automated runtime state.

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

- structural route changes invalidate structural + accuracy **whenever those gates have already passed, even if `reviewed:false`**;
- factual/source changes invalidate accuracy only unless structure also changed;
- research source-basis/prerequisite/order changes invalidate accuracy for affected routes;
- portrait/title/display-only metadata does not invalidate review.

Do not rerun structural review merely because source metadata changed if no route structure changed.

## Pre-merge consistency check

Before a guide change is considered complete, verify tracked generated artifacts are synchronized with their source data.

For example, if `games.json` changes `has_guide` or other landing-visible metadata, root `index.html` must be regenerated or equivalently synchronized according to `scripts/generate.py` and the landing template. This applies even when the reviewing/authoring agent cannot execute the local Python runner.

This is a repository-consistency check, not a reason to redesign the local orchestration.

## Automated orchestration

`scripts/review.py` remains the local issue-based orchestrator. This PR makes one targeted correctness change to it: after structural review passes, the runner snapshots the route's structural signature; if accuracy-stage corrections change that signature, it reruns structural review and then accuracy review before allowing `reviewed: true`. The final mark-reviewed gate also checks both structural and accuracy blockers.

This does not move PR-comment state into the local runner and does not require browser/repository agents to execute the Python orchestration.

Focused regression tests live in `tests/test_review.py` and cover:

- unchanged route structure → one structural + one accuracy pass;
- structural changes during accuracy correction → structural + accuracy rerun;
- source-only / `enGuide` edits → unchanged structural signature;
- open structural blocker → refuse `reviewed: true`.
