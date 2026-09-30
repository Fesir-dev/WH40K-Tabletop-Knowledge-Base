# Core Rules semantic AST readiness model v1

## Purpose

This milestone audits which reviewed Core Rules paragraph profiles are safe **candidates for a future limited condition/effect parser**.

It does not construct AST nodes.

The gate is deliberately stricter than `AXIS_PROFILE_READY`.

## Parent layers

Required parents:

- `CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1`;
- `CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1`;
- verified Games Workshop public 11E Core Rules source.

Parent review baseline:

- profiles: **310**;
- `AXIS_PROFILE_READY`: **156**;
- `MULTI_MODAL_REVIEW_REQUIRED`: **42**;
- `NO_STRONG_SIGNAL_REVIEW_REQUIRED`: **112**.

All 42 multi-modal and all 112 no-strong-signal profiles are blocked before readiness analysis.

## Readiness is not parsing

A readiness result means only that a paragraph's verified range has a sufficiently simple **surface structure** to enter a future parser pilot.

It does not mean:

- the paragraph already has a condition/effect AST;
- subject/object references are resolved;
- scopes are semantically correct;
- a parsed rule would be authoritative without later validation.

## Ordered readiness gates

Every paragraph receives exactly one readiness state.

### Gate 0 — parent review

If parent review state is not `AXIS_PROFILE_READY`:

`BLOCKED_PARENT_REVIEW`

Expected from the closed parent review: **154**.

### Gate 1 — normative modal axis

A condition/effect pilot requires one normative modal family:

- permission;
- obligation;
- prohibition.

If modal axis is `NONE`:

`BLOCKED_NO_NORMATIVE_MODAL`

Expected after parent review: **61**.

`MULTI_MODAL` is already blocked by Gate 0.

### Gate 2 — modal lexical multiplicity

Exactly one lexical modal signal occurrence is required.

If the paragraph has zero or multiple modal occurrences for its modal axis:

`BLOCKED_MODAL_MULTIPLICITY`

Expected after Gates 0–1: **27**.

### Gate 3 — extra semantic axes

The pilot excludes paragraphs carrying any of:

- procedure/sequence;
- definition;
- modification/replacement;
- reference/cross-reference;
- structural-list shape.

It also excludes the corresponding signal families.

Failure:

`BLOCKED_COMPLEX_SEMANTIC_AXES`

Expected after Gates 0–2: **26**.

### Gate 4 — condition-cue multiplicity

Allowed:

- zero condition/trigger cues → direct-modal candidate;
- exactly one condition/trigger cue → conditional-modal candidate.

More than one cue:

`BLOCKED_MULTIPLE_CONDITION_CUES`

Expected after Gates 0–3: **6**.

### Gate 5 — repeated occurrence variants

Paragraphs from repeated Core-rule occurrences remain structurally independent and are not admitted to the first AST pilot.

Failure:

`BLOCKED_REPEATED_VARIANT`

Expected after Gates 0–4: **2**.

After Gate 5, **34** paragraphs enter source-range shape analysis.

## Verified range-shape gates

The official PDF range is transiently read and its paragraph hash is reproduced before shape checks.

No text is committed.

### Gate 6 — sentence shape

The first parser pilot requires exactly one conservative terminal sentence boundary and terminal punctuation at the end of the normalized range.

The sentence-boundary heuristic intentionally over-blocks abbreviations and uncertain punctuation.

Failure:

`BLOCKED_SENTENCE_SHAPE`

### Gate 7 — complex delimiters

Colon or semicolon delimiters are treated as unresolved internal scope boundaries.

Failure:

`BLOCKED_COMPLEX_DELIMITERS`

### Gate 8 — parenthetical scope

Any round/square parenthetical delimiter is excluded from pilot readiness.

Failure:

`BLOCKED_PARENTHETICAL_SCOPE`

## Pilot-ready states

A paragraph passing every gate is one of:

- `PILOT_READY_DIRECT_MODAL` — exactly one modal and no condition cue;
- `PILOT_READY_CONDITIONAL_MODAL` — exactly one modal and exactly one condition cue.

These states are candidates for a future parser pilot only.

## Stored evidence

Per paragraph:

- stable paragraph/rule/occurrence identity;
- semantic SHA-256;
- parent review state;
- modal axis;
- readiness state and blocker gate;
- modal and condition cue counts;
- token/line/character counts;
- sentence-boundary count;
- terminal-punctuation flag;
- complex-delimiter count;
- parenthetical-delimiter count.

No extracted phrase, sentence or paragraph text is stored.

## Completion

The readiness audit is complete when:

1. all 310 paragraph identities receive exactly one readiness state;
2. parent-review blocked count is **154**;
3. pre-shape blocker counts reproduce **61 / 27 / 26 / 6 / 2**;
4. exactly **34** verified ranges reach shape analysis;
5. all 34 paragraph hashes reproduce from the pinned official PDF;
6. pilot-ready plus shape-blocked counts sum to 34;
7. repeated variants are absent from pilot-ready states;
8. no AST nodes, paragraph prose or inferred interactions are committed;
9. whole-faction normative counters remain unchanged.

The exact first-pilot candidate count is established by the generated readiness snapshot, not guessed in advance.
