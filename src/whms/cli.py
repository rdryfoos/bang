# @covers US-LEND-10, AC-LEND-10, AC-LEND-20, US-OUT-10, AC-OUT-20
"""`lend add` and `lend list`."""
import argparse
import sys
from typing import List, Optional

from . import outstanding, records, store


def _line(item) -> str:
    return "%s\t%s\t%s" % (item["name"], item["borrower"], item["date_out"])


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="lend")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="write down an item you lent")
    add.add_argument("--name")
    add.add_argument("--borrower")
    add.add_argument("--date-out", dest="date_out")
    sub.add_parser("list", help="show everything still out, oldest first")
    args = parser.parse_args(argv)

    if args.command == "list":
        try:
            items = outstanding.select(store.load())
            for item in items:
                print(_line(item))
            if not items:
                print(outstanding.EMPTY_MESSAGE)
        except (OSError, ValueError) as err:
            print("error: could not read the records: %s" % err, file=sys.stderr)
            return 1
        return 0

    record, reasons = records.validate(args.name, args.borrower, args.date_out)
    if reasons:
        print("refused: " + "; ".join(reasons), file=sys.stderr)
        return 2
    try:
        store.append(record)
    except (OSError, ValueError) as err:
        print("error: not saved: %s" % err, file=sys.stderr)
        return 1
    print(_line(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
