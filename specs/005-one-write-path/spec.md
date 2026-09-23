# Feature Specification: One Write Path

**Feature Branch**: `retrospective`

**Created**: 2026-09-22

**Status**: Done

**Input**: No card. Written by hand on 2026-09-22, outside the board, for work done in
PR #4. `ids: NFR-ENG-10, AC-ENG-10`

This specification is written after the fact. The promises it claims were created on
2026-09-21 and held in reserved backlog by an open task; the work that keeps them landed
in PR #4 with no card behind it, so no spec directory was made at the time. This is that
directory. Nothing here is a plan: every line describes what is already true of the tree
and is proved by a named test.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The record means one thing (Priority: P1)

**NFR-ENG-10** — Records are written by one path: the screens call the engine's
operations and keep no write of their own.

The owner lends a thing at the command line and marks it returned in the browser, or the
other way round, and the record is the same record either way. Nothing about the software
says which door was used, because there is only one place the file is written and both
doors knock on it.

**Why this priority**: On 2026-09-21 two cards implemented marking a thing returned, one
in the engine and one in the browser screens, and both passed every check this project
had. Nothing was asking whether a promise was already served: the checks ask whether a
branch proves an ID, and both branches did. Two paths that write the same record are not
a duplicated function. They are two answers to the question of what a record is, and the
second one to run wins.

**Independent Test**: Read every module under `src/whms` and look for a file outside the
engine that can put a record on disk. Then drive the browser screens through a lend, a
listing and a return, and watch each one pass through the engine on its way.

**Acceptance Scenarios**:

1. **AC-ENG-10** — **Given** the source under `src/whms`, **When** every module outside
   the engine is read for a call that writes a file, **Then** there is none.
2. **AC-ENG-10** — **Given** the browser screens running over a records file, **When** the
   owner lends a thing, opens the outstanding list and marks the thing returned, **Then**
   each of those three went through the engine's operations to reach the file.

---

### Edge Cases

- **A screen that reads without writing.** Reading is not the promise. The screens read
  through the engine too, but a read that went another way would take nothing from the
  record; a write that went another way would define it.
- **A helper both sides call.** One function called from two places is not two paths. The
  promise is about the number of answers to what a record is, not the number of callers.
- **A new screen.** It keeps the promise by calling the engine, as the existing ones do,
  and the proof holds without being changed, because the proof reads whatever is there
  rather than a list of files it knows about.
- **A write that is not to the records file.** A log line, a temporary file, a served
  page. The proof looks for a call that could put a record on disk, and it is deliberately
  wider than the records file: a screen that writes anything at all is a screen that has
  started to keep state, which is where a second record comes from.

## Clarifications

### Session 2026-09-22

- Q: What is the engine? → A: The modules that hold what a record is and where it lives:
  `src/whms/store.py`, `src/whms/records.py`, `src/whms/outstanding.py`. Everything else
  under `src/whms` is a screen or a command line. Source: the promise's own words, "the
  screens call the engine's operations".
- Q: Did the duplication ship into this repository? → A: No. `src/whms/web.py` has no
  file access at all; its return handler calls the engine. What was owed was the proof
  that nothing else can quietly start writing, not a change to the application.
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

- **NFR-ENG-10**: Records are written by one path: the screens call the engine's
  operations and keep no write of their own.
  - No file under `src/whms` other than the engine modules writes a record, and the
    browser screens' lend, return and list go through the engine (AC-ENG-10).

### Key Entities

- **The engine**: `store.py`, `records.py` and `outstanding.py`. What a record is, where
  it lives, and which records are outstanding.
- **A screen**: any module under `src/whms` that presents records to a person, currently
  `web.py` and `pages.py`. It may read and present; it may not write.

## Success Criteria *(mandatory)*

- **SC-001** (AC-ENG-10): Reading the source of every module under `src/whms` outside the
  engine yields zero calls that could put a record on disk.
- **SC-002** (AC-ENG-10): A lend, a listing and a return made through the browser screens
  each pass through an engine operation, with no fourth way to the file.

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
| A screen writes the records file itself | Two answers to what a record is; the last write wins and the owner cannot tell which ran | NFR-ENG-10, AC-ENG-10 |
| A second implementation passes because every behavioural test still passes | The board goes green over work that was already done, twice | AC-ENG-10, first scenario |
| A new screen is added that keeps its own state | The same failure again, later, with nobody watching for it | AC-ENG-10, proof reads the tree rather than a list |
