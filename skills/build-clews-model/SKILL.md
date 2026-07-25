---
name: build-clews-model
description: Build from scratch a technically valid, uncalibrated OSeMOSYS/CLEWs full-nexus country model using the upstream CLEWs Global workflow. Use when creating a new country model, adapting CLEWs Global or GeoCLEWs to a country, preparing country configuration and geospatial inputs, applying documented technical corrections, solving and packaging a raw baseline, or handing a model off for later calibration. Permit necessary software corrections and evidence-based country adaptations, but never tune parameters or impose constraints to reproduce historical observations during this build stage.
---

# Build a CLEWs country model

Create a reproducible **raw country model**, not a calibrated model. Preserve
the CLEWs Global architecture: GeoCLEWs spatial processing, OSeMOSYS Global
energy inputs, `clewsy` nexus integration, the OSeMOSYS formulation, and an
open solver supported by the workflow.

## Non-negotiable boundary

Do not use historical observations to make model results match history.

Never add or tune:

- historical generation-share or activity locks;
- equal historical lower/upper activity constraints;
- historical minimum/maximum capacity locks;
- capacity, demand, availability, capacity-factor, efficiency, cost, fuel,
  emissions, or yield overrides selected to reduce historical error;
- hydro, biomass, fuel-supply, land, crop, or water parameters inferred solely
  by solving backward from an observed outcome;
- smoothing or ramp constraints introduced only to conceal a historical-to-
  forecast discontinuity.

Do not call the result calibrated, validated against history, or policy-ready.
Record calibration data needs and suspicious outputs for the later calibration
stage without changing the raw model to fix them.

Before delivery, run `scripts/audit_no_forcing.py` and resolve every failure.
Read [references/non-forcing-rules.md](references/non-forcing-rules.md) whenever
an observed country value might influence a model parameter or constraint.

## Required workflow

1. **Define the build**
   - Record country, ISO3 code, intended horizon, administrative resolution,
     climate pathway, and requested use.
   - Label the scenario `raw` or `uncalibrated`.
   - Separate build questions from future calibration and policy questions.

2. **Pin and inspect upstream**
   - Clone CLEWs Global recursively and record the root and submodule commits.
   - Read the upstream README, configuration, Snakefile, environment files,
     licenses, and expected input/output paths.
   - Preserve an untouched upstream reference or reproducible clean checkout.
   - Never copy a previously calibrated country model as the hidden starting
     point.

3. **Prepare authoritative structural inputs**
   - Obtain country boundaries and required administrative layers.
   - Record every source URL, version, access date, unit, geography, and license.
   - Use observed geography, time zone, seasons, administrative structure, and
     technology applicability only as structural inputs.
   - Keep historical performance data in a calibration-candidate inventory;
     do not apply it.

4. **Configure the country**
   - Use native CLEWs Global configuration wherever possible.
   - Set country identifiers, nodes, horizon, seasons, dayparts, climate
     pathway, clustering resolution, projections, trade topology, and
     structurally applicable technologies.
   - Make each consequential choice explicit in a model card.
   - Read [references/country-adaptations.md](references/country-adaptations.md)
     before editing country configuration or crop mappings.

5. **Apply only necessary technical corrections**
   - First reproduce the defect on the pinned upstream version.
   - Prefer a minimal, general correction over a country-result override.
   - Add a regression check and retain a patch/diff.
   - Prove that the correction addresses software behavior, not historical fit.
   - Read [references/technical-corrections.md](references/technical-corrections.md)
     before modifying upstream or submodule source.

6. **Run the native workflow**
   - Build GeoCLEWs outputs.
   - Build OSeMOSYS Global inputs.
   - Integrate the full model with `clewsy`.
   - Convert the data, generate the optimization problem, solve it, and export
     results using the upstream workflow and supported tools.
   - Stop on non-zero subprocess status. Never continue from a partially failed
     stage.

7. **Validate technical and nexus integrity**
   - Confirm solver feasibility/optimality, schema conformance, unique parameter
     indices, complete sets, valid units, balanced time slices, and sensible
     bounds.
   - Verify that energy, land, crop, water, and climate components are present
     and physically linked, not merely colocated files.
   - Check land conservation, crop production/use, water accounting, energy
     balances, emissions accounting, and cross-sector input/output ratios.
   - Inspect year-to-year discontinuities and report them as raw-model behavior.
     Do not suppress them with historical constraints.
   - Compare with observations only to create a transparent gap table. Mark
     every comparison as **diagnostic—not fitted**.

8. **Package the raw handoff**
   - Include the pinned commits, country configuration, generated raw inputs,
     results, geospatial outputs, technical patches, source manifest, solver
     status, technical QA, model card, and reproduction commands.
   - Include `CALIBRATION_HANDOFF.md` listing historical datasets, mismatches,
     suspected drivers, and candidate future constraints. Apply none of them.
   - Preserve a machine-readable no-forcing audit.

## Permitted changes

Permit:

- reproducible technical corrections listed in the technical reference;
- documented country adaptations listed in the country reference;
- deterministic compatibility changes that do not target model outcomes;
- diagnostic comparisons that do not feed values back into the raw model;
- performance or visualization changes proven not to change model parameters.

When a proposed change is both structural and potentially calibrating, use the
counterfactual test:

> Would this exact change still be made if no historical outcome were known?

If no, defer it to calibration.

## Delivery language

State:

> This is a technically solved, uncalibrated CLEWs Global country model. It uses
> upstream defaults plus documented technical corrections and country
> adaptations. No parameters or constraints were introduced to force agreement
> with historical outcomes. Historical calibration and policy constraints are
> separate later stages.

Report solver success as technical validity only. Never present it as evidence
of country calibration.
