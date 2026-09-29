# Official public rules semantic fingerprint pipeline closure — 2026-09-29

## Result

**PASS — operational copyright-safe official evidence layer.**

The repository now fingerprints the complete currently registered public Games Workshop 11th-edition rules PDF surface used by this project without vendoring long copyrighted rules prose.

## Corpus

- official documents: **29 / 29 PASS**;
- Core Rules: **1**;
- public 11E Faction Packs: **28**;
- pages fingerprinted: **1,430**;
- normalized text characters fingerprinted: **1,915,296**;
- extraction failures: **0**.

Extraction contract:

- engine: `pypdf 5.9.0`;
- normalization: `OFFICIAL_TEXT_NFKC_WS_V1`;
- stored evidence: binary hashes, document/page semantic hashes, counts and coarse semantic classes;
- long Games Workshop rules text is **not** stored in the repository.

## Core Rules

Official public source:

`https://assets.warhammer-community.com/eng_01-06_warhammer40k_new40k_core_rules-was6fbu1ix-hfewhmxyiy.pdf`

Observed evidence:

- pages: **88**;
- normalized text characters: **138,078**;
- binary SHA-256: `f6a2443a44627ac5f0ef08407d29aa5ec7e97339998f05bc35f3ae37bf276833`;
- normalized semantic SHA-256: `c8b98076bb0577878fe20f33f743f429ef838cf1df9b3eda2f42e1bba6107fe7`.

Snapshot:

`sources/snapshots/gw_11e_core_rules_asset_2026-09-29.json`

## Faction Packs

All **28 / 28** public Faction Pack PDFs were downloaded from their registered official Games Workshop asset URLs.

Every downloaded Faction Pack binary SHA-256 matched the exact SHA already recorded by the previous official-asset verification layer.

This establishes reproducible official public supplement text fingerprints. It does **not** make a Faction Pack a full Codex replacement.

## Generated evidence

Primary report:

`reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json`

Tool:

`tools/build_official_public_semantic_fingerprints.py`

Schema:

`schemas/official_public_semantic_fingerprint.schema.json`

Workflow:

`.github/workflows/official-public-semantic-fingerprints.yml`

## Currentness integration

The repository now distinguishes these states:

- Core Rules: `OFFICIAL_PUBLIC_SEMANTIC_FINGERPRINTED_NOT_STRUCTURED`;
- public faction supplements: `OFFICIAL_PUBLIC_SUPPLEMENTS_FINGERPRINTED_FULL_CODEX_PENDING`;
- app wording: `PENDING`;
- full Codex/app equivalence: `PENDING`;
- strict full normative faction count: **0**.

`current_normalized_factions = 0` and `full_normative_semantic_factions = 0` remain intentional.

Fingerprints prove exact public official source projections and provide drift evidence. They do not by themselves normalize rule semantics into repository structures and do not prove that secondary-mirror text equals all official Codex/app text.

## Gap-audit advancement

The current normative/app gap projection was advanced after this milestone:

- `OFFICIAL_CORE_RULES_SEMANTIC_INGESTION` → `FINGERPRINT_EVIDENCE_CLOSED_STRUCTURED_NORMALIZATION_PENDING`;
- `PUBLIC_FACTION_SUPPLEMENT_SEMANTIC_INGESTION` → `FINGERPRINT_EVIDENCE_CLOSED_STRUCTURED_EXTRACTION_PENDING`;
- app/Codex-only semantics remain blocked on authorized official evidence;
- public official ↔ mirror overlap comparison is now the next closable layer.

## Drift protection

The fingerprint workflow now runs on relevant repository changes and on a daily schedule.

On pull requests and scheduled runs it rebuilds the official public corpus and requires the committed fingerprint report to reproduce exactly.

A binary/text change therefore becomes explicit drift rather than silently replacing committed evidence.

## Validation evidence

Validated implementation head:

`148843a72d27f20459e064da8c9943eab19c5ed2`

GitHub Actions:

- Official public rules semantic fingerprints: run `36615907736` — **SUCCESS**;
- Normative/app equivalence gap audit: run `36615908005` — **SUCCESS**;
- Validate knowledge base: run `36615907686` — **SUCCESS**.

The full 29-document corpus was rebuilt on the validated head and the committed report reproduced successfully.

## Authority boundary

- Games Workshop remains normative;
- Wahapedia remains a secondary current mirror;
- official public fingerprints do not grant full Codex/app equivalence;
- app-only wording is not inferred;
- Faction Packs remain supplemental official sources;
- no strict normative faction coverage was promoted by this milestone.

## Next milestone

`OFFICIAL_PUBLIC_RULES_MIRROR_OVERLAP_AUDIT`

Scope:

- identify robust comparable semantic units in the public official Core Rules/Faction Packs;
- compare only official public overlap against current mirror semantics;
- distinguish exact matches, extraction/normalization mismatches, real semantic drift and unmappable text;
- do not generalize overlap matches into full-faction equivalence;
- begin structured official-public normalization only where provenance is exact.
