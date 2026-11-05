# VN Guide Standards

These are the canonical, environment-neutral rules for guide generation and review.

Agents may work through a checkout, repository API, connected app, browser, or another execution environment. Shell and `gh` examples elsewhere in the repo are examples only. Use whatever file, web, issue, and repository capabilities are available while preserving the same state transitions and role boundaries.

Game-specific `prompt_supplement.md` files may add stricter title-scoped instructions. They must not weaken or replace these standards except where an explicit repository-owner-approved exception is recorded with provenance.

## Roles

Keep these roles independent:

1. **Author** — researches, generates, and fixes guide content.
2. **Structural reviewer** — checks route-file flow only. Does not fetch walkthroughs or edit guide content.
3. **Accuracy reviewer** — independently checks the guide against Japanese sources. Does not fix route content.
4. **Review orchestrator** — may coordinate fresh role sessions and update review state after a clean pass.

Do not combine author and reviewer roles in one session.

## Research/source gate

Do not generate route content until the research gate passes.

A game requires an **explicit linked guide target**, a directly inspectable complete Japanese primary walkthrough (Set A), and the applicable VN evidence tier described below. Independent Japanese sources must be sought and reconciled; they need not duplicate every exact in-game menu string for a VN when the corroborated-primary tier is justified. Non-VN walkthroughs retain their stricter material-progression rules.

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

- For legacy titles, `games.json.guide_target` is the source of truth. For new or migrated titles, `<slug>/catalog.json.guide_target` is the source of truth. Never edit shared `games.json` for a new guide.
- A caller may explicitly specify a version by edition name, platform, release date, original/remake/port distinction, or other unambiguous constraint **even without supplying all three JSON fields**. Resolve its exact label/platform/URL for that same VN work, then persist it to `<slug>/catalog.json`. An explicit caller version is **immutable** until that same caller explicitly authorizes a different version. Never substitute a remake, later port, edition, platform, or "better documented" release when the requested one is difficult to verify. This applies equally to original-PC requests such as Togainu no Chi versus its later TRUE BLOOD release. Caller targets are scoped to the exact VN work id and never inherited by another guide.
- Persist target provenance in `<slug>/catalog.json.guide_target_origin`: `"caller_explicit"` or `"automatic"`. For existing guides with no provenance field, treat the current persisted target as **pinned**, never as safely auto-retargetable. Set `"automatic"` only when the target was actually chosen without a caller version request; never backfill that designation merely to escape a source blocker. `research.json` must explain any legitimate automatic retarget and why there was no explicit caller version.
- If there is **no caller-selected or pinned repository target**, choose an official native-Japanese release for which the primary Japanese choice walkthrough is demonstrably applicable. When multiple releases have equally sound source applicability, prefer the newest complete official Japanese edition. Do not choose a newer release whose choice/script/save applicability is unverified over a source-supported older release. Use release-specific VNDB/official/store metadata, not a broad work entry. A previous *documented automatic* choice may be retargeted to a better-evidenced release with an explicit audit note; a caller-explicit or provenance-unknown persisted target may not.
- If no release can be precisely identified, or equally supported releases remain indistinguishable, stop rather than inventing a release/version identity. Do not reduce an explicitly requested older edition to a different newer edition to clear this ambiguity.
- `label`, `platform`, and `url` are all required and non-empty.
- The URL should identify the **specific intended release/edition**, not merely the broad work. **Prefer the exact VNDB `https://vndb.org/r...` release page whenever available; use another release-specific source only when VNDB cannot provide a suitable exact-target link.**
- Once a default target is resolved, persist it to the title's `<slug>/catalog.json` before research exactly like a caller-supplied target.
- Copy the exact target into `research.json.guide_target` and later into `guide.json.guide_target`.
- Verify every Set A/B component applies to that exact target, or document version differences and why they do not affect the guide.
- If an **explicitly requested or pinned** target cannot be verified, or walkthroughs only fit a materially different version, **keep that target and record the blocker**. Never silently switch it. Only a documented automatic target may be changed, and only to a precisely identified evidence-compatible Japanese release with matching cover/provenance and fresh reviews.

