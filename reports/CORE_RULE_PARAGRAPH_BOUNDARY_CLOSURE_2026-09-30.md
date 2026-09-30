# Core paragraph/rule-body boundary extraction v1 closure — 2026-09-30

## Result

**PASS — deterministic copyright-safe boundaries exist for all 141 stable numbered Core Rules atoms.**

## Source and parent gates

Before boundary extraction the pipeline revalidates:

- official Games Workshop Core Rules binary SHA-256;
- all **88 / 88** page semantic fingerprints;
- complete document semantic SHA-256;
- parent Core atomization state **141 / 141** with **0** heading-recovery gaps.

Source and parent verification: **PASS**.

## Boundary result

Generated snapshot:

`rules/11e/snapshots/2026-09-30/core_rule_boundaries/index.json`

Compact report:

`reports/CORE_RULE_PARAGRAPH_BOUNDARIES_CURRENT.json`

Exact result:

- Core rules: **141**;
- heading occurrences / rule-body blocks: **146**;
- families: **24**;
- `SINGLE_OCCURRENCE_BOUNDARY`: **136**;
- `REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH`: **5**;
- heading-line recovery gaps: **0**;
- empty rule-body boundaries: **0**;
- page-local paragraph candidates: **310**;
- rules with multiple occurrences: **5**;
- every rule has a non-empty boundary.

## Repeated occurrence variants

The five repeated rules remain:

- `15.07`;
- `15.08`;
- `15.09`;
- `15.10`;
- `15.11`.

Each has two verified occurrence blocks. The normalized body hashes differ between the two occurrences, so the boundary layer records them as `REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH`.

This classification does **not** automatically create a semantic conflict and does not assert which occurrence is semantically canonical.

## Boundary semantics

An occurrence block begins after its verified atom heading and ends immediately before the next numbered atom heading inside the same parent family range. The final occurrence in a family ends at the end of that family page range.

A block may span pages.

Within every page-local body span, contiguous non-empty extracted lines separated by blank lines are represented as paragraph-boundary candidates.

V1 deliberately treats these as extraction structure, not semantic paragraphs.

## Committed evidence

The repository stores only:

- rule/occurrence identities;
- heading page/line anchors and label hashes;
- page-local line ranges;
- page-local character offsets;
- line/character/token counts;
- raw/normalized hashes;
- parent page semantic hashes;
- paragraph candidate ranges/counts/hashes;
- end-boundary relationships.

No paragraph or rule-body prose is committed.

## Authority boundary

This milestone does **not** establish:

- semantic paragraph AST;
- conditions/effects parsing;
- semantic equivalence between repeated occurrence bodies;
- rule-interaction graph;
- Codex/app equivalence;
- whole-faction normative completeness.

Therefore:

- `current_normalized_factions = 0` remains intentional;
- `full_normative_semantic_factions = 0` remains intentional;
- app/Codex-only wording remains `PENDING/UNKNOWN`.

## Current-layer integration

The candidate advances:

- Core currentness → `OFFICIAL_PUBLIC_PARAGRAPH_BOUNDARIES_V1`;
- structured normalization boundary → `RULE_BODY_BOUNDARIES_COMPLETE_PARAGRAPH_ATOMIZATION_PENDING`;
- boundary state → `PASS_141_RULE_BOUNDARIES`;
- coverage status → `CORE_RULE_PARAGRAPH_BOUNDARY_EXTRACTION_V1_COMPLETE`;
- normative Core gap → `PARAGRAPH_BOUNDARIES_CLOSED_PARAGRAPH_ATOMIZATION_PENDING`.

No whole-faction promotion occurs.

## Tooling

- model: `docs/CORE_RULE_PARAGRAPH_BOUNDARY_MODEL.md`;
- schema: `schemas/core_rule_paragraph_boundaries.schema.json`;
- builder: `tools/build_core_rule_paragraph_boundaries.py`;
- tests: `tests/test_core_rule_paragraph_boundaries.py`;
- workflow: `.github/workflows/core-rule-paragraph-boundaries.yml`.

## Pre-PR validation evidence

- paragraph-boundary workflow run `36696663834` — **SUCCESS**;
- normative/app gap reproducibility run `36696967737` — **SUCCESS**;
- generic repository validator + full test suite run `36697099240` — **SUCCESS**.

Final PR-head validation is recorded in the recovery handoff before merge.

## Next milestone

`CORE_RULE_PARAGRAPH_ATOMIZATION_V1`

Scope:

1. turn all **310** paragraph-boundary candidates into stable paragraph identities;
2. preserve parent rule, occurrence, page/range and semantic-hash provenance;
3. distinguish repeated-occurrence paragraph variants without semantic guessing;
4. keep paragraph prose external;
5. leave semantic AST and interaction-graph modeling for later layers;
6. do not alter faction normative coverage or infer app/Codex-only semantics.
