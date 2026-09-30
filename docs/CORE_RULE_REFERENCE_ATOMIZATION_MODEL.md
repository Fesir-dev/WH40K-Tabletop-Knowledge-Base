# Core Rules numbered reference atomization model v1

## Purpose

This milestone turns the verified numbered Core Rules reference families `01.xx`–`24.xx` into stable per-reference structural identities.

The atomized layer remains copyright-safe. It stores short heading labels, official page/hash provenance and structural classifications, not paragraph rule prose.

## Source authority

- normative source: verified Games Workshop public 11E Core Rules PDF;
- structural parent: `rules/11e/snapshots/2026-09-30/core_rules_structure/index.json`;
- fingerprint authority: `reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json`.

The PDF binary, all page fingerprints and the document semantic fingerprint must match before atomization.

## Stable identity

Each numbered reference receives:

- `rule_ref` — for example `09.05`;
- `rule_key` — stable repository key such as `core-rule-09-05`;
- `family_id`;
- parent family page range;
- short heading evidence;
- official page semantic hashes;
- cross-reference pages outside the parent family.

The stable identity is based on the official numbered reference, not on extracted prose.

## Definition evidence boundary

A reference occurrence is definition-eligible only when it appears in a conservative heading candidate **inside its parent family page range**.

Occurrences outside the family range are retained as cross-reference evidence only.

This prevents examples such as an early mention of `24.xx` from becoming the definition of family 24.

## Classification

### `UNIQUE_IN_FAMILY_HEADING`

The reference has heading evidence on exactly one page inside its parent family range.

This is the strongest v1 atomization state.

### `REPEATED_IN_FAMILY_HEADING`

The reference has heading evidence on more than one page inside its family range.

All occurrences are retained. The earliest in-family heading page is a navigation anchor, not a claim that later repeated wording is redundant or semantically identical.

### `MULTIPLE_LABELS_SAME_PAGE`

One in-family page exposes more than one short heading candidate for the same numbered reference.

The atom is retained but marked as layout-ambiguous.

### `HEADING_RECOVERY_GAP`

The structure snapshot records the numbered reference on an in-family page, but the atomizer cannot recover a short heading candidate from the verified PDF.

This state fails the v1 completeness gate and requires extractor review.

## Copyright boundary

Committed atomized records may contain:

- numbered reference IDs;
- short heading labels (bounded to 160 characters);
- page numbers;
- hashes;
- family/range relationships;
- structural classifications.

They must not contain paragraph bodies, long rules descriptions or reconstructed full page text.

## Completion rule

V1 is structurally complete only when:

1. all **141** references from the parent Core structure snapshot have one atom;
2. every atom has at least one in-family heading page;
3. no atom is classified `HEADING_RECOVERY_GAP`;
4. the family set remains exactly `01`–`24`;
5. source binary/page/document fingerprints all match.

Structural atomization does not imply:

- paragraph-level semantic AST completeness;
- complete rule-interaction modeling;
- faction/Codex/app equivalence;
- any increase in whole-faction normative coverage.
