# Original Japanese choice-text reconciliation

`menu-text-evidence.json` contains only the 13 disputed menu strings extracted
read-only from the caller's installed original Japanese Switch assets, plus the
scene instructions that reference them. It is not a whole script or a game dump.
The two Japanese walkthrough evidence lanes remain verbatim in the route files.

## Method and limits

At the caller's request, the author inspected the caller's local Knife setup.
Knife is a reimplementation that reads extracted Switch game data, not a copy
of the walkthrough text. The installed assets use the Japanese build's
unprefixed archive names, rather than the overseas build's `w_` archives.
The two input-file SHA-256 hashes and sizes are recorded in the JSON.

The strings were decoded using the public
[Knife source at commit 794bcc5e14be6bd4bf44716f160a280f4306ab1d](https://github.com/AuroraWright/knife/tree/794bcc5e14be6bd4bf44716f160a280f4306ab1d):

- `ScriptText::parse(..., 0)` reads the Japanese string table.
- `SceneArchive::parse` and `vm::parse::Scene` decode the scene instructions.
- Every listed string was confirmed as a `SELR` choice argument. In one scene
  the keep-glasses choice has both disabled and enabled instruction variants;
  both refer to the same literal.
- `game/choice.rs::cmd_selr` adds the option-number prefix separately. No
  punctuation or spacing normalization was applied to the recorded payload.

The game was **not launched**. No existing save was loaded, copied, unlocked,
written, or restored. Its size, modification time, and SHA-256 were checked
unchanged privately. No save file, account information, ROM, or full script is
part of this contribution.

This is direct asset evidence from the caller's installed Japanese data, **not
a hardware screenshot**. The bundle does not preserve an independently checked
eShop receipt, `control.nacp`, or installed Switch patch version. That provenance
limit is disclosed rather than claiming a particular capture device or binary
identity across releases. No 2024 equivalence is asserted.

The original 2021 target is supported separately by the two Japanese
walkthrough sets. [Independent r3 review](https://github.com/kanjieater/VN-Guide/pull/98#issuecomment-6461638207)
rehashed both archives, freshly compiled the verifier and separately ran KDU,
reproducing all 13 payloads and 14 SELR references.

On **2026-10-28**, the [repository owner](https://github.com/kanjieater/VN-Guide/pull/98#issuecomment-6476454232)
accepted these 13 literals conditional on attribution to the remake, waiving
only exact storefront/download packaging and patch-build provenance. The
pinned Knife README explicitly identifies the Switch remake, its build selector
recognizes the Japanese archive class, and the referenced Arcueid/Ciel scenes
are remake-specific, not from the original Tsukihime. See
`prompt_supplement.md` for exact covered steps and unchanged requirements.

This is an authorized provenance limit, not proof of package/patch identity,
a waiver of two Japanese walkthrough sets, or whole-guide approval. Independent
review of the revised route/research content remains required; the author
grants no approval.

## Reproduce without starting the game

Use your **own** extracted original Japanese assets. First compare the two
input hashes with the JSON; if they differ, record the difference rather than
assuming this extraction describes that build.

With Knife checked out at the pinned commit:

```sh
cargo build --release -p kdu --locked --offline
target/release/kdu --romfs "$ROMFS" --language 0 line 42688
```

Repeat `line` for the JSON's other text IDs. This command reads only
`script_text.mrg`; it does not invoke the game or save system.

For the scene-reference check, compile the supplied `verify-choice-text.rs`
against that checkout's built `knife-core` library:

```sh
rustc --edition=2024 --crate-name verify_knife_choices \
  -L "dependency=$KNIFE_SOURCE/target/release/deps" \
  --extern "knife_core=$KNIFE_CORE_RLIB" \
  verify-choice-text.rs -o "$TMPDIR/verify-knife-choices"
"$TMPDIR/verify-knife-choices" "$ROMFS"
```

`KNIFE_CORE_RLIB` is the matching `libknife_core-*.rlib` produced by the pinned
checkout and toolchain; do not substitute an unrelated build. The verifier reads
only the two named input archives. It prints the requested strings, matching
`SELR` references and a 13-string coverage assertion. It does not write files.

The regression test checks the guide against this small evidence ledger.
CI passing is not independent proof of the underlying extraction; a reviewer
must inspect/reproduce its source and provenance separately.
