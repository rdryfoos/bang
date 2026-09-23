"""What more than one test file needs: the records file, and a running screen server.

The App harness lives here rather than in test_web.py because two files now drive the
screens. A second copy of it would be a second answer to what "the app under test" is,
which is the thing tests/test_one_write_path.py exists to refuse.
"""
import datetime
import threading
import urllib.error
import urllib.parse
import urllib.request

import pytest

from whms import web

TODAY = datetime.date(2026, 9, 20)


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    path = tmp_path / "items.json"
    monkeypatch.setenv("WHMS_DATA_FILE", str(path))
    return path


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class App:
    """The screens, served on a loopback port of the kernel's choosing."""

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
def make_app(data_file):
    """Start a screen server, or a second one, and close every one at the end."""
    started = []

    def make():
        started.append(App())
        return started[-1]

    yield make
    for started_app in started:
        started_app.close()


@pytest.fixture
def app(make_app):
    return make_app()
