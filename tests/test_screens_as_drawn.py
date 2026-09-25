"""The screens are served as drawn, and the styles are part of what is drawn.

On 2026-09-25 puppy's BAN-1 went through Spec, Build and the Gate, reached Review, and
Try it served the four screens as browser-default HTML: black Times on white, no panel,
no cards. Every word on every screen was right. Nothing in the build was wrong by the
contract it was given, which said the copy is binding and layout is a guide and said
nothing at all about the `<style>` block each design file carries.

So the contract now says it, in `design/README.md`, which is the governed copy, and in
`cannon-template/agents/build.md`, which is what the worker reads. These check that the
two agree, that the design files really do carry what is being promised, and that the
app serves it once there is an app.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design"
BUILD_MD = ROOT / "cannon-template" / "agents" / "build.md"

STYLE_LINE = ("Style on the screens is the style: the `<style>` block each file "
              "carries and every inline `style=` on its elements are served as "
              "drawn, not reimplemented and not dropped.")


def _flat(text):
    """The prose as one line, because both files are wrapped."""
    return " ".join(text.split())


def test_the_contract_and_the_worker_say_it_in_the_same_words():
    """The governed copy and the prompt are one sentence or neither.

    `design/README.md` is the contract and `build.md` is what a worker actually reads
    before it writes a screen. A worker that never opens the README is the ordinary
    case, so the sentence has to be in the prompt; a reader deciding what the build
    owes them looks in the README. Two copies, and this is what stops them drifting.
    """
    readme = _flat((DESIGN / "README.md").read_text(encoding="utf-8"))
    build = _flat(BUILD_MD.read_text(encoding="utf-8"))
    flat_line = _flat(STYLE_LINE)
    assert flat_line in readme, "design/README.md no longer makes style binding"
    assert flat_line in build, "build.md no longer tells the worker to serve it as drawn"


def test_build_md_says_layout_being_a_guide_is_not_permission_to_serve_it_bare():
    """The exact misreading, named, because it is a reasonable one.

    "Layout is a guide" and "serve the page with no stylesheet" are one step apart if
    nobody says they are not, and the card that took that step was not being careless.
    """
    build = _flat(BUILD_MD.read_text(encoding="utf-8"))
    assert "served as drawn, styles included" in build
    assert "not permission to serve the markup bare" in build


def _screens():
    return sorted(p for p in DESIGN.glob("*.html"))


def test_every_screen_carries_the_style_the_contract_promises():
    """The promise is about a thing that has to be there for the promise to mean anything.

    If a screen loses its `<style>` block, "served as drawn" quietly becomes a promise
    to serve nothing, and the build that serves nothing is keeping it.
    """
    screens = _screens()
    assert len(screens) == 4, "design/ no longer holds four screens: %s" % [s.name for s in screens]
    for screen in screens:
        text = screen.read_text(encoding="utf-8")
        assert re.search(r"<style\b", text), "%s carries no <style> block" % screen.name
        assert 'style="' in text, "%s carries no inline style attributes" % screen.name


def _style_signature():
    """A line out of the screens' own `<style>` block, shared by all four."""
    text = (DESIGN / "outstanding.html").read_text(encoding="utf-8")
    block = re.search(r"<style\b[^>]*>(.*?)</style>", text, re.S)
    assert block, "outstanding.html has no <style> block to take a signature from"
    for line in block.group(1).splitlines():
        if line.startswith("body{"):
            return line.strip()
    raise AssertionError("no body rule in outstanding.html's style block")


def test_the_served_page_carries_the_screens_own_style():
    """The one that matters, and it arms itself when card one lands.

    The seed ships no web app: the screens are card one's work, which is why there is
    nothing here to assert against yet. This is written now rather than later because
    the run that found the defect is this run, and a test added after the next card
    would be a test written by somebody who had already been told the answer.

    It skips while there is no app and asserts the moment there is one.
    """
    served = ROOT / "src" / "whms" / "pages.py"
    web = ROOT / "src" / "whms" / "web.py"
    if not served.exists() and not web.exists():
        pytest.skip(
            "no web app in the seed yet: the screens are card one's work, and this "
            "asserts as soon as src/whms/pages.py or web.py exists")

    source = "\n".join(
        path.read_text(encoding="utf-8") for path in (served, web) if path.exists())
    signature = _style_signature()
    assert "<style" in source, (
        "the app serves no <style> block; design/README.md says the screens are served "
        "as drawn, styles included")
    assert signature in source, (
        "the app's style is not the screens' own. design/ draws:\n  %s\nand the served "
        "page does not carry it." % signature)
