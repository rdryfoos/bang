#!/usr/bin/env bash
# gate: the project's one deaf check. Invoked from the worktree root with no arguments
# by the runner (its fixed command) and by CI. Floor tier first, first red stops
# (exit 1); then every gate-tier check, every red listed (exit 2); missing tool exit 3.
# Writes the Thread Report into the PR body's two marked sections through the host's
# CLI, from a file, never a command line. Judges nothing.
# Specification: the box's cargo/gate-script.md. Written by the born-threaded practice; MIT.
# Two checks were removed on 2026-09-23 by Rik's ruling, after the first cold run: the
# secrets scan and the dependency advisory scan. Neither was on BANG.md's list of what
# this project fetches, so a Build worker that met MISSING TOOL installed both from
# GitHub releases on its own to get past the preflight, which is a check satisfied by
# fetching rather than by being true. Neither was load-bearing here: this project has no
# dependencies at all, so the advisory scan had no lockfile to read and said so on every
# run, and it holds no credential of any kind, while the promise it does make about
# borrower names is kept by no-records-in-repo.py and test_repo_privacy.py, which a
# secrets scanner cannot make. The tiers are renumbered rather than left with gaps.
# The source project's
# own copy lives at gate/gate.sh rather than scripts/, because its SURFACE.md row M4 holds
# scripts/ to zero network capability and this script writes the PR body through gh; see
# that project's decision 0048.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(pwd)"
CONF="$HERE/gate.conf"
[ -f "$CONF" ] && . "$CONF"
JOURNAL_PREFIX="${JOURNAL_PREFIX:-journal}"
RECEIPT_SOURCE="${RECEIPT_SOURCE:-forge}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
SPECASSAY_CHECK="${SPECASSAY_CHECK:-.specify/extensions/specassay-check/scripts/check-traceability.sh}"
REPORT="$(mktemp)"; TELEMETRY="$(mktemp)"; trap 'rm -f "$REPORT" "$TELEMETRY"' EXIT
line() { printf '%s\n' "$*" | tee -a "$REPORT"; }
tline() { printf '%s\n' "$*" >> "$TELEMETRY"; }
floor_red=0; gate_reds=0; verdict_code=0

