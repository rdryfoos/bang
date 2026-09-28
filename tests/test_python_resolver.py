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
import shutil
import subprocess

import pytest

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
    # uname, because the refusal reads it to decide which advice to print. Nothing else
    # from the real path, so the machine's own python cannot answer instead.
    #
    # Copied rather than symlinked, and found rather than named: it was
    # `symlink_to("/usr/bin/uname")`, which is one absolute path that is not there on
    # Windows and one call that needs a privilege there even when it is.
    uname = shutil.which("uname")
    if not uname:
        pytest.skip("no uname on the path, and the resolver's refusal reads it")
    shutil.copy(uname, binaries / pathlib.Path(uname).name)
    for name, prints in names.items():
        script = binaries / name
        if prints is None:
            script.write_text("#!/bin/sh\nexit 9009\n")
        else:
            script.write_text("#!/bin/sh\necho '%s'\n" % prints)
        script.chmod(0o755)
    env = dict(os.environ, PATH=str(binaries))
    env.pop("PYTHON", None)
    bash = shutil.which("bash")
    if not bash:
        pytest.skip("no bash on the path, so python.sh cannot be sourced here")
    return subprocess.run(
        [bash, "-c", '. "%s" && printf "%%s" "$PYTHON"' % RESOLVER],
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


# ---------------------------------------------------------------------------
# Which Python `specify` runs on, which is not the one `python.sh` resolves.
#
# The first run of this project by a stranger stopped at Spec Kit's catalog fetch with
# CERTIFICATE_VERIFY_FAILED. uv had installed specify-cli onto a python.org 3.12 that
# was already on the machine and whose certificate store had never been installed with
# it: `ssl.get_default_verify_paths()` gave `cafile=None`, while `curl` to the same
# address returned 200. Every cold run before it was on a machine with no Python at
# all, so uv always brought its own and nobody saw what happens otherwise.
# ---------------------------------------------------------------------------

PREFERENCE = 'export UV_PYTHON_PREFERENCE="only-managed"'


def test_the_tool_install_runs_on_a_python_uv_fetched():
    """The line that makes step 3 work on somebody else's Mac."""
    bang = (ROOT / "BANG.md").read_text(encoding="utf-8")
    step3 = bang.split("\n3. Install uv if missing", 1)[1].split("\n4. Node and pnpm", 1)[0]
    install = step3.index("uv tool install specify-cli")
    assert PREFERENCE in step3[:install], (
        "the uv tool install line does not carry UV_PYTHON_PREFERENCE, so uv will use "
        "whatever Python the machine has")


def test_every_place_that_carries_the_uv_set_carries_the_preference():
    """A `uv tool run` made without it is a run on the machine's own Python.

    The set is written out in BANG.md twice and in the launch agent's environment
    twice, and a call that carries four of the five gets the failure above with the
    receipt already printed.
    """
    bang = (ROOT / "BANG.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "write-launch-agent.sh").read_text(encoding="utf-8")

    # Every block that sets UV_TOOL_DIR is a block that runs a uv tool, and every one
    # of those needs the preference. The reverse does not hold: a block may set the
    # preference without the tool set, which is what step 7 does when it asks uv for a
    # Python to make the project's environment on and never touches a tool.
    for name, text in (("BANG.md", bang), ("write-launch-agent.sh", script)):
        # The assignment, not the word: the prose explains `UV_TOOL_DIR` in backticks
        # in a paragraph that sets nothing, and a paragraph cannot carry a preference.
        blocks = text.split('UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools"')[1:]
        assert blocks, "%s no longer carries the uv tool set at all" % name
        for number, block in enumerate(blocks, 1):
            # Within the same paragraph or exec line as the tool directory.
            near = block.split("\n\n")[0]
            if "uv tool uninstall" in near:
                # Undo. It removes a tool rather than running one, so there is no
                # interpreter to choose and an inert flag on a line a person types is
                # a thing for them to wonder about.
                continue
            assert "UV_PYTHON_PREFERENCE" in near, (
                "%s block %d runs a uv tool without the preference" % (name, number))


def test_the_receipt_reads_the_interpreter_and_refuses_the_machines_own():
    """`specify --version` cannot tell you this. The interpreter's path can.

    A version number prints the same on a Python that will fail at the first fetch as
    on one that will not, which is why the run that failed got a green receipt and
    stopped several minutes later with an error that says nothing about step 3.
    """
    bang = (ROOT / "BANG.md").read_text(encoding="utf-8")
    step3 = bang.split("\n3. Install uv if missing", 1)[1].split("\n4. Node and pnpm", 1)[0]
    assert 'uv tool run --from specify-cli python -c "import sys; print(sys.executable)"' in step3
    assert "must be a path under\n   `~/.potato-cannon/uv`" in step3 or \
        "a path under `~/.potato-cannon/uv`" in " ".join(step3.split()), (
        "the receipt does not require the interpreter to be uv's own")
    for wrong in ("/Library/Frameworks", "/opt/homebrew", ".pyenv"):
        assert wrong in step3, "the receipt does not name %s as a wrong answer" % wrong


def test_undo_removes_the_python_uv_fetched():
    """It lands under ~/.potato-cannon/uv/python, so `rm -rf ~/.potato-cannon` has it."""
    bang = (ROOT / "BANG.md").read_text(encoding="utf-8")
    undo = bang.split("## Undo, in full", 1)[1]
    assert "rm -rf ~/.potato-cannon" in undo
    assert "~/.potato-cannon/uv/python" in " ".join(undo.split()), (
        "Undo does not say where the Python uv fetched went")


def test_the_notes_name_the_certificate_error():
    notes = (ROOT / "RUN-NOTES.md").read_text(encoding="utf-8")
    flat = " ".join(notes.split())
    assert "CERTIFICATE_VERIFY_FAILED" in flat
    assert "Do not install certificates by hand" in flat, (
        "RUN-NOTES does not say what not to do about it")


def test_the_preference_is_not_imposed_on_the_projects_own_python():
    """`specify`'s interpreter and the project's are different things.

    `scripts/python.sh` resolves the Python that runs this project's own scripts, which
    on Windows is the one winget installed. UV_PYTHON_PREFERENCE is uv's, about uv's
    tools, and nothing in python.sh reads it or should.
    """
    resolver = RESOLVER.read_text(encoding="utf-8")
    assert "UV_PYTHON_PREFERENCE" not in resolver, (
        "python.sh reads uv's preference; the project's Python is not uv's business")
    assert "only-managed" not in resolver


# ---------------------------------------------------------------------------
# The project brings its own test runner.
#
# The Gate runs `$PYTHON -m pytest` and nothing installed pytest. Apple ships python3
# and does not ship pytest, so on every green run before 2026-09-28 the Build worker
# installed it onto the reader's machine, which is a build asking for an installation
# the page never promised. On 2026-09-28 a worker declined, correctly, and the Gate
# went red with "No module named pytest". The worker was right and the page was wrong.
# ---------------------------------------------------------------------------
VENV = "~/.potato-cannon/venv"


def test_python_sh_prefers_the_projects_own_interpreter():
    """The one with pytest in it, ahead of anything on the path."""
    resolver = RESOLVER.read_text(encoding="utf-8")
    assert "project_python()" in resolver, "python.sh has no project interpreter"
    assert '"$venv/bin/python" "$venv/Scripts/python.exe"' in resolver, (
        "python.sh does not look in both layouts; Windows puts it under Scripts")
    # Before the search, not after it.
    assert resolver.index("project_python && return 0") < resolver.index(
        'for candidate in python3 python'), (
        "python.sh searches the machine before looking at the project's own")


def test_python_sh_still_falls_back_when_there_is_no_project_interpreter():
    """A checkout somebody is poking at by hand, before step 7 or after Undo."""
    resolver = RESOLVER.read_text(encoding="utf-8")
    assert "for candidate in python3 python; do" in resolver, (
        "the fallback search is gone, so a bare checkout resolves nothing")


def test_the_step_that_makes_it_has_a_receipt_that_reads_the_interpreter():
    bang = (ROOT / "BANG.md").read_text(encoding="utf-8")
    step = bang.split("\n7. The project's own Python", 1)[1].split("\n8. ", 1)[0]
    assert 'uv venv --python 3.12 ~/.potato-cannon/venv' in step
    assert "-m pip install pytest" in step
    assert '. scripts/python.sh && echo "$PYTHON"' in step, (
        "the receipt does not print the interpreter it resolved")
    assert '"$PYTHON" -m pytest --version' in step, (
        "the receipt does not prove pytest is in it")
    assert VENV in step


def test_the_test_tier_names_no_interpreter_but_the_resolved_one():
    """`$PYTHON` and nothing else, so the environment step 7 makes is the one used."""
    conf = (ROOT / "scripts" / "gate.conf").read_text(encoding="utf-8")
    command = [l for l in conf.splitlines() if l.startswith("TEST_COMMAND=")]
    assert len(command) == 1, "gate.conf has %d TEST_COMMAND lines" % len(command)
    assert command[0] == 'TEST_COMMAND="$PYTHON -m pytest -q --junitxml=test-results.xml"', (
        "the test tier names an interpreter of its own: %s" % command[0])


def test_the_environment_is_in_the_places_list_and_undo_removes_it():
    bang = (ROOT / "BANG.md").read_text(encoding="utf-8")
    places = bang.split("## What this fetches", 1)[0]
    assert VENV in places, "the places list does not name the project's environment"
    undo = " ".join(bang.split("## Undo, in full", 1)[1].split())
    assert "rm -rf ~/.potato-cannon" in undo
    assert "`~/.potato-cannon/venv`, goes with" in undo, (
        "Undo does not say the environment goes with it")


def test_the_worker_is_told_not_to_install_a_tool_the_checks_need():
    """Skully's worker had to infer this. It is in words now."""
    build = " ".join((ROOT / "cannon-template" / "agents" / "build.md")
                     .read_text(encoding="utf-8").split())
    assert "Do not install it and do not copy it in." in build
    assert "not a test runner" in build, (
        "the rule names the checker but not the test runner, which is the one that bit")


def test_the_notes_carry_the_xcode_licence_stop():
    notes = " ".join((ROOT / "RUN-NOTES.md").read_text(encoding="utf-8").split())
    assert "You have not agreed to the Xcode license agreements" in notes
    assert "sudo xcodebuild -license accept" in notes
    assert "It has nothing to do with Python" in notes, (
        "the note does not say it is unrelated to the Python stop below it")
