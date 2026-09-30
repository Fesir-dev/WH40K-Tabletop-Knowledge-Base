# Adeptus Mechanicus collection baseline import — 2026-09-30

## Scope

Initial physical-collection normalization from the user-supplied New Recruit file `Коллекция мехов.json`.

This milestone deliberately does **not** attempt the final physical reconciliation. The user has already flagged known undercount areas and requested a later loadout audit.

## Baseline extraction

| Pool | Source bodies |
| --- | ---: |
| Belisarius Cawl | 1 |
| Cybernetica Datasmith | 2 |
| Skitarii Marshal | 1 |
| Tech-Priest Dominus | 2 |
| Tech-Priest Enginseer | 2 |
| Tech-Priest Manipulus | 1 |
| Technoarcheologist | 2 |
| Skitarii Rangers | 30 |
| Skitarii Vanguard | 20 |
| Kataphron Destroyers | 3 |
| Sicarian Infiltrators | 20 |
| Sicarian Ruststalkers | 30 |
| Ironstrider Ballistarii | 6 |
| Kastelan Robots | 4 |
| Onager Dunecrawler | 2 |
| Sydonian Dragoons with taser lances | 4 |
| Skorpius Dunerider | 1 |
| **Total represented by export** | **131** |

## User-confirmed incompleteness

The export is a lower bound rather than the final collection inventory.

- Skitarii Rangers: likely more than 30; exact extra count unknown.
- Skitarii Vanguard: likely more than 20; exact extra count unknown.
- Sicarian Infiltrators: additional Princeps/leader bodies exist; exact extra count unknown.
- Sicarian Ruststalkers: additional Princeps/leader bodies exist; exact extra count unknown.

Because at least one extra Princeps body exists for each Sicarian type, the collection has a **confirmed physical minimum of 133 models** even before Rangers/Vanguard are re-counted.

## Source-selected configurations retained

The source export contains model-level selected variants. These are preserved as `SOURCE_MODEL_SELECTION_CONFIGURATION_SNAPSHOT` evidence.

Examples:

- Rangers: 3 Alpha, 2 arc rifle, 2 plasma caliver, 2 transuranic arquebus, 2 data-tether, 19 galvanic rifle.
- Vanguard: 2 Alpha, 1 plasma caliver, 1 transuranic arquebus, 1 data-tether, 15 radium carbine.
- Infiltrators: 3 Princeps + 17 regular bodies in the represented source selections.
- Ruststalkers: 3 Princeps + 27 regular bodies in the represented source selections.
- Ironstriders: 6 source-selected twin cognis lascannon bodies.
- Dragoons: 4 source-selected taser-lance bodies.

These **must not** yet be read as verified physical wargear availability. The user explicitly plans a later revision of actual loadouts.

## Provenance

- Source: `Коллекция мехов.json`
- SHA-256: `62155c7682df465d64155aeea237d4fe7b9600b14cce397438a72e787891e960`
- Generator: New Recruit
- Game system: Warhammer 40,000 11th Edition, revision 14
- Catalogue: Imperium - Adeptus Mechanicus, revision 17
- Source roster points: 3530 — retained as non-authoritative metadata only.

## Next revision gate

The next Adeptus Mechanicus collection pass should resolve, in order:

1. exact Ranger body count;
2. exact Vanguard body count;
3. exact number of extra Infiltrator Princeps bodies;
4. exact number of extra Ruststalker Princeps bodies;
5. physical build state for each pool;
6. actual assembled/magnetized/interchangeable weapon configurations;
7. loose weapon/arm/component pools.

Until then, the inventory remains `PROVISIONAL`.
