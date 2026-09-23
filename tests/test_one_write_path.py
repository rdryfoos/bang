"""One path to the records file, whatever knocks on it.

On 2026-09-21 two cards implemented marking a thing returned, one in the engine and
one in the browser screens, and both passed every check the project had. Nothing asked
whether a promise was already served; the checks asked whether each branch proved it,
and both did. Two paths that write the same record are not a duplicated function: they
are two answers to the question of what a record is, and the second one to run wins.

This test is the question nothing was asking. It reads the source and fails any module
under src/whms outside the engine that can put a record on disk. It names no entry point,
which is the point: it was written while the browser was in the tree, it keeps working
with the browser out of it, and it will refuse a second write path in the screens on the
day somebody builds them back.
"""
import ast
import pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "whms"

# The engine: the records file, the rules about what a record is, and the selection.
# Everything else under src/whms is a screen or a command line, and reaches a record
# through these.
ENGINE = {"store.py", "records.py", "outstanding.py"}

# Modules a write would have to go through, and the calls in them that write. Qualified
# by module on purpose: a bare name would catch a `text.replace(",", " ")` in a module
# that tidies a string and report it as a second write path.
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
