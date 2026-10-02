"""Every "step N" in BANG.md names a step, and names the right one.

BANG.md points at its own steps in prose seventeen times. Three of those pointed at the
wrong step before 2026-10-01: the first-cards step said the project id "came back from
step 9" when registering is step 11, Undo said "step 8 said it used" of the daemon step,
and the prompts paragraph said step 9 installed the template when the register step does.
Two of the three were wrong before any renumbering; the file had simply drifted.

A reference is checked two ways. The number has to be a step that exists, which catches a
reference left behind by an insertion. And the step it lands on has to be the one the
sentence is about, which is the part a number alone cannot tell you: the expectations
below name, for each reference, a word that must appear in that step's own first line.
"""
import re

import pytest

from bang_steps import ROOT, bang, steps

BANG = bang()
STEPS = steps(BANG)

# (the reference's own words, a word that must be in the step it names)
#
# The left side is enough of the sentence to find it and no more, so rewording the
# paragraph around it does not fail this. The right side is what the step is about.
EXPECTED = [
    ("start again from step 1", "Confirm where we are"),
    ("this file's, then start again from step 1", "Confirm where we are"),
    ("Step 2 works out which", "Which machine this is"),
    ("which step 2's receipt", "Which machine this is"),
    ("If step 2 said uv was present", "Which machine this is"),
    ("Step 3 says why Windows needs", "Install uv"),
    ("the same gap step 3 met", "Install uv"),
    ("It carries step 3's `-ExecutionPolicy ByPass`", "Install uv"),
    ("what step 3's fifth export adds", "Install uv"),
    ("in the same terminal as step 4", "Node and pnpm"),
    ("line is step 4's path again, and on Windows it", "Node and pnpm"),
    ("The first line is step 4's path again", "Node and pnpm"),
    ("the same reason step 5's commit is", "Spec Kit on this project"),
    ("by step 8 on the Python uv manages", "The project's own Python"),
    ("moved here by `PIP_CACHE_DIR` in step 8", "The project's own Python"),
    ("the pytest step 8 put in it", "The project's own Python"),
    ("stop\n   you at step 9", "Potato Cannon"),
    ("whichever of the two step 10 said it used", "The daemon"),
    ("with systemd, which step 10 needs", "The daemon"),
    ("step 4 names\n   the build for it", "Node and pnpm"),
    ("Step 6 says why at", "SpecAssay"),
    ("step 11 below installs that", "Register the project"),
    ("the project id came back from step 11", "Register the project"),
]


def test_every_step_reference_names_a_step_that_exists():
    """A reference to a step that is not there is a reference to nothing.

    This is the half that an inserted step breaks, and it breaks it loudly rather than
    leaving a reader to follow a number into the wrong paragraph.
    """
    assert STEPS, "BANG.md's Steps section has no numbered steps"
    highest = max(STEPS)
    missing = sorted({
        int(n) for n in re.findall(r"[Ss]tep (\d+)", BANG)
    } - set(STEPS))
    assert not missing, (
        "BANG.md points at step(s) %s; it has steps 1 to %d"
        % (", ".join(str(n) for n in missing), highest))


def test_the_steps_are_numbered_from_one_with_no_gaps():
    """Otherwise "a step that exists" is a weaker claim than it sounds."""
    assert sorted(STEPS) == list(range(1, max(STEPS) + 1)), (
        "BANG.md's steps are numbered %s" % sorted(STEPS))


@pytest.mark.parametrize("reference,summary", EXPECTED)
def test_each_reference_names_the_step_it_is_about(reference, summary):
    """The half a number cannot check on its own.

    `step 9` is a valid reference and a wrong one if the thing it is about is at 11.
    Three were wrong that way, and nothing noticed for weeks, because every number in
    the file was a number the file had.
    """
    assert reference in BANG, (
        "this reference is not in BANG.md any more, so this expectation is stale: %r"
        % reference)
    n = int(re.search(r"step (\d+)", reference, re.I).group(1))
    assert n in STEPS, "step %d does not exist" % n
    assert summary.lower() in STEPS[n].lower(), (
        "%r points at step %d, which is %r, not the step about %r"
        % (reference, n, STEPS[n], summary))


# RUN-NOTES.md is current guidance, so its step numbers have to track the file's. It is
# checked here rather than in its own test because the thing being checked is BANG.md's
# numbering, and one list of expectations is better than two that can disagree.
#
# RUNS.md is deliberately not checked. It is a log: a run on 2026-09-25 stopped at step 8
# of the file as it was that day, and renumbering the file does not change what happened.
# Rewriting those numbers to match today would falsify the record, which is the opposite
# of what the log is for.
NOTES = (ROOT / "RUN-NOTES.md").read_text(encoding="utf-8")

NOTES_EXPECTED = [
    ("Python from step 2 and the project's own scripts", "Which machine this is"),
    ("That is step 10, and the line", "The daemon"),
    ("first run at step 10", "The daemon"),
    ("`CERTIFICATE_VERIFY_FAILED` at step 3", "Install uv"),
    ("Step 3 answers it by not using", "Install uv"),
]


@pytest.mark.parametrize("reference,summary", NOTES_EXPECTED)
def test_run_notes_points_at_the_right_step_too(reference, summary):
    """The explainer sends a reader to a step by number, so the number has to be right."""
    assert reference in NOTES, (
        "this reference is not in RUN-NOTES.md any more: %r" % reference)
    n = int(re.search(r"step (\d+)", reference, re.I).group(1))
    assert n in STEPS, "RUN-NOTES.md points at step %d, which does not exist" % n
    assert summary.lower() in STEPS[n].lower(), (
        "%r points at step %d, which is %r, not the step about %r"
        % (reference, n, STEPS[n], summary))


def test_every_reference_in_run_notes_is_one_this_test_knows_about():
    found = len(re.findall(r"[Ss]tep \d+", NOTES))
    assert found == len(NOTES_EXPECTED), (
        "RUN-NOTES.md has %d step references and this test pins %d"
        % (found, len(NOTES_EXPECTED)))


def test_every_reference_in_the_file_is_one_this_test_knows_about():
    """A new reference arrives with its expectation, or this goes red.

    Without this the table above is a list of the references somebody remembered, and a
    sentence added later points wherever it likes.
    """
    found = len(re.findall(r"[Ss]tep \d+", BANG))
    assert found == len(EXPECTED), (
        "BANG.md has %d step references and this test pins %d; add the new one to "
        "EXPECTED with the step it is about" % (found, len(EXPECTED)))
