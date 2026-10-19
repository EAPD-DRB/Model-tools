# Ethiopia (ETH): case notes for the OG skills

Country-specific results behind lessons in the OG skills (og-country-calibration,
og-multi-industry-calibration, og-solver-diagnosis, og-run). The skills teach the method; these
are one country's numbers, kept here so the skills stay general. They record what was true when
written; check the country repo before relying on any of them. Do not copy them into another
country's calibration.

## wrong country_id literal

Source: og-country-calibration/references/households-demographics.md, section "Demographics: method and country_id"
The hard-coded `country_id` literal was wrong (710 = South Africa instead of 231 = Ethiopia), twice,
because a wholesale file copy forgot to swap it.

## household balance-sheet wealth ratios (also PHL, ZAF)

Source: og-country-calibration/references/macro-open-economy.md, section "Initial household wealth"
OG-Core's own documentation tabulates these, e.g. PHL 2.50, ZAF 2.56, ETH 1.70.

## gamma clobbered by the live path

Source: og-country-calibration/references/macro-open-economy.md, section "Capital share (gamma)"
The `update_from_api=True` path ... silently clobbers a hand-triangulated `gamma` (e.g. overwrites 0.30 with 0.515).
