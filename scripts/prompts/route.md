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
    "simpleJp": "戦う",
    "jpGuide1": "verbatim text from primary JP source",
    "jpGuide2": "verbatim text from secondary JP source, or empty string",
    "enGuide": "English reference if available, or empty string"
  }
]
```

### Rules for simpleJp

**Every player action is a choice. Write the exact text from the choice box, nothing more.**

In a choice-based VN, every step where the player selects something — whether it is a dialogue option, a route branch, or a location/exploration selection screen — is a choice.

- Write the exact text that appears in the game's choice box, as plain text — no brackets, no punctuation added
- Examples: `戦う` `神社へ行く` `学校の外を探す` `このまま進む`
- **Never add** `を選ぶ`、`を選択する`、`に進む`、or any other suffix. The choice text alone is the step.
- **No location prefix** — omit 【場所】 entirely. Scenes transition automatically in this genre.
- The only steps without brackets are saves (`セーブ1`) and the final ending label

**Saves — required, not optional:**
- Insert a standalone save step **before** every branch point that leads to a bad end or different route
- Mirror the numbered slots from the source guides exactly: `セーブ1`, `セーブ2`, etc.
- Include a load step at the point the player must return: `セーブ1にロード`
- One action per step; never combine a save with a choice

### Rules for jpGuide1 / jpGuide2

**Copy character-by-character from the source page. Never paraphrase, summarize, or add your own words.**

Open the source URL. Find the line or bullet that corresponds to this step. Copy that text exactly as it appears — punctuation, symbols, spacing and all.

- If the source says `屋上へ　→　拓磨ルート`, write `屋上へ　→　拓磨ルート`
- If the source says `・戦う`, write `・戦う`
- Do not add chapter numbers or labels that are not in the source line itself
- Do not write `第二章：屋上` when the source just says `屋上` or `屋上を選択`
- If a source has no entry for this step, write an empty string — do not invent one

The test: paste your jpGuide text back into a search on the source page. It should find an exact match. If it does not, you summarized. Redo it.
- Cover the **complete** route from start to end — all required choices and transitions
- Stop at this route's ending; do not continue into the next route
- Output **only** a valid JSON array to `$ROUTE_FILE` — no markdown fences, no explanation

Generate route `$ROUTE_ID` only. Write the file, then stop.
