#!/usr/bin/env bash
# write-launch-agent: install the thing that keeps the Cannon daemon running, on
# whichever of the three machines this is.
#
# This used to be a plist printed in BANG.md for the reader to copy. It could not be
# copied. The daemon's command is one long shell line, and a plist typeset to fit a
# page breaks it across nine lines; a <string> keeps every newline it is given, so
# what landed on disk was a command with newlines in the middle of it and a daemon
# that never started. The reader's receipt was a failing /health with nothing to say
# why. A file the repository ships cannot be mis-copied, so the plist lives here.
#
# What it writes. On a Mac, ~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist and
# nothing else; it writes beside the target first and moves the file into place once
# plutil has read it, so a plist that does not parse never becomes the installed one.
# On Windows, ~/.potato-cannon/cannon-daemon.sh and nothing else, checked with
# `bash -n` before anything is registered, and then a Task Scheduler task at logon
# named "Bang Potato Cannon" that runs it. The task is the one thing either branch
# leaves outside the home folder, and BANG.md's Undo removes it by name. On Linux,
# the same ~/.potato-cannon/cannon-daemon.sh, checked with `bash -n`, and a systemd
# user unit, ~/.config/systemd/user/bang-potato-cannon.service, that runs it; the unit
# is checked with `systemd-analyze --user verify` before it is enabled.
#
# Two things the reader could not have got right by hand, and the reasons:
#
#   1. StandardOutPath and StandardErrorPath are real paths with the real home folder
#      in them. A plist does not expand ~ or $HOME in a path, so $HOME is substituted
#      here, while every $HOME inside the command string is left alone: that one is
#      inside a shell command and is expanded when the daemon starts. Windows has no
#      equivalent of those two keys on a logon task, so the daemon script redirects
#      itself to the same daemon.log on its first line.
#   2. The daemon is run directly rather than through the Cannon's own start command,
#      which passes --daemon, detaches and exits. Nothing can supervise a process that
#      has already gone, so KeepAlive would restart a thing that exits every time.
#   3. The path names ~/.potato-cannon/node first, which is where BANG.md step 4
#      puts Node 22, so the daemon runs on the Node it was built against and not on
#      whatever the person happens to have. It is ~/.potato-cannon/node/bin on a Mac
#      and ~/.potato-cannon/node on Windows, because the Windows build puts node.exe
#      at the top of the folder where the Mac build has a bin. COREPACK_HOME,
#      PNPM_HOME and npm_config_cache are set for the same reason the path is:
#      anything the daemon or a worker under it downloads lands in ~/.potato-cannon,
#      which is one of the places BANG.md says this project writes to, and Undo
#      removes it whole. The five UV_* are there for the same reason and for one
#      more: a tool installed under one UV_TOOL_DIR is invisible to a call made
#      without it, so a worker running specify has to carry the same five BANG.md
#      step 3 installed with or be told the thing is not there. UV_PYTHON_PREFERENCE
#      is the fifth: without it a `uv tool run` here picks whatever Python the machine
#      has, and on 2026-09-28 a stranger's Mac had one whose certificate store had
#      never been installed.
#
# What the two branches do not share, and a reader should know it before leaning on
# the Windows one: launchd's KeepAlive starts the daemon again when it dies, and a
# logon task has nothing like it. On Windows a daemon that dies stays dead until the
# next logon or until somebody runs `schtasks /Run` by hand. Linux has it back:
# Restart=always in the unit is systemd's KeepAlive, with the same thirty seconds.
#
# Why the unit runs a file rather than carrying the command itself. systemd expands
# $VAR and %x in ExecStart before any shell sees the line, and the daemon's command is
# full of both. Escaping them would make a third spelling of one command; a file that
# holds it is the defence Windows already uses, so Linux uses the same file.
#
# Before it writes anything it checks the port. A daemon that is already listening is
# somebody else's, and every receipt after step 8 would be about their board rather than
# yours: on the sixth cold run a previous test user's daemon answered /health with nine
# and a half hours of uptime, and the run was right to stop.
#
# Usage:  bash scripts/write-launch-agent.sh
#         bash scripts/write-launch-agent.sh --dry-run    print it, write nothing
#
# Written by the born-threaded practice; MIT.
set -uo pipefail

