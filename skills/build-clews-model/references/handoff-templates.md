# Required handoff templates

Use these headings and fields so every country package has predictable
government-review, audit, import, and calibration artifacts.

## Contents

- `DATA_SOURCE_REGISTER.md`
- `MODEL_CARD.md`
- `CALIBRATION_HANDOFF.md`
- `MUIO_IMPORT.md`
- `diagnostics/validation_summary.json`

## `DATA_SOURCE_REGISTER.md`

```markdown
# Data source register

## Build identity

- Country:
- ISO3:
- Scenario:
- Model horizon:
- Register date:

## Exact sources

| Source ID | Provider | Product | Edition | Year/period/scenario | Variable | Source unit | Geography/resolution | Model use | Selection | Transformation | Quality | Proxy | Official URL | License | National alternative | Review owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Crop selection and proxies

| Source item/code | Rank | Area value/unit/year | Area quality | Production value/unit/year | Production quality | Output or aggregate | GAEZ code/layer | Water/input cases | Climate model/pathway/period | AWC | Proxy rationale | Expected limitation |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|

## Government review

| Decision | Current source or assumption | Why it matters | Suggested reviewer | Better national data? | Status |
|---|---|---|---|---|---|

## Notes

- This register identifies the exact sources and assumptions used so reviewers
  can accept them or propose better national data.
- A raw-data copy is not required unless a separate reproducibility or licensing
  requirement calls for one.
- Proposed replacements are not applied silently to this raw build.
```

## `MODEL_CARD.md`

```markdown
# Model card

## Identity and status

- Country / ISO3:
- Scenario:
- Whole-country scope:
- Horizon:
- Upstream status:
- MUIO import status:
- Final MUIO status:
- Intended use:
- Explicitly unsuitable uses:

## Structural configuration

| Choice | Value | Evidence/source ID | Affected sets or parameters | Uncertainty | Sensitivity candidate |
|---|---|---|---|---|---|

Cover administrative resolution, boundary, nodes, grid/island topology,
seasons, dayparts, time zone, climate pathway, clustering, trade, storage,
technology applicability, crops, land, and water.

## Nexus representation

Describe how energy, land, agriculture, water, climate, and emissions are
physically connected. Identify any absent sector or unconnected component.

## Technical corrections

| Defect | Upstream revision | Patch | Regression fixture | Parameter values changed? | Result |
|---|---|---|---|---|---|

## Limitations

State raw-model discontinuities, unsupported data, proxies, spatial/temporal
limitations, and outstanding calibration needs.

## Non-forcing declaration

State that no historical outcome was used to choose a raw-model coefficient,
bound, or constraint, and link the machine-readable audit.
```

## `CALIBRATION_HANDOFF.md`

```markdown
# Calibration handoff

This document records later calibration candidates. None of the observations
or candidate changes below is applied to the raw build.

## Diagnostic gaps

| Sector/metric | Observed source | Geography/period/unit | Observed value | Raw model value | Difference | Suspected cause | Candidate future parameter or constraint | Applied in raw model |
|---|---|---|---:|---:|---:|---|---|---|

Every `Applied in raw model` entry must be `No`.

## Data requested from national counterparts

| Dataset | Preferred institution | Definition needed | Model use | Priority |
|---|---|---|---|---|

## Suspicious raw outputs

List discontinuities, implausible magnitudes, inactive technologies, unused
resources, or unconstrained flows. Do not fix them here.

## Calibration boundary

Describe the explicit version boundary between this technically solved raw
model and any future calibrated model.
```

## `MUIO_IMPORT.md`

```markdown
# MUIO import

## Version and checksum record

| Component | Version/commit | Checksum |
|---|---|---|

Cover CLEWs Global, submodules, otoole configuration, MUIO importer, parameter
registry, and active formulation.

## Separate statuses

| Stage | Status | Solver status | Evidence |
|---|---|---|---|
| Authoritative upstream raw model |  |  |  |
| Complete MUIO import |  | n/a |  |
| Final MUIO model |  |  |  |

## Capability inventory

Link the machine-readable inventory and summarize unsupported, transformed,
workaround, and failed parameters.

## Workbook preparation

Record technology grouping, descriptions, discount-rate handling, empty-sheet
handling, worksheet aliases, and probe results.

## Temporal repair

Record backups, source conversion matrices, repair command, and exact parity
status.

## Input parity

| Class | Row count |
|---|---:|
| Exact |  |
| Implicit default |  |
| Transformed |  |
| Workaround |  |
| Unsupported |  |
| Error |  |

Any error or unsupported nondefault source row blocks completion.

## Association expansion

| Association | Source count | Imported count | Ratio | Explanation/status |
|---|---:|---:|---:|---|

## Result parity

Summarize overlapping outputs, objectives, units, tolerances, and formulation
differences. Never tune inputs to improve parity.

## Reserve-margin representation

State native support or the exact documented workaround and stale-check status.

## Reproduction and restore

Provide exact import, repair, parity, estimate, generate, solve, validate,
package, and restore commands.
```

## `diagnostics/validation_summary.json`

```json
{
  "upstream_raw": {
    "status": "pending",
    "solver_status": null,
    "evidence": null
  },
  "muio_import": {
    "status": "pending",
    "nondefault_errors": null,
    "unsupported_nondefault_rows": null,
    "evidence": null
  },
  "muio_final": {
    "status": "pending",
    "solver_status": null,
    "evidence": null
  }
}
```
