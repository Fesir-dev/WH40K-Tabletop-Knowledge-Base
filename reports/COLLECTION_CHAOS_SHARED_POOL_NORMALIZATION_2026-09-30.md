# Shared Chaos physical-pool normalization — 2026-09-30

## Purpose

Prevent cross-faction double-counting where the same physical models are used by several Chaos armies, and resolve another CSM shared-body identity.

## Chaos Spawn

The user confirmed one global physical pool of **10 Chaos Spawn** across Chaos collections:

- Khorne-styled — 1
- Tzeentch-styled — 2
- visually universal — 7

These are ten bodies total, not separate faction-owned Spawn pools.

### Previous incorrect projection

The World Eaters New Recruit export selected six Chaos Spawn and the initial physical import therefore created a six-body World Eaters Spawn pool.

That interpretation is superseded.

The six models were a roster allocation from the shared physical pool, not evidence of six World Eaters-owned Spawn bodies.

### Canonical model

A new canonical domain is created:

`collection/chaos_shared/`

Faction domains reference `chaos_spawn_shared` but contribute zero local physical bodies.

Initial references are recorded from:

- Chaos Space Marines
- World Eaters
- Thousand Sons

The physical allocation rule is global: the same Spawn body cannot instantiate two simultaneous rosters.

## Haarken / Chaos Lord with Jump Pack

The user confirmed that the apparent Haarken and Jump Pack Lord entries are **one physical miniature**.

Physical facts:

- base model: Haarken Worldclaimer;
- converted;
- magnetized;
- can be configured as Haarken Worldclaimer;
- can be configured as Chaos Lord with Jump Pack;
- roles are mutually exclusive.

The CSM inventory previously counted both roster roles as one body each. The Jump Pack Lord role now contributes zero additional bodies.

## Legionaries probable acquisition layer

The user recalls the Legionary body universe as:

- 20 bodies from two Shadowspear sets — confirmed;
- 5 newer-Chosen-derived bodies built for the Word Bearers Kill Team — confirmed;
- 10 bodies from a separate Legionaries box — probable acquisition, not yet physically reconfirmed.

Therefore:

- confirmed Legionary bodies: **25**
- probable Legionary bodies if the separate box is reconfirmed: **35**

The probable ten are not promoted into the confirmed physical total until their current location/build state is rechecked.

## Count consequences

Before Haarken/Jump-Lord de-duplication, the confirmed unique CSM-domain lower bound was 156.

After shared-body correction:

**155 confirmed unique CSM bodies/models**.

If the remembered separate ten-model Legionaries box is physically reconfirmed:

**165 probable CSM bodies/models**.

The shared Chaos Spawn pool remains outside those faction-domain totals and contains **10 physical bodies** globally.

## Governance result

- shared Spawn ownership: normalized once globally;
- old World Eaters six-Spawn ownership interpretation: superseded by shared-pool reference;
- Haarken / Jump Pack Lord double-count: resolved;
- separate ten-model Legionaries box: preserved as probable, not silently promoted to exact;
- repository physical-count semantics remain body-first and fail-closed.
