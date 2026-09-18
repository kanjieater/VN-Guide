$PROMPT_MD
$GAME_NOTES

---

## Current Task: Generate One Route

Game: $TITLE (VNDB: $VNDB_ID)
Route: **$ROUTE_TITLE** (id: `$ROUTE_ID`)
Save slot offset: **$SAVE_OFFSET** (first new save in this route = セーブ$SAVE_OFFSET_PLUS1)

Research file: `$RESEARCH_FILE`
Output file: `$ROUTE_FILE`

### Instructions

1. Read `$RESEARCH_FILE`.
2. Confirm Japanese verification Set A and Set B both satisfy the canonical research gate for this route. If not, stop without generating route content.
3. Fetch the relevant components of both sets directly.
4. Reconcile every route-defining choice, prerequisite/unlock, ending, and documented save before writing.
5. Write the complete route as a JSON array to `$ROUTE_FILE`.

### Step format

```json
[
  {
    "simpleJp": "戦う",
    "jpGuide1": "verbatim text from Set A",
    "jpGuide2": "verbatim text from Set B, or （第二ガイドに記載なし）",
    "enGuide": ""
  }
]
```

### `simpleJp`

Every player action is the exact in-game choice text, with no added suffix or location prefix.

Save/load instructions are the only non-choice steps.

### Source fields

Both `jpGuide1` and `jpGuide2` must be non-empty on every step.

- `jpGuide1`: exact verbatim text from Set A.
- If a required step has no exact Set-A text, stop: the Set-A source assignment is insufficient. Find a directly inspectable Set-A source that documents the step or document the blocker. Never leave `jpGuide1` empty or fabricate text.
- `jpGuide2`: exact verbatim text from Set B when that exact step is printed there.
- If Set B independently supports the surrounding route/ending but does not print the exact step, use exactly `（第二ガイドに記載なし）`.
- `（第二ガイドに記載なし）` is the only permitted missing-source placeholder.
- Never copy Set A into `jpGuide2`.
- Preserve whitespace and punctuation exactly.

### Saves

- Include a save only when at least one primary set explicitly documents it.
- If only one set documents the save, that is allowed; mark the other source field as not documented rather than inventing text.
- When sources disagree on save position, use the earlier documented position.
- Save slots are sequential across routes in recommended play order.
- Insert a standalone save step immediately before the action it protects.

### Bad-end loads vs ordinary route-entry loads

`isLoad: true` has one meaning only: it terminates a `badEndPath` detour and returns to the main route.

Bad-end pattern:

```json
[
  {"simpleJp":"セーブ9","jpGuide1":"▼SAVE9","jpGuide2":"SAVE9","enGuide":""},
  {"simpleJp":"呼び止める","jpGuide1":"呼び止める → バッドエンド9","jpGuide2":"呼び止める → BAD END 9","enGuide":"","badEndPath":"バッドエンド9"},
  {"simpleJp":"セーブ9にロード","jpGuide1":"セーブ9にロード","jpGuide2":"LOAD SAVE9","enGuide":"","isLoad":true},
  {"simpleJp":"通り過ぎる","jpGuide1":"・通り過ぎる","jpGuide2":"通り過ぎる","enGuide":""}
]
```

If this route begins by loading a save created in an earlier route, write the visible load instruction as a **plain step with no `isLoad` field**.

### Bad-end completeness

Every bad end documented by the Japanese verification sets must be actively played before continuing the main route.

For every documented bad end:

1. Save at the documented point when a source provides one.
2. Add the first wrong choice and set `badEndPath` to the **exact documented bad-end label**.
3. Include every documented step needed to reach the bad-end terminal.
4. Add the matching `isLoad: true` step immediately after the terminal.
5. Continue with the good/main choice.

If multiple bad ends branch from the same save, include **all** of them before continuing.

Never add `badEndPath` when no Japanese source documents a bad end, and never invent a bad-end label or terminal.

### Completion

- Cover the complete route from entry to ending.
- Include all required choices.
- Include every documented bad-end detour completely.
- Stop at this route's ending.
- Output only valid JSON to `$ROUTE_FILE`.

Generate route `$ROUTE_ID` only, then stop.
