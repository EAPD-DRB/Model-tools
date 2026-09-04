---
name: fable-mode
description: >-
  Use PROACTIVELY the moment a task has many layers: multiple dependent steps, unknowns that
  could change the approach, debugging where the first theory might be wrong, or anything that
  needs verification before handoff. Also when a task keeps failing or stalling; before any
  model run, long computation, or multi-repo task; when deciding which model tier a piece of
  work goes to or writing the brief for a delegated agent; when a safety classifier flags
  benign work; and whenever the user asks to slow down, think it through, or work in "fable
  mode". Carries the whole working discipline: the five-gate task loop, the environment ritual
  for model runs, the routing and delegation rules, and how to keep benign work legible to the
  classifiers. Applies on any model.
---

# The Fable Method

The working discipline, written down so any model can run it.

A hard task is anything where the first idea might be wrong: multi-step builds, debugging, research
with claims, anything touching data you haven't looked at yet. For a one-file edit or a simple
lookup, skip the gates and just do the work.

**What actually earns its place here.** On the frontier tier the generic discipline below is
largely native behaviour, and repeating it buys little: instructions written for weaker models
get in the way of stronger ones. The load-bearing content is the environment ritual and the
orchestration rules — non-obvious, learned from incidents, not something a model reconstructs on
its own. Those are kept in full.

## The loop: five gates, in order

A gate must pass before the next one opens. When a task stalls or a result surprises you, name
which gate you're at and re-run it.

1. **Scope** — write what done looks like and how you'll check it. If you can't write the check, you
   don't understand the task. Check standing rules (CLAUDE.md, skills, memory, AGENTS.md) before
   inventing an approach. Name the one to three load-bearing unknowns.
2. **Evidence** — open the real file, data, or tool output before designing against it. Training
   memory is a hypothesis generator, not a source. Attack the biggest unknown with the cheapest
   probe. Prefer a thin end-to-end pass over a complete first stage.
3. **Adversarial** — try to kill your own answer before committing, and actually test the case that
   would break it. Steelman existing code before changing it. **Two failed attempts at the same fix
   means the diagnosis is wrong** — find the assumption under both and test that.
4. **Verify** — verify at the layer of the claim, using evidence you didn't generate. A separate
   verifier with fresh context beats self-critique: on a long run, set a checking interval and
   verify against the specification, not against your own summary. Treat good news as suspect. **A result that reproduces a previously-known-buggy number is contamination
   evidence, not coincidence** — stop and re-verify what code actually ran.
