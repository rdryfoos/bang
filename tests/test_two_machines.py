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
NOTES = (ROOT / "RUN-NOTES.md").read_text(encoding="utf-8")


def _flat(text):
    """The prose as one line, because these files are wrapped.

    A sentence that moved off the page and into RUN-NOTES.md was re-wrapped on the way,
    so a literal substring is asserting about where the line breaks fell rather than
    about what the file says.
    """
    return " ".join(text.split())


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


def test_the_trust_prompt_is_a_beat_on_both_machines_and_explained_once():
    """It was said twice, because Run it explained itself twice. Now it is said once.

    The prompt comes after a screen that looks like the end of the setup, and no is the
    default: a reader who presses return at it has said no to the folder they cloned
    thirty seconds earlier. So the beat is on the page, where a reader with a terminal
    open will see it, and the reason it matters is in RUN-NOTES.md, which is where the
    sentence went when Run it became pastes and beats.
    """
    beat = "Say yes when it asks whether you trust this folder."
    for name, body in _run_it_sections().items():
        assert beat in body, "%s has no trust-prompt beat" % name

    why = '"Yes, I trust this folder"; yes is not the default, so pick it.'
    assert why in _flat(NOTES), "RUN-NOTES.md no longer says why that beat is there"
    assert why not in _flat(README), (
        "the explanation is back on the page; Run it is pastes and beats")


def test_the_page_still_says_which_machines_it_runs_on():
    """It said so in a standalone line above the blocks, which was a third copy.

    The first line says it, and Run it has a section per machine. The line that sat
    between them saying "Mac and Windows." was a sentence of explanation, and Run it
    has none now.
    """
    assert "### On a Mac" in README and "### On Windows" in README, (
        "Run it no longer has one section per machine")
    assert "Mac or Windows" in README.strip().splitlines()[0], (
        "the first line no longer names the machines")
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
    assert "Register-ScheduledTask -TaskName $env:BANG_TASK" in SCRIPT, (
        "the script no longer registers the task under $TASK")
    assert 'export BANG_TASK="$TASK"' in SCRIPT, (
        "$BANG_TASK is what the PowerShell block reads; it must come from $TASK")
    undo = BANG.split("## Undo, in full", 1)[1]
    assert 'schtasks //Delete //TN "%s"' % name in undo, (
        "Undo does not remove the task the script registers, which is %r" % name)


def test_undo_removes_the_startup_launcher_the_script_falls_back_to():
    """The second route, and the one with no record of itself.

    A scheduled task can be asked about afterwards; a file in the Startup folder
    cannot. If its name here and its name in Undo drift, Undo runs, prints nothing
    wrong, and leaves something starting a daemon at every logon on a machine the
    person believes they have cleaned. That is the same failure the task pair has and
    it is quieter, because nothing will ever list it.
    """
    written = re.search(r'^STARTUP_CMD="([^"]+)"', SCRIPT, re.M)
    assert written, "write-launch-agent.sh no longer has a STARTUP_CMD= line"
    name = written.group(1)
    assert '"$STARTUP/$STARTUP_CMD"' in SCRIPT, (
        "the script no longer writes the launcher under $STARTUP_CMD")
    undo = BANG.split("## Undo, in full", 1)[1]
    assert name in undo, "Undo does not remove %r" % name
    assert name in BANG.split("## What this fetches", 1)[0], (
        "the places list does not name %r, which this file writes" % name)


def test_the_script_says_which_of_the_two_routes_it_used():
    """Undo cannot remove the right one unless the run said which it was."""
    assert 'REGISTERED="task"' in SCRIPT and 'REGISTERED="startup"' in SCRIPT, (
        "the script no longer records which route took")
    assert 'say "started the daemon by the $REGISTERED route"' in SCRIPT, (
        "the script no longer prints which route it used")


def test_what_to_do_when_claude_code_refuses_a_command_is_written_down_once():
    """It was on the page twice, once per machine. It is in RUN-NOTES.md now, once.

    Zebra met this on a Mac on 2026-09-23 and the Dell met it on 2026-09-25, and
    between the two nothing had been written down, so the second reader worked it out
    again. It is not a Windows thing and it is not rare: the session refuses a script
    it installed a moment earlier, because it has no history with it. Which is why it
    is checked here rather than left to whoever next moves a paragraph.
    """
    line = "Type `!` at its prompt followed by that line, exactly as printed"
    assert line in _flat(NOTES), "RUN-NOTES.md no longer says what to do with a refusal"
    assert "do not switch to auto mode" in _flat(NOTES)
    assert "as untrusted" in BANG, "BANG.md no longer covers the refusal either"


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


