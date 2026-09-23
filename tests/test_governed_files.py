"""A card may not change the machinery that judges it.

Pinned by Rik's ruling of 2026-09-20, from a real run: a Build worker on card BAN-1's
branch edited scripts/gate.sh and scripts/gate.conf, and nothing objected. The edits were
correct, which is what makes the case worth pinning. This test is the objection.

These tests exercise scripts/governed-files.py over real temporary repositories rather
than mocking git, because what is being checked is a claim about git history.
"""
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "governed-files.py"


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def git(cwd, *args):
    r = run(["git", *args], cwd)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


@pytest.fixture()
def project(tmp_path):
    """A repository shaped like this one: a default branch with machinery on it."""
    d = tmp_path / "project"
    (d / "scripts").mkdir(parents=True)
    (d / "src").mkdir()
    (d / "scripts" / "gate.sh").write_text("# the gate\n")
    (d / "scripts" / "gate.conf").write_text('DEFAULT_BRANCH="main"\n')
    (d / "src" / "app.py").write_text("# the application\n")
    git(d, "init", "-q")
    git(d, "config", "user.email", "t@t")
    git(d, "config", "user.name", "t")
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "project")
    git(d, "branch", "-M", "main")
    return d


def check(project, head="HEAD"):
    return run([sys.executable, str(SCRIPT), "--base", "main", "--head", head], project)


def card_branch(project, name, path, text):
    git(project, "checkout", "-q", "-b", name)
    target = project / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", f"work on {path}")


def test_application_work_is_green(project):
    card_branch(project, "potato/CARD-1", "src/app.py", "# the application, changed\n")
    r = check(project)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "no governed file changed" in r.stdout


def test_editing_the_gate_script_is_red(project):
    card_branch(project, "potato/CARD-2", "scripts/gate.sh", "# the gate, changed by a card\n")
    r = check(project)
    assert r.returncode == 1
    assert "scripts/gate.sh" in r.stderr
    assert "may not change the machinery that judges it" in r.stderr


def test_editing_the_gate_config_is_red(project):
    card_branch(project, "potato/CARD-3", "scripts/gate.conf", 'DEFAULT_BRANCH="main"\nTEST_COMMAND="pytest"\n')
    r = check(project)
    assert r.returncode == 1
    assert "scripts/gate.conf" in r.stderr


def test_a_new_worker_is_red_too(project):
    card_branch(project, "potato/CARD-4", "scripts/helpful.py", "# added by a card\n")
    r = check(project)
    assert r.returncode == 1
    assert "scripts/helpful.py" in r.stderr


def test_both_kinds_of_change_still_reds_and_names_only_the_governed_one(project):
    git(project, "checkout", "-q", "-b", "potato/CARD-5")
    (project / "src" / "app.py").write_text("# application work\n")
    (project / "scripts" / "gate.sh").write_text("# and a quiet edit to the gate\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "both")
    r = check(project)
    assert r.returncode == 1
    assert "scripts/gate.sh" in r.stderr
    assert "src/app.py" not in r.stderr


def test_the_default_branch_itself_is_green(project):
    r = check(project)
    assert r.returncode == 0
    assert "not a card branch" in r.stdout
