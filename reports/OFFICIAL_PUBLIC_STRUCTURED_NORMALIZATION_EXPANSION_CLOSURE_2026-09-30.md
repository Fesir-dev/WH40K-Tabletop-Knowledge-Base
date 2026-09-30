# Official public structured normalization expansion v1 closure — 2026-09-30

## Result

**PASS — scoped public-official structured normalization expansion is closed.**

This milestone advanced the verified public Games Workshop evidence layer beyond document fingerprints and exact mirror overlap while preserving the authority boundary:

- Games Workshop remains normative;
- Wahapedia remains a current mirror/cross-check;
- no residual classification is promoted by inference;
- full Codex/app equivalence remains pending;
- whole-faction normative coverage remains unchanged.

Validated implementation head:

`a1c46b76eb186776559ac1dc91cc925abcf45a44`

## D1 — public Core Rules section structure

Generated evidence:

- model: `docs/OFFICIAL_CORE_RULES_STRUCTURE_MODEL.md`;
- schema: `schemas/core_rules_structure_snapshot.schema.json`;
- extractor: `tools/build_core_rules_structure.py`;
- compact report: `reports/CORE_RULES_STRUCTURE_CURRENT.json`;
- snapshot: `rules/11e/snapshots/2026-09-30/core_rules_structure/index.json`;
- workflow: `.github/workflows/core-rules-structured-normalization.yml`.

Source gate revalidates:

1. official Core Rules binary SHA-256;
2. all **88** page semantic fingerprints;
3. full document semantic SHA-256.

The native PDF bookmark tree was found to be structurally trivial. The extractor therefore fails over to a conservative short-heading map plus numbered rule-reference families.

### Core structure result

- pages verified / represented: **88 / 88**;
- sanitized flat page-heading anchors: **80**;
- numbered rule families: **24**;
- canonical family sequence: **01 → 24**;
- distinct detected numbered rule references: **141**;
- section-level family structure: **complete**;
- nested hierarchy: **not claimed complete**;
- paragraph-level rules AST: **pending**.

Family ranges use two concepts:

- **canonical anchor** = page with the highest density of distinct references from that family;
- **definition start** = nearby pre-anchor heading evidence within a bounded four-page window.

Distant cross-references therefore cannot move a section start backwards by dozens of pages.

## D2 — exact-but-unscoped residual classification

Input residual: **1,566** exact public-overlap units not eligible for the scoped structured snapshot.

Classification:

| Class | Units |
| --- | ---: |
| `CORE_PUBLIC_GLOBAL` | 21 |
| `EDITION_11_SOURCE_MATCH_OUTSIDE_OWN_PACK` | 426 |
| `FACTION_ONLY_MATCH_OUTSIDE_OWN_PACK` | 124 |
| `NON_11_OR_LEGENDS_SOURCE` | 995 |
| **Total** | **1,566** |

Important finding: most exact-but-unscoped units are not missing provenance suitable for automatic promotion. **995** belong to non-11 / Legends source identities whose wording is reused in current public material. Text reuse does not make the old source object current.

## D3 — no-exact-public-overlap classification

Input residual: **7,936** current-mirror semantic units with no exact match under the v1 public comparison contract.

Classification:

| Class | Units |
| --- | ---: |
| `EDITION_11_SOURCE_NO_EXACT_PUBLIC_OVERLAP` | 3,467 |
| `FACTION_ONLY_NO_EXACT_PUBLIC_OVERLAP` | 1,868 |
| `NON_11_OR_LEGENDS_SOURCE_NO_EXACT` | 227 |
| `NO_SOURCE_OR_FACTION_NO_EXACT` | 61 |
| `TOO_SHORT_FOR_SAFE_AUTO_MATCH` | 2,313 |
| **Total** | **7,936** |

Generated evidence:

- model: `docs/OFFICIAL_PUBLIC_OVERLAP_RESIDUAL_MODEL.md`;
- schema: `schemas/public_overlap_residual_classification.schema.json`;
- classifier: `tools/classify_public_overlap_residuals.py`;
- compact report: `reports/OFFICIAL_PUBLIC_OVERLAP_RESIDUAL_CLASSIFICATION_CURRENT.json`;
- full snapshot: `rules/11e/snapshots/2026-09-30/official_public_overlap/residual_classification.json`;
- workflow: `.github/workflows/public-overlap-residual-classification.yml`.

