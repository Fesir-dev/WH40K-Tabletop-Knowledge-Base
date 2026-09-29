# FULL 11E CURRENT INGESTION v1

## Objective

Move the repository from a historical eight-faction bootstrap to complete, measured current 11E coverage across the observed roster universe.

## P0 completed by the 2026-09-29 audit hardening pass

- full BSData roster-universe catalogue (37 roster catalogues, including titan/auxiliary catalogues);
- source-health vs repository-coverage separation;
- scoped currentness profiles;
- release-transition tracking for Orks, Space Marines ecosystem and Adeptus Custodes;
- explicit zero-coverage baseline;
- ingestion-run and coverage schemas;
- offline repository contract tests.

## Import order

### Wave A — global/MFM

Normalize the current MFM first because it gives the cleanest official bulk layer:

- points and unit-size bands;
- Leader/bodyguard relations;
- Detachment Points;
- Force Dispositions.

### Wave B — stable faction rules

For each faction not in an active release transition:

1. record applicable GW source/revision;
2. discover and parse Wahapedia faction projection;
3. inspect pinned BSData catalogue;
4. reconcile names/IDs/options;
5. normalize datasheets/detachments/keywords/wargear;
6. create conflicts rather than guessing;
7. update coverage;
8. promote only complete validated dimensions.

### Wave C — release transitions

- Orks: current Codex/MFM state can be ingested now.
- Space Marines ecosystem: preserve current legal state separately; ingest the new Codex state only when released.
- Adeptus Custodes: previews stay UPCOMING_PREVIEW_PARTIAL; do not overwrite current legal rules.

## Coverage contract

Every faction reports percentages for:

- points;
- unit sizes;
- leader relations;
- detachment points;
- Force Dispositions;
- datasheets;
- wargear constraints;
- keywords;
- detachments;
- enhancements;
- stratagems;
- FAQ/errata.

A claim such as CURRENT_VERIFIED must state which dimensions are complete.

## Promotion gate

A normalized object can become current only when:

1. applicable official source currentness is PASS;
2. object provenance is recorded;
3. its claimed coverage dimension is complete;
4. conflicts are resolved or explicitly scoped;
5. repository validation and unit tests pass;
6. release-state logic confirms it is CURRENT_LEGAL rather than preview-only.
