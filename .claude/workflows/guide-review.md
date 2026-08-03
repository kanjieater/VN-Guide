# VN Guide Review Workflow

A generated guide is immediately live but marked unreviewed. Review is an ongoing process that runs in the background and marks routes as `reviewed: true` in `guide.json` when they pass.

---

## Lifecycle

```
Author generates guide
        ↓
guide_gen.py sets has_guide: true → guide is live (routes: reviewed: false)
        ↓
review.py iterates over each unreviewed route (one at a time)
        ↓
   Check for existing open GitHub issue for this route
     ↓ none                           ↓ exists (pre-existing or from prior round)
   Reviewer session                   skip reviewer → go to Author session
   (fresh claude, no shared context)
   reads research.json + route_*.json for this route
        ↓
   Issues? ──no──→ review.py marks route reviewed: true → deploy → next route
     ↓ yes
   Reviewer creates ONE GitHub issue for this route (all findings in body)
     --label route-accuracy --label <slug>
        ↓
   Author session (fresh claude, no shared context with reviewer)
   reads open issue → applies all fixes → closes issue
        ↓
   Reviewer re-review session
   verifies fixes → closes issue if resolved, comments if not
        ↓
   Issue closed? ──yes──→ reviewed: true → deploy → next route
     ↓ no
   (repeat up to MAX_REVIEW_ROUNDS)
```

Author and reviewer always run as separate `claude` invocations with no shared session.
`review.py` manages the loop — do not chain author and reviewer manually within one session.

---

## Reviewed status in the UI

Routes in `guide.json` carry a `reviewed` boolean:
- `"reviewed": false` — generated but not yet confirmed against sources; shows "unverified" badge in UI
- `"reviewed": true` — reviewer passed with no open issues; badge removed

Routes are always publicly accessible regardless of `reviewed` status.

---

## Deploy gate

The only gate before marking `reviewed: true` is:

```bash
gh issue list --label "route-accuracy" --label "<slug>" --state open
# must return: no results
```

`review.py` checks this automatically. Neither the author agent nor any script may set `reviewed: true` until this check passes.

---

## Running the author workflow manually

```bash
# Generate a new guide (separate session from reviewer)
claude -p "Read .claude/agents/guide-author.md and follow those instructions. Generate the guide for <Game Title> (VNDB: v1234)."

# Apply corrections from open reviewer issues (separate session from reviewer)
claude -p "Read .claude/agents/guide-author.md and follow those instructions. Fix all open GitHub issues labeled route-accuracy and <slug>."
```

---

## Running the reviewer workflow manually

```bash
# Full review of a newly generated guide (separate session from author)
claude -p "Read .claude/agents/guide-reviewer.md and follow those instructions exactly. Review the guide for <slug>."

# Re-review after author corrections (separate session from author)
claude -p "Read .claude/agents/guide-reviewer.md and follow those instructions exactly. Re-review <slug> after author corrections."
```

---

## Running the automated loop

```bash
# From inside the container or locally with REPO_PATH set:
python3 scripts/review.py
```

The loop processes all games with `has_guide: true` that have any `reviewed: false` routes. Each route gets its own reviewer and author sessions — routes are never batched into one session.

To scope to one game or one route (useful for testing):
```bash
GUIDE_PRIORITY_VID=v1715 python3 scripts/review.py           # one game only
GUIDE_PRIORITY_VID=v1715 GUIDE_REVIEW_ROUTE=okita python3 scripts/review.py  # one route
```

These env vars can also be set in `compose.yml` to scope the container's review loop.

---

## GitHub issue conventions

- Labels: always `route-accuracy` + the game slug (e.g. `hakuouki-shinsengumi-kitan`)
- Title: `[<slug>] <Route>: accuracy review`
- Body: Status + Summary + numbered findings (each with File / Section / Problem / Current / Expected / Sources / Required action)
- **One issue per route** — all findings for that route go in a single issue body
- The reviewer adds a comment when any finding is not yet resolved after author corrections
- The reviewer closes the issue only after all findings are resolved
- `review.py` marks routes reviewed after the issue is closed

Searching all open accuracy issues across all games:
```bash
gh issue list --label "route-accuracy" --state open
```
