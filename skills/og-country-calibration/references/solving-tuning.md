# Solving, tuning and the environment

How to run the model is in og-run-rules.md (a copy ships with this skill). This file holds the
background, the troubleshooting, and the tuning loop. When a solve misbehaves (a steady state that
will not converge, a resource-constraint error on the transition, a stall), use
og-solver-diagnosis: it holds the warm-start procedure, the triage of resource-constraint errors by
period, and the pattern for running against an unreleased ogcore.

Contents
- Environment
- Installing and running: troubleshooting
- Why the run rules look the way they do
- The tuning loop
- Order: settle the inputs, then tune once
- Derived parameters regenerate together

## Environment

- **What `Calibration` delivers.** `Calibration(p, update_from_api=False)` (the class default)
  fetches nothing and overlays only identity values (single-industry `alpha_c=[1.0]`,
  `io_matrix=[[1.0]]`); `macro_params` and `demographic_params` are `{}` and `e` is `None`. Count
  what it actually sets: OG-JPN delivered seven parameters where thirty-four mattered. The packaged
  JSON is what makes the whole surface visible. [JPN]
- **The installer runs uv.** `AGENTS.md` covers what the installer does not; the contributor guide
  still describes conda in most repos.
- **Keep `uv.lock` and `.python-version` out of a calibration PR.** In the EAPD-DRB repos the lock
  is updated by Dependabot; if a local sync touches it, restore it.
- **Check the resolved ogcore in `uv.lock`, not the `pyproject.toml` floor.** Floors and resolved
  versions differ across repos. A parameter this skill relies on (`TPI_outer_method`,
  `r_gov_floor`, the `initial_guess_b_SS` family, `alpha_D_ext`) may be missing from an older
  ogcore: check with `hasattr(Specifications(), ...)` in that environment, and treat an ogcore bump
  as its own change. A bump can rename a parameter or change its shape, so load the packaged JSON
  against the new version (og-run-preflight `--params-json`) and fix what it rejects first.
- **Preflight** (og-run-preflight) prints the branch and commit of every repo involved and the
  interpreter, and checks that imports resolve inside the intended copy. Editable installs and
  shadowing on `sys.path` silently run another checkout's code; this has caught real
  contamination.
- **The example run is a smoke test, not a correctness check.** `test_run_example.py` (marked
  `local`) only checks the process is alive after about five minutes. Numeric validation is the
  dashboard.
- **CI-equivalent suite:** `uv run python -m pytest -m 'not local' -q`.

## Installing and running: troubleshooting

- **Run the installer from the new parent folder,** so its log (`.install-*.log`, which the
  preflight reads) sits beside the copy.
- **The installer names the package from the last part of the URL** (lowercased, hyphens dropped)
  and checks that it imports. Install from a clone whose folder is named like the repo
  (`.../OG-<XXX>`), not from a worktree or a demo folder (`OG-<XXX>-demo`), which installs but
  fails the import check.
- **A copy is tied to the commit it cloned.** When the branch moves, install the new commit into a
  new folder rather than pulling inside the copy.
- **Testing an unreleased ogcore under a country model:** pin it on a branch of the country repo
  and install that branch (og-solver-diagnosis, "Running against an unreleased ogcore").
- **Tests that solve the model:** OG-Core's test files build a smaller worker pool than the
  examples (`test_TPI.py`: 4 workers × 2 threads), so their timings are not the example's.
- **If Anderson oscillates or stalls,** finish that run with damped iteration and record the slower
  time per iteration (15–17 minutes per scenario is normal for the fallback). A stall that comes
  with a drifting debt path points at the fiscal setup: fix that, then retry Anderson. Anderson
  works on the transition only and never fixes a fiscal runaway.
- **Solver field names change between ogcore releases;** check the installed version has the
  fields you set rather than relying on release tags (some releases were published untagged).

## Why the run rules look the way they do

- **Results from other paths were wrong.** Hand-built environments, driver scripts, wrappers that
  merged tuning files, and runs launched outside the sequence each produced invalid rounds that had
  to be redone, and a dev checkout once reproduced a known-buggy number. [ETH, PHL, ZAF]
  (history: ETH, PHL)
- **Why seven workers.** `SS.py` and `TPI.py` call `client.submit` inside `for j in range(p.J)`,
  so workers beyond `J` idle; seven is full parallelism when `J = 7`. The examples build one
  `Client(n_workers=min(cpu_count(), 7), threads_per_worker=1)`.
- **Why not a serial steady state.** Older ogcore re-sent the parameters to the workers on every
  evaluation, which made the steady state slower through the client (~38 s vs ~6 s per evaluation
  [JPN]). On a current ogcore a slow steady state through the client is a finding to report.
  `runner` always re-solves the steady state, so `runner(time_path=False)` followed by
  `runner(time_path=True)` solves it twice.
- **Why Anderson.** The PHL transition went from ~30–70 damped iterations (~20 min) to 11–12
  (~2–2.5 min) with steadily falling distances [PHL]; OG-Core's changelog reports a stiff
  multi-industry reform converging in 53 outer iterations instead of 126.
- **Why one job at a time when timing.** Two solves at once share the cores and leave timings that
  cannot be compared. [ETH]

## The tuning loop

Tuning uses real solves, not algebra: a warm-started steady state takes seconds, so solve → read
the dashboard → adjust the dials → re-solve converges in 3–5 rounds for half a dozen dials (the
progressive-tax scale, `tau_c`, the CIT factor, `p_wealth`, `r_gov_shift`, `zeta_K`). [PHL]

The repo ships the tuning script (`examples/tune_ss.py` or similar). It loads the packaged JSON
plus an overrides file, builds the example's worker pool, solves, prints model against target, and
writes the overrides for the next round with every setting carried forward, so one round is one
invocation. If a round needs something the script cannot do, change the script on the work branch
and re-install. When the dials settle:

- fold the settings the last round actually solved into the JSON (and any scales into the code that
  builds it), commit, re-install, and take every reported number from the example script;
- finish with a solve of the packaged JSON with no overrides; it catches schema errors and seed
  problems the overrides hide.

Log every solve to a named file with its settings first (`logs/tune_r04.log`). Seed every solve
from the last converged one: on KOR the same calibration took 394 s from uniform seeds and 32 s
warm. A dial move that breaks a warm-started solve is a calibration signal; one that breaks a cold
start is usually the seed. After a large change (a preference parameter, the capital stock),
regenerate the repo's warm-start seed from the last converged solve. [KOR, ETH]

## Order: settle the inputs, then tune once

Every tuned dial is fitted against the inputs below it, so a corrected input means a retune. JPN
took fourteen rounds because `gamma`, `delta`, `g_y`, `alpha_T` and the data window were each
corrected after the tax dials were tuned; ETH and PHL each lost rounds the same way. [JPN, ETH,
PHL] Work in this order:

1. agree what the baseline targets (the observed start year; a fiscal program or forecast is a
   scenario, not the baseline);
2. settle every sourced input from data, one decision at a time, each logged with its source;
3. tune the dials once: tax dials against revenue, `zeta_K` against the foreign capital share,
   patience last (macro-open-economy.md, `beta_annual`);
4. validate with the example script, steady state and transition.

Audit the whole parameter surface before step 3. After any tax change, re-tune `zeta_K`.

## Derived parameters regenerate together

Anything computed from demographics (a `g_RM` path from `g_n`, an `eta_RM` matrix from `omega_SS`)
belongs in the demographics-regeneration tool, so a rebuild cannot leave it stale. Add a test that
the packaged value equals the constructor applied to the packaged inputs. [PHL]
