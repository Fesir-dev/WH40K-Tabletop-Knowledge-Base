# External ingestion and update pipeline

## Goal

Continuously turn external Warhammer 40,000 information into versioned, attributable knowledge without conflating official rules, community implementations and competitive analysis.

## Rules pipeline

```text
GW official sources
      │
      ├─────────────┐
      ▼             ▼
Wahapedia 11E   BSData/wh40k-11e
 readable          structured
 mirror         implementation
      │             │
      └──────┬──────┘
             ▼
       source diff
             ▼
     conflict detection
             ▼
      normalized KB
             ▼
 validation/regression
             │
             ▼
       New Recruit
   runtime projection audit
```

## Analytics pipeline

```text
BCP / event results ──► empirical snapshots
Stat Check ───────────► aggregated meta snapshots
Goonhammer ───────────► attributed expert analysis
community discussion ─► issue/lead discovery

all ──► analytics domain
never ──► normative rules mutation
```

## BSData change ingestion

For every observed change to `BSData/wh40k-11e`:

1. record upstream commit SHA/date/message;
2. identify changed catalogues/factions;
3. classify changes:
   - points;
   - rules text;
   - unit composition;
   - wargear/options;
   - constraints;
   - keywords/categories;
   - detachments/enhancements;
   - validation logic;
4. compare against the prior BSData snapshot;
5. cross-check affected facts against Wahapedia;
6. verify normative facts against applicable official GW source before promotion;
7. run roster/regression validation;
8. check New Recruit runtime/wiki projection when practical.

## New Recruit integration

New Recruit is treated as a production runtime projection, not an independent rule authority.

Use it for:

- list import/export compatibility;
- runtime roster validation;
- checking whether BSData constraints behave as intended;
- comparing Wiki projection with source catalogue state;
- surfacing user-facing implementation bugs.

Candidate future tooling integration: New Recruit Data Editor's WebMCP tools (`nr_check`, `nr_find`, `nr_read`, etc.) for catalogue validation.

## Snapshot identity

External structured snapshots should retain:

- source ID;
- source version or Git commit SHA;
- checked/retrieved timestamp;
- affected edition/faction;
- content hash where practical;
- normalization version;
- previous snapshot link;
- conflict status.

Historical snapshots are immutable.
