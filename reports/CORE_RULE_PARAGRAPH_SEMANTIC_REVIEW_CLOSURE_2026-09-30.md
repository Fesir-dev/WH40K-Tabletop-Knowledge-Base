# Core Rules paragraph semantic review v1 closure — 2026-09-30

## Result

**PASS — all 310 Core Rules paragraph semantic classifications were reviewed as orthogonal semantic profiles without constructing an AST.**

## Parent evidence

Parent milestone:

`CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1`

Verified parent baseline:

- paragraph identities: **310 / 310**;
- source-range hashes reproduced: **310 / 310**;
- confidence: **64 HIGH / 134 MIXED / 112 NONE**;
- parent `MIXED`: **134**;
- parent `UNCLASSIFIED`: **112**.

No paragraph prose is committed by either layer.

## Review finding

The single v1 `primary_role` dimension was intentionally conservative, but it treated many valid cross-axis combinations as `MIXED`.

Review v1 decomposes already-verified signal families into independent axes:

- modal axis;
- condition / trigger;
- procedure / sequence;
- definition;
- modification / replacement;
- reference;
- structural list context.

No new textual inference is introduced.

## Review result

Generated snapshot:

`rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantic_review/index.json`

Compact report:

`reports/CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_CURRENT.json`

Exact result:

- profiles: **310 / 310**;
- unique paragraph keys: **310**;
- `AXIS_PROFILE_READY`: **156**;
- `MULTI_MODAL_REVIEW_REQUIRED`: **42**;
- `NO_STRONG_SIGNAL_REVIEW_REQUIRED`: **112**;
- total still review-blocked for AST purposes: **154**.

Modal-axis distribution:

- `NONE`: **173**;
- `PERMISSION`: **67**;
- `OBLIGATION`: **17**;
- `PROHIBITION`: **11**;
- `MULTI_MODAL`: **42**.

## What happened to the 134 MIXED rows

The original `MIXED` set decomposes into:

- **92** `AXIS_PROFILE_READY` paragraphs — multiple orthogonal axes but no normative modal conflict;
- **42** `MULTI_MODAL_REVIEW_REQUIRED` paragraphs — two or more normative modal families;
- **0** no-strong-signal rows.

Thus most old `MIXED` rows were not semantic conflicts; they were multi-axis compositions.

## What happened to the 112 UNCLASSIFIED rows

They remain fail-closed:

- **110** signal-free;
- **2** weak-only list-shape evidence;
- **112 / 112** remain review-required.

No semantic role is invented for them.

## Repeated variants

The ten repeated-occurrence paragraph variants remain independent:

- `AXIS_PROFILE_READY`: **4**;
- `MULTI_MODAL_REVIEW_REQUIRED`: **6**.

No equivalence, conflict, precedence, chronology or canonical variant is inferred.

## Authority boundary

`AXIS_PROFILE_READY` means only:

- at least one strong semantic family is present; and
- at most one normative modal family is present.

It does **not** mean:

- condition/effect AST ready;
- subject/object resolved;
- predicate scope resolved;
- interaction graph ready;
- repeated variants semantically equivalent;
- Codex/app equivalence established.

Therefore:

- `semantic_ast_readiness_complete = false`;
- `condition_effect_ast_complete = false`;
- `rule_interaction_graph_complete = false`;
- `current_normalized_factions = 0`;
- `full_normative_semantic_factions = 0`.

## Tooling

- model: `docs/CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_MODEL.md`;
- schema: `schemas/core_rule_paragraph_semantic_review.schema.json`;
- tool: `tools/review_core_rule_paragraph_semantics.py`;
- tests: `tests/test_core_rule_paragraph_semantic_review.py`;
- workflow: `.github/workflows/core-rule-paragraph-semantic-review.yml`.

## Validation evidence

Validated implementation head before closure documentation:

- semantic-review workflow `36708075455` — **SUCCESS**;
- normative/app gap audit `36708075439` — **SUCCESS**;
- generic repository validator + full contract suite `36708075044` — **SUCCESS**.

The official-public overlap workflow triggered by the current-layer update is an independent full-corpus regression and does not define semantic-review correctness.

## Next milestone

`CORE_RULE_SEMANTIC_AST_READINESS_V1`

Scope:

1. consider only the **156 AXIS_PROFILE_READY** profiles as candidates;
2. determine a smaller safely parseable subset using explicit structural prerequisites;
3. keep all **42 MULTI_MODAL** profiles blocked;
4. keep all **112 NO_STRONG_SIGNAL** profiles blocked;
5. do not equate axis-profile readiness with AST readiness;
6. do not build condition/effect AST nodes until that readiness gate is validated;
7. keep paragraph prose external and whole-faction normative counters unchanged.
