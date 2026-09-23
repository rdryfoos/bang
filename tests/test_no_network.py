import ast
import pathlib
import socket
import sys

import pytest

from whms.cli import main

SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "whms"
DENY = {"socket", "http", "urllib", "ssl", "smtplib", "ftplib", "xmlrpc", "requests",
        "httpx", "aiohttp", "asyncio", "telnetlib", "poplib", "imaplib", "socketserver"}
# No module is exempt. While the browser shipped, web.py was allowed http.server and
# urllib.parse, because a local listener is not an outbound request. The screens are card
# one's work now, and the exemption comes back when the module it was for comes back:
# until then a name on this list is denied to everything, which is the stricter reading
# and the one a reader can check.
ALLOWED = {"argparse", "datetime", "html", "json", "os", "sys", "tempfile", "typing"}


def test_AC_PRIV_20_lend_and_list_make_no_outbound_network_request(data_file, monkeypatch, capsys):
    def boom(*args, **kwargs):
        pytest.fail("network call attempted")

    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    assert main(["add", "--name", "ladder", "--borrower", "Pat", "--date-out", "2026-01-05"]) == 0
    assert main(["list"]) == 0


def test_NFR_PRIV_10_source_imports_no_network_or_third_party_client():
    stdlib = getattr(sys, "stdlib_module_names", None) or ALLOWED
    for path in SRC.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    continue
                names = [node.module or ""]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                assert top not in DENY, "%s imports %s" % (path.name, name)
                assert top in stdlib or top == "whms", "%s imports non-stdlib %s" % (path.name, name)
