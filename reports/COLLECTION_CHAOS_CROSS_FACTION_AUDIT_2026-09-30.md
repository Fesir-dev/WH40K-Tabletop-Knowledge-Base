# Chaos cross-faction collection audit — 2026-09-30

## Scope

Audit all currently registered Chaos collection domains as one physical network rather than isolated faction inventories.

Domains audited:

- Chaos Space Marines
- Thousand Sons
- World Eaters
- Chaos Daemons
- shared Chaos pool

Rules-only future interfaces also audited for:

- Death Guard
- Emperor's Children
- Chaos Knights

## Core invariant

A physical body is owned once.

Faction access, ally rules, imported datasheets, shared roles and proxy/cross-role mappings are references to that body and never create another physical miniature.

## Current normalized body accounting

- Chaos Space Marines — 155 confirmed unique bodies
- Thousand Sons — 109 source-declared bodies
- World Eaters — 48 unique bodies excluding shared Spawn
- Chaos Daemons — 340 normalized bodies
- shared Chaos — 10 Chaos Spawn

Total known cross-domain unique sum: **662**.

If the probable separate ten-model Legionaries box is physically reconfirmed:

- CSM becomes 165
- global sum becomes **672**

Verification depth differs by domain and is preserved in the source inventories.

## Formal current 11E bridges

### CSM — Cult of the Dark Gods

At Strike Force size, up to 500 points combined from:

- Khorne Berzerkers
- Rubric Marines
- Plague Marines
- Noise Marines

Owned:

- Khorne Berzerkers — 20
- Rubric Marines — 15
- Plague Marines — none recorded
- Noise Marines — none recorded

### CSM / Chaos Knights — Daemonic Pact

At Strike Force size, up to 500 points of LEGIONES DAEMONICA units.

Per-god gate:

non-BATTLELINE allied units cannot outnumber allied BATTLELINE units with the same god keyword.

Collection consequences:

- Khorne: supported by Bloodletters
- Tzeentch: supported by Horrors
- Slaanesh: supported by Daemonettes
- Nurgle: currently constrained by absence of Plaguebearers

### Chaos Daemons — Shadow Legion

At Strike Force size, up to 1000 points of the listed HERETIC ASTARTES roles.

Physical coverage:

- 13/15 role categories directly owned in CSM
- Sorcerer In Terminator Armour: two high-confidence physical candidates in Thousand Sons
- Raptors: not recorded

Haarken cannot be taken as Haarken under Shadow Legion's Epic Hero restriction, but the user's magnetized Haarken-derived body can be configured as the allowed Chaos Lord With Jump Pack role.

### Chaos Knights allies

If every model in the army has CHAOS, current Chaos Knights rules allow:

- either 1 TITANIC CHAOS KNIGHTS model
- or up to 3 WAR DOG models

No Chaos Knights physical collection is currently registered.

### Chaos Knights — Iconoclast Fiefdom

Can include up to 500 points of CSM DAMNED units.

Relevant owned CSM bodies include:

- Cultist Mob — 40
- Accursed Cultists — 8

This is future roster potential only until Chaos Knights bodies exist.

## God-legion direct daemon overlap

### World Eaters

Direct current daemon-role overlap:

- Bloodletters
- Bloodcrushers
- Bloodthirster
- Flesh Hounds
- Skarbrand

Collection coverage: **5/5 roles**, 39 daemon bodies.

### Thousand Sons

Direct current daemon-role overlap:

- Blue Horrors
- Pink Horrors
- Flamers
- Screamers
- Kairos Fateweaver
- Lord Of Change

Collection coverage: **6/6 roles**, 110 daemon bodies.

### Death Guard

Direct current daemon-role overlap:

- Beasts Of Nurgle
- Great Unclean One
- Nurglings
- Plague Drones
- Plaguebearers
- Rotigus

Collection coverage: **2/6 roles**.

Owned:
- Beasts Of Nurgle — 4
- Nurglings — 12

### Emperor's Children

Direct current daemon-role overlap:

