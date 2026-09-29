# Release transition activation watch closure — 2026-09-29

## Result

**PASS — operational read-only v1.**

The repository now continuously classifies pending release transitions without allowing release monitoring to mutate current rules, build candidates prematurely, or promote anything.

## Watch states

The activation watch maps release-readiness states into four operational classes:

- `NO_ACTION` — still pre-release / preview-only;
- `ACTION_REQUIRED` — calendar/release signal says an explicit official current-legal check is now required;
- `MONITORING_UPSTREAM_PROJECTION` — official current legality has been recorded, but mirror/implementation sources have not changed yet;
- `READY_FOR_GUARDED_CANDIDATE` — official current legality plus upstream projection drift are both present; the existing guarded re-ingestion candidate may now be built.

Unknown states fail closed to `ACTION_REQUIRED`.

## Current checkpoint — 2026-09-29

Global watch status: `NO_ACTION_REQUIRED`.

- `SPACE_MARINES_CODEX_2026`: `NO_ACTION` → `WAIT_PRE_RELEASE`;
- `ADEPTUS_CUSTODES_CODEX_2026`: `NO_ACTION` → `WAIT_OFFICIAL_RELEASE_SIGNAL`;
- action-required transitions: **0**;
- monitoring-upstream transitions: **0**;
- candidate-ready transitions: **0**;
- direct promotion eligible: **0**.

## Scheduled operation

Workflow:

`.github/workflows/release-transition-activation-watch.yml`

Cadence:

**every 6 hours**.

The workflow is repository read-only (`contents: read`). It:

- compiles activation-watch tooling;
- runs regression tests;
- reproduces the committed checkpoint on PR/push;
- evaluates live UTC-date state on schedule/manual dispatch;
- emits a GitHub warning when status becomes `ACTION_REQUIRED` or `READY_FOR_GUARDED_CANDIDATE`;
- writes the current transition/action table to the GitHub step summary;
- uploads the live watch report as an artifact.

It does **not**:

- write repository content;
- open or merge pull requests;
- record activation evidence automatically;
- dispatch re-ingestion;
- modify current rules;
- promote rules.

## Safety invariants

- `auto_promote=false`;
- `direct_current_rules_mutation=false`;
- `promotion_eligible=false` for every watch row;
- release date alone remains insufficient;
- preorder/preview remains insufficient;
- official current-legal activation must still be explicitly recorded;
- upstream projection drift must still be present before candidate generation;
- candidate/promotion continues through the existing guarded reviewed path.

## Validation evidence

Validated implementation head:

`cdcb3e2e66635520c8670d60f8e762840e087d8c`

GitHub Actions:

- Release transition activation watch: run `36609958145` — **SUCCESS**;
- Release transition readiness: run `36609957868` — **SUCCESS**;
- Validate knowledge base: run `36609957783` — **SUCCESS**.

Regression coverage verifies:

- 2026-09-29 checkpoint is `NO_ACTION_REQUIRED`;
- Space Marines release date alone becomes `ACTION_REQUIRED`, not candidate-ready;
- official currentness without source drift becomes monitoring-only;
- official currentness plus source drift becomes candidate-ready only;
- unexpected transition state fails closed;
- direct promotion eligibility never becomes true.

## External release watch remains active

On 2026-10-03 the Space Marines transition should move from pre-release hold to an explicit official-currentness check unless official activation evidence has already been recorded.

Adeptus Custodes remains without a recorded retail/current-legal release date at this checkpoint. The watch therefore waits for an explicit official release/currentness signal rather than guessing.

## Next development milestone

`NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT`

The release watch continues operationally in parallel. The next development work should inventory the remaining reasons `current_normalized_factions = 0`, especially official/app-only wording and mirror-to-official semantic equivalence, without weakening Games Workshop authority boundaries.
