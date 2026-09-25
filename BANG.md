# BANG.md

This file is what your Claude Code session is told to carry out when you
paste block 2 in README.md. Read it before you paste. The agent reads the
same file, in this order, and does nothing that is not written here.

Bang leaves you with a working project: this folder, ~/bang, holding a
small ready-made application, its specification with durable IDs, the
checks that refuse unfinished work, and a running Potato Cannon board in
your browser with the first cards on it. You do not need to be an
administrator of this computer.

## What this writes on your machine

Everything this file does lands in one of these places, and nowhere else.

1. `~/bang/`  This folder, which you cloned. It is the project your board
   works in; nothing else is built here.
2. `~/.local/bin/`  Two small command-line tools: `uv` (a Python tool
   installer) and `specify` (Spec Kit). Both are user-level; nothing goes
   into /usr or /opt.
3. `~/.potato-cannon/`  Potato Cannon's own home: the built application
   under `app/`, its settings file, its database, the registration of
   ~/bang as a project, and a copy of the workflow template it runs. Node
   22 goes in here too, under `node/`, and so does every package cache the
   build fills: corepack's, pnpm's store and cache, and npm's prebuilds.
   They are pointed here on purpose. Left to themselves they write about a
   gigabyte into `~/.cache`, `~/Library/pnpm` and `~/.npm`, three places
   this file would then have to list and Undo would have to reach into;
   here they are one folder that Undo removes whole.
4. `~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist`  One launch
   agent so the Cannon daemon starts when you log in and listens on
   127.0.0.1:3131 only. It is never reachable from another machine.
5. `~/.claude/projects/`  One folder per working copy the Cannon runs a
   worker in, holding that worker's session transcript as a `.jsonl` file.
   Claude Code writes these, not Bang, and it writes them for your own
   sessions too. They can be large: a card that goes round the board once
   leaves a few megabytes. Nothing else under `~/.claude/` is touched:
   your settings, your memory and your sign-in stay as they are.

Read this one twice: the Cannon's worker sessions run Claude Code with
permission prompts turned off (`--dangerously-skip-permissions`). That is
how a card moves from Spec to Build to Gate to Review without you
approving each file write. Three things stand in for the prompts you
would otherwise see. The project's rules file, `CONSTITUTION.md`, which
every worker reads first. A check called `scripts/governed-files.py`,
which refuses a card that changes the scripts or the screens that judge
it. And the working
copy itself: each card is built in its own copy of the project under
`~/bang/.potato/worktrees/`, so a worker's writes land there and not in
your checkout. The workers only ever run inside ~/bang. Your own
interactive Claude Code session, the one reading this file, runs with
prompts on as usual.

The instructions every worker reads are in `cannon-template/agents/`, one
file per worker, and they are the only copy: step 9 below installs that
folder as the project's template, and the workflow reads the prompts from
it. Read them before you paste anything, because they are the whole of
what a worker with the prompts turned off has been told to do.

What there is not, and you should know it: no check reads a card's
specification and refuses a file the specification did not name. A worker
that decides to change a source file nobody asked it to change will do so,
and the Gate will notice only if the change breaks a test or leaves an ID
unproven.

## What this fetches from the network

1. `https://astral.sh/uv/install.sh`  The uv installer, run as your user.
2. `specify-cli` from PyPI, via uv.
3. SpecAssay's Spec Kit catalogs and release files from
   `github.com/rdryfoos/specassay` (MIT).
4. Potato Cannon from `github.com/rdryfoos/potato-cannon`, branch
   `estate/cannon`, commit
   `cb39b5b88a5cb4cb38eaae99e6ba38bb3e070a06`, and the npm packages its
   build needs, fetched by pnpm from the public npm registry.
5. If Node is missing, the Node 22 tarball from `nodejs.org`.
6. Nothing else. No telemetry, no account, no message to anyone.

