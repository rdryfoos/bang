"""The lines a worker writes on a card, read by the check that reads them.

On 2026-09-24 a card went through Spec with no question, through Build with ten tests
named for their criteria, and through the Gate green, and then could not be promoted.
The Build worker had written `branch: potato/BAN-1 at 213f8b6`, because its own
instructions asked for "the branch name and head SHA on the card", and
`scripts/column-check.py` takes everything after `branch:` as a branch name and handed
it to git. There is no branch called `potato/BAN-1 at 213f8b6`.

Two files had to agree about one line and nobody had ever made them. This is that.
The instruction is read out of `cannon-template/agents/build.md` rather than restated
here, so a change to the prompt that breaks the check fails here rather than on
somebody's board.
"""
import importlib.util
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD_MD = ROOT / "cannon-template" / "agents" / "build.md"


def _column_check():
    """Load scripts/column-check.py, which is a script rather than a module."""
    spec = importlib.util.spec_from_file_location(
        "column_check", ROOT / "scripts" / "column-check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# A branch and a SHA the test supplies. build.md deliberately carries neither: an
# example is a value a worker can copy onto a card. A card carrying somebody else's
# commit reads as an answer; a card carrying another card's branch is worse, because
# that branch exists and the check judges this card by what is on it.
A_REAL_BRANCH = "potato/BAN-1"
A_REAL_SHA = "213f8b6c4e2a9d17f05b8e3c6a1d4f9021ab7c3e"


def _step_five():
    """Step 5 of build.md, which is where the card's lines are specified."""
    text = BUILD_MD.read_text(encoding="utf-8")
    return text.split("\n5. At the end of every attempt", 1)[1].split("\n6. ", 1)[0]


def _card_text_build_md_specifies():
    """The card lines build.md tells the worker to write, taken from build.md itself."""
    text = BUILD_MD.read_text(encoding="utf-8")
    pairs = re.findall(r'\{name:\s*"(branch|head)",\s*value:\s*"([^"]+)"\}', text)
    return {name: value for name, value in pairs}


def test_build_md_tells_the_worker_to_write_branch_and_head_separately():
    written = _card_text_build_md_specifies()
    assert "branch" in written, "build.md no longer specifies a branch: line"
    assert "head" in written, "build.md no longer specifies a head: line"
    assert " at " not in written["branch"], (
        "build.md is asking for the branch and the SHA on one line again: %r"
        % written["branch"])


def test_build_md_tells_the_worker_where_to_get_the_branch_name():
    # Described rather than shown, and the description says where to get it, which an
    # example branch name never did.
    branch = _card_text_build_md_specifies()["branch"]
    assert "rev-parse --abbrev-ref HEAD" in branch, (
        "build.md no longer tells the worker where to get its branch: %r" % branch)


def test_branch_of_returns_the_bare_name_for_the_card_build_md_writes():
    # The pair, checked end to end: a card in the shape build.md specifies, with real
    # values, fed to the function that reads it.
    description = "\n".join([
        "ids: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30",
        "Drag this card to Spec and watch what happens.",
        "branch: %s" % A_REAL_BRANCH,
        "head: %s" % A_REAL_SHA,
        "try: route /",
    ])
    assert _column_check().branch_of(description, "BAN-1") == A_REAL_BRANCH


def test_the_head_build_md_asks_for_is_a_full_sha():
    # Short SHAs stop being unique, and the head line is the one record of which commit
    # an attempt ended on. build.md describes the value instead of showing one, so what
    # is asserted is the instruction: it must demand the full forty and say where the
    # worker gets them.
    head = _card_text_build_md_specifies()["head"]
    assert "forty" in head, "build.md no longer asks for the full forty characters: %r" % head
    assert "rev-parse HEAD" in head, (
        "build.md no longer tells the worker where to get the SHA: %r" % head)


def test_build_md_shows_no_value_a_worker_could_copy_onto_a_card():
    # An example value in a prompt is a value that gets copied.
    #
    # A card carrying somebody else's commit is worse than a card carrying none: it
    # reads as an answer. A card carrying another card's branch is worse again, because
    # that branch exists, so the check resolves it, reads what is on it, and judges this
    # card by another card's work: a pass or a fail that is about the wrong thing.
    step = _step_five()

    shas = re.findall(r"\b[0-9a-f]{40}\b", step)
    assert not shas, "step 5 carries a copyable SHA: %s" % shas

    branches = re.findall(r"\b[A-Za-z0-9._-]+/[A-Z]{2,}-\d+\b", step)
    assert not branches, "step 5 carries a copyable branch name: %s" % branches


def test_the_old_one_line_form_is_what_refused_a_finished_card():
    # Proof that this test bites: the form the worker actually wrote on 2026-09-24.
    # branch_of hands this whole string to git as a branch name.
    refused = _column_check().branch_of(
        "branch: potato/BAN-1 at 213f8b6c4e2a9d17f05b8e3c6a1d4f9021ab7c3e", "BAN-1")
    assert refused != "potato/BAN-1"
    assert " at " in refused


def test_a_card_with_no_branch_line_still_falls_back_to_the_prefix(monkeypatch):
    monkeypatch.setenv("BRANCH_PREFIX", "potato")
    assert _column_check().branch_of("ids: US-UI-10", "BAN-1") == "potato/BAN-1"


def test_the_head_line_is_not_mistaken_for_the_branch_line():
    # `head:` sits next to `branch:` on the card now, and a reader of the description
    # that matched on the wrong prefix would hand git a SHA.
    description = "head: 213f8b6c4e2a9d17f05b8e3c6a1d4f9021ab7c3e\nbranch: potato/BAN-1"
    assert _column_check().branch_of(description, "BAN-1") == "potato/BAN-1"
