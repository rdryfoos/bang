# Constitution: Who Has My Stuff

Ratified 2026-09-20, at the project's birth, before any card was built. Four constraints.
They are not preferences, and a spec that needs one of them relaxed is a spec that stops
and asks rather than a spec that proceeds.

The case this serves is in `CASE.md`. The promises are in `PRD.md`, and every ID there is
created by the tool rather than written by hand.

## I. Local only. No network.

The application makes no outbound network request, for any reason, at any time. No
telemetry, no crash reporting, no sync, no cloud storage, no update check, no third-party
service, no address book or contacts access.

This is the promise the reader made in their own words, and it is the one an agent is
most likely to break without being asked. `NFR-PRIV-10` states it and `AC-PRIV-20` proves
it. A dependency that phones home breaks this constraint as surely as code that does.

If a feature appears to require the network, that is a finding to report, not a thing to
build.

## II. Storage is a file on disk.

Records live in a file the owner could open, copy, back up or delete without the
application's help. No database server, no service, no account, no container, no
directory the owner cannot find.

The reader's own assumptions are the reason: one person, one machine, fewer than a
hundred items, ever. `NFR-DUR-10` is the promise that records survive a restart, and a
file on disk is how.

## III. Node or Python only.

The implementation uses the runtimes this machine already has for this work: Node, or
Python. No second language, no compiler toolchain, no runtime the reader would have to
install before the thing runs.

The reader followed a page that installed exactly what was needed and no more. A build
that asks them for another installation has broken the page's promise, not just this
constraint.

## IV. The promotion path is the only way onto main.

A change reaches `main` by one route: a card's branch, merged by the promotion the
template names, with the Gate passing on the merge commit and a receipt written for that
SHA. No direct commit, no branch merged by hand, no exception for a small fix.

`scripts/pre-commit` refuses a commit on `main` unless the promotion sets its flag, and
`scripts/done-check.py` refuses to let a card into Done unless the receipt exists for the
commit that brought its change in. SURFACE row LC2 declares what that receipt is worth:
the Gate ran on this SHA on the machine that built it, and no second party attested it.

This constraint exists because an agent was found standing in the project's own checkout
on `main`, able to commit there, on 2026-09-20. Nothing stopped it but its own judgment.

## Amendment

These four are amended the way everything else here changes: by the operator's hand, in
a commit that says what changed and why, on a branch that reaches `main` by the
promotion path like any other. An agent may propose an amendment and may not make one.
