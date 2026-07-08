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

- **For choices: use the exact choice text verbatim** — just `「選択肢」`. Do not add 「を選ぶ」 or any description. If the source says 「戦う」, write `「戦う」`.
- **No location prefix** — for otome/ADV games scenes transition automatically; omit 【場所】 entirely unless the player faces an explicit navigation menu.
- For saves: standalone step before any branch point
  - Mirror source guide numbered slots exactly: `セーブ1`
  - Include a load step where the player returns: `セーブ1にロード`
  - If no numbered scheme in sources: `セーブ`
- One action per step; do not combine

### Other rules

- `jpGuide1` / `jpGuide2`: preserve source wording exactly (this is the hidden reference section from the instructions above)
- Cover the **complete** route from start to end — all required choices and transitions
- Stop at this route's ending; do not continue into the next route
- Output **only** a valid JSON array to `$ROUTE_FILE` — no markdown fences, no explanation

Generate route `$ROUTE_ID` only. Write the file, then stop.
