# Current 11E ingestion

The ingestion layer records reproducible source observations and update runs.

Pipeline:

```text
GW official source state
        +
Wahapedia readable mirror
        +
BSData structured implementation
        ↓
source snapshot / diff
        ↓
normalized faction objects
        ↓
coverage report
        ↓
conflict + regression checks
        ↓
promotion to CURRENT_VERIFIED
        ↓
New Recruit runtime projection check
```

No SOURCE_INVENTORY run may promote rules data. Promotion requires normalized objects, provenance, complete claimed coverage and passing tests.

## Automated candidate and reviewed promotion

A detected upstream change is no longer handled by manually rerunning the old fixed-date workflows.

`upstream-reingestion-candidate.yml` builds a deterministic plan and executes supported refresh stages in an isolated workspace. Its artifact is evidence only.

A promotion is a separate explicit action. `upstream-reingestion-promote.yml` requires the exact candidate workflow run ID, plan ID, and confirmation string. It applies the candidate to a new branch, rechecks upstreams, reruns New Recruit validation and semantic smoke, runs repository tests, then opens a PR.

Merging that PR remains the promotion decision. No candidate workflow can mutate `main` or change normative MFM data.
