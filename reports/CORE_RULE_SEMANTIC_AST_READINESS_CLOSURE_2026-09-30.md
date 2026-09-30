# Core Rules semantic AST readiness v1 closure — 2026-09-30

## Result

**PASS — readiness audit completed across all 310 stable Core Rules paragraph identities without creating any AST nodes.**

The audit intentionally narrows the first parser pilot to exactly **one** paragraph.

## Parent evidence

Closed parent layers:

- `CORE_RULE_PARAGRAPH_ATOMIZATION_V1` — 310 stable paragraph identities;
- `CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1`;
- `CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1`.

Parent review baseline:

- profiles: **310**;
- `AXIS_PROFILE_READY`: **156**;
- `MULTI_MODAL_REVIEW_REQUIRED`: **42**;
- `NO_STRONG_SIGNAL_REVIEW_REQUIRED`: **112**.

All 154 review-required rows are blocked before readiness analysis.

## Pre-shape readiness gates

The 156 axis-profile-ready rows are narrowed by ordered fail-closed gates:

- parent-review blocked: **154**;
- no normative modal: **61**;
- modal multiplicity: **27**;
- complex semantic axes: **26**;
- multiple condition cues: **6**;
- repeated occurrence variant: **2**.

After these gates, **34** paragraph ranges enter verified source-shape analysis.

## Verified source-shape result

All **34 / 34** candidate ranges reproduce their semantic SHA-256 from the verified official Games Workshop Core Rules PDF.

Shape results:

- `BLOCKED_SENTENCE_SHAPE`: **28**;
- `BLOCKED_COMPLEX_DELIMITERS`: **4**;
- `BLOCKED_PARENTHETICAL_SCOPE`: **1**;
- `PILOT_READY_DIRECT_MODAL`: **1**;
- `PILOT_READY_CONDITIONAL_MODAL`: **0**.

Therefore:

- shape-analyzed: **34**;
- shape-blocked: **33**;
- pilot-ready: **1**;
- AST nodes created: **0**.

## First parser-pilot identity

The only v1 pilot-ready paragraph is:

- rule: `13.07`;
- paragraph: `core-rule-13-07--p50--l1--para-p50-o1`;
- modal axis: `PERMISSION`;
- condition cues: **0**;
- source-shape: exactly one terminal sentence, no complex delimiter and no parenthetical scope.

This is a parser-pilot candidate only.

It is **not**:

- an AST node;
- proof of semantic equivalence;
- a rule-interaction edge;
- permission to generalize the parser to other paragraphs.

## Repeated variants

Repeated Core-rule variants are explicitly excluded from the first pilot.

- repeated variants pilot-ready: **0**;
- repeated-variant semantic equivalence claimed: **false**.

## Authority boundary

This milestone establishes only a reproducible readiness gate.

It does not establish:

- condition/effect AST completeness;
- subject/object resolution;
- quantified predicates;
- interaction-graph completeness;
- Codex/app equivalence;
- full-faction normative completeness.

Accordingly:

- `current_normalized_factions = 0` remains intentional;
- `full_normative_semantic_factions = 0` remains intentional;
- app/Codex-only semantics remain `PENDING/UNKNOWN`.

## Tooling

- model: `docs/CORE_RULE_SEMANTIC_AST_READINESS_MODEL.md`;
- schema: `schemas/core_rule_semantic_ast_readiness.schema.json`;
- audit tool: `tools/audit_core_rule_semantic_ast_readiness.py`;
- tests: `tests/test_core_rule_semantic_ast_readiness.py`;
- workflow: `.github/workflows/core-rule-semantic-ast-readiness.yml`;
- snapshot: `rules/11e/snapshots/2026-09-30/core_rule_semantic_ast_readiness/index.json`;
- compact report: `reports/CORE_RULE_SEMANTIC_AST_READINESS_CURRENT.json`.

## Validation checkpoints

Final pre-closure runs:

- repository validation run `36712053452` — **SUCCESS**;
- normative/app gap audit run `36712053275` — **SUCCESS**;
- readiness workflow run `36712053380` — readiness build + authority checks **SUCCESS**.

## Next milestone

`CORE_RULE_DIRECT_MODAL_AST_PILOT_V1`

Scope is deliberately one paragraph only:

1. parse `core-rule-13-07--p50--l1--para-p50-o1`;
2. build the smallest copyright-safe direct-modal AST representation;
3. retain source-range/hash provenance;
4. validate subject/modal/action extraction against the verified source range;
5. do not add a second paragraph until the pilot closes;
6. do not create interaction edges or infer Codex/app semantics.
