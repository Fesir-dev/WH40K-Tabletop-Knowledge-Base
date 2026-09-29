# Wave B semantic + FAQ operational closure — 2026-09-29

## Result

**PASS — operational semantic/FAQ currentness complete**

This milestone closes the operational currentness layer without vendoring long copyrighted rules prose and without claiming that a secondary mirror is normatively identical to Games Workshop source text.

## Full semantic fingerprint audit

Report:

`reports/WAVE_B_SEMANTIC_FINGERPRINT_AUDIT_2026-09-29.json`

Result:

- expected fingerprints: **16,506**
- matched: **16,506**
- drift: **0**
- missing live entities: **0**
- problems: **0**

Verified semantic surfaces include:

- shared/army abilities;
- datasheet abilities;
- datasheet options;
- unit composition;
- datasheet loadout;
- transport text;
- damaged-profile text;
- detachment abilities;
- enhancements;
- stratagems.

Long prose remains external. The repository stores SHA-256 fingerprints and structured metadata; `tools/query_current_semantics.py` retrieves exact live text on demand and requires a fingerprint match.

## FAQ / errata source currentness

Report:

`sources/snapshots/gw_11e_official_assets_2026-09-29.json`

Result:

- live Wahapedia `Source.csv`: HTTP 200
- edition-11 source rows: **29**
- committed-vs-live source-catalog drift: **0**
- MFM rows: **1** (handled by Wave A)
- official faction-pack PDF assets: **28**
- official faction-pack PDFs verified: **28 / 28**
- failed official assets: **0**

For every referenced official PDF, the audit records the exact Games Workshop asset URL, response metadata, byte size and SHA-256 without storing the PDF itself.

## Authority boundary

This milestone establishes:

- current secondary-mirror semantic identity;
- current source/version metadata;
- exact reachability and identity of referenced official GW faction-pack assets;
- stable on-demand semantic resolution.

It does **not** establish:

- automatic mirror-to-official prose equivalence for every paragraph;
- app-only wording equivalence;
- full normative normalization for all 37 roster identities.

Accordingly:

`current_normalized_factions = 0`

remains intentional.

## Current repository state

`rules/11e/current.json`:

`CURRENT_OPERATIONAL_RULES_LAYER_READY_NORMATIVE_APP_PENDING`

Wave B:

- current-mirror structural roster identities: **35**
- BSData structured-implementation fallback identities: **2**
- structural source availability: **37 / 37**
- current-mirror semantic roster identities: **35**
- full semantic fingerprint audit: **PASS**
- FAQ/errata source catalog + official assets: **PASS**
- retained MFM/Wahapedia source conflicts: **11**

## Validation

Promotion validation commit:

`2f737eb5291e8e37aa6bd4706d408a9d921725f2`

GitHub Actions:

- run: `36585942055`
- result: **SUCCESS**

## Next milestone

`AUTOMATED_DIFF_AND_NEW_RECRUIT_RUNTIME`

The next stage should automate:

1. GW/MFM/Wahapedia/BSData change detection and classified diffs;
2. New Recruit runtime/projection validation against pinned catalogue state;
3. promotion gating when upstream revisions change.
