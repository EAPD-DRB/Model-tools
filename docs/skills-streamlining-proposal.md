# Proposal: streamline the CLEWs/MUIO skills

**Status:** IMPLEMENTED 2026-07-29 (see `## 9. What shipped`). **Date:** 2026-07-29.
**Scope:** the six CLEWs/MUIO skills plus the two handoff skills (~48,800 of the repo's
62,000 skill words). OG skills and `fable-mode` excluded.

## In plain terms

The skills currently work by **telling the model to read a lot of instructions and then
promise it checked everything**. That has three costs. A one-minute
job inherits the ceremony of a six-month one. Instructions have to be re-read from
scratch every single session, so they are a bill you pay forever. And a promise cannot stop a
bad delivery — only a script that refuses to finish can do that.

So the proposal is not "check fewer things." It is:

> **Write each rule once, put the evidence in one set of tables, and let a script be the thing
> that says no.**

Four things went wrong, and they compound:

1. **Nothing has a sense of proportion.** Ask to delete a technology that is connected to
   nothing — a one-minute job — and a skill fires that demands a completed calibration plan,
   an unchanged control run, an A/B test and a checksum register before you are allowed to
   solve. There is no "this is a small change" path anywhere in the six skills, so every
   request, however small, takes the heavy route. **This is the problem to fix first.**
2. **The same rule is written in many places.** The "don't tune the model to match history"
   rule appears in six files, in three different wordings. Those wordings can drift apart, and
   they already have. Same for a dozen other rules.
3. **The paperwork grew until it squeezed out the parts that matter.** The table that is
   supposed to answer *"where did this number come from?"* has a column for a file fingerprint
   but **no column for the page or table number**. And the assumptions table has nowhere to
   write the actual number — you can record "we assumed vessel utilization is moderate" but
   not "0.42".
4. **Most of the fingerprint checks don't check anything.** A checksum is a fingerprint of a
   file, useful for spotting that a file you don't control has changed. But nine of them here
   either only verify the fingerprint is *the right shape* without ever opening the file
   (writing 64 zeros passes — the test file does exactly that), or fingerprint a file the
   script itself created seconds earlier, or re-fingerprint files already inside a bigger
   archive that is also fingerprinted. Exactly one is doing real work.

Fixing all four makes the skills about **70% cheaper to run and gives you *better*
traceability than today**, because the missing columns get added and the two rival table
formats become one.

Nothing below reduces traceability. Data lineage gets **stricter** (the missing columns are
added, the two rival schemas become one) and change lineage gets **stricter** (a new
`CHANGES.csv` records every change with its triage class, machine-checked). What gets deleted
is duplication, dead checksums and re-runs.

---

## 0. The two axes

The fixes fall into two groups. Most help both, but the ordering depends on which pain you
care about, and **waiting time and tokens are not fixed by the same things.**

### Saving waiting time — ranked by how much time

| Fix | Saves | Move |
|---|---|---|
| `clews-model-fix` + triage + negative description clauses | **30 min → 1 min** on every small change. The daily pain. | 0 |
| Re-solve only when a model value actually changed | **hours per country build** — today a citation fix mandates re-solving every scenario | 5 |
| Bound the fix-and-rerun loops | removes open-ended retry; 1 of ~8 loops has a cap today | 5 |
| Collapse 6 validator passes to 3 | under a minute per delivery, but free | 3 |

### Saving tokens — ranked by how much context

| Fix | Saves | Move |
|---|---|---|
| `clews-model-fix` is small by design | the common case loads **~600 tok** instead of 2,200 (`calibrate`) or 13,400 (`build`) | 0 |
| Stop the 10 mandatory reference reads; load at the branch | **~8,400 words** off `build-clews-model` | 2 |
| Trim the two largest SKILL.md files to ~120 lines | ~5,000 words | 2 |
| One provenance schema, one validator | ~2,600 words of prose + ~1,000 lines of duplicated Python | 1 |
| Rewrite the 8 descriptions | **~450 tok every session, forever** | 5 |
| One copy of the no-forcing rule | 6 prose + 3 code copies → 1 + 1 | 5 |

**Move 0 is the only fix at the top of both lists.** It is half a day's work, it is independent
of everything else, and it is where I would start.

---

## 1. What the current overhead costs

