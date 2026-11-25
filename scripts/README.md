# scripts/

Small helper scripts (Python, shell, etc.) that support the tools here —
data prep, format conversion, one-off utilities. Keep them self-contained
and documented at the top of the file.

- `sync_shared.py`: copies shared rules (`skills/shared/`) and the history (`docs/og-lessons/`)
  into the skills that carry them; `--check` fails if a copy is stale.
- `check_skills.py`: checks every skill's frontmatter, that its relative links resolve inside its
  own folder, the history tags, and the shared copies. Run it before committing a skill change; CI
  runs it on every pull request.
