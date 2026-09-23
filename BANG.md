# BANG.md

This file is what your Claude Code session is told to carry out when you
paste block 3 in README.md. Read it before you paste. The agent reads the
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
   into /usr or /opt. If Node is missing it also goes under `~/.local`.
3. `~/.potato-cannon/`  Potato Cannon's own home: the built application
   under `app/`, its settings file, its database, the registration of
   ~/bang as a project, and a copy of the workflow template it runs.
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
how a card moves from Spec to Build to Gate to Align without you
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
   `estate/cannon`, commit `5a5404c`, and the npm packages its build needs,
   fetched by pnpm from the public npm registry.
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
- Push anything anywhere. There is no remote; the project's promotions are
  local merges into its own main branch.
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
   `specify`, `node`, `pnpm`, `claude`. For each that is missing, say so.
   Do not install anything in this step. Receipt: five lines, present or
   missing.

3. Install uv if missing, into `~/.local/bin`, with the installer named
   above. Then `uv tool install specify-cli`. Receipt: `specify --version`
   prints a version at or above 0.14.0.

4. Node and pnpm. **Node 22, not the current LTS.** The Cannon's database
   library has no prebuilt binary for newer Node and building it from
   source fails, so a newer Node will get you through this step and stop
   you at step 7. If `node --version` already starts with `v22.`, skip to
   pnpm. Otherwise, no administrator password needed:

       mkdir -p ~/.local ~/.potato-cannon
       curl -fsSL -o ~/.potato-cannon/node22.tar.xz \
         https://nodejs.org/dist/v22.23.2/node-v22.23.2-darwin-arm64.tar.xz
       tar -xJf ~/.potato-cannon/node22.tar.xz -C ~/.local --strip-components=1
       rm ~/.potato-cannon/node22.tar.xz
       export PATH="$HOME/.local/bin:$PATH"

   On an Intel Mac, use `node-v22.23.2-darwin-x64.tar.xz` instead. Then
   enable pnpm through Node's own corepack:

       corepack enable pnpm

   `~/.potato-cannon` may not exist yet at this step, so the first line
   creates it. The tarball is downloaded there rather than to `/tmp` so
   that every byte this file writes is inside one of the five places
   listed above, and it is deleted as soon as it is unpacked.

   Receipt: `node --version` prints a version beginning `v22.`, and
   `pnpm --version` prints a version. Add `export PATH="$HOME/.local/bin:$PATH"`
   to your shell profile if you want these on the path in new terminals.

5. Spec Kit on this project. The flag that names Claude Code is
   `--integration`, and the current release is Spec Kit 1.0.4. Initialise
   into this folder, which already has files in it:

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

   Receipt: `.specify/` exists, `ls .specify/` is printed, and
   `head -1 .specify/memory/constitution.md` prints
   `# Constitution: Who Has My Stuff`.

6. SpecAssay. Add the three SpecAssay catalogs and install the bundle,
   exactly as the SpecAssay README's catalog path gives them. If the Gate
   config file is reported MISSING, copy it from the template as the
   README says. Then put this project's own settings in place of the
   installed defaults:

       cp cannon-template/specassay-check-config.yml \
          .specify/extensions/specassay-check/specassay-check-config.yml

   The installed file has two settings this project needs and ships
   commented out: `parent_derivation`, which is what makes the
   specification a tree rather than a flat list, and `test_results`,
   which is what makes a passing test count as proof rather than a test
   whose name merely matches. Receipt: the first two lines of
   `bash .specify/extensions/specassay-check/scripts/check-traceability.sh`,
   which name the config file it found, and
   `grep ^parent_derivation .specify/extensions/specassay-check/specassay-check-config.yml`
   printing `parent_derivation: heading-nesting`.

7. Potato Cannon. Clone the fork into `~/.potato-cannon/app` at the
   branch and commit above; `pnpm install`; `pnpm build`. Do not build the
   desktop app. Receipt: `git -C ~/.potato-cannon/app rev-parse --short
   HEAD` prints 5a5404c and `pnpm build` ended with no error.

