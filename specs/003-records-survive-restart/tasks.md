# Tasks: Records Survive Restarting the Application

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Scope**: `NFR-DUR-10, AC-DUR-10`

Format: `[ID] [P?] Description`. Tests are named before the code exists; write each one
first and watch it. All fixture values are invented and generic, never taken from the
reader's answers.

## Phase 1: The proof

- [x] T201 Write `test_AC_DUR_10_lends_and_returns_are_still_present_with_dates_after_restart` in `tests/test_durability.py`. Each "restart" is a separate `python -m whms` subprocess or a fresh `python` process reading `store.load()`, against one temp `WHMS_DATA_FILE`. Add two items with different dates out; in a new process read them back, none lost, dates out unchanged; give one a `date_back` in the file, then in a new process see it kept with its date and the other without one, and `lend list` showing only the unreturned; add a third item in a new process and see all three in another. **Carries**: AC-DUR-10
- [x] T202 Confirm T201 passes against `src/whms/store.py` unchanged. If it fails, fix the fault in `store.py` and add `NFR-DUR-10` to its `@covers` line; do not relax the proof. **Carries**: NFR-DUR-10, AC-DUR-10

## Phase 2: Gate

- [x] T203 Run the SpecAssay Check Gate and paste its result on the card. No task line may lack `**Carries**`, no test name may be unmatched, no `@covers` may be an orphan. **Carries**: NFR-DUR-10, AC-DUR-10

## Dependencies and order

- T201 first, then T202, then T203.

## Notes

- Do not add a way to mark an item returned; that is BAN-3's. T201 supplies `date_back`
  in the data file directly, as BAN-2's tests do.
- No task adds a network import, listener or new dependency.
- `NFR-DUR-10` is carried by T202 and, through it, by the proof T201 of `AC-DUR-10`. The
  `@covers NFR-DUR-10` mark is expected on `tests/test_durability.py`'s first line so the
  promise has a mark even when `store.py` needs no change.
