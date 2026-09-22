# Focused troubleshooting

Read when progress stalls or the actual execution target is uncertain. This is a
set of incident-based aids, not a longer process required for particular models.
Use only the part that addresses the current uncertainty.

## Establish what is running

A full computation once ran stale code successfully. A green result from the wrong
checkout does not establish the requested change.

When entering a new worktree or runtime, changing the environment, preparing an
expensive run, or investigating an unexpectedly stale result, establish the relevant
checkout, inputs, and executable with native tooling. Branch and commit, build
target, or resolved package location can distinguish otherwise identical-looking
runs. For non-repository work, identify the actual input and runtime instead.

Reuse that evidence while it remains valid. Routine rebuilds in an unchanged,
established environment do not need another branch/HEAD and toolchain ritual.
Use existing project preflight commands where appropriate, not a second wrapper
written solely for this skill.

Use the supported project environment and documented entrypoint. A missing package
or wrong import path is a diagnosis, not permission to install dependencies or add
path hacks. Honor the task's existing configuration and installation boundaries.

### Python import shadowing

These failures have occurred in real work:

- An editable install points to another worktree.
- Script invocation puts the script's directory at `sys.path[0]`.
- The working directory shadows the intended package under `python -c`.

Printing a package's `__file__` through the intended environment is a useful initial
probe. A `-c` probe does not prove what a differently invoked script imports:
check the actual documented entrypoint when the discrepancy matters. Other stacks
need their native equivalent, not a Python environment.

## Reassess a recurring failure

Identify what the next attempt will distinguish. Check the implementation,
assumptions, and execution environment rather than declaring the original diagnosis
wrong because a fixed number of attempts failed. Keep the explanation that best
fits the observed evidence; change direction when new evidence warrants it.

If the result matches a known-buggy earlier output, inspect the target or inputs.
The match is a useful signal, not proof of stale code. Similarly, a clean test run
is not evidence that the tests are broken.

For a consequential assumption, choose a direct check that could disprove it.
For a straightforward correction, a diff and focused execution may already settle
the question. Do not invent edge cases to satisfy an adversarial-review ritual.

## Match the evidence to the claim

Distinguish source changes, what was built, what is installed, and what is deployed
when they can differ. If the claim is that a user can perform an action, a helper
unit test alone may not cover the wiring. Check the missing link, not the whole
system by default.

Use existing evidence where it covers the unchanged behavior. Required release
checks remain required. Do not rerun a broad suite or summon an independent reviewer
without a task-specific reason.

Report what the evidence establishes, including a material limitation. A missing
search result is not proof that a user's claim is false. A warning needs observed
support, not merely an imagined failure. Minor findings can be reported together
without interrupting progress; only a real decision or blocker needs a pause.
