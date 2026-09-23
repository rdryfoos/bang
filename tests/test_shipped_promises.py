"""What BANG.md promises a stranger, checked against what the board would actually do.

BANG.md tells the person who is about to paste three blocks that this project pushes
nothing anywhere, and that its promotions are local merges into its own main branch.
Until 2026-09-23 the Build worker's own instructions told it to push every attempt and
open a draft pull request. Nobody had run a card far enough to find out, so the promise
and the prompt sat side by side in the same repository for a week, disagreeing.

These tests read the shipped files as a stranger would: the promise in one, the
instruction in the other.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENTS = ROOT / "cannon-template" / "agents"

# What a worker doing the thing would have to write. Both spellings of the forge CLI,
# because "gh pr create" and "gh  pr" are the same instruction to a reader.
FORBIDDEN = (
    re.compile(r"git\s+push", re.I),
    re.compile(r"\bgh\s+pr\b", re.I),
)


def test_no_agent_is_told_to_push_or_open_a_pull_request():
    offenders = {}
    for path in sorted(AGENTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            for pattern in FORBIDDEN:
                if pattern.search(line):
                    offenders.setdefault(path.name, []).append(f"{number}: {line.strip()}")
    assert not offenders, (
        "BANG.md promises this project pushes nothing anywhere, and these lines tell a "
        "worker otherwise: %s" % offenders)


def test_bang_still_makes_the_promise_these_agents_keep():
    # If the promise goes, the test above is checking nothing, and a reader of this file
    # would not know. So the promise is read here too, in the words BANG.md uses.
    text = (ROOT / "BANG.md").read_text(encoding="utf-8")
    assert "Push anything anywhere" in text, "BANG.md no longer promises not to push"
