# Tasks: One Write Path

**Input**: [spec.md](./spec.md)

**Scope**: `NFR-ENG-10, AC-ENG-10`

Written by hand on 2026-09-22, outside the board, for work done in PR #4. Every task here
is closed, because the work landed before the directory did. The one task is the one that
was reserved in `specs/backlog/tasks.md` as T906; it keeps its number, so a reader
following the backlog's history arrives here.

## Phase 1: The proof

- [x] T906 Make the screens call the engine's operations and keep no write of their own. The screens already did: `src/whms/web.py` has no file access at all and its return handler calls the engine, so what was owed was proof that nothing else can quietly start writing. `tests/test_one_write_path.py` holds two tests named for the criterion: one reads every module under `src/whms` and fails any file outside the engine that can put a record on disk, the other drives the screens and asserts that lending, listing and returning each went through the engine. `src/whms/store.py` carries the marks; it is the one path. Proved by putting the duplication back into `web.py`: the other 25 tests stayed green over a second write path and only these two failed. **Carries**: NFR-ENG-10, AC-ENG-10

## Dependencies and order

- None. One task, already closed.

## Notes

- The reservation in `specs/backlog/tasks.md` closes with this directory. It was held open
  until now because an ID is claimed by a spec or by an open task, and until this file
  existed the open task was the only claim on these two.
- No task here adds a promise, an ID or a dependency.
