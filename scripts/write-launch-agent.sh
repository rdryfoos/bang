#!/usr/bin/env bash
# write-launch-agent: install the thing that keeps the Cannon daemon running, on
# whichever of the two machines this is.
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
# leaves outside the home folder, and BANG.md's Undo removes it by name.
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
#      removes it whole. The four UV_* are there for the same reason and for one
#      more: a tool installed under one UV_TOOL_DIR is invisible to a call made
#      without it, so a worker running specify has to carry the same four BANG.md
#      step 3 installed with or be told the thing is not there.
#
# What the two branches do not share, and a reader should know it before leaning on
# the Windows one: launchd's KeepAlive starts the daemon again when it dies, and a
# logon task has nothing like it. On Windows a daemon that dies stays dead until the
# next logon or until somebody runs `schtasks /Run` by hand.
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
PORT="3131"
HEALTH="http://127.0.0.1:$PORT/health"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

say() { printf '  %s\n' "$*"; }
stop() { printf 'write-launch-agent: STOPPED. %s\n' "$*" >&2; exit 1; }

# Which machine this is, read the same way BANG.md step 2 reads it.
case "$(uname -s)" in
  Darwin)            MACHINE=mac ;;
  MINGW*|MSYS*)      MACHINE=windows ;;
  *)                 stop "this script knows a Mac and Windows, and \`uname -s\` said $(uname -s)." ;;
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
listener_on_3131() {
  if [ "$MACHINE" = mac ]; then
    lsof -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | tail -n +2
    return
  fi
  POTATO_PORT="$PORT" powershell -NoProfile -c '
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
EXEC_LINE='cd "$HOME/.potato-cannon/app" &amp;&amp; exec env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" SHELL="$SHELL" TMPDIR="${TMPDIR:-/tmp}" LANG="en_US.UTF-8" PATH="$HOME/.potato-cannon/node/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" COREPACK_HOME="$HOME/.potato-cannon/corepack" PNPM_HOME="$HOME/.potato-cannon/pnpm" npm_config_cache="$HOME/.potato-cannon/npm-cache" UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools" UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache" UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python" UV_TOOL_BIN_DIR="$HOME/.local/bin" GIT_AUTHOR_NAME="Bang Worker" GIT_AUTHOR_EMAIL="bang-worker@localhost" GIT_COMMITTER_NAME="Bang Worker" GIT_COMMITTER_EMAIL="bang-worker@localhost" POTATO_DAEMON_HOST="127.0.0.1" POTATO_DAEMON_PORT="3131" node ./apps/daemon/dist/server/server.js'

# The same command for Windows, and the differences are all forced. `env -i` is gone:
# it would empty the environment a native node.exe needs to start at all, SystemRoot
# and TEMP among it, so the variables are exported over what is there instead. The
# path names ~/.potato-cannon/node without the bin. And the ampersands are ampersands,
# because this one goes into a shell script rather than into XML.
EXEC_LINE_WIN='cd "$HOME/.potato-cannon/app" && export PATH="$HOME/.potato-cannon/node:$HOME/.local/bin:$PATH" COREPACK_HOME="$HOME/.potato-cannon/corepack" PNPM_HOME="$HOME/.potato-cannon/pnpm" npm_config_cache="$HOME/.potato-cannon/npm-cache" UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools" UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache" UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python" UV_TOOL_BIN_DIR="$HOME/.local/bin" GIT_AUTHOR_NAME="Bang Worker" GIT_AUTHOR_EMAIL="bang-worker@localhost" GIT_COMMITTER_NAME="Bang Worker" GIT_COMMITTER_EMAIL="bang-worker@localhost" POTATO_DAEMON_HOST="127.0.0.1" POTATO_DAEMON_PORT="3131" && exec node ./apps/daemon/dist/server/server.js'

for line in "$EXEC_LINE" "$EXEC_LINE_WIN"; do
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
daemon_sh() {
  cat <<SH
#!/usr/bin/env bash
# Written by scripts/write-launch-agent.sh. Edit that, not this.
#
# Line one is why there is a file here rather than two keys in a task: a logon task
# has no StandardOutPath, so the daemon sends its own output to the same daemon.log
# the Mac's launch agent writes, which is where step 8's receipt looks for it.
exec >> "\$HOME/.potato-cannon/daemon.log" 2>&1
$EXEC_LINE_WIN
SH
}

if [ "$DRY_RUN" = 1 ]; then
  echo "write-launch-agent: dry run. This is the file that would be written to"
  if [ "$MACHINE" = mac ]; then
    echo "$PLIST"
    echo "and nothing else would be written or loaded."
    echo
    plist
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
  # Scheduler understands, since the task is not run from a shell.
  BASH_EXE="$(cygpath -w "$(command -v bash)" 2>/dev/null)"
  [ -n "$BASH_EXE" ] || stop "could not work out where bash.exe is; cygpath found nothing"

  # The doubled slashes are not a typo. Git Bash rewrites an argument beginning with a
  # single slash into a Windows path before the program is started, so a plain /Create
  # reaches schtasks as C:/Program Files/Git/Create and is refused. // is how you say
  # you meant a switch.
  if schtasks //Query //TN "$TASK" >/dev/null 2>&1; then
    schtasks //Delete //TN "$TASK" //F >/dev/null 2>&1
    say "an earlier \"$TASK\" was registered; removed it first"
  fi
  schtasks //Create //TN "$TASK" //SC ONLOGON //TR "\"$BASH_EXE\" -l \"$DAEMON_SH\"" //F >/dev/null \
    || stop "schtasks refused to register \"$TASK\". The script is at $DAEMON_SH and parses; the reason is Task Scheduler's."
  say "registered \"$TASK\" at logon"

  # A logon task starts at the next logon, and you logged in before you read this. So
  # it is started once here, which is what launchctl bootstrap does on the Mac side.
  schtasks //Run //TN "$TASK" >/dev/null \
    || stop "\"$TASK\" is registered but would not start. Task Scheduler has the reason."
  say "started \"$TASK\""
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

    EADDRINUSE="$(grep -c EADDRINUSE "$HOME/.potato-cannon/daemon.log" 2>/dev/null || echo 0)"
    echo "  EADDRINUSE lines in daemon.log: $EADDRINUSE"
    exit 0
  fi
  sleep 1
done

echo "write-launch-agent: the daemon did not answer $HEALTH within 30s." >&2
echo "Its output is in $HOME/.potato-cannon/daemon.log; the last lines:" >&2
tail -20 "$HOME/.potato-cannon/daemon.log" 2>/dev/null >&2
exit 1
