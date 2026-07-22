---
name: add-environmental-accounting
description: Design, implement, regenerate, and validate environmental accounting for a MUIO/OSeMOSYS CLEWS model using technologies and commodities. Use when asked to add Earth-system return flows, residual liquid water, water vapor, land-state accounts, forest or other natural land, emissions, wastewater, brine, backstop diagnostics, or an ENVIRONMENT terminal layer to models such as Zambia, Philippines, or Namibia, especially when edits must originate in the model JSON rather than generated data.txt files.
---

# Add Environmental Accounting

Add a transparent accounting layer without changing the modeled economy or silently inventing environmental data. Treat each model as structurally different: reuse the method, never Namibia-specific identifiers or coefficients.

## Non-negotiable rules

1. Work only on the model named by the user. Keep its source case untouched unless the user explicitly requests an in-place edit.
2. Treat case JSON as source. Never hand-edit `data.txt`, solver output, result CSV files, or Pivot files. Regenerate them with that repository's MUIO code.
3. Preserve every existing physical input, output, cost, demand, and policy connection. Add parallel accounting outputs when a service must continue downstream.
4. Separate physical environmental flows from dummy variables, deficit/backstop supply, and reporting markers.
5. Do not infer units, conversion factors, land suitability, wastewater return rates, desalination recovery, or emissions factors. Mark unavailable accounts as data gaps.
6. Define abbreviations on first use in user-facing answers, including IAR (Input Activity Ratio), OAR (Output Activity Ratio), UDC (User-Defined Constraint), and MUIO (Modelling User Interface for OSeMOSYS).

## Workflow

### 1. Discover the model and its execution path

- Read repository instructions and locate the named case, normally under `WebAPP/DataStorage/<case>`.
- Locate `genData.json`, parameter JSON files, saved results, `Parameters.json`, `Variables.json`, solver model, and the MUIO data-generation/run classes or scripts.
- Confirm regions, scenarios, years, timeslices, modes, existing result cases, and solver. If the bundled audit finds multiple regions, use its summaries only for discovery and validate row-level results by region.
- Run the read-only inventory:

```bash
python scripts/audit_environmental_model.py --model WebAPP/DataStorage/<case>
```

Use the path inside this skill when it is installed elsewhere. Treat its name-based classifications as leads and verify them against ratios, constraints, units, and results. Read [references/accounting-patterns.md](references/accounting-patterns.md) for physical interpretation and [references/muio-json-workflow.md](references/muio-json-workflow.md) before editing.

### 2. Define the accounting boundary

Build a table with one row per proposed account:

| Account | Region | Physical source | Existing human uses | Equation/sign | Unit | Data source/status |
|---|---|---|---|---|---|---|

At minimum investigate:

- water vapor returned through evapotranspiration;
- groundwater and surface water remaining after modeled abstraction;
- forest, grassland, barren/savannah, other natural land, water bodies, built-up land, and cropland;
- native emissions and land-use-change emissions;
- wastewater, desalination feedwater/brine, and resource extraction when coefficients exist;
- backstop/deficit activity as a separate pressure indicator.

Use raw resource-pool commodities for residual water. Do not sum both raw water and its downstream distributed forms. Treat grazed land as environmentally present but human-used; report its land state and pasture service separately.

### 3. Classify special model constructs

- **Dummy land technologies:** inspect their UDC coefficients, activity-change limits, and emissions ratios. Report the signed/net identity; do not call dummy activity physical land.
- **Backstops/deficits:** report separately and exclude from natural resource availability.
- **Shared provenance:** if natural and synthetic/backstop sources produce the same commodity, a simple residual terminal cannot distinguish them. Add a provenance-preserving parallel commodity, calculate a defensible reporting identity, or leave a documented gap.
- **Marker commodities:** a produced commodity with no consumer or demand may be only a scenario/reporting marker. Do not create an environmental terminal for it without a physical interpretation.
- **Missing targets:** distinguish intentional terminal output, capacity-only consumption, broken links, and genuine environmental residuals.

### 4. Select the least intrusive representation

Use these patterns in order of preference:

1. **Endogenous residual:** add a terminal technology consuming the environmental commodity at ratio 1, plus an exact zero-right-hand-side balance over net production. Use an equality because the standard MUIO commodity balance is `production >= use`, which does not force a costless terminal to operate.
2. **Land with an existing service:** add a parallel stock commodity at OAR 1 from the physical land technology; consume only that stock commodity in the environmental terminal. Force that terminal with an equality or proven-fixed bound. Never divert pasture, crops, water, or biomass.
3. **Provably fixed land state:** a terminal may inherit the same annual lower and upper activity value only when the source technology is proven to operate at that value in every year and scenario. Document that it must become an equality account if the source becomes endogenous.
4. **Strict result identity required:** derive a reporting-only account from saved production/use/activity results. Any added solver variable or redundant equality can change the selected basis of a degenerate optimum even when the mathematics and objective are unchanged.

