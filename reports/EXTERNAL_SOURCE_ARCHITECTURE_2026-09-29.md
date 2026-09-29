# External source architecture — 2026-09-29

## Decision

Replace the old flat external-source hierarchy with role-specific source planes.

## Added source planes

1. **Normative** — Games Workshop official rules, updates, MFM and app.
2. **Current mirror** — Wahapedia 11E.
3. **Structured implementation** — BSData/wh40k-11e.
4. **Runtime projection** — New Recruit app and Wiki.
5. **Analytics / expert analysis** — BCP, Stat Check and Goonhammer.
6. **Event/community overlays** — WTC and issue/community intelligence.

## New Recruit finding

For Warhammer 40,000 11E, New Recruit is treated as a downstream runtime consumer/projection of community catalogue data, with `BSData/wh40k-11e` as the key machine-readable upstream tracked by this repository.

Observed BSData head during the research pass:

- SHA: `951d5900d1b4a952a4ba560a30c43788e622ccfc`
- date: 2026-09-27
- message: `Fix weapon limits for Berzerkers`

The exact New Recruit synchronization/polling interval was not established and remains explicitly unknown.

## Operational consequence

A future current-rules refresh will no longer be a single-source scrape. It will produce a multi-plane diff:

```text
GW official
  ↕
Wahapedia
  ↕
BSData
  ↓
New Recruit runtime

plus separate dated analytics:
BCP / Stat Check / Goonhammer
```

Normative promotion still requires official evidence.
