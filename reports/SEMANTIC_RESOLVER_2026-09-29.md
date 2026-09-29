# Semantic resolver verification — 2026-09-29

## Status

**LIVE HASH-VERIFIED: PASS**

GitHub Actions run: `36579177714`.

The resolver does not store long rules prose. It fetches the requested current Wahapedia 11E CSV row, calculates SHA-256 and compares it with the fingerprint stored in the committed structural snapshot.

## Live smoke checks

Eight representative semantic surfaces were checked against the committed 2026-09-29 snapshot and all returned `SNAPSHOT_MATCH`:

1. datasheet ability;
2. datasheet option / wargear constraint prose;
3. unit composition;
4. datasheet loadout;
5. detachment ability;
6. enhancement;
7. stratagem;
8. global/core/faction ability.

The smoke sample used current Custodes structural entities plus a global ability entry. Exact long prose is intentionally not copied into this report.

## Drift behavior

A SHA mismatch is reported as `SOURCE_DRIFT` and exits non-zero. Changed text is not silently treated as snapshot-matched current rules.

## Authority

This mechanism verifies that the **Wahapedia current-mirror projection** still matches the committed fingerprints. It does not override Games Workshop. MFM remains normative for points/cost-bearing fields, and official GW rules/FAQ/app evidence remains the normative layer for rule disputes.

## Remaining work

This resolver makes full semantics operational on demand, but it is not the same as fully normalized semantic coverage. Repository-wide semantic rule extraction/typing and complete official FAQ/errata binding remain pending.
