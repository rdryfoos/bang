# Tasks: Lend and Return in the Browser

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Scope**: `US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30`

Format: `[ID] [P?] Description`. `[P]` means it can run in parallel (different files, no
dependency). Tests are named before the code exists; write each one first and watch it
fail. All fixture values are invented and generic, never taken from the reader's answers.

## Phase 1: Proofs first

- [x] T201 [P] Write `test_AC_UI_10_front_page_lists_outstanding_oldest_first_with_days_out_or_says_nothing_is_out` in `tests/test_web.py`. Temp data file with one returned item and three unreturned in mixed order, fixed "today": the page lists the three oldest first with "N days", a Mark returned link each and a Lend something link, and not the returned one; with none outstanding (absent file, or all returned) it shows "Nothing is out." and the second sentence from the design. **Carries**: AC-UI-10
- [x] T202 [P] Write `test_AC_UI_20_lend_saves_and_shows_in_list_and_missing_borrower_is_refused_in_place` in `tests/test_web.py`. The Lend form defaults date out to today; a complete POST saves and the list shows the item; a POST with no borrower answers with the form, "A borrower is required. Nothing was saved.", the typed values kept, and the data file unchanged (bytes equal, or still absent). **Carries**: AC-UI-20
- [x] T203 [P] Write `test_AC_UI_30_mark_returned_defaults_to_today_removes_item_and_survives_restart` in `tests/test_web.py`. The Mark returned form shows the item and today as the date back; a POST records `date_back`, the list no longer shows it, and a second server started on the same file still does not; returning the last item shows the nothing-out screen; a stale or out-of-range item changes nothing. **Carries**: AC-UI-30
- [x] T204 [P] Write `test_FR_UI_10_local_app_shares_the_command_lines_file_and_binds_loopback_only` in `tests/test_web.py`. The listening socket's address is 127.0.0.1; an item added by `whms.cli` shows on the front page and an item lent through the app shows in `lend list`; no rendered page matches the registry-ID pattern; `python3 -m whms.web --port 0` starts. **Carries**: FR-UI-10
- [x] T205 [P] Write `test_US_UI_10_lend_see_and_return_loop_needs_no_command_line` in `tests/test_web.py`. Against an empty file, only HTTP requests: lend an item, see it listed, mark it returned, see "Nothing is out."; an unreadable file gives an error page and not the nothing-out words. **Carries**: US-UI-10

## Phase 2: The app

- [x] T206 Add `mark_returned(index, date_back)` to `src/whms/store.py`, writing by the same temp-file-then-replace method as `append`, and add `AC-UI-30` to that file's `@covers` line. **Carries**: AC-UI-30
- [x] T207 Create `src/whms/pages.py`: the four screens as HTML with the copy of `design/`, escaped values, days-out and date formatting with an injectable today, the refusal-in-place variant of Lend, and the wide-browser panel styling. First line: `# @covers AC-UI-10, AC-UI-20, AC-UI-30`. **Carries**: AC-UI-10, AC-UI-20, AC-UI-30
- [x] T208 Create `src/whms/web.py`: the loopback-only server, the routes in the plan, per-request reads, error page for unreadable records, `--port N`, `python3 -m whms.web`. First line: `# @covers US-UI-10, FR-UI-10`. **Carries**: US-UI-10, FR-UI-10

**Checkpoint**: T201 to T205 pass, and the earlier command-line tests still pass unchanged.

## Phase 3: Gate

- [ ] T209 Run the SpecAssay Check Gate and paste its result on the card. No task line may lack `**Carries**`, no test name may be unmatched, no `@covers` may be an orphan. **Carries**: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30

## Dependencies and order

- T201 to T205 in parallel, before T206 to T208. T206 before T208. T207 before T208. T209 last.

## Notes

- **Closing the reservation**: `specs/backlog/tasks.md` T904 ("BANV-1, the screens") is the
  open task for these five IDs. It is open (`- [ ]`) at the time of writing.
- Do not add marking returned at the command line; that is the card BANV-5's. Do not add the
  borrower's history to the Lend screen; that is the card BANV-4's.
- No task adds an outbound network import or a dependency beyond the standard library.
  The one listener is loopback only.
- A hand owes an amendment to SURFACE.md row L1 (see the spec).
