# Core Rules direct-modal AST pilot v1 closure — 2026-09-30

## Result

**PASS — exactly one readiness-approved Core Rules paragraph now has one copyright-safe structural AST node.**

No second paragraph was admitted.

## Pilot identity

- rule: `13.07`;
- paragraph: `core-rule-13-07--p50--l1--para-p50-o1`;
- node: `core-ast-direct-modal--13-07--p50-o1`;
- node type: `DIRECT_MODAL_CLAUSE`;
- modal operator: `PERMISSION`;
- lexical signal: `PERMISSION_CAN`.

## Verified structural partition

Parent paragraph:

- page: **50**;
- paragraph tokens: **17**;
- verified paragraph semantic SHA-256: reproduced.

AST partition:

- opaque subject span: **1 token**;
- modal operator span: **1 token**;
- opaque action/predicate span: **15 tokens**;
- total: **17 / 17 tokens**;
- source/page hashes: reproduced;
- spans: ordered and non-overlapping;
- interaction edges created: **0**.

No subject or predicate prose is committed.

## Scope boundary

The pilot creates **one structural AST node**, but does not yet resolve:

- subject semantic/entity type;
- action semantic type;
- target/object;
- quantifier;
- condition/effect semantics beyond the direct modal shape;
- rule interactions;
- repeated-variant equivalence;
- Codex/app equivalence.

Therefore:

- full Core condition/effect AST remains incomplete;
- interaction graph remains incomplete;
- `current_normalized_factions = 0` remains intentional;
- `full_normative_semantic_factions = 0` remains intentional.

## Pilot summary

- AST nodes: **1**;
- unique node keys: **1**;
- paragraphs parsed: **1**;
- direct-modal nodes: **1**;
- permission nodes: **1**;
- conditional nodes: **0**;
- subject spans: **1**;
- action/predicate spans: **1**;
- source hashes reproduced: **1**;
- token partitions complete: **1**;
- interaction edges: **0**;
- additional paragraphs admitted: **0**.

## Tooling

- model: `docs/CORE_RULE_DIRECT_MODAL_AST_PILOT_MODEL.md`;
- schema: `schemas/core_rule_direct_modal_ast_pilot.schema.json`;
- builder: `tools/build_core_rule_direct_modal_ast_pilot.py`;
- tests: `tests/test_core_rule_direct_modal_ast_pilot.py`;
- workflow: `.github/workflows/core-rule-direct-modal-ast-pilot.yml`;
- snapshot: `rules/11e/snapshots/2026-09-30/core_rule_direct_modal_ast_pilot/index.json`;
- compact report: `reports/CORE_RULE_DIRECT_MODAL_AST_PILOT_CURRENT.json`.

## Validation checkpoints

- direct-modal AST pilot workflow `36713380722` — **SUCCESS**;
- repository validator + full contract suite `36713380314` — **SUCCESS**;
- normative/app equivalence gap audit `36713380431` — **SUCCESS**.

## Next milestone

`CORE_RULE_DIRECT_MODAL_AST_SEMANTIC_VALIDATION_V1`

Scope remains the same **single node**:

1. inspect the verified source range for the pilot node;
2. determine whether subject and action/predicate can be typed without speculative inference;
3. retain hash/range provenance;
4. keep interaction edges at zero;
5. do not admit a second paragraph;
6. if semantic typing is ambiguous, preserve opaque spans and close fail-closed rather than guessing.
