#!/usr/bin/env python3
"""Entry checks for the columns before Done, in the same shape as the Done check.

Until 2026-09-20 only Done had a check. Every other column advanced on an exit code, so
an agent that did nothing, said so plainly and exited zero looked exactly like an agent
that had done the work: on the run that found this, the Spec agent wrote nothing, said
why, exited 0, and the card was in Build five seconds later.

Two checks, deliberately minimal. The full version, every column, comes after the demo.

  --spec-names-ids   Spec to Build: a spec file exists on the card's branch and names
                     every ID the card cites.
  --has-commits      Build to Gate: the card's branch carries at least one commit
                     written since the card entered Build.
  --ids-delivered    Align to Done: every ID the card cites reads proven or
                     tracked-debt in the branch's trace-manifest. An ID still at
                     backlog or at GAP means the card is claiming a promise it did not
                     deliver, and the board would say Done over it.

Both read the card from the daemon over loopback and ask git about the card's branch.
They write nothing. Exit 0 allowed, 1 refused a fact does not hold, 2 refused a fact
could not be checked. Written by the born-threaded practice; MIT.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

ID = re.compile(r"\b(?:US|FR|AC|NFR)-[A-Z]+-\d+\b")


class Refused(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def git(argv):
    r = subprocess.run(["git"] + argv, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def conf(name, default):
    try:
        for line in open("scripts/gate.conf"):
            m = re.match(rf'^\s*{name}="?([^"#]*)"?', line.strip())
            if m and m.group(1).strip():
                return m.group(1).strip()
    except OSError:
        pass
    return default


def card(project, ticket):
    host = os.environ.get("POTATO_DAEMON_HOST") or "127.0.0.1"
    port = os.environ.get("POTATO_DAEMON_PORT") or "3131"
    url = (f"http://{host}:{port}/api/tickets/{urllib.parse.quote(project, safe='')}"
           f"/{urllib.parse.quote(ticket, safe='')}")
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read().decode() or "null") or {}
    except Exception as e:
        raise Refused(2, f"could not read card {ticket} from the daemon ({e.__class__.__name__})")


def branch_of(description, ticket):
    for line in description.splitlines():
        if line.strip().startswith("branch:"):
            name = line.split(":", 1)[1].strip()
            if name:
                return name
    return f"{conf('BRANCH_PREFIX', 'potato')}/{ticket}"


def ids_of(description, ticket):
    for line in description.splitlines():
        if line.strip().lower().startswith("ids:"):
            found = ID.findall(line)
            if found:
                return found
    raise Refused(1, f"card {ticket} has no ids: line naming what it carries")


def require_branch(branch, ticket):
    if git(["rev-parse", "--verify", "--quiet", f"{branch}^{{commit}}"]) is None:
        raise Refused(1, f"card {ticket} has no branch {branch} yet")


def spec_names_ids(ticket, description):
    branch = branch_of(description, ticket)
    require_branch(branch, ticket)
    ids = ids_of(description, ticket)

    listing = git(["ls-tree", "-r", "--name-only", branch]) or ""
    specs = [p for p in listing.splitlines()
             if p.startswith("specs/") and os.path.basename(p) == "spec.md"]
    if not specs:
        raise Refused(1, f"no specs/**/spec.md on {branch}; nothing was elaborated")

    text = "\n".join(git(["show", f"{branch}:{p}"]) or "" for p in specs)
    missing = [i for i in ids if i not in text]
    if missing:
        raise Refused(1, f"the spec on {branch} does not name {len(missing)} of the card's "
                         f"{len(ids)} IDs: {', '.join(missing)}")
    return f"{len(specs)} spec file(s) on {branch} name all {len(ids)} of the card's IDs"


BUILD_ENTRY = re.compile(r"Build entered from .*?\bbranch at ([0-9a-f]{7,40})\.")


def build_entry_head(description):
    """Where the branch stood when this card last entered Build.

    column-entry.sh writes it onto the status line at the moment of entry. The most
    recent one wins: a card can enter Build several times, and the question is always
    about the attempt that just finished.
    """
    found = BUILD_ENTRY.findall(description or "")
    return found[-1] if found else None


def has_commits(ticket, description):
    """Did this Build attempt produce anything?

    It used to count commits the branch has that main does not, which answers a
    different question. A card that entered Build, built nothing and exited 0 still
    had the Spec commit ahead of main, so the check passed and the card sailed to
    Gate and then to Align with no code on it. BANV-4 did exactly that twice on
    2026-09-21, and the board was green both times.

    So the base is where the branch stood when Build was entered, not main. A Build
    that wrote nothing is refused at the Gate door, which is where somebody is
    looking.

    With no recorded entry point, it falls back to the old comparison and says so,
    rather than refusing a card over a status line an older Cannon never wrote.
    """
    branch = branch_of(description, ticket)
    require_branch(branch, ticket)
    default = conf("DEFAULT_BRANCH", "main")

    since = build_entry_head(description)
    if since is None:
        base = git(["merge-base", branch, default])
        if base is None:
            raise Refused(2, f"{branch} and {default} share no history")
        count = git(["rev-list", "--count", f"{base}..{branch}"])
        if count is None:
            raise Refused(2, f"could not count commits on {branch}")
        if int(count) < 1:
            raise Refused(1, f"{branch} carries no commit that {default} does not; nothing was built")
        return (f"{branch} carries {count} commit(s) that {default} does not "
                f"(no Build entry point on the card; counted against {default})")

    if git(["rev-parse", "--verify", "--quiet", f"{since}^{{commit}}"]) is None:
        raise Refused(2, f"the card says Build began at {since} and this repository has no such commit")

    count = git(["rev-list", "--count", f"{since}..{branch}"])
    if count is None:
        raise Refused(2, f"could not count commits on {branch} since {since}")
    if int(count) < 1:
        raise Refused(1, f"{branch} is where it was when Build began, at {since}: this attempt "
                         f"wrote nothing. A card does not reach the Gate on work it did not do.")
    return f"{branch} carries {count} commit(s) written since Build began at {since}"


def ids_delivered(ticket, description):
    """Every ID the card cites has to have arrived somewhere real.

    Added 2026-09-20, from a card that reached Done with its acceptance criterion
    proven and the promise that criterion serves still reading backlog. The Gate did
    not object, and could not: its silent-gap rule is about acceptance criteria, which
    are the atomic proof unit, so an unproven promise reds nothing. Nobody noticed
    until the thread was looked at in the viewer.

    proven and tracked-debt both pass. Debt is a state a card may honestly ship in, as
    long as it is declared. backlog and GAP do not: backlog means nothing carries it,
    and GAP means something should and does not.
    """
    branch = branch_of(description, ticket)
    require_branch(branch, ticket)
    ids = ids_of(description, ticket)

    worktree = os.path.join(".potato", "worktrees", ticket)
    manifest = os.path.join(worktree, "trace-manifest.json")
    if not os.path.isfile(manifest):
        raise Refused(2, f"no trace-manifest at {manifest}; the Gate has not run on {branch}")
    try:
        with open(manifest, encoding="utf-8") as f:
            rows = (json.load(f) or {}).get("rows") or []
    except (OSError, ValueError) as e:
        raise Refused(2, f"could not read {manifest} ({e.__class__.__name__})")

    state = {r.get("id"): r.get("status") for r in rows}
    missing = [i for i in ids if i not in state]
    if missing:
        raise Refused(1, f"the manifest on {branch} does not carry {', '.join(missing)}")

    undelivered = [(i, state[i]) for i in ids if state[i] not in ("proven", "tracked-debt")]
    if undelivered:
        named = ", ".join(f"{i} is {st}" for i, st in undelivered)
        raise Refused(1, f"the card claims {len(ids)} ID(s) and {len(undelivered)} did not "
                         f"arrive: {named}. A card does not reach Done over a promise it "
                         f"did not deliver.")
    return (f"all {len(ids)} of the card's IDs arrived: "
            + ", ".join(f"{i} {state[i]}" for i in ids))


def main():
    p = argparse.ArgumentParser(description="Entry checks for the columns before Done.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--spec-names-ids", action="store_true")
    g.add_argument("--has-commits", action="store_true")
    g.add_argument("--ids-delivered", action="store_true")
    args = p.parse_args()

    project = os.environ.get("POTATO_PROJECT_ID")
    ticket = os.environ.get("POTATO_TICKET_ID")
    try:
        if not project or not ticket:
            raise Refused(2, "POTATO_PROJECT_ID and POTATO_TICKET_ID are not set; this runs "
                             "as a Cannon entry check")
        description = card(project, ticket).get("description") or ""
        if args.spec_names_ids:
            result = spec_names_ids(ticket, description)
        elif args.has_commits:
            result = has_commits(ticket, description)
        else:
            result = ids_delivered(ticket, description)
        print(f"column-check: {result}")
        return 0
    except Refused as r:
        print(f"column-check: {r}", file=sys.stderr)
        return r.code


if __name__ == "__main__":
    sys.exit(main())