### Fail-closed interpretation

`NO_EXACT_PUBLIC_OVERLAP` is not a synonym for semantic drift.

Possible explanations remain deliberately unresolved where official evidence does not decide them, including:

- Codex/app-only wording outside public Faction Pack scope;
- extraction/layout differences;
- shared wording whose source scope is not safely attributable;
- genuine current wording difference requiring stronger official evidence.

Therefore residual classification creates:

- promoted semantic units: **0**;
- semantic conflicts: **0**.

## D4 — current-layer integration

Integrated:

- `rules/11e/current.json`
  - Core Rules currentness advanced to `OFFICIAL_PUBLIC_SECTION_STRUCTURE_V1`;
  - structured Core state: `PASS_RULE_REFERENCE_FAMILIES_01_24`;
  - milestone layer: `official_public_structured_normalization_expansion.state = PASS_SCOPED_EXPANSION_V1`;
  - next milestone: `CORE_RULE_REFERENCE_ATOMIZATION_V1`.
- `sources/currentness_gate.json`
  - Core section-level structure is recorded separately from paragraph AST completeness;
  - residual classification is explicitly non-promoting/non-conflicting.
- `coverage/current.json`
  - status: `OFFICIAL_PUBLIC_STRUCTURED_NORMALIZATION_EXPANSION_V1_COMPLETE`;
  - exact residual classes and Core structure metrics are recorded.
- `reports/NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT_CURRENT.json`
  - Core gap advanced to `SECTION_STRUCTURE_CLOSED_RULE_ATOMIZATION_PENDING`;
  - public supplement gap advanced to `EXACT_PUBLIC_OVERLAP_AND_RESIDUAL_CLASSIFICATION_CLOSED_DEEP_EXTRACTION_PENDING`;
  - full faction/app gap remains blocked/conditional on authorized evidence.
- repository validator and regression tests lock the new baseline.

## Authority boundary after closure

Still intentionally unchanged:

- `current_normalized_factions = 0`;
- `full_normative_semantic_factions = 0`;
- public Faction Packs remain supplemental rather than complete Codex replacements;
- app/Codex-only wording remains `PENDING/UNKNOWN`;
- nested Core hierarchy is not claimed complete;
- paragraph-level Core Rules AST is not claimed complete;
- Legends/non-11 exact text reuse never promotes old objects into current rules;
- no-exact residuals do not become `SOURCE_CONFLICT` without additional official evidence.

## Validation evidence

All critical workflows passed on the same implementation head `a1c46b76eb186776559ac1dc91cc925abcf45a44`:

- Validate knowledge base: run `36692560373` — **SUCCESS**;
- Normative/app equivalence gap audit: run `36692560396` — **SUCCESS**;
- Core Rules structured normalization: run `36692560392` — **SUCCESS**;
- Official public overlap residual classification: run `36692560385` — **SUCCESS**;
- Official public mirror overlap audit: run `36692560403` — **SUCCESS**.

The final overlap re-run confirms the expansion did not alter the closed C1–C4 exact-overlap evidence.

## Next milestone

`CORE_RULE_REFERENCE_ATOMIZATION_V1`

Scope:

1. turn the verified **141** detected numbered Core Rules references into stable per-rule structural identities;
2. bind each identity to official page/range hashes and family provenance;
3. keep paragraph prose external/copyright-safe;
4. distinguish safely atomizable references from layout/extraction ambiguities;
5. do not change faction normative coverage or infer Codex/app-only semantics.


## Merge evidence

- merged PR: **#10**;
- merge commit: `191b258a9a85fe71417f48c2fd74ee66afd30644`;
- validated final PR head: `cc1297b7472c835014c215ef5c5ca6a706a55d32`;
- final PR-head generic validation: `36692867757` — **SUCCESS**;
- final PR-head normative/app gap audit: `36692867724` — **SUCCESS**;
- final PR-head Core structure workflow: `36692867778` — **SUCCESS**;
- final PR-head residual classification: `36692867670` — **SUCCESS**;
- final PR-head overlap revalidation: `36692867854` — **SUCCESS**.

The merge therefore promotes the fully validated candidate without changing its authority boundaries.
