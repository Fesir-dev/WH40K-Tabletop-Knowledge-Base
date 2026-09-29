# Independent repository audit and P0 hardening — 2026-09-29

## Audit verdict

The repository architecture is substantially stronger than its current rules coverage.

Before this pass:

- repository files: 106;
- `rules/`: 3 files;
- `factions/`: 2 files;
- `tests/`: 0 files;
- faction catalogue: 8 historical tracked factions;
- complete normalized current factions: 0.

The primary risk was therefore not lack of external sources, but confusing registered/current sources with current normalized repository coverage.

## P0 changes completed

- expanded the faction/roster catalogue to 37 BSData roster catalogues;
- classified primary factions, Astartes supplements, titan forces and auxiliary forces;
- separated source health/currentness from repository coverage;
- added scoped currentness profiles;
- added explicit release-state tracking;
- recorded active Space Marines and Adeptus Custodes release transitions separately from current legal rules;
- added an explicit zero-current-coverage baseline;
- added ingestion-run, faction-catalogue and coverage schemas;
- added BSData source-tree snapshot at commit `951d5900d1b4a952a4ba560a30c43788e622ccfc`;
- added real offline unit tests and enabled them in GitHub Actions;
- updated the migration plan for FULL 11E CURRENT INGESTION v1.

## MFM acquisition finding

The official Warhammer Community downloads page is readable and reports the MFM as updated on 2026-09-02.

The direct interactive MFM endpoint returned HTTP 403 to automated fetch in this environment. Search-index copies of faction pages are readable, but their crawl age can be older than the official current revision.

Therefore:

- the official page is authoritative for revision/date and documented MFM scope;
- stale indexed page content must not be treated as a safe bulk official export;
- structured extraction should use pinned BSData plus current Wahapedia;
- normative promotion must retain official verification and conflict checks.

See `sources/profiles/gw_mfm_11e.json`.

## Next active work

Wave A: normalize the current MFM dimensions across the roster universe.

Wave B: normalize faction rules for stable factions.

Wave C: handle release-transition factions without allowing preview material to overwrite current legal rules.
