# Ethiopia (ETH): lessons behind the OG skills

What happened behind lessons in the OG skills (og-country-calibration,
og-multi-industry-calibration, og-solver-diagnosis, og-run). The skills teach the method; these
are one country's numbers, kept here so the skills stay general. They record what was true when
written; check the country repo before relying on any of them. Do not copy them into another
country's calibration.

## og-country-calibration/SKILL.md

### The mental model: judge the joint steady state, fiscal rows first

- **Lesson:** most parameters are weakly identified alone, so the test is whether the joint steady
  state resembles the economy, and the dashboard should lead with fiscal data.
- **What happened:** OG-ETH's macro chapter says the parameters are "only weakly identified from
  the data on their own" and compares the solved steady state and program-year paths with
  Ethiopian data. The table leads with fiscal rows: `D/Y` 0.505 against 50.5% (FY2024/25), external
  debt, `r_gov`, `T/Y` 0.093 against 7.8%, PIT/Y 1.36% against 1.4%, then `G/Y`, `TR/Y`, pensions
  and `I_g/Y`, all sourced to IMF Country Report 26/174. Production and price rows (`K/Y`, `C/Y`,
  `r`) come after.
- **Evidence:** table added in
  https://github.com/EAPD-DRB/OG-ETH/commit/15f424f3fd2eca22e144c1b36c5f8b82e5c0defc, merged in
  https://github.com/EAPD-DRB/OG-ETH/pull/70; current text at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/docs/book/content/calibration/macro.md
- **When:** 2026-07 (written), 2026-09 (merged, OG-ETH 0.3.0); checked at upstream/main 49ec411.

## og-country-calibration/references/macro-open-economy.md

### Initial household wealth: the balance-sheet ratio and the capital-side number

- **Lesson:** prefer the capital-side measure of initial wealth, cross-check it against household
  balance sheets, and write down which you used.
- **What happened:** the earlier entry said OG-Core's own documentation tabulates balance-sheet
  ratios, with ETH at 1.70 (PHL 2.50, ZAF 2.56). That table was not found. What OG-ETH ships is the
  capital-side number: PWT `K/Y` about 2.2, less the inward FDI stock of about 0.24 of GDP
  (UNCTAD), plus domestically held public debt of 18.7% of GDP, giving 2.15 against a steady-state
  wealth ratio near 3.1. It lives in `ogeth.macro_params.INITIAL_WEALTH_RATIO` and needs
  PSLmodels/OG-Core#1189 (`initial_wealth_ratio`, still open).
- **Evidence:** 2.15 anchor in
  https://github.com/EAPD-DRB/OG-ETH/commit/55c2d1331a7e1cebf4e3a30d686328468c68ac58 (merged in
  https://github.com/EAPD-DRB/OG-ETH/pull/70); macro chapter at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/docs/book/content/calibration/macro.md;
  https://github.com/PSLmodels/OG-Core/pull/1189. For the 1.70 figure: not found (searched: OG-Core
  docs on upstream/master 81f4549 and all local branches, the PR #1189 diff, GitHub code search on
  PSLmodels/OG-Core, OG-ETH docs).
- **When:** 2026-09 (OG-ETH anchor).

### Capital share (gamma): triangulate the labour share for an informal economy

- **Lesson:** in an agrarian or informal economy, adjust the labour share up using non-circular
  evidence and state `gamma` as a range with a centre.
- **What happened:** ILOSTAT's labour share for Ethiopia is 0.385 (2025), which implies a total
  capital share of 0.615. OG-ETH rejects it on three lines: `gamma = (r+δ)(K/Y)` with PWT `K/Y`
  about 2.2 would need an 18% real return; Gollin (2002) puts fuller adjustments at 0.65 to 0.80;
  and all land is state-owned, so imputed land rent inflates measured capital income. It adopts a
  labour share of 0.60, so `gamma` 0.30 after `gamma_g` 0.10, with a range of 0.25 to 0.35.
