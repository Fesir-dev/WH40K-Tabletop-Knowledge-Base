# Chaos Space Marines collection

Checkpoint: **2026-09-30**  
Status: **PROVISIONAL — Wave 1 lower bound**

Canonical inventory: `current.json`.

## Scope

This domain tracks the user's long-running Chaos Space Marines / Heretic Astartes physical collection.

The collection has been accumulated since approximately 2013 across multiple editions. It is explicitly not a clean single-edition purchase/build set: models were bought and assembled at different times, some kits remain on sprues, and historical weapon/squad conventions no longer map cleanly to current 11E datasheets.

Therefore the collection is reconciled in this order:

1. physical body/model ownership;
2. assembled vs partial vs on-sprue state;
3. fixed/magnetized/interchangeable physical loadouts;
4. loose weapon/bit pools;
5. mapping of those physical bodies to current datasheet roles;
6. current roster legality only after the physical layer is stable.

Current rules are never allowed to erase or rewrite an older physical build.

## Wave 1 source

User-supplied New Recruit export:

- roster: `Вся колллекция CSM`
- system: Warhammer 40,000 11th Edition, revision 15
- catalogue: Chaos - Chaos Space Marines, revision 17
- source-reported points: 3600 — metadata only, not collection or current-points authority
- source top-level unit/character entries: **34**
- physical bodies represented by the source selections: **117**

The user explicitly states that **117 is only a lower bound**. Additional assembled models and unassembled/on-sprue kits exist outside this roster.

## Wave 1 physical pools

### Characters / single-model entries

- Abaddon the Despoiler — 1
- Haarken Worldclaimer — 1
- Chaos Lord — 1
- Chaos Lord in Terminator Armour — 1
- Chaos Lord with Jump Pack — 1
- Dark Apostle — 1 + 2 Dark Disciples
- Exalted Champion [Crucible] — 1
- Heretic Astartes Daemon Prince with wings — 1
- Lord Discordant on Helstalker — 1
- Master of Executions — 1
- Master of Possession — 3
- Sorcerer — 2

### Infantry / body pools

- Cultist Mob — **40 bodies**
- Legionaries — **15 bodies**
- Accursed Cultists — **8 bodies**:
  - 5 Mutants
  - 3 Torments
- Chaos Terminators — **10 bodies**
- Havocs — **10 bodies**
- Obliterators — **4 bodies**
- Possessed — **5 bodies**
- Warp Talons — **5 bodies**

### Vehicles / daemon engines

- Helbrute — 1
- Venomcrawler — 2

## Source configuration snapshot

The New Recruit loadouts are retained only as dated roster projection.

Notable Wave 1 source configurations include:

- Legionaries: three 5-model selections; aggregate source projection contains 13 boltguns and 2 lascannons.
- Terminators: two 5-model selections projected as accursed weapon + combi-bolter.
- Havocs: two 5-model selections; aggregate source projection contains 4 autocannons + 4 lascannons plus two champions.
- Helbrute: source projection uses missile launcher + multi-melta.
- Chaos Lord: daemon hammer + plasma pistol in the source roster.

None of those projections is yet treated as exact current physical WYSIWYG. Historical builds, conversions, magnetization and loose bits will supersede the roster projection when directly confirmed.

## Cross-domain identity gate

The Wave 1 roster contains one **Heretic Astartes Daemon Prince with wings**.

The repository already contains a user-confirmed **winged Black Legion-styled Daemon Prince** under `collection/chaos_daemons`.

Until the user confirms whether these are the same physical miniature, the overlap remains unresolved and no global collection total should double-count or deduplicate it automatically.

## Next reconciliation waves

The next work should not restart the import. Continue from this checkpoint and progressively resolve:

- missing models not represented in Wave 1;
- assembled vs on-sprue counts;
- Legionary weapon/body pools;
- Terminator historical loadouts;
- Havoc heavy-weapon bodies and loose bits;
- Helbrute weapon options/magnetization;
- character duplicates/variants;
- shared-body modern-role mappings;
- cross-domain Daemon Prince identity.
