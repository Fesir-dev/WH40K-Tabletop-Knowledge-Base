# Migration batch 02 — 2026-09-29

## Goal

Move the reusable machine semantics from Rules Assistant v0.9 into the new repository without confusing the 2026-08-15 historical `current` state with present-day current rules.

## Added

- 69-file semantic-core checksum/index covering 959,003 uncompressed bytes in the source archive.
- Historical global composition constraints.
- Historical transport profiles.
- Historical current-runtime regression cases.
- Historical interaction-engine regression cases.
- Historical enhancement alias reconciliation.
- Custodes source manifest.
- Custodes MFM v1.2 points.
- Custodes MFM v1.2 detachments/enhancement costs.
- Custodes Leader graph.
- Dated Custodes snapshot manifest.
- Collection-vs-points repricing audit.

## Verified historical repricing

The v0.5 collection roster stored **4000 points** of Custodes entries plus **485 points** of shared Imperial Agents.

Repricing the same Custodes rows against the repository's historical MFM v1.2 snapshot gives **3970 points**.

The -30 points are:

- Custodian Wardens (5): 260 → 250;
- first Venatari Custodians (3): 160 → 150;
- second Venatari Custodians (3): 160 → 150.

This calculation is historical and is not a claim about current September 2026 points.

## Byte-preservation note

`SEMANTIC_CORE_FILE_INDEX.json` records SHA256 values of the original files inside the uploaded v0.9 archive. Some files migrated into GitHub are semantically equivalent JSON reserializations, so their Git blob bytes are not expected to match those original source-file SHA256 values. The original archive checksum remains the immutable baseline identity.
