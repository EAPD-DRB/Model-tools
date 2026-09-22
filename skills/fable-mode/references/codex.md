# Fable mode in Codex

Use when model choice, effort, or delegation matters in a Codex host. Prompting
guidance reviewed 2026-09-14. The active host's controls govern execution.

## Model and effort

Preserve an explicit model and effort setting. Otherwise use the selected model's
effective default. Do not change model because the skill is called Fable mode or
because a task can be described as a checklist.

Where tuning is authorized, consider effort as well as model choice. Compare task
quality, elapsed time, and total cost—including tools, retries, context, and cache
effects—not only a per-token price. Existing representative evidence may suffice;
this does not require or authorize paid benchmarks.

Use identifiers and effort values supported by the actual tool. A recommendation
is not an executed switch. Do not change global configuration to make a preferred
route possible, or infer API costs from subscription usage percentages.

[Model guidance](https://learn.chatgpt.com/docs/models)

## Prompting and completion

For Astra, remove inherited broad read-before-edit routines and redundant
verification stages. Keep the specific project constraints and evidence needed
for the requested result. More checking is not automatically more confidence.

State the whole authorized outcome clearly. Do not stop at the first implementation
when running it or fixing its failures is part of the request. A review-only request
still authorizes an assessment, not unsolicited implementation.

[OpenAI's Astra guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)

## Delegation controls

Use native subagents when independent work justifies the overhead. Small tasks can
stay with the current model. Give helpers the outcome, workspace, scope, and needed
context rather than a mandatory step-by-step script.

Configuration, subagent tools, and desktop task-management tools expose different
controls. Follow the live schema and supported inheritance; do not copy parameter
names between surfaces. Creating a user-visible task is not a substitute for a
subagent and requires the user's request.

Do not assume a child received the parent's history or loaded skills. Preserve
needed context when choosing a fork or model override. Reuse helpers for related
follow-ups where useful; use fresh context when genuine independence matters.
Use native follow-up and wait tools, and do not duplicate a helper's work just to
remain busy.

[Subagent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents)
