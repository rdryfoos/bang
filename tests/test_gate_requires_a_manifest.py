"""A checker that exits 0 and writes nothing is red.

On 2026-10-02 SpecAssay 0.5.4 was installed the cold way on this Mac and the Gate said
green on a tree nothing had checked. The checker could not be parsed by the bash every
Mac ships, 3.2.57: it printed its first three lines, stopped at a construct that bash
will not read, wrote no manifest, and **exited 0**. `scripts/gate.sh` read that 0.

The manifest is the receipt. The checker's one job is to write one, so a run that
produced none did not do its job, whatever it exited with. These exercise the Gate's
specassay line against stub checkers, because the real failure is not reproducible
without a broken release and the behaviour has to be checkable without one.
"""
import os
import re
import subprocess

import pytest

from test_python_resolver import ROOT

GATE = ROOT / "scripts" / "gate.sh"
CONF = ROOT / "scripts" / "gate.conf"

STUB_EXITS_ZERO_WRITES_NOTHING = """#!/bin/sh
# What 0.5.4 did on bash 3.2: say a little, write nothing, exit 0.
echo "SpecAssay Check (Gate 2) starting"
echo "  python: python3 (3.9.6)"
exit 0
"""

STUB_WRITES_A_MANIFEST = """#!/bin/sh
printf '{"gate":{"ok":true},"rows":[]}' > trace-manifest.json
echo "Wrote trace-manifest.json (31 rows) gate.ok=True"
echo "SpecAssay Check (Gate 2): OK (31 registry IDs)"
exit 0
"""

STUB_CLAIMS_A_MANIFEST_IT_DID_NOT_WRITE = """#!/bin/sh
printf '{"gate":{"ok":true},"rows":[]}' > trace-manifest.json
echo "Wrote trace-manifest.v5beta.json (31 rows, schemaVersion 5, beta)"
echo "Wrote trace-manifest.json (31 rows) gate.ok=True"
exit 0
"""

STUB_LEAVES_A_STALE_MANIFEST = """#!/bin/sh
echo "SpecAssay Check (Gate 2) starting"
exit 0
"""


def _tree(tmp_path, stub, stale_manifest=False):
    """The smallest tree the Gate's specassay line will run in.

    Only the pieces that line touches: the config it reads the manifest path from, the
    checker it runs, and a gate.conf that turns the other tiers into no-ops so this test
    is about one line and not about the whole Gate.
    """
    root = tmp_path / "project"
    (root / ".specify" / "extensions" / "specassay-check" / "scripts").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "journal").mkdir()

    conf_dir = root / ".specify" / "extensions" / "specassay-check"
    (conf_dir / "specassay-check-config.yml").write_text(
        'registry: "PRD.md"\nmanifest_path: "trace-manifest.json"\n', encoding="utf-8")

    checker = conf_dir / "scripts" / "check-traceability.sh"
    checker.write_text(stub, encoding="utf-8")
    checker.chmod(0o755)

    for name in ("gate.sh", "python.sh", "check-anchors.py", "governed-files.py",
                 "write-receipt.py", "manifest-table.py"):
        dest = root / "scripts" / name
        dest.write_text((ROOT / "scripts" / name).read_text(encoding="utf-8"),
                        encoding="utf-8")
        # The preflight requires the anchors check to be executable, and a copy made with
        # write_text is not.
        dest.chmod(0o755)

    # The floor and the other gate lines are not what this is about. TEST_COMMAND is a
    # true, and the anchors and governed-files checks are given something that passes.
    (root / "scripts" / "gate.conf").write_text(
        'DEFAULT_BRANCH="main"\nTEST_COMMAND="true"\nTEST_RESULTS="test-results.xml"\n'
        'RECEIPT_SOURCE="local"\nJOURNAL_PREFIX="journal"\n', encoding="utf-8")

    if stale_manifest:
        (root / "trace-manifest.json").write_text('{"stale":true}', encoding="utf-8")
        old = 1000000000
        os.utime(root / "trace-manifest.json", (old, old))

    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    (root / "PRD.md").write_text("- AC-X-10 — a promise.\n", encoding="utf-8")
    env = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@e.com",
               GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@e.com")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", "start"], cwd=root, check=True, env=env)
    return root


