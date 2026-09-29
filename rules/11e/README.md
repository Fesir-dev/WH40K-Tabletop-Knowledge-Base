# Warhammer 40,000 11E rules domain

## Bootstrap status

Legacy checkpoint: **2026-08-15**  
Repository bootstrap: **2026-09-29**  
Status: **CURRENT_PENDING_RECHECK**

The old Rules Assistant v0.9 remains the migration baseline. It previously included:

- core-rules semantic indexes;
- mission/tournament knowledge;
- live-source registry and conflict handling;
- MFM points/detachment layers;
- faction rules updates;
- dataslate semantics;
- Leader/Support graph;
- keyword membership;
- transport profiles;
- faction composition and roster validation;
- regression tests.

## Legacy certified counts

At the 2026-08-15 checkpoint the old project reported:

- 8 tracked factions;
- 282 current-MFM unit point entries;
- 79 detachments;
- 267 enhancement costs;
- 74 Leader/Support links;
- 169 stratagem semantic entries;
- 115 enhancement target predicates;
- 435 keyword membership assertions;
- 14 exact transport profiles;
- 18/18 current-runtime regression cases;
- 19/19 rules-engine regression cases.

These numbers describe the historical checkpoint, not the current state of the game.

## Migration policy

Reusable schemas, validators and derived semantics will be migrated selectively. Every migrated rules object must preserve its source/checkpoint and must not become `CURRENT_VERIFIED` until the official current source set has been checked.
