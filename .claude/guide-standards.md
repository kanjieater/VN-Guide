# VN Guide Standards

These are the canonical, environment-neutral rules for guide generation and review.

Agents may work through a checkout, repository API, connected app, browser, or another execution environment. Shell and `gh` examples elsewhere in the repo are examples only. Use whatever file, web, issue, and repository capabilities are available while preserving the same state transitions and role boundaries.

`prompt.md` may be supplied by the local generation runtime as additional generation guidance. Agents that can access it should read it. Agents that cannot access that local file still have the complete portable workflow and quality gates in this committed standard. Local guidance must not weaken or replace these standards.

## Roles

Keep these roles independent:

1. **Author** — researches, generates, and fixes guide content.
2. **Structural reviewer** — checks route-file flow only. Does not fetch walkthroughs or edit guide content.
3. **Accuracy reviewer** — independently checks the guide against Japanese sources. Does not fix route content.
4. **Review orchestrator** — may coordinate fresh role sessions and update review state after a clean pass.

Do not combine author and reviewer roles in one session.

## Research/source gate

Do not generate route content until the research gate passes.

A game requires an **explicit linked guide target** plus two independent Japanese verification sets that apply to that exact target.

### Guide target

Do **not** infer an arbitrary target from the VNDB work id alone. A single VNDB `v...` work may aggregate materially different original releases, remakes, ports, editions, and localizations.

Before research begins, resolve:

```json
"guide_target": {
  "label": "specific edition/release name",
  "platform": "specific platform",
  "url": "https://authoritative.example/specific-release"
}
```

Rules:

- `games.json.guide_target` is the normal repository source of truth.
- A caller may explicitly supply the same three target fields for a new guide, but the override must also be scoped to the exact VN work id (the local runner uses `GUIDE_TARGET_VID`). A caller target for one VN must never be reused for another pending game. Persist the accepted target to `games.json` before research so later local/browser agents see the same target.
- If neither the repository nor caller supplies a target, default to the **newest official complete release that includes native Japanese in-game text**, using release-specific metadata such as VNDB releases rather than guessing from the broad work entry. This keeps `simpleJp` valid for the target while preferring the newest applicable edition/platform.
- If the newest applicable Japanese release is ambiguous (for example multiple distinct releases on the same newest date, a multi-platform release that cannot be made platform-specific, or insufficient release metadata), stop and request an explicit target instead of choosing arbitrarily.
- `label`, `platform`, and `url` are all required and non-empty.
- The URL should identify the **specific intended release/edition**, not merely the broad work. When VNDB contains the exact target release, prefer its `https://vndb.org/r...` release page over the broader `v...` work page.
- Once a default target is resolved, persist it to `games.json` before research exactly like a caller-supplied target.
- Copy the exact target into `research.json.guide_target` and later into `guide.json.guide_target`.
- Verify every Set A/B component applies to that exact target, or document version differences and why they do not affect the guide.
- If the requested target cannot be verified or available walkthroughs apply to a materially different release, stop and document the blocker rather than silently switching targets.

### Legacy target migration

For existing guides that predate `guide_target`, use the same target resolution policy instead of preserving ambiguity indefinitely.

- Existing reviewed flags are not invalidated **solely** because this field was absent historically.
- Before any new source-dependent generation, correction, or accuracy re-review, the guide must receive a persisted target. If no explicit target exists, resolve the newest unambiguous official complete Japanese release as above.
- If the target backfill merely formalizes the exact release already unambiguously documented in the existing research/sources, the backfill itself is metadata-only and does not invalidate route review.
- If the old research is ambiguous, or the target changes to a different release/platform/edition, redo research for the new target and invalidate all affected route reviews.

Then apply these source roles:

- **Set A** should be the detailed primary walkthrough used for exact step/save text.
- **Set B** must independently cover the full **main-route structure**: every route-defining decision, route prerequisite/unlock, and route/main ending used by the guide. Optional non-main ending detours (bad, normal, alternate, or similarly labeled endings) are handled separately below and may be documented by only one primary set when the other is silent and non-contradictory.
- A verification set may be one page or multiple Japanese pages. If multiple pages are needed, document every component in `research.json` and explain what each component covers.
- A translation, derivative guide, or page that merely cites Set A does not count as an independent Set B.
- A source that cannot be directly inspected does not count toward the gate. It may be listed for provenance only.
- If the two-set gate cannot be satisfied, stop after research and document the blocker. Do not invent or infer missing guide content.
- Legacy `research.json` files may predate explicit `set: "A"` / `set: "B"` fields. For those, use the documented primary-source ordering/notes to identify the two independent Japanese source sets; when the research file is next edited, make the set assignment explicit.

