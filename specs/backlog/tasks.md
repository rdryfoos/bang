# Backlog: reserved, created on purpose and not yet picked up

Reserved backlog is a registry ID whose **only** carrier is an open `- [ ]` TODO. It is
deliberately not in any spec, has no `@covers` mark and no `test_AC_*` proof. The open
TODO is what proves the intent was created rather than drifted in, and it is what keeps
the Gate from reading the ID as a silent gap.

Written 2026-09-20, as a correction to this project's birth. Phase 1 created a registry of
fifteen promises and built none of them, so every ID outside the first card read as a
silent gap and the first card could never be green through no fault of its own. That is
what this file answers.

Each line below says what will deliver it, not who. A card here is a card on somebody's
board, and the cards this project shipped from were a rehearsal on one machine: a line
that named BANV-4 named nothing a reader could ever open. When a spec claims the ID, the
reservation expires and the normal rules apply: the ID has to be proven or declared as
debt on an open task of its own.

## Seeing what is still out

- [x] T900 Deliver the outstanding list end to end, oldest first. **Carries**: US-OUT-10, FR-OUT-10, AC-OUT-10 (reserved backlog). Carried by card BAN-2.
- [x] T901 Say in words that nothing is outstanding, rather than showing an empty screen. **Carries**: AC-OUT-20 (reserved backlog). Carried by card BAN-2, and expected to ship as tracked debt on purpose: the PRD's session design names this one as the promise the reader meets in amber, so they learn that passing does not mean finished.

## Marking a thing returned

- [ ] T902 Deliver marking an item returned, with the date it came back. **Carries**: US-RET-10, FR-RET-10, AC-RET-10 (reserved backlog). Reserved, no card yet.

## The screens

- [ ] T904 Deliver the four screens `design/` draws as a local web app over the same records file the command line writes. **Carries**: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30 (reserved backlog). Reserved, no card yet. It was closed once, on the rehearsal board, and the work shipped in the seed; the seed then had nothing left for a reader's first card to do, so on 2026-09-23 the screens came back out and this reservation with them. `design/` is the brief and `NFR-ENG-10` is the rule the build is held to.

## The borrower's history

- [ ] T905 Show what a borrower has had before, on the Lend screen, once they are named. **Carries**: US-UI-20, AC-UI-40 (reserved backlog). Reserved, no card yet.

## No card yet

- [x] T906 Make every entry point call the engine's operations and keep no write of its own. **Carries**: NFR-ENG-10, AC-ENG-10 (reserved backlog). The reservation expires now that a spec claims it: `specs/005-one-write-path`, written by hand on 2026-09-22 for work done in PR #4 and narrowed on 2026-09-23 when the browser came out of the seed. Both IDs are proven by `tests/test_one_write_path.py`, which reads the source and names no entry point, so it binds T904's screens when they are built. `src/whms/store.py` carries the marks. No card; the work was done by hand.

- [x] T903 Make records survive restarting the application. **Carries**: NFR-DUR-10 (reserved backlog). Carried by card BAN-5, spec `specs/003-records-survive-restart`. It was the blue the reader was meant to see on the first pass, with no card behind it; the reservation expires now that a spec claims it.

## One thing learned writing this file

Every task above keeps its whole **Carries** list on one line. The Gate reads that field
line by line, so a task whose IDs wrap onto a second line has the IDs on the second line
read by the exact-set scan, which greps the file, and missed by the pending scan, which
reads the task. The first draft of this file wrapped, and the result was three acceptance
criteria that counted as claimed and still reported as silent gaps. Nothing warned; the
two scans simply disagreed.
