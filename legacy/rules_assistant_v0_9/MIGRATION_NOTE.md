# Legacy migration note

The original v0.9 ZIP is registered by its archive SHA256 in `sources/baselines/legacy_baselines.json`.

`SEMANTIC_CORE_FILE_INDEX.json` records the original per-file byte size and SHA256 for the selected 69-file semantic core.

Files copied into this public repository may be **JSON-reserialized** for compactness/readability. Therefore:

- semantic content is intended to be preserved;
- GitHub file bytes are not necessarily byte-identical to the source ZIP member;
- the checksum index is the authority for original-byte identity;
- later current-runtime files must be re-derived from present sources rather than silently promoted from legacy.
