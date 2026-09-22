# scripts

Two controls keep the reader's answers out of this repository, and neither one
is a Gate. That is stated here rather than assumed, because this family's
habit is the opposite: in Chalkup the Gate is the control and the hook is the
courtesy.

## One: the answers are not in the worktree

`case.env` points at `~/bang/case/CASE.md`. The form ships blank as `CASE.md`
here; the filled copy lives one directory up, outside the worktree, where no
git command run inside this repository can reach it. Not ignored. Outside.
An ignore rule is a convention that `git add -f` beats, and a stray `git add
-A` from a directory nobody was thinking about beats an ignore rule by
accident, which is how three stray worktrees were swept into a commit in the
project next door on the morning this was written.

## Two: `no-records-in-repo.py`, for the records rather than the file

What it guards changed shape on 2026-09-20 and so did it. The CASE used to hold
real items and real borrowers, and the script compared every staged change against
it. A case describes the problem and uses invented examples now, so there is
nothing in it to leak. The records are the thing worth guarding, and they live in
the application's own data file, outside every repository.

So the script looks for records by their shape rather than by a list of values it
has to be told: a committed JSON document holding objects with a borrower and a
date out. Tests are the obvious near miss and are allowed, because a record
written in Python inside a test is the test's fixture, not the owner's data. It
prints the file and the count, never the values.

It caught one thing on the first commit it ever ran against, which is recorded
in the phase 1 log rather than here.

## Why neither can be a Gate, and what that costs

A CI job cannot run this check, because CI would have to hold the answers in
order to look for them, and the whole promise is that they exist in one place
on one machine.

Committing salted hashes so CI could compare without holding the values was
considered and declined: personal names are low entropy, a salt in the
repository makes the hashes readable by anyone who wants them, and a salt kept
local puts us back where we started.

So this is the one control here that is local-only by construction, and
`--no-verify` beats it. It is declared rather than relied on quietly. The
control that does not depend on anyone's discipline is the first one: the file
is somewhere git cannot see.

## A third, for the duration of the rehearsal

This repository has no git remote. `git remote -v` prints nothing. Nothing to
push to is a stronger control than a script at the push.

## try.sh, and what it does not do yet

`scripts/try.sh` runs the thing the card built and prints what it did. The Cannon's Try
it button runs this file and nothing else: it takes no arguments, so nothing from the
board, the card or the browser reaches a command line, and the project governs the file.
It seeds a temporary data file rather than reading the owner's real records, so a
reviewer sees the software work without seeing whose things are lent to whom.

### Debt, recorded 2026-09-20 rather than left implicit

- **A per-card try command is owed.** `try.sh` knows one application, because this
  project has one. A card should be able to say what trying *it* means, and the button
  should run that rather than a file that knows the whole project by heart.
- **A "Try it" section in the review packet is owed.** The packet gives a reviewer the
  branch, the diff, the Gate and the thread. It should also give them what the software
  did, so the answer is on the card and not only behind a button.

Neither blocks the button. Both are the difference between a demo and a tool.