LABEL="com.dryfoos.bang.cannon"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
TASK="Bang Potato Cannon"
DAEMON_SH="$HOME/.potato-cannon/cannon-daemon.sh"
# The Startup-folder fallback's launcher, named so Undo can find it without guessing.
STARTUP_CMD="bang-potato-cannon.cmd"
STARTUP_CMD_TMP="$HOME/.potato-cannon/$STARTUP_CMD.new"
# Linux's systemd user unit, named the way the Windows pair is so Undo can find it.
UNIT="bang-potato-cannon.service"
UNIT_FILE="$HOME/.config/systemd/user/$UNIT"
PORT="3131"
HEALTH="http://127.0.0.1:$PORT/health"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

# The PowerShell blocks below are single-quoted so that Git Bash hands them over
# unmangled, which means they cannot carry a shell variable. They read these instead.
export BANG_TASK="$TASK"
export BANG_SH="$DAEMON_SH"

say() { printf '  %s\n' "$*"; }
stop() { printf 'write-launch-agent: STOPPED. %s\n' "$*" >&2; exit 1; }

# Which machine this is, read the same way BANG.md step 2 reads it.
case "$(uname -s)" in
  Darwin)            MACHINE=mac ;;
  MINGW*|MSYS*)      MACHINE=windows ;;
  Linux)             MACHINE=linux ;;
  *)                 stop "this script knows a Mac, Windows and Linux, and \`uname -s\` said $(uname -s)." ;;
esac

# Who is listening on the daemon's port, if anybody. One line per listener, with the
# command and the user that owns it, because "a daemon answered" and "our daemon
# answered" are different facts and only the second one is a receipt.
#
# Two ways to ask, because the machines answer to different tools. lsof gives the
# command and the user in one line. Get-NetTCPConnection gives the listening socket
# and the process id that holds it, and nothing about whose process that is, so the
# id is taken to Win32_Process for the name and to its GetOwner for the user. That
# last part is why this asks CIM rather than `Get-Process -IncludeUserName`, which
# wants to be run as an administrator and this step never is.
#
# -ExecutionPolicy ByPass is here for the same reason BANG.md steps 3 and 4 carry it,
# and with less certainty that it is needed: NetTCPIP is a CDXML module and CimCmdlets
# is a binary one, so neither should be refused by the default Restricted policy the
# way a script module is. It costs one flag on a process that lives for a second and
# writes nothing, and the alternative is a cold user stopped at step 8 by a message
# about policy, so it is carried rather than argued about.
listener_on_3131() {
  if [ "$MACHINE" = mac ]; then
    lsof -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | tail -n +2
    return
  fi
  # Linux asks ss, because lsof is not installed everywhere (Omarchy has none) and
  # ss comes with iproute2, which is. ss names the process and its id but not its
  # user, so the id goes to ps for that. A listener owned by another account shows
  # no process at all to a plain user, and that is said rather than left blank: an
  # empty line here would read as "nothing is listening", which is the opposite.
  if [ "$MACHINE" = linux ]; then
    ss -ltnpH "sport = :$PORT" 2>/dev/null | while read -r _ _ _ local _ procs; do
      pid="$(printf '%s' "$procs" | sed -n 's/.*pid=\([0-9]*\).*/\1/p')"
      if [ -n "$pid" ]; then
        printf '%s  pid %s  owner %s\n' "$(ps -o comm= -p "$pid")" "$pid" "$(ps -o user= -p "$pid")"
      else
        printf '%s  (a process this account cannot see: another user'"'"'s)\n' "$local"
      fi
    done
    return
  fi
  POTATO_PORT="$PORT" powershell -NoProfile -ExecutionPolicy ByPass -c '
    Get-NetTCPConnection -LocalPort ([int]$env:POTATO_PORT) -State Listen -ErrorAction SilentlyContinue |
      ForEach-Object {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId = $($_.OwningProcess)"
        "{0}  pid {1}  owner {2}" -f $p.Name, $p.ProcessId, (Invoke-CimMethod -InputObject $p -MethodName GetOwner).User
      }' 2>/dev/null | tr -d '\r' | sed '/^[[:space:]]*$/d'
}

