---
name: og-country-calibration
description: >-
  Calibrates, updates or reviews an OG-Core overlapping-generations country model (OG-USA, PHL,
  ZAF, IDN, BRA, ETH or a new country). Use when setting or checking macro and open-economy
  parameters, gamma, the earnings matrix, demographics, preferences, pensions, initial wealth,
  taxes or informality; when porting the model to a new country or updating a calibration to new
  data; or when validating a steady state or transition against country data. Multi-industry work
  is og-multi-industry-calibration; launching runs is og-run; a failing solve is
  og-solver-diagnosis.
---

# Calibrating an OG-Core country model

Methods and pitfalls learned across the OG-Core country models, for a new country or an update of
an existing one. Every number here is an example; derive your own. Check each claim against the
repo in front of you and the installed ogcore: parameters appear, get renamed or change shape
between releases.

## Running the model

Install each model with OG-Core's installer, one copy per commit, and run the repo's example script
unchanged from that copy's environment; tuning uses the repo's own tuning script, and tests run in
such a copy. A run outside this path cannot be reproduced or compared, so its numbers do not count.
To investigate, read the saved output; for a quick check, run the example's steady state from the
installed copy. A baseline takes under ten minutes. Report with every result the repo, commit,
ogcore version, script and whether it ran online. Detail: [og-run-rules.md](references/og-run-rules.md).

## How a calibration runs

The person you are working with leads: they decide what the baseline targets, which data sources
to use, which method settles each parameter, and when to stop. Your part is to find the data and
the methods, propose a choice with a recommendation and its evidence, run, check, and report
plainly. The order that works:

1. **Targets.** The baseline is the observed economy in the start year (the latest year with data);
   a fiscal program or a forecast is a scenario run against it. Fix the GDP basis once (for example
   rebased national accounts at market prices) and use it for every ratio.
2. **Inputs, one decision at a time.** For each input, the best available data or published
   method, starting with the national institution that owns the number; log each decision with its
   source and the alternatives considered. Settle every input before tuning.
3. **Tune once.** The dials (tax scales, `zeta_K`, patience) against their own measured moments.
4. **Validate.** The example script, steady state and transition, against the dashboard
   (validation-dashboard.md): fiscal rows first, then the first model year, then the long run.
5. **Document,** with every value generated from code and pinned by a test.
6. **Stop** when the remaining gaps are small or need a model the repo does not have, and say which
   gaps remain and why.

Each block has a ladder from minimal to ideal: use the highest rung the data supports, and when you
take a lower one, say so. A documented fallback is a legitimate calibration; an undocumented
placeholder is not. Updating an existing calibration follows the same order: start from what the
repo ships, list what the new data changes, and re-settle only those inputs before one retune.

## The mental model

1. **The packaged `og<xxx>_default_parameters.json` is the source of truth.** `Calibration(p,
   update_from_api=False)` fetches nothing, but an example may call `update_from_api=True` when
   online and overwrite curated values. Read the example before trusting a hand-set value.
2. **Anything you do not set stays American:** `delta_annual` 0.05, `beta_annual` 0.96,
   `mean_income_data` in US dollars (it scales taxes and pensions), `pension_system` US Social
   Security, `tax_func_type` `DEP`, `cit_rate` 0.21, `p_wealth` 0.0, `zeta_D` 0.4,
   `debt_ratio_ss` 2.0, `c_min` 0, the `initial_guess_*` set. Count what your `Calibration`
   actually delivers. [JPN]
3. **Lead the dashboard with fiscal data.** Collections by instrument, debt, its foreign share and
   the effective rate on debt are published precisely and check each other through the budget
   identity. The foreign capital share `K_f/K` is first-tier too.
4. **Calibrate effective, not statutory, quantities:** rate = actual collections ÷ the model's base,
   for every instrument.
5. **Single-industry first;** multi-industry is an overlay built afterwards.
6. **Find every lever before tuning.** Write the model's own closed form for each target moment and
   list every parameter in it ([method.md](references/method.md)); a lever that runs out of road is
   the wrong lever, not a gap in the model.
7. **Read a binding bound economically first.** A parameter stuck at its bound usually means
   another input is wrong or a mechanism is missing; check units and the economics before asking
   for a wider bound.

## Checklist for a new country

Copy into the work log and tick off. For an update, keep the rows the new data touches.

