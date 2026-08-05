---
name: push-handoff
description: Zip the current Fiji and Philippines MUIO cases without solver results, verify the archives, and commit and push the intended country-repository changes.
---

# Push Handoff

Zip and push. Do not rebuild, validate, solve, or redesign a model as part of
this skill.

## Scope

Resolve the sibling `MUIOGO`, `CLEWs-FJI`, and `CLEWs-PHL` repositories by
their Git remotes. Read applicable `AGENTS.md` files before acting.

## Workflow

1. Inspect the branch, upstream relation, and working-tree status of each
   country repository. Stop on conflicts or a behind/diverged branch. Never
   reset, rebase, force-push, or overwrite a published release.
2. Determine the current installed case and destination archive from the
   country repository's current-model documentation, unless the user names
   them explicitly. Never infer the current archive from filename sorting.
3. Export the installed case from `MUIOGO/WebAPP/DataStorage/` as one ZIP with
   one top-level case folder. Use an exclusion list: include every case file
   except `res/`, solver CSVs and logs, `data.txt`, `data_processed.txt`, LP
   files, caches, and other generated results. This preserves every editable
   parameter JSON, case-local documentation or manifest, and required `view/`
   metadata without having to predict future MUIO file types.
4. Run `unzip -t`, reject unsafe paths or excluded results, verify
   `genData.json` and `osy-casename`, and calculate SHA-256. Update only the
   checksum and current-archive pointer needed to identify this ZIP.
5. Review the diff, stage only the intended country-model files and archive,
   commit them, fetch once more, and push normally. Preserve unrelated local
   work.

Do not create a HANDOFF note, reconstruct provenance, run model validation,
or change model inputs. Those are separate modelling tasks and must be
requested separately.

Report the archive path and SHA-256, commit, pushed branch, and any repository
skipped because it was unsafe to update.
