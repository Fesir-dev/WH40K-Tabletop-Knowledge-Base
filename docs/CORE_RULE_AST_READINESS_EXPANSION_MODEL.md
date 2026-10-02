# Core Rule AST Readiness Expansion V1

## Purpose

Refine only the **33 source-shape-blocked paragraphs** from the closed
`CORE_RULE_SEMANTIC_AST_READINESS_V1` snapshot.

This milestone does not revisit the other 277 paragraphs and does not create
any AST node.

Parent blocked population:

- `BLOCKED_SENTENCE_SHAPE`: **28**;
- `BLOCKED_COMPLEX_DELIMITERS`: **4**;
- `BLOCKED_PARENTHETICAL_SCOPE`: **1**.

The previously validated node
`core-ast-direct-modal--13-07--p50-o1` is immutable and remains opaque.

## Expansion object

The only new positive readiness object is a
`CANDIDATE_SINGLE_MODAL_SENTENCE`.

A paragraph may receive that state only when all of the following are true:

1. its parent readiness state is `BLOCKED_SENTENCE_SHAPE`;
2. verified Games Workshop source text and paragraph hash reproduce;
3. deterministic sentence segmentation yields two or more bounded sentence
   ranges;
4. exactly one sentence contains the paragraph's one normative modal signal;
5. every recognized condition cue in the paragraph is inside that same modal
   sentence;
6. the modal sentence ends with terminal punctuation;
7. the modal sentence has no colon or semicolon;
8. the modal sentence has no parenthetical or bracket delimiters;
9. the modal sentence contains no second normative modal;
10. no AST node is created.

The committed candidate stores only parent identity, sentence ordinal/range,
counts and semantic hashes. Sentence prose is not committed.

## Fail-closed states

Previously blocked paragraphs that do not satisfy the positive gate remain
blocked and receive a more specific expansion state:

- `BLOCKED_SENTENCE_SEGMENTATION`;
- `BLOCKED_MODAL_SENTENCE_NOT_UNIQUE`;
- `BLOCKED_CONDITION_OUTSIDE_MODAL_SENTENCE`;
- `BLOCKED_MODAL_SENTENCE_COMPLEX_DELIMITERS`;
- `BLOCKED_MODAL_SENTENCE_PARENTHETICAL_SCOPE`;
- `BLOCKED_MODAL_SENTENCE_NONTERMINAL`;
- `BLOCKED_DELIMITER_SCOPE`;
- `BLOCKED_PARENTHETICAL_SCOPE`.

The four parent `BLOCKED_COMPLEX_DELIMITERS` rows and the one parent
`BLOCKED_PARENTHETICAL_SCOPE` row are classification targets only in v1;
they cannot become candidates in this milestone.

## Source and identity contract

Every audited row must preserve:

- parent paragraph key;
- rule/occurrence identity;
- parent readiness state;
- paragraph semantic SHA-256;
- page semantic SHA-256;
- verified source page/range;
- source hash reproduction.

Every positive sentence candidate additionally stores:

- sentence ordinal;
- paragraph-relative and page-absolute character range;
- token/character counts;
- sentence semantic SHA-256;
- modal axis;
- modal occurrence count;
- condition-cue count.

## Safety boundary

This milestone:

- creates **0 AST nodes**;
- creates **0 interaction edges**;
- mutates **0 existing AST nodes**;
- admits **0 repeated-variant paragraphs**;
- does not relax parent-review/modal-multiplicity/complex-semantic blockers;
- does not infer subject/action semantic types;
- does not infer Codex/app semantics;
- does not change whole-faction normative coverage.

## Completion gate

Expansion v1 passes when:

- exactly 33 parent shape-blocked rows are audited;
- source hashes reproduce for all 33;
- every row receives exactly one expansion state;
- any positive candidate satisfies every gate above;
- no row outside the 33-parent population appears;
- no AST node or interaction edge is created;
- the previously validated direct-modal node remains unchanged/opaque.

## Next decision

Only after the audit closes may a later milestone decide whether any
`CANDIDATE_SINGLE_MODAL_SENTENCE` rows deserve a separate parser pilot.
Candidate status is not AST readiness and does not authorize automatic node
creation.
