#!/usr/bin/env python3
"""Append one gate receipt to the project's ledger, keyed by the SHA the Gate ran on.

The ledger is journal/receipts.jsonl: one append-only file, records stamped in UTC,
found by SHA and never by date.

Called by scripts/gate.sh, and only when the project declares RECEIPT_SOURCE=local: an
project with a forge behind it points the Done check at a CI run instead, and this
writes nothing there. Every value arrives in the environment rather than on a command
line, so no card text and no SHA reaches a process listing.

The record is its own kind rather than a note. The recorder's one-shot note mode
stamps actor "hand", and a receipt written by a script attributed to a hand is the
attribution this project exists to prevent. Written by the born-threaded practice; MIT.
"""
import datetime, json, os, re, sys

def main():
    prefix = os.environ.get("RECEIPT_PREFIX") or "journal"
    sha = (os.environ.get("RECEIPT_SHA") or "").strip()
    result = (os.environ.get("RECEIPT_RESULT") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        print("write-receipt: refusing to write a receipt without a full SHA", file=sys.stderr)
        return 1
    if result not in ("pass", "fail"):
        print(f"write-receipt: result must be pass or fail, not {result!r}", file=sys.stderr)
        return 1
    try:
        code = int(os.environ.get("RECEIPT_CODE") or "0")
    except ValueError:
        code = -1
    rec = {"kind": "gate-receipt", "sha": sha, "result": result, "gate_exit": code,
           "card": os.environ.get("RECEIPT_CARD") or "", "runner": "local",
           "actor": "orchestrator",
           "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    os.makedirs(prefix, exist_ok=True)
    # One append-only ledger, found by SHA. It carries no date in its name on purpose:
    # the record is stamped in UTC and an earlier version named the file by the local
    # date, so for part of every day a reader looking for today's receipts read the
    # wrong file and found nothing. Ruled 2026-09-20.
    path = os.path.join(prefix, "receipts.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print(f"gate: receipt written, {result} at {sha[:7]}, into {path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
