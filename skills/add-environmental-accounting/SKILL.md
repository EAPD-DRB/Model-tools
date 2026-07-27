---
name: add-environmental-accounting
description: Design, implement, regenerate, and validate environmental accounting for a MUIO/OSeMOSYS CLEWS model using exact multimode ENV_WATER and ENV_LAND terminals where their independent proofs allow, reporting ledgers where they do not, and an explicitly authorized diagnostic ENV_WATER plus post-solve Pivot publication when a visible water terminal is required despite a failed exactness proof. Use when asked to add Earth-system return flows, residual liquid water, water vapor, land-state accounts, forest or other natural land, emissions, wastewater, brine, backstop diagnostics, or an ENVIRONMENT accounting layer to models such as Zambia, Philippines, or Namibia.
---

# Add Environmental Accounting

Add a transparent accounting layer without changing the modeled economy or silently inventing environmental data. Treat each model as structurally different: reuse the method, never Namibia-specific identifiers or coefficients.

## Non-negotiable rules

1. Work only on the model named by the user. Keep its source case untouched unless the user explicitly requests an in-place edit.
2. Treat case JSON as source. Never hand-edit `data.txt`, solver output,
   result CSV files, or Pivot files. Regenerate them with that repository's
   MUIO code. The only Pivot exception is an explicitly authorized,
   reproducible post-solve publisher for a separately named unforced
   diagnostic terminal; it must preserve raw solver artifacts and follow the
   safeguards below.
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
- **Account membership versus flow provenance:** determine terminal membership separately from physical-flow membership. Derive every active producer and consumer from the commodity graph; a technology excluded from an environmental terminal may still contribute runoff, recharge, evapotranspiration, emissions, or another environmental flow.
- **Marker commodities:** a produced commodity with no consumer or demand may be only a scenario/reporting marker. Do not create an environmental terminal for it without a physical interpretation.
- **Missing targets:** distinguish intentional terminal output, capacity-only consumption, broken links, and genuine environmental residuals.

### 4. Use domain-specific multimode terminals

Use this default architecture:

```text
ENV_WATER
  mode 1: water vapor
  mode 2: remaining groundwater
  mode 3: remaining surface water

ENV_LAND
  mode 1: forest
  mode 2: grassland
  mode 3: other land
  mode 4: barren/savannah
```

Evaluate the exactness proof independently for each domain. A failed
`ENV_WATER` proof does not block an exact `ENV_LAND`, and a failed `ENV_LAND`
proof does not block an exact `ENV_WATER`. When only one domain passes, use a
documented mixed architecture: add only the safe in-model terminal and keep
the failed domain reporting-only. Never turn one domain's failure into an
all-or-nothing decision for both terminals.

Extend the mode dictionaries only for physically documented accounts such as wastewater, brine, cropland, built land, or water bodies. Keep the mapping stable and record it in technology descriptions and the accounting dictionary because MUIO commonly exposes numeric mode IDs without mode labels.

Require every commodity entering one terminal to use the same physical unit. Normalize with documented conversions or stop; never combine area and volume, or incompatible water units, in one activity variable. Report `ENV_WATER` by mode: vapor is not useful liquid water, and the technology total is not a useful-water indicator.

Give each mode exactly one environmental input at IAR 1 and no output. For land technologies that already provide pasture, crops, runoff, or evapotranspiration, add a parallel area-stock commodity at OAR 1 and feed that stock—not the existing service—to `ENV_LAND`.

Force exact accounting with one aggregate equality per terminal. Standard MUIO commodity balances are inequalities, while the common UDC activity multiplier is technology-level rather than mode-level. For domain `D`, use:

```text
sum[t] alpha[D,t,y] * TotalAnnualTechnologyActivity[t,y]
- TotalAnnualTechnologyActivity[ENV_D,y]
= represented demand/capacity/trade terms
```

where `alpha[D,t,y]` is the sum of net OAR-minus-IAR coefficients across the domain commodities. Individual commodity balances make every unconsumed residual nonnegative; the aggregate equality makes their sum zero, so every mode consumes its complete residual.

Use this proof only when:

- every input mode of the terminal has IAR 1;
- all non-activity terms in the commodity balances are represented in the aggregate equality;
- every connected original technology has the same domain net coefficient in each active mode, so one technology-level UDC multiplier is exact; and
- no omitted provenance, trade, demand, or capacity term can create an unrepresented residual.

If any condition fails for domain `D`, stop the in-model implementation for
that domain and use reporting-only accounting for `D`, or request
authorization for a mode-aware model extension. Continue assessing the other
domain independently. Do not generate a plausible-looking but inexact
multimode terminal.

