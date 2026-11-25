# OG skills evaluation scenarios

Each scenario is answered by a fresh agent that may read only the skills folder it is given and
the scenario's materials. A grader scores each rubric point 1 (clearly present and correct) or 0.
Rubric points are things the skills should teach; they are not in the prompt.

Run every scenario under each variant being compared (for example: no skill, `main`, the branch).
Record the scores in `scores/<date>.md`.

---

## S1. Starting a new country from a sibling

**Prompt.** You are asked to build OG-THA, a Thailand calibration of OG-Core, by copying the
OG-PHL repo. Before any solve, list what you will do, in order, and the inherited values you must
check before trusting them. At most 350 words.

**Rubric.**
1. Search the copied repo for the old country beyond the package rename (ISO and UN codes,
   names), including code paths such as a live-download default.
2. Make the shipped example run offline, or confirm what a live API call would overwrite.
3. Put the UN country code in a named constant and add a regression test for it.
4. Set the start year to the latest year with observed data.
5. Choose the demographic data window deliberately (last usable year; check the long-run growth
   rate against the UN projection).
6. Treat the sibling's solver seeds (`initial_guess_*`) as the sibling's solution, not neutral.
7. Name the run rules: official installer, unchanged example, Anderson with `nu` at most 0.2,
   preflight before a solve.
8. Target private capital: net public capital out of K/Y and depreciation.
9. Set tax rates as effective rates from collections, by instrument (including the bequest tax),
   and close the budget identity with public investment and pensions.
10. Validate with a baseline transition and a fiscal path panel, not only the steady state.

## S2. Auditing an existing calibration

**Materials.** `materials/country_X_parameters.json`: the small parameters of an existing,
published country calibration (arrays over 200 characters removed).

**Prompt.** This is the packaged parameter file of an existing OG-Core country calibration.
Audit it. List the eight most consequential problems you can see or suspect from the file alone,
each with the check or data source that would confirm it. At most 400 words.

**Rubric.**
1. `zeta_K` 0.9 is the known placeholder (drives domestic capital negative); tune it to the IIP
   foreign capital share.
2. `tau_bq` 0.2 is a statutory-style rate; compute it from bequest-tax collections.
3. The PIT is flat/linear (`tax_func_type` linear, ETR 0.22 for everyone); use a progressive form
   (GS) tuned to collections.
4. `nu` 0.4 without Anderson (`TPI_outer_method` unset) breaks the run rules (Anderson, `nu` at
   most 0.2).
5. `delta_annual` 0.05 and/or `beta_annual` 0.96 and/or `world_int_rate` 0.04 are OG-Core's US
   defaults, not sourced for the country.
6. `pension_system` "US-Style Social Security" (with `alpha_db` 0) is the US default; set the
   country's own system.
7. `alpha_I` 0.0003 is a placeholder for public investment; source it (it also enters the budget
   identity).
8. Check `debt_ratio_ss`, `g_y`, `r_gov` and the spending shares together through the budget
   identity (the steady state forces `G`; only the transition shows a runaway).
9. `RC_TPI` / tolerances, `chi_b` 80 or `tau_payroll` 0 flagged as unexamined and needing a reason.

## S3. An early-year consumption spike

**Prompt.** A country model's baseline transition converged: the distance fell below `mindist`
and the reported maximum Euler errors are about 1e-12. But consumption/GDP is 49% in year 1, 63%
in year 2, 53% in year 3, then about 51% for the rest of the path. The households above 1.5 times
their steady-state consumption in year 2 are scattered across ages 56 to 99 and across income
groups in a checkerboard pattern. What is your diagnosis, and what is the first thing you check?
At most 250 words.

**Rubric.**
1. Suspects households alive at t=0 (start cohorts) whose individual solve failed.
2. Notes the reported Euler error does not cover those cohorts, so it cannot rule this out.
3. First check: recompute those cohorts' first-order conditions from the saved path (or compare
   their year-1 choices with the solver's seed).
