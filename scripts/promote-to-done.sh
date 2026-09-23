#!/usr/bin/env bash
# promote-to-done: what the drag from Review to Done actually runs.
#
# The reader moves from the terminal to the board and stays there. The human act of
# promotion is the drag, and this is the promotion the template defines for an project
# with no forge behind it. It is local and nothing else:
#
#   1. merge the card's branch into local main, with a merge commit
#   2. run the gate script on that merge commit, which writes a receipt keyed by its SHA
#   3. ask scripts/done-check.py whether the predicate holds, and exit with its answer
#
# The Cannon never promotes on its own: this runs only as the Done entry check, only on
# a move a hand made, and the daemon refuses the move on any nonzero exit.
#
# A failed promotion leaves main where it was. The merge is rolled back, the receipt is
# kept and committed on its own, the card is marked, and the card stays in Review. So
# the Done column holds only cards that meet the predicate, and the failure is on the
# record rather than in a toast that scrolls away.
#
# An project with a forge behind it points the same hook at its own CI by naming a
# different command in its template. Nothing here is the Cannon's business: the daemon
# knows only the exit code and the last five lines.
#
# Written by the born-threaded practice; MIT.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT" || { echo "promote: cannot enter the project at $ROOT"; exit 2; }

CONF="$HERE/gate.conf"
# shellcheck source=/dev/null
[ -f "$CONF" ] && . "$CONF"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
JOURNAL_PREFIX="${JOURNAL_PREFIX:-journal}"

TICKET="${POTATO_TICKET_ID:-}"
FROM="${POTATO_FROM_PHASE:-}"

# This script is the promotion. scripts/no-commit-on-main.py refuses any commit on the
# default branch unless the promotion says so, and until 2026-09-20 this script set the
# flag only around the gate script, so its own receipt commit was refused by its own
# guard. The receipt was appended, staged, and left uncommitted, and the message saying
# so scrolled past in a hook nobody was reading. Set once, here, for everything this
# script does.
export BANG_PROMOTION=1

say() { printf 'promote: %s\n' "$*"; }

# What a bounced card carries. Two things, because a toast is gone by the time anyone
# looks and a line at the bottom of a four kilobyte description is a line nobody reads:
# a block at the very top of the card, above the ids line, and the blocked flag, which
# is what paints the card red on the board without anyone opening it.
mark_card() {
  printf '**Promotion refused, %s.**\n\n%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" \
    | CARD_IO_MODE=block CARD_IO_BLOCK=refusal CARD_IO_BLOCK_AT=top \
      python3 "$HERE/card-io.py" >/dev/null 2>&1 \
    || say "(the card could not be marked; the reason is in this output only)"
  CARD_IO_MODE=blocked CARD_IO_BLOCKED=true python3 "$HERE/card-io.py" >/dev/null 2>&1 \
    || say "(the card could not be flagged blocked)"
}

# A green promotion clears what a red one set: the card is on main and the flag has
# nothing left to warn about.
#
# What it says depends on whether there was anything to clear. "The promotion that was
# refused here succeeded" on a card that was never refused is a sentence about an event
# that did not happen, and a reader who has not been watching cannot tell that it did
# not. A first green says it was promoted, and that is all.
unmark_card() {
  local when state
  when="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  state="$(CARD_IO_MODE=state python3 "$HERE/card-io.py" 2>/dev/null || echo unknown)"

  if [ "$state" = "blocked" ]; then
    printf 'The promotion that was refused here succeeded at %s.\n' "$when" \
      | CARD_IO_MODE=block CARD_IO_BLOCK=refusal python3 "$HERE/card-io.py" >/dev/null 2>&1 || true
  else
    printf 'Promoted at %s.\n' "$when" \
      | CARD_IO_MODE=block CARD_IO_BLOCK=promotion python3 "$HERE/card-io.py" >/dev/null 2>&1 || true
  fi

  CARD_IO_MODE=blocked CARD_IO_BLOCKED=false python3 "$HERE/card-io.py" >/dev/null 2>&1 \
    || say "(the blocked flag could not be cleared)"
}

fail() {                      # fail <exit code> <reason...>
  local code="$1"; shift
  say "$*"
  mark_card "promotion: REFUSED $(date -u +%Y-%m-%dT%H:%M:%SZ), $*"
  exit "$code"
}

[ -n "$TICKET" ] || { say "POTATO_TICKET_ID is not set; this runs as the Cannon's Done entry check"; exit 2; }

# Done is reached from Review or not at all. A card dragged straight from anywhere else
# has not been read by anyone.
case "${FROM:-}" in
  ""|Align|Review) ;;
  *) fail 1 "a card enters Done from Align, and this one came from $FROM" ;;
esac

# The merge happens in the project's own checkout, on its default branch. If the
# checkout is somewhere else, that is the operator's business and not this script's to
# change underneath them.
current="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || { say "not a git checkout: $ROOT"; exit 2; }
if [ "$current" != "$DEFAULT_BRANCH" ]; then
  fail 2 "the project checkout is on $current, not $DEFAULT_BRANCH; nothing was merged"
fi
if ! git diff --quiet || ! git diff --cached --quiet; then
  fail 2 "the project checkout has uncommitted changes; nothing was merged"
fi