An explicitly user-requested experiment may add an **unforced diagnostic**
terminal for a failed domain, but only in a separate, clearly named diagnostic
case. Give it no forcing UDC, no demand, no output, zero cost, and finite
nonbinding bounds. Keep the external production-minus-ordinary-use ledger
authoritative, exclude the diagnostic terminal's own consumption from that
reference, and reconcile reference, terminal activity, gap, and coverage for
every run, region, year, and mode. Treat `FULL`, `PARTIAL`, `ZERO`, and `EMPTY`
as empirical solver outcomes—not acceptance states—and never promote the
diagnostic terminal as exact accounting. Follow the detailed safeguards in
[references/muio-json-workflow.md](references/muio-json-workflow.md).

If the user also requires that terminal to remain visible in the Dynamic
Graph while Results Pivot shows the authoritative reference, create a
model-specific post-solve publisher. Update only the diagnostic terminal's
linked generated view rows, back up the original solver-generated views,
preserve and hash every raw solver result, publish from the independent
production-minus-ordinary-use calculation, and label the result as
postprocessed reporting rather than optimizer output. Make publication
atomic, validated, and repeatable after every solve. Never apply this
exception to an ordinary production case or use it to conceal a failed
solve.

When strict row-for-row result identity is required, prefer reporting-only accounts. Added solver variables or equalities can change the selected basis of a degenerate optimum even when objective and physical aggregates are unchanged.

### 5. Implement through a reproducible JSON generator

Create a model-specific generator in the target model repository. It must:

- copy the source case to a clearly named environmental-accounting case;
- fingerprint every copied input and selected nested definition before and after generation;
- support a dry run, reject unsafe/symlinked path relationships, and write through a temporary target followed by an atomic rename;
- generate collision-free internal IDs;
- add an `ENVIRONMENT` technology group;
- add the safe subset of `ENV_WATER` and `ENV_LAND` as the only physical
  environmental terminal technologies; if both domains pass, add both, and if
  only one passes, omit the unsafe terminal and document its reporting-only
  account, except in the separately named unforced diagnostic experiment
  described above;
- assign one stable operating mode per documented water or land category;
- append technologies, commodities, ratios, constraints, and complete default parameter rows across all years, timeslices, modes, and scenarios;
- increase the global mode count when necessary and densify every mode-indexed JSON family expected by the host MUIO generator, including inactive default rows for pre-existing technologies;
- put base values in the base scenario and preserve the model's null/inheritance convention in other scenarios;
- derive each implemented domain's aggregate balance coefficient map from
  effective IAR/OAR data and every representable non-activity balance term
  rather than transcribing it;
- reject source technologies whose domain coefficients differ by active mode when the host UDC is technology-level;
- stop when one shared constraint cannot represent different effective saved-case combinations;
- uniformly scale a zero-right-hand-side equality if coefficients are badly conditioned;
- derive expected structural counts from the account definitions rather than hardcoding numeric totals;
- assert that intentionally excluded technologies, commodities, and constraints are absent from the accounting additions; and
- validate counts, references, ratios, constraint membership, and scenario coverage before writing success.

Set terminal capacity parameters only after reading the host solver equations. Prohibit new investment when residual capacity is intended; ensure residual capacity, capacity-to-activity conversion, capacity factors, and annual/model-period bounds cannot bind the physical account. Record the derivation of every bound. If no finite defensible upper envelope can be proven, stop or use reporting-only accounting instead of inserting an arbitrary large number.

Do not add a generic terminal named `ENVIRONMENT`. Use `ENV_WATER` and `ENV_LAND`, grouped under `ENVIRONMENT`, and preserve their categories as operating modes.

If an older derived case already has one terminal per environmental category, migrate it through the JSON generator: preserve the physical accounting commodities, map each one to the documented mode of `ENV_WATER` or `ENV_LAND`, and remove only the superseded terminal technologies and their terminal-specific parameter rows. Rebuild each implemented domain's aggregate constraint from the effective source ratios; do not reuse the old per-terminal coefficient maps without proving the aggregate identities.

When replacing an existing derived case, preserve its results, validation reports, model-fix documents, and a recoverable backup until the promoted case passes the full generation, matrix, solve, closure, and regression chain. Use timestamped or uniquely labeled validation reports; do not overwrite evidence from an earlier baseline or disposable run.

### 6. Regenerate and solve normally

- Run the generator to create the derived case.
- Invoke the repository's existing MUIO data-file generator for every saved case/scenario combination.
- Run the same solver used by the project.
- Let MUIO regenerate `data.txt`, processed data, linear program, solver output, CSV results, and Pivot metadata.
- Require every case to solve optimally before accepting the accounting layer.
- Parse and retain explicit solver status, version, and run metadata.
- For an authorized diagnostic Pivot publication, run the publisher only
  after MUIO finishes all required view generation. Use a unique evidence
  label and rerun it after every subsequent solve.

