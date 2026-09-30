# Official Core Rules structured normalization model

## Scope

This milestone turns the verified public 11E Core Rules PDF into a compact section-level structure without storing long Games Workshop rules prose.

Authority remains Games Workshop. Wahapedia is not used to invent missing Core Rules structure.

## Evidence gate

The extractor must verify all of the following before emitting a snapshot:

1. the downloaded Core Rules PDF SHA-256 equals the committed official fingerprint evidence;
2. the page count equals the committed fingerprint evidence;
3. every page semantic SHA-256 equals the committed page fingerprint;
4. the full document semantic SHA-256 equals the committed fingerprint.

Any mismatch is `SOURCE_DRIFT` and no promotable structure is emitted.

## Structure sources

The extractor uses two independent structural signals:

- native PDF outline/bookmark destinations when present;
- conservative short heading candidates derived from page text.

Native outline entries are preferred for hierarchy. Heading candidates are used only to enrich page-level section evidence and to detect pages not represented by bookmarks.

## Copyright boundary

Allowed committed content:

- short section/heading labels;
- hierarchy/depth;
- official page ranges;
- hashes;
- counts;
- semantic classes;
- source/version provenance.

Disallowed committed content:

- paragraph rule text;
- long extracted page text;
- full-page transcription.

## Section identity

A section receives a stable key from:

- normalized short label;
- outline depth;
- starting official page.

Each section stores:

- `section_key`;
- `title`;
- `depth`;
- `page_start`;
- `page_end`;
- source document ID and binary SHA;
- page semantic SHA list or range digest;
- child section keys;
- optional heading-candidate evidence.

## Completion boundary

This layer proves section-level public Core Rules structure only.

It does not mean:

- every rule paragraph is atomized;
- every rules interaction is normalized;
- app/Codex-only wording is known;
- faction normative completeness can increase.

Whole-faction counters therefore remain unchanged.


## Rule-reference family map

The public Core Rules expose numbered rule references in families `01.xx` through `24.xx`.

The v1 structured layer requires:

- all 24 families to be detected;
- canonical family order to be exactly `01` → `24`;
- every family to retain observed heading pages and exact rule-reference IDs;
- a canonical anchor page chosen by the page with the highest density of distinct references from that family;
- a definition start page allowed to move up to four pages before the density anchor when nearby heading evidence exists.

The last rule prevents distant cross-references from moving a section boundary backwards. For example, an early mention of a `24.xx` rule remains evidence of a cross-reference; it does not become the start of family 24 when the dense definition block occurs much later.

## Completion levels

The snapshot distinguishes three levels:

1. **section-level family structure** — complete only when families `01`–`24` are present in canonical order;
2. **flat heading map** — page-oriented navigation evidence, useful but not an authoritative hierarchy;
3. **nested/paragraph AST** — explicitly incomplete in v1.

Therefore `section_level_structure_complete_for_public_pdf=true` does not mean paragraph-level atomization is complete.
