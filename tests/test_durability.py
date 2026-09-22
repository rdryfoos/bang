# @covers NFR-DUR-10, AC-DUR-10
"""Records survive restarting the application.

Each "restart" is a separate operating-system process, so nothing survives between
them except what is on disk. All fixture values are invented.
"""
import json
import os
import pathlib
import subprocess
import sys

SRC = str(pathlib.Path(__file__).resolve().parent.parent / "src")


def run(env, code=None, args=()):
    cmd = [sys.executable, "-c", code] if code else [sys.executable, "-m", "whms", *args]
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def read_back(env):
    r = run(env, "import json; from whms import store; print(json.dumps(store.load()))")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_AC_DUR_10_lends_and_returns_are_still_present_with_dates_after_restart(tmp_path):
    data = tmp_path / "items.json"
    env = dict(os.environ, WHMS_DATA_FILE=str(data), PYTHONPATH=SRC)

    for name, borrower, date in (("ladder", "Pat", "2026-01-05"), ("drill", "Sam", "2026-01-09")):
        r = run(env, args=["add", "--name", name, "--borrower", borrower, "--date-out", date])
        assert r.returncode == 0, r.stderr
    saved = json.loads(data.read_text())
    assert [i["date_out"] for i in saved] == ["2026-01-05", "2026-01-09"]

    assert read_back(env) == saved

    # A return, stood in for by a date_back written to the file (BAN-3 owns the operation).
    saved[0]["date_back"] = "2026-01-20"
    data.write_text(json.dumps(saved))
    after = read_back(env)
    assert after == saved
    assert after[0]["date_back"] == "2026-01-20" and "date_back" not in after[1]
    listing = run(env, args=["list"])
    assert listing.returncode == 0, listing.stderr
    assert "drill" in listing.stdout and "ladder" not in listing.stdout

    r = run(env, args=["add", "--name", "saw", "--borrower", "Lee", "--date-out", "2026-02-01"])
    assert r.returncode == 0, r.stderr
    final = read_back(env)
    assert final[:2] == saved and len(final) == 3
    assert final[2]["date_out"] == "2026-02-01"
