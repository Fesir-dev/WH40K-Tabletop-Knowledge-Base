# Long-run execution protocol

This project intentionally supports long, deep work sessions. Reliability is achieved through durable internal milestones rather than by shortening the work.

## Operating model

A substantial task can run through several major phases in one working session:

```text
research / source discovery
        ↓
implementation
        ↓
generated data / migration
        ↓
reconciliation / validation
        ↓
promotion / documentation
        ↓
closure
```

Each phase may itself be substantial. The important rule is that a completed phase becomes durable in Git before the next risky phase depends on it.

## Milestone size

Prefer roughly **3–6 meaningful durable milestones** for a large task.

Avoid both extremes:

- dozens of tiny commits that fragment the work;
- one very large uncommitted run whose recovery depends on chat continuity.

## Stream failure policy

A ChatGPT delivery failure such as `Resume stream unavailable` is treated as a UI/transport failure, not as repository state.

Recovery sequence:

1. read the current `main` HEAD;
2. inspect the latest successful CI runs;
3. read `reports/CURRENT_HANDOFF.md`;
4. compare the handoff with current machine-readable state;
5. resume from the latest validated milestone.

Do not redo already committed work merely because the chat stream was interrupted.

## Tool-use policy

For long runs:

- batch related GitHub reads/writes;
- avoid repeatedly polling the same Action run;
- prefer targeted reads over dumping large JSON files;
- use generated reports for large datasets;
- make promotion a separate reviewed step after generation/reconciliation;
- keep source acquisition, normalization, reconciliation and promotion distinct.

## User updates

Keep the user informed at major boundaries, not every low-level tool call.

A long run may therefore contain long stretches of work, but should surface:

- a meaningful discovery that changes the design;
- completion of a durable milestone;
- a blocker that changes the route;
- final closure state.

## Closure rule

A task is not closed because data were generated.

Closure requires, where applicable:

1. generated artifacts committed;
2. provenance recorded;
3. conflicts recorded;
4. validation/tests passing;
5. currentness/coverage updated honestly;
6. documentation/handoff updated;
7. no known unstable transition left unlabelled.
