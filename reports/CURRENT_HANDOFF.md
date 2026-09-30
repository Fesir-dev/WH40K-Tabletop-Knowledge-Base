# CURRENT HANDOFF

Updated: **2026-09-29**

## Recovery authority

Canonical repository: `Fesir-dev/WH40K-Tabletop-Knowledge-Base@main`

Latest closed official-public ↔ mirror overlap milestone:

- merged PR: **#9**;
- merge commit: `a933e69856753d4a97b1537d77eb599c7b2b6dbd`;
- validated PR head: `aadd558093a25bbd56e54724ff97624aeca4f0ca`;
- final generic repository validation: `36688560039` — **SUCCESS**;
- final normative/app gap reproducibility: `36688560359` — **SUCCESS**;
- final full official-public mirror overlap audit: `36688560258` — **SUCCESS**;
- structured exact scoped official-public units: **4,070**;
- next milestone: `OFFICIAL_PUBLIC_STRUCTURED_NORMALIZATION_EXPANSION`.


Latest validated official-public fingerprint evidence:

- merged milestone commit: `1eaa07e137c72ebc5087c3306a3eaa0752356c80`
- validated PR head: `d265ec44b70a62384ffb1d36af987d0aaa7aa8ee`
- official fingerprint reproducibility run: `36616297652` — **SUCCESS**
- normative/app gap projection run: `36616297679` — **SUCCESS**
- generic repository validation run: `36616297669` — **SUCCESS**
- official public corpus: **29 / 29 PASS**
- Core Rules: **1 / 1**, 88 pages
- public Faction Packs: **28 / 28**, all binary SHAs match prior official-asset evidence
- total pages: **1,430**
- normalized fingerprinted text: **1,915,296 characters**
- strict normative faction promotion: **none**
- closure report: `reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CLOSURE_2026-09-29.md`

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


### Normative/app equivalence gap audit
**CLOSED AS CLASSIFICATION LAYER**
- `current_normalized_factions = 0`: intentional normative threshold;
- public 11E Core Rules: official source discovered, ingestion pending;
- public 11E Faction Pack PDFs: **28 / 28** verified;
- faction-pack role: supplemental to Codex, not full Codex replacement;
- Wahapedia semantic mirror: **16,506 / 16,506** current hash matches, secondary only;
- full normative semantic factions: **0**;
- source→roster mapping: **25 direct + 3 alias candidates + 7 parent candidates + 2 no-pack mappings**;
- GW App wording: `BLOCKED_ON_AUTHORIZED_APP_EVIDENCE`;
- mirror→official full equivalence: not claimed;
- recommended public next step: official Core/Faction-Pack semantic fingerprint pipeline.

Authority boundary remains unchanged: public official overlap can be normalized, but missing Codex/app-only text cannot be inferred from Wahapedia, BSData or New Recruit.


### Official public rules semantic fingerprints
**CLOSED AS OPERATIONAL OFFICIAL EVIDENCE LAYER**
- Games Workshop public documents fingerprinted: **29 / 29 PASS**;
- Core Rules: **1**, binary SHA `f6a2443a...276833`, semantic SHA `c8b98076...107fe7`;
- Faction Packs: **28 / 28**, every binary SHA matches prior verified official asset evidence;
- pages: **1,430**;
- normalized text characters: **1,915,296**;
- extraction failures: **0**;
- extraction engine: `pypdf 5.9.0`;
- normalization: `OFFICIAL_TEXT_NFKC_WS_V1`;
- stored content: hashes/counts/classes only; no long GW rules prose;
- daily reproducibility/drift workflow: active;
- Core Rules state: `OFFICIAL_PUBLIC_SEMANTIC_FINGERPRINTED_NOT_STRUCTURED`;
- public faction supplement state: `OFFICIAL_PUBLIC_SUPPLEMENTS_FINGERPRINTED_FULL_CODEX_PENDING`;
- `current_normalized_factions = 0` remains intentional;
- full Codex/app equivalence remains `PENDING`.

The current normative gap projection now records Core/Faction-Pack fingerprint evidence as closed while structured official normalization and public official ↔ mirror overlap remain pending.

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

## Latest closed milestone

`OFFICIAL_PUBLIC_RULES_MIRROR_OVERLAP_AUDIT` — **CLOSED 2026-09-30**

### C1 — comparison contract
**CLOSED**
- model: `docs/OFFICIAL_PUBLIC_MIRROR_OVERLAP_MODEL.md`;
- exact-match and provenance-scoping policy is explicit;
- no full Codex/app inference.

### C2 — executable overlap audit
**CLOSED**
- tool: `tools/audit_official_public_mirror_overlap.py`;
- official public corpus verified: **29 / 29**;
- mirror semantic units audited: **13,572**;
- exact public overlap: **5,636**;
- exact-but-unscoped evidence: **1,566**;
- no exact public overlap: **7,936**;
- transient Wahapedia fetches use bounded retry/backoff and remain hash-gated.

### C3 — structured official-public normalization
**CLOSED AT EXACT PUBLIC OVERLAP V1**
- structured snapshot: `rules/11e/snapshots/2026-09-30/official_public_overlap/index.json`;
- promotable exact source/faction-scoped units: **4,070**;
- no long official/mirror rules prose vendored;
- `current_normalized_factions = 0` unchanged;
- `full_normative_semantic_factions = 0` unchanged.

### C4 — validation / current integration
**CLOSED**
- current rules pointer/state: active;
- currentness scope: active;
- coverage metrics: active;
- repository validator + contract tests: active;
- closure: `reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_CLOSURE_2026-09-30.md`;
- compact recovery summary: `reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_SUMMARY_CURRENT.json`.

Validated implementation checkpoints:
- overlap workflow run `36688272008` — **SUCCESS**;
- normative/app audit run `36688416703` — **SUCCESS**;
- generic repository validation run `36688416705` — **SUCCESS**.

Authority boundary remains:
- public exact overlap proves only the matched semantic object;
- Faction Packs remain supplemental, not full Codex replacements;
- app/Codex-only wording remains `PENDING/UNKNOWN`;
- `NO_EXACT_PUBLIC_OVERLAP` is not automatically a conflict or drift.

## Current active milestone

`OFFICIAL_PUBLIC_STRUCTURED_NORMALIZATION_EXPANSION`

Next unresolved work:

1. build section-level structured normalization for the public Core Rules;
2. review **1,566** exact-but-unscoped units and strengthen provenance where evidence supports it;
3. classify **7,936** no-exact-public-overlap units into short/extraction cases, public-scope absence and likely Codex/app-only scope without assuming disagreement;
4. keep app/Codex-only semantics fail-closed until authorized versioned evidence exists;
5. release-transition activation watch continues independently.

## Execution reliability rule

- decompose substantial work into 2–4 durable milestones where practical: recovery → audit/design → implementation → validation/closure;
- commit/handoff after serious phases; never leave the only copy of progress in an unfinished response;
- High may be replaced by Medium as a practical fallback if a long High run is producing no durable intermediate result; this is not guaranteed to fix transport/runtime failures;
- on `Stream cache expired`, do not refresh-loop expecting that response stream to recover; resume from the latest validated GitHub state.

## Resume rule

Do not restart preservation, Wave A, Wave B, semantic/FAQ audits, upstream watcher, New Recruit runtime validation, the Custodes collection solver v1, guarded reingestion/promotion v1, release-transition readiness v1, activation-watch v1, the normative/app gap audit, or the official-public fingerprint pipeline after a chat/UI failure.

Resume from the latest validated Git HEAD and this active milestone.
