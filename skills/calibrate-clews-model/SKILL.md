---
name: calibrate-clews-model
description: "Refine a solved country MUIO/OSeMOSYS CLEWs model after its CLEWs Global build by finding better national data, replacing generic defaults, adding master-rule-respecting physical stocks and constraints, repairing disconnected or unlimited-free subsystems, solving and diagnosing the integrated model, and documenting every source, calculation, assumption, mapping, gap, and change in the complete inherited schema ledger. Use for country calibration packages such as residual capacity, demand, costs, efficiencies, resource potentials, land, water, agriculture, emissions, stocks, lifetimes, and sector couplings. Not for creating the initial CLEWs Global model—use build-clews-model—or value-neutral cleanup—use clews-model-fix."
---

# Calibrate a CLEWs country model

Turn a solved basic CLEWs Global country model into a better sourced, connected,
basic-yet-real country model. Calibration here means replacing weak, generic,
missing, or physically disconnected inputs with defensible country evidence. It
does not mean tuning parameters until model outputs resemble history.

Read the repository instructions, active local formulation, application export
code, [references/non-forcing.md](references/non-forcing.md), and
[references/SCHEMA.md](references/SCHEMA.md) before editing. If the requested
package includes land, water, biomass, fisheries, emissions, or another closed
resource account, also read
[references/resource-accounting.md](references/resource-accounting.md). Read
[references/connectivity-audit.md](references/connectivity-audit.md) whenever
sector coupling or a suspicious free/backstop route is in scope. Read
[references/stock-turnover-patterns.md](references/stock-turnover-patterns.md)
for stocks, lifetimes, turnover, adoption, or residual capacity.

## Boundary and master rule

Require an existing solved country model. If none exists, use
`build-clews-model` first. Route edits that cannot change any model value to
`clews-model-fix`.

Apply the counterfactual test from the authoritative non-forcing reference:

> Would this exact change still be made if no historical outcome were known?

Use observed data as physical inputs, final demand, initial stock, resource
availability, documented real-world constraints, or benchmarks. Never choose
efficiencies, costs, yields, capacities, shares, activity limits, resource
ceilings, or release years merely to reduce historical error. Record unresolved
mismatches as gaps.

`CHANGES.csv` may retain the repository's A/B/C class as chronology metadata.
It does not select this workflow or reduce its evidence and validation duties.
Evidence-driven country refinement is the core calibration workflow.

## Mandatory calibration package

Before the first full solve, copy
`assets/calibration-package.template.json` into the case documentation and
complete it. Maintain `assets/calibration-backlog.template.csv` as the
prioritized data-quality inventory. Run:

```bash
python scripts/validate_calibration_package.py PACKAGE.json --stage design
```

The package must state:

- source and candidate cases, stored baseline, scenario, horizon, and intended use;
- complete inherited-ledger and retained-evidence locations;
- each weak/default/missing input and its evidence quality;
- every changed parameter, source JSON coordinate, equation, unit, physical
  effect, source/calculation/assumption IDs, and `MODEL_MAP` IDs;
- subsystem roles, expected physical connections, residual/backstop routes,
  account boundaries, spatial index scope, and remaining gaps;
- source-diff allowlist, analytical gates, solve budget, comparison outputs,
  promotion checks, and delivery artifacts.

Do not solve while the design gate fails.

## Workflow

### 1. Establish the canonical baseline

- Confirm repository, branch, case, run, scenario, horizon, solver status,
  timestamps, objective, runtime, matrix dimensions, and source/result identity.
- Prefer a matching stored baseline. Re-solve an unchanged control only when it
  is stale, mismatched, absent, or later diagnostics require it.
- Create the next version by copying the complete current schema ledger and all
  retained evidence. A pointer to the preceding version is chronology, never a
  substitute for inherited records or evidence.
- Validate the inherited ledger and coverage before adding new records.

### 2. Inventory country-data quality

