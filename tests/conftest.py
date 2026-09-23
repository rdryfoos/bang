"""What more than one test file needs: the records file, pointed outside the worktree.

The App harness that used to live here went with the browser. The screens are card
one's work now; when they come back, the harness that drives them comes back with
them, here, so two test files can share one copy of it.
"""
import pytest


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    path = tmp_path / "items.json"
    monkeypatch.setenv("WHMS_DATA_FILE", str(path))
    return path
