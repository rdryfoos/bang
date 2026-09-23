# Tasks: One Write Path

**Input**: [spec.md](./spec.md)

**Scope**: `NFR-ENG-10, AC-ENG-10`

Written by hand on 2026-09-22, outside the board, for work done in PR #4. Every task here
is closed, because the work landed before the directory did. The one task is the one that
was reserved in `specs/backlog/tasks.md` as T906; it keeps its number, so a reader
following the backlog's history arrives here.

## Phase 1: The proof

- [x] T906 Make every entry point call the engine's operations and keep no write of its own. What was owed was never a code change: nothing outside the engine wrote a record, and what was missing was proof that nothing could quietly start. `tests/test_one_write_path.py` reads every module under `src/whms` and fails any file outside the engine that can put a record on disk. It names no entry point, so it holds for the ones that do not exist yet, which is the case it was written for. `src/whms/store.py` carries the marks; it is the one path. Proved on 2026-09-22 by putting the duplication back into the browser module that shipped then: the other tests stayed green over a second write path and only this one failed. The browser came out of the shipped tree on 2026-09-23 to be card one's work; the test stayed, and it is what card one is held to. **Carries**: NFR-ENG-10, AC-ENG-10

## Dependencies and order

- None. One task, already closed.

## Notes

- The reservation in `specs/backlog/tasks.md` closes with this directory. It was held open
  until now because an ID is claimed by a spec or by an open task, and until this file
  existed the open task was the only claim on these two.
- No task here adds a promise, an ID or a dependency.
