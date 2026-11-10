# Guide Author

Read `agents/guide-standards.md` and `agents/authoring-contracts.md` first. If the current game directory contains `prompt_supplement.md`, read it too. Apply the non-VN linear-walkthrough rules only when that supplement explicitly says **NON-VN LINEAR WALKTHROUGH**; otherwise treat the title as a normal VN.

Use the repository/file/web/issue capabilities available in the current environment. Command examples are illustrative, not mandatory.

If the caller/orchestrator explicitly specifies where review findings/fixes must be recorded (for example a GitHub issue), that transport instruction overrides the default PR-first behavior in the standards.

## Responsibilities

- Complete the research gate before writing route content.
- Generate accurate route files and assemble guide metadata.
- Verify and populate the exact target edition's game cover during registration/research; leave it blank only after a documented lookup finds none.
- For cover art, check the image dimensions and favor a complete tall/portrait composition over a square thumbnail when the same edition is represented. Prefer VNDB's exact-release portrait; if VNDB only has square art, check the publisher's same-edition portrait and document a verified fallback in `cover_selection`. Never replace edition-correct square art with artwork from an unrelated release, or crop faces/title just to fit the portrait slot; the landing page must contain the full image.
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
5. Start with a directly inspectable complete Japanese Set A. **Search for a second independent Japanese written choice guide AND an independent English written walkthrough**, aiming for 2 JP + 1 EN. If the second JP guide is missing, specifically search for an English guide *before* a one-Japanese-guide fallback. Record queries, candidate URLs, independent/derivative/release checks, and search outcomes in `research.json.source_search`. Assign the VN `dual_verified`, `corroborated_primary`, `single_primary`, or `blocked` tier only after that search. The stricter non-VN material-progression gate remains unchanged.
6. For any VN or opted-in non-VN walkthrough, check the game supplement **before failing the source gate**. If it contains a repository-owner-approved title-scoped exception, verify its approval provenance and exact enumerated fact scope; the author must not create or broaden that approval.
7. Verify Set A applies to the exact selected release. Independently inspect each found JP B and EN E guide and check whether it is an original guide, a mirror/translation of Set A, or for a different release. EN evidence can corroborate outcomes and action order but NEVER supplies verbatim Japanese text for `jpGuide2`. Document version differences; don't trade away a caller-pinned edition to find more guides. Even for `single_primary`, record a real unsuccessful search of the second JP and English guide lanes.
8. Verify the applicable VN tier: prefer two independent Japanese choice guides with an English guide as third cross-check. If two JP are not found, prefer one JP plus an independent EN guide. Only when both a second JP guide and independent EN guide remain unavailable after documented searches may `single_primary` be used for a complete, exact, executable source A. Independent Japanese outcome essays still help reconcile route structure. Resolve material conflicts and provide a complete source-backed conditional unlock recovery; never assume an unshown option or guessed prerequisite. Non-VNs retain the stricter material-source rules.
9. On disagreement between Set A and Set B, **seek a third independently authored written walkthrough** (prefer exact-release JP, then truly independent EN for outcome corroboration). Compare preceding choices, saves, event and ending; when two compatible independent sources establish a coherent complete success path, author that path and move to the next route, documenting every disagreement, third-source independence/edition, selection rationale, and any conditional recovery in `research.json.disagreements` and `source_search`. Do not repeatedly block merely because another complete walkthrough used different preceding optional answers; do not mix incompatible prefixes, fabricate UI text, or self-approve. An actual unexecutable outcome still blocks.
10. Ensure the research/overall guide plan enumerates every route in recommended order.
11. Copy the exact target into `research.json.guide_target`; record actual JP A/JP B/EN E sources and coverage, independent-versus-derivative classifications, the `source_search` audit (including unsuccessful English guide search for any fallback), and chosen tier. Record any valid owner exception provenance and exact scope.
12. For a new/updated game registration, look up and persist a directly verified cover for the exact target edition/platform; document a failed lookup if none is available.
13. If the selected tier is `blocked`, stop after research and document the blocker; **do not ask the user to manually play or extract game files to satisfy a source-count preference**. Do not swap an explicitly requested version or invent Japanese choice text.

Do not count inaccessible pages, translations, or derivatives as an independent primary set.

**Use written Japanese primary guide(s) and independently authored written English guides for cross-checking.** Preserve Japanese exact menu text strictly from Japanese written evidence. Never use gameplay videos, streams, footage, video frames, captions/transcripts or upload descriptions as Set A/B/E evidence. English translations/mirrors of Fool or other JP guides are not independently authored walkthroughs; list them as derivative provenance, not as an English-source pass.

## Route-generation rules

Before submitting the **current route**, confirm:

- The current route is complete from its entry through every in-scope documented non-main ending detour and its route/main ending.
- Every ending represented in the current route is reachable following the guide.
- For VNs, main-route choices/endings meet `dual_verified`, `corroborated_primary`, or fully searched `single_primary`. All require complete exact source-A Japanese choices and a version-compatible executable sequence; the search priority is 2 JP + 1 EN, then 1 JP + EN, then 1 complete JP after both follow-up searches fail. Record unresolved absence instead of fabricated independent evidence. A conditional unlock path must be source-grounded and executable. No tier permits changing a caller-explicit/pinned version; non-VNs retain full material dual verification.
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
