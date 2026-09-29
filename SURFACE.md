# SURFACE.md: Bang

The declared surface. What this project and the machinery around it expose, and which
of its controls hold by construction rather than by anyone's discipline. Observed but
undeclared is a finding. A control that is local by construction is named here, never
relied on quietly.

Written 2026-09-19, at the project's birth, before any card ran.

## Local controls {#local}

| Row | What | Declaration |
|-----|------|-------------|
| LC1 | The reader's answers | The filled CASE lives at `BANG_CASE_FILE`, outside the worktree, where no git command run inside this repository can reach it. That part holds by construction. The second control, `scripts/no-private-answers.py`, refuses a commit carrying a value out of the answers, and it is a hook rather than a Gate: no CI job can run it, because CI would have to hold the answers in order to look for them. `--no-verify` beats it. See `scripts/README.md`. |
| LC4 | The buddy | One agent a reviewer can address from a card in Review, reading `cannon-template/agents/ticket-qa.md`. In Review it has a pen: `Edit`, `Write` and `Bash` on the card's worktree, so it can make delivery changes on the card's branch, each with its own commit, test run and Gate run. It never touches `PRD.md`, `CASE.md`, `CONSTITUTION.md`, `SURFACE.md` or `scripts/`, never writes a promise (a change to what an AC, FR, US or NFR says is named and handed to a person), and never moves the card. Outside Review it has no pen. The fence is its instructions and the Gate's governed list, not a wall: `Bash` is `Bash`. **The buddy can read anything on this machine that the operator can.** Its read tools take absolute paths and Claude Code has no directory jail, so the worktree is where it starts rather than a boundary it cannot cross. Its instructions tell it not to go looking; nothing stops it. What it reads can appear in a card's chat and in the Cannon's session logs, both on this machine. |
| LC3 | The way onto main | A change reaches `main` by one route: a card's branch, merged by the promotion the template names, with the Gate passing on the merge commit. `scripts/no-commit-on-main.py` refuses any commit on `main` unless `BANG_PROMOTION=1` is set, which the promotion sets and nothing else should. Like LC1 this is a hook rather than a Gate, and `--no-verify` beats it; unlike LC1 it could be checked by a forge. Constitution IV states the rule this enforces. A commit made in GitHub's web editor never passes through a clone and so never meets this hook; the first governed-document edit on `main` (SURFACE.md row L1, 2026-09-29) landed that way. A branch rule on the forge is what would close that, and none is set.|
| LC2 | The Gate receipt | The Gate ran on this SHA on the machine that built it. No second party attested the receipt. `scripts/gate.conf` declares `RECEIPT_SOURCE="local"`, so `scripts/gate.sh` writes a `gate-receipt` record into the journal when it runs on `main`, and the Done entry check reads that record for the merge commit's SHA. An project with a forge behind it declares `forge` instead and the check reads a CI run, which a second party produced. What local costs is independence, not rigor: the same Gate ran on the same commit. |

## Listeners {#listeners}

| Row | What | Bound |
|-----|------|-------|
| L1 | The lending tracker | none yet. The command line is the only door: src/whms/ has cli.py, store.py, records.py and outstanding.py, and none of them binds a port. The web app that will listen is T904's unbuilt work. When it lands, this row becomes one TCP listener on 127.0.0.1 only, on the port given at start. |

## Egress {#egress}

| Row | What | Destinations |
|-----|------|--------------|
| E1 | This repository | github.com/rdryfoos/bang, since 2026-09-25. The rehearsal ran with no remote; the remote exists because the onboarding page has people clone this repository. What holds now is that `main` moves only by a merge Rik performs by hand, and this row claims no branch rule on GitHub behind that.|
| E2 | Cannon workers during Build | the Anthropic API through the claude CLI, and package registries as Build requires. Declared so the project has a comparison target. The reader's answers are not among the things a worker is given. |
