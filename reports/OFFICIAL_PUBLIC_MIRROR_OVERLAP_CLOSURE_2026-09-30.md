# Official public ↔ current-mirror overlap audit closure — 2026-09-30

## Result

**PASS — C1–C3 closed; exact public-official overlap is now a structured, copyright-safe evidence layer.**

This milestone compared the verified public Games Workshop 11E corpus against the hash-verified current Wahapedia semantic projection without treating the mirror as normative authority.

## C1 — comparison contract

Completed:

- comparison model: `docs/OFFICIAL_PUBLIC_MIRROR_OVERLAP_MODEL.md`;
- audit schema: `schemas/official_public_mirror_overlap.schema.json`;
- structured snapshot schema: `schemas/official_public_overlap_snapshot.schema.json`;
- normalization: `OFFICIAL_MIRROR_OVERLAP_NFKC_ALNUM_V1`;
- only complete exact normalized containment is eligible;
- only `DIRECT_SOURCE_SCOPED` and `DIRECT_FACTION_SCOPED` evidence is promotable;
- unscoped exact overlap is evidence-only;
- no-exact-public-overlap is not automatically a semantic conflict.

## C2 — executable overlap audit

Tool:

`tools/audit_official_public_mirror_overlap.py`

The audit verifies before comparison:

1. all required live Wahapedia CSV hashes against the committed current snapshot;
2. all 29 Games Workshop public binaries against committed binary hashes;
3. official per-page semantic fingerprints and document semantic fingerprints.

Any real upstream hash drift fails closed.

A transient Wahapedia network timeout was observed during the first PR execution. The fetch layer was hardened with bounded retry/backoff; the failure was transport-only and did not change source classification.

### Audit totals

- public official documents: **29**;
- Core Rules: **1**;
- public Faction Packs: **28**;
- official pages: **1,430**;
- current mirror semantic units audited: **13,572**;
- exact normalized public overlap units: **5,636**;
- exact single-document matches: **4,145**;
- exact matches present in multiple official documents: **1,491**;
- exact source/faction-scoped units: **4,070**;
- exact but unscoped units: **1,566**;
- no exact public overlap: **7,936**;
- official pages containing at least one exact overlap: **1,268**.

### Provenance distribution

- `DIRECT_SOURCE_SCOPED`: **1,323**;
- `DIRECT_FACTION_SCOPED`: **2,747**;
- `GLOBAL_PUBLIC_TEXT_ONLY`: **1,545**;
- `CORE_PUBLIC_TEXT_ONLY`: **21**.

The last two categories are not promoted into the structured official-public snapshot.

## C3 — structured official-public normalization

Snapshot:

`rules/11e/snapshots/2026-09-30/official_public_overlap/index.json`

Structured promotable units: **4,070**.

By kind:

| Semantic kind | Structured units |
| --- | ---: |
| ability | 12 |
| datasheet ability | 1,401 |
| datasheet damaged description | 269 |
| datasheet loadout | 483 |
| datasheet option | 770 |
| datasheet transport | 62 |
| detachment ability | 129 |
| enhancement | 367 |
| stratagem | 518 |
| unit composition | 59 |

Every normalized entry retains object identity, mirror semantic hashes and exact official document/page evidence. Long Games Workshop or mirror rule prose is not committed.

## Authority boundary

This closure establishes:

> a set of individual current-mirror semantic objects is independently evidenced by exact currently verified public Games Workshop text.

It does **not** establish:

- complete Codex semantics for any faction;
- full Games Workshop app equivalence;
- complete structured Core Rules;
- that unmatched mirror semantics are wrong;
- that a Faction Pack replaces a Codex;
- that all public exact matches are source-scoped;
- that `current_normalized_factions` can increase.

Therefore:

- `current_normalized_factions = 0` remains intentional;
- `full_normative_semantic_factions = 0` remains intentional;
- GW App / Codex-only semantics remain `PENDING/UNKNOWN`;
- Core Rules broader structured normalization remains pending.

## Generated evidence

- full report: `reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json`;
- compact recovery summary: `reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_SUMMARY_CURRENT.json`;
- structured snapshot: `rules/11e/snapshots/2026-09-30/official_public_overlap/index.json`;
- workflow: `.github/workflows/official-public-mirror-overlap.yml`.

## Pre-C4 validation evidence

Validated author head before current-pointer integration:

- generic knowledge-base validation run: `36687880993` — **SUCCESS**;
- official public mirror overlap run: `36687881077` — **SUCCESS**.

The overlap run passed full source verification, audit generation, compact-summary generation and authority-boundary validation.

## Next milestone

`OFFICIAL_PUBLIC_STRUCTURED_NORMALIZATION_EXPANSION`

Priority order:

1. build section-level structured normalization for the public Core Rules rather than relying only on object overlap;
2. review the **1,566** exact-but-unscoped overlap units for stronger provenance;
3. classify the **7,936** no-exact-public-overlap units into short/extraction cases, public-scope absence and likely Codex/app-only scope without assuming disagreement;
4. preserve app/Codex-only content as `PENDING/UNKNOWN` until authorized versioned evidence exists.

## C4 — repository integration and validation

Integrated:

- `rules/11e/current.json` now exposes `official_public_mirror_overlap.state = PASS_EXACT_PUBLIC_OVERLAP_V1`;
- `sources/currentness_gate.json` has a separate `official_public_mirror_overlap` scope profile;
- `coverage/current.json` records the scoped overlap metrics without changing whole-faction normative coverage;
- repository governance explicitly forbids converting no-exact-overlap into a conflict without official evidence;
- `tools/validate_repo.py` and repository contract tests lock the authority boundary and exact checkpoint counts.

Validated integration checkpoints:

- full overlap pipeline after current-pointer integration: run `36688272008` — **SUCCESS**;
- normative/app historical gap audit reproducibility: run `36688416703` — **SUCCESS**;
- repository validator + full unit/contract test suite after milestone-baseline advancement: run `36688416705` — **SUCCESS**.

The implementation-head evidence is intentionally recorded before the final handoff-only commit; the PR head is required to pass its own checks before merge.

