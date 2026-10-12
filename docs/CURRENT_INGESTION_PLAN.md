# FULL 11E CURRENT INGESTION v1

## Objective

Move the repository from a historical eight-faction bootstrap to complete, measured current 11E coverage across the observed roster universe.

## P0 completed by the 2026-09-29 audit hardening pass

- full BSData roster-universe catalogue (37 roster catalogues, including titan/auxiliary catalogues);
- source-health vs repository-coverage separation;
- scoped currentness profiles;
- release-transition tracking for Orks, Space Marines ecosystem and Adeptus Custodes;
- explicit zero-coverage baseline;
- ingestion-run and coverage schemas;
- offline repository contract tests.

## Import order

### Wave A — global/MFM — **COMPLETE 2026-09-29**

Normalized MFM v1.4 (official update 2026-09-02) through a pinned deterministic extraction of the official MFM. Current snapshot totals: 30 source faction pages, 1,789 unit entries, 2,980 pricing rows, 1,574 Leader relations, 571 Support relations, 348 detachments and 1,193 enhancement-cost entries.

Coverage is complete for 36/37 roster identities (Unaligned Forces has no MFM page) for:

- points and unit-size bands;
- copy-tier/requisition-threshold pricing;
- paid wargear;
- Leader/Support relations;
- detachment catalogue and Detachment Points;
- Force Dispositions;
- enhancement costs;
- Legends pricing.

### Wave B — stable faction rules — **STRUCTURAL + OPERATIONAL SEMANTICS COMPLETE 2026-09-29**

For each faction not in an active release transition:

1. record applicable GW source/revision;
2. discover and parse Wahapedia faction projection;
3. inspect pinned BSData catalogue;
4. reconcile names/IDs/options;
5. normalize datasheets/detachments/keywords/wargear;
6. create conflicts rather than guessing;
7. update coverage;
8. promote only complete validated dimensions.

### Wave C — release transitions

- Orks: current Codex/MFM state can be ingested now.
- Space Marines ecosystem: preserve current legal state separately; ingest the new Codex state only when released.
- Adeptus Custodes: previews stay UPCOMING_PREVIEW_PARTIAL; do not overwrite current legal rules.

## Coverage contract

Every faction reports percentages for:

- points;
- unit sizes;
- leader relations;
- detachment points;
- Force Dispositions;
- datasheets;
- wargear constraints;
- keywords;
- detachments;
- enhancements;
- stratagems;
- FAQ/errata.

A claim such as CURRENT_VERIFIED must state which dimensions are complete.

## Promotion gate

A normalized object can become current only when:

1. applicable official source currentness is PASS;
2. object provenance is recorded;
3. its claimed coverage dimension is complete;
4. conflicts are resolved or explicitly scoped;
5. repository validation and unit tests pass;
6. release-state logic confirms it is CURRENT_LEGAL rather than preview-only.


### Wave B semantic/FAQ closure

- 16,506 / 16,506 stored semantic fingerprints match the live Wahapedia 11E CSV projection.
- Live Wahapedia `Source.csv` matches the committed edition-11 source catalog with zero drift.
- 29 edition-11 sources are indexed; one is MFM and 28 faction-pack PDF assets were fetched from the official Games Workshop asset domain and SHA-256 recorded.
- No long copyrighted rule prose is vendored.
- This closes **operational currentness**, not normative prose equivalence. Games Workshop remains authoritative and app-only wording remains a separate unresolved scope.

## Automated refresh control plane — COMPLETE 2026-09-29

Detected mirror/implementation changes now use:

`watch → deterministic plan → isolated candidate → reconciliation/audits → explicit reviewed promotion branch → PR`.

Automatic candidate generation is allowed; automatic promotion is not. A changed MFM extraction remains blocked until official Games Workshop MFM authority is revalidated.

## Active Wave C readiness milestone

`RELEASE_TRANSITION_INGESTION_READINESS`

Current transition facts remain unchanged:

- Space Marines ecosystem: current legal rules remain current; scheduled release date is 2026-10-03 and must not be promoted early.
- Adeptus Custodes: preview/preorder material remains upcoming-only until release/current-legality evidence exists.
- Both transitions should use the guarded candidate/reconciliation/promotion control plane once legally current.

## Release-transition readiness v1 — COMPLETE

The repository now has explicit transition manifests and a fail-closed state machine for the pending Space Marines and Adeptus Custodes releases.

At the 2026-09-29 checkpoint:

- Space Marines: `PRE_RELEASE_HOLD`, scheduled release date 2026-10-03, official current-legal confirmation not yet recorded;
- Adeptus Custodes: `UPCOMING_HOLD_NO_RELEASE_DATE`, current-legal release date intentionally unknown;
- neither transition is candidate-eligible or promotion-eligible.

A release date, preview or preorder announcement is never sufficient for promotion. Official current-legal evidence must be explicitly recorded, then a real upstream projection change must be detected before the existing guarded re-ingestion candidate path can run.

Active milestone:

`RELEASE_TRANSITION_ACTIVATION_WATCH`

## Release-transition activation watch v1 — COMPLETE

The release-transition layer now runs a read-only six-hour watch.

Checkpoint 2026-09-29:

- Space Marines: `NO_ACTION → WAIT_PRE_RELEASE`;
- Adeptus Custodes: `NO_ACTION → WAIT_OFFICIAL_RELEASE_SIGNAL`;
- global status: `NO_ACTION_REQUIRED`;
- direct promotion eligibility: always false.

Future transitions are surfaced as `ACTION_REQUIRED`, `MONITORING_UPSTREAM_PROJECTION`, or `READY_FOR_GUARDED_CANDIDATE`. Even the candidate-ready state only authorizes the existing isolated candidate path; reviewed promotion remains separate.

The release watch remains operational while development proceeds to:

`NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT`

## Normative/app equivalence gap audit — COMPLETE

The authority gap is now machine-classified.

Key result:

- `current_normalized_factions = 0` is an intentional normative threshold, not evidence that the current mirror is empty;
- 11E Core Rules are an official public source and can be ingested now;
- all 28 registered 11E public Faction Pack PDFs are verified, but Games Workshop defines them as supplemental to Codex content rather than full Codex replacements;
- current Wahapedia semantics are hash-current for 35 roster identities, but mirror currentness is not normative equivalence;
- GW App/Codex-only wording remains explicitly blocked on authorized/versioned evidence;
- official source→roster provenance currently resolves as 25 direct matches + 3 naming-alias candidates + 7 parent-source candidates + 2 no-public-pack identities.

Active milestone:

`OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_PIPELINE`

This next pipeline may close public Core Rules and public Faction Pack supplement/FAQ semantics plus official-vs-mirror overlap. It must not automatically promote full-faction normalization or infer app-only text.

## Official public semantic fingerprint pipeline — COMPLETE

The complete registered public Games Workshop 11E PDF surface is now fingerprinted without vendoring long rules prose:

- **29 / 29** official documents PASS;
- **1** Core Rules PDF;
- **28** public Faction Pack PDFs;
- **1,430** pages;
- **1,915,296** normalized text characters;
- **0** extraction failures.

All 28 Faction Pack binary hashes match the previous official-asset audit. The Core Rules binary SHA-256 is `f6a2443a44627ac5f0ef08407d29aa5ec7e97339998f05bc35f3ae37bf276833`.

This closes public-official fingerprint evidence, not structured normative normalization. The strict counters remain:

- `current_normalized_factions = 0`;
- `full_normative_semantic_factions = 0`;
- app/Codex equivalence = `PENDING`.

Active milestone:

`OFFICIAL_PUBLIC_RULES_MIRROR_OVERLAP_AUDIT`

Next compare only semantic units that can be mapped with exact provenance between the public official corpus and the current mirror. Do not infer Codex/app-only text from overlap matches.

## Official public overlap + structured expansion — COMPLETE 2026-09-30

The public Games Workshop ↔ current-mirror comparison and scoped structured expansion are closed:

- mirror semantic units audited: **13,572**;
- exact public overlap: **5,636**;
- exact scoped structured units: **4,070**;
- exact-but-unscoped residuals: **1,566**, classified with **0** promotions;
- no-exact residuals: **7,936**, classified with **0** semantic conflicts;
- Core Rules section structure: families **01–24**, **141** numbered references, all **88** pages verified.

Public exact overlap does not imply full Codex/app equivalence.

## Core rule-reference atomization v1 — COMPLETE

The verified **141** numbered Core Rules references are now stable structural identities.

Result:

- rule atoms: **141 / 141**;
- unique rule refs / keys: **141 / 141**;
- families: **24** (`01–24`);
- unique in-family heading atoms: **136**;
- repeated in-family heading atoms: **5**;
- heading-recovery gaps: **0**;
- atoms with cross-reference pages outside their parent family range: **40**.

