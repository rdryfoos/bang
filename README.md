Bang takes a bare Mac or Windows machine (Omarchy Linux soon) to a working,
"born-threaded" project with a board in your browser: a couple of pastes, about ten
minutes, then your first card. What you are left with is a small lending tracker, its
specification with durable IDs, the checks that refuse unfinished work, and the first
cards already on the board.

`BANG.md` is the instruction set the agent follows. It is written for people too, so
you can read exactly what the agent will do before you paste anything. `RUN-NOTES.md`
is the detailed explainer, tailored for human readers: what each paste does, what the
prompts mean, and what to do when it stops. The project builds a small lending
tracker, what you have lent and to whom; names in the sample were changed to protect
the guilty.

## Run it

You need an Anthropic account; the pastes install everything else.

### On a Mac

1. One paste in your favorite terminal:

```
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
git clone https://github.com/rdryfoos/bang.git ~/bang
cd ~/bang
claude --permission-mode manual "Read BANG.md in this folder from top to bottom. Then carry out its Steps in order, printing the step summary before each and the receipt after. If a receipt does not match, stop and print what you saw. Do nothing that BANG.md does not say."
```

2. Say yes when it asks whether you trust this folder: the default is "No, exit", so arrow to Yes before you press return. Then press return for "Yes" at each prompt after that, until it prints Bang.

3. Bang means go to your browser: the board is open there, and you drag BAN-1 to Spec by hand. Ignore anything Claude Code suggests typing next.

### On Windows

1. In PowerShell, which Windows already has. Get git and Python.

```
winget install --id Git.Git -e --source winget
winget install --id Python.Python.3.12 -e --source winget
```

2. Get Claude Code, and let it finish before you paste anything else.

```
irm https://claude.ai/install.ps1 | iex
```

3. Put Claude Code on your path.

```
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ";$env:USERPROFILE\.local\bin", 'User')
```

4. Close that window and open a new PowerShell, and get the rest.

```
git clone https://github.com/rdryfoos/bang.git $HOME\bang
cd $HOME\bang
claude --permission-mode manual "Read BANG.md in this folder from top to bottom. Then carry out its Steps in order, printing the step summary before each and the receipt after. If a receipt does not match, stop and print what you saw. Do nothing that BANG.md does not say."
```

5. Say yes when it asks whether you trust this folder: the default is "No, exit", so arrow to Yes before you press return. Then press return for "Yes" at each prompt after that, until it prints Bang.

6. Bang means go to your browser: the board is open there, and you drag BAN-1 to Spec by hand. Ignore anything Claude Code suggests typing next.

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
