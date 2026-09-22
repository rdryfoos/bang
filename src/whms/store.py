# @covers FR-LEND-10, AC-LEND-10, NFR-PRIV-10, AC-UI-30
"""Item records kept in one JSON file on this machine."""
import json
import os
import tempfile
from typing import Dict, List

DEFAULT_PATH = os.path.join("~", ".who-has-my-stuff", "items.json")


def data_path() -> str:
    return os.path.expanduser(os.environ.get("WHMS_DATA_FILE") or DEFAULT_PATH)


def load() -> List[Dict[str, str]]:
    try:
        with open(data_path(), encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return []


def _write(items: List[Dict[str, str]]) -> None:
    """Replace the file with `items`; the earlier file goes only after the new one is written."""
    path = data_path()
    folder = os.path.dirname(path) or "."
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=folder, prefix=".items-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(items, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def append(record: Dict[str, str]) -> None:
    """Add a record. The earlier file is replaced only after the new one is written."""
    _write(load() + [record])


def mark_returned(index: int, date_back: str) -> bool:
    """Set date_back on the unreturned item at `index`; False, and no write, if there is none."""
    items = load()
    if not 0 <= index < len(items) or items[index].get("date_back"):
        return False
    items[index]["date_back"] = date_back
    _write(items)
    return True
