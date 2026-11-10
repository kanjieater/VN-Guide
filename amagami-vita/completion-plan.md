# アマガミ（PS Vita エビコレ＋）— 100% エピローグ攻略設計書

> **Status: RESEARCH / NOT YET A PLAYER-EXECUTABLE ROUTE GUIDE.** This is an author-owned source-checked completion plan, not a substitute for the required `route_*.json` arrays. It targets the **2014 Japanese PS Vita edition only**. Every route remains unreviewed.

## What “complete” means

The primary `オールエピローグコンプリート` condition covers the formal ending families below. The separate all-characters / Vita `カーテンコール` milestone requires all six main heroines' `スキ BEST` *and* `ナカヨシ` clear records, plus 上崎 and 美也. Clearing an ending alone does **not** guarantee a 100%-unlocked scene gallery; optional `アタック` variations and certain missed events require additional runs.

| Heroine | Formal endings | Important branch |
|---|---|---|
| 絢辻詞 | スキ BEST / GOOD / BAD; ナカヨシ; ソエン | Source-supported shared `スキ` playthrough for GOOD/BAD |
| 桜井梨穂子 | same five | Paired `スキ` progression for GOOD/BAD |
| 棚町薫 | same five | Paired `スキ` progression for GOOD/BAD |
| 中多紗江 | same five **plus a second ソエン variant** | Second `ソエン` variant appears after a qualifying prior clear |
| 七咲逢 | same five | Avoid pairing `絢辻＋七咲` for dual-★ plans; source says incompatible |
| 森島はるか | same five | Paired `スキ` progression for GOOD/BAD |
| 上崎裡沙 | BEST and a formal BAD epilogue | A separate earlier failure/BAD is documented by a speedrun chart; check whether it is a formal epilogue or an incidental ending |
| 橘美也 | hidden epilogue | Requires the post-上崎 unlock choice and avoidance of main-heroine Christmas commitments |

This is **34 formal epilogues** as enumerated by a separate 2026 Japanese-written overview: 6×5 = 30, one extra 紗江 ソエン = 31, 上崎 BEST/BAD = 33, 美也 = 34. The 2025 optimized written itinerary instead groups **three** 上崎 endings in its cleanup; that additional failure path must be preserved as **supplemental**, not silently counted as a second mandatory formal BAD. Resolve exact gallery-count semantics against game/achievement evidence before marking 100% complete.

## Core gameplay rules to turn into route steps

- One day has `休1`, `休2`, `昼`, and `放課後` action slots. The action map's coordinates are not dialogue choices. The first days of a route must specify *which slot* and *which coordinate*; “advance the story” is insufficient.
- The normal 40-day action cycle ends before day 41 Christmas Eve. Day 42 is a conditional post-double-booking confession outcome, not another routine action-map day.
- `スキ BEST`: secure one heroine's `LEVEL3 スキ` ★ and spend Christmas with her **without** the conflicting double-booking needed for GOOD/BAD.
- `スキ GOOD` / `スキ BAD`: reach `スキ` ★ with **two heroines** simultaneously, save before the day-41 dating choice, and alternate date partner/next-day confession partner to record both different outcomes. For GOOD, confess to the person dated; for BAD, confess to the one stood up. Use explicit save/reload or `今朝に戻る` at the correct boundary.
- `ナカヨシ`: pursue `LEVEL3 ナカヨシ` ★ and accept the appropriate Christmas party invitation. If multiple stars exist, decline unrelated invitations so the intended heroine's ending triggers.
- `ソエン`: progress the heroine's `ソエン` map events until her snowman/epilogue action appears. Ensure no `スキ` / `ナカヨシ` Christmas ending takes precedence; on the final conversation with 梅原 select the heroine. 紗江's `(05,09)` branch and `(03,09)` follow-up distinguish the second outcome; both must be verified as actual Vita states.
- Conversation and `アタック` are stateful. A route requiring a successful conversation must specify enough independent topic/action information to make it repeatable, or a *documented* retry/conditional recovery; “conversation success” is not an actionable route step.
- Do **not** treat PS2 full-price event coordinates as interchangeable with the EbiColle editions without checking the explicit EbiColle change log. Preserve any source-supported branch caused by an earlier relationship state.

## Hidden heroine prerequisites and recovery

### 上崎裡沙

