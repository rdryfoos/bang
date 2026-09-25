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
    # The instruction as it was actually written, which named no command at all:
    # "At the end of every attempt, push the card branch to the remote."
    re.compile(r"\bpush\b[^.]{0,40}\bto the remote\b", re.I),
    re.compile(r"\bopen\b[^.]{0,30}\b(draft\s+)?(pull request|PR)\b", re.I),
)

# A prompt may name the thing in order to forbid it, and on 2026-09-25 it had to: the
# project does have an `origin`, so "there is no remote" was false and the sentence that
# replaced it says `git push` will work and is still forbidden. A worker needs to be
# told that. So a line naming the command passes only when the line forbids it, and a
# line that merely mentions it is an offender exactly as before.
PROHIBITION = re.compile(
    r"\b(do not|don't|never|must not|may not|cannot|forbidden|refus\w*|no agent|"
    r"without pushing|instead of pushing)\b",
    re.I,
)


def _sentences(text):
    """The prose split into sentences, with the line each one starts on.

    Sentences rather than lines, because prose in these files is wrapped: the sentence
    that forbids a thing and the sentence that names it are often on different lines,
    and a line is not a unit of meaning.
    """
    out = []
    for paragraph_start, paragraph in _paragraphs(text):
        line = paragraph_start
        for piece in re.split(r"(?<=[.!?])\s+", paragraph):
            if piece.strip():
                out.append((line, " ".join(piece.split())))
            line += piece.count("\n")
    return out


def _paragraphs(text):
    """(line number, paragraph) for each blank-line-separated block."""
    out = []
    line = 1
    for block in re.split(r"\n\s*\n", text):
        if block.strip():
            out.append((line, block))
        line += block.count("\n") + 2
    return out


# A heading can forbid, and in these files one does: everything under "## Never" and
# under "What this will not do" is a prohibition by where it sits, with no negation
# word of its own. "Open a pull request, or run `gh` at all." is an instruction only if
# you read it without its heading.
FORBIDDING_HEADING = re.compile(r"^#+\s*(Never|What this will not do)\b", re.I)


def _forbidding_sections(text):
    """(start line, end line) for each section whose heading forbids."""
    lines = text.splitlines()
    spans, start = [], None
    for number, line in enumerate(lines, 1):
        if line.startswith("#"):
            if start is not None:
                spans.append((start, number - 1))
                start = None
            if FORBIDDING_HEADING.match(line):
                start = number
    if start is not None:
        spans.append((start, len(lines)))
    return spans


def _instructions_to_push(text):
    """Sentences that name a push or a pull request without forbidding it.

    A sentence is allowed to name the thing only when that same sentence forbids it.
    Not the sentence before: "Do not change CASE.md. Run git push once the tests are
    green." would pass on a neighbour rule, and the difference between an instruction
    and a prohibition is the whole value of this check.
    """
    forbidding = _forbidding_sections(text)
    offenders = []
    for line, sentence in _sentences(text):
        if not any(pattern.search(sentence) for pattern in FORBIDDEN):
            continue
        if PROHIBITION.search(sentence):
            continue
        if any(start <= line <= end for start, end in forbidding):
            continue
        offenders.append((line, sentence))
    return offenders


def test_no_agent_is_told_to_push_or_open_a_pull_request():
    offenders = {}
    for path in sorted(AGENTS.glob("*.md")):
        found = _instructions_to_push(path.read_text(encoding="utf-8"))
        if found:
            offenders[path.name] = [f"{line}: {sentence}" for line, sentence in found]
    assert not offenders, (
        "BANG.md promises this project pushes nothing anywhere, and these lines tell a "
        "worker otherwise: %s" % offenders)


def test_the_push_check_still_catches_an_instruction_to_push():
    """The exemption above must not become the loophole.

    Allowing a line that forbids pushing means allowing a line that contains the word
    "not", and the difference between those two is the whole value of the check. These
    are the lines the old Build worker actually carried, and a plausible way somebody
    might write the rule back in while sounding careful.
    """
    written_back = "\n".join([
        "5. At the end of every attempt, push the card branch to the remote.",
        "   Then run `gh pr create` and write the pr: line onto the card.",
        "   Do not change CASE.md. Run git push once the tests are green.",
    ])
    caught = _instructions_to_push(written_back)
    assert len(caught) == 3, "expected all three instructions, got %r" % caught

    forbidding = "\n".join([
        "- Push anything anywhere, to any branch or any remote. There is an `origin` and",
        "  it is never used; a `git push` that works is still forbidden.",
        "   **Do not push.** `git push` will succeed if you run it. Nothing stops it.",
    ])
    assert not _instructions_to_push(forbidding), (
        "a prompt forbidding a push must be allowed to name it")


