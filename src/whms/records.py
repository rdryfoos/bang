# @covers FR-LEND-10, AC-LEND-20
"""The item record and the reasons a record is refused."""
import datetime
from typing import Dict, List, Optional, Tuple

FIELDS = ("name", "borrower", "date_out")
LABELS = {"name": "an item name", "borrower": "a borrower", "date_out": "a date out"}


def _clean(value: Optional[str]) -> str:
    return (value or "").strip()


def validate(name: Optional[str], borrower: Optional[str],
             date_out: Optional[str]) -> Tuple[Dict[str, str], List[str]]:
    """Return the trimmed record and every reason it is refused (empty when complete)."""
    record = {"name": _clean(name), "borrower": _clean(borrower), "date_out": _clean(date_out)}
    reasons = []  # type: List[str]
    for field in FIELDS:
        if not record[field]:
            reasons.append("%s is required" % LABELS[field])
    if record["date_out"]:
        try:
            datetime.datetime.strptime(record["date_out"], "%Y-%m-%d")
        except ValueError:
            reasons.append("the date out must be a real date written YYYY-MM-DD")
    return record, reasons
