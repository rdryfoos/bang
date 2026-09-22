#!/usr/bin/env python3
"""done-check: the Cannon's entry check for Done. Exits zero only when the card's pull
request merged into the default branch and every check run at the merge commit
completed green; any other exit refuses the move, and the last lines printed are the
reason the operator sees.

Done means two things are true: the card's change is on the default branch, and the Gate
passed on that exact commit. A pull request merged with CI green is one way those facts
get produced and recorded; a local merge followed by a local Gate run that writes a
receipt for the merge SHA is another. The project declares which it uses.

Usage, as the template's entryChecks.Done.command:
    done-check.py [--receipts forge|local] [--repo OWNER/NAME] [--default-branch BRANCH]
                  [--journal PREFIX] [--daemon URL]

The Cannon runs it in the project's path with POTATO_PROJECT_ID and POTATO_TICKET_ID in
the environment. It reads the card from the daemon over loopback, takes the pull request
number from the card's pr: line as digits only, so no card text reaches a command line,
and calls gh for exactly two reads: pr view on that pull request, and the check-runs
endpoint at its merge commit. It writes nothing.

Without --repo and --default-branch it reads both from the project checkout's git
(remote get-url origin, symbolic-ref of origin's HEAD), read only. An project whose
declared surface does not name those reads passes both flags.

With --receipts local it reads no forge at all. It asks git whether the card's branch is
an ancestor of the default branch, finds the commit that brought it in, and looks in the
project's journal for a gate-receipt record carrying that SHA. What that costs is
independence, not rigor: the same Gate ran on the same commit, but the machine that built
the change is the only party that attested it, which the project's SURFACE says out loud.

Exit codes: 0 allowed; 1 refused, a fact does not hold; 2 refused, a fact could not be
checked. Specification: the source project's decision 0062 and SURFACE.md rows E4 and M6.
Written by the born-threaded practice; MIT."""
import argparse, json, os, re, subprocess, sys, urllib.parse, urllib.request

GREEN = {"success", "skipped", "neutral"}
PR_LINE = re.compile(r"^pr:\s*(?:\S*/pull/)?#?(\d+)\s*$")


