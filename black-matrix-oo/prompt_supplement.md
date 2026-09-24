# BLACK/MATRIX OO — game-specific guide supplement

**NON-VN LINEAR WALKTHROUGH**

This title is an ordinary SRPG, not a visual novel. Apply the explicitly scoped non-VN linear-walkthrough rules in `agents/guide-standards.md`. Do not change the repository schema.

## Structure

- Keep using `guide.json.routes` and `route_<id>.json`.
- Treat each stored "route" as the next sequential walkthrough section.
- Build one master order from the beginning of the game through 100% cleanup. The player must never need to leave one section, jump to another branch, and later return.
- Prefer chapter-sized sections, but split a chapter at an optional-content timing window when needed so the optional block can sit exactly where it is playable. Mark optional section titles with `【任意】`.
- Never make one optional route span mandatory story progression. If skipping the optional route would also skip required story steps, split the surrounding mandatory chapter section more finely.
- Group multiple optional events into one `【任意】` section when they share the same timing window; do not create separate routes merely to mirror tiny source entries.
- Multiple playthroughs are still one linear guide: first clear → NG+ / ending cleanup → final completion.

## Step writing

- `simpleJp` is the concise Japanese instruction the player should do next.
- Preserve literal in-game choice/menu text exactly when one exists.
- For travel, talking, battles, preparation, pickups, and similar gameplay, concise author-written Japanese instructions are allowed.
- Do not add `stepType` or any new route/guide fields.

## Battle coverage in the linear route

- Keep mandatory battles in their actual chronological position inside the same master walkthrough; do not create a detached combat appendix.
- Give battle-specific requirements their own actionable step when they affect story progression, a prerequisite/unlock, a bonus scenario, an ending, a missable/one-time reward, a key item, or another practical 100% condition.
- Routine tactics, recommended positioning, ordinary enemy cleanup, and other non-gating advice should normally remain optional detail on the relevant battle step rather than becoming mandatory progression steps.
- If a battle can be skipped, lost intentionally, won for a unique reward, or completed under a turn/kill condition that changes later content, preserve that consequence at the exact point where the battle occurs.

## Locked research lanes for this title

To avoid repeatedly rediscovering the same dead ends, keep these source roles fixed unless a newly discovered source is directly inspectable and materially stronger:

- **Set A is fixed:** Fragments Of Memories (derith) is the independent contemporary Japanese play diary and chronology lane.
- **Set B is a composite, not one missing magic walkthrough:** use currently directly inspectable Japanese material such as CRADLE, Wazap/5ch, RPG大辞典, and other components enumerated in `research.json`. FC2 pages that were historically inspected but currently return HTTP 403 remain provenance only for a fresh accuracy pass unless their exact fact is already covered by the enumerated 2026-09-22 owner exception.
- **TSST is derivative supplemental Japanese evidence only.** Its author explicitly says the bonus-scenario notes were preserved from an older vanished site. It is useful for trigger text and as a search lead, but it cannot establish independent Set-B verification.
- **FFSKY/SquareCN is a detailed original Chinese walkthrough, not the vanished Japanese archive.** Its author says the guide was written from his own month of work/play. It already supplies practical trigger chains, battle consequences, and useful hints for the unresolved scenarios. Preserve those facts for translated `enGuide` use, but it cannot satisfy the Japanese Set-A/Set-B gate.
- **Blocked FC2 search snippets are leads only.** Do not treat snippets as inspected evidence.
- **Historical recovery record:** the exact 2004攻略 thread is `http://game9.2ch.net/test/read.cgi/gameover/1086009241/` (`gameover`, not `gamesrpg`), and broad mirror/cache recovery was already exhausted. This is provenance, not an active gate.
- **NicoNico gameplay, the old攻略 thread, BLUE MATRIX, official-guide interiors, mirrors, and caches are historical recovery leads only.** They remain documented in `research.json` for provenance, but the owner-approved exception below means they are not active authoring/review blockers. Revisit them only if a concrete stronger source appears; do not restart broad recovery sweeps.

## Owner-approved source exception

**Approved by the repository owner on 2026-09-22. This exception is title-scoped to BLACK/MATRIX OO and must not be generalized to other guides.**

The owner explicitly approved moving forward with the Japanese and Chinese sources already recovered instead of continuing indefinite archive/video recovery, and explicitly approved rendering Chinese-source operational material as concise natural English in `enGuide`. For this title, that approval applies to the remaining documented single-lane gaps in the authored 100% route, not only the original four bonus-trigger gaps.

