#!/usr/bin/env bash
# column-entry: the one door every column entry goes through.
#
# Two jobs. It runs whatever check that column has, and it writes one line onto the card
# in plain words saying what happened, who asked for it, and whether the answer was yes
# or no. A card that has
# been refused twice and then let through should say all three things, in order, on
# itself. Before this, a card in Review carried two stale blocked notices and no account
# of how it got there.
#
# Usage, as the template's entryChecks.<Phase>.command:
#     column-entry.sh <Phase>
#
# The exit code is the check's own, so the daemon's refusal behaviour is unchanged: zero
# lets the move through and anything else refuses it. The status line is written either
# way, and a failure to write one never changes the verdict.
#
# Written by the born-threaded practice; MIT.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PHASE="${1:-${POTATO_TO_PHASE:-}}"
FROM="${POTATO_FROM_PHASE:-somewhere}"
TICKET="${POTATO_TICKET_ID:-}"

out="$(mktemp)"; trap 'rm -f "$out"' EXIT

case "$PHASE" in
  Spec)
    # No check. A card enters Spec because a hand put it there, and that is the whole
    # of the requirement. The line below is the record that it happened.
    : > "$out"; code=0
    ;;
  Build)
    python3 "$HERE/column-check.py" --spec-names-ids > "$out" 2>&1; code=$?
    ;;
  Gate)
    python3 "$HERE/column-check.py" --has-commits > "$out" 2>&1; code=$?
    ;;
  Align|Review)
    # Review is the human column. This project called it Align until 2026-09-25 and
    # some of its history entries still say so, so both names are matched: a board
    # that was never renamed keeps working, which is the whole rule.
    bash "$HERE/review-packet.sh" > "$out" 2>&1; code=$?
    ;;
  Done)
    # Before anything is merged: did this card deliver what it claimed? A card that
    # reached Done over a promise still at backlog altitude is how NFR-DUR-10 came to
    # sit unproven under a green board on 2026-09-20.
    if python3 "$HERE/column-check.py" --ids-delivered > "$out" 2>&1; then
      bash "$HERE/promote-to-done.sh" >> "$out" 2>&1; code=$?
    else
      code=$?
    fi
    ;;
  *)
    printf 'column-entry: no check defined for %s\n' "$PHASE" > "$out"; code=0
    ;;
esac

reason="$(grep -v '^[[:space:]]*$' "$out" | tail -1)"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Who moved it. The daemon tells us rather than leaving us to guess, which matters most
# for the case a reader cannot see: a card that advanced on the machine's own legs looks
# exactly like one a person decided to move.
case "${POTATO_ACTOR:-}" in
  auto)      who="the Cannon, on its own" ;;
  hand:*)    who="a hand, ${POTATO_ACTOR#hand:}" ;;
  hook:*)    who="the ${POTATO_ACTOR#hook:} hook" ;;
  "")        who="an unrecorded mover" ;;
  *)         who="$POTATO_ACTOR" ;;
esac

# On entry to Build, the line also records where the card's branch stood. Nothing else
# records it, and without it "did this Build produce anything" can only be answered
# against main, which says yes for a card that built nothing and inherited a commit
# from an earlier attempt. See column-check.py --has-commits.
at=""
if [ "$PHASE" = "Build" ] && [ -n "$TICKET" ]; then
  head="$(git rev-parse --short "potato/$TICKET" 2>/dev/null || true)"
  [ -n "$head" ] && at=" branch at $head."
fi

if [ "$code" = 0 ]; then
  line="$now  $PHASE entered from $FROM, by $who.$at ${reason:-Nothing to check.}"
else
  line="$now  $PHASE refused, the card stays in $FROM, asked by $who. ${reason:-No reason given.}"
fi

if [ -n "$TICKET" ]; then
  CARD_IO_MODE=status CARD_IO_MARK="$line" python3 "$HERE/card-io.py" >/dev/null 2>&1 \
    || echo "column-entry: the status line could not be written to $TICKET" >&2
fi

cat "$out"
exit "$code"
