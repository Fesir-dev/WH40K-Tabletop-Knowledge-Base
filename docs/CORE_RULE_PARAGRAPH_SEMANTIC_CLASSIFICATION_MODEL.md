# Core Rules paragraph semantic classification model v1

## Purpose

This layer classifies the **310 stable Core Rules paragraph atoms** into conservative structural-semantic roles without committing Games Workshop paragraph prose.

It is a classification layer, not a condition/effect AST and not a rule-interaction graph.

## Source chain

Required evidence:

1. verified Games Workshop public 11E Core Rules PDF;
2. `CORE_RULE_PARAGRAPH_ATOMIZATION_V1` snapshot with exactly **310** stable paragraph atoms;
3. every paragraph semantic SHA must reproduce from the verified PDF character range before classification.

Any source/range/hash drift fails closed.

## Classification principle

V1 separates two things:

- **signals** — deterministic lexical/structural evidence found inside a verified paragraph range;
- **primary role** — a conservative summary assigned only when the signal pattern is sufficiently unambiguous.

The repository commits signal IDs/counts and role labels, never the paragraph text that triggered them.

## Signal vocabulary

### Modal / normative signals

- `OBLIGATION_MUST` — normative `must` / `must be` forms.
- `PROHIBITION_MUST_NOT` — `must not`.
- `PROHIBITION_CANNOT` — `cannot` / `can't`.
- `PERMISSION_CAN` — normative `can`.
- `PERMISSION_MAY` — normative `may`.

### Control-flow signals

- `CONDITION_IF` — conditional `if`.
- `TRIGGER_WHEN` — `when`.
- `DURATION_WHILE` — `while`.
- `EXCEPTION_UNLESS` — `unless`.
- `SEQUENCE_BEFORE` — `before`.
- `SEQUENCE_AFTER` — `after`.
- `SEQUENCE_THEN` — `then`.

### Definition / transformation signals

- `DEFINITION_MEANS` — `means`.
- `DEFINITION_KNOWN_AS` — `known as`.
- `DEFINITION_REFERRED_TO_AS` — `referred to as`.
- `REPLACEMENT_INSTEAD` — `instead`.
- `MODIFIER_ADD_SUBTRACT` — explicit add/subtract modifier language.

### Reference signals

- `REFERENCE_SEE` — short cross-reference cue such as `see ...`.
- `REFERENCE_RULE_REF` — another numbered Core rule reference is present in the paragraph.
- `REFERENCE_PAGE` — an explicit page reference is present.

### Procedure/list signals

- `ORDERED_STEP` — paragraph begins with a short numbered/lettered step marker.
- `BULLET_LIKE` — extractor range contains repeated bullet-like line starts.

## Primary roles

### `PROHIBITION`

Assigned only when a prohibition signal exists and no obligation/permission signal competes.

### `OBLIGATION`

Assigned only when an obligation signal exists and no prohibition/permission signal competes.

### `PERMISSION`

Assigned only when permission signals exist and no obligation/prohibition signal competes.

### `DEFINITION`

Assigned when definition signals exist and no competing normative modal signal exists.

### `PROCEDURE_OR_SEQUENCE`

Assigned when ordered-step or sequence signals exist without competing normative/definition signals.

### `CONDITION_OR_TRIGGER`

Assigned when conditional/trigger signals exist without competing normative/definition/sequence signals.

### `REFERENCE_OR_CROSS_REFERENCE`

Assigned only when reference signals are the only strong semantic class.

### `MIXED`

Assigned when multiple strong semantic classes compete in the same paragraph.

### `UNCLASSIFIED`

Assigned when no high-confidence v1 signal supports a primary role.

## Confidence

V1 confidence is structural, not semantic truth probability:

- `HIGH` — one strong role family and no competing strong family;
- `MIXED` — two or more role families;
- `NONE` — no high-confidence role family.

No medium-confidence guessing is used.

## Repeated occurrence variants

The ten paragraph atoms derived from repeated rules `15.07–15.11` are classified independently.

Equal/different classification does not establish semantic equivalence or conflict between occurrences.

## Stored evidence

Per paragraph atom:

- stable `paragraph_key`;
- parent rule/occurrence identity;
- source page/range and semantic hash;
- list of signal IDs with occurrence counts;
- signal-family counts;
- `primary_role`;
- `classification_confidence`;
- classifier version.

No matched phrase, paragraph excerpt, sentence, or reconstructed prose is committed.

## Completion gate

V1 passes when:

1. all **310 / 310** paragraph atoms are represented;
2. all paragraph hashes reproduce from the verified PDF;
3. all classifier outputs use the fixed signal/role vocabulary;
4. every atom has exactly one primary role;
5. every atom has a confidence state;
6. repeated variants remain independent;
7. no prose-bearing evidence fields are committed;
8. whole-faction normative counters remain unchanged.

A high `UNCLASSIFIED` or `MIXED` count does not fail the pipeline. It is preferred to overclassification.

## Non-goals

This layer does not establish:

- condition/effect AST nodes;
- quantified rule predicates;
- subject/object entity resolution;
- rule-interaction edges;
- repeated-variant semantic equivalence;
- Codex/app equivalence;
- full-faction normative completeness.
