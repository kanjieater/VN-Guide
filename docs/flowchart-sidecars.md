# Flowchart sidecars

`flowchart.json` is an optional per-VN topology overlay for facts that the normal flat walkthrough intentionally cannot preserve.

The normal `guide.json` + `route_*.json` files remain authoritative for player instructions. A sidecar must not copy the entire route graph or become a second walkthrough format. Without a valid sidecar, the UI renders the generic inferred chart.

A sidecar being present does **not** by itself mean its topology has passed an accuracy review. The UI therefore describes it neutrally as a detailed/enhanced chart. Factual review still happens through the normal repository review process.

## Version 1

A sidecar has exactly `"version": 1` and may use:

- `syntheticNodes` — topology nodes absent from the optimized flat route.
- `addEdges` / `removeEdges` — relationships generic save/load inference cannot recover correctly.
- `groups` — replace serialized walkthrough steps with one semantic group, such as “all of these, in any order.”
- `routeLinks` — explicit unlock/dependency edges between route sections.

Unknown top-level fields are rejected.

References point back into the graph produced by the same runtime route inference used by the UI:

```json
{ "route": "aries", "save": "9" }
{ "route": "aries", "start": true }
{ "route": "aries", "step": { "simpleJp": "【アリエス】END" } }
{ "synthetic": "aries-smoke-rain-asuka-house" }
```

A `save` reference resolves only when that save is actually emitted as a branch node by runtime inference; merely having a raw `セーブN` route step is insufficient. A `step` reference resolves only to graph nodes that runtime inference renders. If the same `simpleJp` is rendered more than once, add a positive integer `"occurrence"`.

The repository tests execute `flowchart.js` directly under Node and build every committed sidecar with the production `buildEnhancedGraph()` path. This keeps repository validation and browser resolution semantics aligned.

## Synthetic nodes

Synthetic nodes are only for topology genuinely absent from the flat walkthrough:

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

Rules:

- `id` is required and unique across both synthetic nodes and groups.
- `kind` may be `step`, `detour`, `end`, or `branch`.
- `near` is required and controls layout.
- If `route` is supplied, it must match the resolved `near` route.
- `jumpTo` is optional. When present, both the clickable `routeId` and `stepIndex` come from that single resolved target, including for cross-route jumps.
- `rowOffset` and `laneOffset` must be finite numeric values in the supported range.

## Groups

Use a group when the walkthrough serializes actions whose actual semantics are unordered:

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

Groups require at least two concrete `step` references, all from the same route. A supplied group `route` must match that member route. The renderer replaces the serialized member chain with one grouped node and reconnects the incoming/outgoing edges.

## Edges

Each edge has `from`, `to`, optional `label`, and optional `kind`. Supported kinds are `normal`, `detour`, and `unlock`. Entries in `routeLinks` use `unlock`.

A `removeEdges` entry must identify an edge that actually exists after route inference and grouping. Removing a nonexistent edge rejects the whole sidecar instead of silently doing nothing.

## Failure behavior

Sidecars are enhancement-only. The complete v1 shape is validated before use: supported fields and kinds, reference shapes, route membership, occurrences, numeric offsets, unique IDs, group relationships, navigation targets, and edge operations.

If the file is missing, malformed, uses an unsupported version, fails schema validation, references graph nodes that do not exist, or requests an impossible transformation, the renderer rejects the sidecar as a whole and falls back to the generic inferred chart.
