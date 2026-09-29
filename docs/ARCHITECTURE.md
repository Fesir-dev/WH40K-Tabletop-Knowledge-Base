# Architecture

## Goal

Build one durable Warhammer 40,000 tabletop knowledge system rather than separate ad-hoc rule notes, collection lists and hobby inventories.

## Data flow

```text
external authority / personal observation
        ↓
source registry + provenance
        ↓
normalized domain data
        ↓
derived runtime/indexes
        ↓
validation + regression
        ↓
queries / roster analysis / hobby planning
```

## Layering

### 1. Sources

Describes where a fact came from, source authority, version/date, retrieval/check date, checksum when available and whether the source is current or historical.

### 2. Normalized knowledge

Stable facts expressed independently from presentation:

- rules concepts;
- faction/unit metadata;
- points snapshots;
- leader/support/transport/keyword relations;
- owned bodies and bits;
- paints and materials.

### 3. Derived runtime

Indexes and solver-oriented structures produced from normalized knowledge. They should be regenerable.

Examples:

- roster legality indexes;
- keyword membership closures;
- transport eligibility;
- physical model allocation constraints;
- collection-aware army feasibility.

### 4. Historical snapshots

Immutable checkpoints retained to explain old rosters, rule changes and migration decisions.

## Cross-domain invariant

A legal army and a physically buildable army are different questions.

The target system therefore answers them in order:

1. Is the roster legal under a declared rules/points snapshot?
2. Can the user's physical collection instantiate it?
3. Which model/bit allocations are required?
4. Which purchases/build changes would make an infeasible roster possible?

## Current bootstrap boundaries

The rules baseline is from 2026-08-15 and must be revalidated before receiving `CURRENT_VERIFIED`.

The Custodes inventory baseline is from 2026-07-11 and is treated as `PROVISIONAL` until the remaining physical uncertainty is resolved.
