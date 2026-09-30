# Adeptus Mechanicus Skitarii physical reconciliation — closure — 2026-09-30

## Closure status

Rangers and Vanguard are now physically reconciled at aggregate-count and fixed-loadout level.

New Recruit remains source/configuration provenance only. Direct physical observation is the collection authority for the counts below.

## Rangers

Exact physical total: **24**

| Physical variant | Bodies |
| --- | ---: |
| Ranger Alpha | 2 |
| Transuranic arquebus | 3 |
| Plasma caliver | 2 |
| Arc rifle | 2 |
| Enhanced data-tether | 1 |
| Omnispex | 1 |
| Galvanic rifle only | 13 |
| **Total** | **24** |

Alpha configurations:

- Alpha A: arc pistol + user-described taser sword.
- Alpha B: arc pistol + user-described mace.

The earlier pass-2 discrepancy is resolved by direct correction: Rangers have **2 plasma** and **2 arc rifles**, not 3 of each.

## Vanguard

Exact physical total: **14**

| Physical variant | Bodies |
| --- | ---: |
| Current Vanguard Alpha | 1 |
| Plasma caliver | 3 |
| Transuranic arquebus | 1 |
| Arc rifle | 0 |
| Enhanced data-tether | 1 |
| Omnispex | 1 |
| Radium carbine only | 7 |
| **Total** | **14** |

Current Alpha:

- radium pistol + power sword;
- radium carbine visibly carried on the backpack as a WYSIWYG conversion.

One of the seven ordinary radium-carbine troopers wears an Alpha-style helmet. The user now treats that miniature as an ordinary Vanguard; it was likely used as an Alpha in an older edition. The helmet is therefore historical/cosmetic rather than a current role assignment.

This resolves the earlier Vanguard 7-vs-6 arithmetic conflict.

## Fixed support wargear

For both Rangers and Vanguard:

- enhanced data-tether bearers are glued fixed models;
- omnispex bearers are glued fixed models;
- these are not magnetized or interchangeable component pools.

## Data-model consequence

The prior roster-derived `body_variants` representation was removed for Rangers/Vanguard and retained only under `source_configuration_snapshot`.

Direct physical observations now live under `user_observed_physical_variants`.

This prevents future tools from interpreting a historical New Recruit squad configuration as the user's physical inventory.

## Current collection totals

Replacing the source-export 30 Rangers and 20 Vanguard with direct physical totals of 24 and 14 yields **119 normalized known bodies** across the currently quantified Adeptus Mechanicus pools.

At least two additional Sicarian Princeps/leader bodies remain user-confirmed but not exactly counted, so the current collection floor remains **121 physical models**.

## Remaining gates

Skitarii Ranger/Vanguard reconciliation: **CLOSED**.

Still open:

1. exact extra Sicarian Infiltrator Princeps count/loadouts;
2. exact extra Sicarian Ruststalker Princeps count/loadouts;
3. physical loadout verification for remaining Mechanicus pools.
