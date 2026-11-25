# Model-tools

Shared agents, skills, prompts, templates, and workflow tools for OG and CLEWS
model work. This repo is a common home for the reusable pieces we build once
and want to use across model projects — for example, the OG country
calibration skill and shared agent definitions.

## What goes where

| Folder        | Contents |
|---------------|----------|
| `agents/`     | Reusable agent definitions (subagent files, system prompts). |
| `skills/`     | Skills that package a repeatable task (e.g. OG calibration), one dir per skill. |
| `prompts/`    | Standalone reusable prompts — analysis, review checklists, briefings. |
| `templates/`  | Copy-and-fill starting points — config templates, doc skeletons, boilerplate. |
| `workflows/`  | Multi-step processes that orchestrate agents, skills, and scripts. |
| `scripts/`    | Small helper scripts (Python, shell) supporting the tools here. |
| `docs/`       | Longer-form guides, background notes, and reference material. |

Each folder has its own `README.md` with a bit more detail.

## Available tools

| Tool | Type | Description |
|------|------|-------------|
| [clews-model-fix](skills/clews-model-fix/SKILL.md) | skill | Make a structural fix to a MUIO/OSeMOSYS CLEWs model that cannot change any solved value: remove unreferenced technologies, commodities or emissions, fix placeholder descriptions, adjust technology groups. Start here for small changes. |
| [build-clews-model](skills/build-clews-model/SKILL.md) | skill | Build a new uncalibrated OSeMOSYS/CLEWs country model from CLEWs Global and package it as a solved, source-traceable MUIO case. Not for calibration or structural cleanup. |
| [add-fisheries-sector](skills/add-fisheries-sector/SKILL.md) | skill | Add a complete, source-traceable, non-forcing Fisheries sector to an existing solved OSeMOSYS/CLEWs/MUIO country model, including residual stock, boundary reconciliation, unchanged-solver validation, and policymaker-ready number lineage. |
| [assess-clews-calibration](skills/assess-clews-calibration/SKILL.md) | skill | Evaluate technical validity, historical adequacy, forcing, evidence coverage, and fitness for purpose of an OSeMOSYS or full CLEWs country model. |
| [calibrate-clews-model](skills/calibrate-clews-model/SKILL.md) | skill | Refine a solved CLEWs Global country model with better sourced national data, physical stocks and constraints, connectivity repairs, complete inherited schema-ledger provenance, and integrated solve/diagnostic validation. |
| [og-scenario-report](skills/og-scenario-report/SKILL.md) | skill | Design OG-Core reform scenarios and present finished runs: the standard tables, charts and narrative, plus bespoke analysis, comparisons and write-ups. |
| [og-country-calibration](skills/og-country-calibration/SKILL.md) | skill | Calibrate a new OG-Core country model or update one to new data: the order that works, methods and pitfalls by block, validation, tracing where existing values came from, and lessons from other countries indexed by situation. |
| [og-run](skills/og-run/SKILL.md) | skill | Install and run an OG-Core model the way its users do: install, check the environment, run the example, monitor, collect output with provenance, test a code change. |
| [og-solver-diagnosis](skills/og-solver-diagnosis/SKILL.md) | skill | Find the root cause of an OG-Core solve that fails, stalls, diverges or looks wrong, before changing any solver setting. |
| [og-multi-industry-calibration](skills/og-multi-industry-calibration/SKILL.md) | skill | Build or review a multi-industry OG-Core calibration from a SAM or input-output tables, consistent with the single-industry model. |
| [pull-handoff](skills/pull-handoff/SKILL.md) | skill | Bootstrap or update the Fiji and Philippines CLEWs repositories and install their current MUIO case locally. |
| [push-handoff](skills/push-handoff/SKILL.md) | skill | Package the local Fiji and Philippines MUIO cases, verify them, and commit and push the country-repository changes. |
| [clews-model-review](skills/clews-model-review/SKILL.md) | skill | Review a MUIO/OSeMOSYS CLEWs model for structure and data consistency against the NamibiaCLEWs benchmark: referential integrity, orphaned IDs, dangling/stranded technologies, unit discipline, sector coverage, and solve status — via a bundled `audit.py` checker plus a rubric. |
| [add-environmental-accounting](skills/add-environmental-accounting/SKILL.md) | skill | Add a JSON-first environmental accounting layer to any MUIO/OSeMOSYS CLEWS model: inventory physical flows, create separate water and land terminals, preserve existing services, regenerate every scenario through MUIO, and quantify regression differences. |

## What not to commit

Keep this repo shareable. Do **not** commit:

- **Secrets** — API keys, tokens, passwords, credentials, `.env` files.
- **Generated outputs** — model runs, solver output, plots, logs, archives.
- **Large data** — datasets, SAMs, or binaries; link to their source instead.
- **Partner-sensitive material** — anything that shouldn't be shared broadly.

The `.gitignore` covers the common cases, but check your `git status` before
committing.

## Contributing

- One tool per file or directory; give it a short README or header explaining
  what it is and when to use it.
- Match the existing layout — put things in the folder that fits.
- Keep commit messages to a single line.
- Prefer pointers to large or sensitive data over copies of it.
