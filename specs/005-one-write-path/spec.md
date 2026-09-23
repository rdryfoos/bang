# Feature Specification: One Write Path

**Feature Branch**: `retrospective`

**Created**: 2026-09-22

**Status**: Done

**Input**: No card. Written by hand on 2026-09-22, outside the board, for work done in
PR #4, and narrowed on 2026-09-23 when the browser came out of the shipped tree.
`ids: NFR-ENG-10, AC-ENG-10`

This specification is written after the fact. The promises it claims were created on
2026-09-21 and held in reserved backlog by an open task; the work that keeps them landed
in PR #4 with no card behind it, so no spec directory was made at the time. This is that
directory. Nothing here is a plan: every line describes what is already true of the tree
and is proved by a named test.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The record means one thing (Priority: P1)

**NFR-ENG-10** — Records are written by one path: every entry point onto them, present
and future, calls the engine's operations and keeps no write of its own.

However many doors the software grows, the record is the same record through every one
of them. Nothing about it says which door was used, because there is only one place the
file is written and every door knocks on it. Today there is one door, the command line.
Card one adds the screens; the rule is waiting for them.

**Why this priority**: On 2026-09-21 two cards implemented marking a thing returned, one
in the engine and one in the browser screens, and both passed every check this project
had. Nothing was asking whether a promise was already served: the checks ask whether a
branch proves an ID, and both branches did. Two paths that write the same record are not
a duplicated function. They are two answers to the question of what a record is, and the
second one to run wins.

**Independent Test**: Read every module under `src/whms` and look for a file outside the
engine that can put a record on disk. The reading is the whole test, and deliberately so:
it names no entry point, so it holds for the ones that do not exist yet.

**Acceptance Scenarios**:

1. **AC-ENG-10** — **Given** the source under `src/whms`, **When** every module outside
   the engine is read for a call that writes a file, **Then** there is none.
2. **AC-ENG-10** — **Given** a module added to `src/whms` later, by a card or by a hand,
   **When** it writes a record of its own rather than calling the engine, **Then** the
   same reading fails, without anybody having added it to a list.

---

### Edge Cases

- **An entry point that reads without writing.** Reading is not the promise. A read that
  went another way would take nothing from the record; a write that went another way
  would define it.
- **A helper both sides call.** One function called from two places is not two paths. The
  promise is about the number of answers to what a record is, not the number of callers.
- **A new entry point.** The screens card one builds, a second command, anything. It
  keeps the promise by calling the engine, and the proof holds without being changed,
  because the proof reads whatever is there rather than a list of files it knows about.
  This is the case the test was really written for.
- **A write that is not to the records file.** A log line, a temporary file, a served
  page. The proof looks for a call that could put a record on disk, and it is deliberately
  wider than the records file: an entry point that writes anything at all has started to
  keep state, which is where a second record comes from.

## Clarifications

### Session 2026-09-22

- Q: What is the engine? → A: The modules that hold what a record is and where it lives:
  `src/whms/store.py`, `src/whms/records.py`, `src/whms/outstanding.py`. Everything else
  under `src/whms` is an entry point onto them. Source: the promise's own words, "every
  entry point onto them ... calls the engine's operations".
- Q: Did the duplication ship into this repository? → A: No. The browser that carried the
  second write path on the rehearsal board never shipped here with one: its return handler
  called the engine. What was owed was the proof that nothing else can quietly start
  writing, not a change to the application. On 2026-09-23 the browser came out of the
  shipped tree entirely, to be card one's work; the proof stayed, because it was never
  about the browser.
- Q: What counts as writing, for the proof? → A: A call that could put bytes on disk:
  `open` in a writing mode, or a call on `os`, `shutil`, `tempfile`, `json` or `pathlib`
  that creates, replaces or removes a file. Qualified by module on purpose, so that
  `text.replace(",", " ")` in `pages.py` is not read as a screen writing records.
- Q: Why does the proof read the source rather than only exercise the app? → A: Because
  the failure it is for is a path nothing exercises yet. The second implementation on
  2026-09-21 passed every behavioural test there was. A proof that only drives the app
  would have passed then too.

## Requirements *(mandatory)*

### Functional Requirements

- **NFR-ENG-10**: Records are written by one path: every entry point onto them, present
  and future, calls the engine's operations and keeps no write of its own.
  - No file under `src/whms` other than the engine modules writes a record, read from the
    source, binding every entry point present and future (AC-ENG-10).

### Key Entities

- **The engine**: `store.py`, `records.py` and `outstanding.py`. What a record is, where
  it lives, and which records are outstanding.
- **An entry point**: any module under `src/whms` that puts records in front of a person,
  currently `cli.py` and the screens card one will build. It may read and present; it may
  not write.

## Success Criteria *(mandatory)*

- **SC-001** (AC-ENG-10): Reading the source of every module under `src/whms` outside the
  engine yields zero calls that could put a record on disk.
- **SC-002** (AC-ENG-10): A module added under `src/whms` after this specification was
  written is held to the same rule by the same reading, with nobody having to remember
  to add it.

## Assumptions

- **A-1**: The engine is the three modules named above. Adding a fourth would be a change
  to this specification, not a detail of one.
- **A-2**: A read that avoided the engine would be a fault but not this fault. The promise
  is about writing, and the proof is written to match the promise.
- **A-3**: The proof reads the tree as it finds it. A module added later is covered
  without anybody remembering to add it, and that is the point: the failure this is for
  was nobody remembering.

## SpecAssay — durable IDs (required)

IDs are inherited from PRD.md. None is created here. Scope of this feature:
`NFR-ENG-10`, `AC-ENG-10`.

## Risk & failure modes (required)

| Failure | User impact | Mitigation / trace |
|---------|-------------|-------------------|
| An entry point writes the records file itself | Two answers to what a record is; the last write wins and the owner cannot tell which ran | NFR-ENG-10, AC-ENG-10 |
| A second implementation passes because every behavioural test still passes | The board goes green over work that was already done, twice | AC-ENG-10, first scenario |
| A new entry point is added that keeps its own state | The same failure again, later, with nobody watching for it | AC-ENG-10, second scenario |
