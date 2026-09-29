# Adeptus Custodes collection

Baseline: **v0.5-provisional-r2**  
Original checkpoint: **2026-07-11**  
Repository migration: **2026-09-29**  
Status: **PROVISIONAL**

## Confirmed physical totals

- 75 models including shared Imperial Agents.
- 70 Custodes/Sisters excluding those shared agents.
- 5 shared Imperial Agents.

## Important physical constraints already modeled

- Guard-derived Shield-Captains share bodies with ordinary Custodian Guard.
- One magnetized Forge World captain body can represent Shield-Captain or Blade Champion.
- Allarus Captains consume bodies from the same nine-model Allarus pool.
- Dawneagle Shield-Captains consume frames from the same six-bike pool.
- Nine complete Sagittarum are confirmed.
- Ten Wardens exist, with shoulder-pad availability still the remaining open inventory question.
- Ten Sisters of Silence bodies are on sprue; weapon-bit stock is not the limiting factor.
- Six Venatari have pistol+buckler sets and can draw lance components from the Guard spear pool.
- One Caladius hull supports alternative main weapons.
- Two magnetized Telemon hulls share two copies of each arm type.

## Migration correction

The old legacy manifest said “5 built boltguns, 5 unbuilt” for Sisters, while the normalized inventory states **0 built / 10 on sprue**. The normalized inventory is treated as the stronger and later internal representation.

## Next target

Convert narrative hard constraints into solver-ready predicates so roster validation can answer both:

- rules legality;
- physical feasibility from the owned collection.
