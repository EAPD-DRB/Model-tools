# Maintaining the OG skills

How the OG skills (og-country-calibration, og-multi-industry-calibration, og-run,
og-solver-diagnosis, og-scenario-report, og-repo-fleet-sync) are written, tested and extended.

## How the skills are divided

By the job a person brings, not by the steps inside it: calibrating or updating a country model
(og-country-calibration, with og-multi-industry-calibration for the overlay), just running a model
(og-run), a solve that fails or looks wrong (og-solver-diagnosis), designing scenarios and
presenting results (og-scenario-report), and carrying a change across the country repos
(og-repo-fleet-sync). Guidance every job needs (how to run the model) lives in one shared file,
copied into each skill that needs it and stated briefly on its front page, so a job never depends on
a second skill being loaded. The skills are written for anyone doing OG work with an AI assistant:
approval habits and writing style belong to each user's or project's own rules, not to the skills.

## Objective

A skill that is useful to anyone working on an OG-Core country model, new or old, that carries
every lesson the family has learned, and that points to the history behind each lesson for
anyone who needs to look deeper.

## Three layers

| Layer | Holds | Lives in | Installed with the skill |
|---|---|---|---|
| Skill | Methods and checks that apply to a country you have never seen | `skills/<skill>/` | Yes |
| History | What happened, where, with the evidence: one entry per lesson, and `INDEX.md` by situation | `docs/og-lessons/` | Yes: copied into og-country-calibration `references/lessons/` by `scripts/sync_shared.py` |
| Repo state | What a repo ships today and its open defects | That repo's issues and docs | No |

The skill grows only when a country teaches a new method. Most countries add a history entry and
nothing else.

## What a lesson in the skill looks like

Each lesson is short and has the same parts, in this order:

1. **Rule:** what to do, in one or two sentences.
2. **Applies when:** the condition, as a country characteristic (old population, net creditor,
   high-denomination currency, informal economy), never a country name. Omit if it always applies.
3. **Check:** a command, test or number the agent can verify (a grep, a closed form, a dashboard
   row, a test to add).
4. **Why:** one sentence, at most one size example ("on JPN this moved K/Y from 3.67 to 3.81").
5. **History:** the country tag (`[KOR]`), plus a `(history: KOR)` marker where the lesson's own
   numbers live in `docs/og-lessons/KOR.md` rather than in the skill.

Not in the skill:
- A country's own values (targets, data years, tuned parameters). They go in its history entry.
- Repo status ("OG-X still ships 0.9", "checked on <date>"). It becomes a Check, and the status
  goes to that repo's issues.
- Stories. The story goes in the history entry; the skill keeps the rule.
- Dated or pending facts ("not yet upstream"). Write the check ("does your ogcore have X?") and
  keep the date in the history entry.

## What a history entry looks like

`docs/og-lessons/<CODE>.md`, one `##` entry per lesson, with a stable anchor:

- **Lesson:** the rule as the skill states it, and the skill file and section.
- **What happened:** the case, with its numbers.
- **Evidence:** links to the PR, issue, commit, log or run that shows it.
- **Date** and the ogcore version, where it matters.

## Adding a lesson

1. Write the history entry first, and list it under its situation in `docs/og-lessons/INDEX.md`.
2. Ask: does an existing lesson in the skill already cover it? If yes, add the history link to that
   lesson and stop.
3. If it is a new method, add a lesson in the shape above, in the reference file for its block.
4. Run the evaluations (`evals/og-skills/`) before and after. Keep the change only if it does not
   make any scenario worse.

## Evaluations

`evals/og-skills/` holds scenarios that a fresh agent answers with only the skill. Each has a
rubric of the points a correct answer contains. Run each scenario without the change and with
it; a change ships when it improves a scenario or keeps them all equal.

## Mirrors

Model-tools is canonical for the OG skills. MUIOGO-AI carries copies; copy whole files, never edit a
copy. The MUIOGO-specific rules (its two installations, or "worlds") live in the MUIOGO skills and
og-clews-linked-run, not in the OG skills.
