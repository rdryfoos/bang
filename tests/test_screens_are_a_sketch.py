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

SKETCH = "The screens are a low-fidelity sketch, for reference."
REGISTRY = ("What a build must satisfy is the registry, and the controls, order, states "
            "and words that matter are named there in acceptance criteria.")
UNNAMED = ("Anything not named is the build's to choose and the reviewer's to judge in "
           "Review.")

FORK = ("A nav bar or a palette is delivery unless an acceptance criterion says "
        "otherwise; a state or a word an acceptance criterion names is not.")

# The sentences the 2026-09-29 ruling withdrew. A prompt or a contract that says any of
# these again is saying the opposite of the three bullets, and saying it in the file a
# worker reads first.
WITHDRAWN = (
    "the copy on a screen is the copy",
    "Copy on the screens is the copy",
    "Layout is a guide, not a pixel contract",
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


def test_the_readme_carries_the_ruling_in_its_three_bullets():
    """The governed copy says what a build reads, in the words of the ruling."""
    readme = _readme()
    for sentence in (SKETCH, REGISTRY, UNNAMED):
        assert _flat(sentence) in readme, (
            "design/README.md no longer says: %s" % sentence)


def test_the_section_is_three_bullets_and_nothing_else():
    """Three, and no fourth.

    The section this replaces had grown to eight bullets, and the two that caused the
    trouble were the two added last, each one a reasonable answer to a real run. A count
    is what stops the next reasonable answer being added here instead of to the registry,
    where a promise is a promise rather than a paragraph a build has to weigh.
    """
    bullets = [line for line in _section().splitlines() if line.startswith("- ")]
    assert len(bullets) == 3, (
        "the section carries %d bullets, not three:\n%s"
        % (len(bullets), "\n".join(bullets)))
    assert _flat(bullets[0]).endswith(_flat(SKETCH))
    assert _flat(REGISTRY) in _flat(bullets[1])
    assert _flat(UNNAMED) in _flat(bullets[2])


def test_the_prompts_say_it_in_the_same_words_as_the_contract():
    """The three prompts a worker reads carry the ruling, not a paraphrase of it.

    A worker that opens `design/README.md` is the lucky case; the ordinary one reads its
    own prompt and nothing else. Spec is in the list because a specification written
    against the pictures binds a build that never saw them.
    """
    for name in ("build.md", "spec.md", "ticket-qa.md"):
        prompt = _flat((AGENTS / name).read_text(encoding="utf-8"))
        assert _flat(SKETCH) in prompt or "low-fidelity sketch" in prompt, (
            "%s no longer calls the screens a sketch" % name)
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