| | Measured |
|---|---|
| Always-on frontmatter tax | **594 words (~790 tok)** across 8 in-scope descriptions, paid every session whether a skill fires or not; 6 of 8 exceed 40 words |
| `build-clews-model` on fire | **10,059 words (~13.4k tok)** — it mandates reading 10 reference files *before step 1* |
| `add-environmental-accounting` on fire | **7,264 words (~9.7k tok)** across only 3 files |
| `add-fisheries-sector` on fire | **4,986 words (~6.6k tok)** |
| Distinct checks across 17 scripts | **277** (~3,500 lines) |
| `validate_provenance.py` executions per delivery | **6**, for 3 real checkpoints — ~225 redundant check executions, every evidence hash and 3 tree hashes recomputed each pass |
| Prose completion gates in `build-clews-model` | **33**, on top of 107 workflow sub-bullets, and most restated in code as well |
| Provenance schemas | **2 incompatible ones**; the two assumption registers share exactly one column (`assumption_id`) |
| Register burden | **147 columns across 12 CSV templates, 0 worked example rows** |
| Duplicated validator code | **~1,000 lines** (two `validate_provenance.py` that cannot read each other's files) |
| Imperative density | `add-environmental-accounting`: one must/never/verify every **3.5 lines** |

### The mechanism: a four-day ratchet

`build-clews-model/SKILL.md` grew **136 → 460 lines** and **0 → 33 completion gates** between
2026-07-24 and 2026-07-28. The whole `skills/` tree went 30,297 → 62,008 words in the same
window. Every commit added rules; none removed any. The commit verbs name it: *Add* →
*Expand* → *strengthen* → *enforce*.

## 2. The overhead has cost traceability, not bought it

This is the part that matters most, because traceability is the requirement worth protecting.

**2.1 The primary source ledger cannot answer the trace question.**
`assets/country-package/data_sources/SOURCES.csv.tmpl` — the scaffold every new country
model gets — has 21 columns including `sha256`, `review_owner`, `national_alternative`,
`selection`, `transformation`, `status`, `quality`, `proxy`. It has **no `exact_locator` and
no `access_date`**. You can record a 64-character checksum of a PDF but not which page or
table the number came from. The repo's own standard
(`add-fisheries-sector/references/source-traceability.md:31`) says a URL without a table,
page, sheet, cell, or query **is not sufficient**. Twenty-one columns of ceremony crowded
out the two that deliver the requirement.

**2.2 The assumption ledger cannot store an assumption's value.**
`ASSUMPTIONS.csv.tmpl` has 7 columns: `assumption_id, sector, description, used_for, status,
source_or_reason, review_need`. None holds a number or a unit. "Vessel utilization = 0.42"
can be *described* but not *recorded*. The fisheries sibling has `central_value`,
`lower_bound`, `upper_bound`, `unit` — so the two ledgers cannot be reconciled, and the one
used for country builds is the weaker of the two.

**2.3 The hash apparatus is mostly decorative, and its tests say so.**
Of the whole hashing apparatus, **exactly one hash guards a plausible failure mode**: the
post-freeze tree hashes at `build-clews-model/scripts/validate_provenance.py:298-312`, which
catch edits to a package already declared complete. Everything else is format-only string
validation, a hash of a file the same process just wrote, or a re-hash of content already
inside an enclosing hash. Specifically:

- `calibrate-clews-model/scripts/validate_calibration_plan.py:246-254` checks that
  `precision_inputs[].sha256` is 64 hex characters and **never opens `item["path"]`**. Its
  test (`test_validate_calibration_plan.py:45`) sets `sha256 = "0" * 64` and asserts
  promotion returns **zero errors**. The test encodes that fake hashes pass.
- `validate_provenance.py:581-587` requires `importer_sha256`,
  `parameter_registry_sha256`, `formulation_sha256` to be hex and never compares them to the
  importer, registry, or formulation they claim to fingerprint. The scaffold ships all three
  as `null`, so a human types 64 characters once and the gate passes forever.
- `freeze_raw_baseline.py:149` hashes a ZIP it created 13 lines earlier. The ZIP embeds
  mtimes, so the hash can never confirm a rebuild matches.
- `freeze_raw_baseline.py:174-182` and `validate_provenance.py:318-326` hash three files that
  are already inside both the tree hash and the hashed ZIP — triple coverage.
- `estimate_residual_capacity.py:190` writes `input_sha256`; nothing in the repo reads it.
- `add-fisheries-sector/scripts/validate_provenance.py:195-197` format-checks a `sha256`
  column that is not even in its required-column set.

**2.4 A duplicated audit re-introduced a bug the original documents.**
`clews-model-review/audit.py:42-49` parses complete JSON scalars, with a docstring
explaining that regex-over-serialized-text truncates IDs like `TEC_envland_v12` to
`TEC_envland`. `assess-clews-calibration/scripts/audit_muiogo_model.py:147` then does
regex-over-serialized-text. The copy is the buggier one. Six to seven of its ~12 checks are
copied from `audit.py`, including identical `SECTOR_CODES` and placeholder-string constants.

**2.5 Six cross-referenced skills do not exist.**
`muiogo-provision`, `muiogo-run`, `muiogo-scenarios`, `muiogo-analyze`, `muiogo-explain`,
`calibration-provenance`. The "These live in the MUIOGO-AI collection" escape-hatch footer is
duplicated across 10 files and is doing a lot of load-bearing work.

## 3. Where the overhead is, by kind

**Prose restatement.** The no-forcing rule is stated 6 times across 6 files. The
counterfactual test is written 3 times in 3 different wordings — so they can now drift. The
`TAL == TAU` prohibition appears in 8 prose locations *and* 3 separate code implementations
(`audit_no_forcing.py:51-70` over CSVs, `audit_fisheries_freedom.py:212-213` over JSON,
`audit_muiogo_model.py:71` again). "Case JSON is source, never hand-edit generated files"
appears 4 times. The baseline/control-run preflight appears 4 times. Portable packaging
appears 4 times. The `SOURCES.csv` column list is restated as prose in 3 further files beyond
the template itself.

**Fake conditionality.** `build-clews-model/SKILL.md:57-80` frames 10 reference reads as
"read X before doing Y" — but every Y is a step in the *mandatory* 16-step workflow, so all
10 always load. The conditional framing buys sequencing and nothing else.

**Triple encoding.** The norm, not the exception: *no-forcing audit clean* is stated at
`SKILL.md:46` (workflow), `SKILL.md:392` (gate list), and `validate_delivery.py:126-128`
(code). Same for provenance coverage, baseline-manifest match, and the reserve-margin
`CURRENT` check. `calibrate-clews-model` encodes its gates three times: SKILL.md prose, the
`gates` keys in `calibration-plan.template.json`, and `validate_calibration_plan.py`.
`clews-model-review/SKILL.md:77-79` explicitly instructs keeping its rubric and `audit.py` in
sync **by hand**.

**Within-skill duplication.** `build-clews-model` restates the MUIO import workflow 3× —
`references/muio-import.md`, `references/import-quality-gates.md`, and `SKILL.md:240-299` —
with the parity-class table printed twice and the `validation_summary.json` skeleton printed
verbatim twice. The 7 handoff documents are enumerated in `SKILL.md` (3×), in
`provenance-and-layout.md`, and in `handoff-templates.md`, while
`assets/country-package/documentation/*.tmpl` already contains all 7 as real templates.

**Unbounded loops.** No skill bounds the number of fix-and-rerun cycles. The worst is
`source-traceability.md:289-296`: replacing **one citation** triggers "regenerate and solve
all scenarios; rerun the policymaker trace test." Others: "rerun the publisher after every
solve" (3× in `add-environmental-accounting`), "re-run technical/no-forcing checks"
(`build-clews-model:335`), "re-run the resource estimate" (`:320`), "run result parity again
after any formulation workaround" (`muio-import.md:165`), "re-run provenance validation and
the freedom audit" (`add-fisheries-sector:181`), and "resolve every failure" / "resolve every
error before solving" with no iteration budget. `calibrate-clews-model`'s "stop near twice
the known-good runtime" is the **only** cap anywhere in the cluster.

**Regenerate-everything.** `add-environmental-accounting:157-160` requires appending
"complete default parameter rows across all years, timeslices, modes, and scenarios" and
"densify every mode-indexed JSON family"; `:182` regenerates "every saved case/scenario
combination"; `:195` verifies 10 identities "for every case, region, and year".

**Informational checks counted as gates.** `audit_environmental_model.py` (516 lines) and
`compare_history.py` always exit 0. `clews-model-review/audit.py` gates on 4 of its 19
finding types. `audit_muiogo_model.py` self-labels heuristic. Presenting these as enforcement
overstates the gate.

**The handoff skills stack invisibly.** `push-handoff:39` says "Run the repository's
documented validation chain" — that is `MUIOGO-AGENT.md`'s 9-step chain, whose step 9 is
"Regenerate and revalidate the live case." A `push-handoff` invocation is nominally 10 + 9 + 9
gates, and its heaviest step is the unspecified one.

## 4. What must survive

Non-negotiable. Any streamlining that loses one of these is a failure:

1. **The lineage chain.** Every populated model value → one parameter/map row → a source
   and/or calculation and/or assumption → an exact locator. Four hops, machine-checkable.
2. **Exact locators.** Page, table, sheet, cell, dataset variable, API query — not a bare URL.
3. **Access dates and editions** for anything behind a mutable URL.
4. **Assumption values with units** and, where sensitivity-tested, bounds.
5. **Evidence grades A–D**, describing evidence strength, not permission.
6. **Explicit proxy labelling**: source→target, rationale, and which national agency could replace it.
7. **Registered gaps.** Missing lineage recorded as a documented gap — never left blank, never
   turned into a precise zero.
8. **The no-forcing boundary and the counterfactual test** — "would this exact change still be
   made if no historical outcome were known?" That single line is the best thing in the repo.
   It should exist in exactly one place.
9. **Code version pins + external data checksums**, because code pins do not freeze data
   behind mutable URLs.
10. **Separately reported statuses** (`upstream_raw` / `muio_import` / `muio_final`) — a later
    solve must not be able to hide an earlier import failure.
11. **The upstream drift diff** (`audit_no_forcing.py:277-301`) — the only check in the repo
    that compares against ground truth rather than a self-declared record.
12. **A sampled trace test**, run before delivery, result recorded as pass/fail.

## 5. The proposal — six moves

### Move 0: size the ceremony to the change

This is the move that fixes the day-to-day experience, and it is the cheapest one.

**The symptom.** "Remove this technology, it isn't connected to anything." That is a
one-minute job. What happens instead: `calibrate-clews-model` matches — its description says
"Use when changing stocks, residual capacity, lifetimes, turnover, demand … resource limits,
or historical constraints" — and its **mandatory design gate** (`SKILL.md:12-37`) then requires,
*before the first solve*:

1. a completed copy of the 144-line `calibration-plan.template.json`;
2. every observation classified into one of four categories;
3. every changed parameter mapped to its JSON file, formulation equations, generated-data
   representation and physical effect;
4. explicit technology roles;
5. **full-precision initialization inputs and their checksums** — the same checksum whose test
   asserts that 64 zeros pass (§2.3);
6. an unchanged control run, a last-known-good runtime, a candidate time budget and a minimal
   A/B strategy;
7. `validate_calibration_plan.py --stage design` passing.

Followed by "Do not run a full optimization while this gate fails." For deleting an object
that is connected to nothing.

**Why it happens.** Three causes, all fixable:

- **No skill owns small structural fixes.** `clews-model-review` *finds* dangling technologies
  but only audits — it cannot edit. So the nearest skill that changes a model is
  `calibrate-clews-model`, the heaviest one in the repo. The model reaches for it because
  there is nothing else.
- **No skill has a fast path.** The only proportionality rule in the entire repo is in
  `fable-mode` (`:199`, "Don't apply it to trivial work. Forcing all five gates onto a
  two-minute edit is its own failure") — a skill outside this scope. None of the six CLEWs
  skills has any notion of a small change.
- **No description says when *not* to fire.** They are keyword-stuffed for recall, so they
  over-match. Three skills match a request to remove a dangling technology.

**The fix: one triage question, asked first, using a test the repo already has.**
`build-clews-model:382` already asks the right question — it just uses it as a philosophical
afterthought instead of as routing:

> Would this exact change still be made if no historical outcome were known?

Wire it to three paths:

| Class | Test | Ceremony |
|---|---|---|
| **A — structural cleanup** | No parameter value changes and no source data changes | Verify the precondition with the existing audit, make the change, re-run the audit, one line in `HISTORY.md`. **No plan, no registers, no checksums, no A/B, no re-solve.** |
| **B — sourced parameter change** | A number changes, chosen *without* reference to an observed outcome | Provenance applies: `SOURCES`/`CALCULATIONS`/`ASSUMPTIONS` + a `MODEL_MAP` row. Re-solve, because a number changed. **No calibration plan.** |
| **C — calibration** | A value was chosen *with* reference to an observed outcome | The full plan, gates, control and A/B. This is what `calibrate-clews-model` is for. |

For the dead technology the answer is trivially "yes, obviously" → Class A.

#### The precondition that makes Class A safe

"No input and no output activity ratio" is **not** a sufficient test. A technology with no IAR
and no OAR can still carry a capital cost plus a `TotalAnnualMinCapacity` bound, or a UDC
coefficient — and then deleting it *does* change the objective. The sound test is stronger:

> The ID appears **nowhere in the model data except its own definition row** — no activity
> ratio, no cost, no bound, no emission ratio, no UDC coefficient, no constrained group.

That test is already implemented, in one line, in a script that already exists.
`clews-model-review/audit.py:96-105` collects every ID referenced across **every** `*.json` in
the case except `genData.json` — which includes the `*Cn.json` UDC files, cost rows and bounds
— and `:116` computes `set(techs) - used_tid`, "technologies defined but never referenced in
data". It is currently only a `WARN`. **`clews-model-fix` promotes it to the gate.**

When that gate passes, no re-solve is needed to prove the result unchanged: nothing in the
model referenced the object, so no constraint and no objective term contained it. If a
deliverable needs regenerated artifacts, regenerate and assert the objective is **identical** —
but that is a packaging step, not a verification step.

#### `clews-model-fix` — the new skill

One file, ~60 lines, no `references/`, no new checking logic. Draft description (28 words):

> Make a structural fix to a MUIO/OSeMOSYS CLEWs model that cannot change any solved value:
> remove unreferenced technologies, commodities or emissions, fix placeholder descriptions,
> adjust technology groups. Refuses anything that alters a parameter value.

**In scope (Class A only):** delete an unreferenced `TEC_`/`COM_`/`EMI_`; delete an orphaned or
stranded commodity; replace a placeholder description; add or change a `TECHGROUP` assignment
(`build-clews-model:243` already states grouping is interface metadata that must not alter
parameters); add a time-set description; correct a cosmetic label.

**Out of scope — the skill must stop and name the right skill:** any change to a numeric
parameter value (→ Class B); deleting an object that *is* referenced (→ Class B/C, because the
solution changes); a unit correction that implies a conversion (→ Class B, it is a calculation);
anything chosen by looking at a historical outcome (→ Class C, `calibrate-clews-model`).

**The whole procedure:**

```bash
python audit.py MODEL          # gate: the ID must be in "defined but never referenced"
# make the edit
python audit.py MODEL          # confirm the ID is gone and no new findings appeared
```

**Target: under a minute.** No calibration plan, no checksums, no control run, no A/B, no re-solve.

#### What the fast path still records — traceability is not reduced, it is relocated

A Class A change is fast **because there is no data lineage to record**, not because recording
was skipped. Deleting an unreferenced object introduces no source, no calculation and no
assumption — so `SOURCES`, `CALCULATIONS` and `ASSUMPTIONS` are correctly untouched. The
lineage invariant is *"every populated model value traces to a row"*, and a removed object
populated nothing. The registers stay complete by construction, and the validator proves it.

What must still be recorded in full, and is **stronger than today**:

| Ledger | Class A obligation |
|---|---|
| `CHANGES.csv` | **Mandatory.** One row: `change_id`, date, `class=A`, what was removed, the audit output path proving the precondition held, `resolve_status=objective_unchanged`, author, commit. |
| `MODEL_MAP.csv` | If the deleted object had a map row, mark it **superseded** by the `change_id` — never delete the lineage. Existing rule (`source-traceability.md:298`): never make an earlier model version unreconstructable. |
| `documentation/HISTORY.md` | One dated line pointing at the `change_id`. |
| Audit output | Retained as the evidence artifact — the before/after runs *are* the proof, so they are worth keeping and cost nothing extra. |

`CHANGES.csv` is the one genuinely new artifact in this proposal, and it closes a loophole that
exists today: recording the **triage class on every change** makes the proportionality itself
auditable. Anyone can later verify that every change routed through the fast path really was
Class A — and a Class B change quietly pushed through it becomes a visible provenance failure
rather than an invisible one. Today "all the changes done" lives in free-text `HISTORY.md`
with no class, no evidence pointer and no machine check.

Add one rule to the shared validator: **every `CHANGES.csv` row with `class=A` must name an
audit artifact, and no `class=A` row may reference a `MODEL_MAP` row that is still active.**
That is the whole enforcement, and it is a dozen lines of Python.

#### The rest of Move 0

- Put the triage table at the top of `calibrate-clews-model` and
  `add-environmental-accounting`, with an explicit exit: *if Class A, stop and use
  `clews-model-fix`.*
- Add a negative clause to every heavy description. For `calibrate-clews-model`: "**Not** for
  structural cleanup, dead-object removal, descriptions, or technology grouping — use
  `clews-model-fix`."
- State the proportionality rule once, in the shared spine: **the evidence required scales
  with what the change can affect, not with the importance of the model.**

### Move 1: one provenance schema, one validator

Create `skills/shared/provenance/` holding **one** `SCHEMA.md` (one page), **six** CSV
templates, and **one** `provenance.py`. Every skill points at it; none redefines it.

| File | Columns | Purpose |
|---|---|---|
| `SOURCES.csv` | 13 | `source_id, provider, product, edition, reference_period, geography, variable, source_unit, exact_locator, url, access_date, license, sha256` |
| `CALCULATIONS.csv` | 9 (+2) | `calculation_id, formula, source_ids, assumption_ids, input_calculation_ids, input_values, input_units, output_value, output_unit` (+ `script_path, script_version` when code produced the number) |
| `ASSUMPTIONS.csv` | 5 (+3) | `assumption_id, statement, central_value, unit, evidence_source_ids` (+ bounds only where sensitivity-tested) |
| `MODEL_MAP.csv` | 10 | `map_id, model_file, parameter, entity, mode, scenario, years, value_or_expression, model_unit, evidence_ids` — row-granular, replacing both `MODEL_DATA_MAP.csv` and `parameter-register.csv` |
| `GAPS.csv` | 3 | `item, why_absent, upgrade_source` — the only irreducible content of `completeness-register.csv` |
| `CHANGES.csv` | 10 | `change_id, date, class, description, model_objects, evidence_path, map_rows_affected, resolve_status, author, commit` — **new.** Every change to the model, with its triage class. See Move 0. |

**147 columns / 12 templates / 2 validators → ~50 columns / 6 templates / 1 validator.** And
this *adds* `exact_locator`, `access_date`, `central_value`, `unit` — closing §2.1–2.2.

Retire as derivable, or as workflow state rather than lineage:

- `policymaker-trace-test.csv` — a test transcript carrying zero lineage; its `model_location`
  / `model_value` / `model_unit` are copied from the parameter register and the rest are
  reviewer checkboxes. Record pass/fail and the sample IDs in the delivery note.
- `completeness-register.csv` — 8 of 10 columns duplicate the parameter register
  (`status` *is* `evidence_type`; `parameter_record_ids` is the reverse foreign key). Only the
  `data_gap` / `not_applicable` rows are new information → `GAPS.csv`.
- `boundary-register.csv` — becomes `CALCULATIONS` rows tagged `boundary_correction` plus
  `GAPS` rows for excluded flows. Only `origin_statistical_sector` is genuinely new.
- `residual-capacity-input.csv` — a script input, not a register. Reference it from
  `CALCULATIONS.script_path` / `input_values`.
- `SOURCES.selection` / `.transformation` / `.proxy` — three columns that silently
  re-implement `CALCULATIONS` and `ASSUMPTIONS`, and the likeliest place for the two
  representations to diverge.

Keep the government-review table if the project needs it, but keep its columns
(`review_owner`, `national_alternative`, `review_need`, `review_status` — currently spread
across four files) **out of the lineage schema**. It is a stakeholder workflow, orthogonal to
trace.

The whole requirement reduces to one invariant both existing validators already know how to
check (`validate_provenance.py:414-499`, `add-fisheries-sector/scripts/validate_provenance.py:150-271`):

> Every populated model value resolves to exactly one `MODEL_MAP` row; every `MODEL_MAP` row
> carries at least one of `source_ids` / `calculation_id` / `assumption_ids`; every referenced
> ID resolves; every retained evidence file matches its `sha256`.

**The validator is the load-bearing artifact; the eight registers are the ceremony.**

**Ship 2–3 worked example rows per template.** All 12 templates are currently header-only —
asking an analyst or an agent to populate 147 columns with no example of a correct row. This
is the single cheapest fix in the proposal and probably the highest-yield.

Keep from the fisheries validator, which the build one lacks: **calculation dependency cycle
detection** (`:316-334`) and the **evidence-type ↔ lineage consistency** rules
(`direct` → needs `source_ids`; `derived`/`proxy`/`estimated` → needs `calculation_id`).

### Move 2: SKILL.md is the procedure; references load at the branch

Cap each `SKILL.md` at **~120 lines**: the procedure, the boundary rule, the exit criteria.
Delete the up-front "Read these 10 files" block — a reference is named *by the step that needs
it*, and only when that step's branch is actually taken.

- `build-clews-model`: 460 → ~120 lines. Merge `muio-import.md` + `import-quality-gates.md`
  (they duplicate the capability inventory, the 31-char worksheet gate, the parity taxonomy
  and the expansion gate). Delete `handoff-templates.md` and
  `source-and-government-review.md`, whose content already exists as real templates in
  `assets/country-package/**`. Fold `non-forcing-rules.md` into the single shared copy (Move 5).
  That is 11 reference files → 5.
- `add-environmental-accounting`: 278 → ~120 lines. Its `muio-json-workflow.md` is 3,104 words
  on its own; move the 26-item structural validation list into the validator and keep the
  reference for the JSON family patterns.
- `add-fisheries-sector`: fold `source-traceability.md` into the shared provenance schema —
  it is the best-written traceability doc in the repo and should become the canonical one,
  minus the six-register apparatus.

### Move 3: gates live in code, stated once

Delete every prose gate a script already enforces. Keep prose only for gates a script
*cannot* check — the judgment calls. In `build-clews-model` that is roughly **33 → 6** prose
gates, with the rest surviving as the validator's exit code.

Collapse the six `validate_provenance` executions to **three real checkpoints** —
`scaffold`, `build`, `delivery`:

- `SKILL.md:348` (`--stage build`) duplicates `:226`; and `freeze_raw_baseline.py:87` already
  runs the build stage internally.
- `SKILL.md:353` (`--stage delivery`) and `:354` → `validate_delivery.py:109` are back-to-back
  invocations of the identical code path, including a full re-hash of every evidence file and
  three directory trees. The portable ZIP gets `testzip`'d twice in the same run
  (`validate_provenance.py:266` and `validate_delivery.py:195`).
- `SKILL.md:429-430` restates both inside the gate list.

Collapsing these removes ~90 redundant check executions per delivery with **zero loss of
coverage**.

Deduplicate the scripts: **17 / ~3,500 lines → ~9**. Merge `audit_muiogo_model.py` into
`clews-model-review/audit.py`, keeping the correct JSON-scalar parser (§2.4) — that alone
removes 6-7 duplicated checks and a bug. Unify the three `TAL == TAU` implementations into one
bound-lock checker the three callers share. Import `sha256_file` / `tree_hash` /
`selected_tree_hash` from one module — they are byte-identical in
`validate_provenance.py:152-193` and `freeze_raw_baseline.py:18-66`, despite the latter
already importing from the former. Fifteen of `validate_delivery.py`'s 21 required-file checks
duplicate `validate_provenance.py:81-98`.

Fix while in there: `validate_delivery.py:177-185` asserts nine substrings in lowercased
prose, where `"import"` is satisfied by the word *important*. `:35-37` checks that copies of
the validators themselves were copied into the package. `estimate_resources.py:288` emits a
warning unconditionally, and writes `"actual": {all None}` which `validate_delivery.py:168-173`
then requires be non-None — a gate satisfied by typing any number.

### Move 4: hash only across a trust boundary

**Keep** exactly three uses:

1. Post-freeze tree hashes (`validate_provenance.py:298-312`) — catches edits to a package
   declared complete. The one defensible hash in the codebase.
2. Checksums of **externally downloaded data** — mutable URLs, licensing, restricted access.
   This is item 9 of §4 and is genuine traceability.
3. Archive integrity (`testzip`) on the portable ZIP — **once** per run, not twice.

**Delete** the six patterns in §2.3: format-only checks that never open the file; hashes of
files the same process just wrote; re-hashes of content already inside an enclosing hash;
write-only hashes with no readers; hash columns absent from the required set. For code, use
the version pins and `git diff` — that is what they are for. Either make the three MUIO
checksums real (compute and compare them against the installed importer, registry and
formulation) or drop them; shipping them as `null` behind a format check is the worst of both.

Update `test_validate_calibration_plan.py:45`, which currently asserts the broken behavior —
otherwise the test will fight the fix.

### Move 5: single-source the rules, and bound the loops

- **One copy of the no-forcing rule**, in `skills/shared/non-forcing.md`, with **one**
  wording of the counterfactual test. Five skills link to it. Three wordings in three files is
  a drift hazard, not redundancy. Keep the three code implementations collapsed to one shared
  checker (Move 3).
- **Replace "re-run everything" with "re-run what the change touched."** Concretely, retire
  `source-traceability.md:289-296`: a changed citation should invalidate the affected
  `MODEL_MAP` rows and require a re-solve **only if a model value changed**. Recording a
  better locator for the same number must not trigger a multi-scenario re-solve.
- **Put an iteration budget on every fix-and-rerun loop.** Generalize
  `calibrate-clews-model`'s "stop near twice the known-good runtime", which is currently the
  only cap in the cluster. Give "resolve every failure" an explicit cycle limit after which it
  reports rather than retries.
- **Scope the trace sample.** `source-traceability.md:255-256` reads "at least ten populated
  model values, or 10% when fewer than 100" — the 10% wording invites unbounded manual
  reconstruction on a large model. Fix it at ten, drawn to cover the ten evidence categories
  already listed.
- **Rewrite the 8 descriptions**: 594 → ~254 words, saving ~450 tokens *per session,
  permanently*. Drop the keyword-stuffed "or" chains; state the task and the nearest
  alternative skill. Worst offender, `build-clews-model`, 120 → 37 words:

  > Build a new uncalibrated OSeMOSYS/CLEWs country model from CLEWs Global and package it as
  > a solved, source-traceable MUIO case. Use for new country builds, GeoCLEWs adaptation,
  > otoole/MUIO import, or delivery packaging — not for calibration.

- **Fix the dangling skill references** (§2.5): replace the six absent `muiogo-*`
  cross-references with either real skills or a single line in `skills/README.md`. Also
  un-hardcode the case names in `push-handoff:17-19` (`Fiji_v2`,
  `Philippines_v12_ENV_LAND_WATER_DIAGNOSTIC`) — a version bump silently invalidates the
  skill; point at `muio/README.md` as `pull-handoff` step 2 already does.

## 6. Before / after

| | Now | Target |
|---|---|---|
| Frontmatter tax (every session) | 594 words / ~790 tok | ~254 words / ~340 tok |
| `build-clews-model` on fire | 10,059 words / ~13.4k tok | ~2,400 words / ~3.2k tok |
| `add-environmental-accounting` on fire | 7,264 words / ~9.7k tok | ~2,200 words / ~2.9k tok |
| `add-fisheries-sector` on fire | 4,986 words / ~6.6k tok | ~1,800 words / ~2.4k tok |
| Provenance templates / columns | 12 / 147 | 6 / ~50 |
| Provenance validators | 2 (incompatible, ~1,000 dup lines) | 1 |
| Worked example rows | 0 | 2–3 per template |
| Validator scripts | 17 / ~3,500 lines | ~9 |
| `validate_provenance` runs per delivery | 6 | 3 |
| Prose gates in `build-clews-model` | 33 | ~6 (rest in code) |
| Copies of the no-forcing rule | 6 prose + 3 code | 1 prose + 1 code |
| Hash checks that verify nothing | ~9 | 0 |
| Loops with an iteration budget | 1 | all |
| Skills with a small-change fast path | **0 of 6** | 6 of 6 |
| Ceremony for deleting a dangling technology | plan + control + A/B + checksums | 2 audit runs |
| **Traceability columns that are load-bearing** | **missing `exact_locator`, `access_date`, assumption values** | **present** |

Roughly a 70% cut in context cost, a 50% cut in script volume, and a *net gain* in
traceability.

## 7. Sequencing

Ordered so each step is independently valuable and nothing is blocked on a big rewrite:

1. **Move 0 — the triage table, the negative description clauses, and a home for Class A
   changes.** Half a day. This is what turns a 30-minute dead-technology deletion back into a
   one-minute one, and it is independent of everything below.
2. **Add worked example rows to the register templates.** Cheapest fix, highest yield, zero risk.
3. **Rewrite the 8 descriptions.** An hour; saves ~450 tok/session immediately.
4. **Add `exact_locator`, `access_date` to `SOURCES.csv`; `central_value`, `unit` to
   `ASSUMPTIONS.csv`.** Fixes the two real traceability regressions before any consolidation.
5. **Delete the hash checks that verify nothing** (§2.3), and fix the test that asserts the
   broken behavior.
6. **Collapse the 6 `validate_provenance` invocations to 3.** Pure win, no coverage loss.
7. **Merge `audit_muiogo_model.py` into `audit.py`** and unify the three bound-lock checkers.
8. **Unify the provenance schema and validator** (Move 1). The biggest piece; do it once the
   columns are already correct.
9. **Trim `build-clews-model` and `add-environmental-accounting`** to ~120-line SKILL.md files
   with conditional references (Move 2).
10. **Single-source the no-forcing rule and bound the loops** (Move 5).

## 8. What I would deliberately *not* do

- **Not** loosen the no-forcing boundary. It is the scientific integrity of the whole
  exercise. State it once, enforce it in code, keep the counterfactual test verbatim.
- **Not** drop the upstream drift diff, the parity classification, or separate status
  reporting. These catch real failures no amount of ledger discipline would.
- **Not** merge the skills into one mega-skill. They have genuinely different triggers. Share
  the *spine* — provenance, no-forcing, MUIO conventions — and keep the procedures separate.
- **Not** replace the registers with prose documentation. The machine-readable registers plus
  one validator *are* the traceability. Prose is what failed here.
- **Not** touch `compare_muio_results.py` (highest signal-to-line ratio in the repo — a real
  regression differ that refuses to call a run "same" unless it is row-for-row identical, and
  reports `unverified` rather than silently passing), `estimate_residual_capacity.py`'s
  physical-plausibility gates, `validate_calibration_plan.py`'s role/horizon/equation-map
  discipline, `fix_clewsy_grid_mapping.py` (idempotent, has `--check` and a self-test), or
  `compare_history.py`'s exclusion of history-fixed rows from fit credit. These are the good
  parts.

---

## 9. What shipped

Implemented on `main`, 2026-07-29. Every test below was run.

| Move | Status |
|---|---|
| **0 — proportionality** | **Done.** New `clews-model-fix` skill. `audit.py --removable` gate (exit 0/1, names blocking files, `--json`). Triage tables in `calibrate-clews-model` and `add-environmental-accounting` with a Class A exit. Negative clauses in every heavy description. |
| **1 — one provenance schema** | **Partly done.** `shared/provenance/` shipped: `SCHEMA.md`, 6 templates *with worked example rows*, one `provenance.py`, 59 passing tests. `SOURCES` gained `exact_locator`+`access_date`; `ASSUMPTIONS` gained `central_value`+`unit`; new `CHANGES.csv`. **Not migrated:** `add-fisheries-sector` still uses its 6 registers, because its validator enforces them and breaking a working flow was the worse trade. Migration mapping documented in `source-traceability.md`. |
| **2 — procedure, not encyclopedia** | **Done for the worst two.** `build-clews-model` 460 → 172 lines, **10 mandatory reference reads → 0**, 11 references → 8. `add-environmental-accounting` reads made conditional. `muio-import.md`/`import-quality-gates.md` still unmerged — now conditional, so it costs maintenance, not tokens. |
| **3 — gates in code** | **Done.** 33 prose gates → 7 judgment-only. Three provenance checkpoints, stated once. `audit_muiogo_model.py` (324 lines) reduced to a shim delegating to `audit.py`, removing 6–7 duplicated checks **and the ID-truncation bug the copy had re-introduced**. `validate_delivery.py` reuses the required-file list; duplicate `testzip` gone; the nine-substring prose scan gone. |
| **4 — hash only across a trust boundary** | **Done.** Nine dead checks removed or made real. `validate_calibration_plan.py` now opens the file and compares — and the test that asserted `"0"*64` passes was rewritten, plus two new failure tests. Three `null` MUIO checksum keys deleted from the scaffold. Tree hashes at `validate_provenance.py:298-312` untouched, and tamper tests confirm nothing was lost. |
| **5 — single-source and bound** | **Done.** `shared/non-forcing.md` is now the one copy, with one wording of the counterfactual test. Descriptions 594 → 314 words *including a new skill*. Citation-only source replacement no longer triggers a re-solve. Trace sample fixed at ten, not 10%. Fix-and-rerun capped at three cycles. |

### Verified

80 tests pass (59 provenance + 14 audit + 7 calibration-plan; was 6). All 22 Python files
compile; every CLI returns rc=0 on `--help`. `audit.py`'s default output is **byte-identical**
to before the merge on a fixture, same exit code. The shared validator passes on its own
templates and verifies a real digest. All relative markdown links resolve.

### Follow-up fix (same day)

The first cut of Move 0 fixed the *entry* to `calibrate-clews-model` but not its interior, so
a Class B change — one sourced number, no reference to history — still inherited a control
solve, eleven pre-solve gates and an A/B rollback. Worse, it was incoherent: Class B was told
to skip the design gate, which is where the plan is created, and then hit a step requiring
that plan to be validated.

Fixed by adding an explicit **Class B short path** (provenance, equation and units, clean
diff, family-scoped gates, one solve, compare against the *stored* baseline) and by scoping
the eleven pre-solve gates to the parameter family touched: three always apply, the rest only
where they can catch something. A fuel price gets three gates and one solve; an initial stock
still reaches the full vintage machinery, because those gates catch real errors. Control solve
and A/B rollback are now escalations triggered by evidence, not preconditions. Every
plan-validator reference is Class C scoped.

### Known remaining work

1. Migrate `add-fisheries-sector` to the shared schema and retire its four redundant registers.
2. Merge `muio-import.md` and `import-quality-gates.md`.
3. Un-hardcode the case names in `push-handoff:17-19`.
4. Decide the six dangling `muiogo-*` cross-references.
