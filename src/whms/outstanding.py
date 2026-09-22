# @covers FR-OUT-10, AC-OUT-10
"""The outstanding list: items not yet marked returned, oldest first."""
from typing import Dict, List

EMPTY_MESSAGE = "Nothing is out."


def select(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Items with no date back, ordered by date out (stable, so ties keep file order)."""
    unreturned = [item for item in items if not item.get("date_back")]
    return sorted(unreturned, key=lambda item: item["date_out"])
