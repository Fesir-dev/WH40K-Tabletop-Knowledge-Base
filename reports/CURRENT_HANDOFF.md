# CURRENT HANDOFF

Updated: **2026-09-29**

## Recovery authority

Canonical repository: `Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Last verified HEAD before this handoff update:

`deeae1387a2e32cc6cf6165308fd8833e925e0a3`

Validation run:

- GitHub Actions: `36579692566`
- result: **SUCCESS**

## Completed major layers

### Repository/governance
- source authority, freshness, conflicts and provenance;
- scoped currentness vs repository coverage;
- 37 roster identities;
- CI and repository contract tests;
- release-transition tracking.

### Wave A — MFM
**CLOSED**

- MFM 1.4;
- official update 2026-09-02;
- 30 MFM faction pages;
- 36 roster identities with MFM coverage;
- points, unit sizes, Leader/Support relations, DP, Force Dispositions, enhancement/wargear costs and Legends pricing.

### Wave B — structural
**CLOSED STRUCTURALLY / SEMANTICS STILL PENDING**

Current machine state:

- Wahapedia current-mirror structural views: **35 / 37**;
- BSData structured-implementation fallbacks: **2 / 37**;
- total structural source availability: **37 / 37**;
- retained MFM/Wahapedia source conflicts: **11**;
- semantic resolver: **LIVE_HASH_VERIFIED**;
- semantic smoke workflow: **SUCCESS**.

Important boundary:

- `current_normalized_factions = 0` remains intentional;
- long rule semantics and FAQ/errata are not yet promoted as fully normalized current data.

### Painting
- workbook v25 preserved;
- normalized painting inventory, 540 recipes and active project state;
- painting plugin skill active.

### Analytics
- source lineage matrix;
- roster recommendation evidence model;
- meta/analytics sources separated from normative rules.

## Current active milestone

`WAVE_B_SEMANTIC_AND_FAQ_CURRENTNESS`

Remaining high-level work:

1. complete semantic rules/FAQ currentness without vendoring long copyrighted prose;
2. finish automated GW ↔ Wahapedia ↔ BSData normalization/diff workers;
3. add New Recruit runtime projection validation;
4. build collection-aware roster legality/physical-feasibility solver;
5. handle upcoming Space Marines/Custodes release transitions when they become legally current.

## Resume rule

If a chat or stream fails, do **not** restart Wave A or Wave B structural ingestion.

Resume from the current repository HEAD and the active milestone above.
