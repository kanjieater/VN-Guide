# VN Guide — Claude Code Instructions

## Quality gate: guides require independent review before completion

A generated guide is **not complete**. Completion requires:

1. Author generates or corrects the guide
2. Structural reviewer independently checks route flow and bad-end chain integrity
3. Accuracy reviewer independently checks all choices against both Japanese sources
4. All issues from both reviewers are resolved (GitHub issues closed)
5. The accuracy reviewer sets `reviewed: true` once both reviews pass

**Never:**
- Set `reviewed: true` before both the structural (`route-structure`) and accuracy (`route-accuracy`) issues are closed
- Self-approve a guide you just generated or corrected
- Skip review because the changes are small
- Create duplicate GitHub issues for a route that already has an open issue of that type

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

The gate before `reviewed: true` is: no open GitHub issues labeled `route-structure` + `<slug>` AND no open issues labeled `route-accuracy` + `<slug>` for that route.

Valid lifecycle:
```
guide_gen.py generates route        →  reviewed: false
        ↓
Structural reviewer runs            →  creates route-structure issue if chain defects found
        ↓ (if issues)
Author runs (fresh session)         →  fixes structural findings, closes issue
        ↓
Structural reviewer re-runs         →  confirms fixes or comments if still wrong
        ↓ (structural issue closed)
Accuracy reviewer runs              →  creates route-accuracy issue if source mismatches found
        ↓ (if issues)
Author runs (fresh session)         →  fixes accuracy findings, closes issue
        ↓
Accuracy reviewer re-runs           →  confirms fixes or comments if still wrong
        ↓ (both issues closed)
Accuracy reviewer sets reviewed: true  →  deploy
```

The accuracy reviewer sets `reviewed: true` only after confirming both the structural and accuracy issues are closed. Neither the author nor the structural reviewer sets this field.

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
