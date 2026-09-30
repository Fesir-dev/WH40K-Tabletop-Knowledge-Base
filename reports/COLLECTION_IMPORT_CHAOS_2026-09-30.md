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

The original three exports contain **321** source-entry bodies. User confirmation on 2026-09-30 resolved the suspected Daemon Prince overlap and added **3** physical Daemon Prince models that were not present in those exports, yielding **324 confirmed distinct physical models across these three imported Chaos-side collection domains**.

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

## Daemon Prince reconciliation

The previous `DAEMON_PRINCE_CROSS_FACTION_IDENTITY_UNRESOLVED` gate is **closed** by direct user confirmation.

Five distinct physical Daemon Prince miniatures are confirmed:

1. wingless Khorne-styled Daemon Prince;
2. winged Tzeentch-styled Daemon Prince;
3. winged Black Legion-styled Daemon Prince;
4. wingless Nurgle-styled Daemon Prince;
5. one additional Daemon Prince kit still on sprue.

The winged Tzeentch-styled model had been selected with a Khorne rules alignment in the New Recruit export. Physical styling and source roster rules alignment are now stored separately.

The Black Legion, Nurgle and on-sprue Daemon Princes are direct user-confirmed additions and were not counted in the three source exports.

All three inventories remain `PROVISIONAL` only for remaining build-state, magnetization, conversion and loose-component questions; Daemon Prince physical identity is no longer unresolved.
