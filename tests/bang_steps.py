"""BANG.md's steps, found by what they say rather than by their number.

A step was inserted on 2026-10-01 and every number below it moved by one. Three tests
sliced the file with literals like `"\\n7. The project's own Python"`, and all three went
red on a file that was correct, which is a test measuring the numbering rather than the
thing. The numbers are the file's to choose; the opening words are what a step is.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

STEP_LINE = re.compile(r"^(\d+)\. (.*)$", re.M)


def bang():
    return (ROOT / "BANG.md").read_text(encoding="utf-8")


def steps(text=None):
    """Every step as {number: first line}, from the Steps section only.

    The places list and the fetch list are numbered too, so the section is cut first.
    """
    text = text if text is not None else bang()
    body = text.split("\n## Steps", 1)[1].split("\n## What done looks like", 1)[0]
    return {int(m.group(1)): m.group(2) for m in STEP_LINE.finditer(body)}


def step_body(opening, text=None):
    """One step's text, from the step whose first line starts with `opening`.

    Ends where the next numbered step begins, so the step's own fenced blocks and
    paragraphs come back whole.
    """
    text = text if text is not None else bang()
    found = [(n, line) for n, line in steps(text).items() if line.startswith(opening)]
    assert len(found) == 1, (
        "%d steps in BANG.md open with %r" % (len(found), opening))
    n, line = found[0]
    after = text.split("\n%d. %s" % (n, line), 1)[1]
    nxt = re.search(r"^\d+\. ", after, re.M)
    return after[: nxt.start()] if nxt else after


def step_number(opening, text=None):
    """Which number that step currently has."""
    text = text if text is not None else bang()
    found = [n for n, line in steps(text).items() if line.startswith(opening)]
    assert len(found) == 1, "%d steps open with %r" % (len(found), opening)
    return found[0]
