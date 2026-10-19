# Philippines (PHL): case notes for the OG skills

Country-specific results behind lessons in the OG skills (og-country-calibration,
og-multi-industry-calibration, og-solver-diagnosis, og-run). The skills teach the method; these
are one country's numbers, kept here so the skills stay general. They record what was true when
written; check the country repo before relying on any of them. Do not copy them into another
country's calibration.

## model K/Y level

Source: og-country-calibration/references/validation-dashboard.md, section "Know the family traits before fixing them"
The model's endogenous `K/Y` runs high against the PWT across the family (ZAF 4.5 vs 3.7; PHL 4.3).

## debt-path min-only check

Source: og-country-calibration/references/validation-dashboard.md, section "Verify both tails of every path"
**[PHL, a caught error]** A min-only check on the debt path ("trough = 60.0, stays on target")
passed while the path climbed to 74%; the check tested only the direction the previous failure
pointed.

## loosened RC_TPI

Source: og-country-calibration/references/households-demographics.md, section "Discontinuities: the frozen window and fixper"
A sibling's JSON may carry a loosened value (OG-PHL ships 0.01) that the audit should catch and
either justify or tighten.

## start year one past the latest data

Source: og-country-calibration/references/macro-open-economy.md, section "start_year"
PHL shipped start 2026 while its latest data was 2025: the packaged `initial_debt_ratio` 0.60 was the beginning-of-2025 value (a 2026 start needed ~0.62), and the 2025-observed remittance ratio was treated as a 2026 extrapolation.
Exemplar. PHL (caught by the user, moved 2026 → 2025).

## zeta_K re-tune after tax recalibration

Source: og-country-calibration/references/macro-open-economy.md, section "zeta_K"
PHL: honest taxes pushed it 0.26 → 0.14; `zeta_K` 0.4 → 0.47 restored the 0.20 IIP anchor.

## mislabelled fiscal year for interest

Source: og-country-calibration/references/macro-open-economy.md, section "r_gov base wedge (r_gov_scale, r_gov_shift)"
PHL's widely quoted "FY2024" interest figure was FY2025.

## effective r_gov levels (also ZAF)

Source: og-country-calibration/references/macro-open-economy.md, section "r_gov base wedge (r_gov_scale, r_gov_shift)"
It over-predicted ZAF by ~0.5–0.6pp and PHL by ~3pp (5.1% vs the ~2.0% the Treasury pays).
Exemplar. ZAF (~3.7%), PHL (~2.0%).

## g_RM in nominal units, and the cash-measure trap

Source: og-country-calibration/references/macro-open-economy.md, section "Remittances and aid (alpha_RM_1, alpha_RM_T, eta_RM, g_RM, alpha_FA)"
PHL shipped `g_RM = 0.03` (Dec-on-Dec USD growth) against a ~5.7% model-consistent denominator, so RM/Y fell 35% below its calibrated share by t≈24 and recovered only after t≈100, with nothing in the docs intending it. The cash-measure trap: PHL's 0.072 came from a central-bank headline that was the cash series (personal was 8.1%).

## household balance-sheet wealth ratios (also ZAF, ETH)

Source: og-country-calibration/references/macro-open-economy.md, section "Initial household wealth"
OG-Core's own documentation tabulates these, e.g. PHL 2.50, ZAF 2.56, ETH 1.70.

## wealth needed to hit the IIP foreign share

Source: og-country-calibration/references/macro-open-economy.md, section "Initial household wealth"
PHL: hitting the IIP share would have needed 4.3 against a measured 3.35.

## old default scale windfall

Source: og-country-calibration/references/macro-open-economy.md, section "Initial household wealth"
PHL's old default scale was 1.625 (a 63% windfall): retirees consumed at 3–7× steady state for years, C jumped 41% for one year, domestic investment fell to ~2% of long run, and debt was paid down to 50% against a 60% target.

## make-matrix structure

Source: references/inputs.md, section "Finding the data"
Check it: PHL's off-diagonal share is exactly 0 (diagonal make).

## utility industries

Source: references/inputs.md, section "Defining industries and goods"
PHL: Electricity and Water.

## goods

Source: references/inputs.md, section "Defining industries and goods"
PHL I=5 (food, energy, non-durables, durables, services).

## gamma rescale target

Source: references/inputs.md, section "gamma_m"
PHL lands exactly (target 0.58785, private mean 0.53785 = the base `gamma`).

## capital shares of capital-intensive industries

Source: references/inputs.md, section "gamma_m"
Healthy capital-intensive industries (mining, utilities around 0.78 in PHL) solve fine.

## traced household energy row

Source: references/inputs.md, section "io_matrix"
Traced, household energy goes mostly to electricity (74% in PHL, against a manufacturing-heavy
naive split).

## capital-output ratio

Source: references/inputs.md, section "Z_m"
The capital-output ratio from PWT for the SAM year: PHL 2.91.

## Z ranking

Source: references/inputs.md, section "Z_m"
Agriculture lowest in PHL.

## composite-price units constant

Source: references/alignment.md, section "How OG-Core treats industries"
`k = prod_i alpha_c_i^(−alpha_c_i)` (1 when I = 1; 2.97 for PHL's five goods).

## chi conversion before and after

Source: references/alignment.md, section "The chi units conversion"
PHL (k = 2.97, σ = 1.5, scale 1.72):

| | single | M=8 before | M=8 after |
|---|---|---|---|
| r | 0.0708 | 0.0885 | 0.0808 |
| K_f/K | 0.257 | 0.528 | 0.336 |
| B/Y | 3.67 | 2.38 | 3.29 |
| K/Y | 4.29 | 4.02 | 4.24 |
| p_tilde·C/Y | 0.510 | 0.471 | 0.496 |

## solved relative prices

Source: references/alignment.md, section "Reaching the steady state"
PHL prices span 0.4–3.3.

## zeta_K placeholder fix, shipped value

Source: og-solver-diagnosis/references/failure-taxonomy.md, section "B. Binding constraint from a calibration placeholder"
OG-IDN hit and fixed the 0.9; OG-PHL fixed it later (it now ships 0.4); its older logs show the guard firing.

## GS PIT parameters

Source: og-country-calibration/references/taxes-informality.md, section "Progressive-fit recipe (GS and HSV)"
PHL `[0.35, 1.196, 1.9e-8]` → PIT 3.12% of GDP.

## wealth-tax rate for property-type taxes

Source: og-country-calibration/references/taxes-informality.md, section "Capturing non-tax and residual-tax revenue"
PHL: `p_wealth = 0.0035` gives 1.32% of GDP.

## public-investment share

Source: og-country-calibration/references/fiscal-consistency.md, section "The budget identity (with pensions and UBI)"
Forgetting `alpha_I ≈ 0.05` mis-sets `alpha_G` by 5pp of GDP. **[PHL]**

## actual primary balance vs pb*

Source: og-country-calibration/references/fiscal-consistency.md, section "The budget identity (with pensions and UBI)"
(PHL: actual pb −2.8% vs `pb*` −0.7%, so ~2pp embedded consolidation.)

## debt undershoot under a flat alpha_G

Source: og-country-calibration/references/fiscal-consistency.md, section "The alpha_G glide"
(PHL: down to ~48% vs a 58–61% program band)
