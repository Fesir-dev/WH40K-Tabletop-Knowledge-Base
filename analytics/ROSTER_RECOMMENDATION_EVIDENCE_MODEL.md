# ROSTER RECOMMENDATION EVIDENCE MODEL

## Purpose

Roster advice must answer **why this unit/build belongs in this roster**, not merely repeat a tier list.

A recommendation is built in layers:

```text
CURRENT LEGALITY
      ↓
TOURNAMENT PERFORMANCE
      + WINNING-LIST COMPOSITION
      + MATCHUPS / DISPOSITIONS
      + MATHHAMMER
      + EXPERT INTERPRETATION
      ↓
ROLE / MISSION FIT
      ↓
USER COLLECTION + LOADOUT FEASIBILITY
      ↓
EXPLAINABLE ROSTER RECOMMENDATION
```

## Hard gates

1. **Legality:** the roster must pass the declared rules/points snapshot.
2. **Patch alignment:** primary analytics must correspond to that rules/points state.
3. **Physical feasibility:** when building from the user's collection, owned bodies/bits/magnetization are checked independently.

No amount of meta popularity can override a failed legality gate.

## Competitive evidence vector

The default analytical balance is:

| Dimension | Weight |
|---|---:|
| Tournament performance | 30 |
| Winning-list composition | 20 |
| Matchup/disposition evidence | 15 |
| Mathematical efficiency | 15 |
| Expert consensus | 10 |
| Role/mission fit | 10 |

This is **not** a universal unit tier score. The vector is evaluated for a declared roster role and patch.

## Personal-fit vector

| Dimension | Weight |
|---|---:|
| Owned model coverage | 35 |
| Legal loadout/bits fit | 20 |
| Role coverage in the roster | 20 |
| Purchase/build friction | 15 |
| Explicit user preference/familiarity | 10 |

User preference is used only when explicitly known for the relevant choice; it must not be inferred.

## Do not double-count aggregators

If Infinite Archive and BCP describe the same BCP games, they are one empirical lineage.

If Meta Merge summarises Listhammer, which itself draws from BCP/Tabletop Herald, Meta Merge adds **composition analysis**, not another independent tournament sample.

## Minimum evidence quality

- faction/matchup samples below 30 games: weak;
- 30–99: directional;
- 100+: robust enough for stronger claims, subject to selection bias;
- winning-list composition below 5 readable lists: anecdotal;
- 5–9: directional;
- 10+: usable composition signal;
- expert “consensus” requires at least 3 independent expert sources.

These thresholds guide confidence, not mechanical truth.

## Patch boundaries

A September roster recommendation must not quietly pool a pre-MFM build with post-MFM results if the changed points/rules materially alter that build.

Every recommendation therefore records:

- rules snapshot;
- MFM/points state;
- analytics window;
- faction;
- detachment(s);
- Force Disposition where relevant;
- event format if relevant;
- collection snapshot when collection-constrained.

## Required recommendation output

For every substantial roster recommendation, report:

1. **Role:** what problem the unit/build solves.
2. **Legality:** exact current snapshot/gate state.
3. **Observed evidence:** tournament results, samples, take rates.
4. **Derived evidence:** mathhammer/model outputs.
5. **Expert evidence:** attributed reasoning/consensus.
6. **Counter-evidence:** weak matchups, low conversion, conflicting expert view, etc.
7. **Collection fit:** owned / buildable / missing pieces.
8. **Confidence:** HIGH / MEDIUM / LOW and why.
9. **Recommendation state:** e.g. `CORE_SUPPORTED`, `TECH_CHOICE`, `EXPERIMENTAL`.

Machine-readable rules live in `roster_recommendation_evidence_model.json`.
