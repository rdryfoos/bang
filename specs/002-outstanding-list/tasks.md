# Tasks: See What Is Still Out

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Scope**: `US-OUT-10, FR-OUT-10, AC-OUT-10, AC-OUT-20`

Format: `[ID] [P?] Description`. `[P]` means it can run in parallel (different files, no
dependency). Tests are named before the code exists; write each one first and watch it
fail. All fixture values are invented and generic, never taken from the reader's answers.

## Phase 1: Proofs first

- [x] T101 [P] Write `test_AC_OUT_10_item_marked_returned_no_longer_appears_in_outstanding_list` in `tests/test_outstanding.py`. Temp data file holding one item with a `date_back` and one without; `lend list` shows the second and not the first. **Carries**: AC-OUT-10
- [x] T102 [P] Write `test_FR_OUT_10_outstanding_list_shows_every_unreturned_item_oldest_first` in `tests/test_outstanding.py`. Records in file order newest, oldest, middle; the list shows all and only the unreturned ones, ordered by date out ascending. **Carries**: FR-OUT-10
- [x] T103 [P] Write `test_AC_OUT_20_empty_outstanding_list_says_so_in_words` in `tests/test_outstanding.py`. Cases: no data file, an empty list, and every item returned. Each prints non-empty text saying nothing is out, exits 0, and prints no item line. **Carries**: AC-OUT-20
- [x] T104 [P] Write `test_US_OUT_10_unreadable_records_are_an_error_not_an_empty_list` in `tests/test_outstanding.py`. A malformed data file exits non-zero with an error on stderr and does not print the empty message. **Carries**: US-OUT-10

## Phase 2: The list

- [x] T105 Create `src/whms/outstanding.py`: `select(items)` returns items with no non-empty `date_back`, stable-sorted by `date_out` ascending. First line: `# @covers FR-OUT-10, AC-OUT-10`. **Carries**: FR-OUT-10, AC-OUT-10
- [x] T106 Change `lend list` in `src/whms/cli.py` to print `outstanding.select(store.load())`, one item per line as now, and `Nothing is out.` when the selection is empty; read errors keep printing to stderr and exit 1. Add `US-OUT-10, AC-OUT-20` to the `@covers` line. **Carries**: US-OUT-10, AC-OUT-20

**Checkpoint**: T101 to T104 pass, and BAN-1's tests still pass unchanged (its list assertions hold: a saved item appears at once).

## Phase 3: Gate

- [ ] T107 Run the SpecAssay Check Gate locally and report its verdict on the card. No task line may lack `**Carries**`, no test name may be unmatched, no `@covers` may be an orphan. **Carries**: US-OUT-10, FR-OUT-10, AC-OUT-10, AC-OUT-20

## Dependencies and order

- T101 to T104 in parallel, before T105 and T106. T105 before T106. T107 last.

## Notes

- Do not add a way to mark an item returned; that is BAN-3's. Tests supply `date_back`
  directly in the data file.
- T103 carries AC-OUT-20 through T106. Per `specs/backlog/tasks.md` T901 this promise
  is expected to ship as tracked debt; leaving T103 and T106 open is the operator's call
  and does not affect the other tasks.
- No task adds a network import, listener or new dependency.
