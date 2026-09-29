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
