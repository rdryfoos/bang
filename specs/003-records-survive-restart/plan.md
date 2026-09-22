# Implementation Plan: Records Survive Restarting the Application

**Branch**: `potato/BAN-5` | **Date**: 2026-09-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification for `NFR-DUR-10, AC-DUR-10`

## Summary

BAN-1 already keeps records in one JSON file, read fresh on every call and replaced
whole on every write. That design should already survive a restart; nothing has proved
it. This card adds the proof, and changes source only if the proof finds a fault. Python 3
standard library only.

## Technical Context

**Language/Version**: Python 3.9.
**Primary Dependencies**: none; `pytest` for tests.
**Storage**: the existing JSON file (`WHMS_DATA_FILE`). No new storage.
**Testing**: `pytest`, proofs named `test_<ID>_…` under `tests/`.
**Project Type**: single project (CLI).
**Constraints**: no outbound network; no listener; file storage; Python only.
**Scale/Scope**: one owner, one machine, under 100 items.

## Constitution Check

| Principle | Status | How |
|-----------|--------|-----|
| I. Local only, no network | Pass | Local file only. The proof runs the application as a subprocess, which adds no network. |
| II. Storage is a file on disk | Pass | This card is the proof of the reason Constitution II gives. |
| III. Node or Python only | Pass | Python only. |
| IV. Promotion path only | Pass | Work stays on `potato/BAN-5`. |

SURFACE check: no listener (L1 stays "none"), no egress change (E1, E2). Nothing to add.

## Project Structure

### Documentation

```text
specs/003-records-survive-restart/
├── spec.md
├── plan.md
├── tasks.md
└── checklists/requirements.md
```

### Source Code

```text
src/whms/store.py            # UNCHANGED unless the proof finds a fault; then fix here
tests/test_durability.py     # NEW: NFR-DUR-10, AC-DUR-10
```

## Design

### What a restart is (spec A-1)

The proof starts the application as separate operating-system processes
(`python -m whms …`) against one temporary `WHMS_DATA_FILE`. One process ends before the
next begins, so nothing survives between them except what is on disk. An in-process call
would share module state and could not tell a durable record from a cached one.

### The proof (AC-DUR-10)

1. Process A: `lend add` two items with different dates out. Each exits 0.
2. Process B, new: read the records with `store.load()` and compare to what A saved: same
   items, same `date_out`, none lost, none altered.
3. The file is then given a `date_back` on one record, standing in for a return (spec
   A-4). Process C, new: read again; the returned record still has its `date_back` and the
   other still has none. `lend list` in a further new process shows only the unreturned one.
4. A fourth process adds a third item; a fifth reads all three, showing that a write after
   a restart keeps what came before.

Fixture values are invented and generic, never the reader's answers.

### If the proof fails

The fault is in `store.py` (for example a write that drops fields or a read that caches).
The fix goes there, in the same task as the proof, with `# @covers` extended to
`NFR-DUR-10`. It is not a new design.

### Privacy

No new module is added under `src/whms`; the scan of that directory in
`tests/test_no_network.py` is unchanged. The new test file uses only `subprocess` and
`json`.

## Complexity Tracking

None.

## Handoffs

- `US-RET-10`, `FR-RET-10`, `AC-RET-10` (BAN-3): when the return operation exists, the
  proof's stand-in for a return (step 3) should record it through that operation.
- `specs/backlog/tasks.md` T903 named `NFR-DUR-10`; this spec claims it. The card's
  change closes T903, as the card says.
