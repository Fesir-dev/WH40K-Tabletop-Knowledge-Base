# AGENTS.md

## Scope

This repository is the canonical knowledge base for the user's Warhammer 40,000 tabletop hobby.

Agents working here must preserve provenance, version boundaries and the distinction between rules knowledge, personal collection data and hobby inventory.

## Non-negotiable rules

1. Never promote a historical snapshot to current without explicit source revalidation.
2. Never overwrite an old rules/points snapshot in place when the authority/version changed.
3. Never treat points stored in an old roster or collection export as current points.
4. Never infer missing facts. Use `UNKNOWN`, `PROVISIONAL` or an explicit unresolved gate.
5. Official Games Workshop sources outrank secondary sources. Secondary sources can cross-check, discover gaps or detect drift.
6. Keep source facts, normalized facts and derived/runtime facts separable.
7. Personal collection constraints are first-class data: bodies, magnetization, interchangeable roles, bits and mutually exclusive builds matter.
8. Validation must fail closed when required source freshness or legality evidence is missing.
9. This is a public repository. Do not vendor full copyrighted rulebooks/codexes or reproduce large verbatim official texts. Store provenance, hashes, structured facts and concise derived semantics instead.
10. Every migration from legacy material must record the legacy artifact/checkpoint and whether the migrated field was copied, normalized, corrected or re-derived.

## Preferred status values

- `CURRENT_VERIFIED`
- `CURRENT_PENDING_RECHECK`
- `HISTORICAL_VERIFIED`
- `PROVISIONAL`
- `UNKNOWN`

## Repository domains

- `rules/`: edition-wide rules and versioned rules runtime data.
- `factions/`: faction-specific semantics.
- `collection/`: personally owned physical miniatures and components.
- `rosters/`: roster snapshots/builds; never authoritative for current points by themselves.
- `hobby/`: paints, recipes, basing, tools and materials.
- `sources/`: authority registry, hashes, checkpoints and provenance.
- `schemas/`: machine-readable data contracts.
- `tools/`: import/normalize/diff/query/validation utilities.
- `tests/`: regressions and invariants.
- `reports/`: generated audits and migration records.
- `legacy/`: immutable metadata describing superseded project baselines.
