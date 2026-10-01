# Who Has My Stuff — Product Requirements (ID Registry)

This PRD is the **authoritative ID registry** for the First Light house case. It
is pre-decomposed from `CASE.md`: every promise in
the CASE becomes a durable ID here, and specs, tasks, `@covers` marks, and
`test_AC_*` proofs trace back to these IDs. Gate 2 enforces the exact-set rule.

The operator fills their own items, people, and wording into the CASE. The IDs
below do not change when they do — that is the point of creating at intent.

## Lending an item out

- US-LEND-10 — As the owner, I write down what I lent, to whom, and when, so I stop relying on memory. **Authorship**: case
  - FR-LEND-10 — An item record holds a name, a borrower, and a date out. **Authorship**: case
    - AC-LEND-10 — An item saved with a borrower and a date out appears in the outstanding list immediately. **Authorship**: case
    - AC-LEND-20 — An item saved without a borrower is refused, with the reason shown to the owner. **Authorship**: design

## Seeing what is still out

- US-OUT-10 — As the owner, I can see everything still out without hunting. **Authorship**: case
  - FR-OUT-10 — The outstanding list shows every item not yet marked returned, oldest first. **Authorship**: case
    - AC-OUT-10 — An item marked returned no longer appears in the outstanding list. **Authorship**: case
    - AC-OUT-20 — With nothing outstanding, the list says so in words rather than showing an empty screen. **Authorship**: design
    - AC-OUT-30 — Each item in the outstanding list shows what it is, who has it, and the date it went out. **Authorship**: design

## Returning an item

- US-RET-10 — As the owner, I mark a thing returned and it stops nagging me. **Authorship**: case
  - FR-RET-10 — Marking returned records the date back and moves the item out of outstanding. **Authorship**: case
    - AC-RET-10 — Marking an item returned records the date it came back, and that date survives a restart. **Authorship**: design

## Cross-cutting

- NFR-PRIV-10 — Borrower names and item records never leave this machine. No network calls, no cloud storage, no third-party services, no contacts access. **Authorship**: case
  - AC-PRIV-10 — No file under the repository contains a value from the local answers. The reader's filled CASE lives outside the worktree at BANG_CASE_FILE; nothing in this repository, at any commit, carries an item, a borrower, or a date from it. **Authorship**: design
  - AC-PRIV-20 — The application makes no outbound network request during any lending, listing, or returning operation. **Authorship**: case
  - AC-PRIV-30 — The app says on screen where the records are kept, on every screen a person sees. **Authorship**: design
- NFR-DUR-10 — Records survive restarting the application. **Authorship**: design
  - AC-DUR-10 — After a restart, every lend and return recorded before the restart is still present with its dates. **Authorship**: design
- NFR-ENG-10 — Records are written by one path: every entry point onto them, present and future, calls the engine's operations and keeps no write of its own. **Authorship**: retrospective
  - AC-ENG-10 — No file under src/whms other than the engine modules writes a record. The rule is read from the source and binds every entry point, present and future: a module added later that writes a record of its own fails the same test. **Authorship**: retrospective

## Screens

The sketch of this software lives in `design/` and is governed like this file. Each
screen names the IDs it fulfils; `design/README.md` is the map, and it is where what
the screens are, and what a build reads from them, is said.

## Screen promises

- US-UI-10 — As the owner, I lend, see what is out, and mark things returned on a screen in my browser, not only at the command line. **Authorship**: design
  - FR-UI-10 — A local web app serves the four screens in design/ and reads and writes the same records file the command line does; nothing leaves the machine. **Authorship**: design
    - AC-UI-10 — Opening the app shows the outstanding list, oldest first with days out, or says in words that nothing is out when nothing is. **Authorship**: design
    - AC-UI-20 — Lend something takes what, to whom, and a date out defaulting to today; a missing borrower is refused in place and nothing is saved. **Authorship**: design
    - AC-UI-30 — Mark returned takes a date back defaulting to today; the item leaves the list at once and the record survives a restart. **Authorship**: design
    - AC-UI-50 — Every item in the outstanding list carries its own Mark returned control. **Authorship**: design
    - AC-UI-60 — The outstanding list and the nothing-out screen each offer a way to lend something. **Authorship**: design
    - AC-UI-70 — From Lend something and from Mark returned there is a way back to the outstanding list that records nothing. **Authorship**: design
    - AC-UI-80 — The Mark returned screen names the item, who has it and when it went out, before anything is recorded. **Authorship**: design
- US-UI-20 — As the owner, when I lend something I see what I have lent that person before and whether it came back, so I decide with the history in front of me. **Authorship**: design
  - AC-UI-40 — On the Lend screen, once a borrower is named, the app lists what that person has had before, showing what came back and what is still out; a borrower with no history shows nothing extra. **Authorship**: design

---

## Session design (why these IDs are shaped this way)

Not part of the registry. Notes for whoever runs the run-through.

**The one built to be broken.** `AC-OUT-10` is the deliberate refusal. Once the
thread is green, rename its test so it stops matching the ID, run the Gate, and
watch it fail with the silent gap named and the trace-manifest written anyway.
Restore the name and the thread holds again.

**The honest debt.** `AC-OUT-20` ships as tracked debt: created, carried by an
open task, no proof yet. The operator sees amber and learns that passing does
not mean finished, it means nothing unfinished is hidden.