8. The daemon. Write `~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist`
   so that it runs the built daemon directly, in the foreground, with a
   named environment and nothing else in it. The Cannon's own start command
   passes `--daemon`, which detaches and exits, and nothing can then
   supervise it, so the server is run directly instead:

       <?xml version="1.0" encoding="UTF-8"?>
       <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
         "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
       <plist version="1.0">
       <dict>
         <key>Label</key><string>com.dryfoos.bang.cannon</string>
         <key>ProgramArguments</key>
         <array>
           <string>/bin/bash</string><string>-lc</string>
           <string>cd "$HOME/.potato-cannon/app" &amp;&amp; exec env -i
             HOME="$HOME" USER="$USER" LOGNAME="$USER" SHELL="$SHELL"
             TMPDIR="${TMPDIR:-/tmp}" LANG="en_US.UTF-8"
             PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
             GIT_AUTHOR_NAME="Bang Worker"
             GIT_AUTHOR_EMAIL="bang-worker@localhost"
             GIT_COMMITTER_NAME="Bang Worker"
             GIT_COMMITTER_EMAIL="bang-worker@localhost"
             POTATO_DAEMON_HOST="127.0.0.1" POTATO_DAEMON_PORT="3131"
             node ./apps/daemon/dist/server/server.js</string>
         </array>
         <key>RunAtLoad</key><true/>
         <key>KeepAlive</key><true/>
         <key>ThrottleInterval</key><integer>30</integer>
         <key>StandardOutPath</key>
         <string>/Users/you/.potato-cannon/daemon.log</string>
         <key>StandardErrorPath</key>
         <string>/Users/you/.potato-cannon/daemon.log</string>
       </dict>
       </plist>

   Those last two paths are shown with `/Users/you` because a plist does
   not expand `~` or `$HOME` in them: the agent reads your home folder
   with `echo "$HOME"` and writes the real path into the file, so what
   lands on disk names your own home and not a placeholder. Everywhere
   else in the plist `$HOME` is inside a shell command, where it is
   expanded when the daemon starts. The host and port are set by
   `POTATO_DAEMON_HOST` and `POTATO_DAEMON_PORT`, not by command-line
   flags. Load it with
   `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist`.
   Receipt: `curl -s http://127.0.0.1:3131/health` returns a response
   whose status is ok.

9. Register the project. The daemon can only name a template that lives in
   its own templates folder, so copy this project's template there first,
   then register:

       mkdir -p ~/.potato-cannon/templates
       cp -R ~/bang/cannon-template ~/.potato-cannon/templates/bang
       curl -s -X POST http://127.0.0.1:3131/api/projects \
         -H 'Content-Type: application/json' \
         -d "{\"path\":\"$HOME/bang\",\"displayName\":\"bang\",\"template\":\"bang\"}"

   The template's columns are Ideas, Spec, Build, Gate, Align and Done.
   Ideas and Done are added by the Cannon; the other four come from the
   template. Receipt: `curl -s http://127.0.0.1:3131/api/projects` lists
   one project named bang.

10. First cards. Create the cards named in `~/bang/FIRST-CARDS.md` in the
    Ideas column, in that order, with those descriptions, and no others.
    Each card is created with `POST /api/tickets/<project id>` and a title
    and description; the project id came back from step 9. Receipt: the
    card ids, one per line.

11. Open the board. Print `http://127.0.0.1:3131` and open it in the
    default browser. Receipt: the URL.

Then print, on its own, the line: `Bang done. Your board is open.`

## What done looks like

A browser tab showing the Potato Cannon board for the project bang, with
the first cards in Ideas and nothing in any other column. In the terminal,
eleven receipts and the done line. From here the page hands you to First
Light: the first card, dragged through.

## Undo, in full

Run these in order to remove everything this file did.

    launchctl bootout gui/$(id -u)/com.dryfoos.bang.cannon
    rm ~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist
    rm -rf ~/.potato-cannon
    rm -rf ~/bang
    uv tool uninstall specify-cli
    rm ~/.local/bin/uv ~/.local/bin/uvx

Node, if this file installed it, is under `~/.local` and can be removed by
deleting `~/.local/bin/node`, `~/.local/bin/npm`, `~/.local/bin/npx`,
`~/.local/bin/corepack` and `~/.local/lib/node_modules`. The session
transcripts under `~/.claude/projects/` are Claude Code's, not Bang's, and
are left alone; the folders whose names begin with your home path and
`-bang` are the ones this project produced, and deleting them loses
nothing but the transcripts. Claude Code itself was installed by the
page's first block, not by this file, and stays.
