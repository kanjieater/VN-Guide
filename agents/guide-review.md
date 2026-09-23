# VN Guide Review Workflow

The canonical rules are in `agents/guide-standards.md`. This file describes orchestration.

The workflow is environment-neutral: a role may use a checkout, repository API, connected app, browser, or other available tooling. Command examples are optional conveniences; the required state transitions are what matter.

## Review destination

Before reviewing a route, first honor any review transport explicitly specified by the caller/orchestrator.

If none is specified:

- **Open PR, direct/manual agent review:** put review findings and author fixes on that PR instead of creating route-review issue spam.
- **No open PR:** use the existing issue workflow.


## Explicit guide target

Before generation/research:

1. Read `games.json.guide_target` or an explicit caller-supplied target.
2. Require `label`, `platform`, and a specific release/edition `url`.
3. Require caller-supplied targets to be scoped to the exact VN work id; never carry that target into another pending game.
4. Persist accepted caller-supplied targets to `games.json` before research.
5. Copy the exact same object into `research.json` and `guide.json`.
6. Stop rather than infer when no target is supplied.

When VNDB represents multiple releases under one `v...` work, use the specific intended `r...` release link when available. A change to the guide target invalidates the existing research basis and all route reviews.

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

Use the invalidation matrix in `agents/guide-standards.md`.

In particular:

- structural route changes invalidate structural + accuracy **whenever those gates have already passed, even if `reviewed:false`**;
- factual/source changes invalidate accuracy only unless structure also changed;
- research source-basis/prerequisite/order changes invalidate accuracy for affected routes;
- portrait/title/display-only metadata does not invalidate review.

Do not rerun structural review merely because source metadata changed if no route structure changed.

## Pre-merge consistency check

Before a guide change is considered complete, verify tracked generated artifacts are synchronized with their source data.

For example, if `games.json` changes `has_guide` or other landing-visible metadata, root `index.html` must be regenerated or equivalently synchronized according to `tools/generate.mjs` and the landing template. Run `bun run generate` after changing landing-visible repository metadata. The Bun repository-contract tests reject stale generated artifacts.