Potato Cannon is by crathgeb (github.com/crathgeb/potato-cannon), under the
Sustainable Use License: free for your personal and internal use. The copy
fetched here is a fork carrying three small patches, offered upstream as
pull requests; its license and notices are unchanged. Everything in ~/bang
is MIT.

## What this will not do

- Read, write, or list any folder outside the five places above.
- Touch any other repository, project, or file of yours.
- Push anything anywhere. `git clone` gave this folder an `origin`, because
  every clone from GitHub has one, and nothing here ever pushes to it: the
  project's promotions are local merges into its own main branch. `git fetch`
  is not run either. The remote exists and is never used.
- Install anything system-wide or ask for your password.
- Run a worker session outside ~/bang.

If a step below cannot be done inside those limits, the agent stops and
prints why, and nothing after that step runs.

## Steps

The agent carries these out in order. Before each step it prints the step
number and the one-line summary; after each it prints the receipt line
given. If a receipt does not match, it stops and prints what it saw.

1. Confirm where we are. `pwd` must be `~/bang` and `git rev-parse HEAD`
   and `git branch --show-current`. Receipt: the commit hash and the word
   main.

2. Check what is already here. Print the version of each of: `uv`,
   `specify`, `node`, `pnpm`, `claude`, `python3`. For each that is
   missing, say so. Do not install anything in this step. Receipt: six
   lines, present or missing. There is no minimum for `python3` yet: the
   checks ran on Apple's own 3.9.6 on 2026-09-23, so the version line is
   recorded rather than judged.

3. Install uv if missing, into `~/.local/bin`, with the installer named
   above. Then, in this terminal:

       export UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools"
       export UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache"
       export UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python"
       export UV_TOOL_BIN_DIR="$HOME/.local/bin"
       uv tool install specify-cli

   Those four are why this step does not put anything in a place this file
   never told you about. Left to itself uv keeps its tools in
   `~/.local/share/uv`, its cache in `~/.cache/uv` and any Python it
   downloads beside them, which is three more directories and several
   hundred megabytes. `UV_TOOL_BIN_DIR` is the exception and points at
   `~/.local/bin` on purpose: that is where the `specify` command has to
   land to be on your path, and `~/.local/bin` is already one of the five
   places.

   **Every later call to `uv` or `specify` carries the same four**, in this
   file, in `scripts/`, and in the launch agent's environment. A tool
   installed under one `UV_TOOL_DIR` is invisible to a call made without
   it, which is a confusing way to be told the thing you just installed is
   not there.

   Receipt: `specify --version` prints a version at or above 0.14.0, and
   `ls ~/.local/share/uv ~/.cache/uv` says both are missing.

4. Node and pnpm. **Node 22, not the current LTS.** The Cannon's database
   library has no prebuilt binary for newer Node and building it from
   source fails, so a newer Node will get you through this step and stop
   you at step 7. If `node --version` already starts with `v22.`, skip to
   pnpm. Otherwise, no administrator password needed:

       mkdir -p ~/.potato-cannon/node
       curl -fsSL -o ~/.potato-cannon/node22.tar.xz \
         https://nodejs.org/dist/v22.23.2/node-v22.23.2-darwin-arm64.tar.xz
       tar -xJf ~/.potato-cannon/node22.tar.xz -C ~/.potato-cannon/node --strip-components=1
       rm ~/.potato-cannon/node22.tar.xz
       export PATH="$HOME/.potato-cannon/node/bin:$PATH"
       export COREPACK_HOME="$HOME/.potato-cannon/corepack"

   On an Intel Mac, use `node-v22.23.2-darwin-x64.tar.xz` instead. Then
   enable pnpm through Node's own corepack:

       corepack enable pnpm

   **This Node lives in `~/.potato-cannon/node` and nowhere else.** It is
   the Cannon's Node, not yours: it is on the path only in the terminal
   you are working in now, and in the environment the daemon starts with,
   and it never shadows the Node you already had. That is why it does not
   go into `~/.local/bin`, which is on many people's path already, and why
   this file does not ask you to change your shell profile. `COREPACK_HOME`
   keeps corepack's downloads beside it rather than in `~/.cache`.

   The tarball is downloaded into `~/.potato-cannon` rather than `/tmp` so
   that every byte this file writes is inside one of the places listed
   above, and it is deleted as soon as it is unpacked.

   Receipt: `~/.potato-cannon/node/bin/node --version` prints a version
   beginning `v22.`, `pnpm --version` prints a version, and `node --version`
   in a new terminal window prints whatever you had before this step, or
   nothing if you had none.