The normal two-independent-Japanese-source rule still governs facts that have two usable Japanese lanes. Where the research records a residual gap and the owner exception is invoked, use the strongest available combination of:

- Set A contemporary Japanese diary for chronology, observed outcomes, and directly recorded choices;
- directly inspectable or previously directly inspected Japanese Set-B material (FC2, CRADLE, Wazap/5ch, ending sources);
- derivative Japanese TSST only as corroboration, never as an independent Set-B source;
- original Chinese FFSKY for exact operational trigger, reward, or battle-condition detail, translated into concise natural English in `enGuide`.

**The 2026-09-23 request to make the walkthrough more operational is an authoring request, not a new source-gate waiver.** It must not be used to expand this exception. Exact FFSKY-only details outside the enumerated 2026-09-22 exception—such as BS8/BS12 fuller NPC order, the post-5-2 構成員女 / 巡礼する精霊 pairing, or BS13's extra pre-notebook conversations / ordinal choice—may remain supplemental `enGuide` context but must not become required `simpleJp` actions without independent Japanese support or a separate explicit owner approval.

The approved exception specifically includes the currently identified residual facts needed by the authored route:

- BS2/3 trigger/timing;
- grouped BS5/6 triggers;
- BS10 trigger/timing;
- BS14 prerequisite/trigger chain;
- the chapter-6 optional branch/reward conditions;
- BS11's full two-choice sequence where Set A directly establishes `頑張る` for the Yohane/Dana path and TSST/FFSKY establish the later `もうちょっと` transition into ダーナの試練;
- the six literal NG+ answers leading to `それぞれの明日`, accepted from the existing Japanese ending lane together with Set A's observed best-ending run/outcome even though Set A does not print all six literals;
- the listed one-time/unique reward conditions used by the 100% route when the Japanese chronology/battle context is established but the exact reward trigger survives only in FFSKY: `過酷な抱擁` / `募る思いの告白` at 4-2, `破滅の降罪` at 5-1, `盟約の協定` at 5-3, `ファニーナイフ` in chapter 8, `火霊のピアス` after 8-3, and the 10-2 `拷責の神音` / `覇道を叫ぶ雷光` / `神をも滅する剱` rewards.

Do not fabricate Japanese source support to make an exception look like a normal two-set pass. When one Japanese lane does not contain the literal/action, keep the normal omission placeholder in that `jpGuide` field. Chinese text must never be copied into `jpGuide1` or `jpGuide2`.

For BS11, preserve both choices in order: `頑張る` first to remain on the Yohane/Dana sequence, then the later `もうちょっと` choice immediately before ダーナの試練.

This exception closes the BLACK/MATRIX OO research gate and supersedes narrower earlier wording that limited the owner exception to four bonus-scenario gaps. Do not resume generic mirror hunting or require gameplay-video verification before authoring/review.

## Supplemental English-reference lane

- The detailed Chinese FFSKY/SquareCN walkthrough is supplemental only and never satisfies Japanese Set A or Set B.
- It may be used as the English-reference lane for `enGuide`: translate the relevant Chinese evidence into concise English rather than copying Chinese prose into the finished guide.
- Use that supplemental detail to enrich battle conditions, item consequences, trigger sequences, and practical hints only after the underlying progression-critical fact is allowed by the Japanese source gate.
- Never copy Chinese text into `jpGuide1` or `jpGuide2`, and never use it to conceal missing independent Japanese support for an unlock, ending condition, missable timing window, or other material progression fact.

## Completion target

The intended finished guide should cover, when source-verified:

- the complete mandatory story/battle sequence;
- all 14 bonus scenarios and their correct timing;
- ending-affecting choices and prerequisites;
- all endings / NG+ requirements needed for practical scenario completion;
- important missable or one-time content that a 100% player would reasonably expect.

Do not turn repeatable grinding, max-stat optimization, or arbitrary farming into mandatory steps unless a verified completion requirement depends on it.

## Source discipline

The normal two-independent-Japanese-source gate still applies to every fact outside the explicitly enumerated owner-approved exceptions above. Non-Japanese walkthroughs do not become Japanese Set A or Set B. Do not generate route files while `research.json` documents an unresolved primary-source blocker for an unexcepted material fact.