Do not guess command names. Inspect the host repository and call its actual classes or scripts.

### 7. Validate physical closure and non-interference

For every case, region, and year, verify:

- each `ENV_WATER` or `ENV_LAND` mode equals the residual of its mapped commodity;
- each parallel land-stock commodity equals its physical land source;
- the sum of the mode-level residuals equals the corresponding aggregate UDC identity;
- original pasture/crop/biomass outputs remain unchanged;
- backstop water is not counted as natural water remaining;
- vapor and liquid water remain separate and use documented units;
- native demand and emissions remain unchanged;
- every intentionally excluded pathway retains its original links, annual/model-period activity, production, use, costs, and emissions;
- no original technology or commodity link disappeared;
- the source case hashes are unchanged.

Before solving, require an allowlisted structural diff: every original JSON value and link must match, with differences limited to the new accounting records and derived-case metadata.

Before regenerating, preserve the existing results as the baseline. Verify that their generated and processed solver inputs match the current source and preprocessing chain. If they do not, mark them stale and solve a fresh unchanged control, retaining the hashes and reason for rejecting the saved baseline. Compare the accepted baseline with:

```bash
python scripts/compare_muio_results.py \
  <baseline-res> <candidate-res> \
  --exclude t=ENV_WATER --exclude t=ENV_LAND
```

Supply every newly added technology, commodity, and constraint value. Examine objective, activity, capacity, demand, emissions, production, use, and costs. Set absolute and relative tolerances per unit and preserve exact changed keys for investigation. Do not describe a run as “unchanged” if it is not row-for-row identical. If only a degenerate route changes, rerun the unchanged control in the same environment, identify the affected technologies, prove objective and physical aggregates are unchanged within tolerance, and report the distinction. When preprocessing uses unordered sets, run control and candidate with the same explicit Python hash seed and retain both processed-input hashes.

Measure runtime separately from correctness. Compare generated matrix or LP size and repeat timings; do not infer a slowdown from one solve of a highly degenerate model.

### 8. Verify visualization and hand off

- In the Dynamic Graph, confirm each in-model domain's physical source
  connects through its account commodity to the implemented `ENV_WATER` or
  `ENV_LAND` terminal and that original service links remain. Confirm that a
  reporting-only domain has no misleading terminal in a production case. In
  an authorized diagnostic case, confirm that the terminal is visibly labeled
  unforced and non-authoritative.
- Resolve result keys and view-file locations from the host `Variables.json` and viewer-generation code; do not infer them from abbreviations. In forks using the common mapping, `Total Annual Technology Activity By Mode` is `TATABM` in `view/RYTM.json`, while `TTMPA` is model-period activity and is not the annual Pivot.
- In Pivot, verify each implemented `ENV_WATER` or `ENV_LAND` terminal under
  `Total Annual Technology Activity By Mode`, include `Mo Id`, and check every
  mode against the documented category mapping. View reporting-only domains
  in their generated ledger instead. For an authorized diagnostic
  publication, verify every linked activity/use view, retain the original
  solver-selected terminal result in the raw CSVs and backup, and state
  prominently that Pivot is a postprocessed reporting surface.
- Explain constants, discontinuities, dummy activity, and any scenario invariance from source equations—not from chart appearance alone.
- Deliver the generator, derived case location, validation results, accounting dictionary, limitations, and exact viewing instructions.

## Acceptance gate

Do not claim completion unless:

- all in-model changes originate in JSON or a generator that writes JSON;
- every configured scenario solves;
- environmental identities close within solver/result precision;
- the generated case has no superseded category-specific environmental terminal technologies;
- every implemented terminal's mode mapping and units are documented and
  validated, and every omitted unsafe domain has a documented reporting-only
  mapping and failed-proof evidence;
- original physical services are preserved;
- intentionally excluded pathways are proven unchanged and absent from the accounting additions;
- regression differences are quantified honestly;
- dummy/backstop flows are labeled as diagnostics rather than Earth-system stocks;
- every new account has a documented physical meaning and unit.
- any authorized unforced diagnostic terminal is delivered separately, has no
  forcing mechanism, is reconciled against an authoritative reference that
  excludes its own consumption, and is not claimed as a completed exact
  environmental account.
- any authorized diagnostic Pivot publisher is case-restricted, atomic,
  rerunnable after each solve, preserves raw-result hashes and original views,
  changes no non-terminal row, validates all linked activity/use identities,
  and marks published values as reporting-layer rather than solver output.