# Card and daemon
CARD="${POTATO_TICKET_ID:-}"
if [ -z "$CARD" ]; then
  br="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  CARD="${br#*/}"; [ "$CARD" = "$br" ] && CARD=""
fi
DAEMON=""
if [ -n "${POTATO_DAEMON_HOST:-}" ] && [ -n "${POTATO_DAEMON_PORT:-}" ]; then DAEMON="http://${POTATO_DAEMON_HOST}:${POTATO_DAEMON_PORT}"; fi
HEAD_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
IN_CI=0; [ -n "${CI:-}" ] && IN_CI=1

# Preflight: every tool located, versions printed. Missing tool is exit 3.
line "gate: preflight"
need() { # name, command, version-args
  if ! command -v "$2" >/dev/null 2>&1; then line "  MISSING TOOL: $1 ($2)"; return 1; fi
  v="$("$2" $3 2>&1 | head -1 | tr -d '\r')"; line "  $1: $v"; TOOLCHAIN="${TOOLCHAIN:-}${1}=$v; "; return 0
}
missing=0
need python3 python3 --version || missing=1
need gh gh --version || missing=1
need git git --version || missing=1
[ -x "$HERE/check-anchors.py" ] || { line "  MISSING TOOL: check-anchors ($HERE/check-anchors.py)"; missing=1; }
[ -f "$SPECASSAY_CHECK" ] || { line "  MISSING TOOL: specassay check ($SPECASSAY_CHECK)"; missing=1; }
if [ "$missing" = 1 ]; then line "verdict: MISSING TOOL, exit 3"; verdict_code=3; fi

if [ "$verdict_code" = 0 ]; then
  # Floor tier
  line "gate: floor tier"
  # 0 scripts compile under the floor Python. A construct that only parses on a newer
  # interpreter is a script that works until the day it runs, and this project found one
  # the hard way: an f-string with a nested same-type quote, valid from 3.12 and a
  # syntax error on 3.9, run-through in a branch of this very script.
  if out="$(python3 -m compileall -q "$HERE" 2>&1)"; then line "  0 scripts compile: green, $(python3 -c 'import sys;print("python "+".".join(map(str,sys.version_info[:3])))')"; else line "  0 scripts compile: RED"; printf '%s\n' "$out" | head -20 | sed 's/^/    /' | tee -a "$REPORT"; floor_red=1; fi

  if [ "$floor_red" = 1 ]; then line "verdict: FLOOR RED, exit 1"; verdict_code=1
  else
    line "gate: gate tier"
    # 1 anchors
    if out="$(python3 "$HERE/check-anchors.py" 2>&1)"; then line "  1 anchors: green, ${out##*$'\n'}"; else line "  1 anchors: RED"; printf '%s\n' "$out" | sed 's/^/    /' | tee -a "$REPORT"; gate_reds=$((gate_reds+1)); fi
    # 2 tests
    if [ -n "${TEST_COMMAND:-}" ]; then
      if bash -c "$TEST_COMMAND" >"$REPORT.tests" 2>&1; then line "  2 tests: green (results at ${TEST_RESULTS:-unset})"; else line "  2 tests: RED"; tail -40 "$REPORT.tests" | sed 's/^/    /' | tee -a "$REPORT"; gate_reds=$((gate_reds+1)); fi
      rm -f "$REPORT.tests"
    else line "  2 tests: RED, no test command configured in gate.conf"; gate_reds=$((gate_reds+1)); fi
    # 2b governed files: a card may not change the machinery that judges it
    if out="$(python3 "$HERE/governed-files.py" --base "$DEFAULT_BRANCH" 2>&1)"; then line "  2b governed files: ${out#governed-files: }"; else line "  2b governed files: RED"; printf '%s\n' "$out" | sed 's/^governed-files: /    /' | tee -a "$REPORT"; gate_reds=$((gate_reds+1)); fi
    # 3 specassay
    if out="$(bash "$SPECASSAY_CHECK" 2>&1)"; then line "  3 specassay: green"; else line "  3 specassay: RED"; printf '%s\n' "$out" | grep -E 'FAIL|GAP|orphan|drift|gate' | head -40 | sed 's/^/    /' | tee -a "$REPORT"; gate_reds=$((gate_reds+1)); fi
    # 6 advisories below the floor
    # 4 docs owed
    owed="$(python3 - <<'PY'
import re,subprocess,glob
owed=[]
for path in glob.glob("**/*.md", recursive=True):
    if path.startswith((".potato/",".specify/")): continue
    try: text=open(path,encoding="utf-8",errors="ignore").read()
    except Exception: continue
    m=re.search(r"^verified:\s*([0-9a-f]{7,40})", text, re.M)
    if not m: continue
    sha=m.group(1); targets=re.findall(r"@describes\s+(\S+)", text)
    for t in targets:
        t=t.rstrip(",.;")
        if not glob.glob(t): continue
        r=subprocess.run(["git","log","--oneline",f"{sha}..HEAD","--",t],capture_output=True,text=True)
        if r.stdout.strip(): owed.append(path); break
print(", ".join(sorted(set(owed))) if owed else "")
PY
)"
    if [ -n "$owed" ]; then line "  4 docs owed: $owed"; else line "  4 docs owed: none"; fi
    if [ "$gate_reds" -gt 0 ]; then line "verdict: GATE RED, $gate_reds red line(s), exit 2"; verdict_code=2; else line "verdict: GREEN, exit 0"; fi
  fi
fi
line "toolchain: ${TOOLCHAIN:-none}"
line "attempt: head $HEAD_SHA, card ${CARD:-unknown}"

# Telemetry, only when the daemon is reachable
PHASE=""
if [ -n "$DAEMON" ] && [ -n "$CARD" ] && [ -n "${POTATO_PROJECT_ID:-}" ]; then
  python3 - "$DAEMON" "$POTATO_PROJECT_ID" "$CARD" "${CANNON_HOME:-}" "$JOURNAL_PREFIX" "$TELEMETRY" <<'PY'
import json,sys,urllib.request,urllib.parse,glob,os
daemon,project,card,cannon_home,prefix,out=sys.argv[1:7]
def get(u):
    with urllib.request.urlopen(u,timeout=20) as r: return json.loads(r.read().decode() or "null")
