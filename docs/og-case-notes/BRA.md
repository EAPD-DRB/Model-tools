# Brazil (BRA): case notes for the OG skills

Country-specific results behind lessons in the OG skills (og-country-calibration,
og-multi-industry-calibration, og-solver-diagnosis, og-run). The skills teach the method; these
are one country's numbers, kept here so the skills stay general. They record what was true when
written; check the country repo before relying on any of them. Do not copy them into another
country's calibration.

## industry count after folding real estate

Source: references/inputs.md, section "Defining industries and goods"
An earlier BRA draft kept real estate separate at M=10 and was merged down to M=9.

## utility industries

Source: references/inputs.md, section "Defining industries and goods"
BRA: electricity_gas, which also carries piped gas, and water_waste.

## goods

Source: references/inputs.md, section "Defining industries and goods"
BRA I=7 with electricity, water and fuels separate.

## mixed-income split

Source: references/inputs.md, section "gamma_m"
(BRA, phi = 0.428.)

## gamma rescale target

Source: references/inputs.md, section "gamma_m"
BRA's target is the table's own share (0.428) while its single model uses an ILO-based 0.407, a gap
that has to be closed one way or the other.

## capital-output ratio

Source: references/inputs.md, section "Z_m"
The capital-output ratio from PWT for the SAM year: BRA 4.36.

## Z ranking

Source: references/inputs.md, section "Z_m"
Mining and utilities high in BRA.

## per-good tau_c

Source: references/inputs.md, section "Tax rates by industry and good"
Energy goods come out high (BRA electricity 0.34, fuels 0.29), services low.

## base CIT factors

Source: references/inputs.md, section "Tax rates by industry and good"
BRA: average rate about 9%, times 0.7 × 0.3 (`c_corp_share_of_assets` ×
`adjustment_factor_for_cit_receipts`), gives about 2%, against about 7% in the single model.

## public capital stock

Source: references/inputs.md, section "Public capital"
BRA sets them in the overlay from IMF PIMA (Kg/Y 0.35).

## solved relative prices

Source: references/alignment.md, section "Reaching the steady state"
BRA prices span 0.13–2.09.

## labour allocation against the table

Source: references/alignment.md, section "Checking the solved model"
BRA also checks how well the model's labour allocation tracks the table's labour income by industry
(correlation 0.86).