**The one the machine will quietly break.** `NFR-PRIV-10` with `AC-PRIV-20` is
the heart of the demo. Agents reach for sync, telemetry, cloud persistence, and
contacts access unprompted. If the agent adds any of it, the mark is missing and
the promise has a proof that fails, and the operator sees the thread catch
something they never watched happen. If the agent behaves, the same IDs are the
receipt that it behaved. Either outcome is a good first run-through.

**Reserved backlog.** `NFR-DUR-10` carries no implementation on the first pass
and stays at planning altitude with an open `Carries:` TODO, so the operator
meets the blue state too.

---

## Record: the registry was re-created by the tool, 2026-09-19

Every ID above was created by `.specify/extensions/specassay-check/scripts/mint-id.sh`,
in the order the entries appear, with the prose under each left exactly as drafted.

The draft registry numbered everything `-01` and `-02`. That range is not a
numbering the tool ever issues: primary creates land on multiples of ten, and 1
through 9 is a lane reserved for resolving a collision. So a registry written
that way holds no machine-created ID at all, while the run-through's second step
teaches that the machine creates the ID and never renumbers it. The draft is
recorded here rather than kept.

`AC-PRIV-10` is not in the table. It was created by the tool before the rest,
as the criterion covering the local answers, and it keeps the number it was
born with.

| Draft ID | Created ID |
|---|---|
| `US-LEND-01` | `US-LEND-10` |
| `FR-LEND-01` | `FR-LEND-10` |
| `AC-LEND-01` | `AC-LEND-10` |
| `AC-LEND-02` | `AC-LEND-20` |
| `US-OUT-01` | `US-OUT-10` |
| `FR-OUT-01` | `FR-OUT-10` |
| `AC-OUT-01` | `AC-OUT-10` |
| `AC-OUT-02` | `AC-OUT-20` |
| `US-RET-01` | `US-RET-10` |
| `FR-RET-01` | `FR-RET-10` |
| `AC-RET-01` | `AC-RET-10` |
| `NFR-PRIV-01` | `NFR-PRIV-10` |
| `AC-PRIV-01` | `AC-PRIV-20` |
| `NFR-DUR-01` | `NFR-DUR-10` |

Nothing carried these IDs when they changed: no card, no spec, no `@covers`
mark and no test existed yet. That is why this was possible, and why it had to
happen before phase 2 rather than after.

## Record: the project corrected its author, 2026-09-20

The session-design notes below say the empty-list promise "ships as tracked debt:
created, carried by an open task, no proof yet", and that the operator "sees amber"
on the first run. The run-through was written to promise three colors at the first
Gate.

The first card's Gate ran green on 2026-09-20 and the trace-manifest showed two
colors, not three: seven promises proven, eight backlog, nothing amber and
nothing red.

The Gate is right and the note was wrong. Tracked debt is work that started and
has no proof yet, declared on an open task. A promise that no spec has claimed
has not started, so it sits at planning altitude with everything else in the
backlog. The promotion contract says so plainly in rule 5a: an reserved ID rides
as backlog, acceptance criteria included, and an reserved criterion is not a
silent gap.

So the amber the notes expect arrives with the second card, when its spec claims
the empty-list promise and ships it without a test. Ruled 2026-09-20: no debt is
declared on the first card to manufacture a color, and `DEMO-RUN-THROUGH.md` step 4
now tells the newcomer to expect green and blue, with amber named as the thing
the second card brings.

The notes below are left as written. They are the design this project was built
from, and the correction is worth more beside them than in place of them: the
machine checked the plan, the plan was wrong in one particular, and the record
says which.

## Record: authorship filled on all thirty-one rows, 2026-09-30

Every row above now carries `**Authorship**: <value>`, one of `case`, `design`,
`retrospective` or `constitution`. The word the registry used for two different
things was intent: what a person outside this project wanted, and what the project
holds itself to. Authorship answers the first of those and nothing else. It says who
wrote the row, not where the row lives.

Ten rows are `case`, two are `retrospective`, nineteen are `design`, and none is
`constitution`.

Three things the reading pass turned up. They are recorded rather than fixed: none of
them changes an ID, and a re-creation would.

**Two rows carry a design clause inside a case row.** `FR-OUT-10` says the outstanding
list shows every item not yet marked returned, which is the reader's second promise,
and then says "oldest first", which the CASE never asks for. `FR-RET-10` says marking
returned moves the item out of outstanding, which is the reader's third promise, and
then says it records the date back, which the CASE never asks for either. Both are
marked `case` on the clause that dominates. Whoever splits a row one day should start
with these two, because each is two authors in one sentence and the mark can only name
one.

**No `case` row serves the reader's own test.** The CASE says how the reader would know
it worked: "I lend something on a Tuesday, and three weeks later I can still say who
has it without opening a drawer." The only row that makes that checkable is
`AC-OUT-30`, which says each item in the list shows what it is, who has it, and the
date it went out. It is marked `design`, because it was created on 2026-09-29 out of
the survey of what the screens drew that no criterion named, and that survey is its
author. So the sentence the reader offered as the test of the whole thing is served by
a row the reader did not write. That is not wrong, and it is worth knowing.

**`FR-UI-10` restates two other rows in one line.** "Nothing leaves the machine" is
`NFR-PRIV-10`. "Reads and writes the same records file the command line does" is
`NFR-ENG-10`. Neither clause is this row's own promise, and this row is marked `design`
for the part that is: a local web app serving the four screens. A reader checking
`FR-UI-10` is checking three rows without being told so.
