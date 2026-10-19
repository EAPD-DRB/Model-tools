# Japan (JPN): case notes for the OG skills

Country-specific results behind lessons in the OG skills (og-country-calibration,
og-multi-industry-calibration, og-solver-diagnosis, og-run). The skills teach the method; these
are one country's numbers, kept here so the skills stay general. They record what was true when
written; check the country repo before relying on any of them. Do not copy them into another
country's calibration.

## first-transition-year consumption miss

Source: og-country-calibration/references/validation-dashboard.md, section "Completeness: an unscored moment cannot pull its parameter"
(OG-JPN's consumption share in 2025, from a mis-set initial wealth). **[JPN]**

## solved labour share

Source: og-country-calibration/references/validation-dashboard.md, section "Moments most often tuned for but never scored"
`w·L/Y` (solved labour share) against PWT `labsh`: JPN solved 0.5700 against 0.571, a real free check, since nothing forces it when `epsilon != 1`.

## current account vs trade balance

Source: og-country-calibration/references/validation-dashboard.md, section "Two traps when adding rows"
Japan's CA surplus is ~3.8% of GDP against a goods-and-services balance near zero, so a model
`NX/Y` of 0.000 is right, and scoring it against 3.8% would be a concept error.

## "family trait" K/Y miss

Source: og-country-calibration/references/validation-dashboard.md, section "Know the family traits before fixing them"
JPN's "family trait" `K/Y` miss was an untuned `zeta_K`.

## g_y per hour

Source: og-country-calibration/references/macro-open-economy.md, section "g_y_annual"
JPN 2000–2019: +0.557%/yr per worker, −0.472%/yr hours, +1.035%/yr per hour.

## alpha_T cash share

Source: og-country-calibration/references/macro-open-economy.md, section "alpha_T"
JPN shipped 0.075 against a true cash ~0.025: three times too high, the largest single error in its consumption fit.

## gross K_f/K targets (also KOR)

Source: og-country-calibration/references/macro-open-economy.md, section "K_f gross vs net"
KOR: 7.1% on total PWT capital, 8.4% on private. Japan end-2024: (34.5 + 334.8) / 609 / 3.70 = +16.4%, against the 1.5% a placeholder `zeta_K = 0.10` produced.

## net IIP and foreign portfolio

Source: og-country-calibration/references/macro-open-economy.md, section "K_f gross vs net"
Japan's net IIP is +¥533tn, 87.5% of GDP; on the net reading the target is −23.7%, the opposite sign.
For Japan, ¥1,659tn of assets and roughly 3.8% of GDP a year of income.

## K/Y level, target and the beta that failed

Source: skills/og-country-calibration/SKILL.md, section "Finding every lever on a moment"
The failure this prevents: OG-JPN's `K/Y` came in at 3.50 against a PWT 3.70. `beta` needed 0.984,
and at 0.984 the steady state stopped solving.

## zeta_K where the world rate mattered

Source: og-country-calibration/SKILL.md, section "Finding every lever on a moment"
`world_int_rate` (default 0.04) was invisible at the placeholder `zeta_K = 0.10` and set `r` at the IIP-tuned `zeta_K = 0.78`.

## solved savings level against the default seed

Source: og-solver-diagnosis/references/solve-procedures.md, section "Warm-starting the steady state"
The bequest seed lands two orders of magnitude low (JPN: 134× in aggregate, 349× for the top income group, against solved savings of ~6.1 vs the seed's 0.07).

## steady-state factor level

Source: og-solver-diagnosis/references/solve-procedures.md, section "Warm-starting the steady state"
`initial_guess_factor_SS` is validated to a maximum of 500,000, while a low-unit currency needs far more (JPN ~7e6, IDN worse), so the right seed cannot be entered as a parameter.

## initial_debt_ratio error

Source: og-country-calibration/references/fiscal-consistency.md, section "Validation priority: the near-term fiscal path first"
JPN shipped `initial_debt_ratio = 0.864` against an actual 1.148, a 28pp-of-GDP error, for a full day,
in a file whose own `r_gov` derivation used the correct 114.8%. The steady-state dashboard could
not catch it; a debt-path panel would have shown it in period one. **[net-new: JPN]**
