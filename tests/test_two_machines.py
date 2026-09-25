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