Inspect all material inputs, not only the values named by the user. Classify
each as country-specific/current, country-specific/weak, regional proxy, global
default, derived assumption, missing, or disconnected/implausible. Prioritize
items by feasibility risk, influence on investment or resource use, cross-sector
importance, defect severity, and evidence availability.

Cover at least existing stocks, lifetimes, demand, costs, efficiencies,
resource potentials, technology applicability, land, water, agriculture,
emissions, and infrastructure where represented.

### 3. Audit connectivity and unlimited-free routes

Run the generic graph audit before changing the candidate:

```bash
python scripts/audit_clews_connectivity.py CASE_DIR \
  --rules documentation/connectivity-rules.json \
  --output documentation/connectivity-audit.json
```

Start the rules file from `assets/connectivity-rules.template.json`. Declare
technology roles and expected links explicitly; do not infer physical meaning
from name prefixes. Investigate:

- commodities produced but never consumed, or consumed without supply;
- technologies with useful output but missing material inputs;
- zero-cost, unbounded supply or backstop routes;
- crops without land, irrigated production without water, withdrawal without a
  finite source, or generation without fuel/resource/capacity consequences;
- stocks without survival/retirement, resource accounts without closure, and
  national limits accidentally repeated by cluster or mode.

The audit emits candidates, not automatic verdicts. Resolve every material
finding by implementing a defensible connection, declaring and documenting a
legitimate role/exemption, or recording a gap with consequences and upgrade
evidence. Follow the detailed protocol in
[references/connectivity-audit.md](references/connectivity-audit.md).

### 4. Research replacement evidence

Follow [references/country-data-research.md](references/country-data-research.md).
Search official national statistics, ministries, regulators, system operators,
inventories, maps, censuses, and administrative registers first; then primary
international institutions, peer-reviewed work, and engineering evidence. Use
transparent regional/global proxies only when better evidence is unavailable.

Retain source bytes where permitted. Record the exact table, sheet, page, query,
geography, reference period, published unit, access date, URL, license, local
file, and checksum. Never present a normalized transcription as publisher bytes.

### 5. Design the simplest defensible representation

- Read the exact local equation consuming every parameter; verify ratio
  direction, units, indices, guards, defaults, and generated-data behavior.
- Connect each subsystem to the physical resource or stock that materially
  constrains it. Add the fewest objects necessary and reuse existing modes only
  when their semantics and full input/output chain fit.
- Prefer observed initial stocks, asset/vintage data, demands, efficiencies,
  resource assessments, land accounts, water availability, and engineering
  limits. Keep choices endogenous beyond documented physical constraints.
- Make residual, idle, fallow, unallocated, import, extraction, and backstop
  behavior explicit. Bound an unintended sink or infinite supply route.
- Treat national, regional, cluster, mode, annual, cumulative, gross, and net
  quantities as different scopes. Never distribute a national number across
  clusters without evidence or a clearly recorded assumption.
- Use a transparent proxy when precision is unavailable; record its limitation
  and the evidence that would replace it.

### 6. Write provenance with the model change

Maintain the six authoritative CSV ledgers continuously:

- `SOURCES.csv`: publication identity and exact retained evidence;
- `CALCULATIONS.csv`: readable arithmetic, actual inputs/units, dependencies,
  outputs, and scripts;
- `ASSUMPTIONS.csv`: explicit central values, units, rationale, supporting
  evidence, and sensitivity bounds where used;
- `MODEL_MAP.csv`: exact source file, parameter coordinates, value/expression,
  unit, scope, and evidence lineage;
- `GAPS.csv`: what remains absent, why, consequences, priority, and upgrade
  source;
- `CHANGES.csv`: what changed, model objects, affected maps, validation artifact,
  author, commit, and administrative class if the schema requires it.

Record boundary exclusions, crosswalks, scaling, rounding closure, policy-target
interpretation, index allocation, and numerical sentinels as calculations or
assumptions. Regenerate the review workbook from the CSVs; it is not the
authority. Validate reference integrity, evidence hashes, the calculation DAG,
and mapping coverage for every populated input:

