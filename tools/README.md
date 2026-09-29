# Tools

New tools in this directory operate on the repository's current architecture.

Historical scripts imported from the old Rules Assistant are stored under `legacy/rules_assistant_v0_9/tools/`. They are evidence and migration inputs; they are not automatically current runtime tools.

Core validation:

```bash
python tools/validate_repo.py
python -m unittest discover -s tests -v
```

Scoped currentness examples:

```bash
python tools/check_currentness.py --scope points
python tools/check_currentness.py --scope points --faction orks --require-coverage
python tools/check_currentness.py --scope faction_rules --faction adeptus_custodes --json
```

A source-current PASS is not a coverage PASS. Use `--require-coverage` when the question depends on data actually normalized into this repository.

## Current MFM query

```bash
python tools/query_mfm.py orks --summary
python tools/query_mfm.py adeptus_custodes --unit "Custodian Guard"
python tools/query_mfm.py imperial_fists --summary
```

`query_mfm.py` resolves repository roster identities to their MFM source page. For derived Codex-compliant Space Marine chapter views it applies `base_plus_group` unit filtering.


## Collection-aware roster solver

```bash
python tools/solve_collection_roster.py --input rosters/examples/custodes_feasible_ready.json
python tools/validate_collection_solver.py
```

Exit codes from `solve_collection_roster.py`:

- `0` — scoped rules checks pass and physical feasibility is known feasible;
- `2` — scoped MFM-backed legality failed;
- `3` — physical allocation is infeasible against the collection snapshot;
- `4` — physical feasibility is unknown because a required component constraint is unresolved.

The solver never upgrades runtime/BSData facts into normative rules and never upgrades a provisional personal collection snapshot into current verified inventory.
