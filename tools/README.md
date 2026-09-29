# Tools

New tools in this directory operate on the repository's current architecture.

Historical scripts imported from the old Rules Assistant are stored under `legacy/rules_assistant_v0_9/tools/`. They are evidence and migration inputs; they are not automatically current runtime tools.

Initial gate:

```bash
python tools/validate_repo.py
```

The validator intentionally uses only Python's standard library so the basic repository integrity check has no dependency bootstrap.
