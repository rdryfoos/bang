# Feature Specification: See What Is Still Out

**Feature Branch**: `potato/BAN-2`

**Created**: 2026-09-20

**Status**: Draft

**Input**: Card BAN-2, `ids: US-OUT-10, FR-OUT-10, AC-OUT-10, AC-OUT-20`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See everything still out (Priority: P1)

**US-OUT-10** — As the owner, I can see everything still out without hunting.

The owner asks for the outstanding list and gets every item that has not been marked
returned, oldest first, in one place. There is nothing to search, filter or scroll past.

**Why this priority**: This is the reason the owner writes anything down. A record
that cannot be seen at a glance is a record they still have to remember.

**Independent Test**: Save three items with different dates out, mark one returned,
then list. The two unreturned items appear, the earlier date first; the returned one
does not.

**Acceptance Scenarios**:

1. **AC-OUT-10** — **Given** an item that was outstanding, **When** it is marked
   returned, **Then** it no longer appears in the outstanding list.
2. **FR-OUT-10** (the ordering and completeness promise, exercised by the same
   scenario) — **Given** several items not marked returned, **When** the owner lists
   them, **Then** every one appears and the one that went out earliest is first.

---

### User Story 2 - Nothing out says so (Priority: P2)

**AC-OUT-20** belongs to US-OUT-10 and is stated as its own story because its failure
looks different: a blank screen reads as broken, not as good news.

**Why this priority**: The list is right without it, but an owner who sees nothing
cannot tell "nothing is out" from "the tool failed".

**Independent Test**: With no items saved, or every item marked returned, ask for the
list. The output is words saying nothing is outstanding, not an empty output.

**Acceptance Scenarios**:

1. **AC-OUT-20** — **Given** no item is outstanding, **When** the owner asks for the
   outstanding list, **Then** the list says so in words rather than showing an empty
   screen.

---

### Edge Cases

- **No records exist at all** (the data file is absent). Same as nothing outstanding:
  the list says so in words (AC-OUT-20).
- **Every record is returned.** Same: the list says so in words (AC-OUT-20).
- **Two items with the same date out.** Both appear. The promise fixes "oldest first"
  by the date out and says nothing about ties, so no order among ties is promised
  (Assumption A-3).
- **The records cannot be read.** The owner is told so as an error. The application
  never reports "nothing outstanding" when it could not look (Assumption A-4).
- **An item just saved** appears at once (AC-LEND-10, held by another card); this
  feature must not break that.

## Clarifications

### Session 2026-09-20

- Q: What makes an item "returned"? → A: It has been marked returned, which per
  FR-RET-10 records a date back. Marking is the return card's; this feature only reads
  the state. Source: PRD, FR-RET-10. See A-1.
- Q: What does "oldest first" order by? → A: The date out, earliest first. Source:
  FR-OUT-10 with the item record of FR-LEND-10, whose only date is the date out. See A-2.
- Q: What order do items with the same date out take? → A: None is promised. PRD is
  silent, so none is invented. See A-3.
- Q: What are the exact words for an empty list? → A: Any plain words that say nothing
  is outstanding. PRD says "in words" and fixes no text; no wording is invented into a
  promise. See A-5.
- Q: Does the list show more than name, borrower and date out? → A: No. The record
  holds those three. Source: FR-LEND-10.
- Q: Network or listener? → A: None. Constitution I, SURFACE L1 and AC-PRIV-20 apply
  unchanged; the list is read from the file on disk.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-OUT-10**: The outstanding list shows every item not yet marked returned,
  oldest first.
  - An item marked returned is absent (AC-OUT-10).
  - With no item outstanding, the list states so in words (AC-OUT-20).

### Key Entities

- **Outstanding item**: an item record (name, borrower, date out) that has not been
  marked returned. The returned state and its date back are the return feature's
  (US-RET-10) and are read here, never written.

## Success Criteria *(mandatory)*

- **SC-001** (AC-OUT-10): After an item is marked returned, the count of times it
  appears in the outstanding list is zero, on the very next look.
- **SC-002** (FR-OUT-10): For any set of items, the list shows all and only the
  unreturned ones, sorted by date out ascending.
- **SC-003** (AC-OUT-20): With nothing outstanding, 100% of requests for the list
  produce a non-empty message in words saying so.

## Assumptions

- **A-1**: "Marked returned" means the record carries a date back (FR-RET-10). This
  feature reads it; it adds no way to set it. Until the return card lands, no real
  record carries one, and tests supply such records directly.
- **A-2**: Oldest means earliest date out. The date out is the only date an item
  record holds before it is returned (FR-LEND-10).
- **A-3**: No order among items with the same date out is promised or tested. The
  plan may keep insertion order among ties as an implementation detail, which is not
  a promise and carries no ID.
- **A-4**: An unreadable store is an error, never the empty message. Extends AC-OUT-20's
  intent (silence must mean nothing is out) and adds no promise or ID.
- **A-5**: The empty message's text is not fixed by the PRD. Proof asserts that the
  output is non-empty words naming that nothing is outstanding, not a particular string.
- **A-6**: One owner, one machine, fewer than a hundred items (CASE, Constitution II).
  No paging, search or filtering.

## SpecAssay — durable IDs (required)

IDs are inherited from PRD.md. None is created here. Scope of this feature:
`US-OUT-10`, `FR-OUT-10`, `AC-OUT-10`, `AC-OUT-20`.

## Risk & failure modes (required)

| Failure | User impact | Mitigation / trace |
|---------|-------------|-------------------|
| A returned item stays in the list | The owner chases someone who already returned it | AC-OUT-10 |
| An unreturned item is dropped (bad filter) | A lent item is forgotten | FR-OUT-10 |
| Order is by save time rather than date out | The oldest loan is not first | FR-OUT-10 |
| The empty case prints nothing | Owner cannot tell empty from broken | AC-OUT-20 |
| A read failure prints the empty message | Owner believes nothing is out when items are | AC-OUT-20 (A-4) |