BRANCH="$(CARD_IO_MODE=branch BRANCH_PREFIX="${BRANCH_PREFIX:-potato}" python3 "$HERE/card-io.py" 2>&1)" || fail 2 "$BRANCH"
if ! git rev-parse --verify --quiet "$BRANCH^{commit}" >/dev/null; then
  fail 1 "this checkout has no branch $BRANCH, so there is nothing to promote"
fi

BEFORE="$(git rev-parse HEAD)"
say "merging $BRANCH into $DEFAULT_BRANCH at ${BEFORE:0:7}"
if ! git merge --no-ff --no-edit -m "Promote $TICKET: merge $BRANCH into $DEFAULT_BRANCH" "$BRANCH" >/dev/null 2>&1; then
  git merge --abort >/dev/null 2>&1
  fail 1 "$BRANCH does not merge into $DEFAULT_BRANCH cleanly; the merge was aborted and nothing changed"
fi
MERGE="$(git rev-parse HEAD)"
if [ "$MERGE" = "$BEFORE" ]; then
  say "$BRANCH was already on $DEFAULT_BRANCH; no merge commit was made"
fi

# The gate script writes the receipt itself, keyed by the SHA it ran on, because
# gate.conf here declares RECEIPT_SOURCE=local.
say "running the gate script at ${MERGE:0:7}"
gate_out="$(bash "$HERE/gate.sh" 2>&1)"; gate_code=$?
printf '%s\n' "$gate_out" | grep -E '^(verdict|gate: receipt)' | sed 's/^/promote:   /'

# The receipt is found by SHA, never by filename. The ledger is one append-only file
# with no date in its name, ruled 2026-09-20 after a dated name cost this hook a
# receipt: write-receipt.py named the file by the local date and stamped the record in
# UTC, and those disagree for part of every day. The whole journal is still searched,
# so a ledger from before that ruling is still read.
kept="$(mktemp)"; trap 'rm -f "$kept"' EXIT
grep -h -F "$MERGE" "$JOURNAL_PREFIX"/*.jsonl 2>/dev/null | tail -1 > "$kept"
RECEIPTS="$JOURNAL_PREFIX/receipts.jsonl"

# The manifests are not committed at all: they are ignored, because a Gate rewrites them
# on every run and no two runs agree byte for byte. Tracking them made the promotion
# leave the checkout dirty, and committing them on the default branch then made every
# card branch conflict with main on a machine-written file. The receipt is the record.
# Ruled 2026-09-20.

# The snapshot the review packet compares against. The manifests themselves are
# ignored everywhere, because a Gate rewrites them on every run and two runs never
# agree; but a packet with no base loses the one section that says what a card moved.
#
# gate.sh takes it now, on every green promotion on the default branch, so a hand's
# commit refreshes it as well as a card's. This script no longer copies it; it still
# commits it, because the file is tracked and gate.sh writes the working tree, not
# the history. The word "snapshot" below means "include it in this commit".
SNAPSHOT="$JOURNAL_PREFIX/manifest-at-main.json"

commit_receipt() {            # commit_receipt <subject> [snapshot]
  if [ ! -s "$kept" ]; then say "no receipt was written for ${MERGE:0:7}"; return 1; fi
  mkdir -p "$JOURNAL_PREFIX"
  if ! grep -qhF "$MERGE" "$JOURNAL_PREFIX"/*.jsonl 2>/dev/null; then cat "$kept" >> "$RECEIPTS"; fi
  if [ "${2:-}" = "snapshot" ] && [ -s "$SNAPSHOT" ]; then
    say "the snapshot gate.sh took at ${MERGE:0:7} goes in with this commit"
  fi
  git add -- "$JOURNAL_PREFIX" || return 1
  git -c user.name="Cannon Promotion" -c user.email="cannon-worker@dryfoos.com" \
      commit -q -m "$1" -- "$JOURNAL_PREFIX" || return 1
  return 0
}

if [ "$gate_code" != 0 ]; then
  # Roll the merge back so the default branch never carries a red one, then put the
  # receipt back and commit it alone. The reset discards the working tree's copy of the
  # receipt, which is why it was kept aside first.
  git reset --hard "$BEFORE" >/dev/null 2>&1 || say "(the rollback failed; $DEFAULT_BRANCH is at $(git rev-parse --short HEAD))"
  if commit_receipt "Gate red at ${MERGE:0:7}, promotion of $TICKET rolled back"; then
    say "the merge was rolled back; the receipt for ${MERGE:0:7} is committed on $DEFAULT_BRANCH"
  else
    say "WARNING: the receipt for ${MERGE:0:7} could not be committed; $DEFAULT_BRANCH is dirty"
  fi
  fail 1 "the Gate was red at ${MERGE:0:7} (exit $gate_code); $TICKET stays in Review"
fi

commit_receipt "Gate green at ${MERGE:0:7}, promotion of $TICKET (with the manifest snapshot at ${MERGE:0:7})" snapshot \
  || say "(the receipt is written but not committed; the check reads the working tree either way)"

# The promotion has happened. The predicate is still the check's to state, not this
# script's to assume, so the last word is done-check reading the receipt for the SHA.
unmark_card
say "asking the Done check whether the predicate holds"
if out="$(python3 "$HERE/done-check.py" --receipts local --default-branch "$DEFAULT_BRANCH" --journal "$JOURNAL_PREFIX" 2>&1)"; then
  printf '%s\n' "$out"
  say "$TICKET may enter Done"
  exit 0
fi
code=$?
printf '%s\n' "$out"
fail "$code" "the promotion ran but the Done check refused it"
