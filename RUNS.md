# Runs

One line per run of Bang, newest first: date, machine, how long, where you stopped or
stumbled, in your own words. Add yours and open a pull request; that is the whole report.

- 2026-09-25, panda, fresh user, pin `b23fcc3`: **the first run to reach the review
  door, and the first to be refused by it.** Spec asked no question. Build wrote
  `src/whms/web.py`, `src/whms/pages.py` and `tests/test_web.py`, eight tests named for
  the ids, and ticked T904 in `specs/backlog/tasks.md`, which is what
  `cannon-template/agents/build.md` tells a worker to do with a reservation its spec has
  claimed.

  The Gate then went RED on this project's own
  `tests/test_shipped_promises.py::test_the_first_card_carries_the_five_ids_the_seed_leaves_unbuilt`,
  which read the tick as the browser having shipped in the seed again. The worker put
  T904 back to open, wrote on the line why it had, and left it for a person rather than
  arguing with a check; the Gate went GREEN at `398b4ce`. Then
  `column-check.py --tasks-ticked` refused the card at the door into Review, naming the
  T904 line it had just reopened.

  Two rules that had never been run together, each doing its job: tick the reservation
  your spec claims, and do not promote a card whose open tasks carry its own ids. The
  card was right both times and could not move either way. That is the check working,
  and the guard is what was wrong: it was written as a statement about the T904 line
  when it is a statement about the seed. Fixed here.

- 2026-09-25, Dell 7420, cold Windows user, Bang at `a530286`: stopped at step 2, by the
  preflight, correctly. It caught the Microsoft Store stub that holds the `python3` name
  and printed the winget line it was written to print. That part worked exactly as
  designed.

  Then the part nobody had checked. `winget install --id Python.Python.3.12` installed
  Python, `python --version` printed 3.12.10, and `python3` still did not resolve. It
  never will: the python.org build lays down `python.exe` and `py.exe` and no
  `python3.exe`, and the Store's App Execution Alias holds the `python3` name whether
  Python is installed or not. The preflight would have refused the same way a second
  time, on a machine with a working Python on it.

  So `python3` is not a name this project may spell. `scripts/python.sh` resolves it
  once, by asking which of `python3` then `python` prints a line beginning `Python 3`,
  and forty call sites across seven scripts now go through it. The Mac is unchanged and
  lands on `python3`; Windows lands on `python`. Fixed here.

- 2026-09-25, Dell 7420, rik, Bang at `a31d799`: the Windows walk, and the first run of
  this on anything that is not a Mac. Fresh Windows 11 has no git at all. `winget`
  installed Git 2.55, and the window had to be closed and reopened before its path knew
  about it. `irm https://claude.ai/install.ps1 | iex` installed Claude Code 2.1.282 with
  the same path gap the Mac installer has, and the PowerShell path line closed it.
  Clone, then the opening line.

  Claude Code's Bash tool on Windows runs in Git Bash, so steps 1 and 2 of `BANG.md` ran
  as written and printed their receipts. The worker then read ahead and stopped before
  step 3, which is the right thing to do with a file it cannot carry out, and named four
  parts written for a Mac and only a Mac: `python3` on Windows is a Microsoft Store
  placeholder rather than an interpreter; step 4's Node download is darwin-only; step 3's
  uv line is `install.sh`; step 8 is a LaunchAgent. The Cannon was never reached.

  That refusal is what PR #19 was. `BANG.md` now reads `uname -s` at step 2 and carries a
  Windows text for each of those four. None of it has been walked yet. The next run on
  that Dell is the test. (This line went in naming the wrong machine and a thinner
  account of the walk; corrected the same day.)

- 2026-09-25, shark, fresh user, Bang at `7b386ef`, pin `cb39b5b`, blind return at every
  prompt: **the first run to reach the review column.** Install clean, board showing only
  Bang, the daemon shark's own. BAN-1 dragged, and the board ran it: Spec with no
  question asked, Build writing five tests named for their ids, the Build runner GREEN
  and the Gate runner GREEN, then promoted. About twenty-five minutes from the drag.

  `potato/BAN-1` was cut from `main` at `63a2629`, the tip after both install commits,
  and ended at `ebbefb5` with spec `006-browser-screens` and forty tests. That is fork
  #19 proven on a cold user rather than on a fixture: the base was the branch the
  project was actually on, which is what ginger's run could not get.

- 2026-09-25, ginger, fresh user, Bang at `065afab`, blind return at every prompt:
  install clean, board open showing only Bang, and step 8's health check was ginger's
  own daemon. BAN-1 dragged to Spec at 11:43:39Z. The Spec worker refused, correctly:
  its worktree had no `.specify/` and no checker, and it did not copy them in. Build then
  refused on `column-check` because the spec named none of the card's five ids, there
  being no spec. The card sits in Spec.

  The cause, read from the clone rather than guessed: `main` was at `0ce8c90`, two
  commits past the clone after steps 5 and 6; `origin/main` was still `065afab`, because
  nothing is pushed, by rule; and `potato/BAN-1` was at `065afab`. The Cannon cut the
  card's branch from `origin/main`, which for a project that never pushes is stale from
  the moment step 5 commits. The card's base was a commit the project had already left.
  Fixed in the fork, not here: rdryfoos/potato-cannon#19.

- 2026-09-25, parrot, fresh standard user, Bang at `065afab`: stopped at step 8. Steps 1
  to 7 were clean and every receipt matched. Step 8 found a daemon already holding
  127.0.0.1:3131, belonging to a previous test user on the same machine; `/health`
  answered ok with nine and a half hours of uptime on a daemon installed minutes
  earlier, and the worker refused to treat that as its own. It was right to. Nobody
  outside a shared test bench will meet this, but three things came out of it: the
  script now checks the port before it writes anything, step 8's receipt proves the
  listener is ours, and BANG.md stopped claiming the clone has no origin.

- 2026-09-25, sandi: lost to sleep. The machine slept partway through and the run was
  not resumed, so there is nothing to report from it. It is here because a run that was
  started and produced no answer is still a fact about how often that happens.

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
