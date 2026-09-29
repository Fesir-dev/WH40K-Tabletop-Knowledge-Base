# Guarded automated re-ingestion / reconciliation / promotion closure — 2026-09-29

## Result

**PASS — operational guarded v1.**

The repository now has a complete control plane from upstream change detection through isolated candidate generation to explicitly reviewed promotion PR creation.

Current upstream state at closure remains `NO_CHANGE`; therefore no real source revision was promoted during this milestone.

## Automated candidate path

- watcher: `.github/workflows/upstream-change-watch.yml`;
- deterministic planner: `tools/plan_upstream_reingestion.py`;
- isolated executor: `tools/run_upstream_reingestion_candidate.py`;
- candidate workflow: `.github/workflows/upstream-reingestion-candidate.yml`;
- candidate evidence is uploaded as a GitHub Actions artifact;
- candidate generation has read-only repository permissions;
- `auto_promote=false` is invariant.

Supported classifications:

- Wahapedia mirror drift → candidate ingestion + reconciliation + roster views + semantic audit;
- BSData implementation drift → candidate reconciliation + fallback rebuild;
- Wahapedia `Source.csv` drift → additional official Games Workshop asset verification;
- BSData MFM extraction drift → **blocking official MFM authority revalidation**, not automatic ingestion.

## Reviewed promotion path

- promotion tool: `tools/apply_reingestion_promotion.py`;
- runtime-summary sync: `tools/sync_new_recruit_runtime_status.py`;
- workflow: `.github/workflows/upstream-reingestion-promote.yml`;
- required inputs: exact candidate workflow run ID, exact `plan_id`, explicit `PROMOTE_REVIEWED_CANDIDATE` confirmation;
- candidate `plan_fingerprint` must match;
- candidate status must be `PASS` and gate `ELIGIBLE_FOR_REVIEWED_PROMOTION`;
- MFM-derived changes are refused by this path;
- promotion is applied to a **new branch**, never directly to `main`;
- workflow reruns upstream watch after pointer application, so upstream movement during review invalidates promotion;
- New Recruit is revalidated against promoted pointers and unclassified runtime drift blocks promotion;
- semantic resolver smoke, repository validation and unit tests must pass;
- final output is a pull request requiring a separate merge decision.

## Pointer hardening

Mutable current consumers no longer hardcode the bootstrap mirror/implementation date where promotion must move them:

- `tools/query_current_semantics.py` follows `rules/11e/current.json` → current Wahapedia snapshot;
- `tools/watch_upstreams.py` follows the current Wahapedia pointer and registry revisions;
- `tools/validate_new_recruit_runtime.py` follows current MFM, Wahapedia and pinned BSData pointers;
- `tools/validate_repo.py` validates pointer consistency rather than treating bootstrap mirror counts/revisions as eternal;
- `tests/test_repository_contracts.py` preserves bootstrap regression checks while allowing reviewed current projection promotion.

Historical MFM 1.4 exact invariants remain pinned because MFM authority was not changed.

## Fail-closed promotion properties

- `auto_promote=true` is rejected;
- candidate fingerprint mismatch is rejected;
- MFM extraction change is blocked;
- Source.csv change without official asset evidence is blocked;
- candidate mutations of current-authority files are rejected;
- promotion mutation whitelist is enforced;
- normative `current_normalized_factions = 0` remains unchanged;
- runtime/BSData/Wahapedia evidence never changes Games Workshop normative authority.

## Validation evidence

Validated automation head:

`ec85e345b65a4b5d9820f893eab0879a02f57a46`

GitHub Actions:

- Validate knowledge base: run `36603325318` — **SUCCESS**;
- Upstream reingestion candidate: run `36603325327` — **SUCCESS**.

The candidate workflow completed its synthetic end-to-end Wahapedia-change smoke, uploaded reviewable evidence, and asserted `auto-promote: DISABLED`.

Repository tests also exercise the reviewed promotion gate and synthetic pointer application, including fingerprint mismatch, MFM blocking and Source.csv official-asset requirements.

## What was not claimed

- no real upstream revision was promoted, because the watcher state is currently `NO_CHANGE`;
- no exact future source synchronization cadence is inferred;
- no mirror-to-GW paragraph-level normative equivalence is claimed;
- no app-only wording gap is closed;
- no future Space Marines or Custodes preview/release material is promoted before it becomes legally current.

## Next milestone

`RELEASE_TRANSITION_INGESTION_READINESS`

Immediate scope:

- prepare the October 3 Space Marines transition without replacing current legal data early;
- preserve Adeptus Custodes preview/preorder data as upcoming-only until release;
- make the release transition use the same candidate → reconciliation → reviewed promotion control plane.
