"""The screens are a sketch; the registry is what a build must satisfy.

On 2026-09-25 a card built the four screens, passed the Gate, reached Review, and served
black Times on white with no panel and no cards. The first answer was to make the styles
binding: `design/README.md` and `build.md` both grew a sentence saying the `<style>`
block is served as drawn. On 2026-09-29 Rik ruled the other way. The four files in
`design/` are a low-fidelity sketch for reference, and what a build must satisfy is the
registry; a nav bar or a palette is the build's to choose unless an acceptance criterion
says otherwise, and a state or a word an acceptance criterion names is not.

That ruling lives in four files: the governed README, and the three prompts a worker
actually reads. These check that the four agree, that the withdrawn contract has not
crept back in, and that the map still points at screens that exist and IDs the registry
carries.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design"
AGENTS = ROOT / "cannon-template" / "agents"
PRD = ROOT / "PRD.md"

# The section's bullets, in order, as design/README.md writes them. The file is the
# ruling and this is a copy of it: a bullet reworded there and not here is this test's
# fault, not the file's.
#
# It was three bullets from 2026-09-29 until a hand added the second one and extended
# the first on 2026-10-01. What came back with the first is the pixel-contract sentence
# that the September ruling had dropped, which is a reversal and not a slip: a sketch
# that binds nothing about layout left a build free to redraw the thing at any width,
# and Review had no words for saying so.
SKETCH = ("The screens are a low-fidelity sketch, for reference, and the layout is a "
          "guide, not a pixel contract. Type, spacing and color may differ; controls, "
          "order, states and words may not.")
DIVERGES = ("The sketch is where the design started and it is expected to diverge from "
            "the build. When a word in a sketch differs from the registry, the "
            "registry's word holds: since 2026-10-01 the control the sketches call Mark "
            "returned is named Returned (AC-UI-30, 50, 70, 80).")
REGISTRY = ("What a build must satisfy is the registry, and the controls, order, states "
            "and words that matter are named there in acceptance criteria.")
UNNAMED = ("Anything not named is the build's to choose and the reviewer's to judge in "
           "Review.")

BULLETS = (SKETCH, DIVERGES, REGISTRY, UNNAMED)

# The sentence the September ruling withdrew and a hand put back. Pinned on its own,
# because it is the clause a reviewer leans on when a build looks nothing like the
# sketch, and because it has now been taken out once.
PIXEL = "the layout is a guide, not a pixel contract"

# What the prompts share with the first bullet. All three call the screens a sketch; the
# two worker prompts carry the ruling's own sentence, and ticket-qa.md says "a
# low-fidelity sketch of the software" in Buddy's own words, which is why the phrase all
# three must have is the shorter one.
A_SKETCH = "low-fidelity sketch"
A_SKETCH_FULL = "low-fidelity sketch, for reference."

FORK = ("A nav bar or a palette is delivery unless an acceptance criterion says "
        "otherwise; a state or a word an acceptance criterion names is not.")

# The sentences the 2026-09-29 ruling withdrew and that are still withdrawn. A prompt or
# a contract that says any of these again is saying the opposite of the bullets, in the
# file a worker reads first.
#
# "Layout is a guide, not a pixel contract" was on this list and is not any more: a hand
# put it back on 2026-10-01, in the first bullet, and PIXEL above pins it. A guard
# against a sentence the ruling now wants is a trap, and this one was already vacuous by
# accident, because the bullet says "the layout" and the needle said "Layout".
WITHDRAWN = (
    "the copy on a screen is the copy",
    "Copy on the screens is the copy",
    "the definition of \"working\"",
    "the definition of working",
    "Style on the screens is the style",
    "served as drawn, styles included",
)


def _flat(text):
    """The prose as one line, because every one of these files is wrapped."""
    return " ".join(text.split())


def _readme():
    return _flat((DESIGN / "README.md").read_text(encoding="utf-8"))


def _section():
    """"What a build reads from this", as its own lines, up to the next heading."""
    text = (DESIGN / "README.md").read_text(encoding="utf-8")
    body = text.split("## What a build reads from this", 1)[1]
    return body.split("\n## ", 1)[0]


def test_the_readme_carries_the_ruling_in_its_bullets():
    """The governed copy says what a build reads, in the words of the ruling."""
    readme = _readme()
    for sentence in BULLETS:
        assert _flat(sentence) in readme, (
            "design/README.md no longer says: %s" % sentence)


def test_the_layout_is_a_guide_and_not_a_pixel_contract():
    """The clause a reviewer leans on, pinned on its own because it has been lost once.

    The September ruling dropped it with the rest of the old contract, which left a
    sketch binding nothing about layout at all: a build could redraw the thing at any
    width and satisfy every criterion. A hand put it back on 2026-10-01, in the first
    bullet, beside the sentence that says what may differ and what may not.
    """
    readme = _readme()
    assert PIXEL in readme, "design/README.md no longer says %r" % PIXEL
    assert "Type, spacing and color may differ; controls, order, states and words may not." in readme, (
        "the pixel clause is there without the sentence that says what it means")

    bullets = [_flat(line) for line in _section().splitlines() if line.startswith("- ")]
    carrying = [i for i, b in enumerate(bullets, 1) if PIXEL in b]
    assert carrying == [1], (
        "the pixel clause is on bullet(s) %s; it belongs with the sketch sentence on the "
        "first" % carrying)


def test_the_section_is_four_bullets_and_nothing_else():
    """Four, in this order, and no fifth.

    The section this replaces had grown to eight, and the two that caused the trouble
    were the two added last, each one a reasonable answer to a real run. The count is
    what stops the next reasonable answer being added here instead of to the registry,
    where a promise is a promise rather than a paragraph a build has to weigh. It was
    three until 2026-10-01 and is four now, which is the number this test follows rather
    than argues with.
    """
    bullets = [line for line in _section().splitlines() if line.startswith("- ")]
    assert len(bullets) == len(BULLETS), (
        "the section carries %d bullets, not %d:\n%s"
        % (len(bullets), len(BULLETS), "\n".join(bullets)))
    for n, (bullet, expected) in enumerate(zip(bullets, BULLETS), 1):
        assert _flat(bullet) == "- " + _flat(expected), (
            "bullet %d is not the one this test expects.\n  file: %s\n  test: %s"
            % (n, _flat(bullet), _flat(expected)))


def test_the_prompts_say_it_in_the_same_words_as_the_contract():
    """The three prompts a worker reads carry the ruling, not a paraphrase of it.

    A worker that opens `design/README.md` is the lucky case; the ordinary one reads its
    own prompt and nothing else. Spec is in the list because a specification written
    against the pictures binds a build that never saw them.
    """
    for name in ("build.md", "spec.md", "ticket-qa.md"):
        prompt = _flat((AGENTS / name).read_text(encoding="utf-8"))
        assert A_SKETCH in prompt, (
            "%s no longer calls the screens a sketch" % name)
        if name in ("build.md", "spec.md"):
            assert A_SKETCH_FULL in prompt, (
                "%s no longer carries the ruling's own sentence" % name)
        assert "What a build must satisfy is the registry" in prompt, (
            "%s no longer says the registry is what binds" % name)


def test_build_and_qa_carry_the_fork_between_delivery_and_a_named_promise():
    """The sentence a worker acts on, and the one a reader is answered with."""
    build = _flat((AGENTS / "build.md").read_text(encoding="utf-8"))
    assert _flat(FORK) in build, "build.md no longer carries the delivery fork"

    qa = _flat((AGENTS / "ticket-qa.md").read_text(encoding="utf-8"))
    assert ("a nav bar or a palette is delivery unless an acceptance criterion says "
            "otherwise, and a state or a word an acceptance criterion names is not"
            ) in qa, "ticket-qa.md no longer carries the delivery fork"


def test_the_withdrawn_contract_is_gone_from_the_contract_and_the_prompts():
    """Not loosened: the old sentences are absent, and stay absent.

    Each of them was true when it was written and each is now the opposite of the
    ruling. Left in one file while the other three carry the new words, any one of them
    reads as the binding sentence to whichever worker opens that file.
    """
    files = [DESIGN / "README.md"] + [AGENTS / n for n in
                                      ("build.md", "spec.md", "ticket-qa.md")]
    for path in files:
        text = _flat(path.read_text(encoding="utf-8"))
        for sentence in WITHDRAWN:
            assert _flat(sentence) not in text, (
                "%s carries a sentence the 2026-09-29 ruling withdrew: %s"
                % (path.relative_to(ROOT), sentence))


def _table_rows():
    rows = []
    for line in (DESIGN / "README.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and line.endswith(" |") and ".html" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
    return rows


def test_the_map_names_every_screen_that_is_there_and_no_screen_that_is_not():
    """A sketch is still governed, and a map that points at nothing is not a map."""
    drawn = sorted(p.name for p in DESIGN.glob("*.html"))
    mapped = sorted(row[0] for row in _table_rows())
    assert mapped == drawn, (
        "design/README.md maps %s and design/ holds %s" % (mapped, drawn))
    assert len(drawn) == 4, "design/ no longer holds four screens: %s" % drawn


def test_every_id_the_screens_claim_is_one_the_registry_carries():
    """The registry is what binds, so the sketch may not name an ID it does not hold.

    Both places claim IDs: the table's third column, and the `FULFILS` comment in each
    screen's source. An ID in either that PRD.md does not carry is a promise made by a
    picture, which is the thing the ruling says a picture cannot do.
    """
    registry = PRD.read_text(encoding="utf-8")
    pattern = re.compile(r"\b(?:US|FR|AC|NFR)-[A-Z]+-\d+\b")

    claimed = set()
    for row in _table_rows():
        claimed.update(pattern.findall(row[2]))
    for screen in DESIGN.glob("*.html"):
        text = screen.read_text(encoding="utf-8")
        fulfils = re.search(r"<!--\s*FULFILS(.*?)-->", text, re.S)
        assert fulfils, "%s carries no FULFILS comment" % screen.name
        claimed.update(pattern.findall(fulfils.group(1)))

    assert claimed, "no IDs claimed anywhere in design/"
    for ident in sorted(claimed):
        assert re.search(r"\b%s\b" % re.escape(ident), registry), (
            "design/ claims %s and PRD.md does not carry it" % ident)


def test_no_criterion_in_the_registry_delegates_itself_to_a_drawing():
    """The ruling, held where it binds.

    AC-UI-10, AC-UI-20 and AC-UI-30 each read "as design/<file>.html draws it" until
    2026-09-29, which pointed a promise at a sketch for its own content. The named
    things in them stand on their own now. FR-UI-10 still names the folder, because
    serving those screens is what the app is for; naming one of the files inside it is
    the thing that went.
    """
    offenders = []
    for line in PRD.read_text(encoding="utf-8").splitlines():
        if not re.match(r"\s*- (?:US|FR|AC|NFR)-", line):
            continue
        for drawing in re.findall(r"design/[\w.-]+\.html", line):
            offenders.append((line.strip().split("—")[0].strip(), drawing))
    assert not offenders, (
        "a registry line points at a drawing for its content: %s" % offenders)
