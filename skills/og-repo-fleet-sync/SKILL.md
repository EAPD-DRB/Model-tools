---
name: og-repo-fleet-sync
description: "Applies one change across the OG-Core country-repo fleet (OG-USA, OG-PHL, OG-ZAF, OG-IDN, OG-BRA, OG-ETH, OG-FJI and variants) and tracks which repos have it. Use when a fix or upgrade proven in one repo must reach the others (a dependency break, CI or docs update, tooling migration, shared test or packaging fix), or when asked which repos still need something. Prepares per-repo branches and commits; never pushes or opens PRs without asking."
---

# OG repo fleet sync

Generalized from the pandas-3 import-fix rollout (its worked playbook, if one exists on this
machine, shows the level of detail a playbook should reach). The problem this solves: ~20 sibling repos drift apart because changes land in one
repo and propagate by hand, or never (the conda→uv drift is the standing cost of not doing this).

## Name the checkouts

This skill works across several checkouts on purpose. Name each one you look at or change (path,
branch, commit), and leave installed copies that other work depends on alone unless asked.

## The shape of the work

Never loop "fix repo, next repo" from memory. Four phases, with a written artifact between each:

### 1. Characterize the change once — write the playbook

From the repo where the fix is already proven (or being developed), write a short playbook file
before touching a second repo. It must contain, concretely:

- **Detection**: a command that decides "is this repo affected?" mechanically, e.g.
  `rg -n "pandas_datareader|wb\.download" .` plus a smoke probe
  (`.venv/bin/python -c "import <pkg>"`). Detection must be runnable read-only.
- **Fix pattern**: the minimal change, as a pattern, not a diff — repos differ in package name
  (`ogphl`/`ogzaf`/...), layout, and idiom, so a blind cherry-pick is usually wrong.
- **Semantic assumptions to preserve**: the non-obvious invariants the fix must not break. (In the
  worked instance: descending date order mattered because downstream used `pct_change(-1)` —
  transport-level replacement, semantic-level bug.)
- **Tests to add** (e.g. an import smoke test) and **validation commands** — the repo's own
  (`uv run python -m pytest -m 'not local' -q`, `black --check`/`make format`), not a generic set.
- **Scope boundary**: what is explicitly Phase-2 cleanup (design changes, gating, docs refactors)
  that goes to follow-up issues, never into this rollout.

### 2. Probe the fleet — build the tracking table

First check the change has not already landed: search each sibling's merged PRs and grep its
up-to-date upstream default branch for the fix. Some siblings may have reached the same goal
another way, or removed the code on purpose; those rows are not to be "fixed".

Enumerate the fleet fresh (`ls -d <projects root>/OG-*`), and separate **canonical checkouts** from
worktrees/`_bak`/`copy` dirs — sync canonical checkouts only. When sprawl makes this unclear, `git worktree list` in each
checkout separates the two (a personal `worktree-orchard` skill, if installed, does the full
inventory). Run detection read-only on every repo and write the
tracking table to a file (it outlives the session — put it next to the playbook, never inside a
country repo):

| repo | org | affected? | already fixed? | branch | status | notes |
|---|---|---|---|---|---|---|

Statuses: `unaffected` / `already-fixed` / `diverged-on-purpose` (cite the PR that did it) /
`branch-ready` / `blocked` / `needs-decision`. When every canonical checkout sits on a busy
feature branch, work in a fresh worktree off the up-to-date default branch rather than reusing
one.
Fleet facts that change the work per row: EAPD-DRB repos (PHL/ZAF/IDN/ETH/FJI) share the uv +
Dependabot-lock convention — **never commit a `uv.lock` change from sync work**; PSLmodels repos
(USA/BRA) differ in tooling and review culture. Record the org.

### 3. Apply per repo — fresh branch, minimal scope, repo's own validation

Per affected repo:

1. `git fetch --all` first. Branches come from the fork (`origin`), not from upstream: bring the
   fork's default branch up to date with upstream's, then branch from it
   (`git switch -c <change>-<slug>`). Never work on a repo's default branch directly.
2. Re-run detection *in this repo* and read the actual code — expect the pattern to vary. The
   worked instance's second repo lesson: fixing the primary import exposed a *second* import-time
   side effect that also had to move; the smoke test, not the plan, decides when you're done.
3. Apply the minimal fix; add the playbook's tests; run the repo's own validation commands.
   Distinguish *your* failures from pre-existing ones — several repos carry unrelated CI/test
   debt; note pre-existing failures in the table rather than fixing them (scope boundary).
   Distrust old green tests near your change (the worked instance found a
   `list(x).sort() == y.sort()` test that compared `None == None`).
4. Commit with a single-line message; update the tracking table row to `branch-ready`.

Copy this per repo and work through it:

```
- [ ] Fetched; fresh branch off the up-to-date default branch.
- [ ] Detection re-run here; the actual code read.
- [ ] Minimal fix applied; playbook tests added; the repo's own validation run.
      If a failure is not yours: mark it pre-existing in the table, do not fix it.
      If the fix stops being minimal: mark the row needs-decision, move to the next repo.
      If the smoke test still fails: back to the detection step for this repo.
- [ ] Single-line commit; table row set to branch-ready.
```

### 4. Report

When the sweep is done (or blocked), present the tracking table, a per-repo diffstat, and any
`needs-decision` rows. Everything up to here, local branches and commits, is preparation that has
not left the machine. Pushing, opening PRs and merging follow the project's and the user's rules;
show each PR's draft text first, since a PSLmodels repo may want different framing than an
EAPD-DRB one. If PRs are
approved: per-repo PR text follows the playbook (what/why/tested), with Phase-2 items filed as
follow-up issues, not folded in.

## Standing rules

- The tracking table is the deliverable as much as the branches — a half-done sweep with an
  accurate table is resumable; a half-done sweep in memory is lost.
- Mechanical work repeating across 3+ repos gets a script (detection sweeps especially); judgment
  (adapting the fix, reading validation output) stays manual per repo.
- Secrets (`un_api_token.txt` sits in several working trees) must never end up in commits, diffs,
  or the playbook.
- If a repo's fix stops being minimal (architecture fights back, third attempt), stop — mark
  `needs-decision` with the evidence and move on; don't sink the fleet sweep into one repo.