### Legacy target migration

For existing guides that predate `guide_target`, use the same target resolution policy instead of preserving ambiguity indefinitely.

- Existing reviewed flags are not invalidated **solely** because this field was absent historically.
- Before new source-dependent generation, correction, or accuracy re-review, use the persisted caller-selected/pinned target or, where genuinely absent, resolve a source-compatible official Japanese release as above. Never treat missing provenance on an existing target as permission to change it.
- If the target backfill merely formalizes the exact release already unambiguously documented in the existing research/sources, the backfill itself is metadata-only and does not invalidate route review.
- If the old research is ambiguous, or the target changes to a different release/platform/edition, redo research for the new target and invalidate all affected route reviews.

Then apply these source roles:

- **Set A** should be the detailed primary walkthrough used for exact step/save text.
- **Independent Japanese corroboration (Set B):** seek independent firsthand Japanese written guide(s), playlogs or outcome discussions confirming the game's material story structure, number/meaning of endings, and any known unlock/replay behavior. Record exactly which facts are and are not corroborated. For **VNs**, a second complete literal menu transcription is preferred but not mandatory under the corroborated-primary tier below. For opted-in **non-VN** walkthroughs, retain the stricter full material-progression verification requirement.
- A verification set may be one page or multiple Japanese pages. If multiple pages are needed, document every component in `research.json` and explain what each component covers.
- **No video evidence.** Set A and Set B must use directly inspectable written Japanese sources. Do not count or propose videos, livestreams, gameplay recordings, clips, their frames, descriptions, or transcripts as route/source-gate evidence or as a substitute for a missing written walkthrough. If qualifying written sources cannot verify the exact target, preserve the blocker; do not bypass it by researching recordings.
- A translation, derivative guide, or page that merely cites Set A does not count as an independent Set B.
- A source that cannot be directly inspected does not count toward the gate. It may be listed for provenance only.
- If neither VN evidence tier can be satisfied, stop after research and document the blocker unless the title has a valid owner-approved scoped exception covering the exact residual corroboration deficiency. A single incomplete guide, unsupported main-ending selection, unresolved material contradiction, or wrong requested version never qualifies for automatic approval. Do not invent game content.
- Legacy `research.json` files may predate explicit `set: "A"` / `set: "B"` fields. For those, use the documented primary-source ordering/notes to identify the two independent Japanese source sets; when the research file is next edited, make the set assignment explicit.

### VN evidence tiers (automatic; never a version override)

1. **`dual_verified`** — two independent directly inspected Japanese written verification sets substantiate every material route decision, unlock/prerequisite and main ending for the *selected* release. Keep their exact printed text separately in `jpGuide1` and `jpGuide2`.
2. **`corroborated_primary`** — Set A is a directly inspected **complete, executable Japanese walkthrough** for the *selected* release: full exact selectable choice text, route order/ending labels, material reset/continuation behavior and source-backed save/load points. Directly inspected **independent** Japanese B material corroborates the broad route/endings structure and outcome meanings, and raises no **unresolved material contradiction**. Set B may paraphrase endings and omit literal option wording; never present a paraphrase as verbatim game UI. Document each A-only literal terminal and the B outcome/source separately. Use `（第二ガイドに記載なし）` in `jpGuide2` where B does not print the exact step. This tier is valid for VNs without per-title permission, but is **not** a claim of two verbatim sources or proof of edition equivalence.
3. **`blocked`** — no complete trustworthy Japanese Set A, no independent Japanese corroboration of main structure/outcomes, materially conflicting prerequisite/route/ending claims without a verifiable executable resolution, wrong target version, or uncertain applicability of Set A to a **caller-pinned target**. Stop rather than claim an accuracy PASS. A genuinely ambiguous unlock may be explained by a **complete source-grounded conditional fallback** only if the documented alternative choices, completed-ending boundary and replay steps make the path executable in every known supported state; never invent flags, prerequisites or availability.

