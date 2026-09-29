# Wave A — MFM 1.4 normalization closure — 2026-09-29

## Result

**PASS — Wave A complete**

Official MFM state:

- version: **1.4**
- official last update: **2026-09-02**
- verified: **2026-09-29**

Structured extraction:

- repository: `BSData/wh40k-11e-mfm`
- pinned commit: `61a687e858c00a4ad205d564959c622a5605ef3d`
- source: official MFM pages
- upstream validation: zod model + fixture/parser tests + deterministic YAML

## Normalized dataset

- 30 MFM faction pages;
- 36/37 repository roster identities mapped;
- 1,789 unit entries;
- 2,980 pricing rows;
- 1,574 Leader relations;
- 571 Support relations;
- 348 detachments;
- 1,193 enhancement-cost entries;
- 107 paid-wargear cost entries;
- 326 Legends unit entries.

The only roster identity without an MFM page is `unaligned_forces`.

## Dimensions promoted to 100% coverage

For every mapped roster identity:

- points;
- unit-size pricing;
- copy-tier / requisition-threshold pricing;
- Leader/Support relations;
- detachment catalogue;
- Detachment Points;
- Force Dispositions;
- enhancement costs;
- paid wargear costs;
- Legends pricing.

This is **not** full faction coverage. The following remain pending Wave B:

- datasheet characteristics and abilities;
- complete wargear/loadout constraints;
- keywords;
- detachment rules;
- enhancement rules/effects;
- stratagem rules;
- FAQ/errata normalization.

## Astartes mapping

Dedicated supplement pages are used directly for Black Templars, Blood Angels, Dark Angels, Deathwatch and Space Wolves.

Codex-compliant chapter identities without independent MFM pages are derived from the Space Marines MFM page using base units plus their matching `groupTitle`: Imperial Fists, Iron Hands, Raven Guard, Salamanders, Ultramarines and White Scars.

## Current/legal transition safety

MFM v1.4 remains the current legal points layer captured here.

Upcoming Space Marines and Adeptus Custodes preview/release states remain tracked separately in `sources/release_state.json`; preview material did not overwrite this snapshot.

## Verification

GitHub Actions run `36559861472` completed successfully for commit `c9a2a6fa4010f307c81232bc591f4faff8664925`.

CI validates aggregate counts, per-file extraction commit, faction coverage, mappings and repository contracts.


## Wave B extraction candidate

A fresh external reference implementation, `MEC-Guard/Waha40kMcp` at commit `647f59d2e4071aa3bf66dadb0df44de290f7e1d7`, documents Wahapedia 11E CSV endpoints for:

- Factions;
- Sources;
- Datasheets;
- Datasheet keywords;
- model characteristics;
- weapons/wargear profiles;
- abilities;
- options;
- Stratagems;
- Detachment abilities;
- Enhancements.

Its 11E migration commit reports a live smoke test of 1,163 datasheets / 26 factions and adds regression tests around the real CSV column layout.

This is registered as a **REFERENCE_ONLY** Wave B extraction candidate. It does not establish current rules truth and will not raise faction coverage until our own ingestion reproduces and validates the CSV layer.