# The command the daemon runs, on one line and staying on one line. Keeping it in a
# variable rather than inside the plist text is what makes the promise checkable: one
# line here is one line in the file, and the check below says so before anything is
# installed.
EXEC_LINE='cd "$HOME/.potato-cannon/app" &amp;&amp; exec env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" SHELL="$SHELL" TMPDIR="${TMPDIR:-/tmp}" LANG="en_US.UTF-8" PATH="$HOME/.potato-cannon/node/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" COREPACK_HOME="$HOME/.potato-cannon/corepack" PNPM_HOME="$HOME/.potato-cannon/pnpm" npm_config_cache="$HOME/.potato-cannon/npm-cache" UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools" UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache" UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python" UV_TOOL_BIN_DIR="$HOME/.local/bin" UV_PYTHON_PREFERENCE="only-managed" GIT_AUTHOR_NAME="Bang Worker" GIT_AUTHOR_EMAIL="bang-worker@localhost" GIT_COMMITTER_NAME="Bang Worker" GIT_COMMITTER_EMAIL="bang-worker@localhost" POTATO_DAEMON_HOST="127.0.0.1" POTATO_DAEMON_PORT="3131" node ./apps/daemon/dist/server/server.js'

# The same command for Windows, and the differences are all forced. `env -i` is gone:
# it would empty the environment a native node.exe needs to start at all, SystemRoot
# and TEMP among it, so the variables are exported over what is there instead. The
# path names ~/.potato-cannon/node without the bin. And the ampersands are ampersands,
# because this one goes into a shell script rather than into XML.
EXEC_LINE_WIN='cd "$HOME/.potato-cannon/app" && export PATH="$HOME/.potato-cannon/node:$HOME/.local/bin:$PATH" COREPACK_HOME="$HOME/.potato-cannon/corepack" PNPM_HOME="$HOME/.potato-cannon/pnpm" npm_config_cache="$HOME/.potato-cannon/npm-cache" UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools" UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache" UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python" UV_TOOL_BIN_DIR="$HOME/.local/bin" UV_PYTHON_PREFERENCE="only-managed" GIT_AUTHOR_NAME="Bang Worker" GIT_AUTHOR_EMAIL="bang-worker@localhost" GIT_COMMITTER_NAME="Bang Worker" GIT_COMMITTER_EMAIL="bang-worker@localhost" POTATO_DAEMON_HOST="127.0.0.1" POTATO_DAEMON_PORT="3131" && exec node ./apps/daemon/dist/server/server.js'

# The same command for Linux. It is the Mac's, `env -i` and all, with real ampersands
# because it goes into a script, and with no /opt/homebrew on the path. ~/.local/bin
# stays: it is where claude's installer puts the command the workers are started with,
# and on Omarchy where its claude wrapper lives. npm_config_devdir is Linux's alone:
# node-pty ships no linux-x64 binary, so anything that rebuilds it runs node-gyp, and
# node-gyp keeps Node's headers in ~/.cache/node-gyp unless it is told otherwise.
EXEC_LINE_LINUX='cd "$HOME/.potato-cannon/app" && exec env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" SHELL="$SHELL" TMPDIR="${TMPDIR:-/tmp}" LANG="en_US.UTF-8" PATH="$HOME/.potato-cannon/node/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin" COREPACK_HOME="$HOME/.potato-cannon/corepack" PNPM_HOME="$HOME/.potato-cannon/pnpm" npm_config_cache="$HOME/.potato-cannon/npm-cache" npm_config_devdir="$HOME/.potato-cannon/node-gyp" UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools" UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache" UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python" UV_TOOL_BIN_DIR="$HOME/.local/bin" UV_PYTHON_PREFERENCE="only-managed" GIT_AUTHOR_NAME="Bang Worker" GIT_AUTHOR_EMAIL="bang-worker@localhost" GIT_COMMITTER_NAME="Bang Worker" GIT_COMMITTER_EMAIL="bang-worker@localhost" POTATO_DAEMON_HOST="127.0.0.1" POTATO_DAEMON_PORT="3131" node ./apps/daemon/dist/server/server.js'

