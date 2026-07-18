$PROMPT_MD

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
- `portrait`: fetch `https://vndb.org/v$VNDB_ID/chars` to find the character for each route. VNDB character image URLs follow the pattern `https://t.vndb.org/ch/{last2ofID}/{fullID}.jpg` — e.g. character ID 43681 → `https://t.vndb.org/ch/81/43681.jpg`. Match each route to its character by name. Leave empty string if no match found.

Write the file, then stop.