def test_bang_still_makes_the_promise_these_agents_keep():
    # If the promise goes, the test above is checking nothing, and a reader of this file
    # would not know. So the promise is read here too, in the words BANG.md uses.
    text = (ROOT / "BANG.md").read_text(encoding="utf-8")
    assert "Push anything anywhere" in text, "BANG.md no longer promises not to push"


def test_no_shipped_file_claims_the_project_has_no_remote():
    """It has one, and saying otherwise cost two runs.

    `git clone` from a host always leaves an `origin`, so "this project has no remote"
    was false in BANG.md and in the Build worker's prompt. On the sixth cold run the
    worker flagged the mismatch twice, which is the right thing to do with a document
    that disagrees with the machine, and is time nobody should spend twice.

    The true sentence is that the remote exists and is never used, and a worker needs
    that version: `git push` will work if it runs it.
    """
    claim = re.compile(r"(has|have|is|are)\s+no\s+remote\b", re.I)
    offenders = {}
    for path in [ROOT / "BANG.md", *sorted(AGENTS.glob("*.md"))]:
        for line, sentence in _sentences(path.read_text(encoding="utf-8")):
            if claim.search(sentence):
                offenders.setdefault(path.name, []).append(f"{line}: {sentence}")
    assert not offenders, (
        "a clone from a host always has an origin; these say otherwise: %s" % offenders)


def _first_cards(root=ROOT):
    """The three cards as FIRST-CARDS.md gives them: (title, description)."""
    text = (root / "FIRST-CARDS.md").read_text(encoding="utf-8")
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


# Card one's promises: the five the seed deliberately leaves unbuilt so that a reader's
# first card has something to do. Written once, because three things below compare
# against them and a fourth copy is how they stop agreeing.
SEED_IDS = frozenset({"US-UI-10", "FR-UI-10", "AC-UI-10", "AC-UI-20", "AC-UI-30"})

ID_TOKEN = re.compile(r"\b(?:US|FR|AC|NFR)-[A-Z]+-\d+\b")


def _ids_a_spec_claims(text):
    """The IDs a spec.md says are in its own scope.

    Every spec in this tree ends with a "SpecAssay" section whose one job is to name
    them, so that is what is read: a spec that mentions an ID in passing has not
    claimed it, and card one's five are mentioned in passing today, in 005's prose
    about the screens it is waiting for. A spec written without that section is read
    whole, so a claim is never missed for want of a heading.
    """
    parts = re.split(r"^##\s*SpecAssay\b.*$", text, maxsplit=1, flags=re.M)
    body = parts[1].split("\n## ", 1)[0] if len(parts) > 1 else text
    return set(ID_TOKEN.findall(body))


def _spec_claiming_the_seed_ids(root):
    """The spec that claims all five of card one's promises, if one does yet."""
    for spec in sorted((root / "specs").glob("*/spec.md")):
        if SEED_IDS <= _ids_a_spec_claims(spec.read_text(encoding="utf-8")):
            return spec
    return None


