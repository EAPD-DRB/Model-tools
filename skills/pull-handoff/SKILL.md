---
name: pull-handoff
description: Pull the Fiji and Philippines model repositories and safely unzip their documented current MUIO cases into MUIOGO.
---

# Pull Handoff

Pull and unzip. Do not solve, validate, or change model inputs as part of this
skill.

## Scope

Resolve the sibling `MUIOGO`, `CLEWs-FJI`, and `CLEWs-PHL` repositories by
their Git remotes. Read applicable `AGENTS.md` files before acting.

## Workflow

1. Inspect the branch, upstream relation, and working-tree status of each
   country repository. Pull only a clean, behind branch with
   `git pull --ff-only`. Stop on local changes, conflicts, or divergence.
   Never reset, clean, rebase, or overwrite local work.
2. Select the current archive named in each country repository's current-model
   documentation. Never infer it from filename sorting.
3. Verify the documented SHA-256 when available, run `unzip -t`, reject unsafe
   paths, require one top-level case folder containing `genData.json`, and
   verify its directory name matches `osy-casename`.
4. Install it under `MUIOGO/WebAPP/DataStorage/`. If an existing case differs
   in non-result content, move it to a timestamped sibling backup before
   extracting. If it matches, leave it alone. Never copy old solver results
   into the pulled case.
5. If the result-free ZIP omitted empty run directories, recreate the empty
   `res/<run>/csv` directories declared by `view/resData.json`.

Do not solve, run validation, reconstruct provenance, or edit the model.

Report pulled repositories, installed case paths, archive hashes, backup
paths, and any repository skipped because of local changes.
