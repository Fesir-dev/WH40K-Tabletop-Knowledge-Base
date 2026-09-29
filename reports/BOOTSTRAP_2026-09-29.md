# Bootstrap report — 2026-09-29

## Input artifacts

### Rules Assistant

- artifact: `W40K_11E_RULES_ASSISTANT_v0_9_FULL_FACTION_SEMANTICS_20260815(1).zip`
- SHA-256: `98bbc892879e9211fadaff158efbd98321b704e0c56e6dd84df2ef69e9b00947`
- uploaded archive entries: 364
- legacy project manifest entries: 348
- checkpoint: 2026-08-15

### Custodes collection

- artifact: `W40K_COLLECTION_INVENTORY_v0_5_ADEPTUS_CUSTODES_PROVISIONAL(2).zip`
- SHA-256: `6aee2f7bf491f4fe6f254aeecf79dffe84a5579e24a3022aafcea422b9e97f20`
- archive entries: 4
- checkpoint: 2026-07-11

## Bootstrap decisions

- New repository is broader than 11E and will persist across editions.
- Rules and collection data are separate domains.
- Old current-runtime data is demoted to `CURRENT_PENDING_RECHECK` until refreshed against present sources.
- Historical checkpoints remain immutable.
- Large/verbatim official rule texts are not mirrored into the public repository.
- Collection inventory is migrated first because it is user-owned factual state and enables later physical-feasibility solving.

## Known legacy issue captured during migration

The v0.5 collection manifest contains stale Sisters wording (“5 built boltguns, 5 unbuilt”) while the normalized inventory records all ten bodies on sprue. The normalized inventory is preferred.

## Next migration batches

1. Formalize collection constraints into schemas/predicates.
2. Migrate reusable source registry/reconciliation contracts.
3. Migrate current-runtime validators as historical code, then adapt them to the new layout.
4. Re-check current official 11E rules/points and generate explicit diffs from the 2026-08-15 checkpoint.
5. Import the paint/material project.
