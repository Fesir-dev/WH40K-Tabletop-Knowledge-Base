# Painting KB migration — v25 — 2026-09-29

## Source

`Ревизия_красок_база_техник_v25.xlsx`

- SHA-256: `1679f1a20dd1e4bc064fb96c577fa9d8c3f54f04a634756febef4abfe2cd7941`
- size: 497,616 bytes
- sheets: 70

The original workbook is preserved byte-for-byte under `hobby/painting/artifacts/original/`.

## Promoted canonical data

- physical paint/material inventory;
- 540-recipe catalogue;
- source/provenance registry;
- dated replacement-cost snapshot;
- army painting pipelines;
- active Demon Prince project stages/sessions;
- value-level export of every non-audit sheet.

## Intentionally historical-only

Workbook sheets whose names contain `аудит` remain preserved in the XLSX but were not promoted into current guidance. They document how the workbook evolved rather than the final operational state.

## CI invariants

The repository validator requires the source artifact SHA/size plus 217 containers/materials, 212 unique product identities, 5 brands, recipes 1–540, 20 Demon Prince stages, 12 sessions and the dated 143,088 RUB replacement-cost baseline.
