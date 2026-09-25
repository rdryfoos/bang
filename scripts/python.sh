# python.sh: the one place this project decides what runs Python. Sourced, not run.
#
#     . "$HERE/python.sh" || exit 1
#     "$PYTHON" "$HERE/column-check.py" --tasks-ticked
#
# Why there is a file for this. On a Mac the interpreter is `python3` and there is no
# `python` at all. On Windows there is no `python3` and there never will be: the
# python.org installer lays down `python.exe` and `py.exe` and no `python3.exe`, and
# the name `python3` is taken by an App Execution Alias that opens the Microsoft Store
# and exits. The Dell run on 2026-09-25 installed Python 3.12.10 with winget, watched
# `python --version` answer, and watched `python3` go on not resolving.
#
# So the name is not a constant and no script may spell it. This resolves it once, by
# asking, and every caller uses $PYTHON.
#
# The test is what the thing prints, not whether it is on the path. The Store stub is
# on the path and answers `command -v`; it is not an interpreter, and it fails this
# test on either name without needing to be recognised as itself.
#
# Written by the born-threaded practice; MIT.

# The first name on the path that says it is Python 3. Prints it, or nothing.
resolve_python() {
  local candidate version
  for candidate in python3 python; do
    command -v "$candidate" >/dev/null 2>&1 || continue
    version="$("$candidate" --version 2>&1)" || continue
    case "$version" in
      "Python 3"*) printf '%s\n' "$candidate"; return 0 ;;
    esac
  done
  return 1
}

PYTHON="${PYTHON:-$(resolve_python)}"

if [ -z "${PYTHON:-}" ]; then
  echo "python.sh: no Python 3 on this machine." >&2
  echo "  Neither python3 nor python printed a line beginning 'Python 3'." >&2
  case "$(uname -s)" in
    MINGW*|MSYS*)
      # PowerShell by name, not "a terminal". This message is read inside Git Bash,
      # and the window it is asking for is a different one with a different name in
      # the Start menu. A reader told to "open a new window" opens another Git Bash.
      echo "  Open PowerShell, which is not this window, and run:" >&2
      echo "    winget install --id Python.Python.3.12 -e --source winget" >&2
      echo "  Then close this Git Bash window and open a new Git Bash, because a" >&2
      echo "  window reads the path when it opens and never again." >&2
      echo "  If python3 appears to exist and prints nothing, that is the Microsoft" >&2
      echo "  Store's App Execution Alias, not an interpreter." >&2
      ;;
    *)
      echo "  Install Python 3 and try again." >&2
      ;;
  esac
  return 1 2>/dev/null || exit 1
fi

export PYTHON
