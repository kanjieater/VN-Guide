# Authoring Output Contracts

These are provider-neutral concrete output contracts for the **author** role. Read them together with `agents/guide-standards.md`; the standards remain canonical when a rule is more specific there.

## Phase boundary: research only

When the assigned task is the research phase:

1. Resolve and preserve the exact authoritative `guide_target`.
2. Complete the source gate and route/section plan.
3. Write `research.json` in the shape below.
4. **Stop. Do not generate route files in the same phase.**

If no applicable VN evidence tier passes (or the stricter non-VN gate fails), write the best research record, set `verification_tier: "blocked"` for a VN, explain the blocker, and stop. **Before treating one Japanese walkthrough as the last resort, record actual unsuccessful searches for both a second Japanese guide and an independent English guide.** Do not change a caller-explicit or pinned edition just to find a better guide.

### `research.json` shape

```json
{
  "title": "Game title",
  "vndb_id": "v123 or game:manual-key",
  "guide_target": {
    "label": "specific edition/release name",
    "platform": "specific platform",
    "url": "https://authoritative.example/specific-release"
  },
  "verification_tier": "dual_verified | corroborated_primary | single_primary | blocked",
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
      "notes": "Describe exact Japanese choices or narrower story/outcome corroboration"
    },
    {
      "set": "E",
      "url": "https://example.com/english-walkthrough",
      "title": "Independent English written walkthrough, if found",
      "language": "en",
      "notes": "Specific route coverage, target edition and proof it is not translated/copied from A"
    }
  ],
  "source_search": {
    "checked_at": "ISO-8601 timestamp",
    "secondary_japanese": {
      "status": "found | not_found_after_search",
      "queries": ["Japanese title + 攻略", "Japanese title + ending/route", "second Japanese archive/site query"],
      "sites_checked": ["Japanese walkthrough archive"],
      "candidates": [{"url": "https://example.jp/candidate", "assessment": "independent/derivative/inaccessible/wrong edition and what is covered"}]
    },
    "english_walkthrough": {
      "status": "found | not_found_after_search",
      "queries": ["Romanized title + walkthrough", "translated title + ending guide", "title + GameFAQs"],
      "sites_checked": ["GameFAQs", "other relevant written guide source"],
      "candidates": [{"url": "https://example.com/candidate", "assessment": "independent complete guide, derivative translation, review only, empty listing or wrong edition"}]
    }
  },
  "disagreements": "Document source conflicts, omissions, exception scope, and how they are handled",
  "generated_at": "ISO-8601 timestamp"
}
```

Contract details:

- Copy `guide_target` exactly from the accepted caller/pinned/source-supported automatic resolution. Never silently broaden or replace an explicit/pinned version, including an original versus later remake/port distinction; provenance lives in `catalog.json.guide_target_origin` (`caller_explicit`/`automatic`), and absent provenance means pinned. Only a previously documented automatic target may be re-resolved with evidence/reason recorded in research.
- Route `id` values are ASCII-only romanized keys.
- `recommended_order` contains every route/section id in canonical play order; a true/final route is last when applicable.
- For an opted-in linear walkthrough, `routes` is the one sequential walkthrough plan, with optional sections placed exactly where the player should do them.
- `prerequisites` contains only real source-documented unlock/dependency requirements, never simple previous/next sequencing.
- Label Japanese primary sources `set: "A"` or `set: "B"`, independent English written walkthroughs `set: "E"`. Mark English written reviews/nonwalkthroughs in notes as *supplementary* rather than full E corroboration. A translated/derivative English copy of A cannot qualify as independent E; preserve it as provenance with an explicit rejection reason. All source notes must state which facts are actually covered, whether directly inspectable, and target-edition applicability. Under `corroborated_primary`, B may corroborate ending meaning without quoting final UI; preserve honest missing-Japanese-field placeholders. Under `single_primary`, no second Japanese or English guide is falsely attributed.
- Record VN `verification_tier` (`dual_verified`, `corroborated_primary`, `single_primary`, `blocked`), `source_search`, independent Japanese and English guide findings, source disagreements, A-only literal omissions, conditional unlock recovery, version caveats and any owner exception provenance/scope. `source_search` is REQUIRED for any fallback below `dual_verified`, and English must also be searched even for `dual_verified` (its absence alone does not block the two-Japanese-guide tier). Preserve the schema keys and use real queries/URLs/rejection explanations, not empty boilerplate.
- Portrait and cover lookup follow the verification requirements in `agents/guide-standards.md`.

## Phase boundary: one route/section only

When assigned one route/section:

1. Read the current `research.json`.
2. Preserve its exact `guide_target`.
3. Verify the source gate for this route/section before writing.
4. Reconcile every route-defining choice, prerequisite/unlock, ending, and documented save.
5. Write the complete route array to `route_<id>.json`.
6. **Generate only the assigned route/section, then stop.**

Do not opportunistically generate later routes in the same route-generation phase unless the caller explicitly assigns them.

## Route-step JSON shape

A route file is a flat ordered JSON array. The normal step shape is:

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

The structural optional fields are:

- `badEndPath` — only on the first branch step of a documented non-main-ending detour.
- `isLoad: true` — only on the load that terminates a **save-backed** `badEndPath` detour and returns to the main route.
- `badEnd` — optional display detail when useful and source-supported.

For normal VNs, `simpleJp` is exact in-game choice/action text; save/load instructions are the only normal non-choice steps. For explicitly opted-in non-VN linear walkthroughs, follow the non-VN `simpleJp` exception in the standards.

Both `jpGuide1` and `jpGuide2` are always non-empty. Use only the canonical omission placeholders permitted by the standards, never copied/fabricated text.

## Operational save-slot context

Before generating a route, determine the next available save number from all earlier routes in `recommended_order`.

Treat that as an operational authoring input:

- existing highest slot before this route = `N`;
- first new save in this route = `セーブN+1`;
- continue sequentially throughout the route;
- never renumber earlier source-backed saves merely for convenience.

This save offset is authoring context, not a new schema field.

Include a save only when at least one primary set documents it. If sources disagree on save position, use the earlier documented position.

## Canonical save-backed detour shape

A complete detour looks like this:

```json
[
  {
    "simpleJp": "セーブ9",
    "jpGuide1": "▼SAVE9",
    "jpGuide2": "SAVE9",
    "enGuide": ""
  },
  {
    "simpleJp": "呼び止める",
    "jpGuide1": "呼び止める → バッドエンド9",
    "jpGuide2": "呼び止める → BAD END 9",
    "enGuide": "",
    "badEndPath": "バッドエンド9"
  },
  {
    "simpleJp": "セーブ9にロード",
    "jpGuide1": "セーブ9にロード",
    "jpGuide2": "LOAD SAVE9",
    "enGuide": "",
    "isLoad": true
  },
  {
    "simpleJp": "通り過ぎる",
    "jpGuide1": "・通り過ぎる",
    "jpGuide2": "通り過ぎる",
    "enGuide": ""
  }
]
```

If a route begins by loading a save from an earlier route, that visible load instruction is a plain step with **no** `isLoad`.

For a documented ending that requires replay from the beginning because no usable checkpoint exists, include the full failed playthrough through its ending terminal and then repeat the normal opening sequence. Do not invent a save or structural marker.

Every documented non-main ending must be complete through its terminal before the guide returns to or replays the main path.
