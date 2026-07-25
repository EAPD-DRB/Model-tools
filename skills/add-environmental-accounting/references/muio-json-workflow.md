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
10. Derive expected technology, commodity, and constraint counts from the account definitions rather than hardcoding totals.
11. Assert that explicitly excluded names and IDs do not appear in the generated accounting structures.

Make target replacement explicit with an `--overwrite` flag. Preserve saved results, validation reports, and model-fix documents separately before overwriting a derived case. Validate a staged sibling first; if a target exists, rename it to a recoverable backup, rename the stage into place, and restore the backup on failure. Retain the backup until the promoted case passes generation, preprocessing, matrix validation, optimization, closure, and regression checks. If generation and computational validation are separate commands, leave the backup in place and report its path until acceptance. Write timestamped or uniquely labeled validation reports so a rerun cannot erase baseline-control or disposable-run evidence.

When migrating an older environmental-accounting case, treat category-specific terminals as an explicit replacement set. Preserve their physical input commodities, remap those commodities to the documented modes of `ENV_WATER` or `ENV_LAND`, and remove only the superseded technologies and their parameter rows. Reconstruct the aggregate constraints from effective source ratios instead of summing or copying old terminal-specific multipliers blindly.

## 3. Parameter coverage

Adding a technology or commodity to `genData.json` is insufficient. Append complete rows for every parameter family that MUIO expects.

For terminal technologies:

- add exactly `ENV_WATER` and `ENV_LAND`, with one documented operating mode per category;
- require every input to a given terminal to use the same physical unit;
- set exactly one IAR of 1 for each active terminal mode and no terminal output;
- use zero capital, fixed, and variable costs;
- use availability/capacity factors consistent with unconstrained annual accounting;
- provide sufficient residual capacity and nonbinding activity limits;
- prevent investment when residual accounting capacity is intended;
- populate every year, timeslice, mode, and scenario record expected by the host model.

Increase the global operating-mode count if either terminal needs a higher mode ID than the source model provides. Inspect the host generation loops and densify every mode-indexed JSON family they traverse—not only rows belonging to the new terminals. Common examples are `RYTM.json`, `RYTCM.json`, `RYTEM.json`, and any storage-mode table. Use the host parameter defaults for inactive base rows and its normal `null` convention for inheriting scenarios. After preprocessing, verify `MODEperTECHNOLOGY`: every original technology retains exactly its intended modes, while `ENV_WATER` and `ENV_LAND` contain only their documented modes.

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

For each environmental domain `D`, first define the set of same-unit commodities consumed by the modes of `ENV_WATER` or `ENV_LAND`. For every connected region, technology, mode, and year, derive:

```text
net[D,r,t,m,y]
  = sum[c in D] (
      effective_OAR[r,t,c,m,y] - effective_IAR[r,t,c,m,y]
    )
```

The common MUIO CAM (Constraint Activity Multiplier) is technology-level, not mode-level. For each original technology, require `net[D,r,t,m,y]` to be identical in every active mode. That common value is the technology's aggregate coefficient. If the values differ by mode, stop: a single technology-level CAM cannot reproduce the commodity balances exactly.

Add every terminal mode's IAR first. Because each is 1, the total-activity coefficient of the corresponding terminal is `-1`. Construct one zero-right-hand-side equality per domain:

```text
sum[t] alpha[D,r,t,y] * TotalAnnualTechnologyActivity[r,t,y]
- TotalAnnualTechnologyActivity[r,ENV_D,y]
= represented demand/capacity/trade terms
```

Individual commodity balances make every category residual nonnegative. The aggregate equality sets the sum of residuals to zero, forcing every terminal mode to consume its full mapped residual. Include only original technologies with a nonzero aggregate coefficient in at least one year, plus the corresponding terminal.

This proof is valid only when all non-activity balance terms are represented. Inspect annual demand, accumulated demand, trade, new-capacity inputs, total-capacity inputs, and any fork-specific terms. If the UDC cannot represent one of them, use reporting-only accounting or request a mode-aware code extension.

