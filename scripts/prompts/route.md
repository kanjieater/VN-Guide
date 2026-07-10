$PROMPT_MD

---

## Current Task: Generate One Route

Game: $TITLE (VNDB: $VNDB_ID)
Route to generate: **$ROUTE_TITLE** (id: `$ROUTE_ID`)

Research file (read this first for sources): `$RESEARCH_FILE`
Output file: `$ROUTE_FILE`

### Instructions

1. Read `$RESEARCH_FILE` to find the Japanese guide URLs for this game.
2. Fetch those sources and locate the walkthrough for the **$ROUTE_TITLE** route only.
3. Apply the guide philosophy from above: reduce each step to the minimum needed to progress.
4. Write all steps for this route to `$ROUTE_FILE` as a JSON array.

### Step format

```json
[
  {
    "simpleJp": "アクション",
    "jpGuide1": "verbatim text from primary JP source",
    "jpGuide2": "verbatim text from secondary JP source, or empty string",
    "enGuide": "English reference if available, or empty string"
  }
]
```

### Rules for simpleJp

**Every player action is a choice. Every choice gets 「」 brackets. No exceptions.**

In a choice-based VN, every step where the player selects something — whether it is a dialogue option, a route branch, or a location/exploration selection screen — is a choice. All of them get 「」.

- Write the exact text that appears in the game's choice box, wrapped in 「」
- Examples: `「戦う」` `「神社へ行く」` `「学校の外を探す」` `「このまま進む」`
- **Never add** `を選ぶ`、`を選択する`、`に進む`、or any other suffix. The choice text alone is the step.
- **No location prefix** — omit 【場所】 entirely. Scenes transition automatically in this genre.
- The only steps without 「」 are saves (`セーブ1`) and the final ending label

**Saves — required, not optional:**
- Insert a standalone save step **before** every branch point that leads to a bad end or different route
- Mirror the numbered slots from the source guides exactly: `セーブ1`, `セーブ2`, etc.
- Include a load step at the point the player must return: `セーブ1にロード`
- One action per step; never combine a save with a choice

### Other rules

- `jpGuide1` / `jpGuide2`: copy the source text verbatim — do not summarize or rephrase. If the source lists the choice as 「戦う」, write exactly that. Chapter headers like 「第一章：〜」 are not verbatim source text.
- Cover the **complete** route from start to end — all required choices and transitions
- Stop at this route's ending; do not continue into the next route
- Output **only** a valid JSON array to `$ROUTE_FILE` — no markdown fences, no explanation

Generate route `$ROUTE_ID` only. Write the file, then stop.
