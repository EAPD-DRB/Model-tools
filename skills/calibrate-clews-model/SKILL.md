---
name: calibrate-clews-model
description: "Implement or refine a country calibration in an existing MUIO/OSeMOSYS CLEWs model using equation-first, non-forcing, source-traceable changes and bounded solver validation. Use when changing stocks, residual capacity, lifetimes, turnover, demand, capacity factors, utilization, costs, efficiencies, emissions factors, resource limits, or historical constraints; when replacing TAL/TAU or other historical pins; when diagnosing a calibration-induced infeasibility or solve-time regression; or when promoting a calibrated MUIOGO case. This IMPLEMENTS calibration: use assess-clews-calibration to grade an existing calibration and clews-model-review to audit structure."
---

# Calibrate a CLEWs model

Implement calibration as a reproducible model change, not as a search for a
solver result that resembles history. Read the repository instructions, the
active local formulation, and the application export code before editing.

## Mandatory design gate

Before the first full solve:

1. Copy `assets/calibration-plan.template.json` into the case documentation
   and complete it.
2. Classify every observation as exactly one of:
   `initial_stock`, `final_demand`, `real_world_constraint`, or
   `benchmark_only`.
3. Map every changed parameter to its source JSON file, local formulation
   equations, generated-data representation, and physical effect.
4. List explicit technology roles. Never infer physical stock,
   pass-through, accounting, conversion, or backstop behavior from a name
   prefix alone.
5. Register full-precision initialization inputs and their checksums. Do not
   initialize source parameters from rounded display CSVs when lossless solver
   or source data exist.
6. Define the unchanged control, last known-good runtime, candidate time
   budget, and minimal A/B strategy.
7. Run:

   ```bash
   python scripts/validate_calibration_plan.py PLAN.json --stage design
   ```

Do not run a full optimization while this gate fails.

## Non-forcing rules

- Use observed activity as final demand, a benchmark, or evidence for an
  explicitly documented initial effective stock. Do not preserve it as an
  activity target by default.
- Do not add positive exact `TAL = TAU`, fuel-share locks, dispatch shares, or
  other historical reproduction constraints unless the user explicitly
  requests them and the source describes a real continuing constraint.
- Reject a constraint that expires after an arbitrary calibration window.
  Use a full-horizon physical dynamic—stock survival, lifetime, turnover,
  adoption, resource availability, or demand—or leave the outcome
  endogenous.
- Distinguish stock turnover from utilization. Capacity and lifetime
  assumptions can limit replacement speed; they do not guarantee smooth
  dispatch among already available technologies.
- Keep benchmark-only observations out of source parameters.

Read [references/stock-turnover-patterns.md](references/stock-turnover-patterns.md)
when stocks, lifetimes, turnover, adoption or free switching are in scope.

## Equation-first workflow

### 1. Establish a trustworthy baseline

- Confirm case, run, scenario, horizon, solver status, result timestamp and
  source identity.
- Hash the baseline source, generated inputs and full-precision result.
- Reject stale or mismatched results. Solve a fresh unchanged control when
  necessary.
- Record objective, runtime, matrix dimensions and the affected baseline
  activities, capacities, demands, emissions, balances and backstops.

### 2. Trace the implementation path

- Locate `genData.json`, parameter JSON files, `Parameters.json`,
  `Variables.json`, the active solver formulation, `UpdateCase`,
  `DataFile.generateDatafile`, preprocessing and result export.
- For every proposed parameter, read the exact local equation that consumes
  it. Do not rely on parameter names or remembered OSeMOSYS behavior.
- Trace structural edits through `genData.json` and `UpdateCase`. Trace
  numerical edits from source JSON through generated data and derived sets.

### 3. Design from physical evidence

- Prefer observed stocks, commissioning or age cohorts, sales,
  registrations, retirements, survival curves, operational lives, service
  demands and utilization.
- Where no physical stock maps defensibly, use an effective initial stock only
  when its derivation preserves timeslice, availability and
  capacity-to-activity effects and is documented as an assumption.
- Separate official data, inherited model values, engineering assumptions and
  numerical safeguards.
- For each derived value record source IDs, units, geography, reference
  period, transformation, calculation ID, affected source cell and replacement
  evidence.

### 4. Implement in source

- Work on a disposable case.
- Change only source parameter JSON. Make structural changes in
  `genData.json` and regenerate with `UpdateCase`.
- Use an atomic generator with source fingerprints, an allowlisted diff,
  collision checks, invariant assertions and a recoverable backup.
- Never promote an edit made only to `data.txt`, processed data, an LP or
  solver output.

### 5. Pass deterministic pre-solve gates

Before CBC:

- exact referential and scenario-ID integrity;
- explicit technology-role coverage;
- source-diff allowlist and unchanged source hashes;
- initial-year capacity and commodity-balance replay;
- every-year, every-timeslice capacity/service envelope;
- nonnegative and dimensionally consistent stock/vintage profiles;
- full-horizon check of endogenous-vintage survival and replacement;
- no unintended restrictive `TAL`/`TAU`, exact activity pins, or arbitrary
  release years;
- generated-data and derived-set inspection;
- `glpsol --check` and matrix export.

Record each artifact in the plan, then run:

```bash
python scripts/validate_calibration_plan.py PLAN.json --stage pre-solve
```

Treat a deterministic failure as a design or data error. Do not ask CBC to
diagnose it.

### 6. Solve once, diagnose narrowly

- Run CBC through the normal application chain within the plan's time budget.
- If presolve reports infeasibility, map the row back to the named local
  equation, indices, lower/upper values and source parameters before changing
  anything.
- If runtime regresses, stop near twice the known-good runtime unless the log
  shows credible convergence.
- Compare one unchanged control with one minimal A/B rollback. Do not run a
  sequence of speculative formulations.
- A generated-file edit is permitted only in a disposable, clearly labelled
  diagnostic. Reproduce an accepted remedy in source and rerun the entire
  chain.
- Treat large aggregate constraint families and cross-technology coupling as
  formulation changes requiring a dedicated matrix-size and runtime A/B.

### 7. Validate behavior, not just optimality

- Compare objective and runtime with the accepted baseline.
- Check affected activity, capacity, demand, emissions, resource balances,
  backstops, constraint residuals and duals.
- Measure adjacent-year capacity and within-class activity-share changes.
  Report remaining discontinuities; do not hide them with pins.
- Inspect unexpected differences elsewhere and distinguish physical changes
  from alternate optima.
- Verify result freshness, case/run/scenario identity and artifact hashes.

### 8. Document and promote

- Maintain source, assumption, calculation, model-map and parameter-change
  registers.
- Update the case's `MODEL_FIXES*.md` with reason, equations, source changes,
  before/after values, diagnostics, baseline and exact passed/failed/timed-out
  checks.
- Promote only by regenerating the live case from the validated source state.
- Run one fresh live validation; do not copy disposable generated files or
  results.
- Complete the plan's promotion gates and run:

  ```bash
  python scripts/validate_calibration_plan.py PLAN.json --stage promotion
  ```

## Acceptance gate

Do not claim completion unless the plan validator passes at `promotion`, the
normal application chain solves successfully, no required validation is
omitted, and every material data source, transformation and limitation is
traceable.

## Related skills

- `build-clews-model` — build an uncalibrated country model.
- `assess-clews-calibration` — grade calibration quality and fitness for use.
- `clews-model-review` — audit structural and referential integrity.
- `add-environmental-accounting` — add environmental accounts without
  changing the economic model.
