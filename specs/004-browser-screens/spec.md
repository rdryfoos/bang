# Feature Specification: Lend and Return in the Browser

**Feature Branch**: `potato/BANV-1`

**Created**: 2026-09-21

**Status**: Draft

**Input**: Card BANV-1, `ids: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30`

The screens are `design/outstanding.html`, `design/nothing-out.html`,
`design/lend.html` and `design/mark-returned.html`. `design/README.md` is the contract:
the screen is the definition of "working", the copy on it is the copy, and layout is a
guide. Controls, order, states and words are not.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lend, see, and return without the command line (Priority: P1)

**US-UI-10** — As the owner, I lend, see what is out, and mark things returned on a
screen in my browser, not only at the command line.

The owner starts the app, opens it in a browser, and can do the whole loop there:
see what is out, lend something, mark it returned. The command line keeps working and
sees the same records.

**Why this priority**: The whole card. The command line already does these things;
the promise is a second door that does not need it.

**Independent Test**: Against an empty records file, open the app, lend an item on the
Lend screen, see it in the list, mark it returned, and land on "Nothing is out." No
command-line invocation is used at any step.

**Acceptance Scenarios**:

1. **FR-UI-10** — **Given** the app is running, **When** the owner opens it, **Then**
   it serves the four screens over a local web app that reads and writes the same
   records file the command line does, and nothing leaves the machine.
2. **AC-UI-10** — **Given** items are out, **When** the owner opens the app, **Then**
   the outstanding list is shown as `design/outstanding.html` draws it, oldest first with
   days out; **Given** nothing is out, **Then** it is shown as `design/nothing-out.html`
   draws it.
3. **AC-UI-20** — **Given** the Lend screen, **When** the owner gives what and to whom,
   with the date out defaulting to today, **Then** the item is saved and appears in the
   list at once; **When** the borrower is missing, **Then** the refusal is shown in
   place and nothing is saved.
4. **AC-UI-30** — **Given** an item in the list, **When** the owner marks it returned,
   with the date back defaulting to today, **Then** it leaves the list at once and the
   record survives a restart of the app.

---

### Edge Cases

- **No records file yet.** The list shows the nothing-out screen (AC-UI-10). Lending
  creates the file where the command line would.
- **The records cannot be read.** The app says so as an error and never draws the
  nothing-out screen, because that screen tells the owner everything came back
  (Assumption A-5).
- **Missing borrower on Lend.** The form is shown again with what the owner typed kept
  (what, date out), the borrower field marked, and the words "A borrower is required.
  Nothing was saved." under it (AC-UI-20). The records file is unchanged.
- **Missing item name or an unreadable date** on Lend, or an unreadable date back on
  Mark returned. Refused in place the same way, nothing saved (Assumption A-4).
- **Last item marked returned.** The owner lands on the nothing-out screen (AC-UI-30,
  AC-UI-10).
- **Mark returned for an item that is gone or already returned** (a stale page, a second
  tab). The owner lands on the current list; nothing is changed.
- **Another process writes the file while the app runs** (the command line). The next
  page shown reflects it, because the app reads the file on every request rather than
  holding a copy (FR-UI-10).

## Clarifications

### Session 2026-09-21

- Q: What starts the app? → A: `python3 -m whms.web --port N`, binding 127.0.0.1 only,
  reading `WHMS_DATA_FILE` as the command line does. Source: `design/README.md`, "How
  the app is started". See A-1.
- Q: Which records file? → A: The same one the command line reads: `WHMS_DATA_FILE`, else
  the default path. Source: FR-UI-10.
- Q: What are the words on each screen? → A: The words in the four design files, exactly.
  Source: `design/README.md`.
- Q: May a registry ID appear on a screen a user sees? → A: No. The IDs live in the
  README table and in `@covers` marks. Source: `design/README.md`.
- Q: What does "days out" count, and how is it worded? → A: Whole days from the date out
  to today, worded "N days" as the screens draw it. The screen fixes the form for two or
  more; one day reads "1 day" (Assumption A-2).
- Q: How is the date shown and typed? → A: The screens show "Sep 20, 2026". The field
  accepts that form and `YYYY-MM-DD` (the form the command line and the file use), and
  the file always stores `YYYY-MM-DD` (Assumption A-3).
- Q: Does marking returned by the browser use the same field the list already reads? →
  A: Yes: a `date_back` value on the item's record, which is what makes it drop out of
  the list. Marking returned at the command line belongs to the card BANV-5; this feature
  adds only the screen's way of setting the same field, and must not conflict with that
  card's (Assumption A-6).
- Q: Network or listener? → A: A listener on loopback only, no outbound request.
  Constitution I forbids the outbound kind and this is not one; SURFACE row L1 currently
  reads "none yet" and must be updated by a hand (see "Surface owed").
