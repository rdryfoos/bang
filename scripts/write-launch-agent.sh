#!/usr/bin/env bash
# write-launch-agent: install the launch agent that keeps the Cannon daemon running.
#
# This used to be a plist printed in BANG.md for the reader to copy. It could not be
# copied. The daemon's command is one long shell line, and a plist typeset to fit a
# page breaks it across nine lines; a <string> keeps every newline it is given, so
# what landed on disk was a command with newlines in the middle of it and a daemon
# that never started. The reader's receipt was a failing /health with nothing to say
# why. A file the repository ships cannot be mis-copied, so the plist lives here.
#
# What it writes: ~/Library/LaunchAgents/com.dryfoos.bang.cannon.plist, and nothing
# else. It writes beside the target first and moves the file into place once plutil
# has read it, so a plist that does not parse never becomes the installed one.
#
# Two things the reader could not have got right by hand, and the reasons:
#
#   1. StandardOutPath and StandardErrorPath are real paths with the real home folder
#      in them. A plist does not expand ~ or $HOME in a path, so $HOME is substituted
#      here, while every $HOME inside the command string is left alone: that one is
#      inside a shell command and is expanded when the daemon starts.
#   2. The daemon is run directly rather than through the Cannon's own start command,
#      which passes --daemon, detaches and exits. Nothing can supervise a process that
#      has already gone, so KeepAlive would restart a thing that exits every time.
#   3. The path names ~/.potato-cannon/node/bin first, which is where BANG.md step 4
#      puts Node 22, so the daemon runs on the Node it was built against and not on
#      whatever the person happens to have. COREPACK_HOME, PNPM_HOME and
#      npm_config_cache are set for the same reason the path is: anything the daemon
#      or a worker under it downloads lands in ~/.potato-cannon, which is one of the
#      places BANG.md says this project writes to, and Undo removes it whole. The four
#      UV_* are there for the same reason and for one more: a tool installed under one
#      UV_TOOL_DIR is invisible to a call made without it, so a worker running specify
#      has to carry the same four BANG.md step 3 installed with or be told the thing is
#      not there.
#
# Usage:  bash scripts/write-launch-agent.sh
#         bash scripts/write-launch-agent.sh --dry-run    print it, write nothing
#
# Written by the born-threaded practice; MIT.
set -uo pipefail

LABEL="com.dryfoos.bang.cannon"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
HEALTH="http://127.0.0.1:3131/health"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

say() { printf '  %s\n' "$*"; }
stop() { printf 'write-launch-agent: STOPPED. %s\n' "$*" >&2; exit 1; }

# The command the daemon runs, on one line and staying on one line. Keeping it in a
# variable rather than inside the plist text is what makes the promise checkable: one
# line here is one line in the file, and the check below says so before anything is
# installed.
EXEC_LINE='cd "$HOME/.potato-cannon/app" &amp;&amp; exec env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" SHELL="$SHELL" TMPDIR="${TMPDIR:-/tmp}" LANG="en_US.UTF-8" PATH="$HOME/.potato-cannon/node/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" COREPACK_HOME="$HOME/.potato-cannon/corepack" PNPM_HOME="$HOME/.potato-cannon/pnpm" npm_config_cache="$HOME/.potato-cannon/npm-cache" UV_TOOL_DIR="$HOME/.potato-cannon/uv/tools" UV_CACHE_DIR="$HOME/.potato-cannon/uv/cache" UV_PYTHON_INSTALL_DIR="$HOME/.potato-cannon/uv/python" UV_TOOL_BIN_DIR="$HOME/.local/bin" GIT_AUTHOR_NAME="Bang Worker" GIT_AUTHOR_EMAIL="bang-worker@localhost" GIT_COMMITTER_NAME="Bang Worker" GIT_COMMITTER_EMAIL="bang-worker@localhost" POTATO_DAEMON_HOST="127.0.0.1" POTATO_DAEMON_PORT="3131" node ./apps/daemon/dist/server/server.js'

case "$EXEC_LINE" in
  *$'\n'*) stop "the daemon's command has a newline in it. That is the bug this file exists to prevent." ;;
esac

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

if [ "$DRY_RUN" = 1 ]; then
  echo "write-launch-agent: dry run. This is the file that would be written to"
  echo "$PLIST"
  echo "and nothing else would be written or loaded."
  echo
  plist
  exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/.potato-cannon" \
  || stop "could not make $HOME/Library/LaunchAgents"

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

for _ in $(seq 1 30); do
  LINE="$(curl -s --max-time 2 "$HEALTH" 2>/dev/null)"
  if [ -n "$LINE" ]; then
    printf '  %s\n' "$LINE"
    exit 0
  fi
  sleep 1
done

echo "write-launch-agent: the daemon did not answer $HEALTH within 30s." >&2
echo "Its output is in $HOME/.potato-cannon/daemon.log; the last lines:" >&2
tail -20 "$HOME/.potato-cannon/daemon.log" 2>/dev/null >&2
exit 1
