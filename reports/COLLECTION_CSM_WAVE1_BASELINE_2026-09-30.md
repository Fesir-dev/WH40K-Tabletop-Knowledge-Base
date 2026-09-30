# Chaos Space Marines collection — Wave 1 baseline — 2026-09-30

## Purpose

Establish a durable first physical-inventory checkpoint for a long-running Chaos Space Marines collection accumulated across multiple editions.

This is deliberately **not** a final collection audit.

## User scope declaration

The user states that:

- the faction has been collected since approximately 2013;
- purchases/builds were uneven across many editions;
- the army has never been fully completed as one clean edition-specific build;
- many additional models/kits remain outside the supplied roster, including unassembled/on-sprue material;
- historical weapon and squad configurations no longer map cleanly to current 11E unit construction;
- some selections in the source roster require later clarification.

## Source

Uploaded New Recruit export:

- filename: `Вся колллекция CSM.json`
- SHA-256: `8549829fb7d7002aae6f4e5e859ba939cbf86f7370cf3248f75d681c214058ec`
- roster name: `Вся колллекция CSM`
- generator: New Recruit
- game system: Warhammer 40,000 11th Edition, revision 15
- catalogue: Chaos - Chaos Space Marines, revision 17
- source-reported roster value: 3600 pts

The point value is retained as source metadata only and is not current-points authority.

## Extracted Wave 1 body count

34 top-level unit/character entries represent **117 physical bodies/models**.

### Character/single-model layer

- Abaddon — 1
- Haarken — 1
- Chaos Lord — 1
- Chaos Lord in Terminator Armour — 1
- Chaos Lord with Jump Pack — 1
- Dark Apostle set — 3 bodies (Apostle + 2 Disciples)
- Exalted Champion [Crucible] — 1
- winged Heretic Astartes Daemon Prince — 1
- Lord Discordant — 1
- Master of Executions — 1
- Master of Possession — 3
- Sorcerer — 2

### Infantry/body pools

- Cultists — 40
- Legionaries — 15
- Accursed Cultists — 8
- Chaos Terminators — 10
- Havocs — 10
- Obliterators — 4
- Possessed — 5
- Warp Talons — 5

### Vehicle/daemon-engine layer

- Helbrute — 1
- Venomcrawler — 2

## Preserved source configurations

The import preserves roster-projected loadouts without promoting them to physical truth.

High-risk reconciliation examples:

- Legionaries: 15 bodies represented as three 5-model units; source aggregate contains 13 boltguns + 2 lascannons.
- Terminators: 10 bodies represented as accursed weapon + combi-bolter.
- Havocs: 10 bodies; source aggregate contains 4 autocannons + 4 lascannons.
- Helbrute: missile launcher + multi-melta source configuration.
- characters: source weapon options are recorded but assembly/magnetization is unresolved.

## Data-model decision

CSM requires a multi-layer physical model:

1. body ownership;
2. build state;
3. fixed weapon state;
4. magnetized state;
5. loose bit/component pools;
6. edition-specific historical role;
7. current-role projection.

Current rules do not overwrite historical physical builds.

## Cross-domain gate

The CSM source includes a winged Heretic Astartes Daemon Prince.

A winged Black Legion-styled Daemon Prince is already recorded in `collection/chaos_daemons`.

Identity remains unresolved pending direct user confirmation.

## Milestone result

Wave 1 baseline: **COMMITTED AS LOWER BOUND**

- source-declared bodies: 117
- actual collection total: unknown and explicitly larger
- build-state audit: open
- loadout audit: open
- missing-body waves: open
- cross-domain Daemon Prince identity: open

Future work should continue from this checkpoint rather than re-importing the roster from scratch.