5. Spec Kit on this project. The flag that names Claude Code is
   `--integration`. Initialise into this folder, which already has files
   in it:

       export UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools"
       export UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache"
       export UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python"
       export UV_TOOL_BIN_DIR="$HOME/.local/bin"
       specify init --here --force --non-interactive --integration claude

   `--here` means this folder rather than a new one, and `--force` skips
   the confirmation that a non-empty folder would otherwise ask for.
   Neither deletes what is already here: Spec Kit adds `.specify/` and
   `.claude/`, and leaves every file this repository ships.

   Then put this project's own rules in the place Spec Kit's commands
   read from:

       cp CONSTITUTION.md .specify/memory/constitution.md

   This project's own prompts read `CONSTITUTION.md` at the root, but
   every Spec Kit command a worker runs reads
   `.specify/memory/constitution.md`, and what `specify init` leaves
   there is Spec Kit's blank template. Without this copy a worker would
   plan and check its work against that template, whose heading still has
   a placeholder where the project's name should be.

   Then commit what Spec Kit added, on main:

       git add -A && git commit -m "Bang: Spec Kit initialised"

   Every card the board runs is built in its own worktree cut from a
   commit, and a worktree carries only what is committed. Left uncommitted,
   `.specify/` is in your checkout and in no worker's, so the first card to
   reach the Gate finds no checker and fails on a file that is three
   folders away on the same disk.

   Receipt: `.specify/` exists, `ls .specify/` is printed,
   `head -1 .specify/memory/constitution.md` prints
   `# Constitution: Who Has My Stuff`, `git status` is clean, and
   `git ls-tree HEAD .specify` prints the folder.

6. SpecAssay. Read the SpecAssay README from the network and do not save
   it anywhere: it is reference, and a copy of it written into a scratch
   folder is a file this project put on your machine outside the places
   listed above. Then add the three SpecAssay catalogs and install the
   bundle, exactly as that README's catalog path gives them. If the Gate
   config file is reported MISSING, copy it from the template as the
   README says. Then put this project's own settings in place of the
   installed defaults:

       cp cannon-template/specassay-check-config.yml \
          .specify/extensions/specassay-check/specassay-check-config.yml

   The installed file has two settings this project needs and ships
   commented out: `parent_derivation`, which is what makes the
   specification a tree rather than a flat list, and `test_results`,
   which is what makes a passing test count as proof rather than a test
   whose name merely matches. Receipt: the line beginning `config:` in the
   output of
   `bash .specify/extensions/specassay-check/scripts/check-traceability.sh`,
   which names this project's `specassay-check-config.yml`, and
   `grep ^parent_derivation .specify/extensions/specassay-check/specassay-check-config.yml`
   printing `parent_derivation: heading-nesting`. A WARN that
   `test-results.xml` does not exist is expected here; no test has run
   yet.

   Then commit what SpecAssay added, on main:

       git add -A && git commit -m "Bang: SpecAssay installed"

   This covers `.specify/` and the `.claude/skills/speckit-specassay-*`
   folders. It is here for the same reason step 5's commit is, and the
   fourth cold run proved it the expensive way: a card's worktree is cut
   from a commit and carries only what is committed, so BAN-1's first Build
   iteration reported MISSING TOOL because the checker was three folders
   away in your checkout and in no worker's. Uncommitted, the Gate cannot
   run on any card.

   Receipt adds: `git status` is clean, and
   `git ls-tree HEAD .specify/extensions/specassay-check` prints the
   folder.

