# BLACK/MATRIX OO — game-specific guide supplement

**NON-VN LINEAR WALKTHROUGH**

This title is an ordinary SRPG, not a visual novel. Apply the explicitly scoped non-VN linear-walkthrough rules in `.claude/guide-standards.md`. Do not change the repository schema.

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
- **Set B is a composite, not one missing magic walkthrough:** use the directly inspectable Japanese FC2 child pages, CRADLE battle ordering, Japanese ending/NG+ sources, Wazap/5ch corroboration, and other directly inspectable Japanese components already enumerated in `research.json`. Extend Set B only with a directly inspected Japanese source that closes a specific remaining progression-critical gap.
- **TSST is derivative supplemental Japanese evidence only.** Its author explicitly says the bonus-scenario notes were preserved from an older vanished site. It is useful for trigger text and as a search lead, but it cannot establish independent Set-B verification.
- **FFSKY/SquareCN is a detailed original Chinese walkthrough, not the vanished Japanese archive.** Its author says the guide was written from his own month of work/play. It already supplies practical trigger chains, battle consequences, and useful hints for the unresolved scenarios. Preserve those facts for translated `enGuide` use, but it cannot satisfy the Japanese Set-A/Set-B gate.
- **Blocked FC2 search snippets are leads only.** Do not treat snippets as inspected evidence.
- **The 2004 攻略スレ, BLUE MATRIX lead, official-guide interiors, mirrors, and caches are recovery leads only.** Do not spend another pass broadly rediscovering these same leads. Retry one only when a concrete directly inspectable URL/page/scan has been found.
- **The exact 2004攻略 thread is now identified:** `http://game9.2ch.net/test/read.cgi/gameover/1086009241/` (`gameover`, not `gamesrpg`). Generic mirror/cache recovery has already been attempted without directly inspectable trigger text. Do not search the wrong board or repeat broad mirror sweeps; revisit only if a concrete surviving copy is discovered.
- **Next-source priority is the independent NicoNico gameplay series `mylist/38903044`.** Chapter 3/4/7/9 parts are mapped in `research.json`. Do not promote metadata alone; directly watch the relevant free-action sequence and record the visible trigger actions/timing. If the current environment cannot play NicoNico, leave this as a handoff rather than restarting exhausted Wazap/mirror/official-guide searches.

The unresolved research task is therefore **Japanese corroboration, not gameplay discovery**. The operational trigger chains are already known from supplemental sources; research should target only the exact Japanese facts still listed as open in `research.json`.

## Owner-approved source exception

**Approved by the repository owner on 2026-09-22. This exception is title-scoped to BLACK/MATRIX OO and must not be generalized to other guides.**

The research gate may proceed without further video/archive recovery for exactly four residual bonus-scenario evidence gaps: BS2/3, grouped BS5/6, BS10, and the remaining BS14 prerequisite/trigger chain.

For those four gaps only:

- retain the already verified Japanese Set-A chronology and all directly inspected Japanese Set-B evidence;
- permit the directly inspected Japanese TSST bonus memo as derivative corroboration;
- permit the directly inspected original Chinese FFSKY walkthrough to supply operational trigger/action detail and practical hints. **Render those facts as concise natural English in `enGuide`; `enGuide` is a translation/summary field and does not need to match the Chinese source wording.**
- where TSST is incomplete but FFSKY is explicit, use FFSKY's fuller operational sequence while documenting that provenance;
- specifically, BS6 includes the young Cipher Punk member in addition to the woman/man, and BS10 includes the waitress after シリア;
- BS14's セングラー requirement remains backed by direct Japanese Set-B evidence; the exception covers only BS4+BS7+BS10 and 雑記帳「カイン様」→ウェイター;
- never copy Chinese text into `jpGuide1` or `jpGuide2`. Use Japanese source text where available and the normal omission placeholder when the exception leaves one Japanese source field undocumented.

This owner-approved exception closes the research gate for BLACK/MATRIX OO. Do not resume generic mirror hunting or require gameplay-video verification before authoring. This approval also permits FFSKY to supply concise English `enGuide` wording for residual low-level operational details (for example the chapter-6 optional branch/reward conditions) when the Japanese chronology/section placement is already established. This does not turn FFSKY into a Japanese verification set: keep `jpGuide1`/`jpGuide2` Japanese-only, using directly inspected Japanese text or the normal omission placeholder.

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

The normal two-independent-Japanese-source gate still applies. Non-Japanese walkthroughs may be useful supplementary research but do not satisfy either primary Japanese verification set. Do not generate route files while `research.json` documents an unresolved primary-source blocker.
