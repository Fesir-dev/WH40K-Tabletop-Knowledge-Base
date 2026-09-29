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
- [ ] Re-check current official 11E sources and points against the 2026-08-15 checkpoint.
- [ ] Build automated GW ↔ Wahapedia ↔ BSData diff/normalization pipeline.
- [ ] Add New Recruit runtime validation/projection checks to the update pipeline.
- [ ] Expand faction materialization beyond the old local coverage.
- [ ] Add collection-aware roster legality/physical-feasibility solver.
- [ ] Import the user's paint/material inventory and painting recipes.

## Status vocabulary

- `CURRENT_VERIFIED` — verified against the declared current source set.
- `CURRENT_PENDING_RECHECK` — intended current data but not yet revalidated after repository bootstrap.
- `HISTORICAL_VERIFIED` — internally verified historical snapshot.
- `PROVISIONAL` — useful working data with known unresolved questions.
- `UNKNOWN` — insufficient evidence; do not infer.

