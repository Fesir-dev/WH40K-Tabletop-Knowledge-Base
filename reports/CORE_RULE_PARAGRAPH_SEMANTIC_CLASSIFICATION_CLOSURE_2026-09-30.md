# Core Rules paragraph semantic classification v1 closure — 2026-09-30

## Result

**PASS — all 310 stable Core Rules paragraph identities now have deterministic conservative lexical/structural semantic-role classifications.**

## Verified source chain

The classifier is downstream of:

- Games Workshop public 11E Core Rules;
- verified official binary SHA-256;
- **88 / 88** page semantic fingerprints;
- document semantic SHA-256;
- `CORE_RULE_PARAGRAPH_ATOMIZATION_V1`;
- exactly **310** stable paragraph atoms.

Before classification, every paragraph semantic SHA is reproduced from its verified PDF character range.

## Classification result

Generated snapshot:

`rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json`

Compact report:

`reports/CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_CURRENT.json`

Exact baseline:

- paragraphs classified: **310 / 310**;
- unique paragraph identities: **310**;
- paragraph hashes reproduced from verified PDF: **310 / 310**;
- paragraphs with lexical/structural signals: **200**;
- paragraphs without signals: **110**;
- repeated-occurrence paragraph variants: **10**.

Primary role distribution:

- `CONDITION_OR_TRIGGER`: **31**;
- `MIXED`: **134**;
- `MODIFICATION_OR_REPLACEMENT`: **1**;
- `OBLIGATION`: **1**;
- `PERMISSION`: **20**;
- `PROCEDURE_OR_SEQUENCE`: **7**;
- `PROHIBITION`: **4**;
- `UNCLASSIFIED`: **112**.

Confidence distribution:

- `HIGH`: **64**;
- `MIXED`: **134**;
- `NONE`: **112**.

## Fail-closed policy

This milestone intentionally does **not** force every paragraph into a clean semantic type.

`MIXED` means more than one strong role family is present.

`UNCLASSIFIED` means the v1 signal vocabulary does not justify a high-confidence primary role.

These are valid successful states, not pipeline failures.

Formatting-only bullet evidence is weak context and does not independently create a semantic role.

## Repeated occurrence variants

The ten paragraph atoms belonging to repeated rules `15.07–15.11` remain independent.

Current repeated-variant role distribution:

- `CONDITION_OR_TRIGGER`: **2**;
- `MIXED`: **8**.

No semantic equivalence, conflict, chronology, supersession or canonical occurrence is inferred.

## Authority boundary

This milestone establishes lexical/structural semantic-role evidence only.

It does **not** establish:

- condition/effect AST nodes;
- semantic subject/object resolution;
- quantified predicates;
- rule-interaction edges;
- semantic equivalence of repeated variants;
- Codex/app equivalence;
- full-faction normative completeness.

Therefore:

- `current_normalized_factions = 0` remains intentional;
- `full_normative_semantic_factions = 0` remains intentional;
- app/Codex-only semantics remain `PENDING/UNKNOWN`.

## Tooling

- model: `docs/CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_MODEL.md`;
- schema: `schemas/core_rule_paragraph_semantic_classification.schema.json`;
- classifier: `tools/classify_core_rule_paragraph_semantics.py`;
- tests: `tests/test_core_rule_paragraph_semantic_classification.py`;
- workflow: `.github/workflows/core-rule-paragraph-semantic-classification.yml`.

The normative/app gap workflow now also exposes and checkpoints its canonical generated report so current-layer integration remains reproducible.

## Validation evidence before final closure commit

- semantic-classification workflow `36706607549` — **SUCCESS**;
- normative/app equivalence gap audit `36706607636` — **SUCCESS**;
- overlap reproducibility workflow `36706342065` — **SUCCESS**.

The generic repository validator on the immediately preceding author head had only the stale generated gap-report reproducibility failure; all other repository contracts, including paragraph semantic classification, passed. The final closure head must re-run the repository validator after the canonical report checkpoint.

## Next milestone

`CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1`

Scope:

1. review the **134 MIXED** paragraph classifications;
2. review the **112 UNCLASSIFIED** paragraph classifications;
3. distinguish genuinely multi-role text from classifier limitations;
4. refine signal rules only where verified evidence justifies it;
5. preserve uncertain cases instead of forcing classification;
6. do not enter an AST-readiness gate until the review establishes a safe parse subset;
7. keep paragraph prose external and whole-faction normative counters unchanged.
