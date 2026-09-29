# Architecture

## Goal

Build one durable Warhammer 40,000 tabletop knowledge system rather than separate ad-hoc rule notes, collection lists and hobby inventories.

## Data flow

```text
external authority / implementation / analytics / personal observation
        ↓
source registry + role + provenance + freshness
        ↓
snapshot / diff / conflict detection
        ↓
normalized domain data
        ↓
derived runtime/indexes
        ↓
validation + regression + runtime projection checks
        ↓
queries / roster analysis / competitive analytics / hobby planning
```

## External-source planes

### Normative plane

Official Games Workshop sources define current rules/points within their scope.

### Mirror plane

Wahapedia provides a readable, fast-moving secondary projection used for discovery, cross-checking and drift detection.

### Structured implementation plane

BSData/wh40k-11e provides machine-readable catalogue semantics: unit structures, options, constraints, categories and roster validation logic.

### Runtime projection plane

New Recruit consumes catalogue data and shows how those semantics behave for players. Runtime disagreement with BSData is tracked as implementation/projection drift, not as a rules change.

### Analytics plane

Tournament results, statistical aggregations, list-composition feeds, mathematical models and expert analysis are stored separately from normative rules. They answer what is played, what performs and how experts interpret the environment — not what the rulebook says.

The analytics plane is internally split into:

```text
raw tournament evidence
    ↓
aggregate statistics / matchup data
    ↓
winning-list composition
    + mathhammer/model evidence
    + independent expert interpretation
    ↓
lineage-aware evidence synthesis
    ↓
collection-aware roster recommendation
```

Dependent transformations of the same raw tournament feed retain their upstream lineage and do not multiply confidence.

## Layering

### 1. Sources

Describes where a fact came from, source authority/role, version/date, retrieval/check date, checksum/commit when available and whether the source is current or historical.

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
- collection-aware army feasibility;
- patch-scoped competitive evidence vectors;
- lineage-aware roster recommendation support.

### 4. Historical snapshots

Immutable checkpoints retained to explain old rosters, rule changes and migration decisions.

## Cross-domain invariant

A legal army and a physically buildable army are different questions.

The target system therefore answers them in order:

1. Is the roster legal under a declared rules/points snapshot?
2. Can the user's physical collection instantiate it?
3. Which model/bit allocations are required?
4. Which purchases/build changes would make an infeasible roster possible?
5. Separately: how does the roster/faction perform in the dated competitive environment?

## Current bootstrap boundaries

The preserved rules baseline is from 2026-08-15 and remains historical until the current official-source refresh is complete.

The Custodes inventory baseline is from 2026-07-11 and is treated as `PROVISIONAL` until remaining physical uncertainty is resolved.
