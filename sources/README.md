# Sources and provenance

This directory records **where knowledge came from**, why the source is trusted for a particular purpose, and what it is *not* allowed to establish.

## Authority is role-specific

There is no single flat source ranking for every question.

- **Normative rules:** current applicable Games Workshop evidence is authoritative.
- **Readable mirror:** Wahapedia is the preferred current secondary mirror and discovery/cross-check surface.
- **Structured roster implementation:** BSData/wh40k-11e is the preferred machine-readable community implementation.
- **Runtime behavior:** New Recruit app/Wiki shows how catalogue data reaches players.
- **Competitive analytics:** BCP/Stat Check provide empirical evidence; Goonhammer provides attributed expert analysis.
- **Event overlays:** WTC and event packs apply only inside their declared scope.
- **Personal collection:** direct user observation/confirmation outranks roster inference.

See `SOURCE_AUTHORITY_MATRIX.md`, `conflict_policy.json` and `freshness_policy.json`.

## Required behavior

A current normative rules claim cannot become `CURRENT_VERIFIED` from secondary agreement alone.

Wahapedia, BSData and New Recruit are deliberately independent checks:

- Wahapedia helps detect/read current rule drift;
- BSData exposes machine-readable implementation semantics;
- New Recruit exposes runtime projection behavior.

Their disagreement is evidence to investigate, not permission to guess.

Analytics and expert opinion must remain in an analytics/analysis domain and never mutate normative rules facts.
