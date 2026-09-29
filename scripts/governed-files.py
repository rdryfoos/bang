#!/usr/bin/env python3
"""A card may not change the machinery that judges it.

On 2026-09-20 a Build worker, working on its own card branch, edited `scripts/gate.sh`
and `scripts/gate.conf`. The change was correct, which is the uncomfortable part: the
card fixed the script that decides whether the card passes, and nothing anywhere
noticed or objected.

This is the objection. Run over a card branch, it compares the branch against the
default branch and reds on any change to a governed path, naming the files. It is a
Gate line rather than a hook, so it refuses at the moment a card is judged rather than
at the moment an agent commits, and it refuses regardless of what else passed.

Governed paths are the project's own machinery: the scripts, the gate script and its
configuration, the entry checks, and the hooks. Changing them is project work, done by
hand on its own branch, and it is not a thing a card does on the way past.

design/ joined the list on 2026-09-20, when the project gained a picture of the software.
It stays on it after the 2026-09-29 ruling that the screens are a sketch: a sketch a card
may redraw is a sketch that stops being the reference it was kept for.

The four documents joined on 2026-09-29: PRD.md, CASE.md, CONSTITUTION.md and SURFACE.md.
Every prompt on the board had told a worker not to touch any of them for as long as the
prompts had existed, and nothing refused the touch, so the rule held for exactly as long as
each agent kept reading its own instructions. They are not machinery in the sense the
scripts are; they are what the machinery is pointed at. PRD.md is the registry, so a card
that edited it would be marking its own homework more completely than one that edited the
gate, which only decides whether the promise was kept. CASE.md is what the promises were
made about, CONSTITUTION.md is what the build must be true of, and SURFACE.md is what it
may touch: a card that rewrote any of those would be changing the question rather than
answering it.

Usage: governed-files.py [--base BRANCH] [--head REF]
Exit 0 clean, 1 a governed file changed, 2 cannot tell.
Written by the born-threaded practice; MIT.
"""
import argparse
import os
import re
import subprocess
import sys

GOVERNED = (
    "scripts/",
    ".specify/extensions/specassay-check/scripts/",
    ".github/workflows/",
    "design/",
    "PRD.md",
    "CASE.md",
    "CONSTITUTION.md",
    "SURFACE.md",
)

# Documents about the project rather than parts of it. A card may not change them,
# but neither are they machinery that judges a card, so they are named here rather
# than left to be caught by a rule meant for something else. Nothing refuses a change
# to these; they are listed so that a reader can see they were considered.
NOT_GOVERNED = (
    "BANG.md",
    "README.md",
    "FIRST-CARDS.md",
    "cannon-template/",
)


def git(argv):
    r = subprocess.run(["git"] + argv, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def conf(name, default):
    try:
        for line in open("scripts/gate.conf"):
            m = re.match(rf'^\s*{name}="?([^"#]*)"?', line.strip())
            if m and m.group(1).strip():
                return m.group(1).strip()
    except OSError:
        pass
    return default


def main():
    p = argparse.ArgumentParser(description="A card may not change the machinery that judges it.")
    p.add_argument("--base", help="the branch a card's work is measured against")
    p.add_argument("--head", default="HEAD", help="the card's head; HEAD by default")
    args = p.parse_args()

    base = args.base or conf("DEFAULT_BRANCH", "main")
    if git(["rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"]) is None:
        print(f"governed-files: this checkout has no {base} to compare against", file=sys.stderr)
        return 2

    merge_base = git(["merge-base", base, args.head])
    if merge_base is None:
        print(f"governed-files: {args.head} and {base} share no history", file=sys.stderr)
        return 2

    if merge_base == git(["rev-parse", f"{args.head}^{{commit}}"]):
        print("governed-files: green, this is not a card branch (nothing ahead of "
              f"{base})")
        return 0

    changed = git(["diff", "--name-only", f"{merge_base}..{args.head}"]) or ""
    hits = sorted({f for f in changed.splitlines()
                   if any(f.startswith(g) for g in GOVERNED)
                   and not any(f.startswith(n) for n in NOT_GOVERNED)})

    if not hits:
        print(f"governed-files: green, no governed file changed on this branch")
        return 0

    print(f"governed-files: RED. This branch changes {len(hits)} file(s) the project "
          "governs, and a card may not change the machinery that judges it:", file=sys.stderr)
    for f in hits:
        print(f"governed-files:   {f}", file=sys.stderr)
    print("governed-files: if the change is right, it is project work: take it out of this "
          "branch and do it by hand on its own.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
