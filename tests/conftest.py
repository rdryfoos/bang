import pytest


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    path = tmp_path / "items.json"
    monkeypatch.setenv("WHMS_DATA_FILE", str(path))
    return path
