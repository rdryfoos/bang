#!/usr/bin/env python3
"""Refuse a commit that carries the application's records into the repository.

This replaces a script that compared every staged change against the reader's filled
CASE and refused anything quoting it. That script existed because the CASE held real
items and real borrowers. It does not any more: a case describes the problem and uses
invented examples, and real records live in the application's own data file, outside
every repository. So the thing worth guarding changed shape, and so did the guard.

What it looks for is the records themselves, by their shape rather than by a list of
values it has to be told. A lending record is an object carrying a name, a borrower and
a date out; a data file is an array of them. Nothing in this repository should contain
one, not as a file, not as a fixture, not pasted into a spec.

Tests are the obvious near miss, and they are allowed: a test writes records to a
temporary file at run time, and a record written in Python inside a test file is the
test's fixture, not the owner's data. What is refused is a JSON document, committed,
holding records.

Exit 0 clean, 1 on a finding, 2 when it cannot tell. It names the file and the count,
never the values. Written by the born-threaded practice; MIT.
"""
import json
import subprocess
import sys

RECORD_KEYS = {"borrower", "date_out"}


def looks_like_record(value) -> bool:
    return isinstance(value, dict) and RECORD_KEYS.issubset({str(k) for k in value})


def records_in(text: str) -> int:
    """How many lending records a document holds, or zero if it is not one."""
    try:
        data = json.loads(text)
    except ValueError:
        return 0
    if looks_like_record(data):
        return 1
    if isinstance(data, list):
        return sum(1 for item in data if looks_like_record(item))
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list):
                found = sum(1 for item in value if looks_like_record(item))
                if found:
                    return found
    return 0


def main():
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"],
                            capture_output=True, text=True)
    if staged.returncode != 0:
        print("no-records-in-repo: could not read the staged changes", file=sys.stderr)
        return 2

    findings = []
    for rel in staged.stdout.split():
        if not rel.endswith(".json"):
            continue
        blob = subprocess.run(["git", "show", f":{rel}"], capture_output=True, text=True)
        if blob.returncode != 0:
            continue
        count = records_in(blob.stdout)
        if count:
            findings.append((rel, count))

    if not findings:
        return 0

    print("no-records-in-repo: commit refused. The application's records do not belong "
          "in this repository:", file=sys.stderr)
    for rel, count in findings:
        print(f"no-records-in-repo:   {rel}: {count} lending record(s)", file=sys.stderr)
    print("no-records-in-repo: records live in the data file the application writes, "
          "outside every repository. The values are not printed here.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
