---
name: fable-mode
description: Use PROACTIVELY the moment you notice a task has many layers - multiple dependent steps, unknowns that could change the approach, debugging where the first theory might be wrong, or anything that needs verification before handoff. Also use when a task keeps failing or stalling, before any model run / long computation / multi-repo task, or when the user says "fable mode", "fable time", "think like Fable", "use the Fable skill", "use the Fable method", "work like Fable", "slow down and do this right", or "think this through first". Loads Fable 5's working discipline (the five-gate task loop plus standing habits) so any session, especially one running on Opus 5 or Sonnet 5, applies it.
---

# The Fable Method

Fable 5's working discipline, written down so any model can run it.

A hard task is anything where the first idea might be wrong: multi-step builds, debugging, research
with claims, anything touching data you haven't looked at yet. For a one-file edit or a simple
lookup, skip the gates and just do the work.

**What actually earns its place here.** On the frontier tier (Fable 5, Opus 5) the generic
discipline below is largely native behaviour, and repeating it buys little — Anthropic deleted
~80% of Claude Code's system prompt for exactly this reason: instructions written for weaker
models get in the way of stronger ones. The
load-bearing content is the environment ritual and the orchestration rules — non-obvious, learned
from incidents, not something a model reconstructs on its own. Those are kept in full.

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
4. **Verify** — verify at the layer of the claim, using evidence you didn't generate. Treat good
   news as suspect. **A result that reproduces a previously-known-buggy number is contamination
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

**Routing — the checklist test.** Checklist + verifiable output? Route down. Otherwise it stays up.
Scores are cost / intelligence / taste, so routing stops being guesswork:

| Model     | Cost | Intelligence | Taste | Route it… |
|-----------|-----:|-------------:|------:|-----------|
| Fable 5   |    3 |           10 |    10 | orchestrate, plan, verify, write the judgment files — never mechanical execution |
| Opus 5    |    5 |          9.5 |     9 | **anything a human sees, big decisions** — user-facing prose/reports, design calls, adversarial review. Near benchmark parity with Fable on standard evals at half the price — route heavy design/review work down freely; Fable keeps the edge on the longest-horizon work |
| Sonnet 5  |    7 |            7 |     6 | **standard work from a clear spec** — implement to a written plan, run a defined checklist, mechanical refactors |
| Haiku 4.5 |   10 |            4 |     3 | **scoped grunt work, always with grep** — searches, inventories, file sweeps with an exact target |

Scores calibrated July 2026. Cost is log-scaled from list output pricing ($/MTok: Fable 50, Opus
25, Sonnet 15 — $10 intro through 2026-08, Haiku 5). Intelligence is anchored to published
benchmarks (SWE-bench Verified: Opus 5 96.0, Fable 5 95, Sonnet 5 85.2, Haiku 4.5 73.3; GPQA
Diamond: Opus 5 93.2; aggregate rankings place Opus 5 and Fable 5 within ~3 points). Taste is
judgment, not a benchmark. Re-anchor at each model release.

Tiebreaker between tiers: would a wrong answer reach the user or gate a big decision? Yes → route
up. Pass the tier explicitly (`model: "opus" | "sonnet" | "haiku"`) on every Agent/Workflow call.

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

## Guard friction: keep benign work legible to the safety classifiers

Fable-tier safety classifiers deliberately over-trigger (Anthropic says so), and two of our
domains sit near gated categories without being in them: demographic mortality/fertility data
reads bio-adjacent (the gated set is virology/toxicology/molecular design — actuarial and
UN-WPP/DHS statistics are explicitly on the allowed side), and securing our own repos reads
cyber-adjacent (the policy line is authorization: "with the system owner's consent" is allowed
vocabulary, offense-without-authorization is the gated thing). We never do wet-lab bio or
offensive security, so every flag on our work is a false positive — reduce them by making that
legible, never by evasion.

- **Lead with the reason, not only the request** (Anthropic's own template). Put owner + purpose +
  data source BEFORE loaded vocabulary: "for the OG-Core pension model, mortality rates by income
  from UN WPP / DHS surveys…"; "dependency patch on my own repo X — defensive maintenance of code
  we own." Where true, use the policy's allowed-side words: own repository, authorized, defensive.
- **Neutral verbs cost nothing:** terminate a process, not kill it; review for weaknesses, not
  attack; patch the CVE, not exploit. Word choice among equally accurate options is not
  obfuscation.
- **The classifier reads more than the prompt:** file contents, filenames, git status, CLAUDE.md,
  and subagent system prompts are all input. Keep security-review subagent prompts lean or run the
  review inline (documented: same review passed inline, flagged as a keyword-dense subagent). A
  first-message flag in a security-heavy repo can be workspace context alone — `claude --safe-mode`
  isolates that. Never write show-your-reasoning / transcribe-your-thinking instructions into
  skills or CLAUDE.md: that is the one documented self-inflicted trigger (reasoning_extraction).
- **When a guard fires:** never retry verbatim, never rephrase to obscure. One retry with fuller
  true context is officially supported (`/config` → disable switch-models-on-flag → edit and retry;
  otherwise the session falls back bio→Opus 5 / cyber→Opus 4.8 and `/model` returns afterward).
  Flags cascade — after one, move the flagged work to a fresh session and keep guard-prone work
  out of long mixed sessions. Report keepers via /feedback or a claude-code issue with the request
  ID; sustained security work can apply to the Cyber Verification Program.
- **Never:** obfuscate or code terms to slip past detection, split a request into fragments to
  dodge a screen, claim an authorization that isn't real, or instruct any model to ignore its
  safeguards. If honest context doesn't clear it, stop and surface it to Marcelo — the guard might
  be right.

## Notes

- This is a method skill, not a workflow. It changes how you execute the current task; it produces
  no files of its own.
- It stacks with task-specific skills (`systematic-debugging`, `og-run-preflight`, `/code-review`).
  Those are the "how to check" tools; this is the discipline of when to reach for them.
- Don't apply it to trivial work. Forcing all five gates onto a two-minute edit is its own failure
  mode.
- If a task keeps failing under this discipline, that's the signal to escalate to a stronger model,
  not to loosen the process. Keep the discipline either way.
