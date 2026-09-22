# Tasks: Record a Lent Item

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Scope**: `US-LEND-10, FR-LEND-10, AC-LEND-10, AC-LEND-20, NFR-PRIV-10, AC-PRIV-20, AC-PRIV-10`

Format: `[ID] [P?] Description`. `[P]` means it can run in parallel (different files, no
dependency). Tests are named before the code exists; write each one first and watch it
fail. All fixture values are invented and generic, never taken from the reader's answers.

## Phase 1: Setup

- [ ] T001 Create `src/whms/__init__.py` with the mark `# @covers US-LEND-10, FR-LEND-10`, and a `pyproject.toml` or `pytest.ini` that puts `src` on the import path. Python 3.9, standard library only. **Carries**: US-LEND-10, FR-LEND-10

## Phase 2: The record and its refusals (US-LEND-10)

Tests first.

- [ ] T002 [P] Write `test_AC_LEND_10_saved_item_appears_in_outstanding_list_immediately` in `tests/test_lend_item.py`. Uses a temp data file: run `lend add` with a name, borrower and date out, then `lend list`; the item's three values are in the output. **Carries**: AC-LEND-10
- [ ] T003 [P] Write `test_AC_LEND_20_item_without_borrower_is_refused_with_reason` in `tests/test_lend_item.py`. Add with the borrower absent, then with it blank, then with it whitespace-only: each exits non-zero, stderr names the borrower as the reason, and the data file has no new record. **Carries**: AC-LEND-20
- [ ] T004 [P] Write `test_AC_LEND_20_refused_save_leaves_existing_records_untouched` in `tests/test_lend_item.py`. Save one good item, attempt a refused one, and compare the data file byte for byte before and after. **Carries**: AC-LEND-20
- [ ] T005 [P] Write `test_FR_LEND_10_item_record_holds_name_borrower_and_date_out` in `tests/test_lend_item.py`. Also covers the spec's edge cases: missing name, missing date, and an impossible date are each refused with their reason. **Carries**: FR-LEND-10

Then the code.

- [ ] T006 Create `src/whms/records.py`: the item record with `name`, `borrower`, `date_out`; validation that returns every missing or invalid field with a reason; whitespace-only is blank; date must be a real `YYYY-MM-DD`. First line of the file: `# @covers FR-LEND-10, AC-LEND-20`. **Carries**: FR-LEND-10, AC-LEND-20
- [ ] T007 Create `src/whms/store.py`: read the JSON file fresh per call, append a record, write to a sibling temp file and `os.replace`. A write error is raised, never swallowed. Path from `WHMS_DATA_FILE`, default `~/.who-has-my-stuff/items.json`. First line: `# @covers FR-LEND-10, AC-LEND-10, NFR-PRIV-10`. **Carries**: FR-LEND-10, AC-LEND-10, NFR-PRIV-10
- [ ] T008 Create `src/whms/cli.py`: `lend add --name --borrower --date-out` and `lend list`. On refusal print `refused: <reason>` to stderr, write nothing, exit 2. On success print the saved record, exit 0. `list` prints every saved item in insertion order. First line: `# @covers US-LEND-10, AC-LEND-10, AC-LEND-20`. **Carries**: US-LEND-10, AC-LEND-10, AC-LEND-20

**Checkpoint**: T002 to T005 pass. US-LEND-10 is demonstrable alone.

## Phase 3: Nothing leaves this machine (NFR-PRIV-10)

- [ ] T009 [P] Write `test_AC_PRIV_20_lend_and_list_make_no_outbound_network_request` in `tests/test_no_network.py`. Patch `socket.socket`, `socket.create_connection` and `socket.getaddrinfo` to fail the test when called; run `add` and `list` in-process; both succeed. **Carries**: AC-PRIV-20
- [ ] T010 [P] Write `test_NFR_PRIV_10_source_imports_no_network_or_third_party_client` in `tests/test_no_network.py`. Parse every file under `src/whms` with `ast`; fail on any import of `socket`, `http`, `urllib`, `ssl`, `smtplib`, `ftplib`, `xmlrpc`, `requests`, `httpx`, `aiohttp`, or any module outside the standard library. **Carries**: NFR-PRIV-10
- [ ] T011 [P] Write `test_AC_PRIV_10_data_and_test_writes_stay_outside_the_worktree` in `tests/test_repo_privacy.py`. The default data path resolves outside the worktree; running `add` and `list` against a temp data file leaves `git status --porcelain` unchanged. Fixture values are invented and generic. **Carries**: AC-PRIV-10
- [ ] T012 Confirm T009 to T011 pass against T006 to T008 unchanged. If one fails, the fault is in T006 to T008, not the test. Do not relax a proof to make it pass; report a needed relaxation as a finding. **Carries**: NFR-PRIV-10, AC-PRIV-20, AC-PRIV-10

## Phase 4: Gate

- [ ] T013 Run the SpecAssay Check Gate and paste its result on the card. No task line may lack `**Carries**`, no test name may be unmatched, no `@covers` may be an orphan. **Carries**: US-LEND-10, FR-LEND-10, AC-LEND-10, AC-LEND-20, NFR-PRIV-10, AC-PRIV-20, AC-PRIV-10

## Dependencies and order

- T001 first. T002 to T005 in parallel, before T006 to T008. T006 before T007 before T008.
- T009 to T011 may be written any time after T001; they pass only after T008.
- T012 after T008 and T009 to T011. T013 last.

## Notes

- `AC-PRIV-10`'s content scan (does any file carry a value from the reader's answers) is
  `scripts/no-private-answers.py`, a commit hook and not a Gate (SURFACE LC1). T011 proves
  the structural half a Gate can prove. Build must not put any value from the reader's
  answers in a fixture, comment, or commit message.
- Ordering and the empty state of `lend list` belong to the outstanding-list card. Do not add them here.
