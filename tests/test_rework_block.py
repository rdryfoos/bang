"""What a Rework block is, written down in the two files that act on it.

Buddy was asked on 2026-09-29 what a Rework block means and could not answer from this
repository. "Rework" appeared nowhere in CASE.md, CONSTITUTION.md, SURFACE.md or
scripts/, and the rule itself lives in the Cannon, in a TypeScript comment, in another
repository. The Build worker acted on a block correctly because build.md told it how;
nobody had written down what the thing is or who may write one.

It is in both prompts now, word for word, because neither agent reads the other's file:
the Build worker acts on a block at the start of an attempt, and Buddy is the agent the
daemon refuses one from.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENTS = ROOT / "cannon-template" / "agents"
GOVERNED_SCRIPT = ROOT / "scripts" / "governed-files.py"

OPENING = "**A Rework block is a hand's.**"

CLAUSES = (
    "refuses one written by an agent",
    "read at the start of the next Build attempt",
    "back to Build, not back to Spec",
    "carries delivery changes only",
    "is not Rework; that is a new promise",
    "Nothing on disk checks that a card's code does no more than its IDs promise",
)

# The Cannon is another repository, so these cannot be checked by opening them. They are
# checked for being cited at all: a reader who wants the rule rather than the summary has
# to be told where it is, and a paragraph that loses its citation is a paragraph that
# starts being rewritten from memory.
CITATIONS = (
    "apps/daemon/src/services/rework-guard.ts:4",
    "apps/daemon/src/services/session/prompts.ts:177",
)


def _flat(text):
    return " ".join(text.split())


def _paragraph(name):
    """The Rework paragraph out of one prompt, as one line."""
    text = (AGENTS / name).read_text(encoding="utf-8")
    assert OPENING in text, "%s carries no Rework paragraph" % name
    after = text.split(OPENING, 1)[1]
    # It ends at the blank line that follows it, in both files, whatever the indent.
    body = re.split(r"\n\s*\n", after, maxsplit=1)[0]
    return _flat(OPENING + body)


def test_both_prompts_carry_the_paragraph_in_the_same_words():
    """Two copies, because neither agent opens the other's file.

    build.md is read by the worker that acts on a block. ticket-qa.md is read by the
    agent the daemon refuses one from. A single copy would reach one of them.
    """
    build = _paragraph("build.md")
    buddy = _paragraph("ticket-qa.md")
    assert build == buddy, (
        "the two copies have drifted.\nbuild.md:     %s\nticket-qa.md: %s" % (build, buddy))


def test_the_paragraph_says_all_six_things():
    """Each clause is a thing somebody got wrong or could not find out."""
    for name in ("build.md", "ticket-qa.md"):
        paragraph = _paragraph(name)
        for clause in CLAUSES:
            assert _flat(clause) in paragraph, "%s's Rework paragraph drops: %s" % (name, clause)


def test_the_paragraph_says_where_the_rule_actually_lives():
    for name in ("build.md", "ticket-qa.md"):
        paragraph = _paragraph(name)
        for citation in CITATIONS:
            assert citation in paragraph, "%s no longer cites %s" % (name, citation)


def test_the_four_documents_a_card_may_not_change_are_governed():
    """The registry and the three documents beside it, where every prompt assumed they were.

    build.md, spec.md and ticket-qa.md have all told a worker not to change PRD.md,
    CASE.md, CONSTITUTION.md or SURFACE.md for as long as they have existed. Nothing
    refused it: the rule held while each agent kept reading its own instructions, and
    those four are where that is not good enough. They are not machinery the way the
    scripts are; they are what the machinery is pointed at.
    """
    source = GOVERNED_SCRIPT.read_text(encoding="utf-8")
    governed = re.search(r"^GOVERNED = \((.*?)^\)", source, re.S | re.M)
    assert governed, "scripts/governed-files.py has no GOVERNED tuple"
    entries = re.findall(r'"([^"]+)"', governed.group(1))

    not_governed = re.search(r"^NOT_GOVERNED = \((.*?)^\)", source, re.S | re.M)
    assert not_governed, "scripts/governed-files.py has no NOT_GOVERNED tuple"
    exempt = re.findall(r'"([^"]+)"', not_governed.group(1))

    for document in ("PRD.md", "CASE.md", "CONSTITUTION.md", "SURFACE.md"):
        assert document in entries, "%s is not governed: %s" % (document, entries)
        # The check subtracts NOT_GOVERNED from GOVERNED by prefix, so an exemption that
        # is a prefix of one of these would quietly undo the line above it.
        for one in exempt:
            assert not document.startswith(one), (
                "%r in NOT_GOVERNED exempts %s again" % (one, document))


def test_the_prompts_and_the_governed_list_name_the_same_documents():
    """Two places: the fence a worker reads, and the check that refuses the write.

    This pair is the whole defect. The prompts named four documents and the script named
    none of them, and nothing anywhere compared the two lists, so the rule read as
    enforced to every reader of either file alone.
    """
    source = GOVERNED_SCRIPT.read_text(encoding="utf-8")
    governed = set(re.findall(r'"([^"]+)"',
                              re.search(r"^GOVERNED = \((.*?)^\)", source, re.S | re.M).group(1)))
    for name in ("build.md", "spec.md", "ticket-qa.md"):
        prompt = _flat((AGENTS / name).read_text(encoding="utf-8"))
        for document in ("PRD.md", "CASE.md", "CONSTITUTION.md", "SURFACE.md"):
            if "`%s`" % document in prompt or document in prompt:
                assert document in governed, (
                    "%s tells a worker about %s and the governed list does not carry it"
                    % (name, document))
