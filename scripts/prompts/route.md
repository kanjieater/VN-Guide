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

- Keep it to the action only — no location prefix unless the player must explicitly navigate somewhere
- If the game transitions scenes automatically (most otome/ADV games), **omit the location tag**
- Only use 【場所】 when the player is presented with a navigation menu or must choose where to go
- For choices: `「選択肢のテキスト」を選ぶ`
- For saves: `セーブする（ルート分岐前）` — add a save step **before** any choice that branches to a different route or ending
- One action per step; do not combine multiple actions

### Other rules

- `jpGuide1` / `jpGuide2`: preserve source wording exactly (this is the hidden reference section from the instructions above)
- Cover the **complete** route from start to end — all required choices and transitions
- Stop at this route's ending; do not continue into the next route
- Output **only** a valid JSON array to `$ROUTE_FILE` — no markdown fences, no explanation

Generate route `$ROUTE_ID` only. Write the file, then stop.
