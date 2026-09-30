# Core Rule Direct-Modal AST Semantic Validation V1 — Closure

Date: **2026-09-30**

## Result

**PASS — semantic validation closed fail-closed with `OPAQUE_PRESERVED`.**

The single existing direct-modal pilot node was revalidated against the verified Games Workshop Core Rules source range. The validation layer correctly refused to add semantic types that are not justified by the current closed lexicons.

Target:

- node: `core-ast-direct-modal--13-07--p50-o1`;
- rule: `13.07`;
- paragraph: `core-rule-13-07--p50--l1--para-p50-o1`;
- node type: `DIRECT_MODAL_CLAUSE`;
- parent AST nodes admitted: **1**;
- additional paragraphs admitted: **0**;
- interaction edges created: **0**.

## Subject validation

The parent subject span remains structurally valid:

- token count: **1**;
- semantic hash reproduced;
- source range reproduced;
- closed subject-lexicon match: **none**.

Decision:

`OPAQUE_SUBJECT_SPAN` / `LEXEME_NOT_IN_CLOSED_SUBJECT_LEXICON`.

No broader game-entity class is inferred from context or ordinary-language interpretation.

## Action/predicate validation

The 15-token action/predicate span also remains structurally valid and hash-reproduced.

Deterministic decomposition is rejected because:

- no leading action head exists in the closed action lexicon;
- a coordination cue is present;
- therefore the current parser cannot isolate one unambiguous typed action head plus opaque arguments.

Recorded blockers:

- `COORDINATION_CUE`;
- `UNRECOGNIZED_ACTION_HEAD`.

Decision:

`OPAQUE_ACTION_PREDICATE_SPAN` preserved unchanged.

## AST decision

Overall decision:

`OPAQUE_PRESERVED`.

- subject types resolved: **0**;
- predicate heads resolved: **0**;
- full refinements allowed: **0**;
- partial refinements allowed: **0**;
- AST mutated: **false**;
- interaction edges created: **0**;
- additional paragraphs admitted: **0**.

The existing direct-modal structural node therefore remains exactly one permission-modal node with opaque subject and opaque action/predicate spans.

## Authority boundary

This milestone does **not** claim:

- a resolved subject/game-entity type;
- a resolved action verb class;
- target/object or quantifier resolution;
- condition/effect AST completeness;
- a rule-interaction graph;
- semantic equivalence to another Core rule;
- repeated-variant equivalence;
- Codex/app equivalence;
- any increase in whole-faction normative coverage.

`current_normalized_factions = 0` and `full_normative_semantic_factions = 0` remain unchanged.

## Validation evidence

Generated semantic-validation workflow:

- `36729536267` — **SUCCESS**.

Current normative/app gap projection:

- `36733041159` — **SUCCESS**.

Latest generic repository validation after regression expectation repair:

- `36733049749` — **SUCCESS**.

## Next milestone

`CORE_RULE_AST_READINESS_EXPANSION_V1`

Scope:

- preserve this validated AST node unchanged;
- revisit only the **33** source-shape-blocked readiness candidates;
- refine deterministic source-shape gates where possible;
- do not create new AST nodes during the readiness audit itself;
- do not weaken parent-review, modal-multiplicity, repeated-variant or complex-semantic blockers;
- any later parser expansion must be separately reviewed and source-hash gated.
