# Runs

One line per run of Bang, newest first: date, machine, how long, where you stopped or
stumbled, in your own words. Add yours and open a pull request; that is the whole report.

- 2026-09-23, MacBook Pro (Apple silicon, Homebrew already present), about ten minutes,
  Bang at `de27709`: the first cold run, by Rik, from the three blocks in the README.
  It stopped once, at the step 6 receipt, and continued. It finished: the board is open
  in the browser with BAN-1, BAN-2 and BAN-3 in Ideas.

- 2026-09-22, Mac Mini (macOS 15, Python 3.9.6), about ten minutes, not a cold run: a
  throwaway checkout for PR #4, built by laying this repository's `src`, `tests`, `specs`,
  `scripts` and `design` over a project that already had `.specify/` installed, because
  this repository does not ship it. So the run proves the checks and the tests, not
  `BANG.md`. The Gate went green first time and the two new tests passed. What I stumbled
  on: nothing in the run itself, but the harness had to be assembled by hand, and until
  somebody follows `BANG.md` from an empty folder on a machine that has never seen this,
  the first line of the README stands.
