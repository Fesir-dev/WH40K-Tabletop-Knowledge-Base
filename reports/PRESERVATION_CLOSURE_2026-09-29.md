# Preservation closure — 2026-09-29

## Verdict

**LEGACY_ARCHIVES_PRUNE_SAFE = YES**

The two bootstrap uploads no longer need to be kept separately for data preservation.

## Exact preservation

Both source ZIP archives are now stored as exact binary Git blobs under `legacy/artifacts/original/`.

### Rules Assistant v0.9

- original SHA-256: `98bbc892879e9211fadaff158efbd98321b704e0c56e6dd84df2ef69e9b00947`
- size: 883,437 bytes
- 364 ZIP entries = 350 files + 14 directories
- 3,325,692 uncompressed file bytes
- contents: 187 JSON, 119 Markdown, 33 Python, 6 CSV, 2 SQLite DB, 2 JSONL, 1 TXT

### Adeptus Custodes collection v0.5

- original SHA-256: `6aee2f7bf491f4fe6f254aeecf79dffe84a5579e24a3022aafcea422b9e97f20`
- size: 32,347 bytes
- 4 files
- 250,473 uncompressed file bytes
- contents: 3 JSON + 1 Markdown

## Independent backup

Exact copies also exist under:

`/Google Drive/WH40K-Tabletop-Knowledge-Base-Archive/`

Drive reports exactly the same byte sizes as the source uploads.

The complete Drive base64 payloads were compared against the complete GitHub binary-file base64 payloads and matched exactly for both archives.

## Integrity enforcement

`tools/validate_repo.py` verifies:

- artifact presence;
- exact byte size;
- exact SHA-256.

Therefore accidental replacement, truncation or corruption of either preserved legacy ZIP causes CI failure.

## Meaning of PRUNE_SAFE

The original chat uploads/local duplicate copies may now be removed without losing information contained in them.

This does **not** mean the historical rules inside them are current. Their rules/points remain historical snapshots until the current-source refresh is complete.
