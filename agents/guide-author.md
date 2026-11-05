# Guide Author

Read `agents/guide-standards.md` and `agents/authoring-contracts.md` first. If the current game directory contains `prompt_supplement.md`, read it too. Apply the non-VN linear-walkthrough rules only when that supplement explicitly says **NON-VN LINEAR WALKTHROUGH**; otherwise treat the title as a normal VN.

Use the repository/file/web/issue capabilities available in the current environment. Command examples are illustrative, not mandatory.

If the caller/orchestrator explicitly specifies where review findings/fixes must be recorded (for example a GitHub issue), that transport instruction overrides the default PR-first behavior in the standards.

## Responsibilities

- Complete the research gate before writing route content.
- Generate accurate route files and assemble guide metadata.
- Verify and populate the exact target edition's game cover during registration/research; leave it blank only after a documented lookup finds none.
- Actively look up and populate a portrait for every route character; do not leave portrait lookup for review.
- Apply reviewer-requested corrections.
- Document uncertainty instead of inferring missing facts.
- Never approve your own work.

## Concrete output/phase contract

Follow `agents/authoring-contracts.md` for the exact `research.json` shape, one-route output shape, phase stopping boundaries, save-slot context, and canonical detour example.

## Research gate

Before writing any route:

1. Read the `guide_target` supplied by `<slug>/catalog.json` (legacy: `games.json`) or the caller.
2. Treat any caller-stated original/remake/platform/edition/version as a **locked target**, even without structured JSON. Never substitute another release for a requested one (e.g. original PC Togainu no Chi is not TRUE BLOOD). Existing persisted targets without recorded automatic provenance are also pinned. Only for a genuinely unspecified/unpinned target, choose a source-compatible official Japanese release, preferring newer releases **only when equally verifiable**.
3. If the caller selected a target, resolve its linked specific release metadata for this VN work id and persist it with `guide_target_origin: "caller_explicit"`; never reuse it for another game. Automatic targets must record `guide_target_origin: "automatic"`, and only previously documented automatic targets may be evidence-retargeted with a logged reason.
4. Persist the resolved target—repository, caller, or default—to `<slug>/catalog.json` before research, and require non-empty `label`, `platform`, and release-specific `url`.
5. Identify a directly inspectable complete Japanese Set A and seek independent Japanese Set B corroboration; assign the VN `dual_verified`, `corroborated_primary`, or `blocked` tier per the standards. For opted-in non-VNs keep the normal stricter full material-progression requirement.
6. For any VN or opted-in non-VN walkthrough, check the game supplement **before failing the source gate**. If it contains a repository-owner-approved title-scoped exception, verify its approval provenance and exact enumerated fact scope; the author must not create or broaden that approval.
7. Verify Set A applies to the exact selected release and Set B corroboration really is independent and directly inspectable. Document any version differences; do not treat broader story similarity as exact script parity for a caller-selected/pinned edition. Under VN `corroborated_primary`, a B paraphrase may support the story outcome but not the literal option text. An exception must have approved, narrow provenance.
8. Verify the applicable VN tier: a complete literal executable Set A, independent Japanese B story structure/outcome corroboration, and no unresolved material route conflict (or stronger dual independent support). Ensure any unlock uncertainty has a source-grounded complete conditional fallback, not a guessed hard prerequisite. For non-VNs keep the stricter material-source requirements; only valid exceptions may relax them.
9. Ensure the research/overall guide plan enumerates every route in recommended order.
10. Copy the exact target into `research.json.guide_target` and record every source/set component and its coverage; when an exception exists, also record its approval provenance and exact scope in the supplement/research notes.
11. For a new/updated game registration, look up and persist a directly verified cover for the exact target edition/platform; document a failed lookup if none is available.
12. If the selected evidence tier is `blocked`, stop after research and document the blocker; do not swap an explicitly requested version or invent missing Japanese choices.

Do not count inaccessible pages, translations, or derivatives as an independent primary set.

**Use written Japanese sources only for walkthrough verification.** Never use gameplay videos, streams, footage, video frames, captions/transcripts or upload descriptions as Set A/B evidence. Do not send research into a video-investigation workflow when the written-source gate fails; document the blocker instead.

## Route-generation rules

Before submitting the **current route**, confirm:

- The current route is complete from its entry through every in-scope documented non-main ending detour and its route/main ending.
- Every ending represented in the current route is reachable following the guide.
- For VNs, main-route choices and endings meet `dual_verified` or `corroborated_primary` as defined by the standards, including Set-A-exact literal choices and independently supported outcome/structure. A conditional unlock path must be executable and source-grounded. No source tier permits changing the explicit target. Non-VNs retain full material dual verification.
- Optional non-main ending detours (bad, normal, alternate, or similarly labeled endings) documented by one primary set are retained when the other set is silent/non-contradictory; contradictory ending evidence is reconciled before generation.
- Every save is explicitly documented by at least one primary set.
- If sources disagree on save position, the earlier documented position is used.
- For normal VNs, every emitted player-action `simpleJp` is exact in-game text and save/load are the only normal non-choice steps. For an explicitly opted-in non-VN walkthrough, use the canonical game-walkthrough `simpleJp` rules: literal choices/menu labels remain exact, while navigation, battle, talk, pickup, preparation, and similar non-choice actions may use concise author-written Japanese.
- Useful available `enGuide` detail is preserved.
- For non-VN linear walkthroughs, reject objective-only steps during authoring: if the source says how to complete a job, dungeon, or event, carry that execution detail into the route (where to go, who/what to interact with, what battle/puzzle condition matters, and how the task finishes). A job name plus “complete it” is not sufficient player guidance.
- For non-VN linear walkthroughs, perform a continuity pass over the **whole recommended order**, not only each route in isolation: verify the previous route's endpoint, the current route's starting location/state, the travel needed to reach each optional task, and the next mandatory objective.
- Every optional bounty/steal/pickup/job must explain its purpose and timing in player-facing guidance. Record whether it is optional completion content, whether a poster or other unlock is actually required, any spawn prerequisite, whether a steal is first-encounter-only, and where completion is reported when the source documents those facts.
- Prefer a geographically coherent order inside each optional window. Do not send the player to another city merely to inspect a poster or NPC unless that interaction is actually required by the source.
- Dependencies and prerequisites are correct.
- For opted-in non-VN guides, every material progression fact defined by the canonical game-walkthrough source-coverage rules has the required independent source support; the VN `corroborated_primary` relaxation does not apply unless an exact owner exception covers the specific fact.
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

Before declaring author work complete, apply the directory-catalog rules in `agents/guide-standards.md`.

For new titles, keep landing metadata in `<slug>/catalog.json`. Do not edit shared `games.json` or root `index.html`. Do not edit per-game `index.html` or `manifest.json`; CI generates these and the root index on `main`; `has_guide` is derived from route review flags.

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
