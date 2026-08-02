# VN Guide Review Workflow

A guide is not complete when generated. Completion requires independent review and approval.

---

## Lifecycle

```
Author generates guide
        ↓
reviews/<slug>.json → status: "pending_review"
        ↓
Reviewer checks guide against sources
        ↓
   Issues? ──no──→ reviews/<slug>.json → status: "approved"
                           ↓
                   gh issue list --label route-accuracy,<slug> --state open
                   (must return zero results)
                           ↓
                   games.json → has_guide: true
                           ↓
                         Deploy
     ↓ yes
Reviewer creates one GitHub issue per problem
  --label route-accuracy --label <slug>
reviews/<slug>.json → status: "changes_requested", open_issues: [<numbers>]
        ↓
Author reads each issue (gh issue view <number>)
Author applies fix, closes issue (gh issue close <number>)
        ↓
All open issues closed?
  ──no──→ keep fixing
  ──yes──→ reviews/<slug>.json → status: "pending_review", round: N+1
        ↓
Reviewer re-checks closed issues against sources
  Wrong fix? → re-open issue with comment explaining what's still wrong
  All correct? → reviews/<slug>.json → status: "approved"
        ↓
      (loop back if re-opened)
```

---

## Deploy gate (hard enforcement)

Before setting `has_guide: true` in `games.json`, both conditions must hold:

```bash
# 1. No open accuracy issues
gh issue list --label "route-accuracy" --label "<slug>" --state open
# must return: no results

# 2. Review file approved
cat reviews/<slug>.json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['status']=='approved'"
```

Neither the author nor any script may bypass this gate.

---

## Running the author workflow

```bash
# Generate a new guide
claude --agent guide-author -p "Generate the guide for <Game Title> (VNDB: v1234)"

# Apply corrections from open reviewer issues
claude --agent guide-author -p "Apply all open reviewer issues for <slug>"
```

The author agent reads `prompt.md` for all source and formatting rules.

---

## Running the reviewer workflow

```bash
# Full review of a newly generated guide
claude --agent guide-reviewer -p "Review the guide for <slug>"

# Re-review after author corrections
claude --agent guide-reviewer -p "Re-review <slug>, round <N>"
```

The reviewer agent:
1. Reads `<slug>/research.json` to find source URLs
2. Fetches both primary Japanese sources directly
3. Checks `<slug>/guide.json` and all `<slug>/route_*.json` files
4. Creates one GitHub issue per finding
5. Updates `reviews/<slug>.json`

---

## Review state file

Every game has `reviews/<slug>.json`. Keep it in sync with GitHub issue state.

```json
{
  "game": "<slug>",
  "guide_path": "<slug>/guide.json",
  "status": "pending_review",
  "round": 1,
  "open_issues": [],
  "resolved_issues": [],
  "updated_at": "<ISO timestamp>"
}
```

Valid `status` values:
- `"pending_review"` — author finished, awaiting reviewer
- `"changes_requested"` — reviewer found issues, awaiting author fixes
- `"approved"` — reviewer passed, no open issues, guide may be deployed

**Only the reviewer sets `"approved"`.** The author never writes `"approved"` to this field.

---

## GitHub issue conventions

- Labels: always `route-accuracy` + the game slug (e.g. `hakuouki-shinsengumi-kitan`)
- Title: `[<slug>] <Route>: <brief description>`
- Body: Current / Expected / Sources / Required action sections
- One issue per distinct problem — do not bundle multiple problems into one issue
- The reviewer closes issues only when a fix is verified correct
- The author closes issues after applying each fix

Searching all open accuracy issues across all games:
```bash
gh issue list --label "route-accuracy" --state open
```
