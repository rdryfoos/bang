#!/usr/bin/env bash
# review-packet: what a human needs in order to review a card, written onto the card.
#
# Rik opened BAN-1 in Review on 2026-09-20 and found two stale blocked notices and
# nothing else. No diff, no branch, no Gate output, no trace rows. The work was real and
# green and none of it was visible from the place a reviewer stands.
#
# This runs as the Review entry check and writes four things into a review-packet block
# on the card, in the order a reviewer reads them:
#
#   1. the branch, how far ahead and behind it is, and the short log of what it adds
#   2. the diff stat against the default branch
#   3. the Gate's verdict for the branch, verbatim, every line
#   4. the Thread Report for the card's IDs
#
# It illuminates and never refuses: a card reaching Review has already passed the checks
# that can refuse it, and a reviewer with a broken packet is better served by a packet
# that says so than by a card that will not open. It exits 0 unless it cannot reach the
# daemon at all.
#
# Written by the born-threaded practice; MIT.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT" || exit 0

CONF="$HERE/gate.conf"
# shellcheck source=/dev/null
[ -f "$CONF" ] && . "$CONF"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
SPECASSAY_DIR=".specify/extensions/specassay-check"

TICKET="${POTATO_TICKET_ID:-}"
[ -n "$TICKET" ] || { echo "review-packet: no POTATO_TICKET_ID; this runs as the Review entry check"; exit 0; }

BRANCH="$(CARD_IO_MODE=branch BRANCH_PREFIX="${BRANCH_PREFIX:-potato}" python3 "$HERE/card-io.py" 2>/dev/null)"
TRY_LINE="$(CARD_IO_MODE=line CARD_IO_LINE=try python3 "$HERE/card-io.py" 2>/dev/null)"
WORKTREE="$ROOT/.potato/worktrees/$TICKET"
PACKET="$(mktemp)"; GATE_OUT="$(mktemp)"; THREAD="$(mktemp)"
trap 'rm -f "$PACKET" "$GATE_OUT" "$THREAD"' EXIT

{
  printf '### Review packet, written %s\n\nThe Thread Report for this card is at the top of this description.\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # When the card's own try: line says no screen serves its promise, say so before the
  # branch line rather than leaving a reviewer to find out by pressing Try it and
  # reading a transcript they did not expect. The worker put that sentence on the card
  # because it had read the branch; it belongs where the reviewing starts.
  #
  # The commands go in a block under the sentence, one per line, because a reviewer
  # reads them before they press anything and a single bold line of shell is a wall.
  # The card's try: line separates them with semicolons; the block separates them the
  # way a person would type them.
  if printf '%s' "$TRY_LINE" | grep -q '^command '; then
    printf 'No screen. Try it runs this and shows the transcript:\n\n```\n'
    printf '%s' "${TRY_LINE#command }" | tr ';' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$'
    printf '```\n\n'
  fi

  if [ -z "$BRANCH" ] || ! git rev-parse --verify --quiet "$BRANCH^{commit}" >/dev/null; then
    printf 'No branch for this card. There is nothing to review from here.\n'
  else
    ahead="$(git rev-list --count "$DEFAULT_BRANCH..$BRANCH")"
    behind="$(git rev-list --count "$BRANCH..$DEFAULT_BRANCH")"
    printf '**1. The branch.** `%s`, %s commit(s) ahead of `%s`, %s behind.\n\n' \
      "$BRANCH" "$ahead" "$DEFAULT_BRANCH" "$behind"
    printf '```\n%s\n```\n\n' "$(git log --oneline "$DEFAULT_BRANCH..$BRANCH")"

    printf '**2. What it changes.**\n\n```\n%s\n```\n\n' \
      "$(git diff --stat "$DEFAULT_BRANCH...$BRANCH")"

    printf '**3. The Gate on this branch, verbatim.**\n\n'
    if [ -d "$WORKTREE" ]; then
      (cd "$WORKTREE" && bash "$WORKTREE/scripts/gate.sh") > "$GATE_OUT" 2>&1
      printf '```\n%s\n```\n\n' "$(cat "$GATE_OUT")"
    else
      printf 'The card has no worktree at `%s`, so the Gate was not run for this packet.\n\n' \
        ".potato/worktrees/$TICKET"
    fi

  fi
} > "$PACKET"

# The Thread Report goes at the very top of the card, in a block of its own. It is what
# a reviewer opens the card to see, and until now it sat at the bottom of four kilobytes
# of packet behind a See more control, which is a place nobody reads from.
if [ -n "$BRANCH" ] && git rev-parse --verify --quiet "$BRANCH^{commit}" >/dev/null; then
{
  # The base is the snapshot a green promotion wrote, at a path no Gate touches. The
  # manifests themselves are ignored everywhere, so main has no trace-manifest.json to
  # compare against and this stands in its place.
  snapshot="$JOURNAL_PREFIX/manifest-at-main.json"
  snap_sha="$(git log -1 --format=%h -- "$snapshot" 2>/dev/null)"
  base="$(mktemp)"; head="$(mktemp)"; files="$(mktemp)"
  git show "$DEFAULT_BRANCH:$snapshot" > "$base" 2>/dev/null
  if [ -s "$base" ]; then
    printf '**The Thread Report**, compared against %s as of promotion `%s`.\n\n' \
      "$DEFAULT_BRANCH" "${snap_sha:-unknown}"
  else
    printf '**The Thread Report.** No base: %s has no promotion snapshot yet, so this is the head state rather than what moved.\n\n' "$DEFAULT_BRANCH"
  fi
  if [ -s "$WORKTREE/trace-manifest.json" ]; then
    cp "$WORKTREE/trace-manifest.json" "$head"
  else
    git show "$BRANCH:trace-manifest.json" > "$head" 2>/dev/null
  fi
  git diff --name-only "$DEFAULT_BRANCH...$BRANCH" > "$files"
  if [ -s "$base" ] && [ -s "$head" ]; then
    python3 "$SPECASSAY_DIR/scripts/thread-report.py" \
      --base "$base" --head "$head" --changed-files "$files" \
      --config "$SPECASSAY_DIR/specassay-check-config.yml" 2>&1 \
      || printf 'The Thread Report did not run. Its output is above.\n'
  elif [ -s "$head" ]; then
    python3 "$HERE/manifest-table.py" "$head" \
      || printf 'The head state could not be read.\n'
  else
    printf 'No manifest on either side; the Gate has not run on this branch.\n'
  fi
  rm -f "$base" "$head" "$files"
} > "$THREAD"
  CARD_IO_MODE=block CARD_IO_BLOCK=thread-report CARD_IO_BLOCK_AT=top \
    python3 "$HERE/card-io.py" < "$THREAD" >/dev/null 2>&1 \
    || say_thread_failed=1
fi

if CARD_IO_MODE=block CARD_IO_BLOCK=review-packet python3 "$HERE/card-io.py" < "$PACKET" >/dev/null 2>&1; then
  echo "review-packet: written onto $TICKET, $(wc -l < "$PACKET" | tr -d ' ') lines"
else
  echo "review-packet: could not write the packet onto $TICKET; the card will be bare" >&2
fi
exit 0
