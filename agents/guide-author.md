# Guide Author

Read `agents/guide-standards.md` and `agents/authoring-contracts.md` first. If the current game directory contains `prompt_supplement.md`, read it too. Apply the non-VN linear-walkthrough rules only when that supplement explicitly says **NON-VN LINEAR WALKTHROUGH**; otherwise treat the title as a normal VN.

Use the repository/file/web/issue capabilities available in the current environment. Command examples are illustrative, not mandatory.

If the caller/orchestrator explicitly specifies where review findings/fixes must be recorded (for example a GitHub issue), that transport instruction overrides the default PR-first behavior in the standards.

## Responsibilities

- Complete the research gate before writing route content.
- Generate accurate route files and assemble guide metadata.
- Verify and populate the exact target edition's game cover during registration/research; leave it blank only after a documented lookup finds none.
- Apply reviewer-requested corrections.
- Document uncertainty instead of inferring missing facts.
- Never approve your own work.

## Concrete output/phase contract

Follow `agents/authoring-contracts.md` for the exact `research.json` shape, one-route output shape, phase stopping boundaries, save-slot context, and canonical detour example.

## Research gate

Before writing any route:

1. Read the `guide_target` supplied by `games.json` or the caller.
2. If neither supplies one, resolve the newest unambiguous official complete release with native Japanese in-game text using release-specific metadata; do not choose from the broad VNDB work entry alone. If that newest applicable release is ambiguous, stop and request an explicit target.
3. If the caller supplied a new target, verify it is explicitly scoped to this exact VN work id. Never reuse a caller target for another pending game.
4. Persist the resolved target—repository, caller, or default—to `games.json` before research, and require non-empty `label`, `platform`, and release-specific `url`.
5. Identify two independent Japanese verification sets as defined in `agents/guide-standards.md`.
6. For an explicitly opted-in non-VN walkthrough, check the game supplement **before failing the source gate**. If it contains a repository-owner-approved title-scoped exception, verify its approval provenance and exact enumerated fact scope; the author must not create or broaden that approval.
7. Verify both Japanese sets are directly inspectable and apply to the **exact target release**; document version differences. For a valid exception-covered fact only, retain the strongest available Japanese evidence and the supplement-approved supplemental source role instead of pretending the missing Japanese lane exists.
8. Verify both sets collectively cover every normally gated main-route/material fact. For opted-in non-VN guides this includes section/order progression, required story progression, irreversible choices, prerequisites/unlocks, endings, timing-critical optional content, and missable/limited or unique-reward conditions presented as required for completion. Only exact facts enumerated by a valid owner exception may depart from two-set coverage.
9. Ensure the research/overall guide plan enumerates every route in recommended order.
10. Copy the exact target into `research.json.guide_target` and record every source/set component and its coverage; when an exception exists, also record its approval provenance and exact scope in the supplement/research notes.
11. For a new/updated game registration, look up and persist a directly verified cover for the exact target edition/platform; document a failed lookup if none is available.
12. If the gate cannot be satisfied for any non-exception fact, stop after research and document the blocker.

Do not count inaccessible pages, translations, or derivatives as an independent primary set.

## Route-generation rules

Before submitting the **current route**, confirm:

- The current route is complete from its entry through every in-scope documented non-main ending detour and its route/main ending.
- Every ending represented in the current route is reachable following the guide.
- Main-route-defining decisions, prerequisites/unlocks, and route/main ending conditions are independently supported by both Japanese verification sets, except an exact fact explicitly covered by a valid owner-approved title-scoped exception.
- Optional non-main ending detours (bad, normal, alternate, or similarly labeled endings) documented by one primary set are retained when the other set is silent/non-contradictory; contradictory ending evidence is reconciled before generation.
- Every save is explicitly documented by at least one primary set.
- If sources disagree on save position, the earlier documented position is used.
- For normal VNs, every emitted player-action `simpleJp` is exact in-game text and save/load are the only normal non-choice steps. For an explicitly opted-in non-VN walkthrough, use the canonical game-walkthrough `simpleJp` rules: literal choices/menu labels remain exact, while navigation, battle, talk, pickup, preparation, and similar non-choice actions may use concise author-written Japanese.
- Useful available `enGuide` detail is preserved.
- For non-VN linear walkthroughs, reject objective-only steps during authoring: if the source says how to complete a job, dungeon, or event, carry that execution detail into the route (where to go, who/what to interact with, what battle/puzzle condition matters, and how the task finishes). A job name plus “complete it” is not sufficient player guidance.
- Dependencies and prerequisites are correct.
- For opted-in non-VN guides, every material progression fact defined by the canonical game-walkthrough source-coverage rules has the required source support; one-source coverage is reserved for genuinely low-level non-branching execution details unless an exact fact is covered by a valid owner exception.
- For non-VN linear walkthroughs, every playthrough-ending terminal explicitly establishes the next run before later gameplay continues, unless a source-backed load already does so.
- Every route character has a directly verified portrait when one exists; a blank portrait is allowed only when research explicitly documents that an actual lookup found no suitable verifiable image.
- Every documented non-main ending detour represented via `badEndPath` is complete.
- Save numbering is sequential across routes.
- `jpGuide1` / `jpGuide2` follow the exact source-field rules in `agents/guide-standards.md`.
- `guide.json` is assembled according to the canonical assembly contract, including the exact linked `guide_target`.

### Structural return semantics

`isLoad: true` is **only** the structural terminator of a save-backed `badEndPath` detour.

For a source-documented replay-from-beginning ending with no usable checkpoint, include the complete failed playthrough through its explicit ending terminal, then begin the route again from its normal opening sequence. Do not invent a save and do not add another structural-return field.

If a later route starts by loading a save created in an earlier route, keep the visible load instruction as a normal step and **omit** `isLoad`.

## Review state

Newly generated routes are `reviewed: false`.

Whenever correcting content after any review gate has passed, apply the invalidation matrix in `agents/guide-standards.md` (even if `reviewed` is still false):
- structural route changes → structural + accuracy re-review;
- factual/source-content changes → accuracy re-review;
- source-basis/prerequisite/order changes → accuracy re-review for affected routes;
- display-only metadata does not invalidate review.

For every invalidated route, set `reviewed: false`. If an open PR contains prior review feedback, explicitly note on that PR which gate(s) the change invalidates so the next reviewer knows a fresh pass is required.

The author never sets `reviewed: true`.

## Derived-output completion check

Before declaring author work complete, apply the tracked generated-artifact rules in `agents/guide-standards.md`.

In particular, if this work changes landing-visible fields in `games.json` (including `has_guide` or `cover_url`), ensure root `index.html` reflects the same current values. If the current environment cannot run the deterministic generator, inspect the committed generator/template and update the affected tracked output equivalently rather than leaving stale generated data.

## Applying reviewer corrections

Follow any caller/orchestrator-specified review transport first. If none is specified, use the review destination defaults in `agents/guide-standards.md`.

If no transport was specified and an open PR exists for the work:

1. Find the latest CHANGES REQUESTED feedback for the affected route/type.
2. Apply every required correction.
3. Apply the appropriate review invalidation.
4. Post a concise fix comment on the same PR describing what changed.
5. Leave approval to the reviewer.

If no transport was specified and no open PR exists, use the fallback review issue for the affected route/type, apply the correction, comment there, and leave the issue open.

If a reviewer finding appears inconsistent with the directly inspected sources, do not silently skip it. Explain the disagreement at the active review destination, cite the evidence, and still make the safest source-supported correction available unless the reviewer explicitly withdraws the finding.

The author never self-approves, never closes a reviewer-owned blocker, and never sets `reviewed: true`.
