$PROMPT_MD
$GAME_NOTES

---

## Current Task: Generate One Route

Game: $TITLE (key / VNDB when applicable: $VNDB_ID)
Section: **$ROUTE_TITLE** (id: `$ROUTE_ID`)
Save slot offset: **$SAVE_OFFSET** (first new save in this route = セーブ$SAVE_OFFSET_PLUS1)

Research file: `$RESEARCH_FILE`
Output file: `$ROUTE_FILE`

### Instructions

Treat this as a normal VN unless $GAME_NOTES explicitly identifies it as a **NON-VN LINEAR WALKTHROUGH**. That opt-in is game-specific and must not alter ordinary VN generation.

For an opted-in linear game walkthrough, this "route" is simply the next sequential walkthrough section. Follow the game-specific rules in the canonical standards: keep the existing route-file schema, allow concise Japanese action instructions for non-choice gameplay, preserve exact in-game text for literal choices/menu labels, and place optional content only where research says it belongs in the one master order.

1. Read `$RESEARCH_FILE`.
2. Read and preserve the exact `guide_target` from research. Do not reinterpret the VNDB work ID as the target release.
3. Confirm Japanese verification Set A and Set B both satisfy the canonical research gate for this route **and the exact guide target release**. If not, stop without generating route content.
4. Fetch the relevant components of both sets directly.
5. Reconcile every route-defining choice, prerequisite/unlock, ending, and documented save before writing.
   - When sources show different literal choices within the same event, first determine whether they are different decision points in one sequence; if so, preserve both in order instead of treating them as contradictory.
6. If the game supplement contains an explicit owner-approved title-scoped exception, apply it only to the enumerated facts and keep omission placeholders/source roles honest exactly as the supplement requires.
7. Write the complete route as a JSON array to `$ROUTE_FILE`.


### Step format

```json
[
  {
    "simpleJp": "戦う",
    "jpGuide1": "verbatim text from Set A",
    "jpGuide2": "verbatim text from Set B, or an allowed omission placeholder",
    "enGuide": "English reference/hint when available, otherwise empty string"
  }
]
```

### `simpleJp`

For a normal VN, every player action is the exact in-game choice text, with no added suffix or location prefix, and save/load instructions are the only non-choice steps.

For an explicitly opted-in non-VN linear walkthrough only, follow the game-walkthrough `simpleJp` exception in the canonical standards: literal choices/menu labels remain exact, while navigation, battle, talk, pickup, preparation, and similar non-choice actions may use concise author-written Japanese instructions.

### Source fields

Both `jpGuide1` and `jpGuide2` must be non-empty on every step.

- Use exact verbatim source text when that set prints the step.
- Main-route-defining choices, prerequisites/unlocks, and route/main endings must be independently supported by **both** sets. If one set cannot support such a fact, stop and repair the research/source gate.
- For a non-route-defining save/load/repeated UI action **or optional non-main-ending-only step** documented by only one primary set while the other is silent/non-contradictory:
  - Set A missing → `jpGuide1` is exactly `（第一ガイドに記載なし）`.
  - Set B missing → `jpGuide2` is exactly `（第二ガイドに記載なし）`.
- Never use an omission placeholder to hide missing independent support for a main-route-defining fact.
- One-source optional non-main endings (bad, normal, alternate, or similarly labeled) are allowed when the other primary set is silent/non-contradictory; if the other set contradicts that ending, stop and reconcile the conflict before generating it.
- Never copy one source into the other source field.
- Never leave either field empty.
- Preserve whitespace and punctuation exactly.

### `enGuide`

- Preserve a useful English reference/hint when an English source or reliable reference is available.
- Otherwise use exactly `""`.
- Do not erase useful existing English detail merely because this field is optional.

### Saves

- Include a save only when at least one primary set explicitly documents it.
- If only one set documents the save, that is allowed; mark the other source field as not documented rather than inventing text.
- When sources disagree on save position, use the earlier documented position.
- Save slots are sequential across routes in recommended play order.
- Insert a standalone save step immediately before the action it protects.

### Ending-detour returns vs ordinary route-entry loads

`isLoad: true` has one meaning only: it terminates a save-backed `badEndPath` non-main-ending detour and returns to the main route.

For a source-documented replay-from-beginning ending with no usable checkpoint, include the complete failed playthrough through its explicit ending terminal, then immediately repeat the route's normal opening sequence. Do not invent a save or add another structural marker.

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

### Non-main ending detour completeness

Every documented non-main ending—bad, normal, alternate, or similarly labeled—explicitly documented by either primary Japanese verification set must be actively played before continuing the main route when the other set is silent or agrees. One-source detours use the appropriate omission placeholder on detour-only steps. Contradictory ending evidence must be reconciled before generation.

For every documented non-main ending detour:

1. Save at the documented point when a source provides one.
2. Add the first branch choice and set `badEndPath` to the **exact documented ending label**.
3. Include every documented step needed to reach the ending terminal.
4. For a save-backed detour, immediately add the matching `isLoad: true` step after the terminal, then continue with the good/main choice.
5. For a replay-from-beginning ending with no usable checkpoint, include the full failed playthrough from route entry, mark the first wrong choice with `badEndPath`, end at the explicit ending terminal, then immediately replay the route from its normal opening sequence on the good/main path.

If multiple non-main endings branch from the same save, include **all** of them before continuing.

Never add `badEndPath` when no Japanese source documents a non-main ending, and never invent an ending label or terminal.

### Completion

- Cover the complete guide section from entry to its intended documented terminal/outcome. This may be a heroine ending, chapter ending, true ending, post-clear completion result, or another source-documented terminal appropriate to the section.
- Include all required choices.
- Include every documented non-main ending detour completely.
- Stop at this section's intended documented terminal/outcome.
- If that terminal ends a playthrough and later guide content belongs to another clear/NG+/replay, the next section must explicitly establish that fresh run before later gameplay continues unless a source-backed load already does so.
- Output only valid JSON to `$ROUTE_FILE`.

Generate route `$ROUTE_ID` only, then stop.