Record `research.json.verification_tier` as one of these three values and summarize the direct evidence for each main ending, its scope/limitations, and any conditional fallback in `disagreements`. Accuracy reviewers independently validate the chosen tier, literal Set-A transcript, corroborating Japanese sources, source independence and target origin. **Missing duplicate Japanese quotation is not itself a failure under `corroborated_primary`; contradictions, unusable paths and version mismatches still are.** Do not elevate provenance-only snippets, videos, translated/derivative material, or an inaccessible page to B.

A save point, repeated menu operation or optional detour may be supported by Set A alone when B is silent/non-contradictory. For any tier, preserve source-specific quotations and use exact omission placeholders where the other source does not directly print a step. Scope title exceptions only to residual facts not already handled by these tiers.

## Game covers

Every game registration should have a cover image for the exact intended release/edition when one can be directly verified.

**Lookup priority:** First inspect **VNDB's release-specific cover images** for the intended `guide_target` (use the correct `r...` release, not just the VN-level `v...` image). If VNDB exposes a suitable directly verifiable image URL for that exact edition, use it. If not, check the publisher/store's official artwork, then other structured databases such as YMGal. Document the reason for any non-VNDB fallback; an inaccessible API, missing image, unverified edition match, or unusable URL is a valid reason, but an omitted lookup is not. Do not guess image CDN paths or substitute a different edition's physical package cover.

- During initial registration/research, actively look up a cover for the exact `guide_target` edition/platform; do not leave `cover_url` blank merely because cover lookup was deferred.
- Prefer a stable direct image URL from an authoritative, structured, or otherwise reliable source that clearly matches the target edition.
- Do not use a different edition, limited edition, remake, port, or localization cover merely because it is easier to find.
- A blank `cover_url` is permitted only after an actual lookup finds no suitable verifiable image; document that outcome in research notes so “unavailable” is distinguishable from “not checked”.
- Cover-only corrections are display metadata and do not invalidate structural or accuracy route review.
- For new or migrated titles, store the cover in `<slug>/catalog.json`; CI updates the landing page on `main`. Do not edit root `index.html` in a guide PR.

## Character portraits

Portrait URLs must be directly verified against a character record or another authoritative/structured source.

**Lookup priority:** First check **VNDB character records** and their returned `image.url` for every heroine/route character, confirming the character by name. Prefer directly verifiable VNDB `image.url` values over alternate character databases. Only fall back to an official character source or YMGal (or another structured source) when VNDB has no suitable image or the returned image cannot be inspected/used; document that reason and the alternative source. A VNDB character page or image ID alone is not a verified image URL. Do not compose a VNDB CDN path from a character ID or an image ID.

- **A route character must have a portrait whenever a directly verifiable character image exists.** Leaving `portrait` blank because the lookup was skipped, inconvenient, or deferred is an authoring defect.
- Match the route character by name, not by numeric coincidence.
- When using VNDB, use the exact `image.url` returned by the character record. If VNDB exposes an image for that route character, a blank portrait is not acceptable.
- VNDB character IDs (for example `c34600`) and VNDB image IDs are separate identifiers. **Never construct a CDN portrait URL by inserting the character ID into an image-path pattern.**
- If the current environment cannot directly inspect VNDB's character image field, use another verifiable character source and document that source in `research.json`.
- A blank portrait is permitted only after an actual lookup finds no suitable directly verifiable image; document that absence in the route's research notes (or another explicit research field) so reviewers can distinguish “unavailable” from “not checked”.
- A portrait-only correction does not invalidate structural or accuracy route review.

## Source fields

Every route step must have **non-empty** `jpGuide1` and `jpGuide2`.

