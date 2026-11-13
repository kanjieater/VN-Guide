# アマガミ エビコレ＋（2014 PS Vita）全エピローグ実行用チャート — evidence transcription and route ledger

> **AUTHOR RECONCILIATION (2026-11-12):** The runnable guide is now the ordered `route_*.json` files, not the shorthand transcription below. These notes retain the original EbiColle-compatible author's day/map layout for audit. All cross-route saves use unique numbered slots 1–19 in the route JSON, ordinal source choices are expanded to positional instructions, and all 34 formal epilogues plus the supplementary 上崎 sudden BAD are each mapped to explicit endings. The original article is not a literal-menu-choice source. **Independent structural and accuracy reviews remain pending.**


**Target:** Japanese 2014 PS Vita EbiColle+ only. **Scope:** 34 formal epilogues plus the extra 上崎 sudden BAD (35 outcomes), not CG/event 100%. **Status:** written source-backed *working itinerary*, not an independently reviewed or finalized VN-Guide route JSON. See [owner-approved evidence exception](https://github.com/kanjieater/VN-Guide/pull/116#issuecomment-6842545023).

**Primary written itinerary:** [0xwas, ゲーム版アマガミの全エピローグルート](https://note.com/heikin_fan_club/n/ne80b505878c5). Author explicitly states it works on EbiColle regardless of platform, **not** original full-price PS2. Independent ending-condition cross-checks: [攻略情報センター](https://game-kouryaku.info/amagami/ending.html), [@wiki gameplay](https://w.atwiki.jp/amagami/pages/98.html), [EbiColle differences](https://w.atwiki.jp/amagami/pages/91.html).

## How to read / execute

- Coordinates are the source's event-map coordinates, not dialogue text. Each day normally has four actions in order: 休1 → 休2 → 昼 → 放課後. `なし` = advance without selecting heroine event; `強制` = automatic event. `なし×N` means N such advances.
- `(1)`, `(2)`, `(3)` on an event mean **first, second, third displayed choice from the top**, *not* Japanese choice wording. `どれでも` means the source permits any. The shorthand names 絢/七/中/棚/森/桜 refer to 絢辻/七咲/中多/棚町/森島/桜井.
- Source's numbered saves are **local to its branches** and reused: create separately named save files/checkpoints per section to avoid overwriting. `今朝に戻る` is a game command, **not** a file reload. After endings, retain system clear data before loading an old save to unlock hidden routes.
- This is an exact-source **map/action transcription** with editorial day ordering repaired only where obvious. Any marked `⚠` source corruption/ambiguity must be checked in another written source or in-game; do not guess. For exact choice labels, the source gives ordinal positions only.
- Follow the sections in order; a section's `LOAD` is mandatory and is not a continuation of the previous ending.

## A. New game → day 15 shared preparation

```text
D01 32,36(絢) → 34,30(棚) → 31,28(桜) → なし
D02 34,38(絢) → 32,26(桜) → 強制 → なし
D03 33,38(絢) → 36,33(森) → 31,25(桜) → 強制(任意)
D04 28,37(七) → 37,33(森) → 強制のみ(桜の選択肢2、美也任意)
D05 36,28(棚,2) → SAVE A1 → なし×3
D06 なし×4(桜の選択肢任意)
D07 17,34
D08 なし×4
D09 なし×2 → 強制 → なし → 強制
D10 45,38(森) → 44,39(森) → 27,22(桜) → なし
D11 26,22(桜) → 22,31(中) → 22,30(中) → 強制
D12 45,39(森) → 42,22(棚) → 26,21(桜) → 27,47(七,任意)
D13 22,29(中,1または2) → なし → 強制(任意) → 33,48(絢)
D14 17,35(2)
D15 なし×2 → SAVE A2
```

**Source transcription fix:** original article prints D08 before D07; restored chronological order. D09 and other forced events sometimes exceed four tokens; treat forced prompts as additional event text, **not** a fifth time slot.

## B. ナカヨシ 絢辻・中多・桜井; other three ソエン

Continue from **A2**, preserving A1.

```text
D15 26,20(桜) → 26,18(桜)
D16 32,48(絢) → なし → 30,49(絢,1) → 21,29(中)
D17 25,18(桜) → なし → 22,28(中,1) → 21,28(中)
D18 なし×3 → 強制(休3任意)
D19 30,51(絢,1) → なし → 25,17(桜) → 24,17(桜)
D20 なし×3 → 25,16(桜,1→任意)
D21 17,36(2)
D22 なし×3 → 32,51(絢)
D23 なし×3 → 34,51(絢,1)
D24 なし×3 → 18,13(桜)
D25 16,31(中,1) → 19,13(桜) → 15,30(中) → 強制(任意)
D26 なし → 50,47(森) → 12,29(中) → 20,11(桜,任意)
D27 なし×2 → 39,49(絢,任意) → 39,50(絢)
D28 17,37
D29 なし×3 → 21,11(桜)
D30 なし×2 → 51,47(森) → 39,51(絢)
D31 なし → SAVE B3 → 39,52(絢) → 11,28(中,任意) → 強制
D32 10,26(中) → なし×2 → 強制
D33 強制 → 原文は「*2」と動詞を省略：本ルートでは強制→イベント選択なし×2→桜井イベントと解釈（@wikiの33日目強制／桜井座標と照合） → 21,10(桜)
D34 40,54(絢) → 21,09(桜) → なし×2
D35 17,38
D36–37 なし×4 each (D37 forced only)
D38 40,55(絢) → 41,55(絢) → 20,09(桜) → なし
D39 21,08(桜) → なし×3
D40 なし×4; when 放課後 forced event appears SAVE B4
```

At **B4** obtain the three ナカヨシ epilogues (絢辻/中多/桜井) by choosing the respective invitation/ending and using `今朝に戻る` to see the others. **Source does not print the literal invitations**.

**LOAD B3** for 棚町・七咲・森島 ソエン:

```text
D31 なし×2 → 強制
D32 58,08(棚) → 58,07(棚) → 58,06(棚) → 19,58(七)
D33 なし → 19,57(七) → なし → 52,47(森)
D34 なし×3 → 58,05(棚)
D35 17,38
D36 58,04(棚) → なし×3
D37 なし×4
D38 53,48(森) → 15,57(七) → なし×2
D39–40 なし×4 each
D41 completion/map: 今朝に戻る twice to view all three ソエン
```

## C. ナカヨシ 森島・七咲・棚町; other three ソエン

**LOAD A2** (D15):

```text
D15 41,21(棚,2) → 43,21(棚,任意)
D16 なし×2 → 46,41(森) → 28,48(七)
D17 なし×2 → 26,49(七) → 43,20(棚)
D18 44,20(棚,1) → なし → 27,49(七) → 47,42(森) [休3=1]
D19 なし → 28,50(七) → 27,51(七,1) → 47,40(森) [休3≠3]
D20 27,54(七) → 26,53(七,1) → なし → 47,39(森,1)
D21 17,36(2)
D22 なし×3 → 43,19(棚)
D23 なし×3 → 44,19(棚)
D24 53,42(森) → 52,45(森,任意) → なし → 25,54(七,会話話題：世間話→運動→食べ物→食べ物→アタック)
D25 なし×2 → 43,13(棚) → 54,42(森,2)
D26 なし×2 → 44,13(棚) → 54,45(森)
D27 なし×3 → 21,48(七,任意)
D28 17,37
D29 21,49(七) → 31,56(絢) → 31,57(絢) → 31,58(絢)
D30 45,12(棚) → 31,59(絢) → 31,60(絢) → なし
D31 なし×2 → 05,11(中) → 強制
D32 05,10(中) → なし → 14,04(桜) → 原文のセーブ(2)をセーブ5として別枠保存 → 53,41(森,任意×2)
D33 なし×3 → 20,49(七)
D34 なし×3 → 46,12(棚)
D35 17,38
D36–40 なし only; at D40 放課後 forced event SAVE C4
```

At **C4**, view ナカヨシ 森島/七咲/棚町 by selecting each invitation and returning to morning as required.

**LOAD B3** (the D31 セーブ(3) from the FIRST ナカヨシ route; this is intentional cross-section reuse, not an ambiguous new checkpoint) for 桜井/絢辻/中多 ソエン:

```text
D32 なし
D33 なし → なし → 13,03(桜) → なし
D34 13,04(桜) → なし×3
D35 17,38
D36 なし×4
D37 なし → SAVE C37 → 05,09(中,branch choice)
  Choice 1: 03,09(中)
D38 なし×2 → 05,08(中) → 04,08(中)
D39 03,08(中) → 03,07(中) → なし×2
D40 なし×3 → 強制
D41 今朝に戻る once for two endings; retain system data
LOAD C37; at 05,09(中) choose 2
D37 13,02(桜) → なし
D38 12,02(桜) → なし → 05,08(中) → 04,08(中)
D39 03,08(中) → 03,07(中) → なし×2
D40 なし×3 → 強制
D41 今朝に戻る twice for three endings
```

This split includes **both 中多 ソエン variants**. Do not overwrite C37.

## D. 絢辻＋中多 スキ and 上崎 hidden endings

After recording all six ナカヨシ clear records, **LOAD A1** at D5. System clear data must persist.

```text
D05 なし → 28,29(中) → 31,39(絢) [休3=1]
D06 28,28(中) → なし×2 → 強制(1)
D07 17,34
D08 26,28(中) → なし → 26,27(中,1 or 3) → なし
D09 なし×2 → 32,42(絢,任意) → 強制
D10 なし×4
D11 なし×2 → 18,24(中) → なし
D12 なし×3 → 強制
D13 19,24(中) → 18,23(中) → なし×2
D14 17,35(2)
D15 37,39(絢) → なし×3
D16 なし×3 → 39,40(絢)
D17 なし → 38,41(絢) → 39,42(絢) → なし
D18 強制 → なし×2 → 19,21(中,1→1)
D19 なし×3 → 38,43(絢,任意)
D20 39,43(絢,任意) → なし×2 → 40,43(絢)
D21 17,36(2)
D22–24 なし×4 each
D25 なし×3 → 10,23(中)
D26 なし×2 → 12,22(中) → 44,47(絢)
D27 12,21(中) → なし → 強制 → 13,20(中)
D28 17,37
D29 なし×3 → 13,19(中)
D30 45,49(絢) → なし×3
D31 なし → 46,50(絢) → なし → 強制
D32 なし → 14,18(中) → 12,18(中) → 45,50(絢)
D33 なし×2 → 44,51(絢) → 強制
D34 なし×4
D35 17,38
D36 なし×2 → 46,52(絢) → 47,52(絢,任意)
D37 なし×4
D38 なし×3 → 強制(任意×2)
D39 なし×2 → SAVE D39 → 49,52(絢) → なし
D40 なし×2 → 強制(1) → 上崎 events: choose third option in each printed prompt
    After event SAVE D40K → なし → 上崎 sudden BAD
LOAD D40K → 02,33(話題：おしゃれ→おしゃれ→おしゃれ→世間話→世間話, 任意) → choose each documented next option in separate replays to see 上崎 BEST and formal BAD
After both, 今朝に戻る; next choice unlocks 美也
D40 なし×2 → 強制(1→2) → SAVE D40S → 14,17(中,1) → 強制
D41 SAVE D41; choose date 10,13(中) OR 53,54(絢)
D42 if dated 中: see 中多 GOOD and 絢辻 BAD by alternating confession target/今朝に戻る
LOAD D41; choose other D41 date and alternate D42 confession target for 絢辻 GOOD and 中多 BAD
LOAD D40S → D40 なし → 強制 → D41 54,54 = 絢辻 BEST
LOAD D39 → D39 なし×2 → D40 なし → 14,17(中,1) → なし → 強制 [休3=2] → D41 11,12 = 中多 BEST
```

The date/confession principle is independently described by @wiki, but the exact prompt text remains ordinal. The source's two separate D40 blocks follow distinct loads/branches, not a single linear day.

## E. 桜井・棚町・七咲・森島 スキ, plus 美也

**LOAD A1** (D5), after hidden-route system unlock. At D5 choose 休3=3 to unlock 美也; source states her events then advance automatically without affecting heroine events.

```text
D05 38,33(森) → 37,28(棚,1) → 39,34(森,2) [休3=3]
D06 38,28(棚) → 32,24(桜) → なし → 31,23(桜,1)
D07 17,34
D08 38,35(森,1) → なし×3
D09 なし×3 → 強制
D10 26,41(七) → 27,42(会話話題：世間話→運動→世間話→運動→運動) → 28,42(会話話題略記（各ルートJSONで原文と照合して展開）) → なし
D11 29,20(桜) → 45,26(棚) → 45,36(森) → 強制
D12 44,35(森,任意) → 44,34(森) → 30,20(桜) → 44,26(棚)
D13 なし → 31,18(桜) → 23,37(七) → 22,39(七)
D14 17,35(2)
D15 なし → 30,17(桜) → 46,26(棚) → 47,26(棚)
D16 なし×3 → 48,26(棚,2)
D17 49,26(棚) → 31,17(桜) → なし → 23,39(七)
D18 21,39(七,2) → 22,40(七) → なし → 32,17(桜)
D19 なし×2 → after 休3 choice SAVE E19
```

### E1. 桜井＋棚町 スキ

```text
D19 34,18(桜) → 35,18(桜)
D20 49,25(棚,1) → なし×2 → 強制
D21 17,36(2)
D22 なし×3 → 強制
D23 なし×4
D24 なし×2 → 26,13(桜,1) → 27,13(桜,任意)
D25 強制 → 52,22(会話話題略記（各ルートJSONで原文と照合して展開）) → なし → 52,21(棚,2)
D26 なし×2 → 27,12(桜) → なし
D27 なし → 27,11(桜) → なし×2
D28 17,37
D29 強制 → なし×2 → 54,21(棚)
D30 なし → 強制 → なし → 29,11(桜)
D31 なし×3 → 強制
D32 なし×2 → 30,11(桜,1→任意×2) → 54,20(棚,1)
D33–36 なし×4 each [D34 休3=2; D35 17,28]
D37 なし → 56,20(棚,任意) → 55,19(棚,会話話題略記（各ルートJSONで原文と照合して展開）) → 31,11(桜,1)
D38 なし×4
D39 なし×3 → SAVE E39 → 32,11(桜,1)
D40 なし → SAVE E40 → 58,18(棚) → なし → 強制
D41 SAVE E41
D42 use day-41 date and day-42 confession alternations to see 桜井 GOOD/BAD and 棚町 GOOD/BAD; use 今朝に戻る and LOAD E41 to cover both dates
LOAD E40 → D40 なし×2 → 強制 → D41 36,05 = 桜井 BEST
LOAD E39 → D39 なし → D40 58,18(棚) → なし×2 → 強制 → D41 54,14 = 棚町 BEST
```

### E2. 七咲＋森島 スキ

**LOAD E19**:

```text
D19 21,41(七,任意) → 44,33(森)
D20 20,41(七) → なし×2 → 45,32(森,任意)
D21 強制; 七咲★
D22 なし×3 → 45,31(森)
D23 なし×4
D24 なし → 52,36(森) → 53,35(森) → 54,35(森)
D25 なし×3 → 54,36(森)
D26 17,44(七,会話話題略記（各ルートJSONで原文と照合して展開）) → 17,42(七,任意) → 18,42(七) → 16,42(七)
D27 14,43(七) → なし×2 → 16,44(七)
D28 17,37
D29 なし×3 → 15,42(七)
D30 なし×2 → 13,43(七) → 14,44(七)
D31 なし×3 → 強制
D32 なし×3 → 13,44(七)
D33 なし×3 → 55,36(森)
D34 なし×3 → 55,35(森) [休3=1]
D35 17,28
D36 強制 → なし×2 → 13,45(七,3)
D37 なし×2 → 14,42(会話話題略記（各ルートJSONで原文と照合して展開）)
D38 なし×4
D39 なし×2 → SAVE E39N → 55,37(森) → なし
D40 なし×2 → SAVE E40N → 08,48(七) → 強制
D41 SAVE E41N
D42 alternate dates/confessions and 今朝に戻る/LOAD E41N to see 七咲 GOOD/BAD and 森島 GOOD/BAD
LOAD E40N → D40 なし → D41 57,30 = 森島 BEST
LOAD E39N → D39 なし×2 → D40 なし×2 → SAVE E40NB → 08,48(七) → 強制 → D41 08,52 = 七咲 BEST
LOAD E40NB → D40 なし → 強制 → 美也 END → (32,30) automatic → (32,34) automatic all-epilogues completion
```


## Canonical save-slot ledger (ordered route JSON)

| Global slot | Section | Day | Purpose |
| --- | --- | --- | --- |
| 1 | 共通 | 5 | 上崎／美也解禁後の分岐用 |
| 2 | 共通 | 15 | ナカヨシ二分岐 |
| 3 | ナカヨシA | 31 | 両ソエン分岐の起点（Bからもロード） |
| 4 | ナカヨシA | 40 | 3人のナカヨシ招待 |
| 5 | ナカヨシB | 32 | 元資料で再使用のセーブ(2)を独立保存 |
| 6 | ナカヨシB | 40 | 3人のナカヨシ招待 |
| 7 | ナカヨシB | 37 | 中多ソエンの二種類分岐 |
| 8 | 絢辻・中多・上崎 | 39 | BESTと上崎の分岐前 |
| 9 | 絢辻・中多・上崎 | 40 | 上崎の2つのBAD/BEST用 |
| 10 | 絢辻・中多・上崎 | 40 | 絢辻のBEST用 |
| 11 | 絢辻・中多・上崎 | 41 | デート日によるGOOD/BAD 4種 |
| 12 | 4ヒロイン共通 | 19 | 桜井/棚町と七咲/森島への分岐 |
| 13, 14, 15 | 桜井・棚町 | 39, 40, 41 | 2 BEST分岐とデート分岐 |
| 16, 17, 18, 19 | 七咲・森島・美也 | 39, 40, 41, 40 (再ロード後) | 2 BEST／デート／美也分岐 |

**Branch semantics:** `今朝に戻る` keeps the same date state while replaying an outcome. To select a different date, load the previous D41 checkpoint. To restart a different two-heroine pair, explicitly load the preserved D19 checkpoint; to re-enter a hidden route, load the D5 checkpoint after maintaining completed system data. The scenario chronology does not permit continuing gameplay directly from an ending screen.

## Exact ending-branch execution checklist (cross-check against written itinerary)

The following is the **explicit operational expansion** of the article's abbreviated day-41/42 GOOD/BAD procedure. For each two-heroine pair, save immediately before the day-41 date choice, and preserve the two-star state.

| Pair | Day-41 date A | Confess on day 42 to A | Confess on day 42 to B | Reload day-41 checkpoint; date B | Confess to B | Confess to A |
|---|---|---|---|---|---|---|
| 絢辻 A / 中多 B | 53,54 絢辻 | 絢辻 GOOD | 中多 BAD | 10,13 中多 | 中多 GOOD | 絢辻 BAD |
| 桜井 A / 棚町 B | 桜井's displayed date event | 桜井 GOOD | 棚町 BAD | 棚町's displayed date event | 棚町 GOOD | 桜井 BAD |
| 七咲 A / 森島 B | 七咲's displayed date event | 七咲 GOOD | 森島 BAD | 森島's displayed date event | 森島 GOOD | 七咲 BAD |

**Important:** A day-42 confession after a date is not a new day-41 map selection. To collect both confessions for one date, select `今朝に戻る` on the ending's map (as 0xwas instructs). To change which heroine was dated, **load the day-41 checkpoint**, then select the other date. The original written guide prints the two map coordinates for 絢辻/中多, but abbreviates the other two pairs: **do not invent map coordinates** for 桜井/棚町 or 七咲/森島. Their two available starred date events must be identified in the current game state before selecting. This is an explicit unresolved executable detail, not a completed source-backed coordinate.

**Source-confirmed checkpoint dependency:** The source reuses local save labels 1–4 in each subsection. Save A1/A2, B3/B4, C37, D39/D40S/D41, E19/E39/E40/E41 and E39N/E40N/E41N are **editorial unique names** for the article's reused numbered checkpoints, not literal UI save-slot numbers. Never overwrite a save still needed by another branch. In the second ナカヨシ subsection, the source's `セーブ(3)` reference for the ソエン branch points to the day-31 branch made in the first ナカヨシ subsection, not the day-15 common save. This follows the source's explicit `ソエン3人 セーブ(3)から` and the only earlier `セーブ(3)` on day 31.

## Corrections verified against independent ending rules (2026-11-12)

1. The written primary source explicitly states `エビコレ版であれば機種は問いません` and explicitly excludes the original full-price PS2 version. It also specifies **all 35 outcomes**: six × five = 30, second 中多ソエン = 1, 上崎 three = 3, 美也 = 1. The source calls the 上崎 sudden BAD a distinct completion outcome; do not silently discard it as an irrelevant incidental GAME OVER.
2. The first ナカヨシ section creates `セーブ(3)` at **day 31**. The later ソエン section after ナカヨシ(2) explicitly starts from `セーブ(3)` even though ナカヨシ(2) itself does not create a save 3. Therefore **reload the earlier day-31 checkpoint**. This is not a contradiction or missing save.
3. For each two-heroine スキ pair, the independent ending guide defines **GOOD** as confessing to the heroine you actually dated on Christmas Eve, and **BAD** as confessing to the heroine whose date you skipped. The primary guide says return to the morning to view the other confession and load the day-41 save to choose the other date. Therefore the four outcomes are deterministic without needing exact text for the final confession options: date A→confess A = A GOOD; date A→confess B = B BAD; date B→confess B = B GOOD; date B→confess A = A BAD.
4. Independent ending guide specifies 上崎 hidden unlock requires all six heroines' スキ or ナカヨシ endings, the day-5 hidden choice, a heroine in LEVEL3 スキ, and day-40 choices; 美也 unlock requires the special 上崎 day-40 branch. **Do not begin the hidden route until system clear records have been saved.**
5. The independent ending guide distinguishes `カーテンコール` (32,30) from `オールエピローグコンプリート` (32,34); the original guide states both automatically trigger after 美也 on its complete run. They are not interchangeable achievements.

**Current evidence limits and resolved shorthands (2026-11-13):** The source writes day 33 as `強制→*2→21,10`, omitting the repeated-action verb; route JSON makes the no-event ×2 interpretation explicit and independently checks the day-33 event locations. Seemingly garbled parentheticals on days 10, 24–26 and 37 are the source's genuine shorthand for the conversation-topic sequence, expanded in route JSON using the official conversation-mode topic labels. The source's reused `セーブ(2)` has a unique global checkpoint (save5) rather than overwriting the common save2. A source-backed answer also resolves the final 32,30/32,34 playback: 0xwas explicitly prints `美也END→32,30自動再生→32,34自動再生(オールコンプリート！)`. The canonical route JSON now distinguishes 上崎's three selectable question subjects from the subsequent third-position romantic answer, includes formal BAD as a save-backed detour, and makes all date/confession branches explicit. The remaining unavoidable written-source limitation is absence of exact day-41 date-map coordinates for two heroine pairs; the player-facing route selects each named heroine's visible ★ date event instead of fabricating coordinates. Independent structural and accuracy reviewers must still confirm the final result.

## Verification before claiming finished

- [x] Expand authentic five-turn conversation-topic shorthand and preserve day-32 save2 as new slot5; day-33 omitted verb interpreted explicitly with independent wiki map event check.
- [x] Preserve every source local save as a unique slot 1–19 in chronological route order; referenced loads point to prior checkpoints (full in-game test still outstanding).
- [x] Expand each of the six heroines' GOOD/BAD date/confession decisions with separate day-41/day-42 steps, return-to-morning and day-41 reload distinctions.
- [x] Represent all six ナカヨシ, seven ソエン variants, 18 スキ endings, two formal 上崎 endings plus sudden BAD, and 美也 as individually identified terminal steps. **Not an in-game proof of all registered completion flags.**
- [x] Source-credit route JSON in canonical fields and leave `reviewed:false`; [ ] independent structural and accuracy reviewers must re-fetch current blob SHAs.

**Evidence status:** the seven `route_*.json` files contain the current author-corrected executable instructions and preserve the approved version-specific source exception. This ledger remains the historical source shorthand, not the player-facing guide. All review flags remain false until independent structural and accuracy review. The owner approved imperfect cross-source alignment, **not fabricated steps**.