7. Potato Cannon. Clone the fork into `~/.potato-cannon/app` at the branch
   and commit above, then, in the same terminal as step 4:

       export PATH="$HOME/.potato-cannon/node/bin:$PATH"
       export COREPACK_HOME="$HOME/.potato-cannon/corepack"
       export PNPM_HOME="$HOME/.potato-cannon/pnpm"
       export npm_config_cache="$HOME/.potato-cannon/npm-cache"
       cd ~/.potato-cannon/app
       pnpm install --filter '!@potato-cannon/desktop' \
         --store-dir "$HOME/.potato-cannon/pnpm-store" \
         --cache-dir "$HOME/.potato-cannon/pnpm-cache"
       pnpm build

   The filter is what keeps the desktop app out. It is the only part of
   the Cannon that depends on Electron, and installing it downloads a
   hundred megabytes of browser you would never run: the board is a web
   page the daemon serves, and this file never builds the desktop app.
   `pnpm build` builds the three the board needs and no more, so the
   filter matches what is built.

   The four exports are there so that nothing this step downloads lands
   outside `~/.potato-cannon`. Without them corepack writes to
   `~/.cache/node`, pnpm to `~/Library/pnpm`, and `prebuild-install` to
   `~/.npm`, which is about a gigabyte in three places this file never
   told you about and Undo does not remove.

   Receipt: `git -C ~/.potato-cannon/app rev-parse HEAD` prints
   `cb39b5b88a5cb4cb38eaae99e6ba38bb3e070a06`, the commit named above,
   character for character, and `pnpm build` ended with no error. The full
   SHA rather than the short one, because the receipt's whole job is to say
   the clone is at the commit this file pinned, and a seven-character
   comparison is a weaker claim than the one being made.

8. The daemon. Run the script this repository ships:

       bash scripts/write-launch-agent.sh

   It writes `~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist` and
   nothing else, checks it with `plutil -lint` before installing it, loads
   it with `launchctl bootstrap`, and prints the health line. Read it
   first; it is short, and its header says why the daemon is run directly
   rather than through the Cannon's own start command, which passes
   `--daemon`, detaches and exits so that nothing can supervise it.

   This used to be a plist printed here for you to copy, and it could not
   be copied: the daemon's command is one long shell line, a plist typeset
   to fit a page breaks it across nine lines, and a `<string>` keeps every
   newline it is given. What landed on disk was a command with newlines in
   the middle of it and a daemon that never started. Nothing in this file
   is now typeset in a way that changes what it means.

   **If it refuses because something already listens on 3131, stop.** Another
   Cannon is running, and it is not yours: everything after this step would be
   judged against somebody else's board. The script prints which process holds
   the port and which user owns it. Stop that daemon, or log in as that user
   and stop it there, before running this again. Nothing was written.

   Receipt, all three: `curl -s http://127.0.0.1:3131/health` returns a
   response whose status is ok; the listener the script prints is a `node`
   process owned by the user you are logged in as; and the count of
   `EADDRINUSE` lines in `~/.potato-cannon/daemon.log` is 0.

   The health line alone is not a receipt. It says a daemon is there, not that
   it is the one you just built. On the sixth cold run a previous test user's
   daemon was still holding the port: `/health` answered ok, with nine and a
   half hours of uptime on a daemon installed minutes earlier. The other two
   lines are what tell those apart.