- `jpGuide1`: exact verbatim Set-A text when Set A prints that step.
- `jpGuide2`: exact verbatim Set-B text when Set B prints that step.
- For VN main-route choices/prerequisites/endings, apply `research.json.verification_tier`: `dual_verified` requires independent literal/main-fact evidence, while `corroborated_primary` permits Set-A-only exact actionable UI text when independent Japanese B substantiates the relevant structure/outcome and no material contradiction remains. An A-only main-choice `jpGuide2` MUST be `（第二ガイドに記載なし）`, with the independent B outcome attributed separately in the research/`enGuide`. `blocked` cannot pass. Opted-in non-VN walkthroughs retain the stricter two-set material-progression gate unless a valid owner exception applies.
- For a **source-A-only step permitted by the VN tier** (including a complete main-ending literal under `corroborated_primary`), or a non-route-defining save/load/repeated menu/optional non-main ending step that is explicitly documented by one set while the other is silent/non-contradictory, keep the step and use the symmetric omission placeholder for the other field:
  - Set A missing → exactly `（第一ガイドに記載なし）`
  - Set B missing → exactly `（第二ガイドに記載なし）`
- Those two exact strings are the only permitted missing-source placeholders.
- Never copy one source's text into the other source field.
- Never leave either field empty.
- Preserve source whitespace and punctuation exactly when quoting.


## Non-VN linear walkthroughs — explicit game-specific opt-in only

The repository may also contain ordinary games that use the existing guide schema as a linear walkthrough. This mode is **opt-in per game**: apply it only when that game's `prompt_supplement.md` explicitly identifies the title as a **NON-VN LINEAR WALKTHROUGH**. If that explicit instruction is absent, all normal VN rules in this document remain unchanged.

This mode deliberately does **not** introduce a second schema:

- `guide.json.routes` remains the ordered section list.
- `route_<id>.json` remains a flat ordered step array.
- A "route" in storage may represent a chapter, town, story arc, dungeon, optional-content block, NG+ block, or another practical walkthrough section.
- `research.json.recommended_order` is the single canonical play order. The player should be able to follow section 1 → section 2 → section 3 without bouncing between sections.
- `routes[*].prerequisites` is **not** a previous-section pointer. Use it only for real source-documented unlock/dependency requirements. Sequential presentation belongs exclusively in `recommended_order`; an optional section must never become an apparent prerequisite for later mandatory progression merely because it appears immediately before it.
- Optional side content may be isolated into its own section and marked clearly in the section title, for example `【任意】`. Put it at the exact point in the master order where it is safest or most useful to complete. Do not create a separate side-content route that requires the player to leave the main walkthrough and return later.
- A 100% guide may linearize multiple playthroughs as later sections of the same master order (for example first clear → NG+ cleanup → ending cleanup).
- A playthrough-ending terminal is a hard run boundary. If the next section/step requires another clear, NG+, or replay, explicitly establish that fresh run before the next gameplay action unless a source-backed save/load does so. Never imply that gameplay simply continues past an ending.
- When two sources show different literal choices in the same event, first determine whether they occur at different decision points in one sequence before treating them as contradictory. Preserve both in order when the evidence supports sequential choices.

### Game-walkthrough `simpleJp`

For an opted-in non-VN walkthrough only, `simpleJp` is the short Japanese instruction the player should perform next.

