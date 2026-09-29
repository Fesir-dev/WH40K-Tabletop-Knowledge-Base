# CURRENT HANDOFF

Updated: **2026-09-29**

## Recovery authority

Canonical repository: `Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Latest validated guarded-reingestion milestone evidence:

- merged milestone commit: `f9d3a5c462e06bf809307a329c50b54de9e66561`
- validated PR head: `d00d9a66213a6d58698d2da3d9108d18e6b2a70a`
- generic repository validation run: `36604067969` — **SUCCESS**
- upstream reingestion candidate run: `36604068116` — **SUCCESS**
- synthetic candidate path: **PASS**
- reviewed promotion safety tests: **PASS**
- auto-promotion: **disabled**
- closure report: `reports/AUTOMATED_REINGESTION_PROMOTION_CLOSURE_2026-09-29.md`

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


### Guarded automated re-ingestion / reconciliation / promotion
**CLOSED AT OPERATIONAL V1**
- upstream watcher → deterministic reingestion planner: active;
- candidate execution: isolated workspace + reviewable artifact;
- Wahapedia candidate ingestion/reconciliation/roster-view/semantic stages: active;
- BSData implementation candidate reconciliation/fallback rebuild: active;
- Wahapedia Source.csv drift triggers official GW asset verification;
- BSData MFM extraction drift is a blocking official-authority gate;
- reviewed promotion requires exact workflow run ID + plan ID + explicit confirmation;
- promotion applies only to a new branch and opens a PR;
- post-apply upstream recheck: required;
- New Recruit runtime revalidation: required;
- semantic smoke + repository validation + unit tests: required;
- `auto_promote=false` is invariant;
- no real upstream revision was promoted during closure because watcher state is currently **NO_CHANGE**.

Current-promotion consumers are pointer-aware:
- semantic resolver follows current Wahapedia snapshot;
- watcher follows current Wahapedia/registry baselines;
- New Recruit validator follows current MFM/Wahapedia/BSData revisions;
- repository validation distinguishes immutable bootstrap regression from mutable current projection.

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


### Collection-aware roster solver
**CLOSED AT OPERATIONAL V1 FOR ADEPTUS CUSTODES**
- current MFM-backed scoped legality: active;
- solver-ready physical profile: `collection/adeptus_custodes/solver_profile.json`;
- physical bodies modeled: **70** Custodes/Sisters across **15** pools;
- shared-body allocation: active;
- ready vs build-required bodies: active;
- explicit conversion gating: active;
- declared component-capacity checks: active;
- fail-closed unknown component constraints: active;
- smoke/regression cases: **7**;
- solver validation report: **PASS**;
- full normative army legality remains `UNKNOWN_PENDING_NORMATIVE_APP`;
- personal collection remains `PROVISIONAL`.

Validated pre-closure code checkpoint:
- generic repository CI run: `36599092439` — **SUCCESS**;
- collection solver workflow run: `36599092522` — **SUCCESS**.

Closure report:
`reports/COLLECTION_AWARE_ROSTER_SOLVER_CLOSURE_2026-09-29.md`

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

`RELEASE_TRANSITION_INGESTION_READINESS`

High-level remaining work:

1. prepare release-transition ingestion for the Space Marines ecosystem scheduled for 2026-10-03 without replacing current legal data early;
2. preserve Adeptus Custodes preview/preorder material as upcoming-only until legally current, then route it through candidate → reconciliation → reviewed promotion;
3. optional deeper normative/app equivalence where official/app access permits;
4. extend collection-aware solver profiles when additional personal faction inventories are normalized.

## Execution reliability rule

- decompose substantial work into 2–4 durable milestones where practical: recovery → audit/design → implementation → validation/closure;
- commit/handoff after serious phases; never leave the only copy of progress in an unfinished response;
- High may be replaced by Medium as a practical fallback if a long High run is producing no durable intermediate result; this is not guaranteed to fix transport/runtime failures;
- on `Stream cache expired`, do not refresh-loop expecting that response stream to recover; resume from the latest validated GitHub state.

## Resume rule

Do not restart preservation, Wave A, Wave B, semantic/FAQ audits, upstream watcher, New Recruit runtime validation, the Custodes collection solver v1, or guarded reingestion/promotion v1 after a chat/UI failure.

Resume from the latest validated Git HEAD and this active milestone.
