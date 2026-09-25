"""One name for the interpreter, resolved once, spelled nowhere.

On a Mac the interpreter is `python3` and there is no `python`. On Windows there is
`python` and no `python3`, and there never will be: the python.org installer lays down
`python.exe` and `py.exe` and no `python3.exe`, while the name `python3` is held by an
App Execution Alias that opens the Microsoft Store and exits.

The Dell run on 2026-09-25 met all of it in order. BANG.md's preflight caught the Store
stub and printed the winget line, which is what it was written to do. `winget install
--id Python.Python.3.12` then put Python 3.12.10 on the machine, `python --version` said
so, and `python3` went on not resolving, because nothing had installed anything by that
name.

So the name is not a constant, and no script may spell it. `scripts/python.sh` asks.
"""
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESOLVER = ROOT / "scripts" / "python.sh"

# A call is `python3` as a word, not preceded by a slash or a dash. The shebang on a
# .py file is the one exemption and it is a real one: a shebang is not a call, nothing
# in this project runs those files directly (every call site names the interpreter and
# the file), and on Windows a shebang is not read at all. Rewriting them to `python`
# would break every Mac, where that name does not exist.
CALL = re.compile(r"(?<![-\w/])python3(?![-\w])")
SHEBANG = re.compile(r"^#!.*python3\s*$")
BACKTICKED = re.compile(r"`[^`]*`")


def _calls_on(line, number):
    """True when this line runs python3, rather than talking about it.

    A file is allowed to name the thing in order to explain it, and these files have
    to: the whole reason `python.sh` exists cannot be written down without the word.
    The same exemption `test_shipped_promises.py` gives a prompt that forbids a push,
    and the same discipline: a comment or a backticked mention passes, a command does
    not.
    """
    if number == 1 and SHEBANG.match(line):
        return False
    if line.lstrip().startswith("#"):
        return False
    return bool(CALL.search(BACKTICKED.sub("", line)))


def _scripts():
    for path in sorted((ROOT / "scripts").rglob("*")):
        if path.is_file() and path != RESOLVER:
            yield path
    for path in sorted((ROOT / "cannon-template").rglob("*")):
        if path.is_file() and path.suffix in {".sh", ".py", ".md", ".json", ".yml"}:
            yield path


def test_no_script_spells_the_interpreters_name():
    offenders = []
    for path in _scripts():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if _calls_on(line, number):
                offenders.append("%s:%d: %s" % (path.relative_to(ROOT), number, line.strip()))
    assert not offenders, (
        "these spell the interpreter's name instead of resolving it through "
        "scripts/python.sh, and every one of them is a line that fails on Windows:\n%s"
        % "\n".join(offenders))


def test_bang_does_not_tell_the_reader_to_run_python3():
    """Step 2 used to ask for `python3` by name, and on Windows that is a stub."""
    text = (ROOT / "BANG.md").read_text(encoding="utf-8")
    offenders = [
        "%d: %s" % (n, line.strip())
        for n, line in enumerate(text.splitlines(), 1)
        if _calls_on(line, n)
    ]
    assert not offenders, "BANG.md still names the interpreter: %s" % offenders


def test_every_script_that_uses_python_sources_the_resolver():
    """`$PYTHON` unset is `""` under `set -u`, which is a command not found."""
    offenders = []
    for path in _scripts():
        if path.suffix not in {".sh", ""} and path.name != "pre-commit":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        uses = "$PYTHON" in text
        sources = "python.sh" in text
        if uses and not sources:
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, "these use $PYTHON without sourcing python.sh: %s" % offenders


def _resolve_with(tmp_path, names):
    """Run the resolver against a made-up path holding only `names`.

    `names` maps a command name to what it prints. A name mapped to None is the
    Microsoft Store's stub: on the path, and it prints nothing.
    """
    binaries = tmp_path / "bin"
    binaries.mkdir(exist_ok=True)
    # uname, because the refusal reads it to decide which advice to print. Nothing
    # else from the real path, so the machine's own python cannot answer instead.
    (binaries / "uname").symlink_to("/usr/bin/uname")
    for name, prints in names.items():
        script = binaries / name
        if prints is None:
            script.write_text("#!/bin/sh\nexit 9009\n")
        else:
            script.write_text("#!/bin/sh\necho '%s'\n" % prints)
        script.chmod(0o755)
    env = dict(os.environ, PATH=str(binaries))
    env.pop("PYTHON", None)
    return subprocess.run(
        ["/bin/bash", "-c", '. "%s" && printf "%%s" "$PYTHON"' % RESOLVER],
        capture_output=True, text=True, env=env)


def test_it_takes_python3_when_python3_is_real(tmp_path):
    out = _resolve_with(tmp_path, {"python3": "Python 3.12.10", "python": "Python 3.12.10"})
    assert out.returncode == 0
    assert out.stdout == "python3", out


def test_it_falls_to_python_when_python3_is_the_store_stub(tmp_path):
    """Windows, after winget has installed Python and the alias still holds the name."""
    out = _resolve_with(tmp_path, {"python3": None, "python": "Python 3.12.10"})
    assert out.returncode == 0, out.stderr
    assert out.stdout == "python", out


def test_it_takes_python_when_there_is_no_python3_at_all(tmp_path):
    out = _resolve_with(tmp_path, {"python": "Python 3.12.10"})
    assert out.returncode == 0, out.stderr
    assert out.stdout == "python", out


def test_a_python_2_is_not_an_answer(tmp_path):
    """The test is the line it prints, so this costs nothing extra."""
    out = _resolve_with(tmp_path, {"python": "Python 2.7.18"})
    assert out.returncode != 0
    assert "no Python 3" in out.stderr


def test_the_store_stub_on_both_names_counts_as_missing(tmp_path):
    out = _resolve_with(tmp_path, {"python3": None, "python": None})
    assert out.returncode != 0
    assert "no Python 3" in out.stderr


def test_the_windows_refusal_names_powershell_and_not_just_a_window(tmp_path):
    """The message is read inside Git Bash, and PowerShell is a different window.

    "Open a new window" is read, inside Git Bash, as another Git Bash. The Dell run's
    reader needed the name that is in the Start menu.
    """
    text = RESOLVER.read_text(encoding="utf-8")
    windows = text.split("MINGW*|MSYS*)", 1)[1].split(";;", 1)[0]
    assert "PowerShell" in windows, "the Windows refusal does not name PowerShell"
    assert "winget install --id Python.Python.3.12 -e --source winget" in windows


def test_the_web_contract_says_the_same_thing_in_both_places():
    """try.sh acts on it; design/README.md governs it. Three lines, one wording."""
    line = "src/whms/web.py           exists and runs as `$PYTHON -m whms.web`"
    assert line in (ROOT / "scripts" / "try.sh").read_text(encoding="utf-8")
    assert line in (ROOT / "design" / "README.md").read_text(encoding="utf-8")
