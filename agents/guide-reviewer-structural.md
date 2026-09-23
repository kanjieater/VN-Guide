# Structural Reviewer

Read `agents/guide-standards.md` first. Work in a fresh context separate from the author and accuracy reviewer. If the current game directory contains `prompt_supplement.md`, read it; apply non-VN linear-walkthrough semantics only when it explicitly says **NON-VN LINEAR WALKTHROUGH**.

Use whatever repository/file/issue capabilities are available. Do not fetch Japanese walkthroughs and do not edit guide content.

If the caller/orchestrator explicitly specifies a review transport (for example, create/use a `route-structure` issue), follow that transport exactly. Only default to PR-first when no transport is specified.

## Route semantics

Each `route_<id>.json` is a flat guide-section step array.

- `badEndPath` marks the first branch step of a documented non-main ending detour (bad, normal, alternate, or similarly labeled).
- `isLoad: true` terminates a save-backed detour and returns to the main route.
- A replay-from-beginning detour with no usable documented checkpoint ends at its explicit ending terminal; the following repeated opening sequence is the fresh replay boundary. No second structural-return field is used.
- `isLoad: true` must never be used for an ordinary cross-route save load.
- An ordinary route-entry instruction such as `セーブ3にロード` is structurally a plain step unless it terminates a preceding `badEndPath`.

## Structural review

Trace the entire section.

For every non-main-ending chain verify:

- exactly one non-empty `badEndPath` start;
- zero or more intermediate plain steps are allowed (an immediate-terminal bad end may load immediately);
- a save-backed detour has exactly one terminating `isLoad: true`, and that load references a save created earlier in the same route;
- a replay-from-beginning prefix has an explicit ending terminal, is followed immediately by the route's normal opening sequence again, and has no invented save/load terminator;
- no nested/unpaired bad-end start exists;
- the named bad end is represented at the terminal step or is unambiguously identifiable from the chain context.

Reconstruct the main route by removing save-backed non-main-ending chains from `badEndPath` through their terminating `isLoad`. For a replay-from-beginning non-main ending with no usable checkpoint, remove the entire failed-play prefix from route step 0 through its explicit ending terminal; the residual route must begin with the repeated normal opening sequence that follows. The remaining route must:

- begin at step 0;
- end at the intended documented terminal/outcome for that section (for example a heroine ending, chapter ending, true ending, or post-clear completion result);
- contain no `isLoad: true`;
- contain no orphaned structural load.

Ordinary cross-route load instructions may remain on the main route as plain steps.

For an explicitly opted-in **NON-VN LINEAR WALKTHROUGH**, also trace continuity across adjacent sections and across playthrough terminals. If an ending/clear terminal is followed by gameplay from another clear, NG+, or replay, require an explicit fresh-run boundary (or a source-backed load already present in the route). Do not pass an ending → later-gameplay jump merely because the individual route files are each internally linear.

## Review record

Follow caller/orchestrator transport instructions first. If none are specified, follow the review destination defaults in `agents/guide-standards.md`. Use the canonical finding schema for every structural finding.

### Open PR exists and no caller transport was specified

Use the existing PR for this section's structural feedback instead of creating a route issue.

- Clean first pass → leave a concise PASS comment identifying the route and structural review, including `Route blob: <current route-file blob SHA/content hash>`.
- Findings → leave one CHANGES REQUESTED comment containing all structural findings and required actions for the route.

Before posting, inspect existing feedback for the same route/type. Do not run concurrently with another structural reviewer on the same route.

### No open PR exists and no caller transport was specified

Use the fallback issue workflow. Create/reuse at most one `route-structure` issue for the route. A clean first pass creates no issue.

## Re-review

After author corrections, re-read and re-trace the section.

If review is on an open PR:
- still wrong → comment precisely what remains;
- clean → explicitly confirm that the previous structural findings are resolved and include `Route blob: <current route-file blob SHA/content hash>`.

If issue fallback is in use, comment/close the existing structural issue using the normal reviewer ownership rules.

The structural reviewer never sets `reviewed: true`.