def _run_gate(root):
    r = subprocess.run(["bash", "scripts/gate.sh"], cwd=str(root),
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def _specassay_line(out):
    for line in out.splitlines():
        if "specassay:" in line:
            return line.strip()
    raise AssertionError("the Gate printed no specassay line:\n%s" % out)


def test_a_checker_that_exits_zero_and_writes_nothing_is_red(tmp_path):
    """The 0.5.4 failure, as a stub, because the real one needs a broken release."""
    root = _tree(tmp_path, STUB_EXITS_ZERO_WRITES_NOTHING)
    code, out = _run_gate(root)
    assert "3 specassay: RED" in out, _specassay_line(out)
    assert "checker wrote no manifest; exit status alone is not a verdict" in out, (
        "the RED does not say why:\n%s" % out)
    assert "GATE RED" in out, "the Gate did not go red overall:\n%s" % out
    assert code != 0, "the Gate exited %d on a checker that checked nothing" % code


def test_a_checker_that_writes_its_manifest_is_green(tmp_path):
    """The other half, so the check is not just "always red"."""
    root = _tree(tmp_path, STUB_WRITES_A_MANIFEST)
    code, out = _run_gate(root)
    assert "3 specassay: green" in out, _specassay_line(out)
    assert (root / "trace-manifest.json").exists()


def test_a_manifest_left_by_an_earlier_run_does_not_count(tmp_path):
    """Otherwise the first green run makes every later one green.

    The manifest is taken away before the checker runs, so the file that exists
    afterwards is the one this run wrote. A file left in the worktree from last week is
    not evidence that anything ran today, and leaving it there beside a failed check is
    worse than having none.
    """
    root = _tree(tmp_path, STUB_LEAVES_A_STALE_MANIFEST, stale_manifest=True)
    code, out = _run_gate(root)
    assert "3 specassay: RED" in out, _specassay_line(out)
    assert "checker wrote no manifest" in out, (
        "the RED does not say why:\n%s" % out)
    assert "an earlier run's manifest was taken away first" in out, (
        "the RED does not say the stale manifest was removed:\n%s" % out)
    assert not (root / "trace-manifest.json").exists(), (
        "a stale manifest survived a failed check, which is what misleads a reader")


def test_a_manifest_the_checker_claims_but_did_not_write_is_red(tmp_path):
    """There is no config key for the v5beta manifest, so the claim is the contract.

    The checker derives that file's name and announces it. A checker that says "Wrote
    trace-manifest.v5beta.json" and did not is reporting work it did not do, and the
    primary manifest being present is not an answer to that.
    """
    root = _tree(tmp_path, STUB_CLAIMS_A_MANIFEST_IT_DID_NOT_WRITE)
    code, out = _run_gate(root)
    assert "3 specassay: RED" in out, _specassay_line(out)
    assert "the checker said it wrote this" in out, (
        "the RED does not name the claimed manifest:\n%s" % out)
    assert "trace-manifest.v5beta.json" in out


def test_the_gate_reads_the_manifest_path_from_the_config(tmp_path):
    """A project that puts its manifest elsewhere is still checked.

    The path is `manifest_path` in the specassay config, which is the same place the
    checker reads it from. Hard-coding the default here would pass a project that
    configured another name while checking nothing.
    """
    root = _tree(tmp_path, STUB_WRITES_A_MANIFEST)
    conf = root / ".specify" / "extensions" / "specassay-check" / "specassay-check-config.yml"
    conf.write_text('registry: "PRD.md"\nmanifest_path: "build/thread.json"\n', encoding="utf-8")
    code, out = _run_gate(root)
    # The stub writes trace-manifest.json, which is no longer the configured name.
    assert "3 specassay: RED" in out, _specassay_line(out)
    assert "build/thread.json" in out, (
        "the Gate did not look for the configured manifest:\n%s" % out)