- **Evidence:** firms chapter, section "Calibrating the capital share", at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/docs/book/content/calibration/firms.md;
  added in https://github.com/EAPD-DRB/OG-ETH/commit/15f424f3fd2eca22e144c1b36c5f8b82e5c0defc
  (https://github.com/EAPD-DRB/OG-ETH/pull/70).
- **When:** 2026-07 (written), 2026-09 (merged).

### Capital share (gamma): the live path clobbers the triangulated value

- **Lesson:** the `update_from_api=True` path recomputes the naive `1 − ILOSTAT` and silently
  overwrites a hand-triangulated `gamma`; take curated parameters off the live path entirely.
- **What happened:** `get_macro_params` still sets `gamma = 1 − labour share − GAMMA_G_LIC` from
  ILOSTAT when online, so it overwrites the shipped 0.30 with 0.515 (the firms chapter names 0.515
  as the ILOSTAT-implied value). PR #63 restricted the live pull but kept `gamma` on it, and
  refreshed the shipped value from it (0.51791 → 0.5169). Days later the triangulation set 0.30,
  and the live pull stayed. The macro chapter still lists `gamma` as a live parameter.
  The shipped `run_og_eth.py` passes `update_from_api=False`, but `run_og_eth_multi_industry.py`
  and `eth_imm_change.py` pass `True`. OG-IDN took `gamma` off the live path in its PR #55.
- **Evidence:** `ogeth/macro_params.py` at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/ogeth/macro_params.py;
  https://github.com/EAPD-DRB/OG-ETH/pull/63; https://github.com/EAPD-DRB/OG-IDN/pull/55.
- **When:** 2026-07 (PR #63 merged 2026-07-03); still true at upstream/main 49ec411 (2026-10-19).

## og-country-calibration/references/taxes-informality.md

### Standing check: the bequest tax: ETH ships 0

- **Lesson:** compute `tau_bq` from collections over model bequest flows, and grep every port for
  it.
- **What happened:** the first OG-ETH commit shipped `tau_bq = 0.2`, the OG-ZAF value. PR #3 set
  it to 0.0 a month later, and the taxes chapter says wealth and bequest taxes are zero in the
  default calibration. upstream/main still ships 0.0. Zero was set by statement, not derived from
  collections.
- **Evidence:** 0.2 in https://github.com/EAPD-DRB/OG-ETH/commit/97dbf24f04bd7423a33a84a994ceb1700b653b75;
  0.0 in https://github.com/EAPD-DRB/OG-ETH/commit/2a3124561fe3a5496964f6fa945ffb8f2f688ca2
  (https://github.com/EAPD-DRB/OG-ETH/pull/3); current JSON at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/ogeth/ogeth_default_parameters.json
- **When:** 2025-10 (0.2), 2025-11 (0.0); checked at upstream/main 49ec411 on 2026-10-19.

### Informality: the maturity ladder: graded household non-compliance ("Option A")

- **Lesson:** where data allow, grade income-tax non-compliance by lifetime-income group, keep
  every group a filer, and anchor the level to revenue.
- **What happened:** about 85% of Ethiopian employment is informal (ILO 2021). An exploration
  branch assessed three options and completed "Option A": the bottom five of seven groups (90% of
  households) remit no income tax, with a statutory 35% top MTR and the compliant-group ETR from a
  revenue identity. It landed on main in July 2026 with labour and capital non-compliance equal
  and `income_tax_filer` all ones. On main at 49ec411 the form has since moved on: the statutory GS
  schedule with the compliance shape [0, 0, 0, 0, 0, 0.5, 1] times a calibrated
  `COMPLIANCE_SCALE` (0.198381), so PIT collects 1.4% of GDP.
- **Evidence:** assessment at
  https://github.com/marcelolafleur/OG-ETH/blob/356673faefe0e072abf5d5f7cb45b66bf0803930/INFORMALITY.md
  and status commit https://github.com/marcelolafleur/OG-ETH/commit/ce8a230f10c66afa2f7af6da27cf4914cfa47897;
  main change https://github.com/EAPD-DRB/OG-ETH/commit/a991f6e6baff07e10ea890d83b9385f100001cba
  (https://github.com/EAPD-DRB/OG-ETH/pull/70); current taxes chapter at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/docs/book/content/calibration/taxes.md
- **When:** 2026-07 (Option A, ogcore 0.16.3); current form checked at 49ec411 on 2026-10-19.

## og-country-calibration/references/households-demographics.md

### Earnings (the e ability matrix): ETH used the Gini tilt, then replaced it

- **Lesson:** the family reuses OG-USA's `e` matrix with a single-scalar exponential tilt to the
  country's Gini.
- **What happened:** OG-ETH used the tilt, `get_e_interp(gini_to_match=31.1)`, until September
  2026. PR #70 replaced it: the OG-USA matrix is reshaped over age with the NTA labour-income
  profile (Ethiopia 2005 against the US 2006) and across groups with WID pre-tax income shares
  (2021). The commit says this fixes the consumption-Gini against income-Gini mismatch of issue
  #33. A Gini tilt remains as an option (`tilt_to_gini`). So ETH no longer ships the family method;
  it ships both halves described in EAPD-DRB/OG-ZAF#18.
- **Evidence:** https://github.com/EAPD-DRB/OG-ETH/commit/5a39a86c9486c3ab4c3599f6bbf27fa3134c739e
  (https://github.com/EAPD-DRB/OG-ETH/pull/70); https://github.com/EAPD-DRB/OG-ETH/issues/33
  (still open).
- **When:** tilt until 2026-09; replaced in 0.3.0 (merged 2026-09-26).

### Demographics: method and country_id: the wrong literal, twice

- **Lesson:** use one named `country_id` constant and add a test that it matches the country.
- **What happened:** the first `calibrate.py` passed `country_id="710"` (South Africa) instead of
  "231" (Ethiopia). PR #3 fixed it. In April 2026 a rewrite of `calibrate.py` in PR #22 brought 710
  back at both call sites. PR #49 fixed it again; its author called 710 "a leftover from the OG-ZAF
  lineage". PR #70 then added `UN_COUNTRY_CODE = "231"` and a test. The test checks the call
  against the constant, not against "231", so a wrong constant would still pass.
- **Evidence:** https://github.com/EAPD-DRB/OG-ETH/commit/97dbf24f04bd7423a33a84a994ceb1700b653b75
  (710); https://github.com/EAPD-DRB/OG-ETH/commit/ebb1a3704d912c34d096484a4b75f1d61964b6cd
  (fix, https://github.com/EAPD-DRB/OG-ETH/pull/3);
  https://github.com/EAPD-DRB/OG-ETH/commit/9be21bb5f81f9f53d4fe4bb912e328d0a120403f (710 again,
  https://github.com/EAPD-DRB/OG-ETH/pull/22);
  https://github.com/EAPD-DRB/OG-ETH/commit/719ec9186965b56bf7ce0f7b06faf99ec307552e (fix,
  https://github.com/EAPD-DRB/OG-ETH/pull/49; an earlier attempt,
  https://github.com/EAPD-DRB/OG-ETH/pull/46, was closed);
  https://github.com/EAPD-DRB/OG-ETH/commit/285fb03f3676f8a2204e1ce0c880226f4583a8ab (constant and
  test in `tests/test_demographic_gradients.py`).
- **When:** 2025-10 and 2026-04 (regressions); 2025-11 and 2026-06 (fixes); 2026-09 (constant).

### Pensions: the factor seed sits exactly at the validator cap

- **Lesson:** check that the factor seed sits in the validator range; a seed of exactly 500,000
  was probably clipped to the cap, so compare it with the solved `factor`.
- **What happened:** OG-ETH upstream/main ships `initial_guess_factor_SS` exactly 500,000.0, with
  `mean_income_data` 353,049.55 birr. It is clipped by design: `ogeth.labor.factor_guess` returns
  `min(solved factor, 500000)`, citing OG-Core's cap. So the solved factor was at least 500,000; the
  repo does not record its value. The seed was 322,971 before the September 2026 earnings and
  `chi_n` recalibration. OG-Core validates the seed to at most 500,000.
- **Evidence:** JSON at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/ogeth/ogeth_default_parameters.json;
  `factor_guess` at
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/ogeth/labor.py;
  seed change https://github.com/EAPD-DRB/OG-ETH/commit/5a39a86c9486c3ab4c3599f6bbf27fa3134c739e;
  cap at
  https://github.com/PSLmodels/OG-Core/blob/81f45496b9aec37bc82dc22aeebba31f055ca5e2/ogcore/default_parameters.json.
  Solved factor value: not found (searched: OG-ETH docs, CHANGELOG, PR #70 body, code).
- **When:** 2026-09 (seed set); checked at upstream/main 49ec411 on 2026-10-19; cap checked on
  OG-Core master 81f4549 (v0.21.2).

## og-country-calibration/references/validation-dashboard.md

### The steady-state dashboard: a data-comparison table in macro.md

- **Lesson:** put a table in `macro.md` comparing the solved steady state with data targets, each
  with a source, tiered fiscal first.
- **What happened:** OG-ETH's macro chapter has a 20-row table with a data-source column, for the
  history-anchored baseline and the program scenario. Rows include `D/Y`, external debt, `r_gov`,
  `T/Y`, PIT/Y, `G/Y`, `TR/Y`, pensions, `I_g/Y`, `RM/Y`, `K_f/Y`, `K/Y`, `B/Y`, `(I+I_g)/Y`, `C/Y`,
  `CA/Y`, `NX/Y`, factor payments and `r`. It records misses too: `NX/Y` −4.1 to −4.5% against −8.3
  to −9.9%, explained by factor payments abroad of 5.8% of GDP against about 1%.
- **Evidence:** https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/docs/book/content/calibration/macro.md;
  https://github.com/EAPD-DRB/OG-ETH/pull/70.
- **When:** 2026-07 (written), 2026-09 (merged).

### Fast value-pinning test: test_default_parameters.py

- **Lesson:** a fast test loads the shipped JSON and pins calibrated values with sources, asserting
  nothing that needs a solve.
- **What happened:** OG-ETH added `tests/test_default_parameters.py` with the informality
  calibration. It pins the statutory tax functions, non-compliance by group, the CIT collections
  factor, all-filers and array shapes, cites IMF SIP 2025/108, IMF CR 26/20 and ILO 2021, and says
  the revenue split "requires a model solve and is therefore intentionally NOT asserted here". Its
  docstring still describes the July form (ETR 0.0871 from a revenue identity), which main has
  since replaced.
- **Evidence:** https://github.com/EAPD-DRB/OG-ETH/commit/a991f6e6baff07e10ea890d83b9385f100001cba;
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/tests/test_default_parameters.py
- **When:** 2026-07 (added); checked at 49ec411.

### Prevent doc/JSON drift with glue: the taxes chapter

- **Lesson:** a hidden docs cell loads the packaged JSON and `glue()`s the numbers so prose cannot
  drift.
- **What happened:** issue #40 asked that the docs reflect current calibration values. PR #42
  made the taxes chapter read rates such as `tau_payroll` and `cit_rate` from
  `ogeth_default_parameters.json` through `myst_nb.glue`, and closed the issue. Only the taxes
  chapter uses it at 49ec411.
- **Evidence:** https://github.com/EAPD-DRB/OG-ETH/issues/40;
  https://github.com/EAPD-DRB/OG-ETH/pull/42;
  https://github.com/EAPD-DRB/OG-ETH/commit/159315fba05a8b7c364a96ca8f315c54b22cbe7f
- **When:** 2026-05.

## og-solver-diagnosis/references/solve-procedures.md

### Running against an unreleased ogcore: ETH's main pins ogcore by commit

- **Lesson:** to run on an unreleased ogcore, keep the official installer and pin ogcore by commit
  in `[tool.uv.sources]`.
- **What happened:** OG-ETH 0.3.0 needs two OG-Core changes its PR calls unreleased,
  `initial_wealth_ratio` (PSLmodels/OG-Core#1189, still open) and `r_gov_floor` (#1203, since
  merged). Its `pyproject.toml` pins ogcore to
  `marcelolafleur/OG-Core` at `edaa78ab`, a master-plus-#1189 build, while the PyPI metadata keeps
  `ogcore>=0.20.0`. On a released OG-Core the example falls back and says so. The skill
  recommends keeping such a pin off the calibration branch; ETH's main carries it.
- **Evidence:** https://github.com/EAPD-DRB/OG-ETH/commit/e9284552f311f4393a4412f6101681eb22fb5c94;
  https://github.com/EAPD-DRB/OG-ETH/blob/49ec411ab7e6fe36938d402b5280aa2e84084516/pyproject.toml;
  https://github.com/EAPD-DRB/OG-ETH/pull/70.
- **When:** 2026-09.
