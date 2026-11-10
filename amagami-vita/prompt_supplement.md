# エビコレ＋ アマガミ（PlayStation Vita） — game-specific authoring supplement

**NON-VN LINEAR WALKTHROUGH**

This title is a calendar/map-driven romance **simulation**, not a choice-only visual novel. The caller explicitly targets the Japanese 2014 PS Vita edition; **no PS2 full-price or PSP retarget** is permitted.

## Use the existing VN-Guide JSON schema

- Treat a route file as an **ordered playthrough section**, not necessarily one isolated heroine. `recommended_order` must form a single executable chronology for **all formal epilogues** with an explicit state transition, save/load, or new run before moving to the next section. Multiple characters necessarily progress simultaneously.
- For navigation actions without a unique displayed option label, `simpleJp` may be an accurate concise Japanese instruction, such as choosing a *verified* map coordinate during a specific day's `休1`, `休2`, `昼`, or `放課後`. This uses the canonical non-VN game-walkthrough mode rather than a new step schema.
- When a choice has literal text, **use the exact Japanese in-game wording from a directly inspected Japanese written source**. A writer's ordinal shorthand (1/2/3) is not proof of literal text. Do not transform ordinal-only choices into guessed text. Where the complete path depends on an unresolved ordinal choice, stop and document the exact blocker.
- `jpGuide1` and `jpGuide2` quote the respective written sources independently. Use only the canonical omission placeholders when a source does not explicitly document an action. Keep sources and article text distinct; never backfill a quote from a different author.
- Distinguish forced/automatic events, ordinary map selections, day- or slot-limited actions, conversation/attack minigames, and actual player-choice prompts. Every source-supported required action gets one executable step; do not emit objective-only “clear heroine” steps.
- Never imply that 41st-day epilogues are followed by another run without an explicit save/load or fresh run; `今朝に戻る` is not the same operation as reloading an unrelated save slot. Save slots must be numbered sequentially and source-documented.

## Exact-release and evidence requirements

- A viable source must explicitly apply to EbiColle PS Vita or have each applicable difference reconciled using written EbiColle release-change material. The original PS2 game differs in event availability; see https://w.atwiki.jp/amagami/pages/91.html .
- Use the standard two independent Japanese written-source sets plus independent English search. An English PS2 walkthrough may explain mechanics but cannot establish a Vita-specific option, state, or progression requirement. When Japanese sources disagree, investigate a third independently authored written walkthrough before blocking, but do not equate differing prior saves/relationship states.
- The non-VN **material-progression source requirement is unchanged**: both independent sets must support material unlocks, irreversible choices, ending predicates and save/replay boundaries unless an exact repository-owner-approved exception is recorded. **This supplement contains no source-gate exemption.**
- Route content must **not** be created while `research.json.verification_tier` remains `blocked`. Mark `reviewed:false` and leave structural and accuracy PASS to independent reviewer roles.

## Full guide completion scope

- Six main heroines, each with `スキ BEST`, `スキ GOOD`, `スキ BAD`, `ナカヨシ` and `ソエン` endings; 中多紗江 has a distinct `ソエン` branch to verify.
- Hidden 上崎裡沙 (BEST and the **formal** BAD epilogue; record the distinct additional sudden BAD separately if it is not a formal epilogue) and 橘美也.
- Source-grounded double-booking for GOOD/BAD outcomes; unlock of the two hidden heroines, `カーテンコール`, and `オールエピローグコンプリート`.
- Clearly distinguish **formal completion epilogues** from incidental BAD END / GAME OVER events. An all-epilogue guide is not automatically an all-events/100%-scene gallery guide.

## Reference written sources

- Edition-compatible optimized itinerary: https://note.com/heikin_fan_club/n/ne80b505878c5
- Independent event/ending tables and exact-choice fragments: https://game-kouryaku.info/amagami/
- Independent structural and EbiColle change verification: https://w.atwiki.jp/amagami/pages/91.html
- Game's own map/conversation specification: https://www.amagami.info/intro03.html
