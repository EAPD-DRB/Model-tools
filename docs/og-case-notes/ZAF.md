# South Africa (ZAF): case notes for the OG skills

Country-specific results behind lessons in the OG skills (og-country-calibration,
og-multi-industry-calibration, og-solver-diagnosis, og-run). The skills teach the method; these
are one country's numbers, kept here so the skills stay general. They record what was true when
written; check the country repo before relying on any of them. Do not copy them into another
country's calibration.

## g_y consistent with the debt anchor

Source: og-country-calibration/references/macro-open-economy.md, section "g_y_annual"
ZAF: the realized 0.6% was inconsistent with the 0.765 anchor's ~1.8% growth, so `g_y` rose to ~1.4% (= 1.8% − `g_n` 0.42%).

## effective r_gov levels (also PHL)

Source: og-country-calibration/references/macro-open-economy.md, section "r_gov base wedge (r_gov_scale, r_gov_shift)"
It over-predicted ZAF by ~0.5–0.6pp and PHL by ~3pp (5.1% vs the ~2.0% the Treasury pays).
Exemplar. ZAF (~3.7%), PHL (~2.0%).

## household balance-sheet wealth ratios (also PHL, ETH)

Source: og-country-calibration/references/macro-open-economy.md, section "Initial household wealth"
OG-Core's own documentation tabulates these, e.g. PHL 2.50, ZAF 2.56, ETH 1.70.

## make-matrix structure

Source: references/inputs.md, section "Finding the data"
ZAF's median commodity has more than one producer (rectangular make). PHL's off-diagonal share is
exactly 0 (diagonal make).

## employment survey year

Source: references/inputs.md, section "Finding the data"
ZAF uses QLFS 2019.

## SAM vintage checked against the national accounts

Source: references/inputs.md, section "Finding the data"
ZAF's 2019 SAM matched Stats SA to about 0.5pp on primary, secondary and tertiary.

## utility industries

Source: references/inputs.md, section "Defining industries and goods"
ZAF: Electricity and Water & Waste.

## goods

Source: references/inputs.md, section "Defining industries and goods"
ZAF I=5 (food, energy, non-durables, durables, services).

## traced household energy row

Source: references/inputs.md, section "io_matrix"
Traced, household energy goes to electricity (45% in ZAF, against a manufacturing-heavy naive
split).

## capital-output ratio

Source: references/inputs.md, section "Z_m"
The capital-output ratio from PWT for the SAM year: ZAF 2.9.

## Z-level multiplier

Source: references/alignment.md, section "The Z level"
ZAF 23% off, fixed by a common Z multiplier of 0.865 found by a log-log root-find on the solved
`factor` (two or three solves, slope about 1.8).

## gamma_g is zero

Source: skills/og-country-calibration/references/calibration-pr.md, section "Pre-empt the gamma_g question"
If `gamma_g = 0` (e.g. ZAF), say so (private = total, no carve-out) so the reviewer need not raise it.

## GS PIT parameters

Source: og-country-calibration/references/taxes-informality.md, section "Progressive-fit recipe (GS and HSV)"
Examples: ZAF `[0.464, 1.39288, 1.43e-8]` → PIT 10.1% of GDP, top MTR 45%.

## HSV PIT fit

Source: og-country-calibration/references/taxes-informality.md, section "Progressive-fit recipe (GS and HSV)"
(ZAF's HSV fit had τ ≈ 0.14 tracking SARS, before the GS switch.)

## Open question: GS top rate in the PIT example

Raised during the 2026-10-19 generalisation pass, not checked. The GS example
`[0.464, 1.39288, 1.43e-8]` reports a top marginal rate of 45%, while the skill's recipe sets `φ0`
to the statutory top rate. Either the example or the recipe is off; check OG-ZAF's packaged values.