- When the game presents literal choice/menu/action text, preserve that exact in-game text.
- For navigation, battles, conversations, pickups, preparation, or other actions that have no single on-screen command string, a concise author-written Japanese instruction is allowed.
- Keep one actionable instruction per step. Do not add a new step schema or `stepType` field.
- A walkthrough instruction must be **executable**, not merely name an objective. `G#17を完了する`, `ダンジョンを攻略する`, or similar labels are insufficient when the source provides concrete actions.
- For a multi-stage job/quest, either split the route into actionable steps or put a concise ordered procedure in `enGuide`. Include the practical start point, required NPC/object interaction, battle/puzzle condition, and completion/report-back action when the source documents them.
- Guild/job titles are context labels, not walkthrough directions. Preserve the title if useful, but also tell the player **how to clear it**.
- Preserve **player continuity** across every section boundary. The first actionable step after a route/section change must make the player's current location/state and immediate destination unambiguous; the final step or its `enGuide` must make the next destination/objective clear when the game does not force it automatically.
- Do not make the player infer why an optional completion action exists. For a bounty, steal, unique pickup, recruit, or side job, `enGuide` must state whether it is optional, why the guide recommends doing it now, and any missable/first-encounter/lockout consequence that justifies the timing.
- When a bounty has hidden state, distinguish **poster confirmation**, **spawn prerequisites**, and **turn-in/reporting**. Never tell the player merely to 'check posters' when the target does not require poster confirmation, and never omit a prerequisite kill/event that controls whether the target can appear.
- Avoid gratuitous city/country bouncing. Within a safe timing window, order optional actions into an executable travel path unless the sources require a different order; when backtracking is necessary, explain the dependency that makes it necessary.
- This exception does not relax normal VN `simpleJp` rules.

### Game-walkthrough source coverage

The two independent Japanese verification sets remain the default for an opted-in game walkthrough, but source granularity differs from a VN choice guide. A valid repository-owner-approved title-scoped exception may relax that default only for its exact enumerated residual facts.

Both sets must independently support every material progression fact that could change the run: chapter/section order, required story progression, irreversible choices, prerequisites/unlocks, ending conditions, missable/limited content presented as required for completion, and the placement of optional content when timing materially matters—unless that exact fact is covered by a valid owner exception.

Low-level execution details such as ordinary travel, talking to an NPC, a routine pickup, battle advice, or another non-branching microstep may be documented by only one primary set when the other is silent and non-contradictory. Keep both source fields non-empty and use the same symmetric omission placeholders defined below. For exception-covered material facts, use only the source roles and omission behavior explicitly allowed by the supplement. Never use either rule to hide missing independent support for an unlisted progression-critical fact.

### Owner-approved title-scoped source exceptions

The VN `dual_verified` and `corroborated_primary` tiers above are normal policy; neither requires a per-title owner exception. **Non-VNs** still require independent confirmation of material progression by default. A game may depart from the applicable normal tier only through an explicit owner-approved exception recorded in its `prompt_supplement.md`. A VN exception may waive otherwise unavailable **independent corroboration** for enumerated residual facts; it never waives a complete executable Set A, exact Japanese in-game text, target-edition applicability, or independent review.

Such an exception must:

- be title-scoped and must not generalize to other guides;
- record approval provenance in the supplement/research record: at minimum the approval date plus a PR/comment URL, issue/comment reference, or explicit caller-approval context sufficient for a later reviewer to verify that the author did not self-grant the exception;
- enumerate the exact residual facts it covers rather than broadly waiving the source gate;
- state which recovered sources may establish each missing fact and what role each source plays;
- preserve normal Japanese Set A/Set B verification everywhere usable independent Japanese evidence exists;
- keep non-Japanese source material out of `jpGuide1` / `jpGuide2`; use the normal omission placeholder when a Japanese lane lacks the exact text;
- permit non-Japanese operational detail only in the fields explicitly allowed by the supplement (normally concise translated `enGuide`);
- require `research.json` source notes/disagreements to match the current exception scope so stale “gate still open” or narrower exception wording does not contradict the supplement;
- be honored by reviewers exactly as written: do not reopen an approved exception, and do not silently expand it beyond the enumerated facts.

An owner-approved exception is an explicit provenance decision, not evidence that the missing Japanese source suddenly exists. Review findings should distinguish “allowed by the title exception” from “verified by both Japanese sets”.

## Route step semantics

### Step shape / `simpleJp`