- Daemonettes
- Fiends
- Keeper Of Secrets
- Seekers
- Shalaxi Helbane

Collection coverage: **5/5 roles**.

Two keeper-scale bodies permit simultaneous Keeper + Shalaxi representation by using the magnetized body as Shalaxi and the fixed body as Keeper.

## Confirmed shared bodies

### Chaos Spawn

10 globally owned:

- 1 Khorne-styled
- 2 Tzeentch-styled
- 7 universal

Canonical domain: `collection/chaos_shared`.

### Black Legion winged Daemon Prince

One body.

Canonical physical record: Chaos Daemons.

Also instantiates CSM Heretic Astartes Daemon Prince With Wings.

### Haarken / Jump Pack Lord

One magnetized Haarken-derived body.

Roles:

- Haarken Worldclaimer
- Chaos Lord With Jump Pack

Mutually exclusive.

## Sorcerer In Terminator Armour cross-role finding

Thousand Sons inventory contains 2 bodies.

Current CSM and Thousand Sons datasheets both use:

- 40 mm base
- force weapon
- combi-bolter/combi-weapon physical weapon family

Therefore both TS models are marked as **high-confidence physical-role candidates** for the separate CSM Sorcerer In Terminator Armour datasheet.

This does not import the Thousand Sons datasheet into CSM. The legal roster must select the HERETIC ASTARTES datasheet.

## Same-name datasheet overlap

Current non-Legends same-name overlap is broad.

Examples across CSM / god legions include:

- Chaos Rhino
- Chaos Land Raider
- Chaos Predator Annihilator
- Chaos Predator Destructor
- Chaos Spawn
- Defiler
- Helbrute
- Forgefiend
- Maulerfiend
- Heldrake
- Sorcerer
- Sorcerer In Terminator Armour
- Master Of Executions

These names identify future shared-pool candidates only. Existing physical models are not moved into shared ownership without direct user confirmation of body identity, styling and intended cross-faction use.

## Repository changes

Created:

- `collection/CHAOS_CROSS_FACTION_MATRIX.json`
- `collection/CHAOS_CROSS_FACTION_MATRIX.md`

Updated:

- CSM with Cult of the Dark Gods, Daemonic Pact and cross-role references
- Chaos Daemons with Shadow Legion collection coverage
- World Eaters with direct Khorne daemon references
- Thousand Sons with direct Tzeentch daemon references and Terminator Sorcerer cross-role candidates
- collection index with cross-faction graph pointer

## Source checks

Live current 11E checks performed 2026-09-30 against:

- Wahapedia Chaos Space Marines — Cult of the Dark Gods
- Wahapedia Chaos Daemons — Daemonic Pact and Shadow Legion
- Wahapedia Chaos Knights — all-CHAOS Knight ally rule and Iconoclast Fiefdom
- live CSM and Thousand Sons Sorcerer In Terminator Armour datasheets
- repository 2026-09-29 current roster views for CSM, World Eaters, Thousand Sons, Death Guard, Emperor's Children, Chaos Daemons and Chaos Knights

Games Workshop remains normative; the repository uses the live mirror for current structural cross-checking and preserves the authority boundary.

## Audit result

The user's Chaos collection should be treated as a **cross-faction physical network**.

The most important practical consequences are:

1. CSM gains 20 Berzerkers and 15 Rubrics through current formal rules without duplicate purchases.
2. CSM can draw from the user's huge daemon collection through Daemonic Pact.
3. Shadow Legion is already nearly fully physically supported by the CSM collection.
4. World Eaters and Thousand Sons gain large direct daemon pools from the existing Chaos Daemons collection.
5. Emperor's Children are already fully covered for all current Slaanesh-daemon overlap roles even though no EC marine collection exists yet.
6. Death Guard already has partial daemon-side coverage.
7. Shared Spawn, Daemon Prince and Haarken/Jump Lord bodies are now explicitly de-duplicated.
8. Future Chaos vehicles should be audited for cross-faction shared-body potential before assigning them permanently to one faction.
