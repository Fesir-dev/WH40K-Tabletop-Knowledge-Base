# Competitive analytics evidence architecture — 2026-09-29

## Scope

This pass turns competitive/meta research into a durable repository contract for explainable roster recommendations.

## Registered evidence families

### Raw tournament evidence
- Best Coast Pairings
- Tabletop Herald

### Aggregate statistics
- Stat Check
- The Infinite Archive
- Hutber Stats
- WarpFriends

### Winning-list composition
- Listhammer
- Meta Merge
- 40K Meta Tracker

### Mathematical/model evidence
- Tactical Reroll
- UnitCrunch

### Expert interpretation/coaching
- Goonhammer
- Art of War 40K
- 40K Fireside / Atlas
- Vanguard Tactics
- Auspex Tactics
- Grimdark Breakdown

### Architecture/tooling reference
- 40kdc-data

## Critical design rule

Source count is not evidence count.

Several analytics products inherit the same underlying tournament data:

```text
BCP ──► Infinite Archive
   ├──► Hutber
   └──► Listhammer ──► Meta Merge

Tabletop Herald ──► Hutber
                └─► Listhammer ──► Meta Merge
```

The recommendation model therefore deduplicates confidence by lineage.

## Recommendation contract

A competitive recommendation now requires:

- current legality/rules snapshot;
- points snapshot;
- analytics window and patch alignment;
- intended roster role;
- observed performance evidence;
- winning-list composition evidence;
- matchup/disposition evidence where available;
- mathhammer/model evidence;
- attributed expert evidence;
- counter-evidence;
- physical collection/build feasibility when collection-constrained;
- confidence and recommendation state.

Popularity, mathematical efficiency and expert opinion are deliberately kept separate.

## Machine-readable implementation

- `analytics/ANALYTICS_SOURCE_MATRIX.json`
- `analytics/roster_recommendation_evidence_model.json`
- `schemas/roster_recommendation_evidence.schema.json`

CI validates required sources, roles, dependencies, lineage metadata and evidence-model invariants.
