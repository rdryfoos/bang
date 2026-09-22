# Implementation Plan: Record a Lent Item

**Branch**: `potato/BAN-1` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification for `US-LEND-10, FR-LEND-10, AC-LEND-10, AC-LEND-20, NFR-PRIV-10, AC-PRIV-20, AC-PRIV-10`

## Summary

A small command-line tool. `lend add` saves an item record to a JSON file on disk;
`lend list` prints every saved item. Nothing else. Python 3, standard library only,
no network module imported anywhere.

## Technical Context

**Language/Version**: Python 3.9 (the interpreter on this machine is 3.9.6; no
`match`, no `X | Y` type unions).
**Primary Dependencies**: none. Standard library only. `pytest` for tests.
**Storage**: one JSON file, path from `WHMS_DATA_FILE`, default
`~/.who-has-my-stuff/items.json`. Outside the repository, findable by the owner.
**Testing**: `pytest`, proofs named `test_AC_<AREA>_<NN>_…` under `tests/`.
**Target Platform**: this machine, one owner.
**Project Type**: single project (CLI).
**Performance Goals**: none beyond "immediately"; fewer than a hundred items.
**Constraints**: no outbound network; no listener; file storage; Node or Python only.
**Scale/Scope**: one owner, one machine, under 100 items.

## Constitution Check

| Principle | Status | How |
|-----------|--------|-----|
| I. Local only, no network | Pass | No socket, http, urllib, ssl, or third-party client imported. No telemetry. Proven by AC-PRIV-20. |
| II. Storage is a file on disk | Pass | A JSON file the owner can open, copy or delete. No database, no service. |
| III. Node or Python only | Pass | Python only, standard library. |
| IV. Promotion path only | Pass | Work stays on `potato/BAN-1`; nothing here touches `main`. |

SURFACE check: no new listener (L1 stays "none"), no new egress (E1, E2 unchanged). A
CLI adds neither. A web or local-server front end would need a SURFACE row and is
out of this card.

## Project Structure

### Documentation

```text
specs/001-lend-item-record/
├── spec.md
├── plan.md
├── tasks.md
└── checklists/requirements.md
```

### Source Code

```text
src/whms/
├── __init__.py
├── records.py     # Item record, validation, refusal reasons
├── store.py       # Read and atomic-write the JSON file
└── cli.py         # `lend add`, `lend list`

tests/
├── test_lend_item.py     # AC-LEND-10, AC-LEND-20
├── test_no_network.py    # AC-PRIV-20
└── test_repo_privacy.py  # AC-PRIV-10
```

`src/**` and `tests/**` are the globs the traceability Gate scans, so the layout is
already inside its configuration.

## Design

### Data model (FR-LEND-10)

Item record: `name` (non-blank string), `borrower` (non-blank string), `date_out`
(ISO `YYYY-MM-DD`, a real calendar date). Stored as a JSON list of objects in
insertion order. No id, no returned field: those belong to US-RET-10.

Validation returns every missing or invalid field with a reason; a record is saved
only when the list is empty. Whitespace-only counts as blank. Values are stored
trimmed.

### Commands (AC-LEND-10, AC-LEND-20)

- `lend add --name N --borrower B --date-out YYYY-MM-DD`: validates, appends,
  writes, prints the saved record, exit 0. On refusal: writes nothing, prints
  `refused: a borrower is required` (or the matching reason) to stderr, exit 2.
- `lend list`: prints every saved item, one per line, name, borrower, date out. It
  reads the file on each call, so an item saved a moment ago is in it. Order and
  empty wording are US-OUT-10's to settle (spec A-4); this card prints in
  insertion order.

### Storage (Constitution II)

Read the file fresh per command. Write to a sibling temp file and `os.replace` it in,
so a failed write leaves the earlier records intact. A write error is reported and
exits non-zero; success is printed only after the replace.

### Privacy (NFR-PRIV-10, AC-PRIV-20, AC-PRIV-10)

- No network module in `src/`. `test_no_network.py` runs `add` and `list` in-process
  with `socket.socket`, `socket.create_connection` and `socket.getaddrinfo` patched
  to fail the test on call, and statically checks the modules `src/whms` imports
  against a denylist.
- `test_repo_privacy.py` proves the part a Gate can: the default data path and every
  path the tests use resolve outside the worktree, and running `add` and `list`
  leaves the worktree with no new file. All fixture values are invented and
  generic, never taken from the reader's answers.
- The content scan for values from the reader's answers is `scripts/no-private-answers.py`,
  a hook, not a Gate (SURFACE LC1). It cannot run in CI. The plan does not pretend
  otherwise: AC-PRIV-10 is proven here structurally, and the hook holds the content
  rule at commit time.

## Complexity Tracking

None. No constitution violation to justify.

## Handoffs

- `AC-OUT-10`, `AC-OUT-20`, `FR-OUT-10`: the list command here is deliberately the
  smallest thing that makes AC-LEND-10 true. The OUT card owns ordering and the empty
  state.
- `NFR-DUR-10`: the atomic write serves it, but it is not carried or claimed here.
