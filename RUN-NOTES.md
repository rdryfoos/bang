# Run notes

`README.md`'s "Run it" is pastes and one-line beats, and nothing else, because a page
you are reading with a terminal open beside you is a page you are scanning rather than
reading. Everything it used to say between the fences is here. Read this before you
paste, or after it stops; both are what it is for.

`RUNS.md`, which is nearly this file's name, is a different thing: one line per run of
Bang, by whoever ran it.

## Before you start

Bang needs a Mac or a Windows PC, an Anthropic account, and two clocks. About ten
minutes to install, most of it saying yes. Then the first card takes the board about
twenty-five minutes on its own; you can watch, or come back.

It writes to a handful of places in your home folder and nowhere else. `BANG.md` lists
them, lists what it fetches, and lists what it will not do. Read `BANG.md` before you
run it, and read its paragraph that begins "Read this one twice" twice.

Windows is new here and nothing on that page claims it works yet. One walk on one Dell
is what `RUNS.md` has; yours is the next one, and the line you add to `RUNS.md` is
worth more than the line above it.

## What each paste does

### On a Mac

**1. Get Claude and the rest.** Skip the first three lines if you already have Claude
Code. If git asks to install the command line developer tools first, let it; that is
Apple's, not ours. Lines two and three put Claude Code on your path, and the installer
prints the same instruction; `source ~/.zshrc` is why there is no window to reopen.
The last three clone the project to `~/bang`, go in, and start Claude Code there with
the instruction already in its hands. That last line is the whole of what Bang is told
to do, and it is the same line on both machines.

### On Windows

Each paste on its own, and each one finished before the next means anything. That is
why they are seven beats rather than two blocks: a line pasted into a window that is
still busy goes to whatever is running there, not to the shell.

**1. Get git,** in PowerShell, which Windows already has.

**2. Reopen, then get Python.** Windows reads the user path when a window opens and
never again, so the window you typed beat 1 into cannot see git yet. `BANG.md` needs
Python from step 2 and the project's own scripts need it throughout, and a fresh
Windows has none.

**3. Get Claude Code.** It is an installer, and a line pasted while it is still
running goes to the installer rather than to PowerShell. On the second Windows walk
that is how the path line below was swallowed and never ran.

**4. Wait for it to finish, then put Claude Code on your path.** It writes your own
path setting and not the machine's, so it needs no administrator and touches nothing
another user of this PC would see.

**5. Reopen, and get the rest.** For the path again: the window you typed beat 4 into
cannot see it. A new PowerShell, and not Git Bash. Claude Code's own shell on Windows
is Git Bash whatever window launched it, so every command in `BANG.md` runs in bash
regardless, and the window you start it from only has to be one that can see the path.
Every Windows run so far has done this paste in PowerShell and it worked. In the new
window `claude --version` should answer; if it does not, beat 4 is what to look at,
and nothing below will work until it does.

  `$HOME\bang` and not `~/bang`, which is the only line in this
paste that differs from the Mac's. On the Dell, `git clone` with `~/bang` stopped with
"could not create leading directories of '~/bang': Permission denied", which reads
like a permissions problem and is a spelling one: git was handed a tilde and made a
folder named for it. `$HOME` is expanded before git sees it, in either shell, so git
is handed a real path. The `cd` would have worked either way; it matches the clone so
that the two lines cannot drift apart.

## What the prompts mean

Sign in when it asks.

After the "Claude can make mistakes" screen, the next prompt is "Yes, I trust this
folder"; yes is not the default, so pick it.

If the bottom line of Claude Code says auto mode, press shift+tab until it says manual
mode. Auto mode refuses steps 6 and 7 on its own, and if Claude Code offers to switch
to auto mode, say no.

The board opens in your browser when it finishes. The last line is in the terminal.

When it is done, Claude Code offers a suggested next message, and pressing return
accepts it rather than dismissing it. So stop pressing return at `Bang done`: the
board is open in your browser and the drag is yours to do there.

## If Claude Code refuses a command as untrusted

It prints the line it wanted to run. Type `!` at its prompt followed by that line,
exactly as printed, which runs it here and puts the output in the conversation; then
tell it to carry on.

Nothing else: do not reword the line, do not turn the permission check off, and do not
switch to auto mode. The line is the receipt, and a line you improved is a receipt for
something else.

This is not rare and it is not a Windows thing. The session refuses a script it
installed a moment earlier, because it has no history with it. Zebra met it on a Mac
on 2026-09-23 and the Dell met it on 2026-09-25, and between the two nothing had been
written down, so the second reader worked it out again.

## If it stops

It is meant to. `BANG.md` prints a receipt after every step and stops at the first one
that does not match, rather than carrying on over it, so a run that stops has told you
where. Read the receipt it printed and the step above it.

A stop is a result. Write it down.

## When it finishes, or when it stops

When it finishes, or when it stops, add one line to `RUNS.md` saying what happened and
open a pull request. `CONTRIBUTING.md` says how; it is three sentences.
