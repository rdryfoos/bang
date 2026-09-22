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
| LC4 | The buddy | An ad-hoc agent a reviewer can start from a card under review, reading `scripts/buddy.md`. It cannot write and cannot reach the network: `Edit`, `Write`, `NotebookEdit`, `Bash`, `WebFetch` and `WebSearch` are refused to it, and it is given `Read`, `Grep` and `Glob`. **The buddy can read anything on this machine that the operator can.** Its read tools take absolute paths and Claude Code has no directory jail, so the worktree is where it starts rather than a boundary it cannot cross. `scripts/buddy.md` tells it not to go looking; nothing stops it. What it reads can appear in a card's chat and in the Cannon's session logs, both on this machine. |
| LC3 | The way onto main | A change reaches `main` by one route: a card's branch, merged by the promotion the template names, with the Gate passing on the merge commit. `scripts/no-commit-on-main.py` refuses any commit on `main` unless `ESTATE_PROMOTION=1` is set, which the promotion sets and nothing else should. Like LC1 this is a hook rather than a Gate, and `--no-verify` beats it; unlike LC1 it could be checked by a forge, and this project has none. Constitution IV states the rule this enforces. |
| LC2 | The Gate receipt | The Gate ran on this SHA on the machine that built it. No second party attested the receipt. `scripts/gate.conf` declares `RECEIPT_SOURCE="local"`, so `scripts/gate.sh` writes a `gate-receipt` record into the journal when it runs on `main`, and the Done entry check reads that record for the merge commit's SHA. An project with a forge behind it declares `forge` instead and the check reads a CI run, which a second party produced. What local costs is independence, not rigor: the same Gate ran on the same commit. |

## Listeners {#listeners}

| Row | What | Bound |
|-----|------|-------|
| L1 | The lending tracker | none yet. The application does not exist at the time of writing, and `AC-PRIV-20` requires that it make no outbound network request at all. |

## Egress {#egress}

| Row | What | Destinations |
|-----|------|--------------|
| E1 | This repository | none. No git remote exists, for the duration of the rehearsal. `git remote -v` prints nothing, which is a stronger control than a script at the push. |
| E2 | Cannon workers during Build | the Anthropic API through the claude CLI, and package registries as Build requires. Declared so the project has a comparison target. The reader's answers are not among the things a worker is given. |
