# Method: moments, levers and the dashboard

How to find what moves a target moment before tuning anything, and why the transition needs
validating as well as the steady state.

## Step zero: write the equations down before you touch a parameter

Before tuning anything, produce a moment × lever table and commit it. Build it from the equations
OG-Core evaluates (`firm.py`, `aggregates.py`, `household.py`, `fiscal.py`, `tax.py`), not from
convention or this skill's tables. It takes under an hour and pays back more than any other hour of
a calibration. For each target moment write:

1. **The closed form,** every symbol in it. Reproduce the solved value from your formula to 4
   decimals before trusting it. A mismatch means you read the wrong equation, and finding that out
   now costs minutes.
2. **Every parameter in it,** marked `sourced` / `tuned-to-<moment>` / `default-unexamined`.
3. **Which other moments share those levers.**

Worked example, `K/Y`, where convention names one instrument (`beta`). From `firm.get_r`,
`r = (1-tau_b)·p_m·MPK - delta + tau_b·delta_tau + inv_tax_credit·delta`, so under Cobb-Douglas:

```
K/Y = (1 - tau_b)·gamma / (r + delta - tau_b·delta_tau - inv_tax_credit·delta)

  gamma            sourced (PWT labour share)
  delta            sourced (CFC/K)
  tau_b            = cit_rate x c_corp_share_of_assets x adjustment_factor
                     c_corp_share_of_assets = 0.55 is a US default, and it is not
                     separately identified from adjustment_factor -- only the product is
  delta_tau        default 0.027 (US tax depreciation)
  inv_tax_credit   default 0.0
  r                not a parameter -- the household Euler pins the portfolio return r_p,
                     and r solves r_p = weighted avg of r (on K) and r_gov (on D).
                     So beta, sigma, g_y, debt_ratio_ss, r_gov_scale/shift,
                     zeta_K and world_int_rate are all levers on K/Y.

  shares levers with: C/Y (via I), I/Y, K_f/K, r
```

Write the tax terms in full; they are not small (on JPN they move the numerator 14% and the
denominator 3.5%), and `gamma/(r+delta)` points you at the wrong lever. The table has eleven
levers; convention has one. A bigger stock of government debt makes capital pay more, which
shrinks `K`, so `debt_ratio_ss` and `r_gov` are levers too.

**The table is also the tuning order:** sourced levers first, then tuned dials, then re-check
anything that shares a lever with what you moved.

## Finding every lever on a moment

The failure this prevents: OG-JPN's `K/Y` sat 0.20 below its PWT target, the `beta` that closed the
gap broke the steady-state solve, and the miss was written up as an acceptable family trait. It was
neither. `zeta_K` sat at a placeholder 0.10 that the repo's own comment labelled `NEEDS TUNING ...
pending the IIP anchor`; set from the IIP data, it closed 79% of the `K/Y` gap and 85% of a separate
consumption gap. Fourteen tuning rounds had left it untouched.

Four rules:

1. Write the model's own closed form for the moment, then list its arguments (Step zero), not the
   conventional pairing.
2. Leave every parameter in one of three states: sourced; tuned to a named moment; or deliberately
   defaulted with a written reason. "Placeholder" is not a fourth state. Treat a `NEEDS TUNING`
   marker as open work with an exit criterion: make it a release gate and a test that matches any
   wording of the marker (`NEEDS`, `TODO`, `PLACEHOLDER`), as OG-JPN's
   `test_no_unresolved_tuning_markers` does. The JPN comment named the dataset and still shipped,
   because no test failed.
3. Treat two moments that move together as one moment, and check for shared levers before
   diagnosing either. JPN's consumption gap (+2.3pp) and `K/Y` gap (−0.20) were analysed separately
   for a whole calibration. They were the same gap: too little capital means too little investment,
   and `C = Y - I - I_g - G - NX` makes consumption absorb it. One lever closed both. Tuning symptom
   by symptom reliably leaves a spurious "structural" residual.
4. Read a lever that runs out of road as the wrong lever, not as proof the gap is structural. If the
   instrument needs a value that will not solve, or one outside its plausible range, go back to
   rule 1. Avoid the label "acceptable band"; it turns an untuned parameter into a family trait.

**Then sweep the defaults you did not source.** Perturb every unsourced parameter and record which
target moments move. Source or explicitly declare anything that moves one materially. Relevance
depends on settings you have not chosen yet: `world_int_rate` (default 0.04) is invisible at a low
`zeta_K` and sets `r` at a high one; on JPN, dropping it to 3.5% moved `K/Y` from 3.67 to 3.81 and
`K_f/K` from 17% to 27%. High openness hands the interest rate from the country's households to an
unsourced global constant. Run the sweep after the parameters settle. [net-new: JPN]

## Dashboard completeness

An unscored moment cannot pull its parameter. Give every tuned dial its own scored moment; steer a
dial by that moment, not to close a residual; score every resource-constraint component and the
early transition, not only the steady state. The four rules and their cases are in
[validation-dashboard.md](validation-dashboard.md). [net-new: JPN]

## Diagnosing a gap that will not close

Before reaching for a lever, decompose the gap with the identities the model and the data share:
investment = domestic saving + net foreign financing, and the current account from flows against
the change in foreign liabilities. The half that is missing names the lever (saving: patience and
preferences; foreign financing: `zeta_K`, external debt, payments abroad). Measure the candidate
channels in today's data rather than in the country's history: a policy that drove investment a
decade ago may be gone. Then probe each candidate once, at a bound, on the transition, and record
what it buys and what it costs on the other moments. On ETH a misread consumption series made the
gap look like foreign financing, and a week went to the capital share, the state, `zeta_K` and
state-enterprise loans before the decomposition showed it was household saving. [ETH] (history: ETH)

## Why the baseline transition is not optional

The steady state uses one number from each time-varying path (its terminal value), so a whole
mis-specified path is invisible to it. On JPN a wrong demographic window survived eleven
steady-state rounds with every fiscal moment inside 0.2pp of GDP; one transition run caught it.
