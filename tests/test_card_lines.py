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


def test_branch_of_returns_the_bare_name_for_the_card_build_md_writes():
    # The pair, checked end to end: the exact text build.md specifies, fed to the
    # function that reads it.
    written = _card_text_build_md_specifies()
    description = "\n".join([
        "ids: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30",
        "Drag this card to Spec and watch what happens.",
        "branch: %s" % written["branch"],
        "head: %s" % written["head"],
        "try: route /",
    ])
    assert _column_check().branch_of(description, "BAN-1") == written["branch"]


def test_the_head_build_md_asks_for_is_a_full_sha():
    # Short SHAs stop being unique, and the head line is the one record of which commit
    # an attempt ended on.
    head = _card_text_build_md_specifies()["head"]
    assert re.fullmatch(r"[0-9a-f]{40}", head), "build.md's head example is not 40 hex: %r" % head


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
