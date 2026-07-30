#!/usr/bin/env python3
"""Vendor the shared skill rules into every skill that depends on them.

Why this exists
---------------
A skill is installed by copying **one directory** into a skills folder — that is
how both Claude (`~/.claude/skills/`) and Codex install them, and it is how
someone downloading this repo will use it. So a skill that links to
``../shared/non-forcing.md`` is broken the moment it is installed: the target is
outside the copied directory.

Keeping a hand-written copy in each skill is the other failure: the non-forcing
rule already existed in six divergent copies in three different wordings, which
is how it rotted the first time.

So: one editable source in ``skills/shared/``, mechanically copied into each
dependent skill's ``references/``. Edit the source, run this script. ``--check``
fails when a copy has drifted, so the duplication cannot silently fork.

Usage
-----
    python scripts/sync_shared.py            # write the copies
    python scripts/sync_shared.py --check    # exit 1 if any copy is stale
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHARED = REPO / "skills" / "shared"

# shared source -> skills that must carry a local copy in their references/
VENDORED = {
    "non-forcing.md": (
        "build-clews-model",
        "calibrate-clews-model",
        "clews-model-fix",
        "add-environmental-accounting",
        "add-fisheries-sector",
        "assess-clews-calibration",
    ),
    "provenance/SCHEMA.md": (
        "build-clews-model",
        "calibrate-clews-model",
        "clews-model-fix",
        "add-fisheries-sector",
    ),
}

PYTHON_VENDORED = {
    "provenance/provenance.py": (
        ("build-clews-model", "scripts/provenance.py"),
    ),
}

BANNER = (
    "<!-- GENERATED FILE - do not edit here.\n"
    "     Source: skills/shared/{source}\n"
    "     Regenerate: python scripts/sync_shared.py\n"
    "     A local copy exists so this skill works when its directory is\n"
    "     installed on its own, in Claude or in Codex. -->\n\n"
)

PYTHON_BANNER = (
    "# GENERATED FILE - do not edit here.\n"
    "# Source: skills/shared/{source}\n"
    "# Regenerate: python scripts/sync_shared.py\n"
    "# This local copy keeps the installed skill self-contained in Claude and Codex.\n"
)


def rendered(source: str) -> str:
    text = (SHARED / source).read_text(encoding="utf-8")
    # Links in the shared copy are written relative to skills/shared/; from a
    # skill's references/ directory the repo root is three levels up.
    text = text.replace("](../", "](../../../")
    return BANNER.format(source=source) + text


def rendered_python(source: str) -> str:
    text = (SHARED / source).read_text(encoding="utf-8")
    banner = PYTHON_BANNER.format(source=source)
    if text.startswith("#!"):
        first, remainder = text.split("\n", 1)
        return first + "\n" + banner + remainder
    return banner + text


def target_for(skill: str, source: str) -> Path:
    return REPO / "skills" / skill / "references" / Path(source).name


def sync_target(
    target: Path,
    payload: str,
    check: bool,
    stale: list[str],
) -> int:
    current = target.read_text(encoding="utf-8") if target.is_file() else None
    if current == payload:
        return 0
    relative = target.relative_to(REPO)
    if check:
        stale.append(f"{relative} is {'missing' if current is None else 'stale'}")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    print(f"wrote {relative}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if any vendored copy is missing or stale",
    )
    args = parser.parse_args(argv)

    stale: list[str] = []
    written = 0
    for source, skills in VENDORED.items():
        if not (SHARED / source).is_file():
            print(f"missing shared source: skills/shared/{source}", file=sys.stderr)
            return 2
        payload = rendered(source)
        for skill in skills:
            target = target_for(skill, source)
            if not target.parent.is_dir():
                print(f"no references/ dir for {skill}", file=sys.stderr)
                return 2
            written += sync_target(target, payload, args.check, stale)

    for source, targets in PYTHON_VENDORED.items():
        if not (SHARED / source).is_file():
            print(f"missing shared source: skills/shared/{source}", file=sys.stderr)
            return 2
        payload = rendered_python(source)
        for skill, relative_target in targets:
            skill_root = REPO / "skills" / skill
            if not skill_root.is_dir():
                print(f"no skill dir for {skill}", file=sys.stderr)
                return 2
            target = skill_root / relative_target
            written += sync_target(target, payload, args.check, stale)

    if args.check:
        if stale:
            print("Vendored shared rules are out of date:", file=sys.stderr)
            for line in stale:
                print(f"  {line}", file=sys.stderr)
            print("Run: python scripts/sync_shared.py", file=sys.stderr)
            return 1
        print("all vendored shared rules are current")
        return 0

    print(f"{written} file(s) updated" if written else "already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
