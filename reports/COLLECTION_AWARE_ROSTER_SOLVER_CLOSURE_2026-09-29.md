# Collection-aware roster solver closure — 2026-09-29

## Result

**PASS — operational v1 for Adeptus Custodes**

The repository now has an end-to-end collection-aware roster solver for the first canonical personal collection domain.

This closes the active COLLECTION_AWARE_ROSTER_SOLVER milestone at **v1 scope**. It does not claim that every future faction collection is already modeled; additional faction profiles can reuse the same solver contract when personal collection data are added.

## Runtime

Tool: tools/solve_collection_roster.py

Solver-ready physical profile: collection/adeptus_custodes/solver_profile.json

Validation report: reports/COLLECTION_AWARE_ROSTER_SOLVER_CURRENT.json

Workflow: .github/workflows/collection-roster-solver.yml

## Rules scope

The solver uses current repository MFM 1.4 / official update 2026-09-02 for the dimensions MFM can establish:

- unit existence in the current MFM snapshot;
- legal MFM model-count rows;
- copy-tier pricing;
- detachment existence and DP metadata;
- enhancement costs within the selected detachment;
- paid wargear costs;
- declared Leader/bodyguard relations from the normalized MFM graph;
- points-limit arithmetic.

It deliberately does **not** claim full army legality.

Full normative legality remains: UNKNOWN_PENDING_NORMATIVE_APP

Reason: the repository still intentionally does not claim complete official/app semantic normalization.

## Physical collection scope

Source collection: collection/adeptus_custodes/legacy/v0_5_provisional/collection_adeptus_custodes_v0_5_provisional.json

Collection checkpoint: **2026-07-11**

Collection state: **PROVISIONAL**

Solver profile covers:

- **70** Custodes/Sisters physical bodies;
- **15** shared/dedicated body pools;
- ready vs build-required bodies;
- role-sharing between ordinary units and characters;
- Allarus captain/body sharing;
- Vertus/Dawneagle captain frame sharing;
- Guard-derived captain/body sharing;
- Forge World captain / Blade Champion sharing;
- Sisters of Silence shared body allocation;
- optional Sagittarum → Custodian Guard conversion;
- declared component capacities;
- Telemon arm-stock limits;
- known sword/shield stock;
- known Sisters weapon-bit stock.

The five shared Imperial Agents are intentionally outside Custodes solver v1 because their current allied roster legality belongs to a separate faction/ally scope.

## Allocation model

Body allocation uses a minimum-cost flow model.

Preference order:

1. ready direct-role bodies;
2. owned bodies that require assembly;
3. explicit conversion roles, only when allow_conversion=true.

This prevents the solver from consuming conversion bodies while a direct representation is available and distinguishes physical ownership from ready-to-field state.

## Fail-closed component policy

The solver validates component quantities only when the user declares them and the collection has an exact normalized capacity.

Unknown capacities are not guessed.

Example: CUSTODES_VENATARI_GUARD_SPEAR_SHARING

The inventory establishes that Venatari lance configurations draw from the Guard removable spear pool, but it does not explicitly normalize an exact simultaneous lance-equivalent capacity. A roster that requests paid Venatari lances therefore returns UNKNOWN_COMPONENT_FEASIBILITY instead of inventing a physical maximum.

The unresolved Warden extra-shoulder-pad question also remains explicit and does not block building the ten owned Warden bodies.

## Smoke matrix

Seven deterministic cases are validated:

| Case | Result |
| --- | --- |
| ready Custodes roster | FEASIBLE_PROVISIONAL |
| Wardens + Sisters on sprue | FEASIBLE_WITH_BUILD_PROVISIONAL |
| Guard using explicit Sagittarum conversion | FEASIBLE_WITH_CONVERSION_PROVISIONAL |
| six Vertus + Dawneagle Captain sharing six frames | INFEASIBLE_FROM_SNAPSHOT |
| two dual-arachnus Telemons with only two arachnus arms | INFEASIBLE_FROM_SNAPSHOT |
| Venatari lance shared-spear capacity | UNKNOWN_COMPONENT_FEASIBILITY |
| same Guard conversion roster with conversion disabled | INFEASIBLE_FROM_SNAPSHOT |

## Validated points examples

The smoke matrix also verifies current MFM arithmetic, including:

- ready sample: **740 pts**;
- build-required sample: **360 pts**;
- conversion sample: **645 pts**;
- bike shared-body conflict sample: **570 pts**;
- Telemon component conflict sample: **470 pts**;
- Venatari-lance unknown sample: **165 pts**.

These are validation fixtures, not recommended army lists.

## CI evidence

Validated PR head before closure documentation: 097c8cc4fdf114373ed12c81e1147ddb3f645895

GitHub Actions:

- Validate knowledge base: run 36599092439 — **SUCCESS**
- Collection-aware roster solver: run 36599092522 — **SUCCESS**

The dedicated workflow passed Python compile, solver smoke matrix, committed-report reproducibility, and solver unit tests.

The generic repository workflow passed repository validation and repository contract tests.

## Authority boundary

- Games Workshop MFM controls points/sizes/cost-bearing MFM dimensions.
- The personal collection snapshot controls owned-body/component facts.
- BSData/New Recruit runtime facts do not rewrite normative rules.
- Physical feasibility never promotes the collection snapshot from PROVISIONAL.
- Solver PASS means scoped MFM checks passed and the declared physical request is feasible against the named snapshot.
- Solver PASS does not mean full official/app army legality has been established.

## Next milestone

AUTOMATED_REINGESTION_RECONCILIATION_PROMOTION

Goal: when upstream monitoring detects a real change, automate the controlled re-ingestion → reconciliation → reviewed promotion pipeline without allowing automatic normative promotion.