For normal VN guides, use the rules below. An explicitly opted-in **NON-VN LINEAR WALKTHROUGH** uses the game-walkthrough `simpleJp` rules above instead for non-choice gameplay actions; literal in-game choices/menu labels still remain exact.

- Every VN player-action step uses the **exact in-game choice/action text** in `simpleJp`.
- For VNs, do not paraphrase `simpleJp`, append outcome suffixes, or prefix it with location/context text.
- For VNs, save and load instructions are the only normal non-choice `simpleJp` steps.
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

For an opted-in non-VN walkthrough, structural continuity also spans section and playthrough boundaries. After an ending/clear terminal, the next actionable gameplay must explicitly establish the next run (for example clear-data NG+, replay from the beginning, or a source-backed load). Do not accept an impossible ending → later-gameplay transition merely because each individual section is internally linear.

### Structural markers

- `badEndPath` is the historical field name for the first branch step of any documented non-main ending detour, including bad, normal, alternate, or similarly labeled endings.
- `isLoad: true` is reserved **only** for a load that terminates a save-backed `badEndPath` non-main-ending detour and returns to the main route.
- A normal instruction to load a save created in an earlier route is a plain step. Its `simpleJp` may say `セーブNにロード`, but it must **not** have `isLoad: true`.
- A replay-from-beginning ending with no usable documented checkpoint does **not** introduce another structural marker. Represent the complete failed playthrough through its explicit ending terminal, then begin the route again from its normal opening sequence.
### Non-main ending detour completeness

Every documented non-main ending detour—bad, normal, alternate, or similarly labeled—explicitly documented by **either** directly inspected primary Japanese verification set must be actively included before continuing the main route when the other set is silent or agrees. One-set detours are allowed; use the source-omission placeholder for the silent set on detour-only steps. If the second set contradicts the existence, branch condition, or outcome of that ending, reconcile the conflict before including it.

For each documented non-main ending detour:

- insert the save before the branch when a source documents one;
- mark the **first wrong choice** with `badEndPath`;
- use the exact ending label documented by the source;
- include every subsequent step needed to reach the ending terminal;
- for a save-backed detour, immediately follow the terminal with the matching `isLoad: true` load-back step, then continue with the good/main choice;
- for a source-documented replay-from-beginning ending with no usable checkpoint, include the complete failed playthrough from route step 0 through its explicit ending terminal, then immediately begin the route again from its normal opening sequence; during structural reconstruction, remove that entire failed-play prefix through the terminal;
- never invent a save solely to force a replay-from-beginning ending into the load-backed shape;
- if multiple non-main endings branch from the same save, include every documented detour before continuing;
- never add `badEndPath` where no Japanese source documents a non-main ending;
- never invent an ending label or terminal.

## `guide.json` assembly contract

Direct/browser agents must assemble `guide.json` equivalently to the deterministic generator:

- entries follow `research.json` / recommended order for every completed guide section;
- each entry includes `id`, `title`, and `reviewed`;
- do not store a static step count in `guide.json`; route length is derived from the actual `route_<id>.json` array at runtime;
- preserve an existing route's `reviewed` value when reassembling; new routes default to `false`;
- require the verified portrait from current research whenever a verifiable route-character image exists; fall back to an existing verified portrait only when research has none, and permit an empty portrait only when research explicitly documents that no suitable verifiable image was found;
- copy current research `sources` into `guide.json`;
- copy `research.json.guide_target` into `guide.json.guide_target` unchanged;
- keep `title` and `vndb_id` synchronized with the game/research record;
- update `generated_at` only when the assembled guide content actually changes;
- when every planned route is generated, maintain the title's `<slug>/catalog.json` for new/migrated guides; `has_guide` is derived from `reviewed` route flags and CI updates root `index.html` on `main` (legacy entries remain supported through `games.json`).

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

For derived files other than the CI-owned root/per-game HTML and manifests, a change is not complete if a tracked generated file is left inconsistent with its source. Guide PRs must not modify those CI-owned files; CI synchronizes them on `main`.

