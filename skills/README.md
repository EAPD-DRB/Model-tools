# skills/

Skills that package instructions for a repeatable task (e.g. the OG country
calibration skill). One directory per skill, each with its own `SKILL.md`.

## Installing a skill

Copy the skill's directory into your Claude skills folder, then restart Claude
Code (or reload the window) so it's picked up:

- **Personal** (available in every project): `~/.claude/skills/`
- **Project** (shared via a repo): `<repo>/.claude/skills/`

For example, to install `og-country-calibration` for your own use:

```
cp -r skills/og-country-calibration ~/.claude/skills/
```

Claude discovers it by the `name` and `description` in the `SKILL.md`
frontmatter — no other registration needed. Codex users can copy the same
directory into their configured Codex skills folder; skills that include
`agents/openai.yaml` also expose Codex interface metadata.

## Shared spine

`_shared/` holds the rules that several skills depend on. State them there, link to them
from a skill, and never copy them into one:

- [`_shared/non-forcing.md`](_shared/non-forcing.md): the non-forcing boundary and the one
  wording of the counterfactual test.
- [`_shared/provenance/`](_shared/provenance/SCHEMA.md): the canonical six-table provenance
  schema, worked example templates, and the single validator (`provenance.py`).

## Choosing a skill: size the ceremony to the change

| Class | Test | Skill |
|---|---|---|
| **A — structural** | No parameter value changes, no source data changes | `clews-model-fix` |
| **B — sourced change** | A number changes, chosen *without* reference to an observed outcome | `calibrate-clews-model` / `add-*`, with provenance |
| **C — calibration** | A value chosen *with reference to* an observed outcome | `calibrate-clews-model`, full plan |

The discriminator is the counterfactual test: *would this exact change still be made if no
historical outcome were known?* The evidence a change requires scales with what the change
can affect, not with the importance of the model.

## Available skills

- [`add-fisheries-sector`](add-fisheries-sector/SKILL.md): build a complete,
  source-traceable, non-forcing Fisheries sector in an existing solved country
  model.
- [`add-environmental-accounting`](add-environmental-accounting/SKILL.md): add
  auditable water and land accounting to a CLEWS model.
- [`assess-clews-calibration`](assess-clews-calibration/SKILL.md): assess
  technical validity, historical adequacy, forcing, evidence, and fitness for
  purpose.
- [`calibrate-clews-model`](calibrate-clews-model/SKILL.md): implement
  equation-led, non-forcing, source-traceable calibration changes with
  deterministic pre-solve and bounded runtime gates.
- [`build-clews-model`](build-clews-model/SKILL.md): build and package an
  uncalibrated country CLEWS model.
- [`clews-model-fix`](clews-model-fix/SKILL.md): make a structural fix that
  cannot change a solved value — remove unreferenced objects, fix descriptions,
  adjust technology groups. **Start here for small changes.**
- [`clews-model-review`](clews-model-review/SKILL.md): review structure and data
  consistency; also gates whether an object is safe to delete (`--removable`).
- [`fable-mode`](fable-mode/SKILL.md): apply a disciplined evidence, execution,
  and verification loop.
- [`og-analysis-studio`](og-analysis-studio/SKILL.md): free-form OG-Core scenario
  design, result interrogation, and bespoke figures.
- [`og-country-calibration`](og-country-calibration/SKILL.md): calibrate or
  refine an OG-Core country model.
- [`og-scenario-report`](og-scenario-report/SKILL.md): turn a finished OG-Core
  baseline-vs-reform run into the standard deliverable.
- [`pull-handoff`](pull-handoff/SKILL.md): update the Fiji, Philippines, and
  Model-tools repositories and install the latest MUIO cases.
- [`push-handoff`](push-handoff/SKILL.md): package, document, commit, and push
  Fiji and Philippines model handoffs.
