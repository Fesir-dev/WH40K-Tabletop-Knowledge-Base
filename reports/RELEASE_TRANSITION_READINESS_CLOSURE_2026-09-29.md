# Release transition ingestion readiness closure — 2026-09-29

## Result

**PASS — operational v1.**

The repository is prepared to handle the pending 2026 Space Marines and Adeptus Custodes release transitions without allowing preview, preorder, or calendar-date state to replace current legal rules early.

## Tracked transitions

### SPACE_MARINES_CODEX_2026

- impacted roster identities: **12**;
- current legal baseline remains `CURRENT_LEGAL`;
- scheduled release date: **2026-10-03**;
- date confidence: `INFERRED_FROM_OFFICIAL_RELATIVE_DATE`;
- current readiness state at the 2026-09-29 checkpoint: `PRE_RELEASE_HOLD`;
- official current-legal activation confirmed: **false**;
- direct promotion eligible: **false**.

### ADEPTUS_CUSTODES_CODEX_2026

- impacted roster identities: **1**;
- current legal baseline remains `CURRENT_LEGAL`;
- preview/preorder state: `UPCOMING_PREVIEW_PARTIAL` / preorder announced;
- retail/current-legal release date: **UNKNOWN / not recorded**;
- current readiness state at the 2026-09-29 checkpoint: `UPCOMING_HOLD_NO_RELEASE_DATE`;
- official current-legal activation confirmed: **false**;
- direct promotion eligible: **false**.

## State-machine contract

Release readiness is explicitly fail-closed.

Current transition sequence:

```text
preview / preorder / release announcement
        ↓
PRE_RELEASE_HOLD or UPCOMING_HOLD_NO_RELEASE_DATE
        ↓
release date reached (if known)
        ↓
RELEASE_DATE_REACHED_AWAITING_OFFICIAL_CURRENTNESS
        ↓
explicit official current-legal evidence recorded
        ↓
CURRENT_LEGAL_CONFIRMED_WAITING_UPSTREAM_PROJECTION
        ↓
upstream mirror / implementation change detected
        ↓
READY_FOR_GUARDED_REINGESTION
        ↓
isolated candidate → reconciliation → reviewed promotion PR
```

The evaluator never returns direct promotion eligibility. `candidate_eligible=true` only means the existing guarded re-ingestion pipeline may build an isolated candidate.

## Safety invariants

- preview material never promotes;
- preorder state never promotes;
- release date alone never promotes;
- official current-legal evidence is mandatory;
- upstream projection change is mandatory before candidate generation;
- a changed MFM extraction remains subject to the separate official MFM authority gate;
- candidate generation routes through the existing guarded re-ingestion layer;
- reviewed promotion remains branch + PR based;
- `auto_promote=false` remains invariant.

## Operational tooling

- manifests:
  - `ingestion/release_transitions/space_marines_codex_2026.json`;
  - `ingestion/release_transitions/adeptus_custodes_codex_2026.json`;
- schema: `schemas/release_transition_manifest.schema.json`;
- evaluator: `tools/evaluate_release_transitions.py`;
- explicit activation evidence recorder: `tools/record_release_activation.py`;
- workflow: `.github/workflows/release-transition-readiness.yml`;
- current machine-readable report: `reports/RELEASE_TRANSITION_READINESS_CURRENT.json`.

The activation recorder accepts only explicit `GAMES_WORKSHOP_OFFICIAL` HTTPS evidence from approved Warhammer/Games Workshop domains and only updates the transition manifest. It does **not** mutate `rules/11e/current.json`.

## Scheduled readiness workflow

The readiness workflow is repository read-only.

On push/PR it reproduces the committed 2026-09-29 checkpoint exactly.

On schedule/manual dispatch it evaluates the current UTC calendar state and uploads an ephemeral readiness artifact. It also asserts that all transitions remain `promotion_eligible=false` and that auto-promotion is disabled.

## Validation evidence

Validated implementation head:

`22814f3bcc6a5f45cdb0746ffeb7c2dcc6a35eab`

GitHub Actions:

- Release transition readiness: run `36609106222` — **SUCCESS**;
- Validate knowledge base: run `36609106327` — **SUCCESS**.

The readiness workflow passed:

- Python compile;
- release-transition unit tests;
- deterministic checkpoint reproduction.

The repository workflow passed:

- full repository validator;
- repository contract tests.

Regression coverage includes:

- release date alone cannot promote;
- official currentness without upstream projection change waits;
- official currentness plus upstream change allows candidate generation only;
- Custodes can activate from later explicit official evidence without inventing a release date;
- activation evidence must come from approved official HTTPS domains.

## Authority boundary

- Games Workshop remains normative;
- release announcements and previews are evidence about future state, not current rules;
- the current legal rules layer remains unchanged at closure;
- no Space Marines or Custodes future rules were promoted;
- `current_normalized_factions = 0` remains unchanged;
- this milestone prepares transition ingestion; it does not claim future rules are already current.

## Next milestone

`RELEASE_TRANSITION_ACTIVATION_WATCH`

Operational objective:

- watch for official Space Marines current-legal evidence around 2026-10-03;
- watch for an explicit Custodes current-legal release signal without guessing a date;
- after official activation evidence, require actual upstream projection drift before building a candidate;
- route any newly current rules through guarded re-ingestion and reviewed promotion.
