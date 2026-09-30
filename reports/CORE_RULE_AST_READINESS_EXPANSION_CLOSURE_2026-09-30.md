# Core Rule AST Readiness Expansion V1 — Closure

Date: **2026-09-30**

## Result

**PASS — 33 source-shape blockers re-audited fail-closed; 11 modal-sentence readiness candidates isolated; no AST expansion performed.**

## Closed scope

The milestone revisited only the **33** paragraphs that were source-shape blocked by the closed `CORE_RULE_SEMANTIC_AST_READINESS_V1` baseline:

- `BLOCKED_SENTENCE_SHAPE`: **28**;
- `BLOCKED_COMPLEX_DELIMITERS`: **4**;
- `BLOCKED_PARENTHETICAL_SCOPE`: **1**.

All **33 / 33** official-source paragraph hashes reproduced.

The previously validated direct-modal node remains unchanged:

- node: `core-ast-direct-modal--13-07--p50-o1`;
- decision: `OPAQUE_PRESERVED`;
- AST mutated: **false**;
- interaction edges: **0**;
- additional paragraphs admitted: **0**.

## Expansion result

Exactly **11** paragraphs satisfy the narrow `CANDIDATE_SINGLE_MODAL_SENTENCE` readiness gate.

Candidate modal axes:

- permission: **9**;
- prohibition: **2**;
- obligation: **0**;
- conditional candidates: **0**.

Every positive candidate has:

- exactly one normative modal in the selected sentence;
- zero condition cues;
- zero colon/semicolon delimiters;
- zero parenthetical/bracket delimiters;
- terminal punctuation;
- a reproducible official-source sentence range and semantic SHA-256.

Candidate status is **not** AST admission and is **not** parser admission.

## Remaining 22 blockers

The other **22** paragraphs remain fail-closed:

- `BLOCKED_CONDITION_OUTSIDE_MODAL_SENTENCE`: **5**;
- `BLOCKED_DELIMITER_SCOPE`: **4**;
- `BLOCKED_MODAL_SENTENCE_COMPLEX_DELIMITERS`: **2**;
- `BLOCKED_MODAL_SENTENCE_NONTERMINAL`: **2**;
- `BLOCKED_MODAL_SENTENCE_PARENTHETICAL_SCOPE`: **7**;
- `BLOCKED_PARENTHETICAL_SCOPE`: **1**;
- `BLOCKED_SENTENCE_SEGMENTATION`: **1**.

No blocker class was globally relaxed.

## Safety result

- new AST nodes created: **0**;
- interaction edges created: **0**;
- existing AST nodes mutated: **0**;
- additional paragraphs admitted: **0**;
- parent-review blockers relaxed: **false**;
- modal-multiplicity blockers relaxed: **false**;
- repeated-variant blockers relaxed: **false**;
- complex-semantic blockers relaxed: **false**;
- paragraph/sentence prose committed: **false**;
- `current_normalized_factions` change: **0**.

## Evidence

Primary report:

`reports/CORE_RULE_AST_READINESS_EXPANSION_CURRENT.json`

Full snapshot:

`rules/11e/snapshots/2026-09-30/core_rule_ast_readiness_expansion/index.json`

Model:

`docs/CORE_RULE_AST_READINESS_EXPANSION_MODEL.md`

Tool:

`tools/audit_core_rule_ast_readiness_expansion.py`

Workflow:

`.github/workflows/core-rule-ast-readiness-expansion.yml`

Source-backed implementation workflow:

- run `36734460626` — **SUCCESS**.

Implementation-head generic repository validation:

- run `36734460041` — **SUCCESS**.

Current normative/app gap projection after expansion:

- run `36735485529` — **SUCCESS**.

Final closure-head PR validation is required before merge.

## Authority boundary

This milestone does **not** claim:

- that any of the 11 candidates is already an AST node;
- that all 11 candidates should be parsed;
- subject/action semantic types for any candidate;
- condition/effect AST completeness;
- a rule-interaction graph;
- repeated-variant equivalence;
- Codex/app equivalence;
- any increase in whole-faction normative coverage.

## Next milestone

`CORE_RULE_MODAL_SENTENCE_CANDIDATE_SELECTION_V1`

Scope:

- compare only the 11 source-hash-verified sentence candidates;
- choose **at most one** candidate for a separately reviewed parser pilot;
- selection must be deterministic and based on structural complexity/provenance, not semantic guesswork;
- preserve the existing 13.07 AST node unchanged and opaque;
- do not create any new AST node during candidate selection itself.