For a one-mode model, an exact account for commodity `c`, region `r`, and year `y` is:

```text
sum over connected technologies t of
  (OutputActivityRatio[r,t,c,y] - InputActivityRatio[r,t,c,y])
  * TotalAnnualTechnologyActivity[r,t,y]
= 0
```

Include the terminal among the connected technologies; its input ratio of 1 supplies the `-terminal_activity` term.

For multiple modes, sum the mode-specific net coefficients. Never assume mode 1.

### 5. Implement through a reproducible JSON generator

Create a model-specific generator in the target model repository. It must:

- copy the source case to a clearly named environmental-accounting case;
- fingerprint every copied input and selected nested definition before and after generation;
- support a dry run, reject unsafe/symlinked path relationships, and write through a temporary target followed by an atomic rename;
- generate collision-free internal IDs;
- add an `ENVIRONMENT` technology group;
- append technologies, commodities, ratios, constraints, and complete default parameter rows across all years, timeslices, modes, and scenarios;
- put base values in the base scenario and preserve the model's null/inheritance convention in other scenarios;
- derive balance coefficients from the model's effective IAR/OAR data rather than transcribing them;
- stop when one shared constraint cannot represent different effective saved-case combinations;
- uniformly scale a zero-right-hand-side equality if coefficients are badly conditioned;
- validate counts, references, ratios, constraint membership, and scenario coverage before writing success.

Set terminal capacity parameters only after reading the host solver equations. Prohibit new investment when residual capacity is intended; ensure residual capacity, capacity-to-activity conversion, capacity factors, and annual/model-period bounds cannot bind the physical account. Record the derivation of every bound. If no finite defensible upper envelope can be proven, stop or use reporting-only accounting instead of inserting an arbitrary large number.

Do not add a generic terminal named `ENVIRONMENT` that combines unrelated flows into one activity level. Use separate terminal technologies grouped under `ENVIRONMENT` so independent quantities and units remain visible.

### 6. Regenerate and solve normally

- Run the generator to create the derived case.
- Invoke the repository's existing MUIO data-file generator for every saved case/scenario combination.
- Run the same solver used by the project.
- Let MUIO regenerate `data.txt`, processed data, linear program, solver output, CSV results, and Pivot metadata.
- Require every case to solve optimally before accepting the accounting layer.
- Parse and retain explicit solver status, version, and run metadata.

Do not guess command names. Inspect the host repository and call its actual classes or scripts.

### 7. Validate physical closure and non-interference

For every case, region, and year, verify:

- each terminal equals its intended production-minus-non-environmental-use identity;
- each parallel land terminal equals its physical land source;
- original pasture/crop/biomass outputs remain unchanged;
- backstop water is not counted as natural water remaining;
- vapor and liquid water remain separate and use documented units;
- native demand and emissions remain unchanged;
- no original technology or commodity link disappeared;
- the source case hashes are unchanged.

Before solving, require an allowlisted structural diff: every original JSON value and link must match, with differences limited to the new accounting records and derived-case metadata.

Before regenerating, preserve the existing results as the baseline. Compare them with:

```bash
python scripts/compare_muio_results.py \
  <baseline-res> <candidate-res> \
  --exclude t=ENVWATVAP --exclude t=ENVLNDFOR
```

Supply every newly added technology, commodity, and constraint value. Examine objective, activity, capacity, demand, emissions, production, use, and costs. Set absolute and relative tolerances per unit and preserve exact changed keys for investigation. Do not describe a run as “unchanged” if it is not row-for-row identical. If only a degenerate route changes, identify the technologies, prove the objective and physical aggregates are unchanged within tolerance, and report the distinction.

### 8. Verify visualization and hand off

- In the Dynamic Graph, confirm each physical source connects through its account commodity to the correct terminal and that original service links remain.
- In Pivot, verify terminal activities under `Total Annual Technology Activity By Mode`, with year as rows and case as columns.
- Explain constants, discontinuities, dummy activity, and any scenario invariance from source equations—not from chart appearance alone.
- Deliver the generator, derived case location, validation results, accounting dictionary, limitations, and exact viewing instructions.

## Acceptance gate

Do not claim completion unless:

- all changes originate in JSON or a generator that writes JSON;
- every configured scenario solves;
- environmental identities close within solver/result precision;
- original physical services are preserved;
- regression differences are quantified honestly;
- dummy/backstop flows are labeled as diagnostics rather than Earth-system stocks;
- every new account has a documented physical meaning and unit.
