# Core Rules paragraph/rule-body boundary extraction model v1

## Purpose

This milestone derives deterministic, copyright-safe rule-body and paragraph-boundary candidates for the **141** stable numbered Core Rules atoms.

It is a structural boundary layer, not a prose AST.

## Authority chain

1. Games Workshop public 11E Core Rules PDF is normative.
2. `reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json` pins the binary, document and page semantic fingerprints.
3. `rules/11e/snapshots/2026-09-30/core_rule_atoms/index.json` pins the 141 stable numbered reference identities and their verified short-heading evidence.
4. This layer may derive boundaries only after all three source gates reproduce.

## Extraction stream

The implementation uses the pinned `pypdf 5.9.0` extraction stream.

For every PDF page:

- raw extracted text is split into deterministic lines;
- short heading matching uses the same `clean_short_label()` contract as the Core structure/atomization layers;
- each committed atom heading label must resolve to exactly one line on its recorded page.

No alternate OCR/parser is introduced.

## Occurrence block boundary

Each verified in-family heading occurrence becomes one occurrence block.

Start:

- immediately after the matched heading line.

End:

- immediately before the next numbered Core-rule heading occurrence **inside the same family range**, ordered by extracted page/line position;
- for the final occurrence in a family, the end is the end of the family page range.

Leading/trailing empty lines are excluded from the body span.

The boundary is therefore a deterministic **extraction block**, not a claim that every included line is one semantic rule paragraph.

## Repeated headings

The five repeated atoms `15.07–15.11` intentionally create two occurrence blocks each.

Their body hashes are compared, but:

- equal hashes are structural evidence only;
- different hashes are retained as variants;
- neither state is promoted into a claim about semantic equivalence without a later rule-body semantic layer.

## Page-local spans

A block may cross pages.

Committed page-local spans may contain:

- page number;
- 1-based start/end line;
- 0-based character start/end offsets in the page extraction stream;
- line/character/token counts;
- raw-line-stream hash;
- normalized semantic hash;
- verified parent page semantic SHA.

No extracted line text is committed.

## Paragraph-boundary candidates

Within each page-local body span, contiguous non-empty line groups separated by one or more empty extracted lines are recorded as paragraph-boundary candidates.

A paragraph candidate stores only:

- page;
- start/end line;
- start/end character offset;
- line/character/token counts;
- normalized semantic SHA.

Page boundaries always break paragraph candidates. V1 does not infer paragraph continuity across pages.

## Boundary classifications

### `SINGLE_OCCURRENCE_BOUNDARY`

The atom has one verified heading occurrence and one deterministic body block.

### `REPEATED_OCCURRENCE_BOUNDARIES_IDENTICAL_HASH`

The atom has multiple verified in-family headings and all occurrence-body semantic hashes are identical.

### `REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH`

The atom has multiple verified in-family headings and the body semantic hashes differ.

This is not automatically a conflict.

### `EMPTY_BODY_BOUNDARY`

A heading resolves, but no non-empty body content remains before the next numbered heading/family end.

Fails v1 completeness.

### `HEADING_LINE_RECOVERY_GAP`

An atom heading label cannot be resolved to exactly one extracted line on the expected page.

Fails v1 completeness.

## Completion gate

V1 passes only when:

1. all **141** atom identities are preserved;
2. all expected heading occurrences resolve uniquely;
3. every atom has at least one non-empty occurrence body;
4. no `HEADING_LINE_RECOVERY_GAP`;
5. no `EMPTY_BODY_BOUNDARY`;
6. all page/body/paragraph records contain hashes and offsets but no prose;
7. source binary, all 88 page semantic hashes and document semantic hash reproduce;
8. whole-faction normative counters remain unchanged.

## Copyright boundary

Committed data may contain IDs, short atom headings inherited from the atom layer, offsets, counts, hashes, page/range relationships and structural classifications.

Committed data must not contain paragraph bodies, reconstructed rule prose or page text.

## Non-goals

This milestone does **not** establish:

- semantic paragraph AST;
- conditions/effects parsing;
- rule-interaction graph;
- semantic equivalence between repeated occurrence blocks;
- Codex/app equivalence;
- full-faction normative completeness.
