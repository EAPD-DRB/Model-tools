# MUIO JSON implementation workflow

Use this reference while writing the model-specific generator. Inspect the host repository because MUIO forks differ.

## Contents

1. Source files
2. Safe generator contract
3. Parameter coverage
4. Scenario inheritance
5. Constraint construction
6. Regeneration
7. Validation

## 1. Source files

Typical case files under `WebAPP/DataStorage/<case>` include:

| File | Environmental-accounting role |
|---|---|
| `genData.json` | Technologies, commodities, emissions, groups, constraints, scenarios, years, timeslices, modes, and metadata |
| `RT.json` | Region-technology parameters such as discount rate and model-period activity limit |
| `RYT.json` | Annual technology costs, residual capacity, availability, and annual activity/capacity bounds |
| `RYTM.json` | Mode-specific annual variable cost and mode activity limits |
| `RYTTs.json` | Technology-timeslice parameters such as capacity factor |
| `RYC.json` | Annual commodity demands and reserve-margin metadata |
| `RYCTs.json` | Commodity demand profiles by timeslice |
| `RYTCM.json` | Input and Output Activity Ratios by technology, commodity, mode, and year |
| `RYCn.json` | Annual constraint constants |
| `RYTCn.json` | Technology multipliers for constraints |
| `RYTEM.json` | Emission Activity Ratios and activity-change emission ratios |
| `view/resData.json` | Saved case/scenario combinations; copy definitions, refresh valid runtime metadata |

Use `WebAPP/DataStorage/Parameters.json` to obtain defaults. Do not assume every fork has exactly these parameter identifiers.

## 2. Safe generator contract

The generator should:

1. Reject any source other than the explicitly named model.
2. Reject source and target paths that resolve to the same directory.
3. Recursively fingerprint every copied input, including selected nested view definitions.
4. Copy only source JSON and selected view definitions into a separate target.
5. Detect identifier and human-readable-name collisions before appending.
6. Reject source/target symlink or ancestor relationships that could overwrite the source.
7. Support `--dry-run`; write formatted UTF-8 JSON to a temporary sibling and atomically rename only after validation.
8. Validate the generated case and an allowlisted structural diff.
9. Re-fingerprint the source and fail if it changed.

Make target replacement explicit with an `--overwrite` flag. Preserve saved results separately before overwriting a derived case. Validate a staged sibling first; if a target exists, rename it to a recoverable backup, rename the stage into place, and restore the backup on failure. Remove the backup only after post-rename validation succeeds.

## 3. Parameter coverage

Adding a technology or commodity to `genData.json` is insufficient. Append complete rows for every parameter family that MUIO expects.

For terminal technologies:

- use zero capital, fixed, and variable costs;
- use availability/capacity factors consistent with unconstrained annual accounting;
- provide sufficient residual capacity and nonbinding activity limits;
- prevent investment when residual accounting capacity is intended;
- populate every year, timeslice, mode, and scenario record expected by the host model.

Derive capacity settings from the host equations: the maximum feasible terminal activity must remain below residual capacity multiplied by capacity-to-activity conversion and effective availability/capacity factors. Set investment limits to zero when the terminal is not an investment option, and keep annual/model-period activity bounds nonbinding unless implementing a proven-fixed account. If no finite defensible upper envelope exists, stop or use reporting-only accounting.

For stock commodities:

- append annual commodity defaults;
- append timeslice demand-profile defaults if the file schema requires them;
- add metadata and units in `genData.json`.

For constraints:

- add constraint metadata and connected technology IDs;
- add annual constants using the host equality tag and zero right-hand side;
- add annual technology multipliers;
- inspect the solver file to verify tag semantics and equations.

Never copy a Namibia internal ID such as `TEC_*`, `COM_*`, or `CO_*` into another model.

## 4. Scenario inheritance

MUIO models commonly store full values in the base scenario and `null` in policy scenarios to inherit the base. Preserve the target model's convention.

Before deriving balance coefficients, resolve whether non-base scenarios override any connected IAR/OAR values. If they do, either:

- construct case-combination-aware coefficients; or
- stop and implement reporting-only accounting.

Do not silently use base coefficients for a scenario with effective ratio changes.

Inspect the host MUIO scenario resolver (for example `getScOrder` and the parameter-generation loops) and reproduce its exact precedence; do not assume list order. The usual conceptual pattern is parameter defaults, then base values, then active-scenario non-null overrides. Resolve independently for every full index tuple, region, mode, and year. If two saved-case combinations require different coefficients but MUIO exposes only one shared constraint parameterization, stop rather than generating a misleading account.

## 5. Constraint construction

For commodity `c`, derive the net coefficient for every connected region, technology, and mode:

```text
net[r,t,m,y] = effective_OAR[r,t,c,m,y] - effective_IAR[r,t,c,m,y]
```

Add the terminal's IAR first, then derive the coefficient map so it naturally receives `-1`. Include only technologies in the constraint membership list that have a nonzero net coefficient in at least one year.

For a zero-right-hand-side equality, scaling every coefficient by the same value preserves the identity. Use scaling only to improve conditioning and validate closure from unscaled physical results.

## 6. Regeneration

Discover the host command with repository search, for example:

```bash
rg -n "def (generateDatafile|batchRun|run)|class DataFile" API WebAPP
```

A common Python API is conceptually:

```python
from Classes.Case.DataFileClass import DataFile

model = DataFile("<derived-case>")
for case in case_names:
    model.generateDatafile(case)
model.batchRun("cbc", case_names)
```

Do not paste this blindly. Confirm import paths, solver names, case metadata, and return status in the host repository.

Generated artifacts may include `data.txt`, `data_processed.txt`, a linear-program file, `results.txt`, CSV result variables, and Pivot/view data. Generate all of them through MUIO.

## 7. Validation

### Structural

- no source hash changed;
- new IDs and names are unique;
- all metadata links reference defined IDs;
- all parameter families contain every new technology/commodity/constraint for every scenario;
- base ratios and constraint multipliers have expected signs and values;
- policy scenario rows follow inheritance rules;
- result case metadata has valid timestamps.

### Physical

- terminal activity equals its unscaled physical identity;
- parallel land outputs equal physical land activity;
- original services remain connected and unchanged;
- units are internally consistent;
- backstop/dummy production is excluded or separately reported.

### Regression

Compare against saved results from immediately before the change. Filter only explicitly new account rows. Check:

- objective value;
- annual and model-period technology activity;
- capacity and investment;
- demand;
- production and use;
- emissions and activity-change emissions;
- fixed and variable costs;
- policy constraints and backstop activity.

Use both absolute and relative tolerances chosen for each unit, reject non-finite values, retain duplicate dimension keys as errors, and record exact changed keys. Parse every `results.txt` (or host equivalent) and fail on missing or non-optimal status before interpreting numeric comparisons.

When differences occur, identify exact rows, quantify absolute and relative changes, and distinguish physical changes from alternate cost-identical routing.

Primary references:

- [OSeMOSYS documentation](https://osemosys.readthedocs.io/en/latest/manual/Introduction.html)
- [MUIO source repository](https://github.com/OSeMOSYS/MUIO)