1. First clear either a `スキ` or `ナカヨシ` ending **for each of the six main heroines**. The new event at day 5, `休3`, map coordinate `(14,34)` then becomes eligible.
2. Select the Japanese option leading into 上崎's route, documented on the hidden-character written guide. Advance **one** of the main heroines to `LEVEL3 スキ` and trigger the relevant jealousy storyline. For `エビコレ＋`, explicitly avoid the added trust-restoration/protection event that would otherwise terminate her story; the exact character-dependent coordinates are in the version-change page.
3. Keep a checkpoint before the day-40 `休3` decision. Choose the pursue-her branch, then select the source-confirmed affirmative relationship answer. During the required day-40 conversation, achieve the story's documented attack outcome rather than simply skipping the interaction.
4. At Christmas, the decisive choice determines BEST versus the formal BAD. Preserve both via a source-backed save/reload. The additional earlier failure described in the complete-run article is supplemental until its gallery-count status is confirmed.
5. To unlock 美也, separately replay the day-40 branch and decline a romantic relationship due to another girl; finish the run and persist the completion record.

### 橘美也

After recording the required 上崎 unlock, start/reload a legitimate pre-day-5 run. At day 5 `休3`, choose the newly available **美也** option. Let the additional home events occur, **do not** obtain an overriding main heroine Christmas date/party agreement, and complete the run. If using the optimized route's shared day-5 save, first verify that its save was created before the unlock event and can legitimately re-enter the newly added branch; do not assume a retroactive choice appears in an already finalized run.

## Source-backed efficient sequencing

The optimized EbiColle written all-epilogue itinerary offers the following **research plan** (not yet converted into numbered VN-Guide route actions):

1. Establish early multi-heroine relationship states and a genuinely reusable pre-day-5 checkpoint; this save is valuable only if the later hidden-route unlock is compatible with reload behavior.
2. Obtain the first three `ナカヨシ` ends, preserve an earlier branch for three `ソエン` ends, and recover the other three `ナカヨシ` and remaining `ソエン` ends, including both 紗江 variants.
3. Once six main heroines have a qualifying end recorded, replay into 上崎 while concurrently setting up the `絢辻＋中多` double-★ state. Collect the hidden outcomes plus their GOOD/BAD and BEST outcomes by save/reload.
4. Replay a compatible early save to earn `桜井＋棚町` `スキ` endings and `七咲＋森島` `スキ` endings; use separate supported branch saves so all BEST/GOOD/BAD variants are reachable.
5. Trigger the hidden 美也 ending without an overriding heroine holiday commitment. Finally check `オールキャラクリア`, `カーテンコール`, and `オールエピローグコンプリート` separately; do not claim optional scene/CG 100%.

For each phase, a final route must contain each required day/slot/map choice, save-slot number, actual Japanese literal decision text, story trigger, ending terminal, next saved state, and **both independent written evidence fields**.

## Source and edition map

**Exact target:** [KADOKAWA PS Vita release](https://www.kadokawa.co.jp/product/game1531/) (エビコレ＋, 2014-01-30).

**Complete EbiColle all-epilogue itinerary (independently authored; written, not its linked video):** [0xwas](https://note.com/heikin_fan_club/n/ne80b505878c5). It explicitly states the original full-price PS2 does not use its route and EbiColle platforms do. It contains calendar/map/save chronology and many *ordinal* choices rather than exact Japanese strings.

**Independent main Japanese choice/event pages:** [攻略情報センター](https://game-kouryaku.info/amagami/) with [絢辻](https://game-kouryaku.info/amagami/chart_ayatuji.html), [桜井](https://game-kouryaku.info/amagami/chart_sakurai.html), [棚町](https://game-kouryaku.info/amagami/chart_tanamati.html), [中多](https://game-kouryaku.info/amagami/chart_nakata.html), [七咲](https://game-kouryaku.info/amagami/chart_nanasaki.html), [森島](https://game-kouryaku.info/amagami/chart_morisima.html), [隠し](https://game-kouryaku.info/amagami/chart_sonota.html), [ending conditions](https://game-kouryaku.info/amagami/ending.html), and [two-heroine route](https://game-kouryaku.info/amagami/hukusuu_suki.html).

**Third written structure/version lane:** [Amagami @wiki](https://w.atwiki.jp/amagami/pages/98.html), [EbiColle event changes](https://w.atwiki.jp/amagami/pages/91.html), [unlock additions](https://w.atwiki.jp/amagami/pages/41.html), and [2026 independent overview](https://lm8.hatenablog.com/entry/2026/05/31/230051). The wiki warns that its base is the full-price PS2 game, so variant facts require reconciliation.

**English candidate:** [GameFAQs English author guide](https://gamefaqs.gamespot.com/vita/737951-amagami/faqs/80246/faq); PS2-centered, not a substitute for verified Vita literal choices.

**Open authoring defects:** complete exact wording at every progression-changing numbered decision, cross-source verification of *all* calendar-critical actions, per-character directly verified image URLs, source-grounded save/recovery topology, and the extra 上崎 BAD/official-epilogue count disagreement. Until those are satisfied, `research.json.verification_tier` must stay `blocked` and no route should be presented as a finished 100% guide.
