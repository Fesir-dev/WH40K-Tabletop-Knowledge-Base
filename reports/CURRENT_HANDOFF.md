# CURRENT HANDOFF

Updated: **2026-09-29**

## Recovery authority

Canonical repository: `Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Latest validated runtime-monitor milestone evidence:

- runtime workflow run: `36591100159`
- result: **SUCCESS**
- generated runtime report commit: `4ff07c7c5aeba03d18cd7c0abb8a84c1602824f1`

## Completed major layers

### Repository/governance
- authority/freshness/conflict/provenance model;
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
- official faction-pack PDFs verified: **28 / 28**;
- hash-verified semantic resolver active.

### Automated diff / upstream monitoring
**CLOSED AS MONITORING LAYER**
- BSData head watcher: active;
- MFM-extractor head watcher: active;
- 20 Wahapedia CSV hash watcher: active;
- current upstream state: **NO_CHANGE**;
- auto-promotion: **disabled by design**.

### New Recruit runtime projection
**CLOSED AS VALIDATION LAYER**
- roster identities resolved: **37 / 37**;
- representative MFM point checks: **10**;
- matches: **9**;
- known runtime drifts: **1**;
- new runtime drifts: **0**;
- workflow result: **PASS_WITH_KNOWN_RUNTIME_DRIFT**.

Known drift:
- Ghazghkull Thraka: MFM/Wahapedia **300**, New Recruit **235**;
- classified as `KNOWN_RUNTIME_PROJECTION_DRIFT`;
- normative resolution remains MFM **300**.

### Painting
- workbook v25 preserved;
- 217 containers/materials;
- 212 unique products;
- 540 recipes;
- active Demon Prince project normalized;
- painting plugin skill active.

### Analytics
- lineage-aware source matrix;
- tournament/meta/mathhammer/expert layers separated;
- roster recommendation evidence model active.

## Authority boundary

- Games Workshop remains normative.
- Wahapedia remains current readable mirror.
- BSData remains structured implementation.
- New Recruit remains runtime projection.
- Known runtime drift never rewrites normative data.
- app-only wording and full mirror-to-official semantic equivalence remain unresolved.
- `current_normalized_factions = 0` remains intentional for full normative normalization.

## Current active milestone

`COLLECTION_AWARE_ROSTER_SOLVER`

High-level remaining work:

1. collection-aware roster legality + physical-feasibility solver;
2. automated re-ingestion/reconciliation/promotion when upstream watcher detects change;
3. upcoming Space Marines/Custodes release-transition ingestion when legally current;
4. optional deeper normative/app equivalence where official/app access permits.

## Resume rule

Do not restart preservation, Wave A, Wave B, semantic/FAQ audits, upstream watcher, or New Recruit runtime validation after a chat/UI failure.

Resume from the latest validated Git HEAD and this active milestone.
