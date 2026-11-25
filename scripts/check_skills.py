#!/usr/bin/env python3
"""Check the skills in this repo: frontmatter, relative links, history tags, vendored copies.

Usage: python scripts/check_skills.py        # exit 1 on any problem
Checks:
- each skills/<name>/SKILL.md has a `name` equal to its folder and a description of 1-1024 chars;
- every relative Markdown link in a skill resolves to a file inside that skill folder (a skill must
  work when its folder is installed on its own);
- every [CODE] history tag in og-country-calibration has references/lessons/<CODE>.md;
- vendored shared files are current (scripts/sync_shared.py --check).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
problems = []

for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
    folder = skill_md.parent
    text = skill_md.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        problems.append(f"{skill_md}: no frontmatter")
        continue
    fm = m.group(1)
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    if not name or name.group(1) != folder.name:
        problems.append(f"{skill_md}: name does not match folder {folder.name}")
    d = re.search(r"^description:\s*(?:>-?\s*\n((?:[ \t]+.*\n?)+)|\"(.*?)\"|(.*))", fm, re.M)
    desc = ""
    if d:
        desc = " ".join(x.strip() for x in (d.group(1) or d.group(2) or d.group(3) or "").splitlines())
    if not 1 <= len(desc) <= 1024:
        problems.append(f"{skill_md}: description length {len(desc)} (must be 1-1024)")
    for md in folder.rglob("*.md"):
        body = re.sub(r"```.*?```", "", md.read_text(), flags=re.S)
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", body):
            if re.match(r"[a-z]+://|mailto:", target):
                continue
            path = (md.parent / target).resolve()
            if not path.exists():
                problems.append(f"{md.relative_to(ROOT)}: broken link {target}")
            elif folder.resolve() not in path.parents and path != folder.resolve():
                problems.append(f"{md.relative_to(ROOT)}: link leaves the skill folder: {target}")

cal = SKILLS / "og-country-calibration"
if cal.exists():
    tags = set()
    for md in [cal / "SKILL.md", *sorted((cal / "references").glob("*.md"))]:
        for group in re.findall(r"\[([A-Z]{3}(?:, [A-Z]{3})*)\]", md.read_text()):
            tags.update(group.split(", "))
    for code in sorted(tags):
        if not (cal / "references" / "lessons" / f"{code}.md").exists():
            problems.append(f"og-country-calibration: tag [{code}] has no lessons/{code}.md")

r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_shared.py"), "--check"],
                   capture_output=True, text=True)
if r.returncode != 0:
    problems.append("vendored shared files are stale: run scripts/sync_shared.py\n" + r.stdout + r.stderr)

for p in problems:
    print(p)
print(f"{len(problems)} problem(s)" if problems else "all skill checks pass")
sys.exit(1 if problems else 0)
