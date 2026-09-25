"""The pairs of places that have to agree once BANG.md runs on two machines.

Every one of these is two copies of one fact, written down twice because a reader
needs it in both places. Two copies of anything drift, and each of these drifts
silently: nothing fails, nothing is red, and the person finds out by pasting a line
that does not work or by running an Undo that leaves something behind.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
BANG = (ROOT / "BANG.md").read_text(encoding="utf-8")
SCRIPT = (ROOT / "scripts" / "write-launch-agent.sh").read_text(encoding="utf-8")


def _run_it_sections():
    """The Run it section split into its two machines: {"Mac": text, "Windows": text}."""
    run_it = README.split("\n## Run it\n", 1)[1].split("\n## ", 1)[0]
    out = {}
    for name, body in re.findall(r"\n### On (a Mac|Windows)\n(.*?)(?=\n### |\Z)", run_it, re.S):
        out["Mac" if name == "a Mac" else "Windows"] = body
    return out


def _last_line_of_block_two(section):
    """The command the reader's last paste is, out of that machine's second block."""
    blocks = re.findall(r"\n```\n(.*?)\n```", section, re.S)
    assert blocks, "this machine has no pasteable block at all"
    return blocks[-1].strip().splitlines()[-1]


def test_both_machines_start_claude_code_with_the_same_line():
    """The opening line is the instruction. It is the same instruction on both.

    It names the file to read, the order to read it in, and what to do when a receipt
    does not match, and it is the only thing standing between a reader and an agent
    that improvises. A Windows copy that drifts by a word is a second instruction
    nobody decided to write.
    """
    sections = _run_it_sections()
    assert set(sections) == {"Mac", "Windows"}, (
        "README's Run it no longer has one section per machine: %s" % sorted(sections))
    lines = {name: _last_line_of_block_two(body) for name, body in sections.items()}
    for name, line in lines.items():
        assert line.startswith("claude --permission-mode manual "), (
            "%s's block 2 does not end by starting Claude Code: %r" % (name, line))
    assert lines["Mac"] == lines["Windows"], (
        "the two blocks start Claude Code differently.\nMac:     %s\nWindows: %s"
        % (lines["Mac"], lines["Windows"]))


def test_both_machines_are_told_the_trust_prompt_is_not_the_default():
    """Said twice because it is read once, in whichever section the reader is in.

    The prompt comes after a screen that looks like the end of the setup, and no is the
    default. A reader who presses return at it has said no to the folder they cloned
    thirty seconds earlier.
    """
    trust = '"Yes, I trust this folder"; yes is not the default, so pick it.'
    for name, body in _run_it_sections().items():
        assert trust in body, "%s's section does not carry the trust-prompt line" % name


def test_the_page_still_says_which_machines_it_runs_on():
    assert "Mac and Windows." in README, "README no longer says which machines it runs on"
    assert "Mac only" not in README, "README still says Mac only"


def test_undo_removes_the_task_the_script_registers_by_the_name_it_registers_it_under():
    """BANG.md's Undo names the logon task; the script names it when it creates it.

    These two are the pair with the quietest failure in this file. If they drift, Undo
    runs, prints nothing wrong, and leaves a task behind that starts a daemon at every
    logon on a machine the person believes they have cleaned.
    """
    registered = re.search(r'^TASK="([^"]+)"', SCRIPT, re.M)
    assert registered, "write-launch-agent.sh no longer has a TASK= line"
    name = registered.group(1)
    assert 'schtasks //Create //TN "$TASK"' in SCRIPT, (
        "the script no longer registers the task under $TASK")
    undo = BANG.split("## Undo, in full", 1)[1]
    assert 'schtasks //Delete //TN "%s"' % name in undo, (
        "Undo does not remove the task the script registers, which is %r" % name)


def test_bang_names_the_daemon_script_the_script_actually_writes():
    """The places list promises one file; the script writes one file."""
    written = re.search(r'^DAEMON_SH="([^"]+)"', SCRIPT, re.M)
    assert written, "write-launch-agent.sh no longer has a DAEMON_SH= line"
    path = written.group(1).replace("$HOME/", "~/")
    assert path in BANG, (
        "BANG.md does not list %s, which the script writes on Windows" % path)


def test_the_windows_node_path_has_no_bin_in_either_place():
    """Where node.exe is, said in BANG.md step 4 and used in the daemon's own command.

    The Mac build has a bin and the Windows build does not. A path line carrying the
    Mac's shape on Windows finds no node at all, and the daemon would fail to start
    with the same message as a daemon that was never installed.
    """
    assert 'export PATH="$HOME/.potato-cannon/node:$PATH"' in BANG, (
        "BANG.md step 4 no longer gives the Windows path line")
    win = re.search(r"^EXEC_LINE_WIN='(.*)'$", SCRIPT, re.M)
    assert win, "write-launch-agent.sh no longer has an EXEC_LINE_WIN"
    assert '$HOME/.potato-cannon/node:' in win.group(1), (
        "the Windows daemon command does not put ~/.potato-cannon/node on the path")
    assert '$HOME/.potato-cannon/node/bin' not in win.group(1), (
        "the Windows daemon command carries the Mac's node/bin, where nothing lives")


def test_the_windows_daemon_command_is_still_one_line():
    """The whole reason this script exists, now twice over.

    A plist keeps every newline in a <string>, and a task runs a file: both of them
    take a broken command and start nothing, with no message that says why.
    """
    for name in ("EXEC_LINE", "EXEC_LINE_WIN"):
        found = re.search(r"^%s='(.*)'$" % name, SCRIPT, re.M)
        assert found, "%s is no longer one quoted line in the script" % name
        assert "\n" not in found.group(1)


def test_the_pin_is_the_same_in_both_of_bangs_two_places():
    """The fork commit, in the fetch list and in step 7's receipt.

    The receipt's whole job is to say the clone is at the commit this file pinned, and
    it can only say that while the two lines agree. They are forty characters each, for
    the reason step 7 gives: a seven-character comparison is a weaker claim than the one
    being made, and forty characters are forty chances to fix one place and not the
    other.
    """
    pins = re.findall(r"\b[0-9a-f]{40}\b", BANG)
    assert len(pins) == 2, "BANG.md carries %d full SHAs; the pin is two places" % len(pins)
    assert pins[0] == pins[1], "the two pins differ: %s and %s" % tuple(pins)

    fetches = BANG.split("## What this fetches from the network", 1)[1].split("\n## ", 1)[0]
    step_seven = BANG.split("\n7. Potato Cannon.", 1)[1].split("\n8. ", 1)[0]
    assert pins[0] in fetches, "the fetch list does not name the pin"
    assert pins[0] in step_seven, "step 7's receipt does not name the pin"


def test_no_windows_paste_joins_the_path_line_to_another_command():
    """One paste, one command's worth, for the two that cannot survive being joined.

    On the Dell the path line and the `git clone` under it were read as one thing and
    the path line never ran. In the file they were already in separate fenced blocks,
    two paragraphs apart, so the joining happened in the reading and not in the
    markdown: the line above the path line starts an installer, and anything pasted
    after it while it is still running goes to the installer instead of to PowerShell.

    A block holding one command cannot be pasted half-run. This is that, checked.
    """
    windows = _run_it_sections()["Windows"]
    blocks = re.findall(r"\n```\n(.*?)\n```", windows, re.S)
    assert blocks, "the Windows section has no pasteable block"

    path_blocks = [b for b in blocks if "SetEnvironmentVariable" in b]
    assert len(path_blocks) == 1, "the path line is in %d blocks" % len(path_blocks)
    assert path_blocks[0].strip().count("\n") == 0, (
        "the path line shares its block with another command:\n%s" % path_blocks[0])

    for block in blocks:
        joined = [name for name in ("git clone", "install.ps1") if name in block]
        assert not (joined and "SetEnvironmentVariable" in block), (
            "the path line is in one block with %s" % ", ".join(joined))

    installer = [b for b in blocks if "install.ps1" in b]
    assert len(installer) == 1 and installer[0].strip().count("\n") == 0, (
        "the Claude Code installer shares its block, and a line pasted while it runs "
        "goes to the installer")


def test_block_one_ends_by_sending_the_reader_to_a_new_window():
    """Windows reads the user path when a window opens and never again.

    The path line is the last thing block 1 writes and it does nothing in the window it
    was typed in. A reader who goes straight on gets a `claude` that is not found, in a
    window that was right to not find it.
    """
    windows = _run_it_sections()["Windows"]
    block_one = windows.split("Block 2,", 1)[0]
    assert "close this window and open a new powershell" in block_one.lower(), (
        "block 1 does not end by telling the reader to open a new window")
    assert block_one.index("SetEnvironmentVariable") < block_one.lower().index(
        "close this window and open a new powershell"), (
        "the reopen comes before the path line it exists for")


def test_block_two_differs_between_the_machines_in_the_home_folder_and_nothing_else():
    """The whole of block 2, compared line for line, with one substitution allowed.

    The Mac writes the project's folder `~/bang` and Windows writes `$HOME\\bang`,
    because Git Bash expands the tilde and git does not: `git clone` on Windows takes
    `~/bang` as a literal folder name and stops with "could not create leading
    directories of '~/bang': Permission denied", which reads like a permissions
    problem and is a spelling one.

    That is the only difference either block is allowed. Everything else in the two is
    one instruction written twice, and the opening line especially: it is the only
    thing standing between a reader and an agent that improvises.
    """
    sections = _run_it_sections()
    blocks = {}
    for name, body in sections.items():
        found = re.findall(r"\n```\n(.*?)\n```", body, re.S)
        assert found, "%s has no pasteable block" % name
        blocks[name] = found[-1].strip().splitlines()

    mac, windows = blocks["Mac"], blocks["Windows"]
    assert len(mac) == len(windows), (
        "the two block 2s are different lengths.\nMac:     %s\nWindows: %s" % (mac, windows))

    # The one allowed difference, written once and applied to every line.
    normalised = [line.replace("$HOME\\bang", "~/bang") for line in windows]
    for number, (m, w) in enumerate(zip(mac, normalised), 1):
        assert m == w, (
            "block 2 line %d differs by more than the home folder.\n"
            "Mac:     %s\nWindows: %s" % (number, m, blocks["Windows"][number - 1]))

    # And the substitution is really used, so this test cannot pass by the two blocks
    # having quietly become identical again on a tilde that does not work.
    assert any("$HOME\\bang" in line for line in windows), (
        "the Windows block no longer uses $HOME, and git on Windows does not expand ~")
    assert not any("~/bang" in line for line in windows), (
        "the Windows block still carries a tilde path, which git will not expand")


def _eaddrinuse_receipt(tmp_path, log):
    """Run write-launch-agent.sh's own EADDRINUSE lines, lifted out of the script.

    Lifted rather than restated: a copy of the two lines in this file would go on
    passing after somebody changed the script, which is the failure this is for.
    """
    import subprocess
    home = tmp_path / "home"
    (home / ".potato-cannon").mkdir(parents=True)
    if log is not None:
        (home / ".potato-cannon" / "daemon.log").write_text(log, encoding="utf-8")

    text = (ROOT / "scripts" / "write-launch-agent.sh").read_text(encoding="utf-8")
    lifted = re.search(
        r'^\s*(EADDRINUSE="\$\(grep -c EADDRINUSE.*?\n\s*\[ -n "\$EADDRINUSE" \].*?)$',
        text, re.S | re.M)
    assert lifted, "the EADDRINUSE lines are no longer in the shape this test lifts"
    script = "\n".join(line.strip() for line in lifted.group(1).splitlines())
    script += '\necho "  EADDRINUSE lines in daemon.log: $EADDRINUSE"'
    out = subprocess.run(
        ["/bin/bash", "-c", script], capture_output=True, text=True,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"})
    return out.stdout.rstrip("\n")


def test_the_eaddrinuse_receipt_prints_one_number_on_a_clean_run(tmp_path):
    """It printed "0 0" on exactly the run it was written for.

    `grep -c` prints 0 and exits 1 when nothing matches, so the `|| echo 0` that used
    to close the line fired on every clean run and appended a second 0. A receipt that
    is wrong when everything is right is worse than no receipt: the one line a reader
    checks to see that nothing went wrong is itself the thing that looks wrong.
    """
    assert _eaddrinuse_receipt(tmp_path, "started\nlistening on 3131\n") == (
        "  EADDRINUSE lines in daemon.log: 0")


def test_it_still_counts_the_lines_when_there_are_some(tmp_path):
    log = "boot\nEADDRINUSE 3131\nretry\nEADDRINUSE 3131\n"
    assert _eaddrinuse_receipt(tmp_path, log) == (
        "  EADDRINUSE lines in daemon.log: 2")


def test_a_log_that_is_not_there_yet_counts_as_none(tmp_path):
    """The only case with no output at all, and the one the fallback is really for."""
    assert _eaddrinuse_receipt(tmp_path, None) == (
        "  EADDRINUSE lines in daemon.log: 0")
