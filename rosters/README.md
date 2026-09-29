# Rosters

Rosters are versioned snapshots, not authorities.

Every roster should declare:

- rules edition;
- points/MFM source and version;
- source/check date;
- faction/detachment;
- roster total;
- legality status;
- physical-feasibility status against a named collection snapshot.

Old roster points must never silently update the collection inventory.


## Collection-aware solver request

The first operational solver target is Adeptus Custodes.

Example:

```bash
python tools/solve_collection_roster.py \
  --input rosters/examples/custodes_feasible_ready.json
```

The result deliberately separates:

- **scoped MFM legality** — current points/sizes/detachment/cost relations that the MFM snapshot can establish;
- **full normative legality** — still `UNKNOWN_PENDING_NORMATIVE_APP` at the current repository authority boundary;
- **physical feasibility** — allocation against the named personal collection snapshot;
- **readiness** — whether owned bodies are ready or must be built;
- **conversion** — used only when explicitly enabled;
- **component feasibility** — checked only for declared/normalized components; unknown shared-component capacities fail closed.