for line in "$EXEC_LINE" "$EXEC_LINE_WIN" "$EXEC_LINE_LINUX"; do
  case "$line" in
    *$'\n'*) stop "the daemon's command has a newline in it. That is the bug this file exists to prevent." ;;
  esac
done

plist() {
  cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>$EXEC_LINE</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>30</integer>
  <key>StandardOutPath</key><string>$HOME/.potato-cannon/daemon.log</string>
  <key>StandardErrorPath</key><string>$HOME/.potato-cannon/daemon.log</string>
</dict>
</plist>
PLIST
}

# The Windows side of the same idea: a file the task runs, rather than a command
# typed into schtasks. schtasks takes the command as one /TR string and re-parses the
# quotes inside it, and the daemon's command is a long line full of quotes. A file
# holding the line is the same defence as the plist: what is written is what runs.
#
# Linux runs the same file from its unit, for the reason at the top: systemd would
# expand the command's $ and % before bash ever read it.
daemon_sh() {
  local exec_line="$EXEC_LINE_WIN"
  [ "$MACHINE" = linux ] && exec_line="$EXEC_LINE_LINUX"
  cat <<SH
#!/usr/bin/env bash
# Written by scripts/write-launch-agent.sh. Edit that, not this.
#
# Line one is why there is a file here rather than two keys in a task: a logon task
# has no StandardOutPath, so the daemon sends its own output to the same daemon.log
# the Mac's launch agent writes, which is where step 8's receipt looks for it.
exec >> "\$HOME/.potato-cannon/daemon.log" 2>&1
$exec_line
SH
}

# The unit. %h is systemd's own word for the home folder, and the only specifier in
# it. default.target is the user's session, so it starts at login and stops at logout,
# which is what the Mac's launch agent does.
unit() {
  cat <<UNIT
# Written by scripts/write-launch-agent.sh. Edit that, not this.
[Unit]
Description=Bang Potato Cannon daemon on 127.0.0.1:$PORT

[Service]
ExecStart=/bin/bash %h/.potato-cannon/cannon-daemon.sh
Restart=always
RestartSec=30

[Install]
WantedBy=default.target
UNIT
}

if [ "$DRY_RUN" = 1 ]; then
  echo "write-launch-agent: dry run. This is the file that would be written to"
  if [ "$MACHINE" = mac ]; then
    echo "$PLIST"
    echo "and nothing else would be written or loaded."
    echo
    plist
  elif [ "$MACHINE" = linux ]; then
    echo "$DAEMON_SH and $UNIT_FILE"
    echo "and nothing else would be written; the unit would not be enabled."
    echo
    daemon_sh
    echo
    unit
  else
    echo "$DAEMON_SH"
    echo "and nothing else would be written; the task \"$TASK\" would not be registered."
    echo
    daemon_sh
  fi
  exit 0
fi