lines=[]
try:
    t=get(f"{daemon}/api/tickets/{urllib.parse.quote(project,safe='')}/{card}")
    phase=t.get("phase",""); open(out+".phase","w").write(phase)
    lines.append(f"attempt: phase {phase}")
except Exception as e:
    lines.append(f"attempt: phase unavailable ({e.__class__.__name__})")
cost=0.0; toks={"input":0,"output":0,"cache_creation":0,"cache_read":0}; n=0
try:
    sessions=[s for s in get(f"{daemon}/api/sessions") or [] if (s.get("ticketId") or s.get("ticket_id"))==card]
    for s in sessions:
        sid=s.get("id"); 
        for lp in glob.glob(os.path.join(cannon_home,"sessions",f"{sid}.jsonl")) if cannon_home else []:
            for raw in open(lp,encoding="utf-8",errors="ignore"):
                try: ev=json.loads(raw)
                except Exception: continue
                inner=ev.get("raw") if isinstance(ev,dict) else None
                if isinstance(inner,str):
                    try: ev=json.loads(inner)
                    except Exception: continue
                if isinstance(ev,dict) and ev.get("type")=="result":
                    n+=1; cost+=float(ev.get("total_cost_usd") or 0)
                    u=ev.get("usage") or {}
                    toks["input"]+=int(u.get("input_tokens") or 0); toks["output"]+=int(u.get("output_tokens") or 0)
                    toks["cache_creation"]+=int(u.get("cache_creation_input_tokens") or 0); toks["cache_read"]+=int(u.get("cache_read_input_tokens") or 0)
    lines.append(f"cost: {n} result event(s), total_cost_usd {cost:.4f}, tokens in {toks['input']} out {toks['output']} cache_creation {toks['cache_creation']} cache_read {toks['cache_read']}")
except Exception as e:
    lines.append(f"cost: unavailable ({e.__class__.__name__})")
bounces=0
for jp in glob.glob(os.path.join(prefix,"*.jsonl")):
    for raw in open(jp,encoding="utf-8",errors="ignore"):
        try: rec=json.loads(raw)
        except Exception: continue
        if rec.get("kind")=="transition" and rec.get("card")==card and rec.get("phase")=="Build": bounces+=1
lines.append(f"bounce count: Build entered {bounces} time(s), from the journal")
open(out,"a").write("\n".join(lines)+"\n")
PY
  [ -f "$TELEMETRY.phase" ] && PHASE="$(cat "$TELEMETRY.phase")" && rm -f "$TELEMETRY.phase"
  # shared load
  files_here="$(git diff --name-only "origin/$DEFAULT_BRANCH"...HEAD 2>/dev/null | sort -u)"
  shared="$(gh pr list --state open --json number,headRefName,files --jq '.[] | select(.headRefName != "'"$(git rev-parse --abbrev-ref HEAD)"'") | "\(.number) " + ([.files[].path] | join(" "))' 2>/dev/null | python3 -c '
import sys
mine=set(l.strip() for l in open(sys.argv[1]) if l.strip())
out=[]
for l in sys.stdin:
    parts=l.split(); 
    if not parts: continue
    num=parts[0]; common=sorted(mine & set(parts[1:]))
    if common: out.append("PR #%s: %s" % (num, ", ".join(common)))
print("; ".join(out) if out else "none")' <(printf '%s\n' "$files_here"))"
  tline "shared load: $shared"
fi

