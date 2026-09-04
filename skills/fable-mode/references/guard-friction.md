# Guard friction — the detail

Read this when a flag actually fires, or before a stretch of guard-prone work. The standing
rules that prevent flags live in SKILL.md; this file is what the classifier reads and what to
do after one trips.

**Dated content warning.** The category boundaries, the fallback behaviour and the recovery
keystrokes below were true on 2026-09-04. Classifier behaviour changes between models: a newer
model may false-positive less, may route a flag somewhere else, or may permit work this file
says is near the line. Re-read the current model's own prompting page before relying on the
specifics; the practice at the top of SKILL.md is the durable part.

## Where the lines actually sit

- **Bio.** The gated set is virology, toxicology and molecular design. Actuarial tables and
  UN-WPP / DHS demographic statistics are explicitly on the allowed side, which is why
  mortality and fertility work reads adjacent without being in scope.
- **Cyber.** The policy line is authorization. "With the system owner's consent" is allowed
  vocabulary; offense without authorization is the gated thing. As of 2026-09, finding
  vulnerabilities in source code is explicitly permitted, and false positives are fewer than
  they were at the previous model's launch.

## The classifier reads more than the prompt

File contents, filenames, git status, CLAUDE.md and subagent system prompts are all input.

- Keep security-review subagent prompts lean, or run the review inline. Documented case: the
  same review passed inline and was flagged as a keyword-dense subagent.
- A first-message flag in a security-heavy repo can be workspace context alone. Starting the
  session in safe mode isolates that.
- Never write show-your-reasoning or transcribe-your-thinking instructions into a skill or
  CLAUDE.md. That is the one documented self-inflicted trigger, and it is a standing rule in
  SKILL.md rather than an incident-response item.

## When a guard fires

1. Never retry the same words, and never rephrase to obscure. One retry carrying fuller true
   context is the officially supported move.
2. In Claude Code: disable switch-models-on-flag in config, edit the request, retry. Otherwise
   the session falls back to a lower-tier model by refusal category and returns afterwards.
3. Flags cascade. Move the flagged work to a fresh session and keep guard-prone work out of
   long mixed sessions.
4. Report a false positive through feedback or a claude-code issue with the request id.
   Sustained security work can apply to the Cyber Verification Program.
