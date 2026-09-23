# The first cards

Three cards, created in the Ideas column in this order and no others. Each one is a
title and a description in the owner's own words.

The description of each card is the fenced block under its heading, exactly as it is
written there, newlines and all. `BANG.md` step 10 carries the same three blocks, and
`tests/test_shipped_promises.py` fails if the two files ever stop agreeing.

The first card is the one to drag. The other two are there so the board is not empty
behind it, and so you can see what a queue looks like.

---

## 1. Lend and return in the browser

```
Drag this card to Spec and watch what happens.
As the owner, I want to lend, see what is out, and mark things returned on a screen in my browser, so I am not tied to the command line. The screens are in design/. Read design/README.md first.
Every write the screens make goes through the engine (NFR-ENG-10); the test will refuse anything else.
ids: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30
```

## 2. What I have lent before

```
As the owner, when I lend something I want to see what I have lent that person before and whether it came back, so I can decide with the history in front of me.
ids: US-UI-20, AC-UI-40
```

## 3. Remind the borrower

```
As the owner, I want the app to nudge me about a thing that has been out too long.

Nothing in `PRD.md` promises this yet. It is here to show what the board does with a card whose promise does not exist: it waits, and it says why.
```

---

## Why these three

The project you cloned already has a working command-line lending tracker, its
specification, and its tests. It does not have a browser. So the first card is the
one that turns a tool you have to remember commands for into something you can look
at, which is the largest single change the project has left in it and the one whose
result you can see without reading any code.

It is also the card with the least to ask about. `PRD.md` promises the five things it
carries, and `design/` draws all four screens with `design/README.md` saying which
parts of them are binding. A Spec worker reading that has a brief, not a question.

The second and third are smaller and deliberately different in shape. The second adds
something to a screen that does not exist yet, so it cannot start until the first is
done, and its own promise is the one thing `design/README.md` declines to draw, so it
is the card where a question is natural and a person has to answer it. The third
carries no ID at all, because nothing in `PRD.md` promises it, so it cannot run.
Between them they show the two things the board does when work is not ready: it waits,
and it says why.
