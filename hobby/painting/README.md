# Painting Knowledge Base

This domain is the canonical repository view of the user's miniature-painting inventory, recipes, techniques, production pipelines and active painting projects.

## Current baseline

Imported from **Ревизия_красок_база_техник_v25.xlsx** on 2026-09-29.

Verified migration invariants:

- 217 physical paint/material containers;
- 212 unique product identities;
- 5 brands;
- 540 numbered recipes, IDs 1–540 without gaps;
- 20 stages in the active Demon Prince project;
- 12 planned Demon Prince sessions;
- dated baseline replacement-cost estimate: 143,088 RUB.

## Authority model

For personal ownership/state, direct inventory evidence in this domain is authoritative for the user's collection.

Recipes and techniques are working hobby knowledge, not manufacturer specifications unless an entry explicitly cites a manufacturer/source.

Price/replacement-cost data is always a dated estimate and must not be treated as current without a fresh market check.

## Layout

```text
current.json
source_manifest_v25.json
artifacts/original/            exact source workbook
inventory/snapshots/           physical paint/material inventory
recipes/                       normalized recipe catalogue
sources/                       source URLs/provenance from the workbook
economics/                     dated valuation snapshots
army_pipelines/                production painting pipelines
projects/daemon_prince/        active project state
imports/v25/                   value-level export of non-audit workbook sheets
```

## Migration policy

The exact XLSX remains preserved because it contains layout, formulas, historical audits and workbook-specific navigation.

The normalized JSON layer is the preferred machine-readable working authority.

Historical audit sheets were intentionally not promoted as current guidance. Their evidence remains preserved inside the original XLSX.
