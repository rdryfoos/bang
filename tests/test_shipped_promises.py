"""What BANG.md promises a stranger, checked against what the rest of the tree says.

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


def _first_cards():
    """The three cards as FIRST-CARDS.md gives them: (title, description)."""
    text = (ROOT / "FIRST-CARDS.md").read_text(encoding="utf-8")
    return re.findall(r"^## \d+\. ([^\n]+)\n\n```\n(.*?)\n```", text, re.S | re.M)


def _step_ten_cards():
    """The same three as BANG.md step 10 gives them, with its indentation taken off."""
    text = (ROOT / "BANG.md").read_text(encoding="utf-8")
    step = text.split("\n10. First cards.", 1)[1].split("\n11. ", 1)[0]
    cards = []
    for chunk in step.split("    Title: ")[1:]:
        lines = chunk.splitlines()
        title = lines[0].strip()
        body = []
        for line in lines[1:]:
            if line.startswith("    Title: "):
                break
            body.append(line[4:] if line.startswith("    ") else line)
        # The blank line under the title, and the prose after the last card, are the
        # page's, not the card's.
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        cards.append((title, "\n".join(body)))
    # Everything after the third card's block is the step's own prose; it starts at the
    # first line that is not part of a description, which is the one beginning "These are".
    trimmed = []
    for title, body in cards:
        body = body.split("\n    These are the same three")[0]
        body = body.split("\nThese are the same three")[0].rstrip()
        trimmed.append((title, body))
    return trimmed


def test_the_first_cards_are_the_same_in_both_places():
    """FIRST-CARDS.md and BANG.md step 10 carry the same three cards, word for word.

    They are two copies on purpose: a reader who opens FIRST-CARDS.md wants to know why
    these three, and an agent carrying out BANG.md wants the payload in the file it is
    reading. Two copies of anything drift. This is what stops them.
    """
    first = _first_cards()
    step = _step_ten_cards()
    assert len(first) == 3, "FIRST-CARDS.md no longer gives three cards: %s" % [t for t, _ in first]
    assert len(step) == 3, "BANG.md step 10 no longer gives three cards: %s" % [t for t, _ in step]
    for (ft, fb), (st, sb) in zip(first, step):
        assert ft == st, "titles differ: %r in FIRST-CARDS.md, %r in BANG.md step 10" % (ft, st)
        assert fb == sb, (
            "card %r differs between FIRST-CARDS.md and BANG.md step 10.\n"
            "FIRST-CARDS.md:\n%s\n\nBANG.md step 10:\n%s" % (ft, fb, sb))


def test_the_first_card_carries_the_five_ids_the_seed_leaves_unbuilt():
    """Card one's ids: line and the reservation that holds those IDs say the same thing.

    The seed shipped the browser once. The first card then had nothing to do, and nobody
    noticed for a week because no card had been dragged. If the screens ship again, this
    fails: the IDs would be proven and the reservation closed, while card one still asked
    for them.
    """
    first = dict((t, b) for t, b in _first_cards())
    card_one = first["Lend and return in the browser"]
    ids = [line for line in card_one.splitlines() if line.startswith("ids:")]
    assert len(ids) == 1, "card one has no ids: line"
    carried = {i.strip() for i in ids[0][len("ids:"):].split(",")}
    assert carried == {"US-UI-10", "FR-UI-10", "AC-UI-10", "AC-UI-20", "AC-UI-30"}

    reservation = [
        line for line in (ROOT / "specs" / "backlog" / "tasks.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("- [ ] T904")
    ]
    assert reservation, "T904 is not open, so card one's promises are not reserved for it"
    for one in sorted(carried):
        assert one in reservation[0], "%s is on card one but not on T904's Carries list" % one
