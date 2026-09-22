# Implementation Plan: Lend and Return in the Browser

**Branch**: `potato/BANV-1` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification for `US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30`

## Summary

Add `src/whms/web.py`, a standard-library HTTP server bound to 127.0.0.1 that renders
the four screens from the records file on every request, plus `src/whms/pages.py` for the
markup. It reuses `store`, `records` and `outstanding`; the command line is untouched.

## Technical Context

**Language/Version**: Python 3.9 (no `match`, no `X | Y` unions).
**Primary Dependencies**: none. `http.server`, `urllib.parse`, `html`; `pytest` for tests.
**Storage**: the existing JSON file (`WHMS_DATA_FILE`), written with the same
temp-file-then-replace approach as `store.append`.
**Testing**: `pytest`, proofs named `test_<KIND>_UI_<NN>_…` under `tests/`. Tests start the
server on an ephemeral port in a thread or subprocess and use `urllib` against 127.0.0.1.
**Project Type**: single project (CLI plus local web app).
**Constraints**: no outbound network; loopback listener only; file storage; Python only.
**Scale/Scope**: one owner, one machine, under 100 items.

## Constitution Check

| Principle | Status | How |
|-----------|--------|-----|
| I. Local only, no network | Pass | Binds 127.0.0.1 only; no outbound import or request; `test_no_network.py` scans `src/whms` and covers the new modules. |
| II. Storage is a file on disk | Pass | The same JSON file; no second store. |
| III. Node or Python only | Pass | Python standard library only. |
| IV. Promotion path only | Pass | Work stays on `potato/BANV-1`. |

SURFACE check: L1 (listener) changes from "none yet" to a loopback listener. SURFACE.md
is not edited here; the spec's "Surface owed" section asks a hand to amend it. No egress
change (E1, E2).

## Project Structure

### Documentation

```text
specs/004-browser-screens/
├── spec.md
├── plan.md
├── tasks.md
└── checklists/requirements.md
```

### Source Code

```text
src/whms/
├── web.py      # NEW: server, routes, `python3 -m whms.web --port N`
├── pages.py    # NEW: the four screens as HTML, copy taken from design/
└── store.py    # MODIFIED: mark an item returned by position, same atomic write

tests/
└── test_web.py # NEW
```

## Design

### Server (FR-UI-10)

`web.py` defines a `BaseHTTPRequestHandler` and `main(argv)`; `--port` is required to be
an integer (0 allowed for tests, which read back the bound port). The server binds
`("127.0.0.1", port)` and nothing else. Every handler calls `store.load()` afresh. Read
errors render an error page with a non-200 status, never the nothing-out screen (A-5).
Request logging goes to stderr only.

### Routes

| Route | Method | Screen / effect |
|-------|--------|-----------------|
| `/` | GET | outstanding list, or nothing-out (AC-UI-10) |
| `/lend` | GET | Lend form, date out prefilled with today |
| `/lend` | POST | validate with `records.validate`; save via `store.append` and redirect to `/`, or re-render the form with the refusal in place (AC-UI-20) |
| `/return/<n>` | GET | Mark returned form for the item at position `n` in the file, date back prefilled with today |
| `/return/<n>` | POST | set `date_back`, write, redirect to `/` (AC-UI-30) |

`<n>` is the item's index in the file, which is stable between the list render and the
submit unless another process edits the file; an `<n>` that is out of range or already
returned redirects to `/` and changes nothing (spec edge case).

### Dates (A-2, A-3)

`pages.py` shows dates as "Mon D, YYYY". Input is parsed as either that form or
`YYYY-MM-DD` and stored `YYYY-MM-DD`. The existing `records.validate` requires
`YYYY-MM-DD`, so the web layer normalises the typed date before calling it, and the CLI's
behaviour does not change. Days out is computed in `pages.py` from an injectable "today"
so tests are deterministic.

### Refusal in place (AC-UI-20)

A missing borrower yields the form again with values kept, the borrower input given the
error border, and the words "A borrower is required. Nothing was saved." beneath it.
Other refusals use the same shape with their own words (A-4). The file is not opened for
writing on any refused request.

### Mark returned write (AC-UI-30)

`store.mark_returned(index, date_back)` loads, sets `date_back` on that item, and writes
by the temp-file-then-replace method `append` uses, so the file is replaced only after the
new one is written. The response is sent after the replace. If BANV-5 lands its own
write for `date_back` first, the two are unified rather than duplicated; the key is
`date_back` either way (`outstanding.select` reads it).

### Copy and privacy (FR-UI-10)

All words are taken from the four design files. Escaping uses `html.escape` for every
stored value. No page carries a registry ID. A test scans rendered pages for the ID
pattern `[A-Z]+-[A-Z]+-\d\d` and fails on any match.

### Layout (A-8)

One stylesheet inlined in `pages.py`: a 390px-friendly column filling the phone; from a
wide viewport upward, a bounded panel with its own background, a 1px border in the item
cards' colour, rounded corners, a soft shadow and vertical margin.

## Complexity Tracking

None.

## Handoffs

- The card BANV-5 owns marking returned at the command line and its proofs; this plan
  writes only from the screen and reuses the `date_back` key.
- The card BANV-4 owns the borrower's history on the Lend screen; not drawn here.
- A hand amends SURFACE.md row L1 (see the spec).
- `specs/backlog/tasks.md` T904 names IDs this spec now claims; its reservation expires
  with this spec. Removing or closing it is left to the change that lands this card.
