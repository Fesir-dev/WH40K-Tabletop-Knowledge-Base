# Core Rules direct-modal AST pilot v1

## Purpose

This milestone builds the first **single-paragraph structural AST node** from the only paragraph approved by `CORE_RULE_SEMANTIC_AST_READINESS_V1`.

Pilot scope is fixed to:

- rule: `13.07`;
- paragraph: `core-rule-13-07--p50--l1--para-p50-o1`;
- modal axis: `PERMISSION`;
- lexical signal: `PERMISSION_CAN`;
- condition cues: **0**.

No second paragraph is eligible in v1.

## Source gate

Before emitting the node, the parser must verify:

1. the Games Workshop Core Rules source through the existing verified-source pipeline;
2. the paragraph page/range from the stable paragraph atom;
3. paragraph semantic SHA-256;
4. readiness state `PILOT_READY_DIRECT_MODAL`;
5. exactly one lexical `PERMISSION_CAN` signal;
6. exactly one standalone modal token matching `can`;
7. no condition cue, complex delimiter, parenthetical scope or multi-sentence shape.

Any mismatch fails closed.

## AST shape

The v1 node is intentionally minimal:

`DIRECT_MODAL_CLAUSE`

It contains three ordered source spans:

1. `subject_span` — opaque text before the modal;
2. `modal_operator` — normalized operator `PERMISSION`, lexical signal `PERMISSION_CAN`;
3. `action_predicate_span` — opaque text after the modal.

The subject and predicate are **not semantically typed** in this pilot.

Stored evidence is limited to:

- relative/absolute character offsets;
- token/character counts;
- semantic SHA-256 of each opaque span;
- modal operator/signal ID;
- parent paragraph/rule identity;
- page/range/hash provenance;
- parser validation flags.

The raw subject, predicate and paragraph prose are not committed.

## Partition contract

After trimming only leading/trailing whitespace:

- subject span is non-empty;
- modal span is exactly one standalone lexical modal;
- action/predicate span is non-empty;
- spans are ordered and non-overlapping;
- subject tokens + modal token + predicate tokens equal the verified paragraph token count;
- the original paragraph semantic hash still reproduces from the official PDF range.

Punctuation may remain inside the opaque action/predicate span. The pilot does not interpret punctuation semantically.

## What the node means

The parser may claim only:

> this verified paragraph has one structurally recoverable direct permission-modal clause with an opaque subject span and opaque action/predicate span.

It may **not** claim:

- resolved game entity/subject type;
- action verb class;
- target/object;
- quantifier;
- condition/effect AST;
- interaction edge;
- semantic equivalence to another rule;
- full Core Rules AST coverage;
- Codex/app equivalence.

## Completion gate

The pilot passes when:

- exactly one AST node is emitted;
- it belongs to the readiness-approved paragraph and rule 13.07;
- source and parent hashes reproduce;
- the direct modal split is unique;
- all three spans validate;
- no prose-bearing field is committed;
- no interaction edge is created;
- no additional paragraph enters the pilot.

## Next decision

After the pilot closes, evaluate whether the node representation itself is trustworthy and useful.

Expansion to additional paragraphs requires a separate milestone and must not be inferred merely from this one successful node.
