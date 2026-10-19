# Maintaining the OG skills

How the OG skills (og-country-calibration, og-multi-industry-calibration, og-solver-diagnosis,
og-run, og-run-preflight) are written, tested and extended.

## Objective

A skill that is useful to anyone working on an OG-Core country model, new or old, that carries
every lesson the family has learned, and that points to the history behind each lesson for
anyone who needs to look deeper.

## Three layers

| Layer | Holds | Lives in | Installed with the skill |
|---|---|---|---|
| Skill | Methods and checks that apply to a country you have never seen | `skills/<skill>/` | Yes |
| History | What happened, where, with the evidence: one entry per lesson | `docs/og-lessons/` | No; linked |
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
5. **History link:** `([KOR](../../../docs/og-lessons/KOR.md#anchor))` to the entry with the evidence.

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

1. Write the history entry first.
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

Model-tools is canonical for og-country-calibration and og-multi-industry-calibration; MUIOGO-AI
is canonical for og-solver-diagnosis, og-run and og-run-preflight. Each repo carries a copy of the
other's skills. Copy whole files, never edit a copy; the front pages differ only by MUIOGO-AI's
"Which world" section.
