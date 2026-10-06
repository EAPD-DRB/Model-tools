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
directory into their configured Codex skills folder; every CLEWs skill ships
`agents/openai.yaml` with Codex interface metadata.

**Each skill directory is self-contained.** Copy one directory and it works, in
Claude or in Codex — no sibling directories required, no repo checkout needed.
Rules shared between skills are vendored into each skill's `references/` rather
than linked across directories, because a cross-directory link breaks the moment
a skill is installed on its own.

## Shared spine

`shared/` is the **editable source** for rules that several skills depend on. A script
that one skill owns can also be a source, when a second skill needs it verbatim. Never
edit a vendored copy — it carries a generated-file banner and is overwritten:

```bash
python scripts/sync_shared.py          # propagate an edit to every dependent skill
python scripts/sync_shared.py --check  # fail if a copy has drifted
```

Run `--check` before committing a change to a source below. This is what keeps one rule
from forking into six divergent copies again.

- [`shared/non-forcing.md`](shared/non-forcing.md): the non-forcing boundary and the one
  wording of the counterfactual test.
- [`shared/provenance/`](shared/provenance/SCHEMA.md): the canonical six-table provenance
  schema, worked example templates, and the single validator (`provenance.py`).
- [`clews-model-review/audit.py`](clews-model-review/audit.py): the structural checker and
  the `--removable` gate. Owned by `clews-model-review` and vendored into
  `clews-model-fix`, whose only hard gate is that flag — so the fast path works when it is
  the one skill installed.

## Choosing a skill

- Use `build-clews-model` to create the initial solved CLEWs Global country model.
- Use `calibrate-clews-model` to replace generic or weak inputs with better country data,
  repair disconnected systems, add physical stocks and constraints, and maintain complete
  source/calculation/assumption provenance.
- Use an `add-*` skill for a specialized sector package it explicitly covers.
- Use `clews-model-fix` only for edits that cannot change any model value.
- Use `assess-clews-calibration` to grade an existing model.

The A/B/C value in `CHANGES.csv` is administrative chronology, not a workflow selector. The
non-forcing counterfactual test still applies to every parameter: *would this exact change still
be made if no historical outcome were known?* If not, do not promote it as country calibration.

## Available skills

- [`add-fisheries-sector`](add-fisheries-sector/SKILL.md): build a complete,
  source-traceable, non-forcing Fisheries sector in an existing solved country
  model.
- [`add-environmental-accounting`](add-environmental-accounting/SKILL.md): add
  auditable water and land accounting to a CLEWS model.
- [`assess-clews-calibration`](assess-clews-calibration/SKILL.md): assess
  technical validity, historical adequacy, forcing, evidence, and fitness for
  purpose.
- [`calibrate-clews-model`](calibrate-clews-model/SKILL.md): refine a solved basic
  CLEWs Global country model with better sourced national data, physical stocks and
  constraints, connectivity repairs, complete schema-ledger provenance, and integrated
  solve/diagnostic gates.
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
- [`og-multi-industry-calibration`](og-multi-industry-calibration/SKILL.md):
  build a multi-industry OG-Core calibration from a SAM or IO tables and keep it
  consistent with the single-industry model.
- [`og-scenario-report`](og-scenario-report/SKILL.md): turn a finished OG-Core
  baseline-vs-reform run into the standard deliverable.
- [`pull-handoff`](pull-handoff/SKILL.md): update the Fiji, Philippines, and
  Model-tools repositories and install the latest MUIO cases.
- [`push-handoff`](push-handoff/SKILL.md): package, document, commit, and push
  Fiji and Philippines model handoffs.
