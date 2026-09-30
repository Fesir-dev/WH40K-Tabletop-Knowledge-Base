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
