#!/usr/bin/env python3
"""Script three: every #anchor cited in the project's Markdown resolves at HEAD.
Bare #anchor resolves in its own file; FILE.md#anchor resolves in that file.
Flags and never moves: the exit code is the flag. Born in the source project, 2026-09-06; carried in the box."""
import re, sys, pathlib
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
files = sorted(p for p in root.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(root).parts))
defs = {f: set(re.findall(r"\{#([A-Za-z][\w-]*)\}", f.read_text())) for f in files}
byname = {f.name: a for f, a in defs.items()}
cite = re.compile(r"([\w./-]+\.md)#([A-Za-z][\w-]*)|(?<![\w{/#&])#([A-Za-z][\w-]*)")
bad = 0
for f in files:
    for n, line in enumerate(f.read_text().splitlines(), 1):
        for target, qualified, bare in cite.findall(line):
            anchor = qualified or bare
            anchors = byname.get(pathlib.Path(target).name) if target else defs[f]
            if anchors is None or anchor not in anchors:
                bad += 1
                print(f"{f.relative_to(root)}:{n}: unresolved #{anchor}" + (f" in {target}" if target else ""))
print(f"{len(files)} files, {sum(map(len, defs.values()))} anchors defined, {bad} unresolved")
sys.exit(1 if bad else 0)
