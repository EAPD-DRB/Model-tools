---
name: MUIOGO-AGENT
description: Make equation-led, reproducible changes to MUIOGO OSeMOSYS cases and validate them through deterministic preflight, application generation, GLPK matrix-check, and CBC solve chains.
---

# MUIOGO model-change protocol

These instructions apply whenever changing or validating an OSeMOSYS case in this repository.

## Useful resources

- Consult the [OSeMOSYS model documentation](https://osemosys.readthedocs.io/en/latest/manual/Introduction.html) when model concepts, equations, parameters, or constraints need clarification.
- Consult the [OSeMOSYS/MUIO model code](https://github.com/OSeMOSYS/MUIO) when implementation details or the upstream model formulation need clarification.

## Required equation-first design gate

Before editing source parameters or attempting a full solve:

1. State the intended physical behavior and classify every observation as an
   initial stock, final demand, continuing real-world constraint, or
   benchmark-only value.
2. Inspect the active local solver formulation and MUIO generation,
   preprocessing and export code. Map every proposed parameter to the exact
   source file, equation, generated representation and expected effect.
3. Classify affected technologies explicitly as physical stocks,
   pass-throughs, conversions, accounting devices, backstops or demands.
   Never assign physical behavior from a technology-name prefix alone.
4. Use lossless source or full-precision solver values for numerical
   initialization. Rounded display CSVs may be cross-checks, not authoritative
   inputs when more precise evidence exists.
5. Build deterministic checks for initial-year capacity and commodity
   balances and for every-year, every-timeslice stock/vintage/service
   envelopes. Include survival and replacement of endogenous vintages.
6. Define one unchanged control, one minimal candidate, the last known-good
   runtime and the bounded candidate budget.

Do not use a full optimizer to discover a deterministic contradiction. Do not
try alternative formulations until the failed equation, indices and source
inputs are identified.

## Calibration constraints

- Do not reproduce observed activity with `TAL`, `TAU`, fuel shares or
  dispatch shares by default. Use observations as initial conditions, final
  demands or validation benchmarks according to their physical meaning.
- Do not add a constraint that expires after an arbitrary calibration window.
  Use a sourced full-horizon physical dynamic or leave the outcome endogenous.
- Distinguish capacity turnover from utilization. Stock and lifetime
  assumptions can limit replacement speed but do not guarantee smooth
  dispatch among available technologies.
- Treat per-technology and aggregate investment limits as different
  formulations. Document market interpretation, possible over-allowance,
  matrix coupling and solve-time evidence.

## Python environment

- Use the repository's declared virtual environment for validators and
  generation tools.
- Before a validator that imports PyYAML, run an `import yaml` preflight in
  that interpreter. If it fails, treat it as an environment dependency issue:
  repair the declared environment with approval or expose only an isolated
  disposable PyYAML package path. Do not put another project's entire
  `site-packages` directory on `PYTHONPATH`.
- Do not report a missing interpreter dependency as a validator, skill or
  model failure.

## Source of truth

- Make permanent model changes only in the case's source parameter files. Examples include `RYC.json` for demand, `RYT.json` for capacity limits, `RYTM.json` for costs, and the appropriate `RY*.json` file for other parameters.
- Make structural changes, such as adding technologies or commodities, in `genData.json` and pass them through the application's `UpdateCase` workflow so all parameter JSON files are regenerated while existing values are preserved.
- Never make a permanent change directly in generated solver files such as `data.txt`, `data_processed.txt`, or an LP file. Such a change is not reproducible from the application and must not be promoted as a model fix.

## Required validation chain

1. Work on a disposable copy of the case. Do not overwrite the live case's `res/` outputs while testing.
2. Run the deterministic design checks and stop on any unexplained shortfall,
   ID mismatch, unintended activity bound, negative stock or source-diff
   violation.
3. Generate the solver input through the same application path used by the UI: call `DataFile(case).generateDatafile(run)` and then `.preprocessData()`.
4. Inspect the generated data and derived sets to confirm that the source edits survived export and that mappings such as `MODEperTECHNOLOGY` were built correctly.
5. Run `glpsol --check` to validate the matrix and emit the LP. Inspect matrix
   dimensions and use a short presolve/bounded run before the full CBC
   optimization.
6. Solve with CBC through the normal model chain within the declared runtime
   budget.
7. Compare the result with an appropriate unchanged baseline. At minimum, check solver status, objective value and percentage change, runtime, matrix size, the specifically affected activities/capacities/emissions, relevant constraint residuals and duals, adjacent-year changes, and unexpected changes elsewhere.
8. Verify result timestamps and case/version identity so stale or mismatched outputs are never treated as results of the new inputs.
9. Promote the source-file changes to the live case only after all required checks pass. Regenerate and revalidate the live case through the application; do not copy a hand-edited generated file or disposable result into it.

## Diagnostic exception

- A generated file may be modified only inside a disposable test area for a narrowly scoped A/B diagnosis, such as isolating a constraint responsible for infeasibility or poor solver performance.
- Clearly label this as a diagnostic experiment. Reproduce any accepted remedy in the source parameter files and repeat the complete application-generation and solve chain before treating it as a model change.

## Solve-time regression triage

- Treat a sudden solve-time regression as an incident. Inspect the latest source-parameter diff first, then test the smallest plausible rollback in a disposable copy before designing a new formulation.
- Establish one unchanged control and one minimal A/B variant. Use the last known-good runtime as the initial time budget; stop a regressed run after roughly twice that runtime unless its solver log shows credible convergence.
- When the minimal rollback restores an optimal solve, stabilize the case with that rollback and complete the required validation chain. Investigate ways to recover optional calibration detail as separate follow-up work.
- Treat identical positive activity bounds (`TAL = TAU`) as a high-risk calibration technique in CBC. They are mathematically valid, but every new use requires a dedicated solve-time A/B test against the unpinned case.
- Treat large user-defined constraint families and cross-technology coupling as
  formulation changes. Require a matrix-size and runtime A/B before promotion.
- Do not run a long sequence of alternative formulations during incident recovery unless the user explicitly prioritizes preserving the disputed formulation over restoring a working solve.

## Reporting

- Document every model change in the affected case's `MODEL_FIXES*.md` file before considering the work complete. If the case does not yet have one, create it using the case's existing naming convention.
- Each entry must record the reason for the change, the source files and parameters changed, the before/after formulation or values, the generated artifacts and baseline inspected, the validation results, and any incomplete checks or known limitations.
- Do not describe a change as fully validated if generation, preprocessing, matrix validation, CBC optimization, or baseline comparison is incomplete.
- Report exactly which checks passed, failed, timed out, or were not run.
- Preserve an audit trail of the source files changed, generated artifacts inspected, baseline used, and material result differences.
