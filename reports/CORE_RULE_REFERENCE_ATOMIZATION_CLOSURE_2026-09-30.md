# Core rule-reference atomization v1 closure — 2026-09-30

## Result

**PASS — all 141 numbered public Core Rules references have stable, verified structural identities.**

This milestone advances the official public Core Rules layer from family-level structure to per-reference identities while preserving the copyright and authority boundaries.

## Source gate

Normative source: verified public Games Workshop 11E Core Rules PDF.

Before atomization the pipeline revalidates:

- Core Rules binary SHA-256;
- all **88 / 88** committed page semantic fingerprints;
- complete document semantic SHA-256;
- parent Core structure snapshot;
- canonical family set **01–24**;
- parent numbered reference count **141**.

Source verification result: **PASS**.

## Atomization result

Generated snapshot:

`rules/11e/snapshots/2026-09-30/core_rule_atoms/index.json`

Compact report:

`reports/CORE_RULE_REFERENCE_ATOMIZATION_CURRENT.json`

Result:

- atoms: **141 / 141**;
- unique `rule_ref` identities: **141**;
- unique stable `rule_key` identities: **141**;
- families: **24** (`01–24`);
- `UNIQUE_IN_FAMILY_HEADING`: **136**;
- `REPEATED_IN_FAMILY_HEADING`: **5**;
- `MULTIPLE_LABELS_SAME_PAGE`: **0**;
- `HEADING_RECOVERY_GAP`: **0**;
- atoms with cross-reference pages outside their family range: **40**;
- every atom has in-family heading evidence.

## Repeated heading evidence

Exactly five references have repeated valid in-family headings:

- `15.07` — Rapid Ingress;
- `15.08` — Fire Overwatch;
- `15.09` — Snap Shooting;
- `15.10` — Smokescreen;
- `15.11` — Heroic Intervention.

For each, the verified PDF exposes heading evidence on pages **55** and **57**.

These are preserved as repeated structural occurrences. The atomizer does not collapse them into a claim that the surrounding page prose is semantically identical.

## Stable atom identity

Each atom stores only structural evidence:

- official numbered reference;
- stable repository key;
- family identity and family page range;
- family-range hash;
- short in-family heading labels (bounded to 160 characters) and label hashes;
- verified page semantic hashes;
- primary navigation page;
- cross-reference pages outside the parent family.

Stable identity is based on the official numbered reference, not on extracted prose.

## Copyright boundary

Committed atomization data does **not** contain paragraph rule prose.

Allowed committed content remains limited to:

- numbered IDs;
- bounded short headings;
- page numbers/ranges;
- hashes;
- structural classifications and relationships.

Paragraph text is used transiently only for source verification and reference occurrence detection.

## Authority boundary

This milestone establishes per-reference Core Rules structure. It does **not** establish:

- paragraph/rule-body boundary completeness;
- paragraph-level rules AST completeness;
- rule-interaction graph completeness;
- full Codex/app equivalence;
- complete faction normative semantics;
- any whole-faction promotion.

Therefore:

- `current_normalized_factions = 0` remains intentional;
- `full_normative_semantic_factions = 0` remains intentional;
- app/Codex-only wording remains `PENDING/UNKNOWN`.

## Current-layer integration

The candidate advances:

- Core currentness → `OFFICIAL_PUBLIC_RULE_REFERENCE_ATOMIZATION_V1`;
- structured normalization boundary → `RULE_REFERENCE_IDENTITY_COMPLETE_PARAGRAPH_BOUNDARIES_PENDING`;
- atomization state → `PASS_141_RULE_ATOMS`;
- coverage status → `CORE_RULE_REFERENCE_ATOMIZATION_V1_COMPLETE`;
- normative Core gap → `RULE_REFERENCE_ATOMIZATION_CLOSED_PARAGRAPH_BOUNDARIES_PENDING`.

The faction normative counters remain unchanged.

## Tooling

- model: `docs/CORE_RULE_REFERENCE_ATOMIZATION_MODEL.md`;
- schema: `schemas/core_rule_reference_index.schema.json`;
- builder: `tools/build_core_rule_reference_atoms.py`;
- tests: `tests/test_core_rule_reference_atomization.py`;
- workflow: `.github/workflows/core-rule-reference-atomization.yml`.

The workflow also provides scheduled source revalidation and committed-output reproducibility.

## Pre-PR validation evidence

- atomization workflow run `36694945932` — **SUCCESS**;
- normative/app gap reproducibility run `36695667215` — **SUCCESS**;
- repository validator + full test suite run `36695740466` — **SUCCESS**.

Final PR-head validation:

- PR: **#13**;
- validated PR head: `a953b2640600a330c0a00e9f5e2aecb6f0b146d8`;
- merge commit: `ca30daaf0ced6b305e7e4d10b6b0716ab49cea92`;
- generic repository validation: `36695977658` — **SUCCESS**;
- normative/app gap reproducibility: `36695977608` — **SUCCESS**;
- Core atomization revalidation: `36695977620` — **SUCCESS**;
- official-public overlap regression: `36695977631` — **SUCCESS**.

## Next milestone

`CORE_RULE_PARAGRAPH_BOUNDARY_EXTRACTION_V1`

Scope:

1. derive deterministic body/paragraph boundaries for each of the **141** stable rule atoms;
2. bind each boundary to verified page/range hashes and atom provenance;
3. use official page prose transiently, while committing offsets/ranges/hashes and structural metadata rather than long prose;
4. fail closed on layout ambiguity;
5. keep paragraph AST and rule-interaction modeling separate later layers;
6. do not change faction normative coverage or infer Codex/app-only semantics.
