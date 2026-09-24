Bang is one command that leaves you with a working project on your own machine: a
small lending tracker, its specification with durable IDs, the checks that refuse
unfinished work, and a board in your browser with the first cards already on it.
`BANG.md` is the whole instruction, and it is meant to be read before you paste
anything: it lists every folder that will be written, everything fetched from the
network, and how to undo all of it. The application the project builds is a personal
lending tracker, for keeping track of what you have lent and to whom, and every item
and person in this repository is invented.

## Run it

Bang needs a Mac, an Anthropic account, and two clocks. About ten minutes to install,
most of it saying yes. Then the first card takes the board about twenty-five minutes on
its own; you can watch, or come back.

It writes to five places in your home folder and nowhere else; `BANG.md` lists them, and
lists what it fetches and what it will not do. Read `BANG.md` before you run it, and read
its paragraph that begins "Read this one twice" twice.

Two blocks, in order, both pasted into Terminal.

Block 1, "Get Claude". Skip it if you already have Claude Code. If git asks to install
the command line developer tools first, let it; that is Apple's, not ours.

```
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

The second and third lines put Claude Code on your path; the installer prints the same
instruction.

Block 2, "Get the rest". Clones the project to `~/bang`, goes in, and starts Claude Code
there with the instruction already in its hands.

```
git clone https://github.com/rdryfoos/bang.git ~/bang
cd ~/bang
claude --permission-mode manual "Read BANG.md in this folder from top to bottom. Then carry out its Steps in order, printing the step summary before each and the receipt after. If a receipt does not match, stop and print what you saw. Do nothing that BANG.md does not say."
```

Sign in when it asks. Choose "Yes, I trust this folder" when Claude Code asks; that is
Claude Code's own question about the folder you just cloned. If the bottom line of Claude
Code says auto mode, press shift+tab until it says manual mode; auto mode refuses steps 6
and 7 on its own. The board opens in your browser when it finishes; the last line is in
Terminal.

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
