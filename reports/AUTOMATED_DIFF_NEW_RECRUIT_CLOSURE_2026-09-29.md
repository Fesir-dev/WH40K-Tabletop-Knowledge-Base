# Automated diff + New Recruit runtime milestone closure — 2026-09-29

## Result

**PASS — monitoring milestone complete**

This milestone establishes continuous change detection and runtime-projection validation. It deliberately does **not** auto-promote changed upstream data.

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

Policy: any upstream revision/hash change persists a classified report and fails the watcher. Re-ingestion, reconciliation and promotion are required; automatic rule promotion is forbidden.

## New Recruit runtime projection validator

Current report:

`reports/NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json`

Workflow run: `36591100159`

Result: **SUCCESS**

Runtime state:

- system page: HTTP 200
- catalogues reported: **36**
- expected roster identities: **37**
- resolved identities: **37 / 37**
- missing identities: **0**
- page failures: **0**
- representative point checks: **10**
- matches: **9**
- known drifts: **1**
- new drifts: **0**

The validator now reads expected points from the canonical repository MFM snapshot rather than hardcoding them.

## Classified runtime drift

Registry:

`sources/runtime_drift_registry.json`

Active record:

`NR_ORKS_GHAZGHKULL_POINTS_2026_09_29`

Observed chain:

- official/current MFM: **Ghazghkull Thraka = 300 pts**
- current Wahapedia mirror: **300 pts**
- New Recruit runtime/wiki: **235 pts**
- BSData historical upstream evidence: commit `5ca1013537f539995acdac2caafb93c879163f00` on 2026-09-05 changed Ghazghkull root points from **235 → 175**

Classification:

`KNOWN_RUNTIME_PROJECTION_DRIFT`

The New Recruit value matches the pre-change BSData value and is evidence of a stale/lagging runtime projection relative to at least that known upstream mutation. We do not infer New Recruit's undocumented synchronization cadence and do not assert an unverified exact current BSData field value from that historical patch alone.

Normative resolution remains:

**MFM 300 pts**

## Monitoring behavior

- exact registered known drift → report it, workflow remains green;
- new drift → workflow fails;
- changed known-drift value → workflow fails;
- missing catalogue/page → workflow fails;
- known drift disappears → report `RESOLVED_CANDIDATE` for registry review;
- runtime values never overwrite normative rules.

## Next milestone

`COLLECTION_AWARE_ROSTER_SOLVER`

The remaining automation gap is no longer detection. It is automated **re-ingestion/reconciliation/promotion** after a detected upstream change; that remains intentionally separate from this monitoring milestone.