"Cross-validate" means reconcile the two sets, not require identical coverage of every formatting detail. Every **main-route-defining** choice, prerequisite/unlock, and route/main ending must be independently supported by both sets. A save point, repeated UI action, or optional non-main ending detour may appear in only one primary set; include it when explicitly documented and the other set is silent/non-contradictory, and mark the other source field as not documented rather than fabricating text. If the other set contradicts the step/outcome, resolve the conflict before generation.

## Character portraits

Portrait URLs must be directly verified against a character record or another authoritative/structured source.

- Match the route character by name, not by numeric coincidence.
- When using VNDB, use the exact `image.url` returned by the character record.
- VNDB character IDs (for example `c34600`) and VNDB image IDs are separate identifiers. **Never construct a CDN portrait URL by inserting the character ID into an image-path pattern.**
- If the current environment cannot directly inspect VNDB's character image field, use another verifiable character source and document that source in `research.json`.
- A portrait-only correction does not invalidate structural or accuracy route review.

## Source fields

Every route step must have **non-empty** `jpGuide1` and `jpGuide2`.

- `jpGuide1`: exact verbatim Set-A text when Set A prints that step.
- `jpGuide2`: exact verbatim Set-B text when Set B prints that step.
- For a **main-route-defining choice, prerequisite/unlock, or route/main ending**, both verification sets must independently support the fact. If one set cannot support it, the research gate is insufficient and the route cannot pass.
- For a **non-route-defining save, load, repeated UI action, or optional non-main-ending-only step** that is explicitly documented by only one primary set while the other is silent/non-contradictory, keep the useful step and use the symmetric omission placeholder for the other field:
  - Set A missing → exactly `（第一ガイドに記載なし）`
  - Set B missing → exactly `（第二ガイドに記載なし）`
- Those two exact strings are the only permitted missing-source placeholders.
- Never copy one source's text into the other source field.
- Never leave either field empty.
- Preserve source whitespace and punctuation exactly when quoting.


## Route step semantics

### Step shape / `simpleJp`

- Every player-action step uses the **exact in-game choice/action text** in `simpleJp`.
- Do not paraphrase `simpleJp`, append outcome suffixes, or prefix it with location/context text.
- Save and load instructions are the only normal non-choice `simpleJp` steps.
- Keep save steps standalone immediately before the action they protect; do not merge a save and a player action into one step.
- Keep load instructions standalone.
- `enGuide` contains a useful English reference/hint when an English source or reliable reference is available; otherwise use exactly `""`. Do not discard useful existing English detail merely because it is optional.

### Save rules

- Save slot numbers are sequential across the recommended play order.
- Do not invent saves. Include a save when at least one primary set explicitly documents it.
- If sources disagree on the position of the same save/checkpoint, use the **earlier documented position**.
- A save documented by only one set is allowed under the symmetric source-omission rule above.

### Structural terminal

Every `route_<id>.json` is a guide section. Its main-path structural terminal is the section's intended documented terminal/outcome, which may be a heroine ending, chapter ending, true ending, post-clear completion result, or another source-documented terminal appropriate to that section.

Structural review must not require a character/good ending when the section's documented purpose has a different terminal. A linear section with no detours passes structural review when it begins at step 0, contains no orphan structural loads, and ends at its intended documented terminal/outcome.

### Structural markers

- `badEndPath` is the historical field name for the first branch step of any documented non-main ending detour, including bad, normal, alternate, or similarly labeled endings.
- `isLoad: true` is reserved **only** for the load that terminates a `badEndPath` non-main-ending detour and returns to the main route.
- A normal instruction to load a save created in an earlier route is a plain step. Its `simpleJp` may say `セーブNにロード`, but it must **not** have `isLoad: true`.
### Non-main ending detour completeness

