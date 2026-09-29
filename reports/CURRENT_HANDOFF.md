# CURRENT HANDOFF

Updated: **2026-09-29**

## Recovery authority

Canonical repository: `Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Last verified milestone HEAD:

`2f737eb5291e8e37aa6bd4706d408a9d921725f2`

Validation run:

- GitHub Actions: `36585942055`
- result: **SUCCESS**

## Completed major layers

### Repository/governance
- explicit authority/freshness/conflict/provenance model;
- 37 roster identities;
- scoped currentness vs repository coverage;
- CI + repository contract tests;
- resilient long-run execution/handoff protocol.

### Wave A — MFM
**CLOSED**

- MFM 1.4 / official update 2026-09-02;
- 30 MFM faction pages;
- 36 MFM-mapped roster identities;
- points, unit sizes, copy-tier pricing, Leader/Support relations, DP, Force Dispositions, enhancement/wargear costs and Legends pricing.

### Wave B — structural
**CLOSED**

- Wahapedia current-mirror structural views: **35 / 37**;
- BSData structured-implementation fallbacks: **2 / 37**;
- total structural source availability: **37 / 37**;
- retained MFM/Wahapedia conflicts: **11**.

### Wave B — semantic / FAQ operational currentness
**CLOSED**

- full semantic fingerprint audit: **16,506 / 16,506 MATCH**;
- semantic drift/missing: **0**;
- live 11E source-catalog drift: **0**;
- edition-11 sources indexed: **29**;
- official faction-pack PDFs verified: **28 / 28**;
- failed official assets: **0**;
- on-demand hash-verified semantic resolver: active;
- fast semantic smoke + full semantic audit workflows: active.

Authority boundary:

- Games Workshop remains normative;
- Wahapedia semantic mirror currentness is verified, not promoted over GW;
- app-only wording remains unresolved;
- mirror-to-official paragraph-level equivalence is not claimed;
- `current_normalized_factions = 0` remains intentional for full normative normalization.

### Painting
- workbook v25 preserved;
- 217 containers/materials;
- 212 unique products;
- 540 recipes;
- active Demon Prince project normalized;
- painting plugin skill active.

### Analytics
- lineage-aware competitive source matrix;
- raw events / aggregators / list meta / mathhammer / expert evidence separated;
- roster recommendation evidence model active.

## Current active milestone

`AUTOMATED_DIFF_AND_NEW_RECRUIT_RUNTIME`

High-level remaining work:

1. automated GW ↔ Wahapedia ↔ BSData revision/diff workers;
2. New Recruit runtime/projection validation;
3. collection-aware roster legality/physical-feasibility solver;
4. upcoming Space Marines/Custodes release-transition ingestion when legally current;
5. optional deeper normative/app equivalence work where official/app access permits.

## Resume rule

Do not restart preservation, Wave A, Wave B structural, or Wave B semantic/FAQ audits after a chat/UI failure.

Resume from the latest validated Git HEAD and the active milestone above.
