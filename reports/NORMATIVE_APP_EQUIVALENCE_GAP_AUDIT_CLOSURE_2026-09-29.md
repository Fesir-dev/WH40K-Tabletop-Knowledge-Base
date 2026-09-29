# Normative / app equivalence gap audit closure — 2026-09-29

## Result

**PASS — gaps classified and next public-source pipeline bounded.**

The audit explains why `current_normalized_factions = 0` is still correct despite complete MFM coverage and strong current secondary-mirror coverage.

## What is already closed

### MFM normative dimensions

Games Workshop MFM 1.4 remains normative and complete for 36 applicable roster identities across:

- points;
- unit sizes;
- Leader relations;
- Detachment Points;
- Force Dispositions;
- detachment catalogue;
- enhancement costs;
- paid wargear costs;
- Legends pricing.

### Official faction asset provenance

- edition-11 source-catalog rows: **29**;
- MFM source: **1**;
- public faction-pack PDF assets: **28**;
- verified official PDF assets: **28 / 28**;
- failures: **0**;
- live source-catalog drift: **0**.

### Secondary-mirror semantic currentness

- Wahapedia semantic fingerprints expected: **16,506**;
- matched: **16,506**;
- problems: **0**;
- current secondary semantic roster identities: **35**.

This proves currentness of the secondary mirror projection only. It does not establish Games Workshop normative equivalence.

## New official-source discovery

### 11E Core Rules are public

Games Workshop officially published the 11th-edition Core Rules for free on 2026-06-01.

Official article:

`https://www.warhammer-community.com/en-gb/articles/nhqt9wx3/new40k-rules-download-the-free-core-rules-now/`

Official PDF:

`https://assets.warhammer-community.com/eng_01-06_warhammer40k_new40k_core_rules-was6fbu1ix-hfewhmxyiy.pdf`

Therefore the Core Rules gap is **not an availability blocker**. It is a repository registration/semantic-ingestion gap and is closable with current public official sources.

### Public Faction Packs are supplemental, not full Codex replacements

Games Workshop explicitly describes Faction Packs as consolidated supplemental material: additional Detachments, datasheets, FAQs and errata that supplement Codex content. MFM and Core Rules updates remain separate.

Therefore the 28 verified Faction Pack PDFs are suitable for official supplement/FAQ semantic ingestion but are not sufficient, by themselves, to prove full faction/Codex/app equivalence.

## Gap classification

| Gap | State |
| --- | --- |
| Official Core Rules semantic ingestion | `CLOSABLE_WITH_CURRENT_PUBLIC_SOURCE` |
| Public Faction Pack supplement / FAQ ingestion | `CLOSABLE_WITH_CURRENT_PUBLIC_SOURCES` |
| Full faction Codex/app semantics | `BLOCKED_OR_CONDITIONAL_ON_AUTHORIZED_CODEX_APP_EVIDENCE` |
| Mirror → official semantic equivalence | `PARTIALLY_CLOSABLE_PUBLIC_OVERLAP_ONLY` |
| GW App wording / locked datasheet crosscheck | `BLOCKED_ON_AUTHORIZED_APP_EVIDENCE` |
| Official source → roster identity mapping | `CLOSABLE_WITH_METADATA_AND_CONTENT_REVIEW` |
| Normative coverage zero accounting | `INTENTIONAL_ZERO_NOT_MIRROR_DATA_LOSS` |

## Source-to-roster mapping audit

Across the 37 roster identities:

- direct official Faction Pack name match: **25**;
- naming-alias candidate: **3**;
- parent-source candidate: **7**;
- no public Faction Pack mapping: **2**.

The two no-pack identities at this checkpoint are:

- `titanicus_traitoris`;
- `unaligned_forces`.

Alias and parent mappings are provenance candidates only. They must not grant normative semantic equivalence until official content scope is reviewed.

## Why `current_normalized_factions = 0` is still correct

The repository distinguishes three things:

1. **normative MFM facts** — already current and verified;
2. **secondary mirror semantics** — current/hash-verified for 35 roster identities;
3. **full official normative faction semantics** — not yet proven.

The semantic normative dimensions remain intentionally unpromoted for all 37 roster identities:

- datasheets;
- wargear constraints;
- keywords;
- detachments;
- enhancements;
- stratagems;
- FAQ/errata semantic normalization.

This is not missing mirror data. It is an authority threshold.

## GW App boundary

The official app is confirmed by Games Workshop as a live rules surface for the new edition and receives rules updates, but the repository has no authorized, versioned app-content ingestion path.

Therefore:

- `GW_40K_APP` remains `CURRENT_PENDING_RECHECK` / `NOT_INGESTED`;
- app wording remains `PENDING`;
- app-only text must not be inferred from Wahapedia, BSData or New Recruit;
- no app polling cadence is invented.

## What can be done now

With current public official sources the repository can safely build:

1. official Core Rules semantic fingerprints / structured metadata;
2. official public Faction Pack supplement + FAQ/errata semantic fingerprints;
3. reviewed source-to-roster provenance mapping;
4. official-vs-Wahapedia semantic comparison **only for overlapping public official content**.

These steps can improve scoped normative coverage, but they must **not automatically promote full-faction normalization**.

## Validation evidence

Validated audit head:

`436a053786fbdf6acd4f9c5040dc423f7c1c76a1`

GitHub Actions:

- Normative/app equivalence gap audit: run `36611731432` — **SUCCESS**;
- Validate knowledge base: run `36611731596` — **SUCCESS**.

The audit workflow passed:

- Python compile;
- gap-audit regression tests;
- exact generated-vs-committed audit reproduction.

## Next milestone

`OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_PIPELINE`

Scope:

- register the official 2026 Core Rules asset;
- fingerprint/structure official public Core Rules without vendoring long prose;
- fingerprint/structure the 28 verified public Faction Pack supplement/FAQ assets;
- build explicit source-to-roster provenance mapping;
- compare official public overlap with the current mirror;
- preserve Codex/app-only content as explicit `PENDING/UNKNOWN`;
- do not automatically increase `current_normalized_factions`.
