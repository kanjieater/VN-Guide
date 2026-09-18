$PROMPT_MD
$GAME_NOTES

---

## Current Task: Research Phase

Game: $TITLE
VNDB ID: $VNDB_ID
$PLATFORM_NOTE

Complete **only the research phase** from the instructions above.

Do NOT generate any guide content yet. Your only output is the research file below.

When your research is complete, write the results to:
`$RESEARCH_FILE`

Use this exact JSON format:

```json
{
  "title": "$TITLE",
  "vndb_id": "$VNDB_ID",
  "routes": [
    {
      "id": "ascii_route_key",
      "title": "ルート名（日本語）",
      "portrait": "https://t.vndb.org/ch/NN/NNNNN.jpg",
      "prerequisites": [],
      "is_true_ending": false,
      "notes": ""
    }
  ],
  "recommended_order": ["route_key_1", "route_key_2"],
  "sources": [
    {
      "url": "https://example.com/guide",
      "title": "Source title",
      "language": "ja",
      "notes": "How complete and how this will be used"
    }
  ],
  "disagreements": "Document any conflicts between sources here",
  "generated_at": "$DATE"
}
```

Notes:
- `id` must be ASCII-only romanized keys (e.g. `takuma`, `shinji`, `true_end`)
- `recommended_order` lists route ids from first to last (true route last)
- Include all sources found, noting completeness
- `portrait`: match each route to the correct VNDB character by name, then copy that character's actual image URL from VNDB exactly (prefer the Kana API `POST /character` field `image.url`). **Do not construct a portrait URL from the character ID.** VNDB character IDs (for example `c109`) and image IDs (for example the `140` in `https://t.vndb.org/ch/40/140.jpg`) are separate identifiers. Verify the returned character name before writing the URL. Leave an empty string if no verified portrait is available.

Write the file, then stop.
