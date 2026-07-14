$PROMPT_MD

---

## Current Task: Generate One Route

Game: $TITLE (VNDB: $VNDB_ID)
Route to generate: **$ROUTE_TITLE** (id: `$ROUTE_ID`)
Save slot offset for this route: **$SAVE_OFFSET** (first save in this route = セーブ$SAVE_OFFSET_PLUS1)

Research file (read this first for sources): `$RESEARCH_FILE`
Output file: `$ROUTE_FILE`

### Instructions

1. Read `$RESEARCH_FILE` to find the Japanese guide URLs for this game.
2. Fetch **both** primary Japanese sources and locate the walkthrough for the **$ROUTE_TITLE** route.
3. Cross-validate every choice and every save point between sources before writing anything.
4. Write all steps for this route to `$ROUTE_FILE` as a JSON array.

### Step format

```json
[
  {
    "simpleJp": "戦う",
    "jpGuide1": "verbatim text from primary JP source",
    "jpGuide2": "verbatim text from secondary JP source",
    "enGuide": "English reference if available, or empty string"
  }
]
```

For save points with a documented bad ending, use this four-step sequence:

```json
[
  {"simpleJp": "セーブ9", "jpGuide1": "▼SAVE9", "jpGuide2": "SAVE9", "enGuide": ""},
  {"simpleJp": "呼び止める", "jpGuide1": "呼び止める → バッドエンド9", "jpGuide2": "呼び止める → BAD END 9", "enGuide": "", "badEndPath": "バッドエンド9"},
  {"simpleJp": "セーブ9にロード", "jpGuide1": "セーブ9にロード", "jpGuide2": "LOAD SAVE9", "enGuide": "", "isLoad": true},
  {"simpleJp": "通り過ぎる", "jpGuide1": "・通り過ぎる", "jpGuide2": "通り過ぎる", "enGuide": ""}
]
```

- `badEndPath`: string — the bad end label from source (e.g. `バッドエンド9`, `BAD END 9`)
- `isLoad`: boolean `true` — marks the step as a load-back instruction
- The SPA renders `badEndPath` steps in red with a ⚠ badge, and `isLoad` steps in blue with ↩

### Rules for simpleJp

**Every player action is a choice. Write the exact text from the choice box, nothing more.**

- Write the exact text that appears in the game's choice box, as plain text — no brackets, no punctuation added
- Examples: `戦う` `神社へ行く` `学校の外を探す` `このまま進む`
- **Never add** `を選ぶ`、`を選択する`、`に進む`、or any other suffix. The choice text alone is the step.
- **No location prefix** — omit 【場所】 entirely. Scenes transition automatically in this genre.
- Save steps and load steps are the only non-choice steps.

### Rules for jpGuide1 / jpGuide2

**Both must be populated for every step. Copy character-by-character from each source. Never paraphrase.**

Open each source URL. Find the line or bullet that corresponds to this step. Copy that text exactly — punctuation, symbols, spacing and all.

- If source 1 says `・戦う`, write `・戦う`
- If source 2 says `SAVE1` (bold), write `SAVE1`
- Do not add chapter numbers or labels that are not in the source line itself
- Do not write `第二章：屋上` when the source just says `屋上`
- If a source genuinely has no entry for this step (e.g. a save point that only appears in one source), write the other source's text in both fields and note which source it comes from
- Never write an empty string in both jpGuide1 and jpGuide2 — always populate at least one

The test: paste your jpGuide text back into a search on the source page. It should find an exact match. If it does not, you summarized. Redo it.

### Rules for saves — required, validated, cross-route numbered

**Cross-validate first:** Only include a save point if at least one source explicitly marks it (▼SAVE, セーブ, SAVE bold, etc.). When sources disagree on where a save goes, use the **earlier** position (earlier = more useful to the player). When sources disagree on whether a save exists at all, include it if any source has it.

**Cross-route numbering:** Save slots span all routes in play order. This route's first save uses slot **$SAVE_OFFSET_PLUS1** (continuing from previous routes). Number sequentially: セーブ$SAVE_OFFSET_PLUS1, セーブ$SAVE_OFFSET_PLUS2, etc.

- Insert a standalone save step immediately **before** every save-indicated choice
- One action per step — never combine save with choice
- Never invent saves that no source documents

### Rules for bad end steps

The guide actively leads players through every bad end before continuing. Do not just annotate save steps — insert explicit steps.

At every save point with a documented bad ending, insert this sequence (described above in Step format):
1. Save step
2. Bad-end choice step (`badEndPath` field = bad end label from source)
3. Load step (`isLoad: true`, simpleJp = `セーブNにロード`)
4. Good choice step

- `badEndPath`: exact bad end label from source — never invent
- `isLoad`: always `true` on load steps; always `false` (omit) on all other steps
- If a save point has multiple bad ends from different branches, insert each bad-end-choice + load pair before the good branch
- If no source documents a bad end at this save point, just include the save step and good choice — no `badEndPath` or `isLoad` steps

### Summary

- Cover the **complete** route from start to end — all required choices and transitions
- Stop at this route's ending; do not continue into the next route
- Output **only** a valid JSON array to `$ROUTE_FILE` — no markdown fences, no explanation

Generate route `$ROUTE_ID` only. Write the file, then stop.
