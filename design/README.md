# Screens

These four files are a low-fidelity sketch of the software. They are governed: a card does not change them; a hand does, through the promotion path, the same as PRD.md.

Each screen names the registry IDs it fulfils in a `FULFILS` comment in its source. The mockups are static HTML at phone width (390 px). They carry invented items only (the folding camp chair, the green-handled pruning shears, the torque wrench). Real records live in the application's own data file and never in this repository.

Nothing that names an ID appears on a screen a user sees. A person lending a chair to a neighbour has no use for a registry ID, and the screens are what this software looks like to them. The footers were visible until 2026-09-21; the table below and the `@covers` marks in the source are where the IDs live now.

| File | Screen | Fulfils |
| --- | --- | --- |
| outstanding.html | The outstanding list, oldest first, days out, a Mark returned control per item, a Lend something control | US-OUT-10, FR-OUT-10, AC-OUT-10, AC-UI-10 |
| nothing-out.html | The list when nothing is out: says so in words | AC-OUT-20, AC-UI-10 |
| lend.html | Lend something: what, to whom, date out (today unless changed); a borrower is required and the refusal is shown in place | US-LEND-10, FR-LEND-10, AC-LEND-10, AC-LEND-20, NFR-PRIV-10, AC-UI-20 |
| mark-returned.html | Mark returned: the item, the date back (today unless changed); the item leaves the list | US-RET-10, FR-RET-10, AC-RET-10, NFR-DUR-10, AC-UI-30 |

The flow: outstanding to lend and back; outstanding to mark returned and back; mark returned on the last item lands on nothing-out.

The Lend screen may show the borrower's history below the form; design/lend.html does not draw it. AC-UI-40 is where that promise lives, which is the ordinary case rather than a gap: the registry carries promises the sketch never got round to.

## What a build reads from this

- The screens are a low-fidelity sketch, for reference, and the layout is a guide, not a pixel contract. Type, spacing and color may differ; controls, order, states and words may not.
- The sketch is where the design started and it is expected to diverge from the build. When a word in a sketch differs from the registry, the registry's word holds: since 2026-10-01 the control the sketches call Mark returned is named Returned (AC-UI-30, 50, 70, 80).
- What a build must satisfy is the registry, and the controls, order, states and words that matter are named there in acceptance criteria.
- Anything not named is the build's to choose and the reviewer's to judge in Review.

## How the app is started

A reviewer opens these screens by pressing Try it on the card, and `scripts/try.sh` has
to be able to start the app without knowing anything about the branch beyond this:

    src/whms/web.py           exists and runs as `$PYTHON -m whms.web`
    --port N                  the port to listen on, and it binds 127.0.0.1 only
    WHMS_DATA_FILE            the records file, the same variable the command line reads

`$PYTHON` is whatever `scripts/python.sh` resolved: `python3` on a Mac, `python` on
Windows, where no `python3` exists and never will. The build writes the module; nothing
in the build spells the interpreter's name.

The web app reads and writes the same file the command line does. The CLI stays the engine;
the screens are a second door onto it. That is FR-UI-10's promise and not a picture, which is
why it is here and not in the list above.

Binding loopback only is not a convenience. It is the same promise NFR-PRIV-10 makes:
the records stay on this machine, and a web app that listened on every interface would
put them on the network with nobody having decided to.

## Where the picture came from

Drawn 2026-09-20 on a Claude Design canvas titled "Who Has My Stuff Screens", exported as plain HTML. The canvas is the working copy; these files are the record the project governs.
