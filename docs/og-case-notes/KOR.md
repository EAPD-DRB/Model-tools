# Republic of Korea (KOR): case notes for the OG skills

Country-specific results behind lessons in the OG skills (og-country-calibration,
og-multi-industry-calibration, og-solver-diagnosis, og-run). The skills teach the method; these
are one country's numbers, kept here so the skills stay general. They record what was true when
written; check the country repo before relying on any of them. Do not copy them into another
country's calibration.

## wealth by age, solved vs survey, and chi_b sweep

Source: og-country-calibration/references/validation-dashboard.md, section "Moments most often tuned for but never scored"
Wealth by age **[KOR]**: the solved profile had 60+ at 1.86× the 50-59 level
against 0.97 in the survey, and under-30s at 0.02 against 0.2-0.3. `chi_b` moves the old end
(1.86 at 80, 1.60 at 20, 1.26 at 5) but also `K/Y` (4.31, 3.71, 3.47) and bequest revenue, so
re-tune `beta` and `tau_bq` with it. The young end is leveraged housing, which OG-Core does not
model; document it rather than tune for it.

## trade surplus with positive NIIP

Source: og-country-calibration/references/validation-dashboard.md, section "Two traps when adding rows"
(KOR: data `NX/Y` +5.5% with NIIP +47%; model steady state −3.1%, accounting for 8.5
of an 11-point `C/Y` gap.) **[KOR]**

## NTA age-shape port and profile

Source: og-country-calibration/references/households-demographics.md, section "Earnings (the e ability matrix)"
It ported to KOR by changing the country name and year windows; KOR's profile (2019, against US
2011) peaks at 47 and falls to 0.60 of the US shape by 65, the "honorary retirement" and
mandatory-retirement-at-60 signature. **[KOR]**

## last usable demographic data year

Source: og-country-calibration/references/households-demographics.md, section "The data window sets the long-run growth rate"
The archive's last year can be earlier than the API's (it ended at 2099 for KOR, so 2098 was the
limit while ogcore's assert allows 2099).

## diagnosing the final-data-year break

Source: og-country-calibration/references/households-demographics.md, section "Discontinuities: the frozen window and fixper"
It is not mortality improvement stopping (the first guess on KOR).

## resource-constraint error by break, before and after the local fixes

Source: og-country-calibration/references/households-demographics.md, section "Discontinuities: the frozen window and fixper"
Together on KOR they cut the largest resource-constraint error from 9.1e-3 to 1.2e-4 (2.0e-3 →
1.9e-6 at the data year, 9.1e-3 → 6.8e-7 at 120); what is left is the last five periods.

## RC_TPI triage table by period

Source: og-country-calibration/references/households-demographics.md, section "Discontinuities: the frozen window and fixper"
Triage by period before accepting it: KOR's baseline had 0.009 at period 120 and 0.002 at period 74,
1.9e-4 at the last period, and at most 2.2e-6 everywhere else (3.6e-7 in the first ten years). Keep
the loosened tolerance only with that table in the docs. **[KOR]**

## pension spending, t=0 and steady state

Source: og-country-calibration/references/households-demographics.md, section "Pensions"
The t=0 figure can land on either side of today's: KOR's was 2.65% of GDP against 3.1% (steady
state 5.6%, with NPS benefits alone projected to rise from 1.7% toward ~9% by 2080); the reason it
landed below was not investigated. **[KOR]**

## government financial assets

Source: og-country-calibration/references/macro-open-economy.md, section "Debt (initial_debt_ratio, debt_ratio_ss)"
KOR: general government net financial assets +51% of GDP, the pension fund alone 54%.

## sign check fails at the data's own K/Y

Source: og-country-calibration/references/macro-open-economy.md, section "world_int_rate_annual"
KOR: private `K/Y` 4.31 gives `r` 3.97% against a 4.0% world rate; gross IIP target +8.4%, model −0.9% to −3.3% for `zeta_K` 0.17–0.5; a positive share would need a world rate near 3.7% that no source supports.

## OG-Core#1250 and #1189 on an old population

Source: og-country-calibration/references/macro-open-economy.md, section "Initial household wealth"
With KOR's capital-side target 4.43 and the default shape, its in-loop rescaling oscillated for ten damped iterations without decaying (1.47 … 0.64 … 1.55 … 1.10) where the same calibration without it converged steadily. PR #1189 (a static anchor on steady-state GDP, set before the solve; reforms inherit the baseline's B(0)) converged normally and delivered 4.39. Neither removed KOR's early consumption spike, because initial wealth was not its cause: a third of the households alive in the first year had not been solved at all (PSLmodels/OG-Core#1247; og-solver-diagnosis, class M). With the solve fixed, C/Y ran 50.4, 50.5, 50.7% in the first three years under the default initial condition, against 48.6, 62.9, 53.3% before.

## default rescale vs data target

Source: og-country-calibration/references/macro-open-economy.md, section "Initial household wealth"
On KOR the two differ by that factor, 1.53: B(0)/Y(0) is 2.72 with each household at its steady-state wealth and 4.17 rescaled, against a data target of 4.43.

## private vs total K/Y and delta

Source: og-country-calibration/references/macro-open-economy.md, section "delta_annual"
KOR: 5.13 total vs 4.36 private; `delta` 4.35% → 4.75%; at 5.13 the implied `r` was 3.1%, below the 4.0% world rate.

## gross K_f/K targets (also JPN)

Source: og-country-calibration/references/macro-open-economy.md, section "K_f gross vs net"
KOR: 7.1% on total PWT capital, 8.4% on private. Japan end-2024: (34.5 + 334.8) / 609 / 3.70 = +16.4%, against the 1.5% a placeholder `zeta_K = 0.10` produced.

## example reform chosen for the new port

Source: skills/og-country-calibration/SKILL.md, section "De-siblinging a bootstrap copy"
(KOR: the enacted 2026 corporate-rate rise instead of PHL's CIT cut and debt change).

## Anderson stall just above mindist_TPI, distance series and damped fallback

Source: og-solver-diagnosis/references/failure-taxonomy.md, section "C. Oscillation / slow outer-loop convergence"
Signature: the distance falls cleanly to a few times the tolerance, then rises for several iterations in a row (KOR: 2.7e-5 at iteration 18, then 3.2, 3.9, 4.4, 4.7, 4.9e-5 against 1e-5). Damped iteration (`TPI_outer_method="picard"`, `nu` 0.2) from the same calibration went through the same level and converged (9.7e-6 at iteration 55, about 28 minutes at ~30 s an iteration on a loaded 10-core machine).

## unsolved start cohorts, extent

Source: og-solver-diagnosis/references/failure-taxonomy.md, section "M. Unsolved start cohorts (households alive in the first year)"
On KOR a third of the start cohorts failed, with first-order errors up to 7.0, and consumption jumped to 62.9% of GDP in year two (50.5% once solved).

## pension-driven surplus under a flat alpha_G

Source: og-country-calibration/references/fiscal-consistency.md, section "The alpha_G glide"
(KOR, an ageing country with a maturing pension system: pensions 2.7% of
GDP in 2025 rising toward 5.6%, pb +1% to +1.7% a year, debt 49.6% → 35.7% by 2036 against a plan
near 52%).