4. Does not start by changing the initial wealth level or shape (names it as the look-alike).
5. Names the remedy: an ogcore with checked, retried start-cohort solves (PSLmodels/OG-Core#1247).

## S4. Resource-constraint spikes on the transition

**Prompt.** A baseline transition solved. The largest resource-constraint errors are 9e-3 at
period 120 and 2e-3 at period 74, which is the final year of UN data; every other period is below
2e-6 except the last, at 2e-4. The packaged `RC_TPI` is 0.01. What do you conclude, what do you
check, and what do you do? At most 250 words.

**Rubric.**
1. Identifies both as demographic breaks in OG-Core (the final data year, and `fixper` = 1.5S),
   not calibration errors.
2. Check: the stored rates reproduce the stored population path (the law of motion), period by
   period.
3. Does not tune calibration parameters to remove them.
4. `RC_TPI` 0.01 is loosened from OG-Core's 1e-4: keep it only with a per-period table, or tighten.
5. Checks whether the installed ogcore has the fixes, or reports upstream.

## S5. A large net creditor

**Prompt.** The country is a large net creditor: net international investment position +80% of
GDP, a trade surplus of 3% of GDP. How do you set the `K_f/K` target and `zeta_K`, and how do you
score `NX/Y`? At most 250 words.

**Rubric.**
1. Uses the gross reading: inward direct-investment equity plus portfolio equity, over GDP, over
   the model's private K/Y.
2. Notes the net reading gives the opposite sign; OG-Core has one `K_f`, so the foreign asset side
   cannot be represented.
3. States what is omitted (the foreign portfolio and its income) in the docs.
4. `NX` is the trade balance, not the current account.
5. In the steady state a net creditor runs `NX < 0`; compare only signs there and score `NX/Y` in
   the early transition.
6. If `r` sits at or below the world rate, `zeta_K` is not identified by the steady state: set it
   from the openness prior with a reason and report the miss.

## S6. Following a lesson to its history

**Materials.** The skills folder plus the Model-tools `docs/` folder (as in a checkout).

**Prompt.** The skill tells you to compute the bequest tax `tau_bq` from collections rather than
use the statutory rate, and tags the lesson with a country. A reviewer asks: where did this lesson
come from, what happened, and where is the evidence? Answer from the material you have. At most
200 words.

**Rubric.**
1. Finds the country tag and goes to `docs/og-lessons/<CODE>.md`.
2. Finds the matching entry and reports what happened, with its numbers.
3. Gives at least one evidence link or file from the entry.
4. Distinguishes the general rule (in the skill) from the case (in the history).

## S7. Not handing out a country's answers

**Prompt.** You are calibrating the Republic of Korea from scratch. What values do you use for the
last year of the demographic data window and for the initial household wealth-to-GDP target, and
how do you get them? Use the skills only; no data access. At most 200 words.

**Rubric.**
1. Gives the method for the data window (the archive's last year, minus one; check before use)
   rather than asserting a year as the answer.
2. Gives the method for the wealth target (capital side: private K/Y less foreign-owned share plus
   domestically held debt; cross-check with balance sheets) rather than asserting a number.
3. Does not present another country's or a remembered value as the answer.

## S8. A pension scheme still maturing

**Prompt.** A middle-income country's main pension scheme started 25 years ago and is still
maturing: few retirees have full contribution histories. With the legislated replacement rate set
in `alpha_db`, the model's baseline transition pays pensions of 4.8% of GDP in the first year,
against 2.1% actually paid, and debt overshoots the fiscal program. How do you set the pension
block, and how do you score it? At most 250 words.

**Rubric.**
1. Keeps the steady state at the mature, legislated system and scores it against the scheme's
   long-run actuarial projection.
2. Does not lower the constant `alpha_db` to hit today's spending (that understates the legislated
   system).
3. Puts `alpha_db` on a time path rising from today's value to the mature value over the maturing
   period.
4. Scores today's spending at t=0 of the transition.
5. Re-derives the spending glide (`alpha_G`) from the transition's own pension path, and checks the
   debt path against the program afterwards.

## S9. A transition that got slow

**Prompt.** After a recalibration, a country model's baseline transition converges in about 60
iterations, as before, but each iteration now takes about 20 seconds; the whole baseline takes 20
minutes. Solved one at a time, each income group's household problem takes about 4 seconds.
During each iteration one of the seven workers is at 100% CPU while the others are idle for most
of it. Switching the pension system off to test it made the run slower, not faster. What is going
on, and what do you check first? At most 250 words.

**Rubric.**
1. Reads it as one worker holding up each iteration (a straggler), not slower convergence.
2. Does not start by blaming the hardware or the calibration, or by changing solver settings.
3. Check: time each income group's task per iteration, with its residual evaluations or
   Levenberg-Marquardt fallbacks, and see whether the slow task follows one worker.
4. Names state cached on the worker (the household Jacobian's sparsity pattern) as the suspect, or
   dask moving data to the workers, and checks the ogcore version for a fix.
5. Explains why the pension-off test does not clear or convict the pension (it changes which
   worker or pattern is slow, not only the cost).
6. Confirms the cause with an official run (installer copy, shipped example) before reporting it.

## S10. Borrowed labour supply

**Prompt.** A country port ships OG-USA's `chi_n`. Total hours per working-age person in the
country are about 5% above the US. Is the borrowed `chi_n` acceptable? If not, how do you calibrate
it, and what else has to change with it? At most 250 words.

**Rubric.**
1. Compares the model's labour supply by age with hours by age, not only the total.
2. Targets hours per person (employment rate × hours of the employed), not per worker, because the
   model has no extensive margin.
3. Calibrates by re-solving the steady state after each `chi_n` step, warm-started.
4. Handles ages where `chi_n` reaches its upper bound (leaves them out of the fit and reports them).
5. Makes the earnings (`e`) age profile per hour, so hours are not counted twice.

## S11. A first-year consumption windfall

**Prompt.** A country with a young population sets `initial_wealth_ratio` from data. `beta` was
tuned so the steady state matches today's capital-output ratio. The baseline transition solves, but
household consumption is 81% of GDP in the first year against 76% in the data, and investment is 20%
against 24%. The start cohorts were checked and are solved. What is going on, and what do you change?
At most 250 words.

**Rubric.**
1. Explains that a steady state tuned to today's ratio is wrong for a young population: the same
   patience implies more wealth once the population ages, so households start with a windfall.
2. Does not expect the age shape of initial wealth alone to fix it.
3. Tunes `beta` to first-year moments (consumption and investment shares), judged on the
   transition rather than the steady state, and within the long-run bounds: the owners' return on
   capital inside the return evidence and foreign-owned capital non-negative in the steady state.
4. Reports the steady-state `K/Y` as an outcome, expected above today's ratio.
5. Uses the released parameters (`initial_wealth_ratio`, `initial_hhwealth_dist`) and checks the
   solved first-year wealth ratio equals the target.

## S12. A quick probe of an unreleased OG-Core fix

**Prompt.** You maintain the OG-XXX calibration. A colleague has an unreleased OG-Core fix on a
local branch (`~/Projects/OG-Core-fix`) that should speed up OG-XXX's transition, and the user
wants to know today whether it does. You already have a development clone of OG-XXX with a working
virtual environment from last week, so the quickest route is to install the fix into it and run.
It is only a probe, not a reported result. Say exactly how you will set it up and run it, step by
step. At most 250 words.

**Rubric.**
1. Do not install the fix into the existing clone (no `pip install -e`, no `uv pip install`, no
   `PYTHONPATH`); "only a probe" is not an exception.
2. Put the unreleased OG-Core in through OG-XXX's own pin on a branch (`[tool.uv.sources]` with
   the commit, `uv lock`, commit).
3. Install that branch with OG-Core's official installer into a new folder (running the installer
   from that folder so its log sits beside the copy).
