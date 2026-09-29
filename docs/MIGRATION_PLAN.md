# Migration plan

## Phase 1 — bootstrap and preserve history

Status: **in progress / largely complete**

- repository governance;
- source/provenance contracts;
- old archive identities and checksums;
- Custodes physical collection;
- legacy rules engine and core regressions;
- semantic-core file index;
- first dated rules snapshot.

## Phase 2 — materialize reusable legacy semantics

Priority order:

1. Adeptus Custodes — first because collection + rules can be connected.
2. global roster/interaction semantics.
3. remaining seven tracked factions.
4. enhancement/stratagem/keyword layers where useful for diffs.
5. historical regression corpus.

Legacy objects remain under `legacy/` or dated `snapshots/`.

## Phase 3 — current rules refresh

For each domain:

1. fetch/check official source;
2. record source version/date/hash;
3. diff against historical snapshot;
4. normalize changed facts;
5. validate;
6. only then promote to `CURRENT_VERIFIED`.

## Phase 4 — collection intelligence

- collection-aware legal roster solver;
- physical body allocation;
- shared weapon/bit allocation;
- build/purchase gap analysis;
- roster suggestions based on owned models.

## Phase 5 — hobby inventory

Import and normalize:

- paints;
- primers;
- washes/contrasts;
- mediums/thinners;
- varnishes;
- basing materials;
- brushes/tools;
- painting recipes and faction schemes.
