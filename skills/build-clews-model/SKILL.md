---
name: build-clews-model
description: Build from scratch a technically valid, uncalibrated OSeMOSYS/CLEWs full-nexus country model with the upstream CLEWs Global workflow, then import, repair, verify, solve, and package it as a usable MUIO model. Use when creating a new country CLEWs model; adapting CLEWs Global or GeoCLEWs; preparing country configuration and geospatial inputs; applying documented technical corrections and country adaptations; converting CLEWs CSVs through otoole and MUIO; repairing season/day/time mappings; handling unsupported reserve-margin tags with a documented UDC workaround; checking import and result parity; or delivering a portable MUIO case for later calibration. Never tune parameters or impose constraints to reproduce historical observations during this build stage.
---

# Build a CLEWs country model through MUIO

Create, in one continuous workflow:

1. a reproducible raw CLEWs Global country model; and
2. a solved, portable MUIO case representing that model as faithfully as the
   installed MUIO version permits.

Preserve GeoCLEWs spatial processing, OSeMOSYS Global energy inputs, `clewsy`
nexus integration, the upstream OSeMOSYS formulation, and an open solver.
Treat MUIO import as a separate representation and verification phase. Do not
describe MUIO conversion fixes or formulation workarounds as country
calibration.

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

The MUIO phase does not weaken this boundary. A user-defined constraint is
permitted only when it faithfully ports an upstream formulation feature or
implements the reserve-margin workaround defined below. Never use a UDC to
lock historical capacity, activity, generation, land, water, or emissions.

## Required references

Read:

- [references/country-adaptations.md](references/country-adaptations.md) before
  changing country structure, technology applicability, time definitions, or
  crop mappings;
- [references/technical-corrections.md](references/technical-corrections.md)
  before patching CLEWs Global, a submodule, otoole, or a generated pipeline;
- [references/muio-import.md](references/muio-import.md) before preparing the
  MUIO workbook or touching a MUIO case;
- [references/reserve-margin-workaround.md](references/reserve-margin-workaround.md)
  whenever reserve-margin tags are present or native support is uncertain.

## Required workflow

1. **Define the build**
   - Record country, ISO3 code, intended horizon, administrative resolution,
     climate pathway, requested use, CLEWs Global location, and MUIO location.
   - When the user supplies only the country, proceed with documented
     upstream-supported raw defaults and evidence-based structural assumptions.
     Ask only when a missing choice or inaccessible resource would materially
     change the model architecture or prevent completion.
   - Label the scenario `raw` or `uncalibrated`.
   - Separate build questions from future calibration and policy questions.
   - Define two completion targets: a solved upstream package and a solved
     portable MUIO case.

2. **Pin and inspect both codebases**
   - Clone CLEWs Global recursively and record the root and submodule commits.
   - Locate or obtain MUIO and record its commit/version.
   - Read the upstream README, configuration, Snakefile, environment files,
     licenses, otoole configuration, MUIO importer, MUIO parameter registry,
     active MUIO formulation, and expected input/output paths.
   - Preserve an untouched upstream reference or reproducible clean checkout.
   - Record checksums of shared MUIO importer/formulation files that the
     country workflow must not modify.
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

5. **Apply only necessary technical corrections**
   - First reproduce the defect on the pinned upstream version.
   - Prefer a minimal, general correction over a country-result override.
   - Add a regression check and retain a patch/diff.
   - Prove that the correction addresses software behavior, not historical fit.

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

8. **Package the upstream raw model**
   - Include the pinned commits, country configuration, generated raw inputs,
     results, geospatial outputs, technical patches, source manifest, solver
     status, technical QA, model card, and reproduction commands.
   - Include `CALIBRATION_HANDOFF.md` listing historical datasets, mismatches,
     suspected drivers, and candidate future constraints. Apply none of them.
   - Preserve a machine-readable no-forcing audit.

9. **Prepare the MUIO import workbook**
   - Convert the complete CLEWs CSV input folder to Excel using otoole and the
     matching CLEWs/otoole configuration.
   - Add MUIO-required `TECHGROUP` definitions and assign every technology.
     Grouping is interface metadata and must not alter parameters.
   - Add deterministic time-set descriptions.
   - If CLEWs Global supplies no `DiscountRate` row, insert an explicit
     `GLOBAL, 0.05` fallback and document it. Preserve any supplied value.
   - Omit empty optional parameter sheets when the installed importer
     misinterprets an empty sheet as populated.
   - Save the untouched otoole workbook and the prepared MUIO workbook.

10. **Import without modifying shared MUIO code**
    - Use a country-local one-off import driver around MUIO's existing
      `ImportTemplate.py`.
    - Hash the importer before and after and fail if it changes.
    - Refuse to overwrite an existing case silently.
    - Store every import helper inside the country package so the workflow is
      portable to another laptop.
    - Do not change `ImportTemplate.py`, `Parameters.json`, or the shared
      OSeMOSYS formulation merely to accommodate this country.

