# skills/

Skills that package instructions for a repeatable task (e.g. the OG country
calibration skill). One directory per skill, each with its own `SKILL.md`.

## Installing a skill

Copy the skill's directory into your Claude skills folder, then restart Claude
Code (or reload the window) so it's picked up:

- **Personal** (available in every project): `~/.claude/skills/`
- **Project** (shared via a repo): `<repo>/.claude/skills/`

For example, to install `og-country-calibration` for your own use:

```
cp -r skills/og-country-calibration ~/.claude/skills/
```

Claude discovers it by the `name` and `description` in the `SKILL.md`
frontmatter — no other registration needed.