```bash
python scripts/provenance.py LEDGER_DIR --stage build --model-inputs MODEL_INPUT_DIR
```

### 7. Implement reproducibly in source

- Work in a disposable candidate case while iterating.
- Modify source parameter JSON and `genData.json`; regenerate derived structures
  through `UpdateCase` and the normal application chain.
- Use a deterministic generator with source fingerprints, an allowlisted diff,
  collision checks, invariant assertions, and recoverable backups.
- Never promote edits made only to generated data, an LP, or solver output.
- Reject collateral changes outside the package's declared source scope.

### 8. Pass deterministic pre-solve gates

Run the checks each changed parameter family and coupling can break:

- identifier, scenario, role, and mode integrity;
- exact source-diff allowlist and unchanged-sector hashes;
- equation/unit replay and generated-data inspection;
- base-year initialization and full-horizon stock/capacity survival;
- account closure and joint floor/ceiling feasibility for every year;
- residual, rewarded-class, free-backstop, and zero-bound stress tests;
- national-versus-cluster scope and destination-specific constraint tests;
- cumulative-envelope versus true adjacent-year transition semantics;
- matrix generation and `glpsol --check` where available;
- complete, passing schema-ledger provenance and input coverage.

For a resource account, also run:

```bash
python scripts/validate_resource_account.py RESOURCE_ACCOUNT.json
```

Then update package gate artifacts and run:

```bash
python scripts/validate_calibration_package.py PACKAGE.json --stage pre-solve
```

Treat deterministic failures as data or design errors. Do not ask the solver to
diagnose them.

### 9. Solve, diagnose, and iterate

- Solve through the normal application chain within the recorded budget.
- Map infeasible rows to local equations, indices, bounds, and source values
  before changing anything.
- Inspect directly affected quantities, binding bounds, resource balances,
  residual/backstop use, adjacent sectors, and full-horizon behavior.
- Correct mapping, units, scope, or formulation defects exposed by the solve.
  Several evidence-led solve/diagnose cycles are legitimate for coupled systems;
  speculative outcome-fitting is not.
- Re-solve the unchanged control or use a minimal rollback only when the stored
  baseline is unreliable or an unexpected interaction needs isolation.

### 10. Compare behavior and promote

Compare structural outcomes before row-level activity:

- final demand, emissions, resource totals, total/new capacity, and account
  closure;
- affected production, use, costs, stocks, backstops, residuals, and duals;
- objective and runtime in absolute and percentage terms;
- annual/adjacent-year changes and terminal behavior.

Aggregate equivalent routes before interpreting differences. Identify
alternative optima instead of presenting degenerate dispatch reallocations as
physical change. Generate the first-pass comparison with:

```bash
python scripts/compare_clews_runs.py BASELINE_CSV_DIR CANDIDATE_CSV_DIR \
  --output documentation/run-comparison.json
```

Benchmark against observations as `diagnostic — not fitted`.

Promote only by regenerating the live case from validated source. Run one fresh
live validation, build a result-free archive, verify live/archive source identity,
and run:

```bash
python scripts/validate_calibration_package.py PACKAGE.json --stage promotion
```

## Acceptance gate

Do not claim completion unless:

- the normal application chain solves and the result identity is fresh;
- the targeted subsystem has basic physical and economic behavior;
- no material disconnected or unlimited-free route remains unexplained;
- relevant accounts close at the correct temporal and spatial scope;
- all changes pass the master rule and equation-specific gates;
- every new value, calculation, assumption, mapping, gap, and change is in the
  complete self-contained inherited ledger;
- the live case and result-free delivery archive match; and
- remaining limitations and replacement evidence are explicit.

Solver success proves technical validity only. State the model's actual fitness
for use and direct grading requests to `assess-clews-calibration`.

## Related skills

- `build-clews-model` — create the initial solved CLEWs Global country model.
- `clews-model-fix` — value-neutral structural cleanup.
- `assess-clews-calibration` — grade calibration quality and fitness for use.
- `add-environmental-accounting` — add reporting accounts when they are not
  intended to constrain the economic model.
