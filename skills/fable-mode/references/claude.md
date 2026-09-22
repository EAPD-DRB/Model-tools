# Fable mode in Claude

Use when model choice, effort, or delegation matters in Claude Code or a
Claude-backed runtime. Prompting guidance reviewed 2026-09-22.

## Model and effort

Preserve the user's model and effort. Fable mode is the name of this method; it
does not request the Fable model. Aliases, availability, and delegation controls
depend on the host; use the actual supported identifier and do not silently
substitute an unavailable model.

Where a choice is open, Anthropic's own starting point is Opus 5.5 for most work,
and Fable 5.1 for demanding reasoning or long-horizon work that Opus 5.5 at higher
effort still does not handle. On the published results of 2026-09-22 Opus 5.5 led
Fable 5.1 at 40% of its price, so treat Fable as an escalation on measured
shortfall, not a default. Sonnet 5 and Haiku 4.5 remain the cheaper tiers until
their 5.5 successors ship.

When tuning is authorized, compare effort alongside model choice. Defaults differ:
Opus 5.5 runs at `medium` unless told otherwise, Fable 5.1 and Opus 5 at `high`.
Effort labels do not mean the same amount of thinking across models, so do not
carry a setting from one model to another; Opus 5.5 at `medium` matched Opus 5 at
`high` in Anthropic's testing. A smaller model is not necessarily cheaper per
completed task. Include context, cache, tools, retries, and orchestration in
comparisons. At low effort, check whether needed search and retrieval still happen.
Existing evidence can guide a choice; routine work does not require an effort sweep
or a paid experiment.

[Model configuration](https://code.claude.com/docs/en/model-config) ·
[Models overview](https://platform.claude.com/docs/en/models/overview)

## Prompting differences

Use the guidance for the model actually running, not a universal Claude recipe:

- **Opus 5.5:** Opus 5 prompts carry over. Thinking is always on; lower effort
  rather than writing "don't think" instructions, and remove prompt lines that ask
  for reasoning written out in the reply. Between tool calls it reports progress;
  a turn that ends in such a report is not the end of the task, so keep the task's
  parts in a checklist and continue while items remain open and nothing blocks them.
  It gets to work quickly: on loosely specified tasks, tell it to look through the
  relevant material first.
- **Opus 5:** remove redundant self-check prompts and added verification stages.
  Avoid delegating small tasks merely to double-check them. Preserve specific
  acceptance criteria and required project release checks.
- **Fable 5.1:** make completion and scope explicit so already-authorized next steps
  are executed rather than offered as follow-ups. Keep changes and added tests within
  the requested scope. A question or diagnosis is still an assessment-only task.

[Opus 5.5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5) ·
[Opus 5 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) ·
[Fable 5.1 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)

## Delegation and host boundaries

Use the live invocation's supported model, effort, and inheritance controls.
Claude Code subagent definitions and tools may expose different fields. Do not
copy their settings into Codex or assume a particular agent tool exists everywhere.

Give a helper the intended outcome, workspace, scope, relevant skills or context,
and genuine stopping conditions. Add incident-specific cautions only when relevant.
Do not assume the helper has read the parent's loaded skills.

Keep independent work moving while helpers run, and wait for actual dependencies.
Reuse useful context; request independent review when the task warrants it, not
as a compulsory second pass.

[Subagent controls](https://code.claude.com/docs/en/sub-agents)

API history, caching, and progress-display settings belong in the harness, not a
global skill ritual. Consult the current provider guide when changing that code;
do not modify a desktop app's configuration merely to apply a prompting example.
