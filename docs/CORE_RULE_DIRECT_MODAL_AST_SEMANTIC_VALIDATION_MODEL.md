# Core Rule Direct-Modal AST Semantic Validation V1

## Purpose

Validate the **single** existing `DIRECT_MODAL_CLAUSE` pilot node without expanding parser scope.

Target:

- node: `core-ast-direct-modal--13-07--p50-o1`;
- rule: `13.07`;
- paragraph: `core-rule-13-07--p50--l1--para-p50-o1`;
- parent AST node count: **1**;
- additional paragraphs admitted: **0**;
- interaction edges: **0**.

## Validation questions

1. Can the existing 1-token subject span be typed from an exact, closed game-entity lexicon?
2. Can the 15-token action/predicate span be decomposed into a deterministic action head plus opaque arguments without semantic inference?

## Fail-closed rules

Subject typing is allowed only for exact canonical lexemes in the closed subject lexicon. Otherwise the subject remains `OPAQUE_SUBJECT_SPAN`.

Predicate decomposition is allowed only when:

- the leading lexical action head belongs to the closed action lexicon;
- the predicate contains no second modal operator;
- no condition cue is introduced;
- no negation cue is introduced;
- no coordinating action cue is present;
- no subordinate-clause cue is present.

Arguments remain opaque even when an action head is accepted.

## Decisions

- `FULL_REFINEMENT_ALLOWED`: subject type and action head both deterministic.
- `PARTIAL_REFINEMENT_ALLOWED`: exactly one side is deterministic.
- `OPAQUE_PRESERVED`: neither side can be safely typed.

This validation layer does **not** mutate the pilot AST. A later milestone may apply only refinements explicitly authorized by this report.

## Copyright boundary

The official source range is reconstructed transiently from the verified Games Workshop PDF. Repository artifacts store:

- offsets;
- token/character counts;
- semantic hashes;
- semantic type identifiers;
- blocker identifiers.

No paragraph prose is committed.

## Authority boundary

- Games Workshop remains normative.
- No second paragraph is admitted.
- No interaction edge is created.
- No repeated-variant equivalence is inferred.
- No Codex/app semantics are inferred.
- Whole-faction normative counters remain unchanged.