The five repeated-heading references are `15.07–15.11`; each appears as valid in-family heading evidence on pages **55** and **57**. They are retained as repeated structural evidence rather than collapsed into a semantic claim.

Every atom retains official page/range hash provenance and bounded short headings. Paragraph rule prose is not committed.

This milestone does **not** claim:

- paragraph/rule-body boundaries are complete;
- paragraph-level rules AST is complete;
- rule interaction graph is complete;
- full Codex/app equivalence;
- any increase in whole-faction normative coverage.

Strict counters remain:

- `current_normalized_factions = 0`;
- `full_normative_semantic_factions = 0`.

Active milestone:

`CORE_RULE_PARAGRAPH_BOUNDARY_EXTRACTION_V1`

Next derive deterministic rule-body/paragraph boundaries for each stable atom using verified official page text transiently while committing only offsets/ranges/hashes and structural metadata, not paragraph prose.

## Core paragraph-boundary extraction v1 — COMPLETE

All **141** stable Core rule atoms now have deterministic extraction boundaries.

Result:

- rules: **141**;
- resolved heading occurrences: **146**;
- single-occurrence rules: **136**;
- repeated-occurrence rules: **5**;
- paragraph-boundary candidates: **310**;
- heading-line recovery gaps: **0**;
- empty rule-body boundaries: **0**.

The repeated rules `15.07–15.11` each produce two body occurrences. Their normalized body hashes differ between the two occurrences, so v1 preserves them as `REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH`. This is structural evidence, not an automatic semantic conflict.

Committed boundary data contains only page/line/character ranges, counts, hashes and structural relationships. Paragraph/rule-body prose remains external.

This milestone does **not** claim:

- paragraph semantic AST completeness;
- semantic equivalence of repeated body occurrences;
- rule-interaction graph completeness;
- Codex/app equivalence;
- any increase in whole-faction normative coverage.

Strict faction counters remain zero.

Active milestone:

`CORE_RULE_PARAGRAPH_ATOMIZATION_V1`

Next assign stable identities to the **310** page-local paragraph candidates, retain parent rule/occurrence provenance and hashes, and keep semantic parsing as a later layer.


## Core paragraph atomization v1 — COMPLETE

All **310** verified page-local Core paragraph-boundary candidates now have stable structural identities.

Result:

- paragraph atoms / unique keys: **310 / 310**;
- parent rules represented: **141**;
- parent occurrences represented: **146**;
- Core families represented: **24**;
- single-occurrence paragraph atoms: **300**;
- repeated-occurrence paragraph variants: **10** across `15.07–15.11`;
- range validation failures: **0**;
- paragraph semantic hashes reproduced from the verified PDF ranges: **310 / 310**.

Each paragraph atom preserves its parent rule, parent occurrence, page, line/character range, counts, verified page hash, paragraph semantic hash and parent body hash. Paragraph prose is not committed.

The ten repeated-occurrence paragraph atoms remain independent structural variants. They are not paired as semantic equivalents, do not select a canonical occurrence and do not create semantic conflicts automatically.

This milestone does **not** claim:

- semantic paragraph-role completeness;
- condition/effect AST completeness;
- rule-interaction graph completeness;
- Codex/app equivalence;
- any increase in whole-faction normative coverage.

Strict faction counters remain zero.

Active milestone:

`CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1`

Next classify the **310** stable paragraph identities into conservative semantic roles, preserving ambiguous/mixed cases explicitly and keeping semantic AST construction as a later layer.

## Core AST readiness expansion v1 — COMPLETE

The **33** source-shape blockers from the closed AST-readiness baseline were re-audited from verified official Core Rules ranges.

Result:

- rows audited / source hashes reproduced: **33 / 33**;
- `CANDIDATE_SINGLE_MODAL_SENTENCE`: **11**;
- candidate axes: **9 permission + 2 prohibition**;
- candidate condition cues: **0 across all 11**;
- remaining blocked: **22** under more specific fail-closed states;
- new AST nodes: **0**;
- interaction edges: **0**;
- existing AST mutations: **0**;
- additional paragraphs admitted: **0**.

The existing rule 13.07 direct-modal node remains `OPAQUE_PRESERVED`.

The 11 sentence candidates are readiness evidence only. They are neither AST nodes nor automatic parser admissions.

Active milestone:

`CORE_RULE_MODAL_SENTENCE_CANDIDATE_SELECTION_V1`

Next compare only those 11 candidates and choose **at most one** structurally simplest, source-hash-verified candidate for a separate parser pilot. Do not create a new AST node during candidate selection itself.

