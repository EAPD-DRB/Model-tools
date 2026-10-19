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
