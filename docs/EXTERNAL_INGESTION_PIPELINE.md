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
BCP ─────────────┐
Tabletop Herald ─┴─► raw event snapshots
                         │
              ┌──────────┴───────────┐
              ▼                      ▼
      Stat Check / Infinite      Listhammer
      Archive / Hutber               │
      aggregate performance          ▼
                              Meta Merge
                              list composition

BSData ─► Tactical Reroll ─► mathhammer + pick-rate model
profiles ─► UnitCrunch ────► independent simulation

Goonhammer / Art of War / Fireside / Vanguard / others
                         └─► attributed expert evidence

all analytics evidence
        ↓
lineage de-duplication
        ↓
patch/time-window alignment
        ↓
ROSTER_RECOMMENDATION_EVIDENCE_MODEL
        ↓
collection-aware recommendation

never ──► normative rules mutation
```

### Evidence lineage

A derived dashboard is not an independent dataset merely because it is a different website.

Examples:

- Infinite Archive performance data inherits BCP lineage.
- Meta Merge inherits Listhammer, which inherits BCP/Tabletop Herald event lineage.
- Hutber inherits BCP/Tabletop Herald for tournament evidence and BSData for list-building reference data.
- New Recruit/Tactical Reroll/Hutber can share BSData catalogue lineage.

Confidence synthesis therefore counts independent upstream lineages, not raw source count.

### Recommendation snapshots

Every substantial roster recommendation must retain:

- rules snapshot / points snapshot;
- analytics window start/end;
- patch/dataslate identity;
- faction / detachment / Force Disposition context;
- source IDs and lineage IDs;
- sample sizes where available;
- observed vs modelled vs expert evidence;
- counter-evidence;
- collection snapshot if collection-constrained;
- confidence and recommendation state.

See `analytics/ROSTER_RECOMMENDATION_EVIDENCE_MODEL.md`.

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

## Guarded automated re-ingestion

The upstream watcher now feeds a two-stage refresh path.

```text
upstream watcher
      ↓
deterministic reingestion plan
      ↓
isolated candidate workspace
      ↓
candidate snapshot + reconciliation + semantic audit
      ↓
reviewable GitHub Actions artifact
      ↓
explicit workflow_dispatch promotion
      ↓
new promotion branch
      ↓
post-apply upstream recheck
      ↓
New Recruit runtime revalidation
      ↓
semantic smoke + repository contracts
      ↓
promotion pull request
      ↓
human merge
```

Safety contract:

- candidate generation may be automatic;
- `auto_promote` is always `false`;
- a changed `BSDATA_MFM_11E` revision blocks this path until the official Games Workshop MFM revision is revalidated;
- a changed Wahapedia `Source.csv` requires a fresh official GW asset audit;
- candidate execution occurs in an isolated repository copy and may not mutate current authority pointers;
- promotion requires the exact candidate `plan_id` and fingerprint;
- promotion is applied only to a new branch and opens a PR; it never pushes promotion state directly to `main`;
- the promotion branch reruns the upstream watcher after pointer changes, so a source that moved again invalidates the proposal;
- New Recruit runtime drift must remain classified; new/unclassified runtime drift blocks promotion;
- normative GW/MFM authority is never changed by this mirror/implementation refresh path.

Relevant tooling:

- `tools/plan_upstream_reingestion.py`
- `tools/run_upstream_reingestion_candidate.py`
- `tools/apply_reingestion_promotion.py`
- `tools/sync_new_recruit_runtime_status.py`
- `.github/workflows/upstream-reingestion-candidate.yml`
- `.github/workflows/upstream-reingestion-promote.yml`
