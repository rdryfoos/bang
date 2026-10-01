"""Which main a card is measured against, and whether the refusal says so.

BANG.md has every cold user commit to local `main`. On a machine that later fetches, the
local branch is a stale copy of the project's main: a hand's commit that reached origin is
ahead of it, so a card branch cut from local main reads as carrying that hand's work. The
ThinkPad met this on 2026-09-30 with a PRD.md edit that was not the card's.

So the check prefers `origin/main` when the repository has one, and falls back to the
local branch, which is every cold machine and is unchanged for them. The refusal names
which one it used, because a reader meeting a surprising RED has to know what they were
measured against, and a check that is right and unexplainable is a check somebody turns
off.
"""
import os
import subprocess

import pytest

from test_python_resolver import ROOT  # the repository root, resolved once


def _run(cwd, *argv):
    env = dict(os.environ,
               GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@example.com")
    r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, env=env)
    assert r.returncode == 0, "%s: %s%s" % (argv, r.stdout, r.stderr)
    return r.stdout


def _repo(path):
    path.mkdir(parents=True, exist_ok=True)
    _run(path, "git", "init", "-q", "-b", "main")
    (path / "scripts").mkdir(exist_ok=True)
    # The check reads DEFAULT_BRANCH out of this file, and nothing else from it.
    (path / "scripts" / "gate.conf").write_text('DEFAULT_BRANCH="main"\n', encoding="utf-8")
    (path / "README.md").write_text("start\n", encoding="utf-8")
    _run(path, "git", "add", "-A")
    _run(path, "git", "commit", "-q", "-m", "start")
    return path


def _check(cwd, *extra):
    """governed-files.py as the Gate runs it, from the tree under test."""
    script = str(ROOT / "scripts" / "governed-files.py")
    r = subprocess.run(["python3", script, *extra], cwd=str(cwd),
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def _card_branch(path, filename="PRD.md"):
    _run(path, "git", "checkout", "-q", "-b", "potato/CARD-1")
    (path / filename).write_text("a card edits a governed file\n", encoding="utf-8")
    _run(path, "git", "add", "-A")
    _run(path, "git", "commit", "-q", "-m", "the card's work")


def test_a_repository_with_no_origin_uses_its_local_main(tmp_path):
    """Every cold machine. The fallback is exactly the old behaviour."""
    repo = _repo(tmp_path / "cold")
    _card_branch(repo)
    code, out = _check(repo)
    assert code == 1, out
    assert "PRD.md" in out
    assert "measured against the local main" in out
    assert "has no origin/main" in out


def test_a_repository_with_an_origin_uses_that_one(tmp_path):
    """The machine that fetched. Local main is behind and is not the project's main."""
    upstream = _repo(tmp_path / "upstream")
    clone = tmp_path / "clone"
    _run(tmp_path, "git", "clone", "-q", str(upstream), str(clone))

    # A hand lands a governed change on the project's main, after this clone was taken.
    (upstream / "PRD.md").write_text("a hand edits the registry\n", encoding="utf-8")
    _run(upstream, "git", "add", "-A")
    _run(upstream, "git", "commit", "-q", "-m", "a hand's work on the registry")
    _run(clone, "git", "fetch", "-q", "origin")

    # The card touches a different governed path, so only its own change should be named.
    _card_branch(clone, filename="scripts/column-check.py")
    code, out = _check(clone)
    assert code == 1, out
    assert "scripts/column-check.py" in out
    assert "PRD.md" not in out, (
        "the hand's commit on origin/main was read as the card's work:\n%s" % out)
    assert "measured against origin/main" in out


def test_a_named_base_is_used_as_named(tmp_path):
    """A caller that knows which branch it means is not second-guessed."""
    repo = _repo(tmp_path / "named")
    _run(repo, "git", "checkout", "-q", "-b", "other-main")
    _run(repo, "git", "checkout", "-q", "main")
    _card_branch(repo)
    code, out = _check(repo, "--base", "other-main")
    assert code == 1, out
    assert "named on the command line" in out


def test_a_repository_with_neither_says_so_rather_than_guessing(tmp_path):
    """Exit 2 is cannot-tell, which is not the same as green."""
    repo = tmp_path / "empty"
    repo.mkdir()
    _run(repo, "git", "init", "-q", "-b", "work")
    (repo / "scripts").mkdir()
    (repo / "scripts" / "gate.conf").write_text('DEFAULT_BRANCH="main"\n', encoding="utf-8")
    (repo / "a.txt").write_text("x\n", encoding="utf-8")
    _run(repo, "git", "add", "-A")
    _run(repo, "git", "commit", "-q", "-m", "only branch")
    code, out = _check(repo)
    assert code == 2, out
    assert "no main and no origin/main" in out


def test_the_green_line_also_names_the_branch_it_used(tmp_path):
    """A reader who sees green should know what that was green against."""
    repo = _repo(tmp_path / "green")
    code, out = _check(repo)
    assert code == 0, out
    assert "main" in out
