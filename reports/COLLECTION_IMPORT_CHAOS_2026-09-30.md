# Chaos-side collection import — 2026-09-30

## Scope

Three user-supplied New Recruit JSON exports were normalized into physical collection data:

1. Thousand Sons collection export.
2. Mixed World Eaters + Khorne daemon export.
3. Tzeentch/Legiones Daemonica export hosted through the Titanicus Traitoris catalogue.

## Import result

- Thousand Sons: **109** source-declared physical bodies.
- World Eaters: **54** source-declared physical bodies.
- Chaos Daemons: **158** source-declared physical bodies.
  - Khorne-aligned: **40**.
  - Tzeentch-aligned: **117**.
  - Undivided: **1**.
- Total source-entry bodies across the three normalized inventories: **321**.

The repository does **not** claim 321 globally unique physical miniatures yet because the two Daemon Prince entries may describe one shared physical model.

## Provenance hashes

- `колекция тысяча сынов (1).json`: `fa80cbbb1430db124c5df319a9b3cdeaddfe853e355c119242d36550c1381f77`
- `Unnamed list (4).json`: `668b9228ff8e37f15af36c1bdabf22cdc2a04adbfdaa87b2b4ada7bcf5537109`
- `Коллекция тзинтча.json`: `da5415beeec66cadcf7d56f4d1dc1f9c74ba72373a9b39f99f2cc1e4311e6e04`

## Classification decisions

- Physical ownership is separated from points, detachment choice and roster legality.
- Khorne daemon selections embedded in the World Eaters export were routed to `collection/chaos_daemons/`.
- World Eaters faction-tagged selections were routed to `collection/world_eaters/`.
- The Titanicus Traitoris host catalogue in the Tzeentch export was treated as a container only; model faction tags control physical classification.
- Source-selected model variants are retained where they establish body counts, but build state and magnetization are not inferred.

## Open gate

`DAEMON_PRINCE_CROSS_FACTION_IDENTITY_UNRESOLVED`: determine whether the World Eaters Daemon Prince of Khorne and the winged Khorne Daemon Prince in the daemon export are one shared miniature or two physical models.

All three inventories remain `PROVISIONAL` until physical build state and shared-body questions are checked.
