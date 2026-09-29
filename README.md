# WH40K Tabletop Knowledge Base

Canonical, versioned knowledge base for the user's Warhammer 40,000 tabletop hobby.

This repository is intended to unify:

- current and historical Warhammer 40,000 rules knowledge;
- faction/datasheet/points semantics and validation tooling;
- personal miniature collection and physical build constraints;
- army rosters and collection-aware list building;
- paints, painting recipes, basing, tools and hobby materials;
- provenance, source freshness and regression checks.

## Current bootstrap state

The repository was initialized on 2026-09-29 from two previously developed project baselines:

1. **W40K 11E Rules Assistant v0.9 Full Faction Semantics** — checkpoint 2026-08-15.
2. **Adeptus Custodes Collection Inventory v0.5 provisional-r2** — checkpoint 2026-07-11.

These baselines are **historical inputs**, not a claim that their rules or points are current on 2026-09-29.

## Core principles

1. **Source authority is explicit.** Official Games Workshop sources outrank secondary references.
2. **Freshness is data.** Every current rules claim must carry source/version/checkpoint information.
3. **UNKNOWN beats guessing.** Missing or conflicting evidence remains unresolved until verified.
4. **Physical inventory is independent from game points.** Collection files describe owned models, bodies, bits and build constraints; points live in versioned rules/points layers.
5. **Historical snapshots are immutable.** New updates create new snapshots/diffs rather than silently rewriting old evidence.
6. **Derived data is reproducible.** The long-term target is raw/source metadata → normalized data → derived runtime → validation/regression.
7. **Public-repository copyright hygiene.** Official source texts are referenced by provenance, URL/version/hash where appropriate; the repository should not become a verbatim mirror of copyrighted rulebooks.
8. **Personal hobby knowledge is first-class.** Painting inventory, recipes, techniques and project state are versioned independently from game rules and competitive analytics.

## Repository layout

```text
rules/                  Rules knowledge, current and historical snapshots
factions/               Faction-specific normalized/derived knowledge
collection/             Owned miniatures, bits and physical constraints
rosters/                Versioned roster snapshots and collection-aware builds
analytics/              Tournament/meta evidence and explainable roster recommendations
hobby/                   Paints, recipes, basing, tools and materials
sources/                 Source registry, provenance and baseline manifests
schemas/                 Data contracts
tools/                   Import, validation, diff and query tooling
tests/                   Regression/consistency tests
reports/                 Generated audits and migration reports
legacy/                  Metadata for superseded project baselines
```

## Immediate roadmap

- [x] Initialize repository governance and layout.
- [x] Register the 2026-08-15 rules baseline.
- [x] Import the current known Adeptus Custodes physical inventory baseline.
- [x] Preserve the complete legacy bootstrap artifacts and integrity-gate them in CI.
- [x] Establish role-specific external source authority and conflict/freshness policies.
- [x] Register Wahapedia, BSData/wh40k-11e and New Recruit as mirror → implementation → runtime cross-check layers.
- [x] Register BCP/Stat Check/Goonhammer as separate analytics/analysis sources.
- [x] Build a broader competitive source matrix (raw events → aggregators → list meta → mathhammer → expert analysis).
- [x] Define a lineage-aware roster recommendation evidence model and schema.
- [x] Verify the current GW downloads endpoint and MFM revision (updated 2026-09-02).
- [x] Expand the roster-universe catalogue from 8 historical factions to all 37 observed BSData roster catalogues.
- [x] Separate source health, scoped currentness and repository coverage.
- [x] Add release-transition tracking, coverage contracts, ingestion-run schema and repository contract tests.
- [x] Complete Wave A MFM v1.4 normalization: 30 faction pages / 36 roster identities / points, sizes, Leaders, DP, Force Dispositions and costs.
- [x] Complete Wave B structural faction ingestion: Wahapedia 11E CSV snapshot, MFM/BSData reconciliation and 35/37 roster-specific structural views.
- [x] Add a hash-verified on-demand semantic resolver with daily drift smoke checks.
- [x] Complete Wave B operational semantic/FAQ currentness: 16,506/16,506 mirror fingerprints match live data; 28/28 official faction-pack PDF assets verified; normative text equivalence remains explicitly unclaimed.
- [x] Add automated upstream revision/hash change watcher for BSData, MFM extraction and all 20 Wahapedia CSV snapshot files; changes stop the baseline and require re-ingestion/reconciliation.
- [x] Add drift-aware New Recruit runtime validation for all 37 roster identities, five-source mismatch lineage, representative point archetypes and selected structural runtime surfaces.
- [ ] Build automated re-ingestion/reconciliation/promotion after a detected upstream change.
- [x] Add collection-aware roster legality/physical-feasibility solver v1 for Adeptus Custodes, with shared-body allocation, build/conversion states, component limits and fail-closed unknowns.
- [x] Import painting inventory, 540-recipe knowledge base, active painting project state and source artifact from workbook v25.

## Status vocabulary

- `CURRENT_VERIFIED` — verified against the declared current source set.
- `CURRENT_PENDING_RECHECK` — intended current data but not yet revalidated after repository bootstrap.
- `HISTORICAL_VERIFIED` — internally verified historical snapshot.
- `PROVISIONAL` — useful working data with known unresolved questions.
- `UNKNOWN` — insufficient evidence; do not infer.


## Current ingestion status

Independent audit / ingestion hardening: `reports/INDEPENDENT_REPO_AUDIT_2026-09-29.md`.

Machine-readable current coverage: `coverage/current.json`.


## Wave B structural status

Checkpoint: **2026-09-29**.

- Wahapedia CSV last update: `2026-09-28 02:38:04`.
- Wahapedia current-mirror structural roster views complete: **35 / 37**.
- The two Wahapedia gaps, `titanicus_traitoris` and `unaligned_forces`, are covered by pinned BSData **structured-implementation fallbacks** without promoting BSData to normative authority.
- Total structural source availability: **37 / 37**.
- Reconciliation: 1,242 MFM/Wahapedia unit-name matches; 1,202 point signatures compared.
- Retained source conflicts: **11**. MFM remains normative for cost-bearing conflicts.
- Operational semantic/FAQ currentness is complete: all 16,506 stored semantic fingerprints match live Wahapedia, the live 11E source catalog has zero drift, and 28/28 referenced official faction-pack PDFs are reachable and hash-verified. `current_normalized_factions` intentionally remains 0 because mirror-to-official semantic equivalence and app-only wording are not claimed.

See `reports/WAVE_B_STRUCTURAL_CLOSURE_2026-09-29.md`.


## Semantic access

`tools/query_current_semantics.py` can retrieve exact current Wahapedia semantic text on demand and compare it with the SHA-256 fingerprint stored in the snapshot.

The fast smoke run remains available, and the full 2026-09-29 audit matched all 16,506 stored semantic fingerprints. A mismatch returns `SOURCE_DRIFT`; changed text is never silently accepted as snapshot-matched.

This is an operational semantic access layer, not a claim that the whole rules corpus has already been normalized or that Wahapedia overrides Games Workshop.
