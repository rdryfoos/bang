# Feature Specification: Records Survive Restarting the Application

**Feature Branch**: `potato/BAN-5`

**Created**: 2026-09-20

**Status**: Draft

**Input**: Card BAN-5, `ids: NFR-DUR-10, AC-DUR-10`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - What I wrote down is still there tomorrow (Priority: P1)

**NFR-DUR-10** — Records survive restarting the application.

The owner writes down what they lent, closes the application, and opens it again
later. Everything they wrote is there. Their whole reason for writing it down was to
stop relying on memory; a tool that forgets on restart puts the memory back on them.

**Why this priority**: Every other promise assumes the records are still there when the
owner next looks. Three weeks later (the CASE's own test) is many restarts away.

**Independent Test**: Lend two items, stop the application, start it again, and read
the records. Both are present with their dates out.

**Acceptance Scenarios**:

1. **AC-DUR-10** — **Given** lends and returns recorded before a restart, **When** the
   application is restarted, **Then** every one of them is still present with its
   dates: the date out for a lend, and the date back for a return.

---

### Edge Cases

- **A restart with no records yet.** Nothing is lost because nothing was there; the
  application starts and behaves as with no records (AC-OUT-20, held by another card).
- **A save that failed.** It was never recorded, so it is not owed to the owner after a
  restart. The application already tells the owner the save did not happen (BAN-1).
- **A record that was returned.** It must come back from a restart still marked returned,
  with its date back. Losing the return would put a returned item back on the outstanding
  list (AC-OUT-10, held by another card).
- **The records cannot be read after the restart.** The owner is told so as an error;
  the application never presents that as "no records" (BAN-2, A-4 there).

## Clarifications

### Session 2026-09-20

- Q: What counts as a restart? → A: The application stopping and starting again as a new
  process, with the owner's records file left where it was. The application is a command
  the owner runs, so every run is already a fresh process. Source: PRD, NFR-DUR-10;
  Constitution II. See A-1.
- Q: What does "with its dates" cover? → A: The date out on every record, and the date
  back on every returned record, exactly as recorded. Source: AC-DUR-10 with FR-LEND-10
  and FR-RET-10. See A-2.
- Q: Where do records live so they can survive? → A: In a file on disk the owner can
  open, copy or delete, per Constitution II. That file is BAN-1's data file; no new
  storage is introduced. Source: Constitution II.
- Q: Must records survive a crash or power loss mid-write? → A: The PRD says "restarting
  the application" and no more. Nothing beyond the write BAN-1 already makes (new file
  written whole, then swapped in) is promised or added. See A-3.
- Q: How can the return half be shown before the return operation exists? → A: The return
  operation is BAN-3's. What durability owes is that a record carrying a date back comes
  back with it. See A-4.
- Q: Network or listener? → A: None. Constitution I, SURFACE L1 and AC-PRIV-20 apply
  unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **NFR-DUR-10**: Records survive restarting the application.
  - After a restart, every lend and return recorded before it is present with its dates
    (AC-DUR-10).

### Key Entities

- **Record**: an item record (name, borrower, date out, and once returned a date back)
  as kept in the owner's records file. Its lifetime is the file's, not the process's.

## Success Criteria *(mandatory)*

- **SC-001** (AC-DUR-10): For any records written before a restart, reading them in the
  new process yields the same set of records, each with the same date out and, where it
  had one, the same date back: zero lost, zero altered.

## Assumptions

- **A-1**: A restart is a new process reading the same records file. Nothing is held
  only in memory between runs, so none is lost when the process ends.
- **A-2**: "Its dates" means date out and, for returned records, date back, byte for byte
  as recorded.
- **A-3**: Crash and power-loss safety is not promised beyond what BAN-1's write already
  does. No promise and no ID is added for it.
- **A-4**: The operation that records a return is BAN-3's. Until it lands, proof of the
  return half supplies a record with a date back directly in the records file, as BAN-2's
  proofs do. Once BAN-3 lands, the proof should record the return through that operation;
  that swap changes no promise here.
- **A-5**: One owner, one machine, fewer than a hundred items (CASE, Constitution II).

## SpecAssay — durable IDs (required)

IDs are inherited from PRD.md. None is created here. Scope of this feature:
`NFR-DUR-10`, `AC-DUR-10`.

## Risk & failure modes (required)

| Failure | User impact | Mitigation / trace |
|---------|-------------|-------------------|
| Records are held in memory and dropped at exit | The owner loses everything on the next start | NFR-DUR-10, AC-DUR-10 |
| A return's date back is not kept | A returned item reappears as outstanding | AC-DUR-10 |
| A record's date out changes across a restart | The oldest loan is no longer first | AC-DUR-10 |
| A restart reads a broken file as empty | The owner believes nothing was ever lent | AC-DUR-10 (edge case) |
