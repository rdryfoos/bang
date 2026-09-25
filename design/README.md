# Screens

These four files are the picture of the software. They are governed: a card does not change them; a hand does, through the promotion path, the same as PRD.md.

Each screen names the registry IDs it fulfils in its footer. The mockups are static HTML at phone width (390 px). They carry invented items only (the folding camp chair, the green-handled pruning shears, the torque wrench). Real records live in the application's own data file and never in this repository.

| File | Screen | Fulfils |
| --- | --- | --- |
| outstanding.html | The outstanding list, oldest first, days out, a Mark returned control per item, a Lend something control | US-OUT-10, FR-OUT-10, AC-OUT-10, AC-UI-10 |
| nothing-out.html | The list when nothing is out: says so in words | AC-OUT-20, AC-UI-10 |
| lend.html | Lend something: what, to whom, date out (today unless changed); a borrower is required and the refusal is shown in place | US-LEND-10, FR-LEND-10, AC-LEND-10, AC-LEND-20, NFR-PRIV-10, AC-UI-20 |
| mark-returned.html | Mark returned: the item, the date back (today unless changed); the item leaves the list | US-RET-10, FR-RET-10, AC-RET-10, NFR-DUR-10, AC-UI-30 |

The flow: outstanding to lend and back; outstanding to mark returned and back; mark returned on the last item lands on nothing-out.

## What a build reads from this

- The screen is the definition of "working" for the IDs it names. A build that satisfies the sentence but not the screen is not done.
- The web app reads and writes the same file the command line does. The CLI stays the engine; the screens are a second door onto it.
- Copy on the screens is the copy: the words a person sees are these words.
- Layout is a guide, not a pixel contract. Type, spacing and colour may differ; controls, order, states and words may not.
- Style on the screens is the style: the `<style>` block each file carries and every inline `style=` on its elements are served as drawn, not reimplemented and not dropped. Layout being a guide is about where things sit at a given width, not about whether the page has a stylesheet at all. On 2026-09-25 a build read the two together as permission to serve the markup bare, and the screens came up as browser-default HTML: black Times on white, no panel, no cards. It was not wrong to read it that way, because nothing here said otherwise.
- On a wide browser the page is bounded as a panel: its own background, a 1px border in the item cards' colour, rounded corners, a soft shadow, margin above and below; on a phone it fills the screen.
- The Lend screen may show the borrower's history below the form; design/lend.html does not draw it.
- The IDs in each screen's `FULFILS` comment are for the agents and the Gate. Nothing that names an ID appears on a screen a user sees. A person lending a chair to a neighbour has no use for a registry ID, and the screens are what this software looks like to them. The footers were visible until 2026-09-21; the table above and the `@covers` marks in the source are where the IDs live now.

## How the app is started

A reviewer opens these screens by pressing Try it on the card, and `scripts/try.sh` has
to be able to start the app without knowing anything about the branch beyond this:

    src/whms/web.py           exists and runs as `$PYTHON -m whms.web`
    --port N                  the port to listen on, and it binds 127.0.0.1 only
    WHMS_DATA_FILE            the records file, the same variable the command line reads

`$PYTHON` is whatever `scripts/python.sh` resolved: `python3` on a Mac, `python` on
Windows, where no `python3` exists and never will. The build writes the module; nothing
in the build spells the interpreter's name.

Binding loopback only is not a convenience. It is the same promise NFR-PRIV-10 makes:
the records stay on this machine, and a web app that listened on every interface would
put them on the network with nobody having decided to.

## Where the picture came from

Drawn 2026-09-20 on a Claude Design canvas titled "Who Has My Stuff Screens", exported as plain HTML. The canvas is the working copy; these files are the record the project governs.