For a zero-right-hand-side equality, scaling every coefficient by the same value preserves the identity. Use scaling only to improve conditioning and validate closure from unscaled physical results.

Keep account selection separate from coefficient provenance. Build each domain's producer and consumer membership from the actual commodity links and effective ratios, not from the list of technologies assigned to environmental groups. Use the complete physical contributor set when deriving coefficients and finite activity/capacity envelopes.

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

Do not infer a result key or view-file path from an abbreviation. Read the host `Variables.json` and result-viewer generation code. In forks using the common mapping, `Total Annual Technology Activity By Mode` is stored as `TATABM` in `view/RYTM.json`; `TTMPA` denotes model-period activity and is not a substitute for an annual-by-mode Pivot. Verify the mapping in the target fork before asserting that visualization output exists.

Inspect the processed `MODEperTECHNOLOGY` set before solving. Original technologies must retain their source modes; `ENV_WATER` and `ENV_LAND` must expose only their documented category modes. Treat a missing, duplicated, or unintended mode as a generation failure.

## 7. Validation

### Structural

- no source hash changed;
- new IDs and names are unique;
- all metadata links reference defined IDs;
- all parameter families contain every new technology/commodity/constraint for every scenario;
- exactly two physical environmental terminal technologies exist: `ENV_WATER` and `ENV_LAND`;
- no superseded category-specific terminal technologies remain;
- terminal mode dictionaries, input commodities, descriptions, and same-unit requirements agree;
- every terminal mode has exactly one IAR of 1 and no output;
- all mode-indexed JSON families are dense enough for the host generator;
- processed `MODEperTECHNOLOGY` retains original modes and contains only documented terminal modes;
- base ratios and constraint multipliers have expected signs and values;
- every connected original technology has one domain net coefficient across all active modes;
- aggregate UDC terms cover every non-activity term in the represented commodity balances;
- policy scenario rows follow inheritance rules;
- generated counts equal the lengths derived from the account definitions;
- explicitly excluded names and IDs are absent from new accounting structures;
- result case metadata has valid timestamps.

### Physical

- every terminal mode equals the unscaled residual of its mapped commodity;
- the sum of category residuals equals the unscaled domain UDC identity;
- parallel land-stock outputs equal physical land activity;
- original services remain connected and unchanged;
- technologies excluded from the accounting additions retain their original links and physical contributions to other environmental balances;
- units are internally consistent;
- backstop/dummy production is excluded or separately reported.

### Regression

Compare against saved results from immediately before the change only after verifying that their generated and processed solver inputs match the current source and preprocessing chain. If either differs, label the saved outputs stale and solve a fresh unchanged control. Record the compared hashes, result timestamps, and reason for selecting or rejecting the saved baseline. Store each validation pass under a timestamped or unique label rather than overwriting earlier evidence.

Run the unchanged control and candidate in the same software and solver environment. When preprocessing traverses unordered sets, use the same explicit `PYTHONHASHSEED` and retain both processed-input hashes. A highly degenerate model may select a different cost-identical basis even in the unchanged control; distinguish this from a physical-accounting effect.

Filter only explicitly new account rows. For every intentionally excluded technology or commodity, check that its original links, annual/model-period activity, production, use, costs, and emissions remain unchanged. Also check:

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

Assess runtime separately. Compare matrix or LP dimensions and repeated solve timings; do not attribute a one-run timing change to the accounting layer.

### Results interface

- In the Dynamic Graph, verify each mapped commodity feeds the correct mode of `ENV_WATER` or `ENV_LAND` while the original service links remain.
- In Pivot, select `Total Annual Technology Activity By Mode`, filter `Tech` to `ENV_WATER` and `ENV_LAND`, include `Mo Id`, and interpret the numeric modes with the documented dictionaries.
- For water, report vapor separately from the sum of useful liquid-water modes. Never interpret total `ENV_WATER` activity as useful liquid water.

Primary references:

- [OSeMOSYS documentation](https://osemosys.readthedocs.io/en/latest/manual/Introduction.html)
- [MUIO source repository](https://github.com/OSeMOSYS/MUIO)
