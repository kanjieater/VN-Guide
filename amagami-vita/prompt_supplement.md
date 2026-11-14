# エビコレ＋ アマガミ（PlayStation Vita） — game-specific authoring supplement

**NON-VN LINEAR WALKTHROUGH**

This title is a calendar/map-driven romance **simulation**, not a choice-only visual novel. The caller explicitly targets the Japanese 2014 PS Vita edition; **no PS2 full-price or PSP retarget** is permitted.

## Use the existing VN-Guide JSON schema

- Treat a route file as an **ordered playthrough section**, not necessarily one isolated heroine. `recommended_order` must form a single executable chronology for **all formal epilogues** with an explicit state transition, save/load, or new run before moving to the next section. Multiple characters necessarily progress simultaneously.
- For navigation actions without a unique displayed option label, `simpleJp` may be an accurate concise Japanese instruction, such as choosing a *verified* map coordinate during a specific day's `休1`, `休2`, `昼`, or `放課後`. This uses the canonical non-VN game-walkthrough mode rather than a new step schema.
- When a choice has literal text, **use the exact Japanese in-game wording from a directly inspected Japanese written source**. A writer's ordinal shorthand (1/2/3) is not proof of literal text. Do not transform ordinal-only choices into guessed text. Under the owner exception below, an ordinal explicitly printed in the EbiColle-compatible written itinerary may be rendered as a positional instruction (e.g. 「上から2番目を選ぶ」), clearly labeled as an ordinal instruction, NOT as a verbatim Japanese menu quote. If an ordinal is ambiguous or its event/state cannot be identified, document and resolve that blocker; do not guess.
- `jpGuide1` and `jpGuide2` quote the respective written sources independently. Use only the canonical omission placeholders when a source does not explicitly document an action. Keep sources and article text distinct; never backfill a quote from a different author.
- Distinguish forced/automatic events, ordinary map selections, day- or slot-limited actions, conversation/attack minigames, and actual player-choice prompts. Every source-supported required action gets one executable step; do not emit objective-only “clear heroine” steps.
- Never imply that 41st-day epilogues are followed by another run without an explicit save/load or fresh run; `今朝に戻る` is not the same operation as reloading an unrelated save slot. Save slots must be numbered sequentially and source-documented.

## Exact-release and evidence requirements

- A viable source must explicitly apply to EbiColle PS Vita or have each applicable difference reconciled using written EbiColle release-change material. The original PS2 game differs in event availability; see https://w.atwiki.jp/amagami/pages/91.html .
- Use the standard two independent Japanese written-source sets plus independent English search. An English PS2 walkthrough may explain mechanics but cannot establish a Vita-specific option, state, or progression requirement. When Japanese sources disagree, investigate a third independently authored written walkthrough before blocking, but do not equate differing prior saves/relationship states.
- The non-VN **material-progression source requirement is unchanged**: both independent sets must support material unlocks, irreversible choices, ending predicates and save/replay boundaries unless an exact repository-owner-approved exception is recorded. **Title-scoped owner exception below relaxes full second-source calendar/map/save agreement, but not source-grounded ending reachability.**
- Route content must **not** be created while `research.json.verification_tier` remains `blocked` **unless it is covered by the exact title-scoped owner exception below and the step itself is supported by written evidence**. Mark `reviewed:false` and leave structural and accuracy PASS to independent reviewer roles.

## Repository-owner-approved scoped exception (2026-11-12)

Provenance: [PR #116 Conversation comment #6842545023](https://github.com/kanjieater/VN-Guide/pull/116#issuecomment-6842545023), recording the owner's explicit in-chat instruction: “Obviously they dont have to completely match to get to the end perfectly ... We just need routes to get all endongs properly.”

For this **2014 Japanese PS Vita EbiColle+ Amagami** ending-complete guide ONLY, two independent written sources **need not match every day/slot/map/save step**. Use [0xwas's written EbiColle-compatible all-epilogue itinerary](https://note.com/heikin_fan_club/n/ne80b505878c5) for calendar/coordinate/ordinal/save sequencing, corroborated by [攻略情報センター ending conditions](https://game-kouryaku.info/amagami/ending.html) and independently hosted Japanese @wiki mechanics and release-change evidence. Explicit numbered options from the itinerary may be shown as **positional instructions**, clearly distinguished from actual verbatim choice labels; never manufacture literal text. Do not treat partial independent corroboration as a second complete guide, or assume an English translation is independent.

This exception **does not** waive edition fidelity, real evidence for ending-critical state/unlocks, source honesty, explicit save/load/new-run transitions, or reviewer independence. Unresolved contradictions and corrupted/ambiguous ordinal/map tokens remain local blockers to be reconciled; don't silently invent a solution. Cover 34 formal epilogues plus the distinct extra 上崎 sudden BAD (35 outcomes); do not require gallery completion. Keep all `reviewed:false` until independent review.

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
