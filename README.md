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