def test_the_reopens_are_beats_of_their_own_and_sit_after_what_they_are_for():
    """Windows reads the user path when a window opens and never again.

    Each reopen exists because of the paste above it, and a reader who goes straight on
    gets a command that is not found in a window that was right not to find it. They
    are numbered beats now rather than sentences after a fence, which is the whole
    shape of this page: one thing to do per number.
    """
    windows = _run_it_sections()["Windows"]
    reopens = [line for line in windows.splitlines()
               if re.match(r"^\d+\. Close this window and open", line)]
    assert len(reopens) == 2, (
        "Windows should reopen twice, after git and after the path line: %s" % reopens)
    assert "PowerShell" in reopens[1], (
        "the second reopen does not name PowerShell. Claude Code's own shell on Windows "
        "is Git Bash whatever window launched it, so the launching window only has to "
        "be one that can see the path, and beat 7 is PowerShell syntax.")

    # And the second one comes after the path line it exists for.
    assert windows.index("SetEnvironmentVariable") < windows.index(reopens[1]), (
        "the reopen comes before the path line it exists for")

    mac = _run_it_sections()["Mac"]
    assert any(re.match(r"^\d+\. Close this window and open a new Terminal", line)
               for line in mac.splitlines()), "the Mac has no reopen beat"


def test_block_two_differs_between_the_machines_in_the_home_folder_and_nothing_else():
    """The whole of block 2, compared line for line, with one substitution allowed.

    The Mac writes the project's folder `~/bang` and Windows writes `$HOME\\bang`.
    On the Dell, `git clone` with `~/bang` stopped with "could not create leading
    directories of '~/bang': Permission denied", which reads like a permissions
    problem and is a spelling one: git was handed a tilde and made a folder named for
    it. `$HOME` is expanded before git sees it, in either shell.

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


def test_nothing_states_a_count_of_the_places_this_file_writes_to():
    """The list grows; a number written beside it does not.

    It said "five places" in three sentences across two files, and the list became six
    when uv's Windows receipt was added to it. A count is a copy of the list, kept in
    prose, which nobody updates because nobody is looking at the list when they write
    the sentence. The list is the record; the sentences point at it.
    """
    # Only a count of *this* list. "three places this file never told you about",
    # naming ~/.cache, ~/Library/pnpm and ~/.npm, is a count of somewhere else and is
    # the sentence that makes the point, so it is not one of these.
    numbered = re.compile(
        r"\b(two|three|four|five|six|seven|eight|nine|ten|\d+)\s+places\b"
        r"(?=\s+(above|in your home)\b)", re.I)
    offenders = {}
    for name, text in (("BANG.md", BANG), ("README.md", README)):
        for number, line in enumerate(text.splitlines(), 1):
            if numbered.search(line):
                offenders.setdefault(name, []).append("%d: %s" % (number, line.strip()))
    assert not offenders, (
        "a count of the places is a second copy of the list: %s" % offenders)


def test_nothing_still_calls_bang_one_command():
    """It has been two pastes since the README grew two blocks, and three on Windows.

    The sentence outlived the thing it described because it is the first line, which
    is the line nobody re-reads. It is also the line the Sites page is to take its own
    first sentence from, so a false one here would have become a false one in public.
    """
    claim = re.compile(r"\bone command\b", re.I)
    offenders = {}
    for name, text in (("README.md", README), ("BANG.md", BANG)):
        for number, line in enumerate(text.splitlines(), 1):
            if claim.search(line):
                offenders.setdefault(name, []).append("%d: %s" % (number, line.strip()))
    assert not offenders, (
        "Bang is not one command and has not been since block 2: %s" % offenders)


def test_the_readmes_first_line_and_its_run_it_section_agree_about_the_machines():
    """The first line names the machines; Run it is where a reader acts on that.

    Two sentences about the same fact, forty lines apart, and the first is the one
    quoted elsewhere. If a third machine lands in one and not the other, the page
    promises what its own instructions do not carry.
    """
    first = README.strip().splitlines()
    opening = " ".join(first[:5])
    assert "Mac or Windows" in opening, "the first line no longer names the machines"
    assert "### On a Mac" in README and "### On Windows" in README, (
        "Run it no longer has one section per machine")
    # Linux is named as coming, and nowhere claimed as working.
    assert "Omarchy Linux soon" in opening
    assert "Linux is not supported yet" in BANG, (
        "BANG.md no longer says Linux is not supported, while the page says soon")


def test_run_it_is_pastes_and_beats_and_carries_no_explanation():
    """The shape of the page, which is the whole of what it is for.

    Run it is read with a terminal open beside it, which means it is scanned and not
    read. Every sentence between the fences was a sentence somebody had to skip past
    to find the next thing to paste, and every one of them is now in RUN-NOTES.md,
    where a reader who wants it goes on purpose.

    So a line in Run it is one of four things: a heading, a numbered beat, a fence or
    what is inside one, or the one line that links the notes. Anything else is prose
    that has crept back, and prose creeps back a sentence at a time.
    """
    run_it = README.split("\n## Run it\n", 1)[1].split("\n## ", 1)[0]

    stray, in_fence = [], False
    for number, line in enumerate(run_it.splitlines(), 1):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip():
            continue
        if line.startswith("#"):
            continue
        if re.match(r"^\d+\. ", line):
            continue
        if "RUN-NOTES.md" in line or line.startswith("prompts mean"):
            continue
        stray.append("%d: %s" % (number, line.strip()))
    assert not stray, (
        "Run it has prose in it again; it belongs in RUN-NOTES.md:\n%s" % "\n".join(stray))


def test_every_beat_is_one_line_and_every_fence_has_a_beat_over_it():
    """One thing to do per number, and no fence a reader meets unannounced."""
    for name, body in _run_it_sections().items():
        lines = body.splitlines()
        beats = [(i, l) for i, l in enumerate(lines) if re.match(r"^\d+\. ", l)]
        assert beats, "%s has no beats" % name

        # The numbers run 1..n with nothing missing, so a reader can follow them.
        numbers = [int(l.split(".", 1)[0]) for _, l in beats]
        assert numbers == list(range(1, len(numbers) + 1)), (
            "%s's beats are numbered %s" % (name, numbers))

        # A beat is one line: the line after it is blank, a fence, or the next beat.
        for i, beat in beats:
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            assert nxt == "" or nxt.startswith("```"), (
                "%s's beat %r runs on into %r" % (name, beat, nxt))

        # Every fence that opens a block opens under a beat, so a reader never meets
        # a paste without having been told what it is for. Tracked with a toggle: the
        # line above a closing fence is the last line of the paste, not a beat.
        opening = True
        for i, line in enumerate(lines):
            if not line.startswith("```"):
                continue
            if opening:
                above = [l for l in lines[:i] if l.strip()]
                assert above and re.match(r"^\d+\. ", above[-1]), (
                    "%s has a paste under %r, which is not a beat" % (name, above[-1:]))
            opening = not opening
        assert opening, "%s has an unclosed fence" % name


def test_the_notes_are_linked_from_run_it_exactly_once():
    """Once, because a page of beats with a link on every beat is a page of prose."""
    run_it = README.split("\n## Run it\n", 1)[1].split("\n## ", 1)[0]
    assert run_it.count("RUN-NOTES.md") == 1, (
        "Run it links the notes %d times" % run_it.count("RUN-NOTES.md"))
    assert (ROOT / "RUN-NOTES.md").exists()


def test_the_notes_say_which_file_they_are_not():
    """RUN-NOTES.md and RUNS.md are one letter and a hyphen apart.

    One is what to read before you paste; the other is the log of who ran it and what
    happened. A reader who opens the wrong one finds a list of other people's runs
    where they expected the instructions.
    """
    assert "RUNS.md" in _flat(NOTES), "RUN-NOTES.md does not say what RUNS.md is"


def test_bang_names_the_paste_that_starts_it_the_way_the_page_numbers_it():
    """BANG.md's first sentence points at the page, and the page was renumbered.

    It said "block 2", which was true while Run it had two blocks. Run it has beats
    now, and a reader sent to a block they cannot find on the page is a reader who
    starts by doubting the file.
    """
    opening = _flat(BANG.split("## What this writes", 1)[0])
    assert "block 2" not in opening, "BANG.md still sends the reader to a block"
    assert "beat 3 on a Mac, beat 7 on Windows" in opening, (
        "BANG.md does not name the beat that starts it")

    # And those two beats are the ones that actually start Claude Code.
    for name, beat in (("Mac", 3), ("Windows", 7)):
        body = _run_it_sections()[name]
        lines = body.splitlines()
        where = next(i for i, l in enumerate(lines) if l.startswith("%d. " % beat))
        block = "\n".join(lines[where:where + 8])
        assert "claude --permission-mode manual" in block, (
            "%s's beat %d is not the one that starts Claude Code" % (name, beat))
