# fable-mode changes

- 2026-09-28: Claude Sonnet 5.5 released at Sonnet 5's price ($2/$10, half of Opus 5.5).
  The Claude reference now names it as the cheaper tier for work with "a clear spec and a way
  to check the result" and keeps Opus 5.5 for judgment-heavy and open-ended work; tabulates
  effort defaults by host (Claude Code runs Sonnet 5.5 at `medium`, the API at `high`); notes
  that a Claude Code helper inherits the session's effort; adds the Sonnet 5.5 prompting notes
  (early check-ins and unverified "done" at low effort, unrequested additions, answering from
  training knowledge, self-started review rounds at `xhigh`/`max`) and Anthropic's measured
  cost of splitting work across models. The skill body now asks a delegation brief to say how
  the helper can check its result. Haiku 4.5 stays until Haiku 5.5 ships. Prompted by
  [Nate Herk's seven-task Sonnet 5.5 vs Opus 5.5 test](https://www.youtube.com/watch?v=7eo-11K2e3c):
  with a clear spec or a skill defining what good looks like, Sonnet matched Opus for less;
  on vague asks Opus won; Opus cost about $16 more over all seven, not double. Sources:
  [Introducing Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5),
  [Building with Sonnet 5.5](https://claude.dev/blog/building-with-claude-sonnet-5-5/),
  [Prompting Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5),
  [Choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model),
  [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence),
  [Model configuration](https://code.claude.com/docs/en/model-config),
  [Subagents](https://code.claude.com/docs/en/sub-agents).
- 2026-09-22: Claude Opus 5.5 released. The Claude reference now names Opus 5.5 as the
  default starting point and Fable 5.1 as an escalation on measured shortfall, records the
  different effort defaults (Opus 5.5 `medium`; Fable 5.1 and Opus 5 `high`), and adds the
  Opus 5.5 prompting notes: thinking always on, a progress report is not the end of a task,
  look through the relevant material before acting. The skill body says outright that the
  name is the method's, not a model's. Sources: [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5),
  [What's new in Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5),
  [Models overview](https://platform.claude.com/docs/en/models/overview).
- 2026-09-14: simplified to a method with optional lenses; fixed verification rituals removed;
  reviewed against [OpenAI's Astra skill guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
  and [Anthropic's skill authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
  The dated review note moved here from the skill body; delegation regained "say what a correct result looks like".
