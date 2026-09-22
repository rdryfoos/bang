#!/usr/bin/env bash
# try: run the thing the card built, and print what it did.
#
# A reviewer reading a card can see the diff, the Gate and the thread, and until now
# could not see the software run without leaving the board and finding a terminal. This
# is the one command that answers "does it work", and the Cannon's Try it button runs
# exactly this file and nothing else.
#
# It takes no arguments, on purpose. Nothing from the board, the card or the browser
# reaches a command line here: the button names this file, this file decides what to
# run, and the project governs the file. Adding arguments would make the button a way to
# run things.
#
# It touches no network and writes nothing outside a temporary directory. The records it
# shows are seeded here rather than read from the owner's real file, so a reviewer, or
# anyone watching over their shoulder, sees the software work without seeing whose
# things are lent to whom.
#
# Exits with the application's own exit code, so a reviewer sees a failure as a failure.
#
# Two modes, since 2026-09-20 and the screens in design/. If the branch carries a web
# app, this starts it on a free loopback port and prints the URL, because a screen is
# not a thing you can read the output of. Otherwise it runs the command line, as it has
# from the start, and a branch with no application at all says so and exits 0.
#
# The web mode's contract. It is stated for the build in design/README.md, under
# "How the app is started", and that is the governed copy; these three lines are
# what this script acts on, and they are meant to stay the same three:
#
#   src/whms/web.py           exists and runs as `python3 -m whms.web`
#   --port N                  the port to listen on, and it binds 127.0.0.1 only
#   WHMS_DATA_FILE            the records file, the same variable the command line reads
#
# The server is left running so the reviewer can click through the screens, and it is
# not left running for ever: it stops after TRY_WEB_MINUTES minutes, 30 by default.
# Pressing the button again stops whatever the last press started, so there is never
# more than one.
#
# Two things enforce that, because on 2026-09-21 one press outlived its watchdog by
# three hours. The watchdog itself could not be made to fail in isolation, under a
# normal exit or under the SIGTERM the daemon's execFile timeout sends, so the cause
# was most likely the watchdog subshell sharing a process group with the daemon and
# dying with it, while the nohup-ed server did not. Rather than trust a diagnosis that
# could not be reproduced:
#
#   1. the watchdog runs under setsid, in its own session, so nothing aimed at the
#      daemon's process group reaches it; and
#   2. a deadline is written to disk beside the pid, and every run of this script
#      reaps an app that is past its own deadline before starting another.
#
# The second is what makes the promise true even if the first is killed anyway: the
# next press, or the next reset, collects it.
#
# Written by the born-threaded practice; MIT.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT" || { echo "try: cannot enter $ROOT"; exit 2; }

# What the card says, and what the design map says.
#
# The Try it route runs this script with cwd set to the card's worktree and no
# environment at all: no POTATO_TICKET_ID, no POTATO_PROJECT_ID. So the card id comes
# from the directory this is standing in, and the project from the one whose path is
# this worktree's repository. Both are read-only lookups against the daemon; if either
# fails, everything below falls through to the next option, which is the point of
# having four.
card_id() { basename "$ROOT"; }

card_line() {                 # card_line <name>  -> the value, or nothing
  python3 - "$DAEMON_URL" "$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || echo "$ROOT")" "$(card_id)" "$1" <<'PY' 2>/dev/null
import json, os, sys, urllib.parse, urllib.request

daemon, repo, ticket, want = sys.argv[1:5]
# The worktree lives at <project>/.potato/worktrees/<card>, so the project's own path
# is two levels above it.
project_path = os.path.dirname(os.path.dirname(os.path.dirname(repo)))

def get(path):
    with urllib.request.urlopen(daemon + path, timeout=10) as r:
        return json.loads(r.read().decode() or "null")

try:
    projects = get("/api/projects") or []
    match = [p for p in projects if p.get("path") in (project_path, repo)]
    if not match:
        raise SystemExit(0)
    card = get(f"/api/tickets/{urllib.parse.quote(match[0]['id'], safe='')}/{urllib.parse.quote(ticket, safe='')}") or {}
    for line in (card.get("description") or "").splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(want.lower() + ":"):
            print(stripped.split(":", 1)[1].strip())
            break
except Exception:
    pass
PY
}