9. Register the project. The daemon can only name a template that lives in
   its own templates folder, so copy this project's template there first,
   then register:

       export PATH="$HOME/.potato-cannon/node/bin:$PATH"
       mkdir -p ~/.potato-cannon/templates
       cp -R ~/bang/cannon-template ~/.potato-cannon/templates/bang
       curl -s -X POST http://127.0.0.1:3131/api/projects \
         -H 'Content-Type: application/json' \
         -d "{\"path\":\"$HOME/bang\",\"displayName\":\"bang\",\"template\":\"bang\"}"

   The template's columns are Ideas, Spec, Build, Gate, Review and Done.
   Ideas and Done are added by the Cannon; the other four come from the
   template. Receipt: `curl -s http://127.0.0.1:3131/api/projects` lists
   one project named bang.

10. First cards. Create these three in the Ideas column, in this order and
    no others. Each is created with `POST /api/tickets/<project id>` and a
    title and a description; the project id came back from step 9. A
    description is the text under its title exactly as written here,
    newlines and all, with the four spaces of indentation removed and
    nothing added.

    Title: Lend and return in the browser

    Drag this card to Spec and watch what happens.
    As the owner, I want to lend, see what is out, and mark things returned on a screen in my browser, so I am not tied to the command line. The screens are in design/. Read design/README.md first.
    Every write the screens make goes through the engine (NFR-ENG-10); the test will refuse anything else.
    ids: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30

    Title: What I have lent before

    As the owner, when I lend something I want to see what I have lent that person before and whether it came back, so I can decide with the history in front of me.
    ids: US-UI-20, AC-UI-40

    Title: Remind the borrower

    As the owner, I want the app to nudge me about a thing that has been out too long.

    Nothing in `PRD.md` promises this yet. It is here to show what the board does with a card whose promise does not exist: it waits, and it says why.

    These are the same three, in the same words, as `~/bang/FIRST-CARDS.md`,
    which says why they are these three. Either file is the payload, and
    this project's own tests compare them, so they cannot drift apart
    without something going red.

    Receipt: the card ids, one per line.

11. Open the board. Print `http://127.0.0.1:3131`, then print, on its own,
    the line `Bang done. Your board is open.`, and only then open the URL
    in the default browser. The done line goes before the open command so
    that it is the last thing written to the terminal: opening the browser
    takes the reader's attention away, and a line printed after it is a
    line nobody reads. Receipt: the URL and the done line.

## What done looks like

A browser tab showing the Potato Cannon board for the project bang, with
the first cards in Ideas and nothing in any other column. In the terminal,
eleven receipts and the done line. From here the page hands you to First
Light: the first card, dragged through.

## Undo, in full

Run these in order to remove everything this file did.

    launchctl bootout gui/$(id -u)/com.dryfoos.bang.cannon
    rm ~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist
    UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools" uv tool uninstall specify-cli
    rm ~/.local/bin/specify
    rm -rf ~/.potato-cannon
    rm -rf ~/bang

The uninstall carries `UV_TOOL_DIR` because the install did: uv keeps its
tools where that variable points, and a call without it looks in
`~/.local/share/uv`, finds nothing, and says so. It goes before the
`rm -rf ~/.potato-cannon` for the same reason: afterwards there is nothing
left for it to uninstall. `specify` is removed by name because
`UV_TOOL_BIN_DIR` put it in `~/.local/bin`, which holds things this file
did not install.

**Remove uv itself only if this file installed it**, which step 2's receipt
told you: it listed `uv` as missing. If step 2 said uv was present, it is
yours and predates this project, and these two lines are not yours to run:

    rm ~/.local/bin/uv ~/.local/bin/uvx

Node, if this file installed it, is under `~/.potato-cannon/node` and goes
with `rm -rf ~/.potato-cannon`, along with every package cache the build
filled. Your
own Node, if you had one, is untouched: this file never put anything on the
path outside the terminal it was working in. The session
transcripts under `~/.claude/projects/` are Claude Code's, not Bang's, and
are left alone; the folders whose names begin with your home path and
`-bang` are the ones this project produced, and deleting them loses
nothing but the transcripts. Claude Code itself was installed by the
page's first block, not by this file, and stays.