class Refused(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def unverifiable(message):
    return Refused(2, message)


def run(argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode != 0:
        last = ((r.stderr or r.stdout).strip().splitlines() or ["no output"])[-1]
        raise unverifiable(f"{argv[0]} {argv[1]} failed: {last}")
    return r.stdout


def daemon_url(arg):
    if arg:
        return arg.rstrip("/")
    host = os.environ.get("POTATO_DAEMON_HOST") or "127.0.0.1"
    port = os.environ.get("POTATO_DAEMON_PORT")
    if not port:
        raise unverifiable("no daemon address: pass --daemon or run under the Cannon")
    return f"http://{host}:{port}"


def card_description(daemon, project, ticket):
    url = f"{daemon}/api/tickets/{urllib.parse.quote(project, safe='')}/{urllib.parse.quote(ticket, safe='')}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return (json.loads(r.read().decode() or "null") or {}).get("description") or ""
    except Exception as e:
        raise unverifiable(f"could not read card {ticket} from the daemon ({e.__class__.__name__})")


def pr_number(description, ticket):
    numbers = [m.group(1) for m in (PR_LINE.match(l.strip()) for l in description.splitlines()) if m]
    if not numbers:
        raise Refused(1, f"card {ticket} has no pr: line naming a pull request")
    if len(set(numbers)) > 1:
        raise Refused(1, f"card {ticket} has more than one pr: line ({', '.join(numbers)})")
    return numbers[0]


def repo_and_branch(args):
    repo, branch = args.repo, args.default_branch
    if not repo:
        url = run(["git", "remote", "get-url", "origin"]).strip()
        m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
        if not m:
            raise unverifiable("could not tell the repository from the project's origin remote")
        repo = m.group(1)
    if not branch:
        ref = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"]).strip()
        branch = ref.split("/", 1)[1] if "/" in ref else ref
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise unverifiable(f"repository name is not OWNER/NAME: {repo!r}")
    return repo, branch



def git_out(argv):
    r = subprocess.run(["git"] + argv, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def card_branch(description, ticket, daemon, project):  # noqa: ARG001
    """The branch the card's work is on: the card's own branch: line when it has one,
    otherwise the project's branch prefix and the ticket id, which is what the Cannon
    names a worktree's branch."""
    for line in description.splitlines():
        m = re.match(r"^branch:\s*(\S+)\s*$", line.strip())
        if m:
            return m.group(1)
    # The daemon's project list does not carry branchPrefix and there is no
    # single-project endpoint, so the prefix cannot be read from the Cannon. The project
    # states it, and "potato" is the daemon's own default from worktree.ts.
    prefix = (os.environ.get("BRANCH_PREFIX") or "").strip() or "potato"
    return f"{prefix}/{ticket}"


def merge_commit_on(branch, default):
    """The commit on the default branch that brought the branch in. For a merge by hand
    that is the merge commit; for a fast-forward it is the branch's own tip."""
    path = git_out(["rev-list", "--reverse", "--ancestry-path", f"{branch}..{default}"])
    if path:
        return path.splitlines()[0]
    return git_out(["rev-parse", f"{branch}^{{commit}}"])


def receipt_for(prefix, sha):
    """The last gate-receipt record in the journal carrying this SHA."""
    d = os.path.join(os.getcwd(), prefix)
    if not os.path.isdir(d):
        raise unverifiable(f"no journal at {prefix}/; this project cannot show a local receipt")
    found = None
    for name in sorted(os.listdir(d)):
        if not name.endswith(".jsonl"):
            continue
        try:
            with open(os.path.join(d, name), encoding="utf-8", errors="ignore") as f:
                for raw in f:
                    try:
                        rec = json.loads(raw)
                    except Exception:
                        continue
                    if rec.get("kind") == "gate-receipt" and rec.get("sha") == sha:
                        found = rec
        except OSError:
            continue
    return found


def check_local(args, ticket, project, daemon):
    default = args.default_branch or "main"
    description = card_description(daemon, project, ticket)
    branch = card_branch(description, ticket, daemon, project)
    if git_out(["rev-parse", "--verify", f"{branch}^{{commit}}"]) is None:
        raise Refused(1, f"card {ticket} names branch {branch}, which this checkout does not have")
    if git_out(["rev-parse", "--verify", f"{default}^{{commit}}"]) is None:
        raise unverifiable(f"this checkout has no branch {default}")
    merged = subprocess.run(["git", "merge-base", "--is-ancestor", branch, default]).returncode == 0
    if not merged:
        raise Refused(1, f"{branch} is not on {default} yet; the merge is a hand's, and it has not happened")
    sha = merge_commit_on(branch, default)
    if not sha or not re.fullmatch(r"[0-9a-f]{40}", sha or ""):
        raise unverifiable(f"could not tell which commit on {default} brought {branch} in")
    rec = receipt_for(args.journal, sha)
    if rec is None:
        raise Refused(1, f"no Gate receipt for {sha[:7]} on {default}; run the gate script there first")
    if rec.get("result") != "pass":
        raise Refused(1, f"the Gate receipt for {sha[:7]} says {rec.get('result')}, exit {rec.get('gate_exit')}")
    return (f"{branch} is on {default} at {sha[:7]}, and the Gate passed there at {rec.get('time')}; "
            "receipt written locally, no second party attested it")

def check(args):
    project = os.environ.get("POTATO_PROJECT_ID")
    ticket = os.environ.get("POTATO_TICKET_ID")
    if not project or not ticket:
        raise unverifiable("POTATO_PROJECT_ID and POTATO_TICKET_ID are not set; this runs as a Cannon entry check")
    if args.receipts == "local":
        return check_local(args, ticket, project, daemon_url(args.daemon))
    number = pr_number(card_description(daemon_url(args.daemon), project, ticket), ticket)
    repo, branch = repo_and_branch(args)

    pr = json.loads(run(["gh", "pr", "view", number, "--repo", repo, "--json", "state,baseRefName,mergeCommit"]))
    if pr.get("state") != "MERGED":
        raise Refused(1, f"pull request #{number} is {str(pr.get('state', 'unknown')).lower()}, not merged")
    if pr.get("baseRefName") != branch:
        raise Refused(1, f"pull request #{number} merged into {pr.get('baseRefName')}, not {branch}")
    sha = (pr.get("mergeCommit") or {}).get("oid") or ""
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise unverifiable(f"pull request #{number} reports no merge commit")

    runs = json.loads(run(["gh", "api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100",
                           "--jq", "[.check_runs[] | {name, status, conclusion}]"]))
    if not runs:
        raise Refused(1, f"no check run at merge commit {sha[:7]}; CI has not reported")
    running = [r["name"] for r in runs if r.get("status") != "completed"]
    if running:
        raise Refused(1, f"{len(running)} check(s) still running at {sha[:7]}: {', '.join(running)}; "
                         "try again when CI finishes")
    red = [f"{r['name']} ({r.get('conclusion')})" for r in runs if r.get("conclusion") not in GREEN]
    if red:
        raise Refused(1, f"CI not green at {sha[:7]}: {', '.join(red)}")
    return f"pull request #{number} merged into {branch} at {sha[:7]}; all {len(runs)} check(s) green"


def main():
    p = argparse.ArgumentParser(description="The Cannon's entry check for Done.")
    p.add_argument("--receipts", choices=("forge", "local"), default="forge",
                   help="where the proof that the Gate passed lives: a CI run at the host, "
                        "or a receipt this project wrote itself. Default forge.")
    p.add_argument("--journal", default="journal", help="the project's journal prefix, for --receipts local")
    p.add_argument("--repo", help="OWNER/NAME; read from the project's origin remote if omitted")
    p.add_argument("--default-branch", help="read from origin's HEAD in the project checkout if omitted")
    p.add_argument("--daemon", help="daemon URL; built from POTATO_DAEMON_HOST and POTATO_DAEMON_PORT if omitted")
    args = p.parse_args()
    try:
        print(f"done-check: {check(args)}")
        return 0
    except Refused as r:
        print(f"done-check: {r}", file=sys.stderr)
        return r.code


if __name__ == "__main__":
    sys.exit(main())
