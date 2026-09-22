# @covers US-UI-10, FR-UI-10
"""The browser screens: a loopback-only web app over the same records file as `lend`."""
import argparse
import datetime
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, List, Optional
from urllib.parse import parse_qs

from . import outstanding, pages, records, store

READ_ERRORS = (OSError, ValueError, KeyError, TypeError)
UNREADABLE = "The records could not be read, so nothing is shown. Nothing was changed."


class Handler(BaseHTTPRequestHandler):
    today = staticmethod(datetime.date.today)  # type: Callable[[], datetime.date]

    def log_message(self, fmt, *args):
        sys.stderr.write("%s\n" % (fmt % args))

    def _send(self, status: int, html: str) -> None:
        data = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, where: str = "/") -> None:
        self.send_response(303)
        self.send_header("Location", where)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _form(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace")
        return {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}

    def _item(self, part: str):
        """(index, item) of an unreturned item, or None when it is gone or already back."""
        if not part.isdigit():
            return None
        index = int(part)
        items = store.load()
        if index >= len(items) or items[index].get("date_back"):
            return None
        return index, items[index]

    def _guard(self, action) -> None:
        try:
            action()
        except READ_ERRORS:
            self._send(500, pages.error_page(UNREADABLE))

    def do_GET(self):
        self._guard(self._get)

    def do_POST(self):
        self._guard(self._post)

    def _get(self) -> None:
        path = self.path.split("?")[0]
        today = self.today()
        if path == "/":
            items = store.load()
            index = {id(item): i for i, item in enumerate(items)}
            rows = [(index[id(item)], item) for item in outstanding.select(items)]
            self._send(200, pages.outstanding_page(rows, today))
        elif path == "/lend":
            self._send(200, pages.lend_page({"date_out": pages.format_date(today.isoformat())}))
        elif path.startswith("/return/"):
            found = self._item(path[len("/return/"):])
            if found is None:
                return self._redirect()
            self._send(200, pages.return_page(
                found[0], found[1], pages.format_date(today.isoformat())))
        else:
            self._send(404, pages.error_page("There is nothing at that address."))

    def _post(self) -> None:
        path = self.path.split("?")[0]
        form = self._form()
        if path == "/lend":
            self._lend(form)
        elif path.startswith("/return/"):
            self._return(path[len("/return/"):], form)
        else:
            self._send(404, pages.error_page("There is nothing at that address."))

    def _lend(self, form) -> None:
        typed = {k: form.get(k, "") for k in ("name", "borrower", "date_out")}
        iso = pages.parse_date(typed["date_out"])
        record, _ = records.validate(typed["name"], typed["borrower"], iso or "")
        errors = {}
        if not record["name"]:
            errors["name"] = "An item name is required. Nothing was saved."
        if not record["borrower"]:
            errors["borrower"] = "A borrower is required. Nothing was saved."
        if iso is None:
            errors["date_out"] = "Write the date like Sep 20, 2026. Nothing was saved."
        if errors:
            return self._send(200, pages.lend_page(typed, errors))
        store.append(record)
        self._redirect()

    def _return(self, part: str, form) -> None:
        found = self._item(part)
        if found is None:
            return self._redirect()
        typed = form.get("date_back", "")
        iso = pages.parse_date(typed)
        if iso is None:
            return self._send(200, pages.return_page(
                found[0], found[1], typed,
                "Write the date like Sep 20, 2026. Nothing was saved."))
        store.mark_returned(found[0], iso)
        self._redirect()


def make_server(port: int, today: Optional[Callable[[], datetime.date]] = None) -> HTTPServer:
    """A server on 127.0.0.1 only. `today` lets tests fix the date."""
    handler = type("BoundHandler", (Handler,), {})
    if today is not None:
        handler.today = staticmethod(today)  # type: ignore
    return HTTPServer(("127.0.0.1", port), handler)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m whms.web")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args(argv)
    server = make_server(args.port)
    print("http://127.0.0.1:%d/" % server.server_address[1], flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
