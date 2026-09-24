# Runs

One line per run of Bang, newest first: date, machine, how long, where you stopped or
stumbled, in your own words. Add yours and open a pull request; that is the whole report.

- 2026-09-24, MacBook Pro (Apple silicon, fresh standard user), about ten minutes to
  install, Bang at `302a5fd`: the fourth cold run, by Rik, and the first that reached a
  board and then ran a card on it. BAN-1 went through Spec with no question asked, Build
  wrote ten tests named for their criteria, and the Gate went GREEN on the second Build
  iteration. Spec took nine minutes and Build twenty-six including the retry.

  It could not be promoted. `scripts/column-check.py` refused the card, because the Build
  worker had written `branch: potato/BAN-1 at 213f8b6` and the check takes everything
  after `branch:` as a branch name. The work was finished and proven and the board would
  not let it through, which is the best kind of refusal to find: the card was right and
  the two files that had to agree about one line did not.

  The first Build iteration also reported MISSING TOOL, because `.specify/` was in the
  checkout and in no worker's worktree. The worker copied it in and carried on, which is
  a worker fetching its own judge. Both are fixed here.

- 2026-09-23, MacBook Pro (Apple silicon, fresh standard user), Bang at `4034d05`: the
  third cold run, by Rik, abandoned at step 6 by decision rather than finished. Steps 1 to
  5 were clean: `.specify` committed on main, Node 22 under `~/.potato-cannon/node`, the
  tester's own Node untouched. It stopped at step 6 in auto mode, which is now Claude
  Code's default on a fresh install, so the README's instruction to leave Claude Code in
  its normal permission mode was not enough: it asked the reader to undo a mode they never
  chose. Block 2 now starts Claude Code in manual mode itself.

- 2026-09-23, MacBook Pro (Apple silicon, fresh standard user), about ten minutes, Bang at
  `157f672`: the second cold run, by Rik. It stopped once at the step 6 receipt because
  Claude Code was in auto mode; continued in default mode. It finished: the board is open.
  (Added later the same day, with the third run's line: this one was written into that
  run's report and its pull request description and never into this file, and the miss was
  found while adding the third above it.)

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
