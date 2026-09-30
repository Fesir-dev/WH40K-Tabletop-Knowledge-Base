# Official public ↔ current-mirror overlap model

## Purpose

This contract defines how the repository can compare **public Games Workshop 11E rules text** with the current Wahapedia 11E projection without turning a secondary mirror into normative authority and without vendoring long copyrighted rules prose.

The model closes only the portion of semantic equivalence that can be proven from the public official corpus:

- the public 11E Core Rules PDF;
- the 28 currently registered public 11E Faction Pack PDFs.

It does **not** prove Codex/app-only wording and does not by itself promote a whole faction to `CURRENT_VERIFIED`.

## Source roles

| Plane | Source | Role in this milestone |
| --- | --- | --- |
| Normative public | Games Workshop Core Rules / Faction Packs | text authority inside their exact public scope |
| Current mirror | Wahapedia 11E | candidate semantic-unit projection and drift surface |
| Structured implementation | BSData | out of scope for semantic-equivalence promotion |
| Runtime | New Recruit | out of scope for semantic-equivalence promotion |
| App/Codex-only | GW app / locked Codex content | remains `PENDING/UNKNOWN` unless separately authorized and versioned |

## Comparable semantic unit

The comparison unit is **not an arbitrary PDF paragraph**.

A comparable unit starts from an already identified current-mirror semantic object with a stable identity, for example:

- army ability;
- datasheet ability;
- datasheet option;
- unit-composition rule;
- datasheet loadout / transport / damaged rule;
- detachment ability;
- enhancement;
- stratagem.

The live mirror text is accepted for comparison only when the complete live CSV file hash matches the committed current Wahapedia snapshot manifest.

The official side is an exact Games Workshop document plus page evidence. Official binaries must match the already verified SHA-256 evidence before they are used.

## Comparison normalization

Version: `OFFICIAL_MIRROR_OVERLAP_NFKC_ALNUM_V1`.

For comparison only:

1. HTML entities/tags are removed from mirror text.
2. Unicode is normalized with NFKC.
3. soft hyphens and dash variants are normalized;
4. text is case-folded;
5. non-alphanumeric separators collapse to one space;
6. whitespace collapses.

The original prose is never committed. The repository stores identities, lengths, hashes, classifications and official page references.

## Classification

### `EXACT_NORMALIZED_TEXT_MATCH`

The complete normalized mirror semantic unit occurs contiguously in an official public page window.

This is the only text-equivalence classification eligible for automated structured official-public overlap normalization.

### `EXACT_NORMALIZED_TEXT_MATCH_MULTI_OFFICIAL`

The same complete normalized semantic unit occurs in more than one official public document/page.

This proves the text is present in public official rules, but source-to-roster provenance can be ambiguous. It is not automatically eligible for a source-scoped faction promotion.

### `NO_EXACT_PUBLIC_OVERLAP`

No exact normalized containment was found in the currently registered public official corpus.

This is **not** automatically a semantic conflict. The text may be Codex/app-only, may lie outside the public pack scope, or may require a stronger extraction mapping.

### `UNSCOPED_EXACT_PUBLIC_OVERLAP`

Exact public text exists, but the mirror object lacks a sufficiently direct official source mapping.

It can be retained as evidence but is not promoted into the source-scoped normalized official layer.

### `SOURCE_DRIFT`

A required official binary or current-mirror CSV no longer matches the committed source evidence.

The audit fails closed. Changed upstream text is never silently accepted.

## Provenance scopes

### `DIRECT_SOURCE_SCOPED`

The mirror object carries a source identity that maps directly to the official Faction Pack document and the exact text match is inside that document.

Eligible for structured official-public normalization.

### `DIRECT_FACTION_SCOPED`

The mirror object has a unique faction mapping to an official pack and exact text appears in that pack.

Eligible only when the mapping is unambiguous and recorded by the audit.

### `GLOBAL_PUBLIC_TEXT_ONLY`

Exact text appears somewhere in the public official corpus but source-to-roster identity is not strong enough.

Evidence only; no automated normative object promotion.

### `CORE_PUBLIC_TEXT_ONLY`

Exact text appears in the official Core Rules. This proves public official wording for that semantic unit, but it does not claim that the full Core Rules have been structurally normalized.

## Promotion rule

A semantic object may enter the structured **official-public overlap** snapshot only when all are true:

1. official binary SHA matches committed official evidence;
2. all live mirror CSV files used by the audit match the committed Wahapedia manifest;
3. classification is exact normalized containment;
4. provenance is `DIRECT_SOURCE_SCOPED` or an explicitly unambiguous `DIRECT_FACTION_SCOPED`;
5. the object stores no long rule prose;
6. the object records document ID, page evidence and semantic hashes.

Promotion into this overlap snapshot means only:

> this exact semantic unit is independently evidenced by current public Games Workshop material.

It does **not** mean:

- the complete faction is normatively normalized;
- a Faction Pack is a full Codex replacement;
- app-only wording is known;
- unmatched Wahapedia text is wrong;
- `current_normalized_factions` should automatically increase.

## Core Rules boundary

The Core Rules PDF is part of the audit corpus, but this v1 model does not pretend that the whole 88-page document is converted into a complete rules AST.

Exact current-mirror semantic units found in the Core Rules can be recorded as public official overlap. Broader Core Rules section normalization remains a subsequent structured-ingestion task.

## Required outputs

The executable audit produces:

- `reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json`;
- immutable structured snapshot under `rules/11e/snapshots/<date>/official_public_overlap/index.json`.

The report must expose:

- official-source verification state;
- mirror snapshot verification state;
- counts by semantic kind and classification;
- document/page coverage;
- exact scoped overlap units;
- exact unscoped overlap units;
- no-exact-overlap counts;
- authority/promotion boundaries.

## Failure policy

The audit is fail-closed.

Any required upstream hash drift, malformed official PDF, missing current snapshot pointer or inconsistent mapping returns a non-PASS state and produces **no promotable normalized snapshot**.
