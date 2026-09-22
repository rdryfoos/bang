# Feature Specification: Record a Lent Item

**Feature Branch**: `potato/BAN-1`

**Created**: 2026-09-19

**Status**: Draft

**Input**: Card BAN-1, `ids: US-LEND-10, FR-LEND-10, AC-LEND-10, AC-LEND-20, NFR-PRIV-10, AC-PRIV-20, AC-PRIV-10`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Write down what I lent (Priority: P1)

**US-LEND-10** — As the owner, I write down what I lent, to whom, and when, so I stop
relying on memory.

The owner tells the application the name of the thing, the person who has it, and the
day it went out. The application keeps that record. The owner no longer has to
remember it.

**Why this priority**: Every other promise (seeing what is out, marking it back)
starts from a record existing. Without this there is nothing to list or return.

**Independent Test**: Save one item with a borrower and a date out, then look at the
outstanding list. The item is there, with all three facts.

**Acceptance Scenarios**:

1. **AC-LEND-10** — **Given** an item with a name, a borrower and a date out,
   **When** the owner saves it, **Then** it appears in the outstanding list
   immediately, with no further step.
2. **AC-LEND-20** — **Given** an item with a name and a date out but no borrower,
   **When** the owner tries to save it, **Then** it is refused, the owner is shown
   the reason (that a borrower is required), and no record is kept.

---

### User Story 2 - What I write down stays on this machine (Priority: P1)

**NFR-PRIV-10** — Borrower names and item records never leave this machine. No network
calls, no cloud storage, no third-party services, no contacts access.

This is a promise about the whole application, and it is met by this card for the
lending operation. It is stated as a story because the owner's trust in the first
story depends on it: they will not write down a friend's name in something that
shares it.

**Why this priority**: The reader's fourth promise. It is the one an implementation
is most likely to break unasked.

**Independent Test**: Run the lending operation with every outbound network route
made to fail loudly. The operation still succeeds, and nothing tried to connect.

**Acceptance Scenarios**:

1. **AC-PRIV-20** — **Given** the application is running, **When** the owner lends an
   item or lists the outstanding items, **Then** the application makes no outbound
   network request.
2. **AC-PRIV-10** — **Given** the repository at any commit, **When** its files are
   searched for values from the reader's local answers, **Then** none is found: the
   filled CASE lives outside the worktree at `BANG_CASE_FILE`, and no item, borrower
   or date from it appears in any file.

---

### Edge Cases

- **Borrower is blank or only spaces.** Treated as no borrower (AC-LEND-20).
- **Item name or date out missing.** FR-LEND-10 says a record holds all three. A record
  without one is refused with its reason shown, the same way as a missing borrower
  (see Assumption A-1).
- **Date out is not a real date** (for example 31 February). Refused with the reason
  shown.
- **Two items with the same name and borrower.** Both are kept. Lending the same
  thing twice is a fact, not an error (Assumption A-3).
- **A refused save.** Leaves every existing record exactly as it was.
- **The place records are kept is unreachable or unwritable.** The owner is told the
  save did not happen. The application never reports a save that did not occur.

## Clarifications

### Session 2026-09-19

- Q: What if the item name or date out is missing? → A: Refused with the reason shown,
  as for a borrower. Source: FR-LEND-10 (a record holds all three). See A-1.
- Q: Does the application fill in the date out when the owner gives none? → A: No.
  Source: PRD is silent on a default, so none is invented. See A-2.
- Q: How does the owner reach the application, and does that open a listener? → A: Left
  to the plan. SURFACE L1 declares no listener and AC-PRIV-20 forbids outbound requests,
  so the plan must not open one.
- Q: Which runtime and storage? → A: Left to the plan. Constitution II and III fix the
  boundary: a file on disk, Node or Python only.
- Q: Does this card fix the outstanding list's order or empty wording? → A: No. That is
  the outstanding-list card's. See A-4.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-LEND-10**: An item record holds a name, a borrower, and a date out.
  - Saving a complete record makes it appear in the outstanding list (AC-LEND-10).
  - Saving a record without a borrower is refused with the reason shown (AC-LEND-20).

### Non-Functional Requirements

- **NFR-PRIV-10**: Borrower names and item records never leave this machine.
  - Proven for lending and listing by AC-PRIV-20.
  - Proven for the repository's contents by AC-PRIV-10.

### Key Entities

- **Item record**: a name (what was lent), a borrower (who has it), and a date out
  (the day it left). No other attribute belongs to this feature. The date back and
  the returned state belong to the return feature and are not specified here.

## Success Criteria *(mandatory)*

- **SC-001** (AC-LEND-10): After saving a complete record, the owner sees it in the
  outstanding list on the very next look, with no waiting and no refresh step.
- **SC-002** (AC-LEND-20): 100% of attempts to save without a borrower are refused, each
  with a stated reason, and none leaves a record behind.
- **SC-003** (AC-PRIV-20): Across every lend and list operation, the count of outbound
  network requests is zero.
- **SC-004** (AC-PRIV-10): The count of files in the repository containing a value from
  the reader's local answers is zero, at every commit.

## Assumptions

- **A-1**: A missing name or date out is refused like a missing borrower. FR-LEND-10
  makes all three part of a record; the PRD names only the borrower's absence as an
  acceptance criterion, and this assumption extends the same behaviour to the other two
  rather than saving an incomplete record. It adds no promise and carries no new ID.
- **A-2**: The owner supplies the date out. The application does not guess it. The PRD
  says the record holds "a date out" and gives no default.
- **A-3**: No duplicate check. The PRD promises none.
- **A-4**: The outstanding list is specified by another card's scope (seeing what is
  still out). This feature asks only that a saved item be visible in it immediately.
  Ordering, empty-state wording, and the effect of returning are not specified here.
- **A-5**: One owner, one machine, fewer than a hundred items (CASE and Constitution II).
  No accounts, no sharing, no concurrent writers.

## SpecAssay — durable IDs (required)

IDs are inherited from PRD.md. None is created here. Scope of this feature:
`US-LEND-10`, `FR-LEND-10`, `AC-LEND-10`, `AC-LEND-20`, `NFR-PRIV-10`, `AC-PRIV-20`,
`AC-PRIV-10`.

## Risk & failure modes (required)

| Failure | User impact | Mitigation / trace |
|---------|-------------|-------------------|
| A dependency or helper phones home (telemetry, update check) | A friend's name leaves the machine | AC-PRIV-20, NFR-PRIV-10 |
| The reader's own items or borrowers are pasted into a fixture, spec or comment | The reader's answers leak into the repository history | AC-PRIV-10 |
| A refused save still writes a half-record | An unreal item shows as lent | AC-LEND-20 |
| A save reports success but the record is not kept | The owner trusts a record that is not there | AC-LEND-10, FR-LEND-10 |
| Contacts access is added to fill in the borrower | Third-party data enters the app | NFR-PRIV-10 |
