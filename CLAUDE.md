# VN Guide — Claude Code Instructions

## Quality gate: guides require independent review before completion

A generated guide is **not complete**. Completion requires:

1. Author generates or corrects the guide
2. Reviewer independently checks the guide against both Japanese sources
3. All reviewer issues are resolved (GitHub issue closed)
4. `review.py` sets `reviewed: true` on the route in `guide.json`

**Never:**
- Set `reviewed: true` in `guide.json` manually — only `review.py` sets this
- Self-approve a guide you just generated or corrected
- Skip review because the changes are small
- Create duplicate GitHub issues for a route that already has an open issue

---

## Roles

**Guide Author** (`.claude/agents/guide-author.md`)
— generates and corrects guides; leaves review to the reviewer.

**Accuracy Reviewer** (`.claude/agents/guide-reviewer.md`)
— independently verifies guides against Japanese sources; does not edit guides.

Use the appropriate agent for each task. Do not mix roles in a single session.

---

## Review state

Review state is tracked per route as `"reviewed": bool` inside `<slug>/guide.json`.

- `"reviewed": false` — generated but not yet confirmed; shows "unverified" badge in UI
- `"reviewed": true` — reviewer passed with no open GitHub issues; badge removed

The gate before `reviewed: true` is: no open GitHub issues labeled `route-accuracy` + `<slug>` for that route.

Valid lifecycle:
```
guide_gen.py generates route  →  reviewed: false
        ↓
Reviewer runs (fresh session)  →  creates one GitHub issue if problems found
        ↓ (if issues)
Author runs (fresh session)    →  fixes all findings, closes the issue
        ↓
Reviewer re-runs               →  confirms fixes or comments if still wrong
        ↓ (when issue closed)
review.py sets reviewed: true  →  deploy
```

Only `review.py` may set `reviewed: true`. Neither the author nor reviewer sets this directly.

---

## Workflow reference

See `.claude/workflows/guide-review.md` for manual command examples and the full lifecycle.

---

## Guide generation rules

Core rules live in `prompt.md`. Read it before every guide session.

Key points:
- Two complete Japanese walkthroughs required before writing
- Cross-validate every choice and save point
- No invented content — document uncertainty instead
- Bad end paths must be complete and correctly tagged
- Save numbering is cross-route sequential
