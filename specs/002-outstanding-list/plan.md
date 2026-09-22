# Implementation Plan: See What Is Still Out

**Branch**: `potato/BAN-2` | **Date**: 2026-09-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification for `US-OUT-10, FR-OUT-10, AC-OUT-10, AC-OUT-20`

## Summary

Make `lend list` the outstanding list: filter out items marked returned, sort the rest
by date out ascending, and print a plain sentence when none remain. Python 3 standard
library only, built on the modules BAN-1 already put in `src/whms`.

## Technical Context

**Language/Version**: Python 3.9 (no `match`, no `X | Y` unions).
**Primary Dependencies**: none. Standard library; `pytest` for tests.
**Storage**: the existing JSON file (`WHMS_DATA_FILE`). Read only; this card writes nothing.
**Testing**: `pytest`, proofs named `test_AC_<AREA>_<NN>_…` under `tests/`.
**Project Type**: single project (CLI).
**Constraints**: no outbound network; no listener; file storage; Python only.
**Scale/Scope**: one owner, one machine, under 100 items.

## Constitution Check

| Principle | Status | How |
|-----------|--------|-----|
| I. Local only, no network | Pass | Reads a local file; no new import beyond the standard library, none of it networking. |
| II. Storage is a file on disk | Pass | Same JSON file, unchanged format for existing fields. |
| III. Node or Python only | Pass | Python only. |
| IV. Promotion path only | Pass | Work stays on `potato/BAN-2`. |

SURFACE check: no listener (L1 stays "none"), no egress change (E1, E2). Nothing to add.

## Project Structure

### Documentation

```text
specs/002-outstanding-list/
├── spec.md
├── plan.md
├── tasks.md
└── checklists/requirements.md
```

### Source Code

```text
src/whms/
├── outstanding.py   # NEW: select unreturned, order by date out, empty message
└── cli.py           # MODIFIED: `lend list` uses outstanding.py

tests/
└── test_outstanding.py   # NEW: AC-OUT-10, AC-OUT-20, FR-OUT-10
```

## Design

### Selection and order (FR-OUT-10, AC-OUT-10)

`outstanding.select(items)` returns the items with no `date_back` value, sorted by
`date_out` ascending with a stable sort, so ties keep file order (spec A-3, not a
promise). `date_out` is stored `YYYY-MM-DD`, so string order is date order. An item is
returned exactly when its record has a non-empty `date_back` (spec A-1; FR-RET-10's
"date back"). This card only reads that key; BAN-3 writes it.

### The empty state (AC-OUT-20)

When `select` returns nothing, `lend list` prints one sentence, `Nothing is out.`,
to stdout, exit 0. The words are the plan's choice, since the PRD fixes none (spec A-5),
and tests assert a non-empty message containing no item line, not this exact string
being a promise. A missing data file takes the same path.

### Read failures (spec A-4)

Unchanged from BAN-1: an unreadable or malformed file prints `error: could not read
the records: …` to stderr and exits 1, never the empty message.

### Privacy

No new module beyond `datetime`-free sorting; no network import. BAN-1's
`test_no_network.py` scans `src/whms`, so it covers `outstanding.py` unchanged.
Fixtures use invented generic values, never the reader's answers.

## Complexity Tracking

None.

## Handoffs

- `US-RET-10`, `FR-RET-10`, `AC-RET-10` (BAN-3): must record the date back under the
  key `date_back` for this list to drop the item. Not claimed here.
- `AC-OUT-20`: the backlog (`specs/backlog/tasks.md`, T901) says it is expected to ship
  as tracked debt. Whether Build leaves its task open is the operator's call; the task
  here is written so it can be left open without touching the others.
- `NFR-DUR-10`: not carried or claimed here.
- `specs/backlog/tasks.md` T900 and T901 name IDs this spec now claims; their
  reservation expires with this spec (per that file). Removing them is left to the
  change that lands this card, since this worker edits only the card's spec.
