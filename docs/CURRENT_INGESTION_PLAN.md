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

## Release-transition readiness v1 — COMPLETE

The repository now has explicit transition manifests and a fail-closed state machine for the pending Space Marines and Adeptus Custodes releases.

At the 2026-09-29 checkpoint:

- Space Marines: `PRE_RELEASE_HOLD`, scheduled release date 2026-10-03, official current-legal confirmation not yet recorded;
- Adeptus Custodes: `UPCOMING_HOLD_NO_RELEASE_DATE`, current-legal release date intentionally unknown;
- neither transition is candidate-eligible or promotion-eligible.

A release date, preview or preorder announcement is never sufficient for promotion. Official current-legal evidence must be explicitly recorded, then a real upstream projection change must be detected before the existing guarded re-ingestion candidate path can run.

Active milestone:

`RELEASE_TRANSITION_ACTIVATION_WATCH`

## Release-transition activation watch v1 — COMPLETE

The release-transition layer now runs a read-only six-hour watch.

Checkpoint 2026-09-29:

- Space Marines: `NO_ACTION → WAIT_PRE_RELEASE`;
- Adeptus Custodes: `NO_ACTION → WAIT_OFFICIAL_RELEASE_SIGNAL`;
- global status: `NO_ACTION_REQUIRED`;
- direct promotion eligibility: always false.

Future transitions are surfaced as `ACTION_REQUIRED`, `MONITORING_UPSTREAM_PROJECTION`, or `READY_FOR_GUARDED_CANDIDATE`. Even the candidate-ready state only authorizes the existing isolated candidate path; reviewed promotion remains separate.

The release watch remains operational while development proceeds to:

`NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT`

## Normative/app equivalence gap audit — COMPLETE

The authority gap is now machine-classified.

Key result:

- `current_normalized_factions = 0` is an intentional normative threshold, not evidence that the current mirror is empty;
- 11E Core Rules are an official public source and can be ingested now;
- all 28 registered 11E public Faction Pack PDFs are verified, but Games Workshop defines them as supplemental to Codex content rather than full Codex replacements;
- current Wahapedia semantics are hash-current for 35 roster identities, but mirror currentness is not normative equivalence;
- GW App/Codex-only wording remains explicitly blocked on authorized/versioned evidence;
- official source→roster provenance currently resolves as 25 direct matches + 3 naming-alias candidates + 7 parent-source candidates + 2 no-public-pack identities.

Active milestone:

`OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_PIPELINE`

This next pipeline may close public Core Rules and public Faction Pack supplement/FAQ semantics plus official-vs-mirror overlap. It must not automatically promote full-faction normalization or infer app-only text.

