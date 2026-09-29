# Wave B — Wahapedia structural ingestion

Wave B uses Wahapedia's documented 11E CSV export as a readable/structured secondary projection.

Wahapedia's Data Export page states that the export contains linked CSV files for datasheets, abilities and stratagems and that export files are updated as the site is updated. The repository does **not** treat this as normative authority; Games Workshop remains authoritative.

## Public-repository copyright policy

The generated snapshot intentionally does not vendor long rule prose.

Stored directly:

- faction/source IDs and versions;
- datasheet names/roles/links;
- model characteristics;
- weapon profiles and weapon keywords;
- keywords;
- point rows (for cross-check only; MFM remains normative);
- leader-link rows;
- detachment/enhancement/stratagem names and metadata.

Long descriptions/loadout prose are represented by SHA-256 fingerprints plus source links. Exact wording is fetched from the external source when needed.

## Promotion model

The workflow first generates a structural snapshot with `promotion=NONE`.

Only a later reviewed step can update `coverage/current.json` after:

1. schema and count checks pass;
2. source edition/version is confirmed as 11E;
3. faction mapping is reviewed;
4. BSData/MFM cross-checks are run;
5. release-transition rules are respected.
