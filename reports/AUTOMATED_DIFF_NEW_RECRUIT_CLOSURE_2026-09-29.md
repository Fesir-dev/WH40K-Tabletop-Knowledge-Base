# Automated diff + New Recruit runtime milestone closure — 2026-09-29

## Result

**PASS — monitoring milestone complete and lineage-hardened**

This layer remains closed operationally. The 2026-09-29 hardening pass does not reopen Wave A or Wave B and does not move the active milestone backwards. It strengthens mismatch classification and runtime sampling after recovery from the actual Git/CI state.

## Upstream revision/hash watcher

Current report:

`reports/UPSTREAM_CHANGE_WATCH_CURRENT.json`

State: **NO_CHANGE**

Verified baseline:

- `BSData/wh40k-11e` pinned/live: `951d5900d1b4a952a4ba560a30c43788e622ccfc`
- `BSData/wh40k-11e-mfm` pinned/live: `61a687e858c00a4ad205d564959c622a5605ef3d`
- Wahapedia snapshot files checked: **20**
- changed Wahapedia files: **0**
- Wahapedia `Last_update.csv` drift: **false**

Workflow:

`.github/workflows/upstream-change-watch.yml`

Cadence: every 6 hours.

Policy: an upstream revision/hash change is classified and blocks the baseline until ingestion/reconciliation/promotion is performed. Automatic normative promotion remains forbidden.

## New Recruit runtime projection validator

Current report:

`reports/NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json`

Current report schema: **2.0**

Runtime state:

- system page: HTTP 200
- catalogues reported: **36**
- libraries reported: **11**
- roster identities resolved: **37 / 37**
- missing identities: **0**
- catalogue/page failures: **0**
- representative point checks: **15**
- point matches: **10**
- classified known point drifts: **5**
- new/unclassified point drifts: **0**
- representative structural surface checks: **5**
- structural matches: **4**
- classified known structural drifts: **1**
- new/unclassified structural drifts: **0**
- overall: **PASS_WITH_KNOWN_RUNTIME_DRIFT**

The point sample now covers named characters, infantry, vehicles/monsters, a Leader and multi-size units. Structural probes cover selected detachment existence, Leader/bodyguard relation, enhancement presence, wargear presence and constraint behavior.

## Classification contract

Mismatch classification is separate from registry state.

Allowed base classifications:

- `NORMATIVE_MATCH`
- `IMPLEMENTATION_DRIFT`
- `RUNTIME_PROJECTION_DRIFT`
- `UPSTREAM_REVISION_DRIFT`
- `UNKNOWN_RUNTIME_DRIFT`

A known registered mismatch keeps its base classification and additionally receives registry state `KNOWN_ACTIVE`.

Every classified point mismatch stores:

- GW/MFM value;
- Wahapedia value;
- pinned BSData value;
- live BSData value;
- New Recruit runtime value;
- source revisions;
- classification;
- recommended action;
- `normative_kb_change_required`.

Runtime mismatches never automatically rewrite normative data.

## Exact Ghazghkull lineage

Active record:

`NR_ORKS_GHAZGHKULL_POINTS_2026_09_29`

Observed chain:

| Layer | Value |
| --- | ---: |
| GW/MFM 1.4 | **300 pts** |
| Wahapedia current mirror | **300 pts** |
| pinned `BSData/wh40k-11e@951d590...` | **300 pts** |
| live `BSData/wh40k-11e` HEAD | **300 pts** |
| New Recruit runtime/wiki | **235 pts** |

Classification:

`RUNTIME_PROJECTION_DRIFT`

Recommended action:

Investigate New Recruit projection/cache synchronization. **No normative KB change is required.**

Exact New Recruit synchronization cadence remains:

`UNKNOWN_NOT_INFERRED`

### Correction of earlier evidence

The earlier closure text attributed the `235 → 175` hunk in BSData commit
`5ca1013537f539995acdac2caafb93c879163f00` to Ghazghkull Thraka.

That attribution is withdrawn. The hunk alone did not identify Ghazghkull and therefore was not valid Ghaz-specific lineage evidence. The hardened validator now extracts the exact Ghazghkull value from pinned and live BSData directly; both are **300**.

## Additional classified runtime drift discovered by stronger sampling

The stronger representative sample exposed four additional point mismatches where current MFM, current Wahapedia and pinned/live BSData agree while New Recruit differs:

| Unit | MFM / Wahapedia / pinned+live BSData | New Recruit | Classification |
| --- | ---: | ---: | --- |
| Boyz | 90 | 75 | `RUNTIME_PROJECTION_DRIFT` |
| Battlewagon | 150 | 145 | `RUNTIME_PROJECTION_DRIFT` |
| Warboss | 100 | 85 | `RUNTIME_PROJECTION_DRIFT` |
| Necron Warriors | 85 | 80 | `RUNTIME_PROJECTION_DRIFT` |

These are retained as runtime evidence only. They do not change normative points.

## Structural projection sampling

Selected runtime checks:

- Warboss → BOYZ / BREAKA BOYZ / NOBZ Leader-bodyguard relation: **MATCH**
- Targetin' Gizmos enhancement presence: **MATCH**
- Battlewagon Wreckin' ball + Grabbin' klaw presence: **MATCH**
- Boyz `max(force): 6` constraint marker: **MATCH**
- current Orks `Shoota Boyz` detachment: **RUNTIME_PROJECTION_DRIFT**

For `Shoota Boyz`:

- current MFM: present;
- current Wahapedia snapshot: present;
- pinned BSData: present;
- live BSData: present;
- sampled New Recruit Orks detachment selector: absent.

Registry record:

`NR_ORKS_SHOOTA_BOYZ_DETACHMENT_2026_09_29`

## Monitoring behavior

- exact registered known drift → report it, workflow remains green;
- new/unclassified drift → workflow fails;
- changed known-drift value/classification → workflow fails;
- missing catalogue/page → workflow fails;
- known drift disappears → report `RESOLVED_CANDIDATE` for registry review;
- full five-source lineage is fetched for point mismatches rather than for every matching sample, keeping runtime cost bounded;
- runtime values never overwrite normative rules.

## Active milestone

The active milestone remains:

`COLLECTION_AWARE_ROSTER_SOLVER`

The separate automation gap also remains automated re-ingestion/reconciliation/promotion after an upstream change. This hardening pass does not change that roadmap.
