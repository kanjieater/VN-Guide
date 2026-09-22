$PROMPT_MD
$GAME_NOTES

---

## Current Task: Research Phase

Game: $TITLE
Game key / VNDB work ID when applicable: $VNDB_ID
Authoritative guide target: $GUIDE_TARGET_JSON

Complete **only the research phase**.

Treat this as a normal VN unless $GAME_NOTES explicitly identifies it as a **NON-VN LINEAR WALKTHROUGH**. That opt-in is game-specific; do not apply chapter/area/optional-section semantics to ordinary VNs.

For an opted-in linear game walkthrough, keep the existing schema unchanged: plan one ordered `routes` list whose entries are sequential walkthrough sections. Put optional-content sections at their exact place in the master play order and mark them clearly in the title. The player must not need to bounce between sections.

Do not generate route content until the two-independent-Japanese-verification-set gate in the canonical standards is satisfied.

Write the result to:
`$RESEARCH_FILE`

Use this JSON shape:

```json
{
  "title": "$TITLE",
  "vndb_id": "$VNDB_ID",
  "guide_target": $GUIDE_TARGET_JSON,
  "routes": [
    {
      "id": "ascii_route_key",
      "title": "ルート名（日本語）",
      "portrait": "<verified character image URL or empty string>",
      "prerequisites": [],
      "is_true_ending": false,
      "notes": ""
    }
  ],
  "recommended_order": ["route_key_1", "route_key_2"],
  "sources": [
    {
      "set": "A",
      "url": "https://example.com/guide",
      "title": "Source title",
      "language": "ja",
      "notes": "What this component covers and whether it is directly inspectable"
    },
    {
      "set": "B",
      "url": "https://example.jp/guide",
      "title": "Independent Japanese source",
      "language": "ja",
      "notes": "What this component covers and whether additional B components are needed"
    }
  ],
  "disagreements": "Document source conflicts, omissions, and how they are handled",
  "generated_at": "$DATE"
}
```

Rules:

- `guide_target` is the authoritative resolved target from the repository, caller, or pre-research newest-Japanese-release default. Copy it **exactly**; do not broaden or replace it during research.
- Its `url` must link to the specific intended release/edition when possible (prefer a VNDB `r...` release page rather than the broader `v...` work page when VNDB has the exact release).
- Verify every Set A/B component applies to that exact target release. Document port/remaster/edition differences and whether they affect routes, choices, saves, unlocks, or endings.
- If the supplied target cannot be verified or the sources only apply to a materially different release, stop and document the blocker rather than silently switching targets.
- `id` must be ASCII-only romanized keys.
- `recommended_order` lists route ids from first to last; true/final route last when applicable. For an explicitly opted-in linear game walkthrough, it is the single canonical section order from start through completion/cleanup.
- Label every primary source component with `set: "A"` or `set: "B"`.
- A set may contain multiple Japanese pages, but together it must cover the complete route/ending structure required by the canonical standards.
- Do not count translations, derivatives, or inaccessible pages toward the two-set gate.
- Include useful supplemental/provenance sources too, but identify them clearly in `notes`; they do not replace A/B.
- Explicitly document what each source component does and does not cover.
- If the A/B gate cannot be satisfied, write the best research file you can, explain the blocker in `disagreements`, and stop. Do not generate routes.
- For `portrait`, match the route character by name and use a **directly verified image URL** from the source record. When using VNDB, fetch the character's returned `image.url` (or equivalent explicit image field) exactly. **Never synthesize a VNDB image URL from the character ID**; VNDB character IDs and image IDs are separate identifiers. If VNDB cannot be inspected in the current environment, use another directly inspectable authoritative/structured character source and document it in `research.json`. Leave blank only when no verified route-character image can be obtained.

Write the file, then stop.
