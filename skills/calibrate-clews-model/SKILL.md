---
name: calibrate-clews-model
description: "Calibrate a solved country CLEWs model by replacing generic inputs with traceable national evidence, repairing physical connectivity and resource accounts, validating lineage, solving, and comparing behavior. Not for initial CLEWs Global builds—use build-clews-model—or value-neutral structural cleanup—use clews-model-fix."
---

# Calibrate a CLEWs country model

Refine an existing solved country model with defensible evidence and physical
structure. Calibration does not mean tuning inputs until outputs resemble history.

## Boundary

Require a solved country baseline. Use `build-clews-model` if none exists and
`clews-model-fix` for edits that cannot change any model value.

Apply the counterfactual test in
[references/non-forcing.md](references/non-forcing.md):

> Would this exact change still be made if no historical outcome were known?

Use observations as physical inputs, demand, initial stock, availability,
documented real-world constraints, or diagnostic benchmarks. Never select a
parameter merely to reduce historical error; record unresolved mismatches as gaps.

## Calibration package

Put a completed copy of `assets/calibration-package.template.json` at
`CASE_DIR/documentation/calibration-package.json`. Maintain the backlog at
`CASE_DIR/documentation/calibration-backlog.csv`. All package paths are relative to
`CASE_DIR`; override inference explicitly with `--case-dir`:

```bash
python scripts/validate_calibration_package.py \
  CASE_DIR/documentation/calibration-package.json \
  --case-dir CASE_DIR --stage design
```

The package validator compares the baseline and candidate source JSON directories,
derives the allowlist from `changes[].source_file`, resolves lineage against the
six CSV ledgers, verifies
the inherited ledger and retained evidence against the predecessor, reads JSON
gate reports, and checks connectivity dispositions. A passed gate needs a JSON
artifact whose top-level status is `pass`; only the explicitly optional gates may
be `not_applicable`, with a reason. Do not solve while the design gate fails.

## Workflow

### 1. Establish the baseline and inventory

Record the source and candidate cases, scenario, horizon, intended use, stored
baseline identity, solver status, objective, runtime, and model dimensions. Start
the candidate with a complete copy of the current ledger and retained evidence.

Inspect all material inputs and classify country specificity, currency, age,
proxy use, missingness, and connectivity. Prioritize feasibility risk, decision
influence, cross-sector importance, defect severity, and evidence availability.
Use the research hierarchy and trace rules in
[references/country-data-research.md](references/country-data-research.md).

### 2. Audit connectivity

Start from `assets/connectivity-rules.template.json`. Declare roles and physical
links explicitly; never infer them from prefixes. Run:

```bash
python scripts/audit_clews_connectivity.py CASE_DIR \
  --rules CASE_DIR/documentation/connectivity-rules.json \
  --output CASE_DIR/documentation/connectivity-audit.json
```

The audit fails closed on unknown rule entities and stale exemptions, checks free
routes year by year, and emits collision-free finding IDs. Resolve every active
finding by connecting or bounding it, declaring a sourced legitimate role, or
recording a consequential gap. Follow
[references/connectivity-audit.md](references/connectivity-audit.md).

### 3. Design the representation

Read the exact local equation and export path for each changed parameter. Verify
ratio direction, units, indices, guards, defaults, generated-data behavior, and
national-versus-cluster scope. Use the fewest objects needed for a defensible
physical chain, leaving choices endogenous beyond documented constraints.

For initial stocks, survival, retirement, or adoption, use
[references/stock-turnover-patterns.md](references/stock-turnover-patterns.md).
For land, water, biomass, fisheries, emissions, or another closed account, use
[references/resource-accounting.md](references/resource-accounting.md) and run:

```bash
python scripts/validate_resource_account.py RESOURCE_ACCOUNT.json \
  --json CASE_DIR/documentation/resource-account-validation.json
```

### 4. Record provenance and implement

Use the six-ledger contract in [references/SCHEMA.md](references/SCHEMA.md).
Every package evidence ID, map ID, and change ID must resolve. Validate the ledger
and write its JSON report for the package gate:

```bash
python scripts/provenance.py LEDGER_DIR --stage build \
  --model-inputs MODEL_INPUT_DIR --json documentation/provenance.json
```

Modify source parameter JSON and `genData.json`, then regenerate through
`UpdateCase` and the normal application chain. Never promote generated-data, LP,
or solver-output-only edits. The package validator requires the actual changed
top-level source JSON files to equal `changes[].source_file`.

### 5. Pass pre-solve gates

Attach the machine reports named by the package's `gates` keys, resolve every
active connectivity finding, then run:

```bash
python scripts/validate_calibration_package.py \
  CASE_DIR/documentation/calibration-package.json \
  --case-dir CASE_DIR --stage pre-solve
```

Treat failures as data or design errors rather than solver diagnostics.

### 6. Solve and diagnose

Solve through the normal application chain within the recorded budget. Map
infeasible rows to equations, indices, bounds, and evidence before changing
anything. Inspect affected quantities, binding limits, resource balances,
backstops, residuals, adjacent sectors, and full-horizon behavior. Correct only
mapping, unit, scope, evidence, or formulation defects—not historical mismatch.

### 7. Compare and promote

Compare structural totals before row-level activity. Add project-specific land,
water, or resource tables with repeated `--structural` options when needed:

```bash
python scripts/compare_clews_runs.py BASELINE_CSV_DIR CANDIDATE_CSV_DIR \
  --output CASE_DIR/documentation/run-comparison.json
```

Investigate tables present on only one side, aggregate equivalent routes, and do
not mistake alternative-optimum dispatch reallocations for physical change.
Benchmarks remain diagnostic, never fitted.

Regenerate the live case from validated source, solve once fresh, create the
result-free archive, verify live/archive source identity, run provenance at
`--stage delivery`, and finish with:

```bash
python scripts/validate_calibration_package.py \
  CASE_DIR/documentation/calibration-package.json \
  --case-dir CASE_DIR --stage promotion
```

## Judgment at delivery

The scripts cannot decide whether evidence is substantively appropriate. Confirm
that each change passes the counterfactual test, physical roles and scopes are
defensible, no material free or disconnected route remains unexplained, and
limitations name the evidence needed to replace proxies. Solver success proves
technical validity only; use `assess-clews-calibration` to grade calibration and
fitness for purpose.
