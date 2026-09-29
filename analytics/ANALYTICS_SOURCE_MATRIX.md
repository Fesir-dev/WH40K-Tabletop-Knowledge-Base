# ANALYTICS SOURCE MATRIX

This matrix defines which external sources can support **roster and competitive decisions**. It is intentionally separate from rules authority.

## Core rule

**More websites do not automatically mean more evidence.** If several sites transform the same BCP or Tabletop Herald event feed, they share an evidence lineage and must not be counted as independent confirmations.

## P0 — core ingestion

| Source | Role | Best use | Key limitation |
|---|---|---|---|
| BCP | raw tournament evidence | events, pairings, placements, lists | event/access coverage varies |
| Tabletop Herald | raw tournament evidence | events, pairings, lists, European coverage | platform/regional selection |
| Stat Check | aggregate statistics | WR, representation, matchups, Elo | upstream lineage must be audited |
| Infinite Archive | advanced statistics | confidence intervals, matchups, top-cut, VP/consistency | performance data is BCP-derived |
| Listhammer | winning-list feed | current X-0/X-1 lists, detachments, dispositions | winner-only feed; not win rate |
| Meta Merge | winning-list composition | spine/flex/tech, consensus build, momentum | derived from Listhammer; not independent |

## P1 — strong supporting layer

- **Tactical Reroll:** unit mathhammer + recent tournament pick data.
- **Hutber Stats:** integrated faction/detachment/unit/player analytics.
- **40K Meta Tracker:** curated top-table builds for practice.
- **UnitCrunch:** independent probability/Monte Carlo cross-check.
- **Goonhammer:** competitive editorial, Ruleshammer and list analysis.
- **Art of War 40K:** high-level tournament/list construction expertise.
- **40K Fireside / Atlas:** matchup and deployment coaching plus player intelligence.
- **40kdc-data:** architecture/schema reference, not a meta authority.

## P2 — supplementary opinions / digests

- Vanguard Tactics
- WarpFriends
- Auspex Tactics
- Grimdark Breakdown

These are useful for alternative explanations, quick reaction and disagreement discovery, but they should not outweigh stronger empirical evidence solely because they are more recent or more confident in tone.

## Evidence lineage examples

```text
BCP
 ├─ Infinite Archive performance layer
 ├─ Hutber (part)
 └─ Listhammer (part)
      └─ Meta Merge

Tabletop Herald
 ├─ Hutber (part)
 └─ Listhammer (part)
      └─ Meta Merge

BSData/wh40k-11e
 ├─ New Recruit
 ├─ Tactical Reroll (rules/stats layer)
 ├─ Hutber list-building reference
 └─ Meta Merge catalogue/model-count layer
```

Therefore a recommendation supported by BCP + Infinite Archive + Meta Merge is **not** three independent empirical confirmations.

Machine-readable detail lives in `ANALYTICS_SOURCE_MATRIX.json`.
