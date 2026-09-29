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

### Wave A — global/MFM — **COMPLETE 2026-09-29**

Normalized MFM v1.4 (official update 2026-09-02) through a pinned deterministic extraction of the official MFM. Current snapshot totals: 30 source faction pages, 1,789 unit entries, 2,980 pricing rows, 1,574 Leader relations, 571 Support relations, 348 detachments and 1,193 enhancement-cost entries.

Coverage is complete for 36/37 roster identities (Unaligned Forces has no MFM page) for:

- points and unit-size bands;
- copy-tier/requisition-threshold pricing;
- paid wargear;
- Leader/Support relations;
- detachment catalogue and Detachment Points;
- Force Dispositions;
- enhancement costs;
- Legends pricing.

### Wave B — stable faction rules — **STRUCTURAL + OPERATIONAL SEMANTICS COMPLETE 2026-09-29**

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


### Wave B semantic/FAQ closure

- 16,506 / 16,506 stored semantic fingerprints match the live Wahapedia 11E CSV projection.
- Live Wahapedia `Source.csv` matches the committed edition-11 source catalog with zero drift.
- 29 edition-11 sources are indexed; one is MFM and 28 faction-pack PDF assets were fetched from the official Games Workshop asset domain and SHA-256 recorded.
- No long copyrighted rule prose is vendored.
- This closes **operational currentness**, not normative prose equivalence. Games Workshop remains authoritative and app-only wording remains a separate unresolved scope.

## Automated refresh control plane — COMPLETE 2026-09-29

Detected mirror/implementation changes now use:

`watch → deterministic plan → isolated candidate → reconciliation/audits → explicit reviewed promotion branch → PR`.

Automatic candidate generation is allowed; automatic promotion is not. A changed MFM extraction remains blocked until official Games Workshop MFM authority is revalidated.

## Active Wave C readiness milestone

`RELEASE_TRANSITION_INGESTION_READINESS`

Current transition facts remain unchanged:

- Space Marines ecosystem: current legal rules remain current; scheduled release date is 2026-10-03 and must not be promoted early.
- Adeptus Custodes: preview/preorder material remains upcoming-only until release/current-legality evidence exists.
- Both transitions should use the guarded candidate/reconciliation/promotion control plane once legally current.

