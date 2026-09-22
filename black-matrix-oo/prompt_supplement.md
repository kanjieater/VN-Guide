# BLACK/MATRIX OO — game-specific guide supplement

**NON-VN LINEAR WALKTHROUGH**

This title is an ordinary SRPG, not a visual novel. Apply the explicitly scoped non-VN linear-walkthrough rules in `.claude/guide-standards.md`. Do not change the repository schema.

## Structure

- Keep using `guide.json.routes` and `route_<id>.json`.
- Treat each stored "route" as the next sequential walkthrough section.
- Build one master order from the beginning of the game through 100% cleanup. The player must never need to leave one section, jump to another branch, and later return.
- Prefer chapter-sized sections, but split a chapter at an optional-content timing window when needed so the optional block can sit exactly where it is playable. Mark optional section titles with `【任意】`.
- Never make one optional route span mandatory story progression. If skipping the optional route would also skip required story steps, split the surrounding mandatory chapter section more finely.
- Group multiple optional events into one `【任意】` section when they share the same timing window; do not create separate routes merely to mirror tiny source entries.
- Multiple playthroughs are still one linear guide: first clear → NG+ / ending cleanup → final completion.

## Step writing

- `simpleJp` is the concise Japanese instruction the player should do next.
- Preserve literal in-game choice/menu text exactly when one exists.
- For travel, talking, battles, preparation, pickups, and similar gameplay, concise author-written Japanese instructions are allowed.
- Do not add `stepType` or any new route/guide fields.

## Completion target

The intended finished guide should cover, when source-verified:

- the complete mandatory story/battle sequence;
- all 14 bonus scenarios and their correct timing;
- ending-affecting choices and prerequisites;
- all endings / NG+ requirements needed for practical scenario completion;
- important missable or one-time content that a 100% player would reasonably expect.

Do not turn repeatable grinding, max-stat optimization, or arbitrary farming into mandatory steps unless a verified completion requirement depends on it.

## Source discipline

The normal two-independent-Japanese-source gate still applies. Non-Japanese walkthroughs may be useful supplementary research but do not satisfy either primary Japanese verification set. Do not generate route files while `research.json` documents an unresolved primary-source blocker.