# The local receipt. An project with no forge behind it has no CI run to point at, so the
# proof that the Gate passed on a commit is written here, by the run itself, keyed by the
# SHA it ran on. Three conditions, all required:
#
#   RECEIPT_SOURCE=local   the project declares it has no forge to attest for it
#   BANG_PROMOTION=1     a promotion invoked this run, set by promote-to-done.sh
#   on DEFAULT_BRANCH      the fact recorded is about the project's history
#
# The middle one was added 2026-09-20 after a Build-phase runner, standing in the primary
# checkout on the default branch because a worktree had failed, wrote three receipts
# against HEAD that no promotion produced. A receipt is a claim about a promotion, so
# only a promotion may write one. Every other invocation of this script is read-only.
#
# It writes into the recorder's journal rather than a second one. The record is its own
# kind and carries actor "orchestrator": a receipt written by a script is not a hand's
# note, and the recorder's one-shot --note mode stamps actor "hand", which would be an
# attribution this project does not permit.
if [ "$RECEIPT_SOURCE" = "local" ] && [ "${BANG_PROMOTION:-}" = "1" ]; then
  cur_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  if [ "$cur_branch" = "$DEFAULT_BRANCH" ]; then
    mkdir -p "$JOURNAL_PREFIX"
    receipt_result=pass; [ "$verdict_code" = 0 ] || receipt_result=fail
    receipt_out="$(RECEIPT_PREFIX="$JOURNAL_PREFIX" RECEIPT_SHA="$HEAD_SHA" \
      RECEIPT_RESULT="$receipt_result" RECEIPT_CODE="$verdict_code" RECEIPT_CARD="${CARD:-}" \
      python3 "$HERE/write-receipt.py" 2>&1)" && line "$receipt_out" \
      || line "gate: receipt not written (non-fatal): $receipt_out"

    # The snapshot the Thread Report compares a card against. It used to be taken by
    # promote-to-done.sh, so only a card's promotion refreshed it and a hand's commit
    # on main did not. On 2026-09-21 this project's snapshot was eight hours stale and
    # from another board entirely, and every Thread Report said so in its first line
    # while reporting the whole UI family as newly created.
    #
    # Taken here instead, because here is where every green promotion passes: a card's
    # and a hand's alike. The manifests are untracked everywhere else, so this is the
    # one copy anything reads, and it is written only on a green run, only on the
    # default branch, only under BANG_PROMOTION. A red run leaves the last good
    # snapshot alone rather than replacing it with a picture of a tree that was
    # rolled back.
    if [ "$verdict_code" = 0 ] && [ -s trace-manifest.json ]; then
      if cp trace-manifest.json "$JOURNAL_PREFIX/manifest-at-main.json"; then
        line "gate: snapshot taken at ${HEAD_SHA:0:7} into $JOURNAL_PREFIX/manifest-at-main.json"
      else
        line "gate: snapshot not taken (non-fatal)"
      fi
    fi
  else
    line "gate: no receipt, this run is on $cur_branch and receipts are written on $DEFAULT_BRANCH only"
  fi
elif [ "$RECEIPT_SOURCE" = "local" ]; then
  line "gate: no receipt, this run is not a promotion (BANG_PROMOTION is unset); read-only"
fi

# Write the PR body: section one always, section two only when telemetry exists
PR_NUM="$(gh pr list --state all --head "$(git rev-parse --abbrev-ref HEAD)" --json number --jq '.[0].number' 2>/dev/null || true)"
if [ -n "$PR_NUM" ] && [ "$PR_NUM" != "null" ]; then
  body_file="$(mktemp)"; gh pr view "$PR_NUM" --json body --jq .body > "$body_file" 2>/dev/null || true
  python3 - "$body_file" "$REPORT" "$TELEMETRY" <<'PY'
import sys
body_path,report_path,tele_path=sys.argv[1:4]
body=open(body_path).read()
B1,E1="<!-- thread-report:begin -->","<!-- thread-report:end -->"
B2,E2="<!-- project-telemetry:begin -->","<!-- project-telemetry:end -->"
def replace(body,b,e,content):
    if b in body and e in body and body.index(b)<body.index(e):
        pre=body[:body.index(b)+len(b)]; post=body[body.index(e):]
        return pre+"\n"+content.rstrip("\n")+"\n"+post
    return body
report=open(report_path).read()
body=replace(body,B1,E1,"```\n"+report+"```")
tele=open(tele_path).read()
if tele.strip():
    body=replace(body,B2,E2,"```\n"+tele+"```")
open(body_path,"w").write(body)
PY
  gh pr edit "$PR_NUM" --body-file "$body_file" >/dev/null 2>&1 || line "gate: PR body write failed (non-fatal)"
  rm -f "$body_file"
  if [ "$verdict_code" = 0 ] && [ "$PHASE" = "Gate" ]; then gh pr ready "$PR_NUM" >/dev/null 2>&1 && line "gate: PR #$PR_NUM marked ready for review"; fi
fi
exit "$verdict_code"