```
- [ ] Existing work: open PRs and branches touching this block; the current gaps and their sign.
- [ ] Targets and GDP basis agreed; a fiscal-path panel and a steady-state dashboard planned.
- [ ] Moment x lever table from OG-Core's equations (method.md).
- [ ] Bootstrap from the closest sibling repo, then replace every inherited value (bootstrap.md).
- [ ] Install with the installer; note the resolved ogcore; preflight.
- [ ] Demographics: named country code + test; data window to the last usable year; g_n_ss
      against the UN projection; income gradients if available.
- [ ] Earnings: shares or Gini on the same concept as the reference; NTA age shape if available.
- [ ] Macro: start_year, debt (measured start, anchored long run), external debt, zeta_D,
      world rate, g_y per hour, remittances and aid, r_gov to the treasury's effective real rate,
      debt premium centred on the target, public capital, initial wealth, transfers (cash only).
      K/Y and delta on private capital.
- [ ] Capital share from the labour share (adjusted for self-employment) or rent flows; decided
      when sourced, never moved to close a K/Y gap.
- [ ] Taxes: every rate effective (collections / model base), by instrument; close the budget
      identity alpha_G + alpha_T + alpha_I + pensions/Y + UBI/Y = revenue/Y - pb*.
- [ ] Pensions in local currency; chi_n to hours by age.
- [ ] Preferences: sigma, a subsistence floor if relevant, Frisch; then patience.
- [ ] Tune the dials once; validate steady state and transition, including the first-year
      cohorts (og-solver-diagnosis, class M).
- [ ] Ship a warm-start seed from the first converged solve; regenerate after large moves.
- [ ] Final solve of the packaged JSON with no overrides; tests; changelog; docs from the JSON.
```

When a check fails, go back before moving on: after a tax change re-tune `zeta_K`; after a sourced
input changes, redo the tax dials and then patience; if the packaged JSON fails on its own, revisit
the overrides just folded in; if the transition's resource-constraint error is not small and
steady, triage it by period (og-solver-diagnosis) before tuning.

## Reporting

Report in plain language: the baseline is the observed economy, a program is a scenario, and
model-against-data tables use the names in the data. Say what is measured, what is assumed and what
is a check. Keep internal labels (round names, "dials", "official run") out of reports.

## Reference files

Read the one for the block you are working on.

| File | Read when |
|---|---|
| [method.md](references/method.md) | Before tuning: the moment × lever table, finding every lever, why the transition is validated |
| [bootstrap.md](references/bootstrap.md) | Copying a sibling repo for a new country |
| [macro-open-economy.md](references/macro-open-economy.md) | Start year, debt and external debt, `zeta_D`, `zeta_K`, world rate, `g_y`, `r_gov`, remittances and aid, debt premium, public capital, initial wealth, `delta`, `beta`, `gamma` |
| [households-demographics.md](references/households-demographics.md) | Earnings matrix, demographics, preferences (`sigma`, `c_min`, Frisch), pensions, `chi_n` |
| [fiscal-consistency.md](references/fiscal-consistency.md) | Spending shares, the budget identity, a debt path that runs away, the fiscal path panel |
| [taxes-informality.md](references/taxes-informality.md) | Any tax rate, the income-tax form, payroll and bequest checks, informality, non-tax revenue |
| [validation-dashboard.md](references/validation-dashboard.md) | Building or scoring the dashboard, data anchors, reading output, tests that pin values |
| [solving-tuning.md](references/solving-tuning.md) | Environment, troubleshooting a run, the tuning loop and its order |
| [calibration-pr.md](references/calibration-pr.md) | Writing the calibration PR |
| [og-run-rules.md](references/og-run-rules.md) | How to run the model |
| [lessons/INDEX.md](references/lessons/INDEX.md) | Your country has a feature another country has dealt with: the lessons by situation, with each country's case |

Related skills: og-run, og-solver-diagnosis, og-multi-industry-calibration, og-scenario-report
(presenting runs). Where an existing value came from: [provenance.md](references/provenance.md).

## Lessons and tags

A tag such as `[PHL]` records where a lesson was learned, not where it applies; the condition is
stated as a country feature (informal economy, net creditor, concessional debt). `[family]` marks a
practice shared by most repos, `[emerging]` one used in one or two, `[net-new]` one used nowhere
yet. Each country's
cases, with numbers and evidence, are in `references/lessons/<CODE>.md`; start from the index by
situation. When your country teaches something new, add it as `docs/og-skills-maintenance.md` in
Model-tools describes.

## The traps that cost the most

- **The budget does not balance at the debt target:** the transition runs away while the steady
  state looks fine (fiscal-consistency.md).
- **Statutory rates in effective slots:** `tau_bq`, payroll on top of the income-tax function, a
  flat income tax (taxes-informality.md).
- **Placeholder `zeta_K`:** tune it to the measured foreign capital share (macro-open-economy.md).
- **`r_gov` from the cross-country intercept:** anchor it to the treasury's effective real rate.
- **Wrong `initial_debt_ratio`:** invisible in the steady state, obvious in the first year.
- **A consumption spike in the first years:** rule out unsolved first-year cohorts
  (og-solver-diagnosis, class M) before blaming the initial wealth.
- **Short demographic window:** it sets the long-run growth rate silently.
- **Live data overwriting a curated value:** take curated parameters off the live path.
- **Tuning before the inputs are settled:** every later correction costs a retune.
- **Patience at its bound:** usually high curvature with fast growth, or households financing
  investment the state finances; see `beta_annual` and preferences before widening the bound.
- **Remittances or aid left out where they matter:** a spurious trade surplus and a fiscal squeeze.
