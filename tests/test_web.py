import datetime
import json
import re
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request

import pytest

from whms import web
from whms.cli import main

TODAY = datetime.date(2026, 9, 20)
ID_PATTERN = re.compile(r"[A-Z]+-[A-Z]+-\d\d")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class App:
    def __init__(self):
        self.server = web.make_server(0, today=lambda: TODAY)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.opener = urllib.request.build_opener(NoRedirect)

    def request(self, path, form=None, follow=True):
        data = urllib.parse.urlencode(form).encode() if form is not None else None
        url = "http://127.0.0.1:%d%s" % (self.port, path)
        try:
            resp = (urllib.request.urlopen if follow else self.opener.open)(url, data)
            return resp.status, resp.read().decode(), resp.headers
        except urllib.error.HTTPError as err:
            return err.code, err.read().decode(), err.headers

    def get(self, path):
        return self.request(path)[1]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def app(data_file):
    a = App()
    yield a
    a.close()


def seed(data_file, items):
    data_file.write_text(json.dumps(items))


def test_AC_UI_10_front_page_lists_outstanding_oldest_first_with_days_out_or_says_nothing_is_out(app, data_file):
    seed(data_file, [
        {"name": "Ladder", "borrower": "Pat", "date_out": "2026-09-01"},
        {"name": "Returned drill", "borrower": "Lee", "date_out": "2026-01-01", "date_back": "2026-02-01"},
        {"name": "Camp chair", "borrower": "Alex", "date_out": "2026-07-14"},
        {"name": "Shears", "borrower": "Sam", "date_out": "2026-09-19"},
    ])
    page = app.get("/")
    assert page.index("Camp chair") < page.index("Ladder") < page.index("Shears")
    assert "Returned drill" not in page
    assert "68 days" in page and "19 days" in page and "1 day<" in page
    assert "Alex has it. Out since Jul 14, 2026." in page
    assert page.count("Mark returned") == 3 and 'href="/return/2"' in page
    assert 'href="/lend"' in page and "Lend something" in page
    assert "Your records are in a file on this machine and nowhere else." in page
    for empty in (None, [{"name": "x", "borrower": "y", "date_out": "2026-01-01", "date_back": "2026-01-02"}]):
        if empty is None:
            assert not data_file.exists() or data_file.unlink() is None
        else:
            seed(data_file, empty)
        page = app.get("/")
        assert "Nothing is out." in page
        assert "Everything you lent has come back, or you have not lent anything yet." in page
        assert "Lend something" in page


def test_AC_UI_20_lend_saves_and_shows_in_list_and_missing_borrower_is_refused_in_place(app, data_file):
    form = app.get("/lend")
    assert 'value="Sep 20, 2026"' in form and "Back to the list" in form and "Save" in form
    status, _, headers = app.request("/lend", {"name": "Wrench", "borrower": "Sam", "date_out": "Sep 20, 2026"}, follow=False)
    assert status == 303 and headers["Location"] == "/"
    assert json.loads(data_file.read_text()) == [{"name": "Wrench", "borrower": "Sam", "date_out": "2026-09-20"}]
    assert "Sam has it. Out since Sep 20, 2026." in app.get("/")
    before = data_file.read_bytes()
    status, page, _ = app.request("/lend", {"name": "Drill", "borrower": "  ", "date_out": "2026-09-18"})
    assert "A borrower is required. Nothing was saved." in page
    assert 'value="Drill"' in page and 'value="2026-09-18"' in page
    assert data_file.read_bytes() == before
    fresh = data_file.parent / "other.json"
    for bad in ({"name": "", "borrower": "Sam", "date_out": "Sep 20, 2026"},
                {"name": "Drill", "borrower": "Sam", "date_out": "soonish"}):
        _, page, _ = app.request("/lend", bad)
        assert "Nothing was saved." in page
    assert data_file.read_bytes() == before and not fresh.exists()


def test_AC_UI_20_missing_borrower_on_absent_file_creates_nothing(app, data_file):
    _, page, _ = app.request("/lend", {"name": "Drill", "borrower": "", "date_out": "Sep 20, 2026"})
    assert "A borrower is required." in page and not data_file.exists()


def test_AC_UI_30_mark_returned_defaults_to_today_removes_item_and_survives_restart(app, data_file):
    seed(data_file, [{"name": "Camp chair", "borrower": "Alex", "date_out": "2026-07-14"},
                     {"name": "Shears", "borrower": "Sam", "date_out": "2026-08-01"}])
    page = app.get("/return/0")
    assert "Camp chair" in page and "Alex has it. Out since Jul 14, 2026." in page
    assert 'value="Sep 20, 2026"' in page and "Back to the list" in page
    assert app.request("/return/0", {"date_back": "Sep 20, 2026"}, follow=False)[0] == 303
    assert json.loads(data_file.read_text())[0]["date_back"] == "2026-09-20"
    assert "Camp chair" not in app.get("/") and "Shears" in app.get("/")
    second = App()
    try:
        assert "Camp chair" not in second.get("/")
    finally:
        second.close()
    before = data_file.read_bytes()
    for stale in ("/return/0", "/return/9", "/return/x"):
        assert app.request(stale, {"date_back": "Sep 20, 2026"}, follow=False)[0] == 303
    assert data_file.read_bytes() == before
    _, page, _ = app.request("/return/1", {"date_back": "never"})
    assert "Nothing was saved." in page and data_file.read_bytes() == before
    app.request("/return/1", {"date_back": "2026-09-20"})
    assert "Nothing is out." in app.get("/")


def test_FR_UI_10_local_app_shares_the_command_lines_file_and_binds_loopback_only(app, data_file, capsys):
    assert app.server.server_address[0] == "127.0.0.1"
    assert main(["add", "--name", "ladder", "--borrower", "Pat", "--date-out", "2026-09-01"]) == 0
    assert "ladder" in app.get("/")
    app.request("/lend", {"name": "Wrench", "borrower": "Sam", "date_out": "Sep 20, 2026"})
    capsys.readouterr()
    assert main(["list"]) == 0
    assert "Wrench\tSam\t2026-09-20" in capsys.readouterr().out
    for path in ("/", "/lend", "/return/0", "/nowhere"):
        assert not ID_PATTERN.search(app.get(path))


def test_FR_UI_10_module_starts_on_a_port_and_reports_it(tmp_path):
    env = {"WHMS_DATA_FILE": str(tmp_path / "i.json"), "PYTHONPATH": "src", "PATH": ""}
    proc = subprocess.Popen([sys.executable, "-m", "whms.web", "--port", "0"],
                            stdout=subprocess.PIPE, env=env)
    try:
        url = proc.stdout.readline().decode().strip()
        assert url.startswith("http://127.0.0.1:")
        assert "Nothing is out." in urllib.request.urlopen(url).read().decode()
    finally:
        proc.terminate()
        proc.wait()


def test_US_UI_10_lend_see_and_return_loop_needs_no_command_line(app, data_file):
    assert "Nothing is out." in app.get("/")
    app.request("/lend", {"name": "Wrench", "borrower": "Sam", "date_out": "Sep 20, 2026"})
    assert "Wrench" in app.get("/")
    app.request("/return/0", {"date_back": "Sep 20, 2026"})
    assert "Nothing is out." in app.get("/")
    data_file.write_text("{ not json")
    status, page, _ = app.request("/")
    assert status == 500 and "Nothing is out." not in page
