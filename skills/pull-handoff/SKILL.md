---
name: pull-handoff
description: Pull the Fiji and Philippines model repositories, safely unzip their current MUIO cases into ignored repository-local working trees, and maintain relative MUIOGO DataStorage symlinks.
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
4. Require `/case/` to be ignored by the country repository. Install the
   archive as `<country-repository>/case/<case-name>`, never as a tracked
   working tree. Extract to a temporary directory first. If the existing
   local case differs in non-result content, move the complete old case to
   `case/.backups/<case-name>-<timestamp>` before installing. If it matches,
   leave it intact so local results are not discarded.
5. Maintain `MUIOGO/WebAPP/DataStorage/<case-name>` as a relative symlink to
   the repository-local case. Leave a correct link unchanged. Before replacing
   a real directory, broken link, or wrong link, move it recoverably under
   `case/.backups/`; never delete it. Verify that the final link resolves to
   the intended case and that `osy-casename` matches its directory name.
6. If the result-free ZIP omitted empty run directories, recreate the empty
   `res/<run>/csv` directories declared by `view/resData.json` inside the
   repository-local case.

Do not solve, run validation, reconstruct provenance, or edit the model.

Report pulled repositories, repository-local case paths, relative symlink
targets, archive hashes, backup paths, and any repository skipped because of
local changes.
