#!/usr/bin/env python3
"""Refuse a commit on the default branch unless a promotion is making it.

Constitution IV: a change reaches main by one route, a card's branch merged by the
promotion the template names. This is the guard that makes that structural rather than
customary, for the case the project has already met: an agent standing in the primary
checkout on the default branch, one `git commit` away from putting work on main with no
branch, no review and no promotion. On 2026-09-20 the only thing that stopped it was the
agent noticing where it was.

The promotion sets ESTATE_PROMOTION=1 and is the only caller that may. A human doing
project work by hand sets it too, deliberately, and that use is visible in the shell
history and in this file's reason for existing.

Exit 0 allowed, 1 refused, 2 cannot tell. Written by the born-threaded practice; MIT.
"""
import os
import pathlib
import re
import subprocess
import sys


def conf_value(root, name, default):
    path = root / "scripts" / "gate.conf"
    if not path.exists():
        return default
    for line in path.read_text().splitlines():
        m = re.match(rf'^\s*{name}="?([^"#]*)"?', line.strip())
        if m and m.group(1).strip():
            return m.group(1).strip()
    return default


def main():
    try:
        root = pathlib.Path(subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip())
    except subprocess.CalledProcessError:
        print("no-commit-on-main: not a git checkout", file=sys.stderr)
        return 2

    default_branch = conf_value(root, "DEFAULT_BRANCH", "main")
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True).stdout.strip()

    if branch != default_branch:
        return 0
    if os.environ.get("ESTATE_PROMOTION") == "1":
        return 0

    print(f"no-commit-on-main: commit refused. This checkout is on {default_branch}, and "
          "the promotion path is the only way onto it (constitution IV).", file=sys.stderr)
    print("no-commit-on-main: work on a card's branch and let the drag from Review to Done "
          "merge it. If you are the promotion, set ESTATE_PROMOTION=1 and mean it.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
