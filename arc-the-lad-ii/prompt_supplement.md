# Arc the Lad II — game-specific guide supplement

**NON-VN LINEAR WALKTHROUGH**

This title is an ordinary strategy RPG, not a visual novel. Apply the explicitly scoped non-VN linear-walkthrough rules in `.claude/guide-standards.md`. Do not change the repository schema.

## Authoritative target

The guide target is the **Japanese PlayStation Classic built-in release (2018)**. Sony's Japanese PlayStation Blog explicitly lists both `アークザラッド` and `アークザラッドⅡ` among the domestic PlayStation Classic titles. This release runs the original PlayStation game content and retains Arc I → Arc II conversion support through shared virtual memory-card data.

The guide must remain fully usable from a non-converted Arc II start. Conversion-only events are optional sections and must be labeled `【任意・コンバート】`; do not make a converted Arc I clear mandatory for ordinary story completion.

## Structure

- Keep using `guide.json.routes` and `route_<id>.json`.
- Treat each stored "route" as the next sequential walkthrough section.
- Build one master order from a new Arc II game through the ending and all practical source-verified completion content.
- Split mandatory story progression at important optional-content windows, especially when a guild job, wanted monster, one-time item, optional recruit, or conversion event can expire or become inaccessible.
- Group optional work that shares the same safe timing window instead of creating one route per tiny quest.
- Mark ordinary optional blocks with `【任意】` and conversion-only blocks with `【任意・コンバート】`.
- `prerequisites` records only real source-documented dependencies, never previous-section pointers.
- The game has one normal story ending; do not invent VN-style ending branches or NG+ structure.

## Step writing

- `simpleJp` is the concise Japanese instruction the player should do next.
- Preserve literal in-game choice/menu text exactly when one exists.
- For travel, battles, conversations, pickups, preparation, guild jobs, bounty hunts, and similar gameplay, concise author-written Japanese is allowed.
- Keep one actionable instruction per step.
- Do not add `stepType` or any new route/guide fields.

## Practical 100% scope

The finished linear guide should cover, when supported by the research gate:

- the complete mandatory story through the Air Castle/final battle;
- every guild job, placed before its source-documented expiration window, with prerequisite chains preserved;
- every wanted monster/bounty that is materially missable or needed for practical bounty completion, and any source-documented one-time steal/drop choice that materially affects a 100% run;
- source-verified optional permanent recruits and summons available within Arc II itself;
- the Ruins Dungeon and Choko-related content, including the conversion-only continuation when a valid Arc I converted save makes it available;
- timing-critical sealed-ruin, unique-item, synthesis-material, and optional-dungeon pickups when the source documents that delaying or skipping them would permanently lose practical completion content;
- one-time or mutually exclusive reward choices, with the consequence stated before the decision.

Do **not** turn repeatable grinding, max level/stat optimization, arbitrary random drops, every generic treasure chest, every monster species capture, or inventory perfection into mandatory route steps unless a verified completion dependency specifically requires it.

## Arc I conversion

PlayStation Classic supports conversion between its built-in Arc I and Arc II titles. Treat conversion as an optional enhancement lane:

- normal Arc II story steps must not assume conversion;
- label conversion-only story scenes/rewards clearly;
- Choko's full awakening continuation below Ruins Dungeon B50 is conversion-gated and belongs in an `【任意・コンバート】` section;
- when converted data changes whether a summon is newly recruited versus already inherited, write the route so either state is understandable;
- do not prescribe Arc I preparation inside this Arc II guide beyond a concise prerequisite note. Arc I itself is a separate game.

## Monster Game / external software

`アークザラッド・モンスターゲーム with カジノゲーム` is separate software and is **not** part of the PlayStation Classic Arc II target. Do not require Monster Game transfers, prizes, duplication, casino rewards, or external-disc detours for this guide's 100% path. Such items may be mentioned only as out-of-target alternatives when useful.

## Locked research lanes

Use these source roles unless a materially stronger directly inspectable source is found:

- **Set A:** ちょこた / みどりすたいる `アークザラッド2攻略` is the detailed Japanese walkthrough lane. Its four main scenario pages plus guild-event, wanted-monster, Choko, Ruins Dungeon, sealed-ruin, and rare-item pages provide exact chronological and operational guidance.
- **Set B:** `アークザラッド２ データまとめ Wiki*` is the independent Japanese data-verification lane. Use its guild-job timing/prerequisite pages, regional/battle data, wanted-monster data, character/summon data, item data, and late-game availability notes as a composite set.
- Additional Japanese firsthand/technical sources may corroborate a fact but do not replace missing Set A/B support unless explicitly promoted in `research.json`.

There is **no owner-approved source exception for Arc the Lad II**. If a material progression fact required by the route cannot be independently supported under the normal gate, leave it out of mandatory 100% claims or stop that affected generation until research closes the gap.

## Source discipline

- Material story order, guild-job windows, prerequisites, conversion gates, irreversible choices, final lockouts, and unique/missable completion conditions require the normal two-Japanese-set support.
- Low-level non-branching execution detail may use one lane plus the standard omission placeholder.
- Never copy one source into the other source field.
- Keep quoted source fragments short and verbatim; put synthesized player advice in `enGuide`.
- When the two lanes disagree, document the discrepancy in `research.json` and use the safest source-supported timing rather than guessing.

## Final lockout

Treat entry into the Air Castle as the final practical lockout. All source-verified expiring guild work, bounties, optional recruits, conversion events, and completion cleanup that must occur beforehand should be placed before that transition.