11. **Repair and verify temporal structure**
    - After import, reconstruct each MUIO timeslice's season, day type, and
      daily time bracket from `Conversionls.csv`, `Conversionld.csv`, and
      `Conversionlh.csv`.
    - Reconstruct `DaySplit` from the CLEWs CSV.
    - Back up every generated JSON file before one-off repair.
    - Assert one active member per timeslice per temporal dimension and exact
      set/year coverage.
    - Generate a MUIO data file and verify the resulting conversion matrices,
      `YearSplit`, and `DaySplit`.

12. **Run import parity before adding workarounds**
    - Round-trip the generated MUIO data through otoole after removing only
      MUIO-only sets and parameters from an analysis copy.
    - Classify every source row as exact, implicit default, intentionally
      transformed representation, unsupported, or erroneous.
    - Treat unexplained loss or change as an import failure.
    - Compare upstream and MUIO results on overlapping outputs. Explain
      formulation differences, defaults, units, and objectives; never tune the
      model to make parity pass.

13. **Handle reserve-margin tags**
    - First test whether the installed MUIO version supports native
      `ReserveMargin`, `ReserveMarginTagFuel`, and
      `ReserveMarginTagTechnology` parameters and an active reserve constraint.
      Use native support when it exists.
    - Otherwise apply the annual MUIO UDC workaround in
      [references/reserve-margin-workaround.md](references/reserve-margin-workaround.md).
    - Clearly label it a **workaround for unsupported reserve-margin tags**,
      not a native import and not calibration.
    - Use the source capacity credits and reserve-margin default/value. Do not
      substitute Input/Output Activity Ratios, CapacityFactor, or a single
      `ReserveMargin.csv` value for technology-specific credits.
    - Install a conspicuously named constraint, a model-local configuration,
      and a checker/updater that reports `STALE` with a nonzero exit when
      demand, demand profile, `YearSplit`, `CapacityToActivityUnit`, capacity
      credits, reserve margin, years, timeslices, or scenarios invalidate the
      derived UDC.
    - Require a `CURRENT` zero-mismatch check before solving.

14. **Solve, validate, and package the MUIO model**
    - Preserve a pre-workaround run for diagnosis and create a separate
      reserve-proxy run when the workaround is needed.
    - Generate MUIO data, solve with an available supported open solver, and
      require an optimal/feasible status.
    - Verify all UDC rows appear in generated data and results and that credited
      capacity satisfies the annual requirement within solver tolerance.
    - Re-run technical/no-forcing checks and the reserve-proxy stale check.
    - Export a MUIO-compatible case ZIP that includes the model JSON,
      configuration marker, check fingerprint, runs, and results while
      respecting MUIO's backup layout.
    - Include the prepared workbook, otoole config, one-off scripts, backups,
      parity reports, solve status, and `MUIO_IMPORT.md` in the country package.
    - Verify the ZIP and provide exact reproduction, check, update, solve, and
      restore commands.

## Permitted changes

Permit:

- reproducible technical corrections listed in the technical reference;
- documented country adaptations listed in the country reference;
- deterministic compatibility changes that do not target model outcomes;
- diagnostic comparisons that do not feed values back into the raw model;
- performance or visualization changes proven not to change model parameters;
- MUIO-only technology groups and descriptions;
- one-off repair of importer-created time references using authoritative CLEWs
  conversion matrices;
- an explicit 5% discount-rate fallback only when CLEWs Global supplies no
  value;
- the documented reserve-margin UDC workaround when native MUIO support is
  absent and its structural preconditions are proven.

When a proposed change is both structural and potentially calibrating, use the
counterfactual test:

> Would this exact change still be made if no historical outcome were known?

If no, defer it to calibration.

## Completion gates

Do not call the task complete until:

- the native CLEWs Global workflow solves;
- nexus and technical integrity checks pass;
- the no-forcing audit has zero failures;
- all country corrections and adaptations are documented;
- MUIO contains the complete sets and parameters expected after supported
  defaults and documented transformations;
- timeslice season/day/bracket mappings exactly match CLEWs conversions;
- unsupported inputs are explicitly inventoried;
- reserve tags are either imported natively or represented by a validated,
  clearly labelled workaround;
- the reserve workaround checker reports `CURRENT` with zero mismatches;
- the final MUIO run solves;
- parity differences are explained rather than hidden;
- the portable MUIO ZIP passes an archive integrity check; and
- shared MUIO code checksums are unchanged unless the user separately
  authorized a general MUIO software change.

## Delivery language

State:

> This is a technically solved, uncalibrated CLEWs Global country model. It uses
> upstream defaults plus documented technical corrections and country
> adaptations, and it has been imported into MUIO with documented
> representation repairs. No parameters or constraints were introduced to
> force agreement with historical outcomes. Any reserve-margin UDC is a
> labelled workaround for unsupported native tags, not calibration. Historical
> calibration and policy constraints are separate later stages.

Report solver success as technical validity only. Never present it as evidence
of country calibration.
