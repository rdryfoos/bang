"""One path to the records file, and the screens on it.

On 2026-09-21 two cards implemented marking a thing returned, one in the engine and
one in the browser screens, and both passed every check the project had. Nothing asked
whether a promise was already served; the checks asked whether each branch proved it,
and both did. Two paths that write the same record are not a duplicated function: they
are two answers to the question of what a record is, and the second one to run wins.

These tests are the question nothing was asking. The first reads the source and says
which files can put a record on disk. The second drives the browser screens and says
that lending, returning and listing all went through the engine to get there.
"""
import ast
import pathlib

from whms import store

SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "whms"

# The engine: the records file, the rules about what a record is, and the selection.
# Everything else under src/whms is a screen or a command line, and reaches a record
# through these.
ENGINE = {"store.py", "records.py", "outstanding.py"}

# Modules a write would have to go through, and the calls in them that write. Qualified
# by module on purpose: a bare name would catch `text.replace(",", " ")` in pages.py and
# report a screen writing records because it tidies a string.
FS_MODULES = {"os", "shutil", "tempfile", "json", "pathlib"}
FS_WRITES = {"replace", "rename", "remove", "unlink", "rmdir", "makedirs", "mkdir",
             "mkstemp", "mkdtemp", "NamedTemporaryFile", "TemporaryFile", "fdopen",
             "dump", "copy", "copyfile", "copy2", "move", "write_text", "write_bytes"}


def _writes(tree):
    """Every call in `tree` that could put a record on disk, named as it is written."""
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "open":
            mode = node.args[1] if len(node.args) > 1 else None
            for keyword in node.keywords:
                if keyword.arg == "mode":
                    mode = keyword.value
            text = mode.value if isinstance(mode, ast.Constant) else ""
            if isinstance(text, str) and any(c in text for c in "wax+"):
                found.append("open(..., %r)" % text)
        elif isinstance(func, ast.Attribute) and func.attr in FS_WRITES:
            owner = func.value
            if isinstance(owner, ast.Name) and owner.id in FS_MODULES:
                found.append("%s.%s()" % (owner.id, func.attr))
            elif isinstance(owner, ast.Attribute) and isinstance(owner.value, ast.Name) \
                    and owner.value.id in FS_MODULES:
                found.append("%s.%s.%s()" % (owner.value.id, owner.attr, func.attr))
    return found


def test_AC_ENG_10_no_file_outside_the_engine_writes_a_record():
    offenders = {}
    for path in sorted(SRC.glob("*.py")):
        if path.name in ENGINE:
            continue
        calls = _writes(ast.parse(path.read_text(encoding="utf-8")))
        if calls:
            offenders[path.name] = calls
    assert not offenders, "a second write path: %s" % offenders


def test_AC_ENG_10_the_screens_lend_return_and_list_through_the_engine(app, data_file,
                                                                      monkeypatch):
    through = []

    def watch(name):
        real = getattr(store, name)

        def seen(*args, **kwargs):
            through.append(name)
            return real(*args, **kwargs)

        monkeypatch.setattr(store, name, seen)

    for operation in ("load", "append", "mark_returned"):
        watch(operation)

    app.request("/lend", {"name": "Torque wrench", "borrower": "Sam",
                          "date_out": "Sep 1, 2026"})
    assert "append" in through, "the Lend screen saved without calling the engine"

    listing = app.get("/")
    assert "Torque wrench" in listing
    assert "load" in through, "the outstanding list was read without the engine"

    app.request("/return/0", {"date_back": "Sep 20, 2026"})
    assert "mark_returned" in through, "the return screen wrote without the engine"

    assert "Torque wrench" not in app.get("/")