# Nothing is written until 3131 is ours to take.
#
# On the sixth cold run a previous test user's daemon was still holding the port. The
# health check answered ok, because a daemon was there; it had nine and a half hours of
# uptime, because it was not the one this run had just built. Everything after that step
# would have been judged against somebody else's board. A port that is already listening
# is not a thing to write a launch agent over: two daemons on one port is the failure
# this cannot detect afterwards, because the one that answers is the one that got there
# first.
LISTENER="$(listener_on_3131)"
if [ -n "$LISTENER" ]; then
  printf 'write-launch-agent: STOPPED. Something already listens on 127.0.0.1:%s.\n' "$PORT" >&2
  printf '%s\n' "$LISTENER" | sed 's/^/  /' >&2
  echo "" >&2
  echo "  Another Cannon is running. Nothing was written and nothing was loaded." >&2
  echo "  Stop that daemon, or log in as the user that owns it and stop it there," >&2
  echo "  before running this again." >&2
  exit 1
fi

mkdir -p "$HOME/.potato-cannon" || stop "could not make $HOME/.potato-cannon"

if [ "$MACHINE" = mac ]; then
  mkdir -p "$HOME/Library/LaunchAgents" || stop "could not make $HOME/Library/LaunchAgents"

  # Beside the target, then moved in. A plist that does not parse must never be the
  # installed one, and launchd reads whatever is there the next time it looks.
  plist > "$PLIST.new" || stop "could not write $PLIST.new"
  if ! plutil -lint "$PLIST.new" >/dev/null 2>&1; then
    plutil -lint "$PLIST.new" >&2
    rm -f "$PLIST.new"
    stop "the plist does not parse; nothing was installed"
  fi
  mv "$PLIST.new" "$PLIST" || stop "could not move the plist into place"
  say "wrote $PLIST"
  say "plutil -lint: OK"

  # Loading it twice is the ordinary case, because a reader who re-runs a step is a
  # reader following instructions. Unload first and say so rather than failing on
  # "service already loaded", which reads like a refusal and is not one.
  if launchctl print "gui/$(id -u)/$LABEL" >/dev/null 2>&1; then
    launchctl bootout "gui/$(id -u)/$LABEL" >/dev/null 2>&1
    say "an earlier $LABEL was loaded; unloaded it first"
  fi
  launchctl bootstrap "gui/$(id -u)" "$PLIST" \
    || stop "launchctl bootstrap refused. The plist is at $PLIST and parses; the reason is launchd's."
  say "bootstrapped $LABEL"
elif [ "$MACHINE" = linux ]; then
  # A user unit needs a user manager to hand it to. Most desktops have one; WSL
  # without systemd and most containers do not, and there the honest answer is to
  # stop rather than write a unit nothing will ever read.
  systemctl --user show-environment >/dev/null 2>&1 \
    || stop "systemctl --user does not answer, so there is no systemd user manager to run the daemon. Nothing was written."

  # The script first, the same file and the same check as Windows.
  daemon_sh > "$DAEMON_SH.new" || stop "could not write $DAEMON_SH.new"
  if ! bash -n "$DAEMON_SH.new" 2>/dev/null; then
    bash -n "$DAEMON_SH.new" >&2
    rm -f "$DAEMON_SH.new"
    stop "the daemon script does not parse; nothing was installed"
  fi
  mv "$DAEMON_SH.new" "$DAEMON_SH" || stop "could not move the daemon script into place"
  chmod +x "$DAEMON_SH"
  say "wrote $DAEMON_SH"
  say "bash -n: OK"

  # Then the unit, beside its target and moved in once systemd has read it. The
  # check reads a file named for the unit, so the candidate is written into a
  # folder of its own under ~/.potato-cannon rather than as $UNIT_FILE.new, which
  # systemd-analyze would refuse for its suffix before it read a line of it.
  mkdir -p "$HOME/.config/systemd/user" || stop "could not make $HOME/.config/systemd/user"
  CANDIDATE_DIR="$HOME/.potato-cannon/unit-check"
  mkdir -p "$CANDIDATE_DIR" || stop "could not make $CANDIDATE_DIR"
  unit > "$CANDIDATE_DIR/$UNIT" || stop "could not write $CANDIDATE_DIR/$UNIT"
  if ! systemd-analyze --user verify "$CANDIDATE_DIR/$UNIT" >/dev/null 2>&1; then
    systemd-analyze --user verify "$CANDIDATE_DIR/$UNIT" >&2
    rm -rf "$CANDIDATE_DIR"
    stop "the unit does not verify; nothing was enabled"
  fi
  mv "$CANDIDATE_DIR/$UNIT" "$UNIT_FILE" || stop "could not move the unit into place"
  rm -rf "$CANDIDATE_DIR"
  say "wrote $UNIT_FILE"
  say "systemd-analyze --user verify: OK"

  # Running it twice is the ordinary case, as it is on the Mac. enable --now starts
  # a stopped unit and leaves a running one alone, so a re-run would keep the old
  # daemon on the old script; restart is what makes the one just written the one
  # that runs.
  systemctl --user daemon-reload || stop "systemctl --user daemon-reload refused"
  systemctl --user enable "$UNIT" >/dev/null 2>&1 \
    || stop "systemctl --user enable $UNIT refused. The unit is at $UNIT_FILE and verifies; the reason is systemd's."
  systemctl --user restart "$UNIT" \
    || stop "$UNIT is enabled but would not start. \`journalctl --user -u $UNIT\` has the reason."
  say "enabled and started $UNIT"