Before finishing author work:

1. Identify whether any modified source-of-truth file has tracked derived outputs in the repository.
2. Inspect the committed generator/template to determine the exact dependency.
3. If the current environment can safely run the relevant deterministic generation step, use it.
4. If it cannot, reproduce only the affected deterministic transformation from the committed source/template and update the tracked derived file directly.
5. Verify the derived file now agrees with the source-of-truth values before declaring the work complete.

Do **not** modify local automated orchestration merely to make a browser or repository agent able to run it. The committed generator is the specification for the derived output, not a required execution environment.

Known dependency in this repo:

- Root `index.html` is CI-owned: on `main`, its landing data is generated from legacy `games.json` and per-game `<slug>/catalog.json` (with `has_guide` derived from route review flags). Guide PRs do not edit the root index.
- CI generates and commits root `index.html` and per-game `<slug>/index.html` and `<slug>/manifest.json` on `main`; guide PRs must not edit these generated outputs.
- Shared bootstrap-template changes stay in infrastructure PRs; CI propagates those changes to game directories on `main`.

This consistency check is separate from structural/accuracy review. It does not invalidate a route review when only a derived presentation artifact is synchronized to already-approved source data.

## Review lifecycle

For each unreviewed route:

1. Structural reviewer performs a fresh structural review.
2. If structural findings exist, the author fixes them and the structural reviewer independently re-verifies.
3. Accuracy reviewer independently verifies the Japanese primary walkthrough, independent corroboration, chosen VN evidence tier (or non-VN dual set), and exact locked target.
4. If accuracy findings exist, the author fixes them and the accuracy reviewer re-fetches sources and independently re-verifies.
5. **If any accuracy-stage fix changes route structure** (step order, saves/loads, replay-from-beginning prefixes, `badEndPath`, `isLoad`, or another structural-flow element), the prior structural pass is stale. Rerun structural review, then rerun accuracy review against the structurally final route.
6. Repeat until both gates are clean for the same route content.
7. Only then may the accuracy stage/orchestrator set `reviewed: true`.

Use the open PR for direct-agent feedback when one exists; otherwise use the existing issue workflow. Automated runners may retain their own transport.

The author and structural reviewer never set `reviewed: true`.

## Review invalidation

Whenever a gate has already passed, a later change can invalidate that pass **even while `reviewed: false`**. Invalidate only the gates affected:

| Change | Set reviewed:false? | Structural re-review | Accuracy re-review |
| --- | --- | --- | --- |
| Route step order, `badEndPath`, `isLoad`, save/load structure, replay-from-beginning prefix | Yes, affected route | Yes | Yes |
| Route choice/source text/save position/ending content without structural change | Yes, affected route | No | Yes |
| Research source basis, prerequisites, unlocks, or route-order claims | Yes, affected routes | No unless route files changed structurally | Yes |
| Backfill of the exact already-documented legacy target, with no source/route behavior change | No | No | No |
| **Guide target release/platform changes or previously ambiguous target is resolved to a specific release** | **Yes, all routes** | **Yes after routes are regenerated/checked for the target** | **Yes, with fresh research for the target** |
| Portrait/title/display-only metadata | No | No | No |
| Issue labels/comments/duplicate cleanup only | No | No | No |

If uncertain whether a route-content change is structural, rerun structural review.

## Completion gate

A guide section is complete only when:

- `guide_target` is explicit, linked, and matches the source-compatible release/platform; caller-selected and pinned targets were never substituted for ease of research;
- every route character has a verified portrait when a verifiable image exists, or research explicitly documents that no suitable image was found;
- its structural review is clean,
- its accuracy review is clean against both Japanese verification sets,
- all reviewer findings for the active review have been independently re-verified as resolved, and
- `reviewed: true`.

A game is fully reviewed only when every guide section satisfies that gate.
