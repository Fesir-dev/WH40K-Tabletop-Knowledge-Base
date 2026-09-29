# AGENTS.md

## Scope

This repository is the canonical knowledge base for the user's Warhammer 40,000 tabletop hobby.

Agents working here must preserve provenance, version boundaries and the distinction between rules knowledge, personal collection data, runtime implementations, competitive analytics and hobby inventory.

## Non-negotiable rules

1. Never promote a historical snapshot to current without explicit source revalidation.
2. Never overwrite an old rules/points snapshot in place when the authority/version changed.
3. Never treat points stored in an old roster or collection export as current points.
4. Never infer missing facts. Use `UNKNOWN`, `PROVISIONAL` or an explicit unresolved gate.
5. Only applicable current Games Workshop evidence can establish `CURRENT_VERIFIED` normative rules truth.
6. Wahapedia is the preferred readable current mirror/cross-check, not a source that overrides official Games Workshop evidence.
7. BSData/wh40k-11e is the preferred machine-readable roster implementation cross-check. Treat its catalogue constraints/validation as implementation evidence, not normative authority.
8. New Recruit is a runtime projection of structured catalogue data. Use it to validate player-facing behavior and integration; do not treat it as an independent official source.
9. If Wahapedia and BSData disagree, create `SOURCE_CONFLICT` and verify the applicable official source. If BSData and New Recruit disagree, create `RUNTIME_PROJECTION_DRIFT`.
10. Tournament results/statistics and expert analysis (for example BCP, Stat Check, Goonhammer) belong to analytics/analysis domains. They never mutate normative rules facts.
11. Event-specific rulings (for example WTC) are scoped overlays and must not silently replace global matched-play rules.
12. Keep source facts, normalized facts and derived/runtime facts separable.
13. Personal collection constraints are first-class data: bodies, magnetization, interchangeable roles, bits and mutually exclusive builds matter.
14. Validation must fail closed when required source freshness or legality evidence is missing.
15. This is a public repository. Do not vendor full copyrighted rulebooks/codexes or reproduce large verbatim official texts. Store provenance, hashes, structured facts and concise derived semantics instead.
16. Every migration from legacy material must record the legacy artifact/checkpoint and whether the migrated field was copied, normalized, corrected or re-derived.
17. Git-backed external sources must be pinned by commit SHA when used for a reproducible snapshot.
18. Do not invent New Recruit synchronization cadence or undocumented API behavior; record unknowns explicitly.

## Preferred status values

- `CURRENT_VERIFIED`
- `CURRENT_PENDING_RECHECK`
- `HISTORICAL_VERIFIED`
- `PROVISIONAL`
- `UNKNOWN`

## External source contracts

Read before external-source work:

- `sources/SOURCE_AUTHORITY_MATRIX.md`
- `sources/registry.json`
- `sources/conflict_policy.json`
- `sources/freshness_policy.json`
- `docs/EXTERNAL_INGESTION_PIPELINE.md`

## Repository domains

- `rules/`: edition-wide rules and versioned rules runtime data.
- `factions/`: faction-specific normalized/derived knowledge.
- `collection/`: personally owned physical miniatures and components.
- `rosters/`: roster snapshots/builds; never authoritative for current points by themselves.
- `hobby/`: paints, recipes, basing, tools and materials.
- `sources/`: authority registry, source profiles, hashes, checkpoints and provenance.
- `schemas/`: machine-readable data contracts.
- `tools/`: import/normalize/diff/query/validation utilities.
- `tests/`: regressions and invariants.
- `reports/`: generated audits and migration records.
- `legacy/`: immutable historical project baselines and preserved artifacts.