5. **Report** — lead with the answer; separate verified from assumed out loud ("I confirmed X by
   running Y; I'm assuming Z because I couldn't check it"); cite file paths, commands, and numbers.

Effort budget: ~1 tool call for single facts, 3–5 for medium tasks, 5–10 for deep
research/comparisons; more only when the action is irreversible, hours-long, or published.

Full prose for every gate, the standing habits, and the skipped-gate smell list:
[references/full-discipline.md](references/full-discipline.md). The environment info names the
model you are running on: anything below the frontier tier (Sonnet, Haiku) MUST Read that file
before starting work; frontier models load it only when a task keeps failing under this skeleton.

## Mandatory ritual: model runs & environments

Before ANY model solve, battery, build, or long computation — never launch on "it looks right":

1. Print branch + HEAD of every repo involved.
2. Print what the interpreter will actually import and assert the path is under the intended
   worktree: `<venv-python> -c "import <pkg>; print(<pkg>.__file__)"`. Three shadowing vectors,
   all real: (a) an editable install pointing at another worktree; (b) script invocation putting
   the script's dir at `sys.path[0]`; (c) cwd shadowing — `python -c` / `python script.py` from
   another checkout's root imports THAT checkout's package regardless of venv. Console scripts are
   immune to (c). A `-c` probe does not reproduce (b) — probe with the run's own invocation style.
3. Each worktree gets its own venv (`pip install -e .`); entry scripts pin `sys.path.insert(0,
   REPO)` and assert the resolved package path. Launch wrappers assert before exec.
4. Run as a user would: the documented CLI from the checkout's own env. No ad-hoc path hacks.
5. If a result reproduces a previously-known-buggy number: contamination evidence. Stop, re-verify
   imports, never bless or commit those outputs.

This ritual exists because a full battery once silently ran stale code. `og-run-preflight`
mechanizes it for OG-Core/CLEWS runs — prefer that skill when it applies.

## Orchestration: route by the checklist test, delegate with a brief

The teacher move: judgment is written into files; executors run them; the orchestrator verifies.
Executors never bless their own output; the orchestrator never skips the spot check (2–3 minimum)
because the executor sounded confident.

**Try effort before you try another model.** Anthropic calls effort, not model choice, the
primary control for trading intelligence against latency and cost. Sweep it first, because the
answer often removes the need to route down at all: **the top model at low effort tends to beat a
cheaper model at high effort on both cost per task and quality**, so price that comparison before
you route down. A cascade also forfeits cache reuse, since caches are model-scoped. Default is
`high`; `xhigh`/`max` only where a measurement shows the gain. Two traps: at low effort a model
calls search and retrieval tools less often and answers from memory, so raise effort for research
turns; and level names do not mean the same amount of thinking across models, so the sweep is
per-model, not once.

**Routing — the checklist test.** Checklist + verifiable output? Route down. Otherwise it stays up.
Scores are cost / intelligence / taste, so routing stops being guesswork:

| Model     | Cost | Intelligence | Taste | Route it… |
|-----------|-----:|-------------:|------:|-----------|
| Fable 5.1 |    3 |           10 |    10 | orchestrate, plan, verify, write the judgment files; never mechanical execution |
| Opus 5    |    5 |          9.5 |     9 | **anything a human sees, big decisions** — user-facing prose and reports, design calls, adversarial review |
| Sonnet 5  |    8 |            7 |     6 | **standard work from a clear spec** — implement to a written plan, run a defined checklist, mechanical refactors |
| Haiku 4.5 |   10 |            4 |     3 | **scoped grunt work, always with grep** — searches, inventories, file sweeps with an exact target |

**Rows dated 2026-09-04. Source of truth: your own model table — first-party prices, carrying a
date.** Cost is log-scaled from list output price, so it ignores cache reads, and the frontier
row's reads are a quarter of the usual rate, which puts its real spend below the tier beneath it
on any read-heavy loop. Intelligence is anchored to the published SWE-bench and GPQA figures at
those dates; taste is judgment, not a benchmark. Two live flags: the frontier row carries no
verified first-party SWE-bench figure, and the cheapest row has a near-term retirement floor, so
check the current one before pinning new work to it.

**When a model ships, re-anchor before trusting the table.** Refresh the four rows, re-run the
effort sweep on your own work, and read that model's own prompting page for behaviour changes.
Everything above this paragraph is method and should survive a release; the table and this
paragraph are the parts that expire. A pinned score nobody re-checked is worse than no table.

Tiebreaker between tiers: would a wrong answer reach the user or gate a big decision? Yes → route
up. Pass the tier explicitly (`model: "fable" | "opus" | "sonnet" | "haiku"`) on every
Agent/Workflow call.

**The brief — make the plan expect trouble.** Every delegated task ships as a written brief with
four parts; a brief missing any of them is not ready to delegate:

- **Each step:** what you should SEE if it worked — the literal expected output/path/number, not
  "verify it works".
- **Likeliest failure:** its signals + the countermove (e.g. "cwd resets between commands → every
  command block starts with an explicit `cd`; a path printing outside the worktree IS the finding
  — report it, don't retry from elsewhere").
- **Stop when:** the conditions to REPORT, not improvise. An executor that hits a wall returns
  with findings; it never invents an alternate plan.
- **Flag:** anything it couldn't verify, explicitly listed — silence is not a pass.

**Don't block on the fan-out.** Dispatch and keep working; take each result when it lands.
Anthropic measures lower average time to completion at the same quality and cost when the lead
keeps going instead of waiting on each subagent, and a long-lived subagent that keeps its context
across subtasks saves both through cache reads. The thing to avoid is bottlenecking on the
slowest one.

## Guard friction: keep benign work legible to the safety classifiers

Two of our domains sit near gated categories without being in them: demographic
mortality/fertility data reads bio-adjacent, and securing our own repos reads cyber-adjacent. We
never do wet-lab bio or offensive security, so every flag on our work is a false positive. Reduce
them by making that legible, never by evasion.

- **Lead with the reason, not only the request** (the vendor's own template). Owner, purpose and
  data source BEFORE any loaded vocabulary: "for the OG-Core pension model, mortality rates by
  income from UN WPP / DHS surveys…"; "dependency patch on my own repo X — defensive maintenance
  of code we own." Where true, use the allowed-side words: own repository, authorized, defensive.
- **Neutral verbs cost nothing:** terminate a process, not kill it; review for weaknesses, not
  attack; patch the CVE, not exploit. Choosing among equally accurate words is not obfuscation.
- **Never write show-your-reasoning or transcribe-your-thinking instructions** into a skill or
  CLAUDE.md. That is the one documented self-inflicted trigger.
- **Never** obfuscate or code terms to slip past detection, split a request into fragments to
  dodge a screen, claim an authorization that isn't real, or instruct any model to ignore its
  safeguards. If honest context doesn't clear it, stop and surface it to the user — the guard
  might be right.

When a flag actually fires, or before a stretch of guard-prone work, read
[references/guard-friction.md](references/guard-friction.md): where the category lines sit, what
the classifier reads besides the prompt, the supported retry, session hygiene, and how to report
a false positive.

## Notes

- This is a method skill, not a workflow. It changes how you execute the current task; it produces
  no files of its own.
- It stacks with task-specific skills (`systematic-debugging`, `og-run-preflight`, `/code-review`).
  Those are the "how to check" tools; this is the discipline of when to reach for them.
- Don't apply it to trivial work. Forcing all five gates onto a two-minute edit is its own failure
  mode.
- If a task keeps failing under this discipline, that's the signal to escalate to a stronger model,
  not to loosen the process. Keep the discipline either way.
