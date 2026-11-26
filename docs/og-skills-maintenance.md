# Maintaining the OG skills

How the OG skills (og-country-calibration, og-multi-industry-calibration, og-run,
og-solver-diagnosis, og-scenario-report) are written and extended.

## How the skills are divided

By the job a person brings, not by the steps inside it: calibrating or updating a country model
(og-country-calibration, with og-multi-industry-calibration for the overlay), just running a model
(og-run), a solve that fails or looks wrong (og-solver-diagnosis), designing scenarios and
presenting results (og-scenario-report). Tools for maintaining the EAPD-DRB repos themselves
(carrying a change across the country repos, PR conventions) are kept privately by their
maintainers and are not part of this set. Guidance every job needs (how to run the model) lives in one shared file,
copied into each skill that needs it and stated briefly on its front page, so a job never depends on
a second skill being loaded. The skills are written for anyone doing OG work with an AI assistant:
approval habits and writing style belong to each user's or project's own rules, not to the skills.

## Objective

A skill that is useful to anyone working on an OG-Core country model, new or old, that carries
every lesson the family has learned, and that points to the history behind each lesson for
anyone who needs to look deeper.

## F.69: how the skills guide the assistant

Structure before the assistant is a blindfold; structure after it is useful persistence.

Give the assistant the objective, the principles with examples and warnings, the tools, and access
to the complete material (data, code, calibrations, papers, earlier work). Then let it read, judge
and decide. Country economies, data and questions differ too much for a fixed procedure to fit them,
and a capable assistant judges better from the evidence than from a summary of it.

Match the freedom to the fragility. Analysis is open ground: what matters in a dataset, which method
the data support, what a result means. Leave that to the assistant. A few steps are fragile because
a mistake there is costly, hard to undo or breaks reproducibility. For these, state the step exactly
and say why: keep originals unchanged; tie every claim to its source and compute every number from
the actual outputs; keep references stable and runs reproducible; respect cost limits; keep a
lasting record; release nothing without the user's go. The operating skills spell these out.

Structure placed after the assistant keeps its work: decision records with their evidence,
histories, tests that pin decided values, run provenance. Records are an index and a history; read
the material itself.

Before adding structure to a skill or tool, ask which side of the assistant it sits on. If it sits
before the assistant and is not one of the fragile steps, it has to justify itself.

This follows the skill-writing guidance of Anthropic (Agent Skills best practices: set the degree of
freedom by the task's fragility; explain why; concise, consistent terms) and OpenAI (prefer
instructions to scripts unless the behaviour must be deterministic; avoid contradictory or
over-emphatic instructions).

## Three layers

| Layer | Holds | Lives in | Installed with the skill |
|---|---|---|---|
| Skill | Methods and checks that apply to a country you have never seen | `skills/<skill>/` | Yes |
| History | What happened, where, with the evidence: one entry per lesson, and `INDEX.md` by situation | `docs/og-lessons/` | Yes: copied into og-country-calibration `references/lessons/` by `scripts/sync_shared.py` |
| Repo state | What a repo ships today and its open defects | That repo's issues and docs | No |

The skill grows only when a country teaches a new method. Most countries add a history entry and
nothing else.

## What a lesson in the skill looks like

A lesson equips the assistant's judgment; it does not replace it (see "How the skills guide the
assistant", F.69). Each lesson is short and uses these parts, leaving out any that add nothing:

1. **Principle:** the objective and the concept: what a good answer is and why, in one or two
   sentences.
2. **Applies when:** the condition, as a country characteristic (old population, net creditor,
   high-denomination currency, informal economy), never a country name. Omit if it always applies.
3. **Examples:** the methods that have worked, as a ladder from the best the data allow down to a
   documented fallback, each with where it was used and what it needs.
4. **Warnings:** the traps seen, each with its size where known ("on JPN this moved K/Y from 3.67
   to 3.81").
5. **Check:** what a good answer passes, as something the assistant can verify (a closed form, a
   dashboard row, a test to add, a grep).
6. **History:** the country tag (`[KOR]`), plus a `(history: KOR)` marker where the lesson's own
   numbers live in `docs/og-lessons/KOR.md` rather than in the skill.

State an exact step only where the step is fragile: a mistake there is costly, hard to undo or
breaks reproducibility. Then give the step and its reason. Everywhere else, describe the objective
and the evidence and let the assistant choose.

Write each lesson so an assistant can use it without the code it came from: the data concept, the
transformation, and the check. Name sources and scripts only as examples or helpers ("for example",
"if the repo has one"), never as the one required route; OG-Core's own parameter and function names
stay, since they are the interface.

Not in the skill:
- A country's own values (targets, data years, tuned parameters). They go in its history entry.
- Repo status ("OG-X still ships 0.9", "checked on <date>"). It becomes a Check, and the status
  goes to that repo's issues.
- Stories. The story goes in the history entry; the skill keeps the principle and the warning.
- Dated or pending facts ("not yet upstream"). Write the check ("does your ogcore have X?") and
  keep the date in the history entry.

## What a history entry looks like

`docs/og-lessons/<CODE>.md`, one `##` entry per lesson, with a stable anchor:

- **Lesson:** the principle as the skill states it, and the skill file and section.
- **What happened:** the case, with its numbers.
- **Evidence:** links to the PR, issue, commit, log or run that shows it.
- **Date** and the ogcore version, where it matters.

## Adding a lesson

1. Write the history entry first, and list it under its situation in `docs/og-lessons/INDEX.md`.
2. Ask: does an existing lesson in the skill already cover it? If yes, add the history link to that
   lesson and stop.
3. If it is a new method, add a lesson in the shape above, in the reference file for its block.
4. Re-read the skill as someone new to the country would: does the lesson sit where that person
   will look, and does it say plainly what a good answer is, what has worked and what to watch for?

## Learning from use

The skills improve through real calibrations: each country, update or multi-industry build is the
test. When a session shows the skill missing something, misleading, or being worked around, record
it as a history entry and adjust the skill. `evals/og-skills/` keeps written scenarios with rubrics
from earlier rounds; they check what an agent knows, not what it does under pressure, so treat
them as a quick check of knowledge, not as the gate for a change.

## One home per skill, and how other repos carry the skills

Every reusable skill has one home, and it is edited only there:
- **Model-tools:** the OG skills (og-run, og-solver-diagnosis, og-country-calibration,
  og-multi-industry-calibration, og-scenario-report), the CLEWs skills and the
  handoff skills, with their history (`docs/og-lessons/`), shared rules (`skills/shared/`) and
  evaluations.
- **The repo whose code a skill drives:** a skill that instructs one product's interface lives with
  that product (MUIOGO-AI's `muiogo-*` skills drive its `muiogo` command line, and
  og-clews-linked-run drives the OG-CLEWS link inside a MUIOGO installation; MUIOGO-AI also holds
  its installation rules, `WORLD_DISCIPLINE.md`).

Skills here are written for any environment. They never depend on one; where an environment adds
its own instructions (where models are installed, which installation to use), the skills follow
them through one generic line in the shared run rules, and the environment states them in its own
`AGENTS.md` or workspace skill.

A repo that carries Model-tools skills (MUIOGO-AI) vendors them unchanged at a pinned Model-tools
commit, records the pin, and checks that its copies equal the pinned ones; it never edits a copy.
Fixes go here first, then the pin moves. Lessons learned while using a vendored copy come back here
as history entries.

Retired skills: og-run-preflight (now part of og-run), calibration-provenance (now
og-country-calibration's provenance reference), og-analysis-studio (now og-scenario-report);
og-repo-fleet-sync left this set. og-clews-linked-run moved to MUIOGO-AI.
