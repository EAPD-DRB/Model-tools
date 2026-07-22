# Environmental accounting patterns for CLEWS

Use this reference while interpreting flows and choosing accounts. Values and identifiers are illustrative; derive them from the target model.

## Contents

1. Accounting boundary
2. Exact terminal pattern
3. Water
4. Land
5. Emissions
6. Dummies, backstops, and markers
7. Numerical behavior
8. Extension checklist

## 1. Accounting boundary

Environmental accounting should distinguish:

- **inflows from the Earth system:** precipitation, raw groundwater/surface water, biomass, land endowment, fossil resources;
- **human transformations and uses:** abstraction, distribution, irrigation, livestock grazing, crops, power generation, land conversion;
- **returns to the Earth system:** evapotranspiration, wastewater, brine, air emissions, residues;
- **remaining stocks or annual states:** water remaining in modeled pools and land allocated to environmental or human-influenced classes;
- **diagnostics:** backstop supply, unmet-demand technologies, dummy variables, and unallocated resources.

Do not combine flows and stocks in one total. Do not label a residual “available” unless the model represents accessibility, quality, timing, and ecological reserve requirements.

## 2. Exact terminal pattern

Standard MUIO/OSeMOSYS annual and timeslice commodity balances are inequalities:

```text
production >= demand + use
```

A zero-cost terminal consumer can therefore stay at zero. Force an exact account with a zero-right-hand-side equality over net commodity coefficients:

```text
sum[t,m] (OAR[t,c,m,y] - IAR[t,c,m,y]) * Activity[t,m,y] = 0
```

The terminal has IAR 1, so its contribution is negative and its activity equals the residual. Here IAR is Input Activity Ratio and OAR is Output Activity Ratio.

Include every active producer and consumer and resolve scenario inheritance before constructing coefficients. If scenario overrides alter ratios, build coefficients for each effective scenario combination or stop and explain why the simple pattern is unsafe.

Uniformly multiplying all coefficients in a zero-right-hand-side equality by the same nonzero factor does not change its mathematics. Use this only for conditioning, and document it.

## 3. Water

### Residual liquid water

Prefer raw resource-pool commodities:

```text
groundwater remaining = raw groundwater production - non-environmental raw groundwater use
surface water remaining = raw surface-water production - non-environmental raw surface-water use
```

Do not add raw water and distributed water: that double-counts the same water at two network stages. Report groundwater and surface water separately, then optionally sum them only after unit normalization.

### Water vapor

If land technologies output evapotranspiration, route that commodity to a vapor terminal. Water vapor is a return to the atmosphere, not useful residual liquid water.

### Backstops

A high-cost groundwater or surface-water deficit technology is synthetic feasibility supply. Report its activity as water stress. Exclude it from natural availability and verify whether its output can enter a residual terminal.

### Wastewater and desalination

Add these only with documented coefficients:

- sectoral wastewater return fraction and destination;
- treatment/reuse losses;
- seawater feed and desalination recovery ratio;
- brine volume and unit.

Do not derive brine from desalinated output unless feedwater and recovery are known. Normalize units before connecting commodities.

## 4. Land

### Parallel stock account

When a land technology already produces pasture, crops, runoff, or evapotranspiration, preserve those outputs and add a parallel stock commodity:

```text
LNDGRS --OAR 1--> LNDGRSSTK --IAR 1--> ENVLNDGRS
       --existing--> pasture and water flows
```

The stock output reports area; it does not create another area or consume the pasture service.

### Interpretation

- Grazed land remains part of the environment but is human-used. Report both facts.
- “Other land” is whatever the source model defines; do not infer forest suitability.
- Forest remaining is meaningful only if forest can vary. A fixed forest technology reports a fixed assumption, not an optimized ecological residual.
- Unallocated land exists only if the model has an explicit full-endowment closure and a residual category. Do not infer it by subtracting incomparable land activities.
- Solar or infrastructure land is a capacity-linked use only if a footprint coefficient is present.

### Fixed terminals

A fixed terminal is acceptable only when all current scenarios and years prove the source activity equals a common exogenous bound. Copy the bound through JSON, preserve the parallel commodity, validate terminal-to-source equality after every run, and document that future endogenous behavior requires an equality account.

## 5. Emissions

Use the model's native emissions mechanism for existing atmospheric accounts. Confirm:

- emission unit and scale;
- positive process/fuel/livestock factors;
- negative sequestration factors;
- activity-change emissions and their first-year treatment;
- annual and model-period limits;
- whether dummy land technologies proxy land-use change.

Do not disaggregate carbon-dioxide-equivalent emissions into gases without source factors.

## 6. Dummies, backstops, and markers

### Land-balance dummies

A common pattern is:

```text
physical land + dummy reduction - dummy increase = reference land
```

Only the signed identity is physical. A constant dummy reduction means the current stock is below a reference; it is not necessarily an annual loss. If reduction and increase operate simultaneously, inspect activity-change limits and emissions equations before interpreting either series.

The dummy commodity may have no consumer because the technologies exist primarily as variables in a UDC (User-Defined Constraint). Do not send that commodity to the environment.

### Backstop technologies

High-cost `BST*`, deficit, import, or unmet-demand technologies keep a model feasible. Their use is a diagnostic failure/stress indicator, not a natural flow.

### Marker commodities

A scenario may give a technology an otherwise unused output solely to make activity visible or tag a pathway. If it has no consumer, demand, capacity use, constraint, or physical unit interpretation, treat it as metadata—not an environmental residual.

## 7. Numerical behavior

Adding a zero-cost variable or redundant equality preserves the feasible objective mathematically but can change the basis selected in a degenerate linear program. Typical symptoms include:

- switching between equal-cost groundwater and surface-water routes;
- changes in unused capacity variables;
- small rounded cost differences;
- identical demand/emissions with different technology-level activity.

Compare both row-level results and invariant aggregates. Never hide this distinction. Prefer a reporting-only account when the user requires byte-for-byte identity.

## 8. Extension checklist

After the core accounts work, assess these separately:

- wastewater and reuse;
- seawater and brine;
- crop residues and biomass harvest;
- fossil extraction and depletion;
- air pollutants beyond greenhouse gases;
- energy-infrastructure land footprints;
- ecological reserve constraints;
- land restoration and degradation;
- explicit unallocated land;
- water quality and salinity.

Each extension requires a physical coefficient, unit, source, and validation identity.
