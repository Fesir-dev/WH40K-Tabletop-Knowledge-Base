# Official public overlap residual classification model

## Purpose

This model explains the semantic units left outside the exact source/faction-scoped official-public overlap snapshot.

It covers two residual sets:

- exact official-public text that is not safely source-scoped;
- current-mirror semantic units with no exact public-official match under the v1 comparison contract.

Residual classification is diagnostic evidence. It does not change Games Workshop authority and it does not create a semantic conflict by itself.

## Exact but unscoped classes

### `CORE_PUBLIC_GLOBAL`

The semantic text is exactly present in the public Core Rules but has no faction/source scope suitable for faction promotion.

### `NON_11_OR_LEGENDS_SOURCE`

The mirror object belongs to a non-11 or Legends source identity, while identical text also appears in current public official material.

Text reuse does not make the old/Legends object current.

### `EDITION_11_SOURCE_MATCH_OUTSIDE_OWN_PACK`

The mirror object points to an edition-11 source, but exact public evidence occurs only outside its own mapped official pack.

This can be shared/generic wording or another scope relationship. It remains non-promotable until stronger provenance is established.

### `FACTION_ONLY_MATCH_OUTSIDE_OWN_PACK`

The object has faction identity but no direct source identity, and the exact match occurs outside the faction's own mapped public pack.

It remains evidence-only.

## No-exact-public-overlap classes

### `TOO_SHORT_FOR_SAFE_AUTO_MATCH`

The semantic unit is below the conservative exact-match length/token threshold.

This is an automation limitation, not evidence of disagreement.

### `NON_11_OR_LEGENDS_SOURCE_NO_EXACT`

The mirror object belongs to a non-current/Legends source. Lack of overlap with the current public corpus is expected to remain non-promotable.

### `EDITION_11_SOURCE_NO_EXACT_PUBLIC_OVERLAP`

An edition-11 source object has no exact match in the registered public corpus.

Allowed interpretations remain open:

- Faction Pack supplemental scope does not contain the Codex/app wording;
- extraction/layout normalization prevents exact containment;
- current official wording differs;
- another official public source is required.

The classifier does not choose between these explanations.

### `FACTION_ONLY_NO_EXACT_PUBLIC_OVERLAP`

The object has faction scope but no direct public-source match.

### `NO_SOURCE_OR_FACTION_NO_EXACT`

The object lacks source/faction provenance sufficient for scoped official comparison.

## Non-negotiable boundary

None of the residual classes automatically means:

- `SOURCE_CONFLICT`;
- Games Workshop text is missing or wrong;
- Wahapedia text is wrong;
- Codex/app wording can be inferred;
- a faction is normatively complete.

The residual layer never increases `current_normalized_factions` and never creates semantic conflicts without additional official evidence.
