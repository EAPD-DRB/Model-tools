# Fable mode in Claude

Use when model choice, effort, or delegation matters in Claude Code or a
Claude-backed runtime. Prompting guidance reviewed 2026-09-28.

## Model and effort

Preserve the user's model and effort. Fable mode is the name of this method; it
does not request the Fable model. Aliases, availability, and delegation controls
depend on the host; use the actual supported identifier and do not silently
substitute an unavailable model.

Where a choice is open, Anthropic's own starting point is Opus 5.5 for most work,
and Fable 5.1 for demanding reasoning or long-horizon work that Opus 5.5 at higher
effort still does not handle. On the published results of 2026-09-22 Opus 5.5 led
Fable 5.1 at 40% of its price, so treat Fable as an escalation on measured
shortfall, not a default.

Sonnet 5.5 (released 2026-09-28) is the cheaper tier, at half Opus 5.5's price per
token. Anthropic says it fits best "when the task has a clear spec and a way to
check the result": well-scoped coding and bug fixes, high-volume work, documents,
slides and spreadsheets, and well-defined agent tasks run repeatedly. Complex work
that needs careful judgment, and the hardest problems, stay on Opus. An open-ended
or taste-driven request is where Opus earns its price; a brief or skill that
defines what good looks like narrows the gap. Haiku 4.5 stays the
cheapest tier until Haiku 5.5 ships ("in the coming weeks" as of 2026-09-28).

When tuning is authorized, compare effort alongside model choice. Defaults differ
by model and by host:

| Model | API default | Claude Code default |
| --- | --- | --- |
| Opus 5.5 | `medium` | `medium` |
| Sonnet 5.5 | `high` | `medium` |
| Fable 5.1, Opus 5 | `high` | `high` |

Effort labels do not mean the same amount of thinking across models, so do not
carry a setting from one model to another; Opus 5.5 at `medium` matched Opus 5 at
`high` in Anthropic's testing. A smaller model is not necessarily cheaper per
completed task. Include context, cache, tools, retries, and orchestration in
comparisons. At low effort, check whether needed search and retrieval still happen.
Existing evidence can guide a choice; routine work does not require an effort sweep
or a paid experiment.

[Model configuration](https://code.claude.com/docs/en/model-config) ·
[Models overview](https://platform.claude.com/docs/en/models/overview) ·
[Choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) ·
[Sonnet 5.5 launch notes](https://claude.dev/blog/building-with-claude-sonnet-5-5/)

## Prompting differences

Use the guidance for the model actually running, not a universal Claude recipe:

- **Opus 5.5:** Opus 5 prompts carry over. Thinking is always on; lower effort
  rather than writing "don't think" instructions, and remove prompt lines that ask
  for reasoning written out in the reply. Between tool calls it reports progress;
  a turn that ends in such a report is not the end of the task, so keep the task's
  parts in a checklist and continue while items remain open and nothing blocks them.
  It gets to work quickly: on loosely specified tasks, tell it to look through the
  relevant material first.
- **Sonnet 5.5:** Sonnet 5 prompts carry over, but its effort levels are
  recalibrated, so set effort instead of carrying one over. At `low` and `medium`
  on long agentic work it may stop to check in before a multi-part task is done,
  and at `low` it may call a code change done without a real check: say to carry
  the whole task through unless blocked or before a risky step, and name the check
  that counts. At every effort it tends to add unrequested tests and docs, so state
  the scope. In research it can answer from training knowledge: ask for current
  sources, and drop "minimize tool calls" wording, which it follows literally. At
  `xhigh` and `max` it starts its own review rounds, sometimes with reviewer
  subagents; on coding tasks at `max`, Anthropic's line "When the work the user
  asked for is done and its checks pass, stop and report." cut session cost by
  about a third with no change in quality.
- **Opus 5:** remove redundant self-check prompts and added verification stages.
  Avoid delegating small tasks merely to double-check them. Preserve specific
  acceptance criteria and required project release checks.
- **Fable 5.1:** make completion and scope explicit so already-authorized next steps
  are executed rather than offered as follow-ups. Keep changes and added tests within
  the requested scope. A question or diagnosis is still an assessment-only task.

[Opus 5.5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5) ·
[Sonnet 5.5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5) ·
[Opus 5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) ·
[Fable 5.1 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)

## Delegation and host boundaries

Use the live invocation's supported model, effort, and inheritance controls.
Claude Code subagent definitions and tools may expose different fields. Do not
copy their settings into Codex or assume a particular agent tool exists everywhere.
In Claude Code a helper runs at the session's effort unless its definition sets
`effort`, so a Sonnet 5.5 helper started from a `max` session also runs at `max`.
Where that matters, set effort in the definition, or put the scope and
stop-and-report lines in the brief.

Splitting work costs a plan, a handoff, and a merge that one model gets for free.
In Anthropic's measurements, when the work was one dependent chain or fit in one
context, one model at lower effort came out ahead; splitting fits independent
pieces, most of all when they add up to more than one context.

Give a helper the intended outcome, workspace, scope, relevant skills or context,
and genuine stopping conditions. Add incident-specific cautions only when relevant.
Do not assume the helper has read the parent's loaded skills.

Keep independent work moving while helpers run, and wait for actual dependencies.
Reuse useful context; request independent review when the task warrants it, not
as a compulsory second pass.

[Subagent controls](https://code.claude.com/docs/en/sub-agents) ·
[Cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence)

API history, caching, and progress-display settings belong in the harness, not a
global skill ritual. Consult the current provider guide when changing that code;
do not modify a desktop app's configuration merely to apply a prompting example.
