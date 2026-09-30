# Core Rules paragraph atomization v1 closure — 2026-09-30

## Result

**PASS — all 310 verified Core Rules paragraph-boundary candidates now have stable copyright-safe structural identities.**

## Source and parent gates

The layer remains downstream of the verified Games Workshop public 11E Core Rules source and the closed paragraph-boundary layer.

Before atomization the pipeline verifies:

- official Core Rules binary SHA-256;
- all **88 / 88** page semantic fingerprints;
- full document semantic SHA-256;
- parent boundary snapshot **PASS**;
- parent rules: **141**;
- parent occurrences: **146**;
- parent paragraph candidates: **310**;
- heading recovery gaps: **0**;
- empty body boundaries: **0**.

The paragraph builder additionally recomputes **310 / 310 paragraph semantic hashes** directly from the verified PDF character ranges.

## Atomization result

Generated snapshot:

`rules/11e/snapshots/2026-09-30/core_rule_paragraph_atoms/index.json`

Compact report:

`reports/CORE_RULE_PARAGRAPH_ATOMIZATION_CURRENT.json`

Exact result:

- paragraph atoms: **310**;
- unique paragraph keys: **310**;
- parent rules represented: **141**;
- parent occurrences represented: **146**;
- Core families represented: **24**;
- single-occurrence paragraph atoms: **300**;
- repeated-occurrence paragraph variants: **10**;
- range validation failures: **0**;
- paragraph hashes reproduced from verified PDF: **310 / 310**.

## Stable identity

Paragraph identity is structural and source-version scoped:

`<occurrence_key>--para-p<page>-o<ordinal_on_page>`

Each atom retains:

- parent rule reference/key/family;
- parent occurrence key and occurrence ordinal;
- paragraph ordinal in the occurrence;
- page plus line/character range;
- line/character/token counts;
- paragraph semantic SHA-256;
- parent page semantic SHA-256;
- parent occurrence body semantic SHA-256.

No paragraph prose is committed.

## Repeated occurrence variants

The five repeated Core rules remain:

- `15.07`;
- `15.08`;
- `15.09`;
- `15.10`;
- `15.11`.

They contribute **10** paragraph atoms classified as:

`REPEATED_OCCURRENCE_PARAGRAPH_VARIANT`

The classification is structural only. It does not:

- pair the two occurrences as semantic equivalents;
- select a canonical occurrence;
- create a semantic conflict;
- infer chronology or supersession.

## Authority boundary

This milestone establishes stable structural paragraph identities only.

It does **not** establish:

- paragraph semantic types;
- condition/effect AST nodes;
- semantic equivalence of repeated variants;
- rule-interaction graph completeness;
- Codex/app equivalence;
- whole-faction normative completeness.

Therefore:

- `current_normalized_factions = 0` remains intentional;
- `full_normative_semantic_factions = 0` remains intentional;
- app/Codex-only semantics remain `PENDING/UNKNOWN`.

## Tooling

- model: `docs/CORE_RULE_PARAGRAPH_ATOMIZATION_MODEL.md`;
- schema: `schemas/core_rule_paragraph_atoms.schema.json`;
- builder: `tools/build_core_rule_paragraph_atoms.py`;
- tests: `tests/test_core_rule_paragraph_atomization.py`;
- workflow: `.github/workflows/core-rule-paragraph-atomization.yml`.

## Validation evidence

Validated implementation head:

- Core paragraph atomization workflow run `36703546953` — **SUCCESS**;
- normative/app equivalence gap audit run `36703546973` — **SUCCESS**;
- generic repository validator + full contract suite run `36703546698` — **SUCCESS**.

The independent overlap workflow triggered by current-layer integration is orthogonal to paragraph identity semantics and remains governed by its own reproducibility contract.

## Next milestone

`CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1`

Scope:

1. classify all 310 stable paragraph identities into conservative structural/semantic roles;
2. derive classifications from verified paragraph ranges without committing paragraph prose;
3. keep ambiguous/mixed paragraphs explicit rather than forcing a role;
4. preserve the ten repeated-occurrence variants independently;
5. do not build condition/effect AST nodes until semantic-role confidence is sufficient;
6. do not alter whole-faction normative coverage or infer app/Codex-only wording.
