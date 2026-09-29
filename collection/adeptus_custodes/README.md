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

## Collection-aware solver

The narrative constraints now have a derived solver profile:

`solver_profile.json`

Runtime:

`tools/solve_collection_roster.py`

The solver can allocate shared bodies, distinguish ready vs on-sprue bodies, gate explicit conversions, validate declared component stock, and fail closed when a component constraint is still unknown.

Important boundary: the collection snapshot remains **PROVISIONAL**. Solver feasibility is always feasibility **against this snapshot**; it does not promote the personal inventory to `CURRENT_VERIFIED`.

The solver currently checks the MFM-backed subset of rules legality (unit existence, legal MFM size/copy-tier price, detachment existence, enhancement and paid-wargear costs, and declared Leader relations). Full normative army legality remains `UNKNOWN_PENDING_NORMATIVE_APP` until the repository closes that separate authority gap.