- Q: The Lend screen's borrower history? → A: Not in scope. It belongs to the card
  BANV-4, and `design/README.md` says the Lend design does not draw it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-UI-10**: A local web app serves the four screens and reads and writes the same
  records file the command line does.
  - Started as `python3 -m whms.web --port N`; listens on 127.0.0.1 only.
  - Reads the file on every request; a record written by the command line shows on the
    next page, and a record written by the app shows in `lend list`.
  - Makes no outbound network request and adds no dependency beyond the standard library.
  - No page a user sees contains a registry ID.
- **AC-UI-10**: The front page is the outstanding list.
  - Each item shows its name, "`<borrower>` has it. Out since `<date>`.", its days out,
    and a Mark returned control that opens the Mark returned screen for that item.
  - Items are ordered oldest first by date out.
  - A Lend something control opens the Lend screen.
  - With nothing out, the page shows "Nothing is out." and "Everything you lent has
    come back, or you have not lent anything yet.", with the Lend something control.
  - Both states carry the footer line "Your records are in a file on this machine and
    nowhere else."
- **AC-UI-20**: The Lend screen has What, To whom, and Date out (today unless changed),
  a Save control, and a Back to the list link.
  - A complete form saves the item and returns to the list, where it appears.
  - A missing borrower re-shows the form with "A borrower is required. Nothing was
    saved." in place under the field, and the records file is not touched.
- **AC-UI-30**: The Mark returned screen shows the item ("`<borrower>` has it. Out since
  `<date>`."), a Date back (today unless changed), a Mark returned control and a Back to
  the list link.
  - Submitting records the date back on that item and returns to the list, where it no
    longer appears; if it was the last, the nothing-out screen shows.
  - The record is written to the file before the page answers, so it survives a restart.

### Key Entities

- **Item record**: name, borrower, date out, and, once returned, date back; one JSON
  file on this machine, shared with the command line.
- **Screen**: one of the four designs, rendered from the current file contents.

## Success Criteria *(mandatory)*

- **SC-001** (AC-UI-10): With N items out, the front page lists exactly those N, in
  date-out order, each with the right days out; with none, it shows the nothing-out words.
- **SC-002** (AC-UI-20): A lend without a borrower leaves the records file byte-for-byte
  unchanged and shows the refusal words on the same screen.
- **SC-003** (AC-UI-30): After marking returned, a freshly started app shows the item
  absent and the file holds its date back.
- **SC-004** (FR-UI-10): No listener other than 127.0.0.1 exists, no outbound request is
  made, and a change through either door is visible through the other.
- **SC-005** (US-UI-10): The lend, see, return loop completes in a browser with no
  command-line step.

## Assumptions

- **A-1**: Start-up contract is exactly that of `design/README.md`, which `scripts/try.sh`
  relies on. No other flags are promised.
- **A-2**: Days out is `today - date out` in whole days; the singular is "1 day". A date
  out in the future shows 0 days. The PRD fixes none of this, so no promise is added.
- **A-3**: Date text is accepted as "Sep 20, 2026" or `YYYY-MM-DD`; stored as
  `YYYY-MM-DD`. Anything else is refused in place with nothing saved. The screens fix the
  displayed form and the file already fixes the stored one.
- **A-4**: Refusals other than the missing borrower reuse the shape AC-UI-20 draws (in
  place, nothing saved). Their wording is not on the screens and is not fixed here; proof
  asserts the refusal is in place and the file unchanged, not a string.
- **A-5**: An unreadable records file is an error page, never the nothing-out screen.
- **A-6**: Which item a Mark returned control refers to is decided by the plan, not the
  owner. Nothing about it appears on a screen.
- **A-7**: One owner, one machine, fewer than a hundred items. No paging, search, login,
  or concurrent-editor handling beyond reading the file per request.
- **A-8**: Screens render legibly at phone width and, on a wide browser, sit as a bounded
  panel per `design/README.md`. Type, spacing and colour may differ from the mockups.

## Surface owed

registry line owed: none. SURFACE.md row L1 (the lending tracker's listener) reads "none
yet" and this feature makes it true that a listener exists: 127.0.0.1, port chosen by
`--port`, started by hand or by `scripts/try.sh`. A hand should amend row L1 to say so.
This spec cannot change SURFACE.md.

## SpecAssay — durable IDs (required)

IDs are inherited from PRD.md. None is created here. Scope of this feature:
`US-UI-10`, `FR-UI-10`, `AC-UI-10`, `AC-UI-20`, `AC-UI-30`.

## Risk & failure modes (required)

| Failure | User impact | Mitigation / trace |
|---------|-------------|-------------------|
| The app listens on every interface | Records reachable from the network | FR-UI-10 |
| A refused lend still writes a record | A nameless loan sits in the list | AC-UI-20 |
| Mark returned answers before the write lands | The item returns after a restart | AC-UI-30 |
| Unreadable file drawn as nothing-out | Owner believes nothing is lent | AC-UI-10 (A-5) |
| The app caches records | The command line's changes do not show | FR-UI-10 |
| A registry ID appears on a page | The software reads as a registry, not a tool | FR-UI-10 |
| The screens drift from the designs | Build passes the sentence, fails the screen | AC-UI-10, AC-UI-20, AC-UI-30 |
