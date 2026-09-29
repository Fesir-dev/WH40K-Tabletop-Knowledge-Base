# Schemas

The repository uses explicit machine-readable contracts so source roles, rules snapshots, collection state and analytical recommendations remain reproducible.

Current/planned schema domains include:

1. source registry entries;
2. rules snapshots;
3. faction/unit semantics;
4. points snapshots;
5. collection body pools;
6. shared component/weapon pools;
7. physical allocation constraints;
8. roster snapshots;
9. competitive analytics snapshots;
10. roster recommendation evidence;
11. paint/material inventory;
12. migration records.

Implemented contracts include:

- `source_entry.schema.json` — source authority/role, lineage and provenance metadata.
- `collection_inventory.schema.json` — personal physical collection state.
- `roster_recommendation_evidence.schema.json` — patch-scoped, lineage-aware evidence for roster/unit/build recommendations.\n- `painting_inventory.schema.json` — personal paint/material inventory snapshots.\n- `painting_recipe_catalog.schema.json` — normalized painting recipe catalogue.

Schema evolution must be versioned and backwards-aware.

- `faction_catalog.schema.json` — complete roster-universe identities and hierarchy.
- `faction_coverage.schema.json` — measured normalized current coverage by faction/dimension.
- `ingestion_run.schema.json` — reproducible source-refresh/diff/promotion run record.
- `mfm_faction_snapshot.schema.json` — normalized current MFM page with exact extraction provenance.
