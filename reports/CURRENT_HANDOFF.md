# CURRENT HANDOFF

Updated: **2026-09-29**

## Recovery authority

Canonical repository: `Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Latest validated runtime-monitor hardening evidence:

- validated branch head: `ecb6e756624dacb09c889e56d110dcfd1498ba95`
- GitHub Actions validation run: `36596361579`
- result: **SUCCESS**
- runtime report: `reports/NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json` schema **2.0**
- runtime report state: **PASS_WITH_KNOWN_RUNTIME_DRIFT**

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
**CLOSED AS VALIDATION LAYER — LINEAGE HARDENED**
- roster identities resolved: **37 / 37**;
- representative point checks: **15**;
- point matches: **10**;
- classified known point drifts: **5**;
- representative structural surface checks: **5**;
- structural matches: **4**;
- classified known structural drifts: **1**;
- new/unclassified runtime drifts: **0**;
- report schema: **2.0**;
- workflow result: **PASS_WITH_KNOWN_RUNTIME_DRIFT**.

Exact Ghazghkull chain:
- GW/MFM **300**;
- Wahapedia **300**;
- pinned BSData `951d590...` **300**;
- live BSData HEAD **300**;
- New Recruit **235**;
- classification: `RUNTIME_PROJECTION_DRIFT`;
- normative KB change required: **false**.

Additional sampled runtime projection drift:
- Orks Boyz **90 → 75**;
- Orks Battlewagon **150 → 145**;
- Orks Warboss **100 → 85**;
- Necron Warriors **85 → 80**;
- current Orks `Shoota Boyz` detachment present in MFM/Wahapedia/pinned+live BSData but absent from sampled New Recruit selector.

Exact New Recruit synchronization cadence remains `UNKNOWN_NOT_INFERRED`.

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
- Runtime drift never rewrites normative data; registry state is separate from the base drift classification.
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
