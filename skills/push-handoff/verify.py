#!/usr/bin/env python3
"""Verify a MUIO case handoff before it is committed and pushed.

Companion to SKILL.md (push-handoff). Answers the one question Git cannot: is
the RIGHT thing inside the archive? Git tracks the ZIP as a single opaque blob
and transfers it flawlessly whether it holds the case you meant or the control
run standing next to it. The live case itself is gitignored, so nothing in the
normal push path ever looks inside.

Every check here is a predicate with a yes/no answer. It reports and never
fixes: a verifier that repairs things hides the fact that something was wrong.
It fails closed — a state it cannot establish is a FAIL, not a pass.

Usage:
    python verify.py --repo ../CLEWs-PHL --case Philippines_v16
    python verify.py --repo ../CLEWs-PHL --case Philippines_v16 --archive path/to.zip
    python verify.py --repo ... --case ... --staged        # also gate the commit
    python verify.py --repo ... --case ... --allow docs/HISTORY.md
    python verify.py --repo ... --case ... --json report.json

Exit status:
    0   every check passed; safe to commit and push
    1   at least one check FAILED; stop and read it
    2   the request was unusable (bad path, no archive, ambiguous archive)

This does not fetch. Upstream comparison uses the refs already in the repo, so
run `git fetch` first or treat the branch check as advisory — it says so in its
own output rather than guessing.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, zipfile

# Content that must never travel in a handoff archive. Solver output is the one
# that matters most: it looks valid to whoever unzips it, and it came from a
# different model version than the inputs beside it.
EXCLUDED = [
    ("solver results (res/)", lambda p: "/res/" in p or p.endswith("/res")),
    ("generated data.txt", lambda p: os.path.basename(p) in (
        "data.txt", "data_processed.txt",
        "upstream_data.txt", "upstream_data_preprocessed.txt")),
    ("LP/MPS solver input", lambda p: p.lower().endswith((".lp", ".mps"))),
    ("solver log", lambda p: p.lower().endswith(".log")),
    ("python cache", lambda p: "__pycache__" in p or p.endswith(".pyc")),
    ("macOS metadata", lambda p: os.path.basename(p) == ".DS_Store"),
]

# Files a recipient needs for the case to open and for pull-handoff to rebuild
# the empty res/ tree the exclusion above removes.
REQUIRED_IN_ZIP = ["genData.json", "view/resData.json"]


class Report:
    """Accumulates findings so every check runs before anything is reported.

    Stopping at the first failure would hide the second one, and the second is
    often what explains the first.
    """

    def __init__(self):
        self.rows = []

    def add(self, ok, name, detail=""):
        self.rows.append({"check": name, "ok": bool(ok), "detail": detail})
        return ok

    def ok(self, name, detail=""):
        return self.add(True, name, detail)

    def fail(self, name, detail=""):
        return self.add(False, name, detail)

    @property
    def failed(self):
        return [r for r in self.rows if not r["ok"]]

    def render(self, stream=sys.stdout):
        width = max((len(r["check"]) for r in self.rows), default=0)
        for r in self.rows:
            mark = "PASS" if r["ok"] else "FAIL"
            line = "  {}  {}".format(mark, r["check"].ljust(width))
            if r["detail"]:
                line += "  " + r["detail"]
            print(line.rstrip(), file=stream)
        print(file=stream)
        if self.failed:
            print("  {} of {} checks FAILED — do not push.".format(
                len(self.failed), len(self.rows)), file=stream)
        else:
            print("  all {} checks passed.".format(len(self.rows)), file=stream)


def git(repo, *args):
    """Run a git command, returning (returncode, stdout). Never raises."""
    try:
        proc = subprocess.run(
            ["git", "-C", repo] + list(args),
            capture_output=True, text=True)
    except OSError as exc:                                       # git missing
        return 127, str(exc)
    return proc.returncode, proc.stdout.strip()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_archive(repo, case):
    """Locate the one archive for this case, or explain why we cannot.

    Returns (path, error). Ambiguity is an error, not a choice to make on the
    caller's behalf — picking the newest is how the wrong version ships.
    """
    hits = []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in (".git", "case", "node_modules")]
        if os.path.basename(root) != "muio":
            continue
        for name in files:
            if name.endswith(".zip") and name.startswith(case + "_"):
                hits.append(os.path.join(root, name))
    if not hits:
        return None, ("no archive matching {}_*.zip under any muio/ folder in {}"
                      .format(case, repo))
    if len(hits) > 1:
        listing = "\n    ".join(sorted(os.path.relpath(h, repo) for h in hits))
        return None, ("{} archives match {}_*.zip — name the one you mean with "
                      "--archive:\n    {}".format(len(hits), case, listing))
    return hits[0], None


# ── the checks ────────────────────────────────────────────────────────────────

def check_repo_state(rep, repo):
    code, _ = git(repo, "rev-parse", "--git-dir")
    if code != 0:
        return rep.fail("git repository", "{} is not a git checkout".format(repo))
    rep.ok("git repository", os.path.abspath(repo))

    if os.path.exists(os.path.join(repo, ".git", "MERGE_HEAD")):
        rep.fail("no merge in progress", "finish or abort the merge first")
    else:
        rep.ok("no merge in progress")

    code, upstream = git(repo, "rev-parse", "--abbrev-ref", "@{u}")
    if code != 0:
        rep.fail("branch tracks upstream",
                 "no upstream set — a push would not know where to land")
        return
    code, counts = git(repo, "rev-list", "--left-right", "--count", "@{u}...HEAD")
    if code != 0 or not counts:
        rep.fail("branch not behind upstream", "could not compare against " + upstream)
        return
    behind, ahead = (counts.split() + ["?", "?"])[:2]
    if behind != "0":
        rep.fail("branch not behind upstream",
                 "{} commit(s) behind {} — pull before packaging".format(behind, upstream))
    else:
        rep.ok("branch not behind upstream",
               "{} ahead of {} (refs as of last fetch)".format(ahead, upstream))


def check_case_ignored(rep, repo):
    code, _ = git(repo, "check-ignore", "-q", "case")
    if code == 0:
        rep.ok("case/ is gitignored", "the live case stays out of history")
    else:
        rep.fail("case/ is gitignored",
                 "case/ is TRACKABLE — a commit could pull in the whole working tree")


def check_case_and_link(rep, repo, case, datastorage):
    live = os.path.join(repo, "case", case)
    if not os.path.isdir(live):
        rep.fail("live case exists", "no directory at " + live)
        return None
    rep.ok("live case exists", os.path.relpath(live, repo))

    if not datastorage:
        rep.fail("DataStorage link resolves to the live case",
                 "--datastorage not given and could not be located")
        return live

    entry = os.path.join(datastorage, case)
    if not os.path.exists(entry) and not os.path.islink(entry):
        rep.fail("DataStorage link resolves to the live case",
                 "nothing at " + entry)
    elif not os.path.islink(entry):
        rep.fail("DataStorage link resolves to the live case",
                 "{} is a real directory, not a symlink — two candidate sources "
                 "of truth, and no way to tell which you meant".format(entry))
    elif os.path.realpath(entry) != os.path.realpath(live):
        rep.fail("DataStorage link resolves to the live case",
                 "points at {}, expected {}".format(
                     os.path.realpath(entry), os.path.realpath(live)))
    else:
        rep.ok("DataStorage link resolves to the live case",
               "{} -> {}".format(case, os.readlink(entry)))
    return live


def check_case_identity(rep, live, case):
    """The name inside the model must match the folder it lives in.

    A mismatch survives every downstream check, because the archive opens
    perfectly well — under the wrong identity.
    """
    if live is None:
        return
    gen = os.path.join(live, "genData.json")
    if not os.path.isfile(gen):
        rep.fail("osy-casename matches folder", "no genData.json in " + live)
        return
    try:
        with open(gen, encoding="utf-8") as fh:
            declared = json.load(fh).get("osy-casename")
    except (OSError, ValueError) as exc:
        rep.fail("osy-casename matches folder", "unreadable genData.json: {}".format(exc))
        return
    if declared != case:
        rep.fail("osy-casename matches folder",
                 "model calls itself {!r}, folder is {!r}".format(declared, case))
    else:
        rep.ok("osy-casename matches folder", declared)


def check_archive(rep, archive, case):
    if not os.path.isfile(archive):
        rep.fail("archive exists", "no file at " + archive)
        return
    size = os.path.getsize(archive)
    rep.ok("archive exists", "{} ({:.1f} MB)".format(
        os.path.basename(archive), size / 1048576.0))

    try:
        zf = zipfile.ZipFile(archive)
    except (zipfile.BadZipFile, OSError) as exc:
        rep.fail("archive is a readable ZIP", str(exc))
        return
    with zf:
        names = zf.namelist()
        if not names:
            rep.fail("archive is not empty", "no entries")
            return

        tops = sorted({n.split("/")[0] for n in names if n.strip("/")})
        if tops == [case]:
            rep.ok("one top-level folder, named for the case", case)
        else:
            rep.fail("one top-level folder, named for the case",
                     "found {} — expected exactly [{!r}]".format(tops, case))

        for label, matches in EXCLUDED:
            hits = [n for n in names if matches(n)]
            if hits:
                rep.fail("no " + label,
                         "{} entr{} — e.g. {}".format(
                             len(hits), "y" if len(hits) == 1 else "ies", hits[0]))
            else:
                rep.ok("no " + label)

        present = set(names)
        for rel in REQUIRED_IN_ZIP:
            want = "{}/{}".format(case, rel)
            if want in present:
                rep.ok("contains " + rel)
            else:
                rep.fail("contains " + rel, "missing " + want)

        bad = zf.testzip()
        if bad is None:
            rep.ok("archive integrity (CRC of every entry)",
                   "{} entries".format(len(names)))
        else:
            rep.fail("archive integrity (CRC of every entry)", "corrupt entry: " + bad)


def check_checksum(rep, archive):
    """SHA256SUMS must describe THIS archive.

    A checksum file left describing the previous archive is worse than none:
    the recipient's verification passes against a stale reference.
    """
    sums = os.path.join(os.path.dirname(archive), "SHA256SUMS")
    if not os.path.isfile(sums):
        rep.fail("SHA256SUMS matches the archive", "no SHA256SUMS beside the archive")
        return
    base = os.path.basename(archive)
    recorded = None
    try:
        with open(sums, encoding="utf-8") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) >= 2 and parts[-1].lstrip("*") == base:
                    recorded = parts[0]
                    break
    except OSError as exc:
        rep.fail("SHA256SUMS matches the archive", str(exc))
        return
    if recorded is None:
        rep.fail("SHA256SUMS matches the archive", "no line for " + base)
        return
    actual = sha256(archive)
    if recorded.lower() != actual.lower():
        rep.fail("SHA256SUMS matches the archive",
                 "recorded {}… actual {}…".format(recorded[:16], actual[:16]))
    else:
        rep.ok("SHA256SUMS matches the archive", actual[:16] + "…")


def check_staged(rep, repo, archive, allow):
    """Only the handoff files may be in the commit.

    Unrelated local work swept into a handoff commit is invisible to the
    recipient and hard to unpick later.
    """
    code, out = git(repo, "diff", "--cached", "--name-only")
    if code != 0:
        rep.fail("staged files are handoff files only", "could not read the index")
        return
    staged = [p for p in out.splitlines() if p.strip()]
    if not staged:
        rep.fail("staged files are handoff files only", "nothing staged")
        return

    adir = os.path.relpath(os.path.dirname(archive), repo)
    permitted = {
        os.path.relpath(archive, repo),
        os.path.join(adir, "SHA256SUMS"),
        os.path.join(adir, "README.md"),
    }
    permitted.update(allow or [])
    extra = [p for p in staged if p not in permitted]
    if extra:
        rep.fail("staged files are handoff files only",
                 "{} unexpected: {}".format(len(extra), ", ".join(sorted(extra)[:5])))
    else:
        rep.ok("staged files are handoff files only",
               "{} file(s)".format(len(staged)))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="country repository (CLEWs-FJI, CLEWs-PHL)")
    ap.add_argument("--case", required=True, help="case name, e.g. Philippines_v16")
    ap.add_argument("--archive", help="the ZIP to publish (default: the one match under muio/)")
    ap.add_argument("--datastorage", help="MUIOGO WebAPP/DataStorage (default: sibling MUIOGO)")
    ap.add_argument("--staged", action="store_true", help="also gate what is staged for commit")
    ap.add_argument("--allow", action="append", metavar="PATH",
                    help="additional repo-relative path allowed in the commit (repeatable)")
    ap.add_argument("--json", metavar="PATH", dest="json_path", help="write the report here too")
    args = ap.parse_args(argv)

    repo = os.path.abspath(os.path.expanduser(args.repo))
    if not os.path.isdir(repo):
        print("error: no directory at " + repo, file=sys.stderr)
        return 2

    archive = args.archive
    if archive:
        archive = os.path.abspath(os.path.expanduser(archive))
    else:
        archive, err = find_archive(repo, args.case)
        if err:
            print("error: " + err, file=sys.stderr)
            return 2

    datastorage = args.datastorage
    if not datastorage:
        guess = os.path.join(os.path.dirname(repo), "MUIOGO", "WebAPP", "DataStorage")
        datastorage = guess if os.path.isdir(guess) else None
    if datastorage:
        datastorage = os.path.abspath(os.path.expanduser(datastorage))

    print("\n  push-handoff verification")
    print("  repo {}\n  case {}\n  zip  {}\n".format(repo, args.case, archive))

    rep = Report()
    check_repo_state(rep, repo)
    check_case_ignored(rep, repo)
    live = check_case_and_link(rep, repo, args.case, datastorage)
    check_case_identity(rep, live, args.case)
    check_archive(rep, archive, args.case)
    check_checksum(rep, archive)
    if args.staged:
        check_staged(rep, repo, archive, args.allow)

    rep.render()

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump({"repo": repo, "case": args.case, "archive": archive,
                       "checks": rep.rows}, fh, indent=2)

    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