# design/README.md maps a screen file to the IDs it fulfils. This turns the card's
# first ID into the route that shows it, so a card that never got a try: line still
# opens where its promise lives rather than on whatever the front page happens to be.
route_for_ids() {             # route_for_ids <ids...>  -> a route, or nothing
  [ -f "$ROOT/design/README.md" ] || return 0
  python3 - "$ROOT/design/README.md" "$@" <<'PY' 2>/dev/null
import re, sys
readme, ids = sys.argv[1], [i.strip().rstrip(",") for i in sys.argv[2:]]
ROUTES = {"outstanding.html": "/", "nothing-out.html": "/",
          "lend.html": "/lend", "mark-returned.html": "/return/1"}
rows = []
for line in open(readme, encoding="utf-8"):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) >= 3 and cells[0].endswith(".html"):
        rows.append((cells[0], {c.strip() for c in cells[2].split(",")}))
for want in ids:
    for filename, fulfils in rows:
        if want in fulfils and filename in ROUTES:
            print(ROUTES[filename])
            raise SystemExit(0)
PY
}

DAEMON_URL="http://${POTATO_DAEMON_HOST:-127.0.0.1}:${POTATO_DAEMON_PORT:-3131}"
WEB_ENTRY="src/whms/web.py"
# One state directory per project, not one per machine. A shared directory meant that
# staging one board killed the Try it app of another, because both wrote the same pid
# file. The key is the project's own path, so two boards cannot collide.
STATE_KEY="$(printf '%s' "$ROOT" | shasum | cut -c1-12)"
STATE="${TMPDIR:-/tmp}/bang-try-web-$STATE_KEY"
LIFETIME_MINUTES="${TRY_WEB_MINUTES:-30}"

seed() {                      # the same invented things the command line mode shows
  python3 -m whms add --name "Green-handled pruning shears" --borrower "Sam" \
    --date-out 2026-08-01 >/dev/null 2>&1 || true
  python3 -m whms add --name "Folding camp chair" --borrower "Alex" \
    --date-out 2026-07-14 >/dev/null 2>&1 || true
}

# Collect anything a previous run left past its own deadline. This is the half that
# does not depend on a watchdog having survived.
reap_expired() {
  [ -f "$STATE/pid" ] && [ -f "$STATE/deadline" ] || return 0
  local deadline now pid
  deadline="$(cat "$STATE/deadline" 2>/dev/null || echo 0)"
  now="$(date +%s)"
  [ "$now" -ge "$deadline" ] 2>/dev/null || return 0
  pid="$(cat "$STATE/pid" 2>/dev/null || true)"
  if [ -n "$pid" ] && kill "$pid" 2>/dev/null; then
    echo "try: an app from an earlier press was past its ${LIFETIME_MINUTES}-minute"
    echo "     deadline and had not stopped itself. Stopped it (pid $pid)."
  fi
  rm -rf "$STATE/data" "$STATE/pid" "$STATE/deadline"
}

start_web() {
  mkdir -p "$STATE"
  reap_expired
  if [ -f "$STATE/pid" ]; then
    kill "$(cat "$STATE/pid")" 2>/dev/null || true
    rm -f "$STATE/pid" "$STATE/deadline"
  fi
  rm -rf "$STATE/data"; mkdir -p "$STATE/data"

  export WHMS_DATA_FILE="$STATE/data/items.json"
  export PYTHONPATH="$ROOT/src"
  seed

  PORT="$(python3 -c 'import socket
s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"
  if [ -z "$PORT" ]; then
    echo "try: could not find a free port."
    return 2
  fi

  echo "Starting the web app from this branch on a free loopback port."
  [ -n "${ROUTE_WHY:-}" ] && echo "$ROUTE_WHY"
  echo "It reads a temporary records file seeded with invented things; nobody's real"
  echo "records are read or written, and nothing is reachable off this machine."
  echo

  nohup python3 -m whms.web --port "$PORT" > "$STATE/log" 2>&1 &
  pid=$!
  echo "$pid" > "$STATE/pid"

  for _ in $(seq 1 30); do
    if curl -sf --max-time 2 "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
      echo "$(( $(date +%s) + LIFETIME_MINUTES * 60 ))" > "$STATE/deadline"
      setsid bash -c "sleep $((LIFETIME_MINUTES * 60)); kill $pid 2>/dev/null; \
        rm -rf '$STATE/data' '$STATE/pid' '$STATE/deadline'" >/dev/null 2>&1 &
      echo "    http://127.0.0.1:$PORT${ROUTE:-/}"
      echo
      echo "It is answering. The link is live for $LIFETIME_MINUTES minutes, then it"
      echo "stops itself and its seeded records are deleted. Press Try it again to get"
      echo "a fresh one; that also stops this one."
      return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid"; code=$?
      echo "try: the web app exited $code before it answered. Its output:"
      sed 's/^/  /' "$STATE/log"
      rm -f "$STATE/pid" "$STATE/deadline"
      return "$code"
    fi
    sleep 1
  done

  kill "$pid" 2>/dev/null; rm -f "$STATE/pid" "$STATE/deadline"
  echo "try: the web app did not answer on 127.0.0.1:$PORT within 30s. Its output:"
  sed 's/^/  /' "$STATE/log"
  return 1
}

