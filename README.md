Bang is one command that leaves you with a working project on your own machine: a
small lending tracker, its specification with durable IDs, the checks that refuse
unfinished work, and a board in your browser with the first cards already on it.
`BANG.md` is the whole instruction, and it is meant to be read before you paste
anything: it lists every folder that will be written, everything fetched from the
network, and how to undo all of it. The application the project builds is a personal
lending tracker, for keeping track of what you have lent and to whom, and every item
and person in this repository is invented.

## Run it

Bang needs a Mac, an Anthropic account, and about ten minutes, most of it approving
steps. It writes to five places in your home folder and nowhere else; `BANG.md` lists
them, and lists what it fetches and what it will not do. Read `BANG.md` before you run
it, and read its paragraph that begins "Read this one twice" twice.

Three blocks, in order, each pasted into Terminal.

Block 1, once per machine. Installs Claude Code for your user and signs you in. If git
asks to install the command line developer tools first, let it; that is Apple's, not
ours.

```
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
claude
```

The second and third lines put Claude Code on your path; the installer prints the same
instruction. Sign in when it asks, then type `/exit`.

Block 2. Puts the project at `~/bang` and opens Claude Code in it.

```
git clone https://github.com/rdryfoos/bang.git ~/bang
cd ~/bang
claude
```

If you paste block 2 into Claude Code by mistake, it still works; then paste block 3.

Block 3, pasted into Claude Code, not Terminal.

```
Read BANG.md in this folder from top to bottom. Then carry out its Steps in order,
printing the step summary before each and the receipt after. If a receipt does not
match, stop and print what you saw. Do nothing that BANG.md does not say.
```

The board opens in your browser when it finishes. The last line is in Terminal; go back
and read it.

When it finishes, or when it stops, add one line to `RUNS.md` saying what happened and
open a pull request. `CONTRIBUTING.md` says how; it is three sentences.

## What you were handed

Four files, one sentence each. CASE.md: the problem in plain words,
with invented people and items, never real ones. PRD.md: the
promises (sometimes called requirements), each with an ID that never
changes, which every card and test refers to by name. design/:
wireframe-grade screens the build reads from; the README says which
parts are binding. CONSTITUTION.md: the rules every worker reads
before it touches a file. Run a few cards through with these files
as they are, so you see the machinery move on something that is
reasonably clear and simple.

## Your own project

When the board has done what the page promised, the second project
is yours: clone bang again into a folder of your own name, replace
CASE.md with your case (the template is CASE-TEMPLATE.md, the same
questions), empty PRD.md of the lending promises and write your
own, redraw or delete the screens, keep the constitution. The how-to
there is basic lean product management. A design loop focused on
understanding users, their needs and motivations, their journey and
workflow, and defining an MVP to test is the real "what's next" step.
