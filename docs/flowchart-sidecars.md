# Flowchart sidecars

`flowchart.json` is an optional per-VN topology overlay for facts that the normal flat walkthrough intentionally cannot preserve.

The normal `guide.json` + `route_*.json` files remain authoritative for player instructions. A sidecar must not copy the entire route graph or become a second walkthrough format. Without a valid sidecar, the UI continues to render the generic inferred chart.

## Version 1

A sidecar has `"version": 1` and may contain four kinds of corrections:

- `syntheticNodes` — a documented choice/result that is missing from the optimized flat route.
- `addEdges` / `removeEdges` — correct relationships that generic save/load inference cannot recover.
- `groups` — collapse ordered walkthrough steps into a semantic group such as “all of these, in any order.”
- `routeLinks` — explicit unlock/dependency edges between route sections.

References point back into existing route data instead of duplicating it:

```json
{ "route": "aries", "save": "9" }
{ "route": "aries", "start": true }
{ "route": "aries", "step": { "simpleJp": "【アリエス】END" } }
{ "synthetic": "aries-smoke-rain-asuka-house" }
```

If the same `simpleJp` appears more than once, add `"occurrence": 2` (or higher). Sidecar references are validated against the current route files by the unit tests.

## Synthetic nodes

Synthetic nodes are only for source-verified topology that is genuinely absent from the flat walkthrough:

```json
{
  "id": "alternate-choice",
  "route": "route-id",
  "kind": "step",
  "label": "missing in-game choice text",
  "near": { "route": "route-id", "step": { "simpleJp": "existing choice" } },
  "laneOffset": 1,
  "rowOffset": 0,
  "jumpTo": { "route": "route-id", "save": "3" }
}
```

`near` is a layout anchor. `jumpTo` is optional; when present, tapping the synthetic node opens the closest actionable point in the normal guide.

## Groups

Use a group when the walkthrough serializes actions whose true game semantics are unordered:

```json
{
  "id": "late-visits",
  "route": "route-id",
  "label": "3か所すべて（順不同）",
  "members": [
    { "route": "route-id", "step": { "simpleJp": "場所A" } },
    { "route": "route-id", "step": { "simpleJp": "場所B" } },
    { "route": "route-id", "step": { "simpleJp": "場所C" } }
  ]
}
```

The renderer replaces the serialized member chain with one grouped node and reconnects the incoming/outgoing graph edges.

## Failure behavior

Sidecars are enhancement-only. If the file is missing, malformed, uses an unsupported version, or any required reference cannot be resolved, the renderer falls back to the generic inferred chart rather than presenting stale topology as verified.
