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
19. Before substantial roster/meta recommendations, read `analytics/ANALYTICS_SOURCE_MATRIX.md` and `analytics/ROSTER_RECOMMENDATION_EVIDENCE_MODEL.md`.
20. Never count dependent aggregators as independent confirmations. Deduplicate evidence by underlying lineage (for example BCP-derived data).
21. Never silently combine evidence across materially different rules/points patches. Every competitive recommendation must declare its rules snapshot and analytics window.
22. Popularity/take rate is not performance evidence; mathhammer efficiency is not table strength; expert confidence is not empirical sample size. Keep these dimensions separate.
23. Call something expert consensus only when at least three independent expert sources support the same material conclusion; otherwise attribute the individual views.
24. Paid/subscription sources may be referenced by metadata and accessible summaries, but do not scrape, vendor or reproduce protected subscriber content.\n25. For painting/hobby work, read `hobby/painting/current.json` and `hobby/painting/README.md` before using old workbook assumptions.\n26. The painting XLSX source artifact is immutable. New revisions create new snapshots/diffs; never overwrite v25 in place.\n27. Separate physical paint inventory from recipe guidance, active project state, and dated economics/pricing. A current inventory snapshot does not make old prices current.

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
- `analytics/ANALYTICS_SOURCE_MATRIX.md`
- `analytics/ROSTER_RECOMMENDATION_EVIDENCE_MODEL.md`

## Repository domains

- `rules/`: edition-wide rules and versioned rules runtime data.
- `factions/`: faction-specific normalized/derived knowledge.
- `collection/`: personally owned physical miniatures and components.
- `rosters/`: roster snapshots/builds; never authoritative for current points by themselves.
- `hobby/`: paints, recipes, basing, tools and materials. The current painting authority starts at `hobby/painting/current.json`.
- `analytics/`: dated tournament/meta evidence, mathematical models, expert analysis and roster-recommendation evidence.
- `sources/`: authority registry, source profiles, hashes, checkpoints and provenance.
- `schemas/`: machine-readable data contracts.
- `tools/`: import/normalize/diff/query/validation utilities.
- `tests/`: regressions and invariants.
- `reports/`: generated audits and migration records.
- `legacy/`: immutable historical project baselines and preserved artifacts.

28. Source health/currentness and repository coverage are different facts. Never infer imported coverage from a healthy source.
29. Before claiming current faction data, check both `sources/currentness_gate.json` for the relevant scope and `coverage/current.json` for normalized coverage.
30. Preview/preorder rules remain separate from CURRENT_LEGAL data. Follow `sources/release_state.json`; never overwrite current rules from preview articles.
31. A faction/dimension can be promoted to CURRENT_VERIFIED only with applicable official-source currentness, provenance, complete claimed coverage, resolved/scoped conflicts, and passing tests.


## Long-run execution resilience

32. Substantial multi-stage work may remain a long single task, but each completed logical phase must be committed before the next high-risk phase begins.
33. A long task should normally use 3–6 durable milestones rather than dozens of tiny commits or one giant uncommitted run.
34. After each durable milestone, update or verify `reports/CURRENT_HANDOFF.md` before proceeding to the next major phase.
35. GitHub commit history and CI are the recovery authority if the ChatGPT delivery stream fails; never assume a missing chat update implies missing repository work.
36. Avoid repeated polling of the same workflow when no new state is expected. Prefer one status check at natural milestone boundaries.
37. Avoid loading entire large JSON files when a targeted summary/range/query is sufficient.
38. Do not continue far beyond a newly created unstable checkpoint. If a later phase depends on it, require passing validation first.

## Release-transition ingestion safety

39. A scheduled release date is a recheck trigger, not rules authority. Never promote new rules solely because the calendar date was reached.
40. Every upstream candidate eligible for promotion must declare `affected_roster_identities`. Legacy candidates without an impact set must be regenerated.
41. Before reviewed promotion, intersect affected roster identities with active entries in `sources/release_state.json`. Any pending transition with `candidate_authorization=false` blocks promotion until applicable official Games Workshop evidence explicitly authorizes the new release as current.