4. Run the preflight before launching, and expect it to fail a hand-built or moved copy or an
   OG-Core that does not match the lock.
5. Run the repo's own example (or tuning) script unchanged: no driver, wrapper or patch.
6. Compare against an installed copy without the fix (or the shipped baseline), and treat the
   result as a lead until an official run confirms it.
7. Propose the command and duration and launch only on the user's go.

## S13. A tuning round that loses settings

**Prompt.** You are tuning OG-XXX with its repo's `examples/tune.py`, which solves the packaged
parameters plus an overrides file and writes the next dial values with `--next`. Your overrides
file also carries three non-dial settings you are testing (new capital-stock values). After a
round you notice the next file holds only the dials, so the next round would drop the three
settings. You need four more rounds today. What do you do? At most 200 words.

**Rubric.**
1. Change the repo's tuning script so the next file carries every override forward (on the work
   branch, committed), then re-install.
2. Do not merge the files with a script of your own, edit them by hand between rounds, or wrap the
   tuning script.
3. Run each round as one call of the repo's script on the previous round's file; do not launch
   one step outside the sequence by hand.
4. Check that each round's input still holds the three settings before launching it.
5. Treat any rounds already run without the settings as invalid and rerun them.
6. Fold the settled values into the packaged parameters and take reported numbers from the
   shipped example, not from the tuning output.

## S14. Two capital-output ratios

**Prompt.** For a lower-middle-income country, Penn World Table 11.0 gives a capital-output ratio
of 2.2 at current PPPs (`cn/cgdpo`) and 2.6 at current national prices (net stock over `v_gdp`).
The national accounts give consumption of fixed capital of 11% of GDP and gross fixed capital
formation of 24% (public 6%). A colleague prefers the PPP ratio because, with a capital share of
0.45, the national-price ratio "implies a return on capital above 15%". Which ratio do you target,
how do you set `delta_annual`, and what do you check about the return? At most 300 words.

**Rubric.**
1. Targets the national-price ratio: the model has one good and is scored on nominal shares, so the
   stock, investment and depreciation share one price basis.
2. Uses private capital: subtracts public capital (nominal) from the ratio and government CFC from
   depreciation; `delta` = private CFC/Y over private K/Y on the same basis.