# What to open, in order. The first that answers wins.
#
#   1. the route on the card's try: line          the worker said where to look
#   2. the command on the card's try: line        the worker said there is no screen
#   3. the screen design/README maps this card's IDs to   nobody said anything
#   4. the fixed add-and-list script              nothing said anything at all
#
# A transcript is the last resort, and the card outranks the map in getting there.
# The map was ahead of the command form until 2026-09-22, and BANV-5 showed what that
# costs: its worker read the branch, found that nothing it built has a screen, wrote
# "no screen serves this promise yet" on the card and gave the commands that do show
# it. The map then matched US-RET-10 to mark-returned.html and Try it opened
# /return/1, which works, because the branch inherits BANV-1'"'"'s web app from main. A
# reviewer was shown a working screen proving a promise this card never touched, with
# nothing on it to say so. That is worse than a transcript; it looks like evidence.
#
# So a try: line beats the map, in either form. The map is for a card whose worker
# said nothing, and a worker that wrote the command form has said something, and it
# has read the code.
TRY_LINE="$(card_line try)"
ROUTE=""
ROUTE_WHY=""

case "$TRY_LINE" in
  route\ *)
    ROUTE="${TRY_LINE#route }"
    ROUTE_WHY="Opening $ROUTE, which this card's try: line names."
    ;;
  command\ *)
    : ;;                      # handled below, once the route forms have had their turn
esac

if [ -z "$ROUTE" ] && [ -z "$TRY_LINE" ] && [ -f "$WEB_ENTRY" ]; then
  IDS_LINE="$(card_line ids)"
  if [ -n "$IDS_LINE" ]; then
    # shellcheck disable=SC2086
    ROUTE="$(route_for_ids $(printf '%s' "$IDS_LINE" | tr ',' ' '))"
    [ -n "$ROUTE" ] && ROUTE_WHY="Opening $ROUTE: design/README.md maps this card's IDs to that screen."
  fi
fi

if [ -n "$ROUTE" ] && [ -f "$WEB_ENTRY" ]; then
  start_web
  exit $?
fi

if [ -f "$WEB_ENTRY" ] && [ -z "$TRY_LINE" ]; then
  ROUTE="/"
  ROUTE_WHY="No try: line on the card and no screen mapped to its IDs; opening the front page."
  start_web
  exit $?
fi

case "$TRY_LINE" in
  command\ *)
    if [ ! -d src/whms ]; then
      echo "try: the card asks for a command sequence and this branch has no application."
      exit 0
    fi
    WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
    export WHMS_DATA_FILE="$WORK/items.json"
    export PYTHONPATH="$ROOT/src"
    echo "No screen serves this card's promise, so this is what it does at the command"
    echo "line, against a temporary file. Nobody's real records are read or written."
    echo
    printf '$ %s\n' "${TRY_LINE#command }"
    ( eval "lend() { python3 -m whms \"\$@\"; }; ${TRY_LINE#command }" ) 2>&1 | sed 's/^/  /'
    code="${PIPESTATUS[0]}"
    echo
    echo "Exited $code."
    exit "$code"
    ;;
esac

if [ ! -d src/whms ]; then
  echo "try: this branch has no application yet; nothing to run."
  exit 0
fi

echo "Nothing on this card says what to open, and no screen is mapped to its IDs."
echo "This is the fallback: the command line, doing the one thing it has always done"
echo "here. It is not this card's proof."
echo

WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
export WHMS_DATA_FILE="$WORK/items.json"
export PYTHONPATH="$ROOT/src"

run() {                       # run <description> <args...>
  printf '$ lend %s\n' "$*"
  python3 -m whms "$@" 2>&1 | sed 's/^/  /'
  return "${PIPESTATUS[0]}"
}

echo "Running the lending tracker from this branch, against a temporary file."
echo "Nobody's real records are read or written."
echo

run list || true
echo
run add --name "Green-handled pruning shears" --borrower "Sam" --date-out 2026-08-01 || true
run add --name "Folding camp chair" --borrower "Alex" --date-out 2026-07-14 || true
echo
run list; code=$?
echo
run add --name "Torque wrench" --date-out 2026-09-01 || true

echo
if [ "$code" = 0 ]; then
  echo "The outstanding list ran and exited 0."
else
  echo "The outstanding list exited $code."
fi
exit "$code"