Every documented non-main ending detour—bad, normal, alternate, or similarly labeled—explicitly documented by **either** directly inspected primary Japanese verification set must be actively included before continuing the main route when the other set is silent or agrees. One-set detours are allowed; use the source-omission placeholder for the silent set on detour-only steps. If the second set contradicts the existence, branch condition, or outcome of that ending, reconcile the conflict before including it.

For each documented non-main ending detour:

- insert the save before the branch when a source documents one;
- mark the **first wrong choice** with `badEndPath`;
- use the exact ending label documented by the source;
- include every subsequent step needed to reach the ending terminal;
- immediately follow the terminal with the matching `isLoad: true` load-back step;
- then continue with the good/main choice;
- if multiple non-main endings branch from the same save, include every documented detour before continuing;
- never add `badEndPath` where no Japanese source documents a non-main ending;
- never invent an ending label or terminal.

## `guide.json` assembly contract

Direct/browser agents must assemble `guide.json` equivalently to the local generator:

- entries follow `research.json` / recommended order for every completed guide section;
- each entry includes `id`, `title`, `stepCount`, and `reviewed`;
- `stepCount` equals the actual length of `route_<id>.json`;
- preserve an existing route's `reviewed` value when reassembling; new routes default to `false`;
- use the verified portrait from current research, falling back to an existing verified portrait only when research has none;
- copy current research `sources` into `guide.json`;
- copy `research.json.guide_target` into `guide.json.guide_target` unchanged;
- keep `title` and `vndb_id` synchronized with the game/research record;
- update `generated_at` only when the assembled guide content actually changes;
- when every planned route is generated and the guide is made available, update `games.json.has_guide` and then synchronize tracked generated artifacts such as root `index.html`.

Do not mark routes reviewed merely as part of assembly.

## Review finding schema

Use the same evidence-rich finding format regardless of whether feedback is posted to a PR or a fallback issue.

Every finding must include:

- **File / step:** exact route file and step index or narrow section.
- **Problem:** precise defect.
- **Current:** exact current content/behavior.
- **Expected:** exact corrected content/behavior.
- **Required action:** deterministic author action.

Accuracy findings must additionally include:

- **Set A evidence:** source URL plus the shortest relevant verbatim excerpt.
- **Set B evidence:** source URL plus the shortest relevant verbatim excerpt, or explicitly `not documented` only where these standards permit that omission.

Structural findings do not fetch Japanese sources; instead they must show the relevant route-step sequence that demonstrates the structural defect.

Group all findings for one route/type together. Do not create one issue/comment per individual finding.

## Review feedback destination

**Caller/orchestrator transport instructions take precedence.** If the invoking prompt or automated runner explicitly says to create/use a GitHub issue, PR comment, or another review destination, follow that transport exactly.

Only when the caller does **not** specify a transport should direct/manual agents use the defaults below.

Keep review feedback consolidated when possible, but do not make the feedback transport itself a second approval-state system.

### When an open PR exists for the work

For direct/manual agent review, put structural and accuracy findings on the existing PR instead of creating per-route review issues. Keep each route/type clearly identified in the comment so the author and re-reviewer can follow the thread.

- Clean review: leave a concise PASS comment for that route/type.
- Findings: leave one detailed CHANGES REQUESTED comment for that route/type.
- Author corrections: reply/comment on the same PR with what changed.
- Re-review: confirm the findings are resolved on the same PR, or state precisely what remains.

Do not launch multiple reviewers of the same type against the same route concurrently.

PR comments are an audit trail and collaboration surface; they are **not** a machine-readable replacement for `reviewed` or for whatever persistence mechanism an automated orchestrator already uses.

For direct/manual PR review, clean review evidence must be **content-bound**:

- Structural `PASS` / resolved records include the reviewed route file's current repository blob SHA (or an equivalent deterministic content hash if the environment does not expose blob SHAs).
- Accuracy `PASS` / resolved records include both the reviewed route-file blob SHA and the current `research.json` blob SHA/content hash.
- Before relying on an earlier clean record or setting `reviewed: true`, fetch the current identifiers again. If the route identifier no longer matches the structural record, structural review is stale. If the route or research identifier no longer matches the accuracy record, accuracy review is stale.
- Final approval requires structural and accuracy clean records that match the **current** relevant content. This rule does not depend on the author remembering to announce invalidation.

