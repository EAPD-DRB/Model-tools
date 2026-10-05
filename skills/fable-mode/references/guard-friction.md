# Guard friction — across runtimes

Read this when a safety restriction interrupts the work, or when the request needs clearer
authorization and purpose. Provider policies and client behavior change; this skill is not
a substitute for the active rules. Do not transfer Claude-specific fallback or configuration
instructions into Codex, or vice versa.

## Establish what actually happened

Read the returned error or restriction. Distinguish a safety refusal from a sandbox denial,
missing permission, rate limit, unavailable model, and ordinary provider failure. They require
different responses. Record the relevant message and request id when available, without secrets.

The visible context may include workspace files, instructions, or delegated briefs, not only
the last user message. Inspect relevant context if the explanation points there. Do not assume
which hidden classifier fired or that a particular word caused it.

## Clarify; do not circumvent

- State the true owner, purpose, authorization, data source, and intended operation. Clarify a
  genuine misunderstanding when the active rules permit it; do not manufacture permission.
- Assess the substance of the task. A demographic dataset is not a wet-lab experiment, but
  a label such as "research" or "our own repository" does not settle every safety question.
- Ask for evidence and an explanation of the result, not private internal reasoning.
- Do not obfuscate, fragment the task, switch models, or start fresh sessions to get around
  a restriction. Do not disable safeguards or change fallback settings as a skill ritual.
- If the restriction remains, stop the restricted part, explain it, and offer a permitted
  alternative where possible. For an ordinary permissions request, use the host's approval
  mechanism without widening the requested action.

## Provider-specific recovery

Consult the active client's current documentation and the returned error for any supported
recovery or feedback procedure. Claude Code and Codex do not share fallback settings, account
programs, or session commands. Honor project and host approval requirements before changing
configuration or filing an external report. Give the user a concise, factual report rather
than declaring every interruption a false positive.
