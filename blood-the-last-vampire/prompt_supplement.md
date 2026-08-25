
---

## Game-Specific Rules: Blood: The Last Vampire

This game has two mechanics beyond dialogue choices that **every player must perform to progress**. Both must appear as explicit guide steps — treating this as a pure choice-based VN will produce an unusable guide.

---

### Mechanic 1 — BSS (Blood Search System) taps

The BSS is a button the player presses during specific dialogue lines to activate a "blood search." Each successful BSS trigger raises the player's BLOOD level by one point and is required to unlock certain choices and endings later.

**The primary Japanese sources list every BSS trigger verbatim** — look for a dedicated BSS/ブラッドサーチシステム section or inline trigger markers in the walkthrough. Every listed trigger must become a guide step.

#### Step format for a BSS trigger

```json
{
  "simpleJp": "BSSタップ：「[dialogue excerpt]」",
  "jpGuide1": "[verbatim BSS trigger entry from source 1]",
  "jpGuide2": "[verbatim BSS trigger entry from source 2, or （第二ガイドに記載なし）]",
  "enGuide": "Blood Search System — tap here to raise BLOOD level"
}
```

- `simpleJp`: always starts with `BSSタップ：` followed by the exact dialogue line the player taps on, in quotation marks
- Place the BSS step at the exact position in the sequence where the trigger line appears — before the next choice if one follows, in order with surrounding steps if no choice follows immediately
- If the source groups multiple BSS triggers in a block (e.g. a list of 5 triggers before a save), insert each as a separate step in the order listed
- Never skip a documented trigger — each one is required BLOOD level progress

#### Example

```json
[
  {"simpleJp": "BSSタップ：「彼女の口元が歪んだ」", "jpGuide1": "彼女の口元が歪んだ＞", "jpGuide2": "彼女の口元が歪んだ", "enGuide": "Blood Search System — tap here to raise BLOOD level"},
  {"simpleJp": "BSSタップ：「黒い影が」", "jpGuide1": "黒い影が＞", "jpGuide2": "黒い影が", "enGuide": "Blood Search System — tap here to raise BLOOD level"},
  {"simpleJp": "セーブ3", "jpGuide1": "▼SAVE3", "jpGuide2": "SAVE3", "enGuide": ""},
  {"simpleJp": "追いかける", "jpGuide1": "追いかける＞", "jpGuide2": "追いかける", "enGuide": ""}
]
```

---

### Mechanic 2 — BLOOD level thresholds at gated choices

Some choices only appear (or lead to different outcomes) if the player's BLOOD level is at or above a threshold (e.g. 50, 70, 85, 100). The source documents these explicitly. When a threshold gates a choice, add a note step immediately before the gated choice.

#### Step format for a BLOOD level checkpoint

```json
{
  "simpleJp": "BLOODレベル確認：[N]以上必要",
  "jpGuide1": "[verbatim source text noting the threshold]",
  "jpGuide2": "[verbatim source 2 text, or （第二ガイドに記載なし）]",
  "enGuide": "BLOOD level must be [N] or higher to unlock this choice — if it is not, reload from your last save and collect more BSS triggers"
}
```

- `simpleJp`: always `BLOODレベル確認：` followed by the threshold (e.g. `70以上必要`)
- Place this step immediately before the choice it gates
- If BLOOD level affects which of several branches the player gets (not just whether a choice appears), document the threshold for the desired branch

#### Example

```json
[
  {"simpleJp": "BLOODレベル確認：70以上必要", "jpGuide1": "BLOODレベル70以上", "jpGuide2": "BLOOD level ≥70", "enGuide": "BLOOD level must be 70 or higher — if not, reload from your last save and collect more BSS triggers"},
  {"simpleJp": "テープを取る", "jpGuide1": "テープを取る＞", "jpGuide2": "テープを取る", "enGuide": ""}
]
```

---

### How the two mechanics interact with saves and bad ends

Saves should be placed before both gated choices and before BSS-heavy sections, so the player can reload if they miss triggers or don't meet a threshold. Source walkthroughs mark save points in the usual way (▼SAVE, セーブ, bold SAVE); apply the same cross-route numbering rules as any other game.

Bad ends in this game are reached through wrong choices exactly as in other VNs — the `badEndPath` / `isLoad` rules are unchanged. BSS trigger steps and BLOOD level checks are never tagged with `badEndPath`; they are always plain steps on the main route.

---

### Joukan-to-Gekan carry-over flags

Three named flags from Joukan carry over into Gekan and matter on the 瑠璃亜編 route. The research.json documents all three. When a choice sets one of these flags, note it clearly in `enGuide` so the player knows it is load-bearing:

- **瑠璃亜の過去フラグ** — set by asking Rulia why she became a chiropteran (required OFF for true ending)
- **吸血鬼の本フラグ** — set by buying the vampire book and letting Rulia keep it (required ON for true ending)
- **五匹の子豚さんフラグ** — set by winning over the karaoke 'mama-san' (required ON for true ending)

Example:
```json
{"simpleJp": "吸血鬼の本を買う", "jpGuide1": "吸血鬼の本を買う＞", "jpGuide2": "吸血鬼の本を買う", "enGuide": "Sets 吸血鬼の本フラグ — required ON for true ending (瑠璃亜編 / 真・瑠璃亜編)"}
```

---

### Complete guide means every required action

A complete Blood: The Last Vampire guide step list covers, in order:
1. Every BSS trigger the source documents (as `BSSタップ：` steps)
2. Every BLOOD level checkpoint before a gated choice (as `BLOODレベル確認：` steps)
3. Every save point (as `セーブN` steps)
4. Every bad-end detour with load (using `badEndPath` / `isLoad` as usual)
5. Every dialogue choice
6. Every carry-over flag choice (with `enGuide` noting the flag name and true-ending impact)

A guide that only lists dialogue choices is incomplete for this game.
