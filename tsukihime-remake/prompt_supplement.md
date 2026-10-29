# Tsukihime remake — owner-approved literal provenance scope

This is a normal VN guide for **Tsukihime -A piece of blue glass moon-**
(`v17909`), targeting the 2021 Japanese Nintendo Switch Download Edition
(`https://vndb.org/r82483`). This supplement does not change that target.

## Owner authorization

On **2026-10-28**, repository owner `kanjieater` explicitly accepted the
independently reproduced Japanese menu literals **provided the inspected assets
are attributable to the remake, not the original Tsukihime**:
https://github.com/kanjieater/VN-Guide/pull/98#issuecomment-6476454232

The owner waived exact Switch storefront/download packaging and patch-build
provenance **only for the 13 literal payloads below**. This records that
authorization, not an author-granted exception or whole-guide approval.

## Exact covered facts

Indices are zero-based in the named route arrays. Text IDs identify the
independently reproduced payloads in `menu-text-evidence.json`.

| Route file | Step | Text ID |
|---|---:|---:|
| `route_arcueid.json` | 7 | 42688 |
| `route_arcueid.json` | 21 | 42607 |
| `route_arcueid.json` | 54 | 42639 |
| `route_ciel_normal.json` | 23 | 42694 |
| `route_ciel_normal.json` | 26 | 42695 |
| `route_ciel_normal.json` | 44 | 42725 |
| `route_ciel_normal.json` | 55 | 42724 |
| `route_ciel_normal.json` | 64 | 42734 |
| `route_ciel_normal.json` | 65 | 42735 |
| `route_ciel_normal.json` | 78 | 42750 |
| `route_ciel_normal.json` | 81 | 42751 |
| `route_ciel_normal.json` | 88 | 42754 |
| `route_ciel_normal.json` | 91 | 42755 |

## Supporting evidence and remake attribution

- Independent reproduction:
  https://github.com/kanjieater/VN-Guide/pull/98#issuecomment-6461638207
  A separate reviewer rehashed both inputs, freshly compiled the verifier,
  reproduced all 13 strings with both the verifier and KDU, and checked all
  14 recorded SELR references.
- The pinned [Knife source](https://github.com/AuroraWright/knife/tree/794bcc5e14be6bd4bf44716f160a280f4306ab1d)
  identifies the engine as a reimplementation of the Switch remake,
  *Tsukihime -A piece of blue glass moon-*, supporting Japanese and overseas
  builds. Its Japanese archive selector and the extracted remake-specific
  Arcueid/Ciel scenes support attribution to that remake, not the original VN.
- `menu-text-evidence.json`, `menu-text-evidence.md`, and
  `verify-choice-text.rs` preserve the minimal payload ledger, method, hashes
  and scene references. They do not establish storefront or patch identity.

For these exact facts, use the independently reproduced remake payload as the
literal tie-breaker between differing walkthrough transcriptions. Distinguish
**allowed under the owner's provenance waiver** from **identically quoted by
both Japanese sets**. Do not reopen the waived packaging/patch demand for these
13 payloads, and do not extend the waiver beyond them.

## Requirements that remain unchanged

- Keep two independent Japanese walkthrough sets for route-defining choices,
  prerequisites, route order, ending conditions and all other normally gated
  facts. This is not a waiver of Set A/Set B coverage.
- Preserve every `jpGuide1` and `jpGuide2` quotation verbatim, including
  disagreements; the asset ledger is supplemental evidence, not a new lane.
- No other literals, steps, saved states, conditional prompts, checkpoints,
  routes or releases are covered. The extraction does not certify gameplay
  execution or route-state behavior.
- Do not claim that patch identity was established, that cartridge/download or
  2021/2024 binaries are equivalent, or that the entire guide was approved.
- Independent structural and accuracy gates, content binding, and review-state
  ownership remain in force. The author must not self-approve.
