#!/usr/bin/env python3
"""Every registry row and the state it is in, as a table.

What section 4 of the review packet falls back to when there is no base to compare
against, which is true of the first promotion an project ever makes. It says less than a
Thread Report, and it says something true, which beats a section that vanishes.
"""
import collections
import json
import sys


def main():
    if len(sys.argv) < 2:
        print("manifest-table: a manifest path is required", file=sys.stderr)
        return 2
    try:
        rows = (json.load(open(sys.argv[1])) or {}).get("rows") or []
    except (OSError, ValueError) as err:
        print(f"manifest-table: could not read the manifest ({err.__class__.__name__})",
              file=sys.stderr)
        return 2
    by = collections.defaultdict(list)
    for row in rows:
        by[row.get("status") or "unknown"].append(row.get("id") or "?")
    print("| State | Count | IDs |")
    print("|---|---|---|")
    for state in sorted(by):
        ids = ", ".join("`%s`" % i for i in sorted(by[state]))
        print(f"| `{state}` | {len(by[state])} | {ids} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
