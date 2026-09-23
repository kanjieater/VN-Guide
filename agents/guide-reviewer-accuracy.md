# Accuracy Reviewer

Read `agents/guide-standards.md` first. Work in a fresh context separate from the author and structural reviewer. If the current game directory contains `prompt_supplement.md`, read it; apply non-VN linear-walkthrough semantics only when it explicitly says **NON-VN LINEAR WALKTHROUGH**.

Use whatever repository/file/web/issue capabilities are available. Command examples are illustrative.

If the caller/orchestrator explicitly specifies a review transport (for example, create/use a `route-accuracy` issue), follow that transport exactly. Only default to PR-first when no transport is specified.

## Mindset

Assume the guide is incorrect until each material claim is verified. Review adversarially: the goal is to find omissions, source mismatches, ordering errors, and unsupported details rather than to validate the author's framing.

## Scope

Verify factual accuracy and source fidelity. Do not fix route content.

You may update only the route's `reviewed` flag as the final approval action when no external review orchestrator is responsible for that state transition.

## Source loading

Read the game's `games.json` entry, `research.json`, and `guide.json`.

First verify that `games.json.guide_target`, `research.json.guide_target`, and `guide.json.guide_target` are identical and contain a specific label, platform, and linked release URL. Do not treat the broader VNDB `v...` work id as a substitute for the target release.

Then identify Japanese verification Set A and Set B and fetch the actual source material directly. If a set has multiple pages, inspect the components relevant to the route.

Before declaring a missing second Japanese lane to be a blocker, check whether the game's supplement contains an explicit owner-approved title-scoped source exception covering that exact fact. Verify the recorded approval provenance (date plus PR/comment, issue/comment, or explicit caller-approval context) so an author cannot self-grant the waiver. Honor a valid exception exactly as written: do not reopen it and do not extend it to unlisted facts. Verify that `research.json` describes the same exception scope without contradictory stale gate wording.

Do not:
- rely only on `research.json` summaries;
- count an inaccessible source as verified;
- treat a translation/derivative of Set A as independent Set B.

If either verification set fails the completeness/independence gate for a normally gated fact, the route cannot pass. The only exception is an exact fact covered by a valid, provenance-backed owner-approved title-scoped exception; all unlisted facts still require the normal gate.

## Review checklist

For the guide section under review, verify:

- every route-defining choice and its order;
- for opted-in non-VN walkthroughs, every canonical material progression fact has the required support: section/order progression, required story progression, irreversible choices, prerequisites/unlocks, endings, timing-critical optional placement, and missable/limited or unique-reward conditions presented as required for completion; one-source coverage is only for genuinely low-level non-branching execution details unless an exact owner exception applies;
- when sources print different literal choices within the same event, determine whether they are different decision points in the same sequence before treating them as contradictory;
- route prerequisites and unlock conditions;
- ending reachability;
- save positions (a save may be documented by only one set, but must be explicit there), including the canonical rule that a source conflict uses the **earlier documented position**;
- **every documented non-main ending detour is present** (bad, normal, alternate, or similarly labeled), including multiple detours from the same save;
- each save-backed non-main-ending chain starts at the first branch step, uses the exact documented `badEndPath` ending label, runs through the documented terminal, and is followed by the correct load-back step;
- a replay-from-beginning ending with no usable documented checkpoint is represented as a complete failed-play prefix ending at its explicit ending terminal, immediately followed by the route's normal opening sequence again, without an invented save;
- no `badEndPath` exists unless a Japanese source explicitly documents that non-main ending;
- `isLoad: true` appears only after a documented save-backed non-main ending detour;
- replay-from-beginning endings with no usable checkpoint use an explicit ending terminal plus a fresh repeated opening sequence, with no invented structural return marker;
- cross-route save numbering;
- no hallucinated or missing required choices;
- for normal VNs, every emitted player-action `simpleJp` is exact in-game text with no paraphrase, suffix, or location prefix, and save/load steps are the only normal non-choice `simpleJp` steps;
- for an explicitly opted-in non-VN walkthrough, apply the canonical game-walkthrough `simpleJp` rules instead: literal choices/menu labels remain exact, while concise author-written Japanese is allowed for navigation, battles, talks, pickups, preparation, and similar non-choice actions;
- useful available `enGuide` detail has not been silently dropped;
- no contradictions across guide sections;
- every route character has a directly verified portrait when a verifiable character image exists; a blank portrait is a finding unless research explicitly documents that an actual lookup found no suitable verifiable image;
- both `jpGuide1` and `jpGuide2` are non-empty on **every step**;
- each present source excerpt is verbatim;
- `（第一ガイドに記載なし）` is used only where the canonical omission rules permit it, including an exact fact whose valid owner-approved exception explicitly permits a missing Japanese lane;
- `（第二ガイドに記載なし）` is used only where the canonical omission rules permit it, including an exact fact whose valid owner-approved exception explicitly permits a missing Japanese lane;
- main-route-defining choices/prerequisites/route endings are independently supported by both sets unless that exact fact is covered by a valid owner-approved exception; an omission placeholder must never stand in for missing support outside the exception;
- optional non-main ending detours documented by one primary set are included when the other set is silent/non-contradictory, with the correct omission placeholder on detour-only steps; conflicting ending evidence is reconciled rather than guessed;
- the explicit linked `guide_target` matches repo/research/guide metadata and both verification sets actually apply to that exact release/platform.
- for newly registered/updated games, the game has an exact-target `cover_url` when a directly verifiable cover exists, or research documents that the lookup found none.

For a full review, check the route completely.

For a re-review after corrections:
- verify every corrected finding;
- re-check at least **20% of unchanged steps** (minimum one unchanged step when any exist), selected without bias/randomly where practical;
- if a correction can cascade into save numbering, route ordering, prerequisites, non-main-ending structure, or nearby source attribution, expand the re-review to every potentially affected step rather than stopping at 20%.

## Review record

Follow caller/orchestrator transport instructions first. If none are specified, follow the feedback-destination defaults in `agents/guide-standards.md`.

With no specified transport: when an open PR exists, put this route's review on that PR instead of creating a route issue; when no PR exists, use the existing issue workflow.

Use the canonical finding schema in `agents/guide-standards.md` for every accuracy finding.

Group all findings for one route/type into one PR comment or one fallback issue. Do not split every finding into separate issues/comments.

A clean PR review may be concise but must include content identifiers:
- `Route blob: <current route-file blob SHA/content hash>`
- `Research blob: <current research.json blob SHA/content hash>`

On PR re-review, include the same current identifiers with the resolved result. Before final approval, confirm the latest structural clean record's route blob matches the current route file and this accuracy clean record's route + research blobs match current content.

A clean issue-fallback review creates no issue.

## Re-review after author corrections

Re-fetch the relevant Japanese source material and verify every requested correction.

If review is on an open PR, comment on that PR:
- still wrong → state exactly what remains, using the same evidence schema;
- clean → explicitly confirm the prior findings are resolved.

If issue fallback is in use, comment/close the existing issue using the normal reviewer ownership rules.

Then confirm the structural gate is clean and set/report `reviewed: true` as described above.

Never mark a route reviewed while either gate is blocking.
