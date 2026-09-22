#!/usr/bin/env python3
"""The two things the promotion hook needs from the daemon: which branch a card's
work is on, and a way to leave a mark on the card when a promotion fails.

Every value arrives in the environment rather than on a command line, so no card
text reaches a process listing. Modes, in CARD_IO_MODE:

  branch   print the card's branch on stdout
  mark     append CARD_IO_MARK to the card's description, once
  status   append CARD_IO_MARK as one line inside the card's status block, which is
           the running account of how the card got where it is
  block    replace the block named CARD_IO_BLOCK in the description with the text on
           stdin, adding it at the end if the card has no such block yet, or at the
           very top when CARD_IO_BLOCK_AT is "top"
  blocked  set the card's blocked flag from CARD_IO_BLOCKED, "true" or "false"
  state    print "blocked" or "clear" on stdout, the card's flag as it stands
  line     print the value of the CARD_IO_LINE named line, or nothing if absent

The card's branch is its own `branch:` line when it has one, otherwise the
project's branch prefix and the ticket id, which is what the Cannon names a
worktree's branch. Written by the born-threaded practice; MIT.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def daemon():
    host = os.environ.get("POTATO_DAEMON_HOST") or "127.0.0.1"
    port = os.environ.get("POTATO_DAEMON_PORT") or "3131"
    return f"http://{host}:{port}"


def api(path, method="GET", body=None):
    url = f"{daemon()}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode() or "null")


def ticket_path(project, ticket):
    return (f"/api/tickets/{urllib.parse.quote(project, safe='')}"
            f"/{urllib.parse.quote(ticket, safe='')}")


def main():
    project = os.environ.get("POTATO_PROJECT_ID") or ""
    ticket = os.environ.get("POTATO_TICKET_ID") or ""
    mode = os.environ.get("CARD_IO_MODE") or ""
    if not project or not ticket:
        print("card-io: POTATO_PROJECT_ID and POTATO_TICKET_ID are not set", file=sys.stderr)
        return 2

    try:
        card = api(ticket_path(project, ticket)) or {}
    except Exception as e:
        print(f"card-io: could not read card {ticket} ({e.__class__.__name__})", file=sys.stderr)
        return 2
    description = card.get("description") or ""

    if mode == "branch":
        for line in description.splitlines():
            line = line.strip()
            if line.startswith("branch:"):
                name = line.split(":", 1)[1].strip()
                if name:
                    print(name)
                    return 0
        prefix = (os.environ.get("BRANCH_PREFIX") or "").strip()
        if not prefix:
            # The daemon's own default, from worktree.ts. Its project list does not carry
            # branchPrefix, and there is no single-project endpoint, so this cannot be
            # read from the Cannon and is stated in gate.conf instead.
            prefix = "potato"
        print(f"{prefix}/{ticket}")
        return 0

    if mode == "mark":
        mark = (os.environ.get("CARD_IO_MARK") or "").strip()
        if not mark:
            print("card-io: nothing to mark", file=sys.stderr)
            return 2
        if mark in description:
            return 0
        body = {"description": (description.rstrip() + "\n" + mark) if description else mark}
        try:
            api(ticket_path(project, ticket), method="PUT", body=body)
        except Exception as e:
            print(f"card-io: could not mark card {ticket} ({e.__class__.__name__})", file=sys.stderr)
            return 2
        return 0

    if mode == "status":
        line = (os.environ.get("CARD_IO_MARK") or "").strip()
        if not line:
            print("card-io: nothing to say", file=sys.stderr)
            return 2
        begin, end = "<!-- status:begin -->", "<!-- status:end -->"
        if begin in description and end in description:
            head, rest = description.split(begin, 1)
            body, tail = rest.split(end, 1)
            body = body.rstrip("\n") + "\n" + line + "\n"
            new_description = head + begin + "\n" + body.lstrip("\n") + end + tail
        else:
            new_description = (description.rstrip() + "\n\n" + begin + "\n" + line
                               + "\n" + end + "\n")
        try:
            api(ticket_path(project, ticket), method="PUT", body={"description": new_description})
        except Exception as e:
            print(f"card-io: could not write the status line ({e.__class__.__name__})", file=sys.stderr)
            return 2
        return 0

    if mode == "block":
        name = (os.environ.get("CARD_IO_BLOCK") or "").strip()
        if not name:
            print("card-io: no block named", file=sys.stderr)
            return 2
        text = sys.stdin.read().strip("\n")
        begin, end = f"<!-- {name}:begin -->", f"<!-- {name}:end -->"
        if begin in description and end in description:
            head, rest = description.split(begin, 1)
            _, tail = rest.split(end, 1)
            new_description = head + begin + "\n" + text + "\n" + end + tail
        elif (os.environ.get("CARD_IO_BLOCK_AT") or "").strip() == "top":
            # A reason nobody scrolls to is a reason nobody reads. A refusal goes above
            # everything, including the ids line, because it is the first thing a
            # reader of a bounced card needs.
            new_description = (begin + "\n" + text + "\n" + end + "\n\n"
                               + description.lstrip())
        else:
            new_description = (description.rstrip() + "\n\n" + begin + "\n" + text
                               + "\n" + end + "\n")
        try:
            api(ticket_path(project, ticket), method="PUT", body={"description": new_description})
        except Exception as e:
            print(f"card-io: could not write the {name} block ({e.__class__.__name__})", file=sys.stderr)
            return 2
        return 0

    if mode == "line":
        want = (os.environ.get("CARD_IO_LINE") or "").strip().lower()
        if not want:
            print("card-io: line needs CARD_IO_LINE", file=sys.stderr)
            return 2
        for raw in (card.get("description") or "").splitlines():
            stripped = raw.strip()
            if stripped.lower().startswith(want + ":"):
                print(stripped.split(":", 1)[1].strip())
                break
        return 0

    if mode == "state":
        print("blocked" if bool(card.get("blocked")) else "clear")
        return 0

    if mode == "blocked":
        want = (os.environ.get("CARD_IO_BLOCKED") or "").strip().lower()
        if want not in ("true", "false"):
            print("card-io: blocked must be true or false", file=sys.stderr)
            return 2
        if bool(card.get("blocked")) == (want == "true"):
            return 0
        try:
            api(ticket_path(project, ticket), method="PUT", body={"blocked": want == "true"})
        except Exception as e:
            print(f"card-io: could not set blocked on {ticket} ({e.__class__.__name__})",
                  file=sys.stderr)
            return 2
        return 0

    print(f"card-io: unknown mode {mode!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