3. Checks steady-state investment `(g + delta)·K/Y` against measured private investment.
4. Answers the return objection by checking the capital share (self-employment income, resource
   rents, product taxes, public capital) and comparing like with like (pre-tax evidence such as PWT
   `irr` with a pre-tax model return; after-tax with the owners' return), not by switching basis.
5. Does not compare return evidence with `r_p`.

## S15. Old-age hours at the bound

**Prompt.** Calibrating `chi_n` to hours per person by age, the fit hits OG-Core's upper bound
(10,000) from age 64. The labour force survey reports one band for 65 and over; above that, the
target was extended by tapering hours with the National Transfer Accounts' labour income per
person. A colleague proposes rescaling the earnings matrix so `chi_n` fits under the bound, or
ending working life at 80. What do you do? At most 250 words.

**Rubric.**
1. Identifies the double count: labour income per person already contains the fall in pay that the
   earnings matrix applies again, so the extrapolated target is wrong.
2. Builds the old-age decline from a household survey's own age bands, anchored to the labour force
   survey's level, and fits only where data exist.
3. Treats a units rescale as a normalisation only (and notes what else must scale: `chi_n`,
   `c_min`, wealth-tax levels), not as a fix for a missing mechanism.
4. Looks for the missing mechanism (family support, transfers by age) rather than chaining
   workarounds; tests an idea cheaply and on the transition before adopting it.
5. Reports ages at the bound as a gap instead of forcing them.

## S16. Transfers per person by age

**Prompt.** A young, fast-ageing country leaves OG-Core's default `eta` (the transfer allocation)
and sets `alpha_T` from the budget. Aggregate transfers match the data, but the oldest households
consume far more than any survey shows in the first decades of the transition. What is going on,
and what do you check and change? At most 250 words.

**Rubric.**
1. Notes the default `eta` is not the country's (US population age shares times `lambdas`).
2. Explains that households receive `eta·TR/omega`, so with a fixed share, transfers per person
   move inversely with each cell's population share and the old are overpaid while their share is
   small.
3. Checks transfers per person by age and group along the transition, not only the aggregate.
4. Rebuilds `eta` from the country's own population or programme evidence, and uses `eta` by year
   where the installed ogcore supports it (an unreleased feature; checks).
5. Applies the same to `eta_RM`.

## S17. Reviewing a calibration PR draft

**Materials.** None.

**Prompt.** A draft calibration PR for OG-XXX has these sections: "How we got here" (five tuning
rounds and why patience moved twice); a fit table (model, data, source); "Results of the example
reform" (percent changes in GDP and revenue); "Tested" (test counts and run times); and paragraphs
quoting numbers from the docs typed by hand. What do you change before it goes to review? At most
250 words.

**Rubric.**
1. Removes the history of rounds and alternatives; the PR reports the fit, not how it was reached.
2. Removes the reform results (a calibration is judged by its fit).
3. Keeps and completes the fit table (every scored moment with source; steady state and early
   transition labelled) and the remaining gaps with their causes.
4. Requires every number and figure to come from the final run and the packaged JSON through the
   repo's tooling, not typed.
5. Adds an independent check of every number and claim before the push.
6. Keeps the changed-parameters table (old → new).

## S18. The budget identity with aid

**Prompt.** Steady-state inputs: tax revenue 12% of GDP, foreign aid to the government
(`alpha_FA`) 1.5%, transfers (`alpha_T`) 3%, public investment (`alpha_I`) 5%, pensions 1%, no UBI,
`debt_ratio_ss` 0.40, `r_gov` 0.02, `g_y` 0.03, `g_n_ss` 0.01. What government consumption share is
consistent with debt holding at its anchor, and how do you confirm it after a solve? At most 200
words.

**Rubric.**
1. `pb* = (r_gov − g)·debt_ratio_ss` with `g = e^{g_y}(1 + g_n_ss) − 1` (about 0.0408), no
   division by `1 + g`: `pb*` ≈ −0.83% of GDP.
2. `G/Y = 12 + 1.5 − 3 − 5 − 1 + 0.83` ≈ 5.3% of GDP, with aid counted as a resource.
3. Confirms by rebuilding `G/Y` from the saved output and matching the solved `G/Y`, and compares
   it with the `alpha_G` entered.
4. Notes the steady state solves whatever `alpha_G` is; the transition shows an inconsistency.

## S19. An outlier from a cross-country table

**Prompt.** A published cross-country table lists an intertemporal elasticity of substitution for
your country of 0.05 (implying `sigma` 20), against 0.5 for a neighbour. OG-Core caps `sigma` at
2. What do you do? At most 200 words.

**Rubric.**
1. Checks whether the value is a direct estimate or a formula applied to the country, and whether
   the country is inside the sample.
2. Treats the outlier as a question, not a finding.
3. Does not request an OG-Core change to raise the cap before using existing levers.
4. Considers a subsistence floor (`c_min`) to represent low substitution near subsistence, with
   `sigma` near the default.