def _seed_guard_problem(root):
    """What is wrong with the seed's reservation of card one's promises, or None.

    This is a statement about the seed, and on 2026-09-25 it was written as though it
    were a statement about the T904 line. The ninth cold run found the difference the
    expensive way. panda's Build worker wrote the screens, named eight tests for the
    ids, and ticked T904 because `cannon-template/agents/build.md` tells it to tick a
    reservation its spec has claimed. This guard then went red, because it read the
    tick as the screens having shipped in the seed again. Both rules were right and
    they contradicted each other, and nothing had ever run the pair together.

    So the open assertion is conditional, which is what it always meant. While no spec
    claims the five, T904 must be open, because an open task is the only thing holding
    those promises out of the Gate's silent-gap reading and the only thing keeping the
    seed's first card from having nothing to do. Once a spec claims them the
    reservation has expired by `specs/backlog/tasks.md`'s own rule, exactly as T906's
    line says of itself, and the box may be ticked or not.

    What is checked in both cases is the pair: card one carries five ids, and the T904
    line carries the same five. That one does not expire.
    """
    cards = dict(_first_cards(root))
    card_one = cards.get("Lend and return in the browser")
    if card_one is None:
        return "FIRST-CARDS.md has no card called 'Lend and return in the browser'"

    ids = [line for line in card_one.splitlines() if line.startswith("ids:")]
    if len(ids) != 1:
        return "card one has %d ids: lines, and it has one" % len(ids)
    carried = {one.strip() for one in ids[0][len("ids:"):].split(",")}
    if carried != set(SEED_IDS):
        return ("card one carries %s; the promises the seed leaves unbuilt are %s"
                % (sorted(carried), sorted(SEED_IDS)))

    tasks = (root / "specs" / "backlog" / "tasks.md").read_text(encoding="utf-8")
    lines = [line for line in tasks.splitlines() if re.match(r"^- \[[ x]\] T904\b", line)]
    if len(lines) != 1:
        return "specs/backlog/tasks.md has %d T904 lines; the reservation is one line" % len(lines)
    line = lines[0]

    missing = [one for one in sorted(carried) if one not in line]
    if missing:
        return "%s on card one but not on T904's Carries list" % ", ".join(missing)

    if _spec_claiming_the_seed_ids(root) is None and not line.startswith("- [ ] "):
        return ("T904 is ticked and no spec claims card one's five promises. Either the "
                "screens have shipped in the seed again, leaving a reader's first card "
                "nothing to do, or a tick went on ahead of the spec that earns it.")
    return None


def test_the_first_card_carries_the_five_ids_the_seed_leaves_unbuilt():
    """Card one's ids: line and the reservation that holds those IDs say the same thing.

    The seed shipped the browser once. The first card then had nothing to do, and nobody
    noticed for a week because no card had been dragged.
    """
    problem = _seed_guard_problem(ROOT)
    assert problem is None, problem


def _seed_tree(tmp_path, ticked=False, spec_claims=False):
    """A tree with just the three files the guard reads.

    Card one comes from the real FIRST-CARDS.md, because a fixture that wrote its own
    copy of the five ids would pass while the shipped file said something else.
    """
    (tmp_path / "specs" / "backlog").mkdir(parents=True)
    (tmp_path / "FIRST-CARDS.md").write_text(
        (ROOT / "FIRST-CARDS.md").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "specs" / "backlog" / "tasks.md").write_text(
        "# Backlog\n\n- [%s] T904 Deliver the four screens `design/` draws. "
        "**Carries**: %s (reserved backlog).\n"
        % ("x" if ticked else " ", ", ".join(sorted(SEED_IDS))), encoding="utf-8")
    if spec_claims:
        claiming = tmp_path / "specs" / "006-browser-screens"
        claiming.mkdir()
        (claiming / "spec.md").write_text(
            "# Feature Specification: Browser Screens\n\n"
            "## SpecAssay \u2014 durable IDs (required)\n\n"
            "IDs are inherited from PRD.md. None is created here. Scope of this "
            "feature: %s.\n" % ", ".join("`%s`" % one for one in sorted(SEED_IDS)),
            encoding="utf-8")
    return tmp_path


def test_the_seed_guard_passes_on_the_seed_with_the_reservation_open(tmp_path):
    """The shipped state, and the one this repository is in today."""
    assert _seed_guard_problem(_seed_tree(tmp_path)) is None


def test_the_seed_guard_fails_on_the_seed_with_the_reservation_ticked(tmp_path):
    """The failure it exists for, and the one the conditional must not let through.

    Nothing claims the five, and the box says they are delivered. That is either the
    browser back in the seed or a tick ahead of its spec, and both leave a reader
    dragging a card that has nothing to do.
    """
    problem = _seed_guard_problem(_seed_tree(tmp_path, ticked=True))
    assert problem is not None, "a ticked reservation with no spec behind it passed"
    assert "T904 is ticked" in problem


def test_the_seed_guard_passes_when_a_spec_claims_the_five_and_the_reservation_is_ticked(tmp_path):
    """panda's branch, which was refused and should not have been.

    A spec claims the five, the work is built and proven, and the worker ticked the
    reservation because `build.md` tells it to. The reservation has expired; the guard
    has nothing left to say.
    """
    tree = _seed_tree(tmp_path, ticked=True, spec_claims=True)
    assert _seed_guard_problem(tree) is None, _seed_guard_problem(tree)
    # And the claim is what makes the difference, not the spec directory existing.
    assert _spec_claiming_the_seed_ids(tree) is not None
