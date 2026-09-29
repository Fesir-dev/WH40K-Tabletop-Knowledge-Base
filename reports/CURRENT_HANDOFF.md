# CURRENT HANDOFF

Updated: **2026-09-29**

## Recovery authority

Canonical repository: `Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Latest validated release-transition activation-watch evidence:

- validated implementation head: `cdcb3e2e66635520c8670d60f8e762840e087d8c`
- activation-watch run: `36609958145` — **SUCCESS**
- release-readiness run: `36609957868` — **SUCCESS**
- generic repository validation run: `36609957783` — **SUCCESS**
- activation-watch checkpoint: `NO_ACTION_REQUIRED`
- auto-promotion / direct current mutation: **disabled**
- closure report: `reports/RELEASE_TRANSITION_ACTIVATION_WATCH_CLOSURE_2026-09-29.md`

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


### Release-transition ingestion readiness
**CLOSED AT OPERATIONAL V1**
- transition manifests: Space Marines 2026 + Adeptus Custodes 2026;
- evaluator: fail-closed state machine;
- explicit official activation-evidence recorder: active;
- daily/manual read-only readiness workflow: active;
- preview/preorder never promotes;
- release date alone never promotes;
- official current-legal evidence required;
- upstream projection change required before candidate generation;
- route after activation: guarded re-ingestion candidate → reviewed promotion PR;
- auto-promotion: **disabled**.

Checkpoint 2026-09-29:
- Space Marines: `PRE_RELEASE_HOLD`, scheduled release date **2026-10-03**, current-legal confirmation **false**;
- Adeptus Custodes: `UPCOMING_HOLD_NO_RELEASE_DATE`, retail/current-legal release date **UNKNOWN**, current-legal confirmation **false**;
- no future rules promoted.


### Release-transition activation watch
**CLOSED AT OPERATIONAL READ-ONLY V1**
- cadence: **every 6 hours**;
- current checkpoint: `NO_ACTION_REQUIRED`;
- Space Marines: `NO_ACTION → WAIT_PRE_RELEASE`;
- Adeptus Custodes: `NO_ACTION → WAIT_OFFICIAL_RELEASE_SIGNAL`;
- actionable future states: `ACTION_REQUIRED`, `MONITORING_UPSTREAM_PROJECTION`, `READY_FOR_GUARDED_CANDIDATE`;
- unknown states fail closed to `ACTION_REQUIRED`;
- GitHub warnings/step summary: active;
- repository mutation permissions: none;
- direct promotion eligibility: always false;
- candidate-ready state only authorizes the existing guarded candidate route.

The watch remains operational while other development continues.

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

`NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT`

High-level remaining work:

1. inventory the exact normative/app gaps that keep `current_normalized_factions = 0`;
2. separate app-only wording, unavailable official text, mirror-to-official equivalence, and genuinely unresolved rules dimensions;
3. define which gaps can be closed with current repository capabilities and which must remain explicit UNKNOWN;
4. release-transition watch continues in parallel and must not be restarted or bypassed.

## Execution reliability rule

- decompose substantial work into 2–4 durable milestones where practical: recovery → audit/design → implementation → validation/closure;
- commit/handoff after serious phases; never leave the only copy of progress in an unfinished response;
- High may be replaced by Medium as a practical fallback if a long High run is producing no durable intermediate result; this is not guaranteed to fix transport/runtime failures;
- on `Stream cache expired`, do not refresh-loop expecting that response stream to recover; resume from the latest validated GitHub state.

## Resume rule

Do not restart preservation, Wave A, Wave B, semantic/FAQ audits, upstream watcher, New Recruit runtime validation, the Custodes collection solver v1, guarded reingestion/promotion v1, release-transition readiness v1, or activation-watch v1 after a chat/UI failure.

Resume from the latest validated Git HEAD and this active milestone.
