# Core Rules paragraph atomization model v1

## Purpose

This milestone turns the **310** deterministic page-local paragraph-boundary candidates into stable structural paragraph identities.

It is still a structural evidence layer, not a semantic paragraph AST.

## Authority chain

1. Games Workshop public 11E Core Rules PDF remains normative.
2. Official binary, all 88 page semantic fingerprints and document semantic fingerprint must reproduce.
3. Parent rule-body boundary snapshot must be `PASS` with:
   - **141** rules;
   - **146** occurrences;
   - **310** paragraph candidates;
   - **0** heading recovery gaps;
   - **0** empty body boundaries.
4. Paragraph atoms are derived only from those committed parent candidates.

## Stable paragraph identity

Each paragraph candidate receives a stable repository identity:

`<occurrence_key>--para-p<page>-o<ordinal_on_page>`

The identity is structural and source-version scoped. It is based on:

- stable parent rule identity;
- stable parent occurrence identity;
- official PDF page;
- candidate ordinal on that page within the occurrence.

Offsets and hashes are evidence, not the semantic meaning of the identity.

## Stored provenance

A paragraph atom may contain only:

- `paragraph_key`;
- parent `rule_ref`, `rule_key`, `family_id`;
- parent `occurrence_key` and occurrence ordinal;
- paragraph ordinal inside the occurrence;
- page and page semantic SHA;
- line/character ranges;
- line/character/token counts;
- paragraph semantic SHA;
- parent body semantic SHA;
- structural classification.

No paragraph text is committed.

## Repeated-occurrence variants

Rules `15.07–15.11` each have two valid parent occurrences.

Their paragraph atoms are classified:

`REPEATED_OCCURRENCE_PARAGRAPH_VARIANT`

This means only that the paragraph belongs to a repeated structural occurrence whose parent body hashes differ.

It does **not**:

- pair two paragraphs as semantic equivalents;
- choose one occurrence as canonical;
- create a semantic conflict;
- infer which wording is newer or authoritative beyond the same verified official source.

All other paragraph atoms are:

`SINGLE_OCCURRENCE_PARAGRAPH`

## Completion gate

V1 passes only when:

1. parent boundary snapshot is `PASS`;
2. source binary/page/document fingerprints reproduce;
3. all **310 / 310** parent paragraph candidates become atoms;
4. paragraph keys are unique;
5. all **141** parent rules and **146** parent occurrences are represented;
6. classification split is exactly **300 single + 10 repeated-variant** for the current verified source;
7. every candidate range is inside its parent occurrence body span;
8. every paragraph atom has a 64-character semantic SHA and verified parent page SHA;
9. no paragraph prose is committed;
10. whole-faction normative counters remain unchanged.

## Non-goals

This milestone does not establish:

- semantic paragraph types;
- condition/effect AST nodes;
- semantic equivalence of repeated occurrences;
- rule-interaction graph;
- Codex/app equivalence;
- full-faction normative completeness.

The next semantic layer must consume these stable paragraph identities rather than reparsing paragraph boundaries ad hoc.
