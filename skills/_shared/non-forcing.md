# The non-forcing boundary

The single authoritative statement of this rule. Every CLEWs skill links here.
Do not restate it in a skill; link to it. Divergent copies are how this rule rots.

## The bright line

**Do not use historical observations to make model results match history.**

Observed data is legitimate as a *structural input* (geography, seasons, administrative
units, technology applicability), as *final demand*, as a *benchmark you report against*,
or as evidence for an explicitly documented *initial stock*. It is not legitimate as an
activity target.

## The counterfactual test

One wording. Apply it to any change that touches a parameter or a constraint:

> **Would this exact change still be made if no historical outcome were known?**

If no, it is calibration-by-fitting. Defer it, document it, and leave the raw model alone.

## Never add or tune

- historical generation-share, fuel-share or dispatch-share locks;
- equal historical lower/upper activity bounds (`TAL == TAU`, `TAMinC == TAMaxC`) with a
  positive value;
- historical minimum/maximum capacity locks;
- capacity, demand, availability, capacity-factor, efficiency, cost, fuel, emissions or
  yield overrides selected to reduce historical error;
- hydro, biomass, fuel-supply, land, crop or water parameters inferred solely by solving
  backward from an observed outcome;
- smoothing or ramp constraints introduced only to conceal a historical-to-forecast
  discontinuity;
- a constraint that expires after an arbitrary calibration window. Use a full-horizon
  physical dynamic — stock survival, lifetime, turnover, adoption, resource availability,
  demand — or leave the outcome endogenous.

A user-defined constraint is permitted only when it faithfully ports an upstream
formulation feature or implements a documented, labelled workaround. Never use a UDC to
lock historical capacity, activity, generation, land, water or emissions.

## What to do instead

Record the gap; do not close it by force. For every material mismatch, log the observed
value, the modelled value, the suspected driver, and the parameter that would legitimately
change if better evidence arrived. Mark every such comparison **diagnostic — not fitted**.
Keep historical performance data in a calibration-candidate inventory and apply none of it
during a build.

## Enforcement

`clews-model-review/audit.py` implements the exact-bound-pair detection for the
`TAL`/`TAU` and `TAMinC`/`TAMaxC` families. `build-clews-model/scripts/audit_no_forcing.py`
covers the config-level forcing keys and the upstream drift diff. Run the audit that
applies to your representation; do not hand-check this list.

## Language

Never call a result calibrated, validated against history, or policy-ready on the strength
of a solver status. Solver success is technical validity only.
