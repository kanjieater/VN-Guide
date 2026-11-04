# 機神飛翔デモンベイン — game-specific guide supplement

**NON-VN LINEAR WALKTHROUGH**

This 2006 PC release combines a choice-free novel with mandatory 3D action battles. Use the existing linear-walkthrough semantics for player-action instructions. This is an **ending-completion-only** guide (three reachable endings), not a combat strategy walkthrough or a fabricated branching heroine VN.

- One recommended order: first clear → optional Dr. West ending → final TRUE ending. The two post-clear endings each independently require a normal first clear; West is **not** an unlock prerequisite for TRUE.
- The BATTLE:02 Destroyer Robot vs Demonbane Blood victory ends that playthrough early; to reach TRUE, **do not win** it on the later replay.
- At the final boss, the hidden command must be entered during the finishing-move input window after a normal first clear. Preserve both the independently reported directional action and the optional keyboard remapping tip, with the narrow owner-approved source exception below; Set A supports the hidden-command mechanism/timing, while independent contemporary written accounts support the literal inputs but their original pages cannot currently all be retrieved.
- No documented reusable save position was found in the Japanese sources. Do not invent numbered save/load steps or assume a replay-select feature. Each later route explicitly starts a new run.
- Do not misapply guides for 斬魔大聖デモンベイン or 機神咆吼デモンベイン; those are different games with heroine routes.
- Set A / composite Set B source roles and target edition are recorded in research.json. The title-specific source-evidence exception below is approved; no broader source-gate relaxation is granted.

## Owner-approved source-evidence exception — 2026-11-04

**Approval and provenance:** On 2026-11-04, following the posted accuracy findings and correction report, the repository owner explicitly instructed: “alright go ahead and approve and merge then” for PR #108. This instruction is recorded in [the PR's owner-approval provenance comment](https://github.com/kanjieater/VN-Guide/pull/108#issuecomment-6635414789). The author did not grant the exception.

**Exact scope:** Original 2006 Japanese Windows PC `機神飛翔デモンベイン 通常版` only, `route_true.json` **step 3** only: waive the unavailable *second directly inspectable independent Japanese passage that spells out the four literal TRUE END inputs* `上→下→上→攻`. Do not extend this to the TRUE END unlock, timing, fight outcome, other routes or choices, or other games. This authorization approves use of a corroborated command, not a finding that inaccessible pages were inspected.

**Recovered evidence and field roles:**

- Set A: https://nayutam.exblog.jp/3738908/ (directly inspectable Japanese guide); independently verifies TRUE END divergence during the finishing-move command-input window and says the first Normal END reveals the command. Its `jpGuide1` remains its verbatim generic explanation, **not** a fabricated quote of the literal inputs.
- Set B: https://blog.livedoor.jp/shibachi1/archives/50598379.html (independent contemporary Japanese first-hand account with indexed text); describes rebinding `上→S`, `下→D`, `攻→A` and successfully entering `SDSA`. The original direct page times out. Its existing `jpGuide2` preserves the recovered original Japanese text; do not assert the page is currently directly retrievable.
- Corroborating *unverified-access provenance*, not additional inspected primary lanes: https://qposo.blog.fc2.com/blog-entry-124.html (indexed `↑↓↑攻` on Normal END screen) and https://trinityabsolute.blog24.fc2.com/blog-entry-94.html (indexed `上下上攻` for final battle). Their FC2 originals redirect-loop; do not portray them as directly inspected. Their indexed account corroborates the action but does not automatically satisfy the default two-lane gate.

Only the exact missing direct-access/literal-quotation verification for this one step is waived. Keep the current `simpleJp` command and player-facing `enGuide`, without hallucinating source text, saves, or choices. All other material facts follow normal A/B requirements.

**Review/merge provenance:** The same 2026-11-04 owner instruction explicitly requested approval and merging. Any publishing of `reviewed: true` as part of that request is recorded as **manual owner direction**, not as independently performed structural/accuracy PASS reviews. This case-specific manual override does not alter the repository's general independent-review policy.
