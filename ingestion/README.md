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
