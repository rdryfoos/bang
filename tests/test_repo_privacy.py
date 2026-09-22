import os
import pathlib
import subprocess

from whms import store
from whms.cli import main

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _status():
    return subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                          capture_output=True, text=True).stdout


def test_AC_PRIV_10_data_and_test_writes_stay_outside_the_worktree(data_file, monkeypatch, capsys):
    monkeypatch.delenv("WHMS_DATA_FILE")
    default = pathlib.Path(store.data_path()).resolve()
    assert ROOT not in default.parents
    monkeypatch.setenv("WHMS_DATA_FILE", str(data_file))
    assert ROOT not in data_file.resolve().parents
    before = _status()
    assert main(["add", "--name", "ladder", "--borrower", "Pat", "--date-out", "2026-01-05"]) == 0
    assert main(["list"]) == 0
    assert _status() == before