### When no open PR exists

Use the existing issue workflow:

- at most one open `route-structure` issue per route;
- at most one open `route-accuracy` issue per route;
- clean first passes create no issue;
- findings are fixed by the author and closed only by the owning reviewer after re-verification.

Before creating an issue, check for an existing one and re-check immediately before creation.

### Automated orchestrators

An automated runner may keep its existing transport/persistence mechanism. It must still enforce the same role separation, review gates, evidence requirements, and `reviewed` semantics. These standards do not require a particular shell command, API, issue format, or local process.

## Tracked generated-artifact consistency

A change is not complete if a tracked generated file is left inconsistent with the source data that produces it.

Before finishing author work:

1. Identify whether any modified source-of-truth file has tracked derived outputs in the repository.
2. Inspect the committed generator/template to determine the exact dependency.
3. If the current environment can safely run the relevant deterministic generation step, use it.
4. If it cannot, reproduce only the affected deterministic transformation from the committed source/template and update the tracked derived file directly.
5. Verify the derived file now agrees with the source-of-truth values before declaring the work complete.

Do **not** modify local automated orchestration merely to make a browser or repository agent able to run it. The committed generator is the specification for the derived output, not a required execution environment.

Known dependency in this repo:

- `games.json` → root `index.html` via `scripts/generate.py::generate_landing()` and `scripts/templates/landing.html`.
- Therefore changes to landing-visible fields such as `slug`, `title`, `alttitle`, `cover_url`, or `has_guide` must also be reflected in the tracked root `index.html`.
- A browser/repository agent that cannot run `generate.py` must still update the affected embedded landing data equivalently and verify it matches current `games.json`.

This consistency check is separate from structural/accuracy review. It does not invalidate a route review when only a derived presentation artifact is synchronized to already-approved source data.

## Review lifecycle

For each unreviewed route:

1. Structural reviewer performs a fresh structural review.
2. If structural findings exist, the author fixes them and the structural reviewer independently re-verifies.
3. Accuracy reviewer independently verifies both Japanese verification sets.
4. If accuracy findings exist, the author fixes them and the accuracy reviewer re-fetches sources and independently re-verifies.
5. **If any accuracy-stage fix changes route structure** (step order, saves/loads, `badEndPath`, `isLoad`, or another structural-flow element), the prior structural pass is stale. Rerun structural review, then rerun accuracy review against the structurally final route.
6. Repeat until both gates are clean for the same route content.
7. Only then may the accuracy stage/orchestrator set `reviewed: true`.

Use the open PR for direct-agent feedback when one exists; otherwise use the existing issue workflow. Automated runners may retain their own transport.

The author and structural reviewer never set `reviewed: true`.

## Review invalidation

Whenever a gate has already passed, a later change can invalidate that pass **even while `reviewed: false`**. Invalidate only the gates affected:

| Change | Set reviewed:false? | Structural re-review | Accuracy re-review |
| --- | --- | --- | --- |
| Route step order, `badEndPath`, `isLoad`, save/load structure | Yes, affected route | Yes | Yes |
| Route choice/source text/save position/ending content without structural change | Yes, affected route | No | Yes |
| Research source basis, prerequisites, unlocks, or route-order claims | Yes, affected routes | No unless route files changed structurally | Yes |
| Backfill of the exact already-documented legacy target, with no source/route behavior change | No | No | No |
| **Guide target release/platform changes or previously ambiguous target is resolved to a specific release** | **Yes, all routes** | **Yes after routes are regenerated/checked for the target** | **Yes, with fresh research for the target** |
| Portrait/title/display-only metadata | No | No | No |
| Issue labels/comments/duplicate cleanup only | No | No | No |

If uncertain whether a route-content change is structural, rerun structural review.

## Completion gate

A guide section is complete only when:

- `guide_target` is explicit, linked, and matches the release/platform against which research was performed;
- its structural review is clean,
- its accuracy review is clean against both Japanese verification sets,
- all reviewer findings for the active review have been independently re-verified as resolved, and
- `reviewed: true`.

A game is fully reviewed only when every guide section satisfies that gate.
