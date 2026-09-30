# Core Rules paragraph semantic review model v1

## Purpose

This milestone reviews the 310 paragraph classifications produced by `CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1`.

The review does **not** reinterpret Games Workshop prose and does not build condition/effect AST nodes. It reorganizes already-verified lexical/structural signal families into independent semantic axes so that the previous single `primary_role` no longer treats every cross-axis combination as a semantic conflict.

## Parent contract

Required parent:

- `rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json`;
- status `PASS`;
- classifier `CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1`;
- exactly **310** paragraph identities;
- exactly **310** reproduced paragraph hashes;
- baseline: **64 HIGH / 134 MIXED / 112 NONE**;
- baseline roles: **134 MIXED / 112 UNCLASSIFIED** plus the high-confidence single-role classes.

No paragraph prose is committed or reconstructed.

## Review finding

The v1 `MIXED` label conflates orthogonal signal dimensions.

A paragraph can legitimately contain, for example:

- a condition/trigger axis;
- one normative modal axis;
- a sequence/procedure axis;
- definition or modification evidence;

without those axes contradicting one another.

The review therefore decomposes every paragraph into independent axes.

## Semantic profile axes

### Modal axis

Exactly one of:

- `NONE`;
- `PERMISSION`;
- `OBLIGATION`;
- `PROHIBITION`;
- `MULTI_MODAL`.

`MULTI_MODAL` is used when two or more of permission / obligation / prohibition signal families are present in the same paragraph. It remains review-required.

### Control / structure axes

Independent booleans:

- `condition_trigger_present`;
- `procedure_sequence_present`;
- `definition_present`;
- `modification_replacement_present`;
- `reference_present`;
- `structural_list_present`.

These booleans do not by themselves claim subject/object binding, predicate scope, chronology or semantic interaction.

## Review states

### `AXIS_PROFILE_READY`

Assigned when:

- at least one strong semantic family is present; and
- zero or one normative modal family is present.

This means the paragraph can be represented as a non-conflicting multi-axis profile.

It does **not** mean AST-ready.

### `MULTI_MODAL_REVIEW_REQUIRED`

Assigned when two or more normative modal families are present.

No modal precedence or conflict resolution is inferred.

### `NO_STRONG_SIGNAL_REVIEW_REQUIRED`

Assigned when no strong semantic family is present.

Weak-only evidence such as list shape or references does not justify a stronger semantic label.

## Baseline result

Against the closed v1 classification snapshot:

- `AXIS_PROFILE_READY`: **156**;
- `MULTI_MODAL_REVIEW_REQUIRED`: **42**;
- `NO_STRONG_SIGNAL_REVIEW_REQUIRED`: **112**.

Therefore:

- profile-ready without modal conflict: **156 / 310**;
- still review-required: **154 / 310**.

The original `MIXED` population decomposes into:

- **92** axis-profile-ready mixed paragraphs;
- **42** genuinely multi-modal review-required paragraphs.

The original `UNCLASSIFIED` population remains:

- **110** signal-free paragraphs;
- **2** weak-only list-shape paragraphs.

Repeated occurrence variants remain independent:

- **4** axis-profile-ready;
- **6** multi-modal review-required.

## Modal-axis baseline

Across all 310 paragraphs:

- `NONE`: **173**;
- `PERMISSION`: **67**;
- `OBLIGATION`: **17**;
- `PROHIBITION`: **11**;
- `MULTI_MODAL`: **42**.

## Completion boundary

Review v1 is complete when:

1. all 310 parent paragraph identities are represented exactly once;
2. every row has one modal-axis value and all six independent boolean axes;
3. review-state counts reproduce **156 / 42 / 112**;
4. original 134 MIXED rows reproduce as **92 profile-ready + 42 multi-modal**;
5. original 112 UNCLASSIFIED rows remain review-required;
6. all 10 repeated variants remain independently represented;
7. no paragraph prose or matched phrases are committed;
8. no condition/effect AST, interaction graph or Codex/app equivalence is claimed;
9. whole-faction normative counters remain unchanged.

## Next gate

After review closure, the next milestone is:

`CORE_RULE_SEMANTIC_AST_READINESS_V1`

That gate may assess which subset of the **156 AXIS_PROFILE_READY** rows is safe for limited AST parsing. It must not assume that all 156 are AST-ready.
