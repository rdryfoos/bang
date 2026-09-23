# The first cards

Three cards, created in the Ideas column in this order and no others. Each one is a
title and a short description in the owner's own words. None of them carries an ID:
the IDs live in `PRD.md`, and a card gets its ids line when somebody decides which
promises that card is for.

The first card is the one to drag. The other two are there so the board is not empty
behind it, and so you can see what a queue looks like.

---

## 1. Lend and return in the browser

Drag this card to Spec and watch what happens.

As the owner, I want to lend, see what is out, and mark things returned on a screen
in my browser, so I am not tied to the command line. The screens are in `design/`.
Read `design/README.md` first.

## 2. What I have lent before

As the owner, when I lend something I want to see what I have lent that person
before and whether it came back, so I can decide with the history in front of me.

## 3. Mark a thing returned

As the owner, I mark a thing returned and it stops nagging me.

---

## Why these three

The project you cloned already has a working command-line lending tracker, its
specification, and its tests. It does not have a browser. So the first card is the
one that turns a tool you have to remember commands for into something you can look
at, which is the largest single change the project has left in it and the one whose
result you can see without reading any code.

The second and third are smaller and deliberately different in shape. One adds
something to a screen that does not exist yet, so it cannot start until the first is
done. One is about the command line only, so its proof is a transcript rather than a
page. Between them they show the two things the board does when work is not ready:
it waits, and it says why.