else
  # Beside the target, then moved in, for the same reason the plist is: a script that
  # does not parse must never be the one the task runs. `bash -n` is the Windows
  # branch's plutil -lint, and it reads the file without running a line of it.
  daemon_sh > "$DAEMON_SH.new" || stop "could not write $DAEMON_SH.new"
  if ! bash -n "$DAEMON_SH.new" 2>/dev/null; then
    bash -n "$DAEMON_SH.new" >&2
    rm -f "$DAEMON_SH.new"
    stop "the daemon script does not parse; nothing was registered"
  fi
  mv "$DAEMON_SH.new" "$DAEMON_SH" || stop "could not move the daemon script into place"
  chmod +x "$DAEMON_SH"
  say "wrote $DAEMON_SH"
  say "bash -n: OK"

  # The task runs Git Bash on that file. Which bash, asked rather than assumed: Git
  # for Windows is not always under C:\Program Files, and the one running this script
  # is by definition the one that works. cygpath turns it into the spelling Task
  # Scheduler and the Startup folder understand, since neither runs it from a shell.
  BASH_EXE="$(cygpath -w "$(command -v bash)" 2>/dev/null)"
  [ -n "$BASH_EXE" ] || stop "could not work out where bash.exe is; cygpath found nothing"
  # It is worked out here rather than at the top, so it is exported here too: the
  # PowerShell block below is single-quoted and reads it out of the environment.
  export BANG_BASH="$BASH_EXE"

  # Two ways to be started at logon, and the reason there are two is that the first
  # one is refused for a plain user.
  #
  # `schtasks /Create /SC ONLOGON` writes a task that fires for *whoever* logs on,
  # which is an act on the machine, so Windows wants an administrator and answers a
  # standard account with "Access is denied". That is what the Dell met on
  # 2026-09-25. PowerShell's Register-ScheduledTask with a trigger scoped to one
  # user is the same idea asked for properly: a task about this account, registered
  # by this account, which does not need the machine's permission. Neither can be
  # tried from the Mac this was written on, so both are here.
  #
  # Task Scheduler is tried first, and the Startup folder is the fallback, because a
  # task is a thing the script can ask about afterwards. `Get-ScheduledTask` says
  # whether it is registered, what it runs and whether it last started; Undo removes
  # it by name; and nothing a reader does to their own files disturbs it. A shortcut
  # in the Startup folder is a file in a folder people tidy, with no record anywhere
  # that it was meant to be there. It always works, which is why it is the fallback,
  # and it knows nothing about itself, which is why it is not the first choice.
  REGISTERED=""

  if powershell -NoProfile -ExecutionPolicy ByPass -c '
      $ErrorActionPreference = "Stop"
      try {
        Unregister-ScheduledTask -TaskName $env:BANG_TASK -Confirm:$false -ErrorAction SilentlyContinue
        $action  = New-ScheduledTaskAction -Execute $env:BANG_BASH -Argument ("-l `"" + $env:BANG_SH + "`"")
        $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
        Register-ScheduledTask -TaskName $env:BANG_TASK -Action $action -Trigger $trigger -Force | Out-Null
        exit 0
      } catch { exit 1 }' >/dev/null 2>&1; then
    REGISTERED="task"
    say "registered the scheduled task \"$TASK\", at logon, for this account"
    powershell -NoProfile -ExecutionPolicy ByPass \
      -c 'Start-ScheduledTask -TaskName $env:BANG_TASK' >/dev/null 2>&1 \
      || stop "\"$TASK\" is registered but would not start. Task Scheduler has the reason."
  else
    # No privilege of any kind: a .cmd in this account's own Startup folder, which
    # Windows runs at logon because it is there and for no other reason.
    STARTUP="$(cygpath "$(powershell -NoProfile -ExecutionPolicy ByPass \
      -c '[Environment]::GetFolderPath("Startup")' 2>/dev/null | tr -d '\r')" 2>/dev/null)"
    [ -n "$STARTUP" ] && [ -d "$STARTUP" ] \
      || stop "Task Scheduler refused and the Startup folder could not be found; nothing was registered."
    printf '@echo off\r\nstart "" /b "%s" -l "%s"\r\n' "$BASH_EXE" "$DAEMON_SH" > "$STARTUP_CMD_TMP" 2>/dev/null \
      || stop "could not write into the Startup folder"
    mv "$STARTUP_CMD_TMP" "$STARTUP/$STARTUP_CMD" || stop "could not move the launcher into the Startup folder"
    REGISTERED="startup"
    say "Task Scheduler refused; wrote $STARTUP/$STARTUP_CMD instead"
    say "that folder is run at logon and needs no privilege"
    ( cd "$HOME" && "$DAEMON_SH" & ) >/dev/null 2>&1
  fi

  # A logon task starts at the next logon, and you logged in before you read this, so
  # whichever one took is started once here. That is what launchctl bootstrap does on
  # the Mac side, and it is why the receipt below can be read now rather than after a
  # reboot.
  say "started the daemon by the $REGISTERED route"
fi

for _ in $(seq 1 30); do
  LINE="$(curl -s --max-time 2 "$HEALTH" 2>/dev/null)"
  if [ -n "$LINE" ]; then
    printf '  %s\n' "$LINE"

    # A health line says a daemon is there. It does not say it is ours. These two say
    # that: the process holding the port, with the user that owns it, and how many
    # times the daemon we just started found the port taken.
    echo "  listener on $PORT:"
    OWNED="$(listener_on_3131)"
    if [ -n "$OWNED" ]; then
      printf '%s\n' "$OWNED" | sed 's/^/    /'
    else
      echo "    (nothing reported it, which should not happen while /health answers)"
    fi

    # `grep -c` prints 0 and exits 1 when nothing matches, so the `|| echo 0` this
    # used to carry fired on exactly the clean run it was written for and appended a
    # second 0. The receipt read "EADDRINUSE lines in daemon.log: 0 0". The only case
    # with no output at all is a log that is not there yet, which is what the test
    # below covers.
    EADDRINUSE="$(grep -c EADDRINUSE "$HOME/.potato-cannon/daemon.log" 2>/dev/null)"
    [ -n "$EADDRINUSE" ] || EADDRINUSE=0
    echo "  EADDRINUSE lines in daemon.log: $EADDRINUSE"
    exit 0
  fi
  sleep 1
done

echo "write-launch-agent: the daemon did not answer $HEALTH within 30s." >&2
echo "Its output is in $HOME/.potato-cannon/daemon.log; the last lines:" >&2
tail -20 "$HOME/.potato-cannon/daemon.log" 2>/dev/null >&2
exit 1
