"""A card whose work is done says so on its own task lines.

On the eighth cold run BAN-1 reached the review column with forty passing tests and a
GREEN Gate, and its Intent block read OPEN DEBT: T203, T208, T209 and T211 in
`specs/006-browser-screens/tasks.md`, and T904 in `specs/backlog/tasks.md`, all
unticked. The Build worker had done every one of them and ticked none.

That card is not slightly untidy. Its own file says the work is owed, the reservation
says nobody has started, and the next reader has to open the diff to find out which is
true. The Gate cannot catch it: the Gate asks whether the ids are proven, and they were.

Two halves, and both are here: the instruction to the worker, read out of build.md
rather than restated, and the check that refuses the card if the worker did not follow
it.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD_MD = ROOT / "cannon-template" / "agents" / "build.md"

# BAN-1's own ids line, from the eighth run.
CARD_IDS = ["US-UI-10", "FR-UI-10", "AC-UI-10", "AC-UI-20", "AC-UI-30"]


def _flat(text):
    """The prose as one line, because these files are wrapped.

    "before the commit that finishes it" is split across a newline and three spaces of
    indent in build.md. An assertion that matches on a literal space is asserting about
    the wrapping, not about the sentence.
    """
    return " ".join(text.split())


def _column_check():
    spec = importlib.util.spec_from_file_location(
        "column_check", ROOT / "scripts" / "column-check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- the instruction -------------------------------------------------------------

def test_build_md_tells_the_worker_to_tick_what_it_finished():
    text = _flat(BUILD_MD.read_text(encoding="utf-8"))
    assert "`- [ ]` becomes `- [x]`" in text, "build.md does not say to tick the box"
    assert "before the commit that finishes it" in text, (
        "build.md does not say when to tick it")


def test_build_md_tells_the_worker_to_close_the_reservation_its_spec_claims():
    text = _flat(BUILD_MD.read_text(encoding="utf-8"))
    assert "specs/backlog/tasks.md" in text, "build.md does not name the reservation file"
    assert "the reservation has expired" in text, (
        "build.md does not say the reservation is the worker's to close")


# --- the check -------------------------------------------------------------------

def test_an_open_task_carrying_the_cards_ids_is_found():
    open_tasks_carrying = _column_check().open_tasks_carrying
    # T904's real line, as it ships.
    tasks = (
        "- [ ] T904 Deliver the four screens `design/` draws as a local web app over the "
        "same records file the command line writes. **Carries**: US-UI-10, FR-UI-10, "
        "AC-UI-10, AC-UI-20, AC-UI-30 (reserved backlog). Reserved, no card yet.\n"
    )
    found = open_tasks_carrying(tasks, CARD_IDS)
    assert len(found) == 1
    assert "T904" in found[0]


def test_a_ticked_task_is_not_an_offender():
    open_tasks_carrying = _column_check().open_tasks_carrying
    tasks = (
        "- [x] T904 Deliver the four screens. **Carries**: US-UI-10, FR-UI-10, "
        "AC-UI-10, AC-UI-20, AC-UI-30 (reserved backlog).\n"
    )
    assert open_tasks_carrying(tasks, CARD_IDS) == []


def test_an_open_task_for_another_card_is_left_alone():
    # A card is answerable for its own promises and no others. T905 carries the
    # borrower's history, which is a different card's work.
    open_tasks_carrying = _column_check().open_tasks_carrying
    tasks = (
        "- [ ] T905 Show what a borrower has had before. **Carries**: US-UI-20, "
        "AC-UI-40 (reserved backlog).\n"
    )
    assert open_tasks_carrying(tasks, CARD_IDS) == []


def test_an_open_task_carrying_one_of_the_cards_ids_is_enough():
    open_tasks_carrying = _column_check().open_tasks_carrying
    tasks = "- [ ] T211 Mark returned on the screen. **Carries**: AC-UI-30\n"
    assert len(open_tasks_carrying(tasks, CARD_IDS)) == 1


def test_an_open_task_that_carries_nothing_is_not_this_checks_business():
    # A task with no Carries line is not claiming any of this card's promises, and the
    # Gate has its own opinion about task lines without one.
    open_tasks_carrying = _column_check().open_tasks_carrying
    assert open_tasks_carrying("- [ ] T500 Tidy the README.\n", CARD_IDS) == []


def test_it_reads_the_traces_spelling_too():
    # **Traces**: is the pre-rename spelling, and the Gate still accepts it.
    open_tasks_carrying = _column_check().open_tasks_carrying
    tasks = "- [ ] T203 The screens. **Traces**: AC-UI-10\n"
    assert len(open_tasks_carrying(tasks, CARD_IDS)) == 1


def test_the_eighth_runs_card_would_have_been_refused():
    """All five lines BAN-1 carried into the review column, in one file."""
    open_tasks_carrying = _column_check().open_tasks_carrying
    tasks = "\n".join([
        "- [ ] T203 The four screens as design/ draws them. **Carries**: US-UI-10, AC-UI-10",
        "- [ ] T208 Lend on the screen. **Carries**: AC-UI-20",
        "- [ ] T209 The outstanding list. **Carries**: AC-UI-10",
        "- [ ] T211 Mark returned on the screen. **Carries**: AC-UI-30",
        "- [x] T210 Something already ticked. **Carries**: AC-UI-20",
        "- [ ] T904 The reservation. **Carries**: US-UI-10, FR-UI-10, AC-UI-10, AC-UI-20, AC-UI-30",
    ])
    found = open_tasks_carrying(tasks, CARD_IDS)
    assert len(found) == 5, found
    for number in ("T203", "T208", "T209", "T211", "T904"):
        assert any(number in line for line in found), f"{number} was not found"
    assert not any("T210" in line for line in found), "a ticked task was reported"


def test_the_refusal_names_the_lines():
    # A refusal that says "some tasks are open" sends the reader to look for them. The
    # lines are what makes it actionable.
    module = _column_check()
    tasks = "- [ ] T211 Mark returned on the screen. **Carries**: AC-UI-30\n"
    found = module.open_tasks_carrying(tasks, CARD_IDS)
    assert "T211" in found[0]
    assert "Mark returned on the screen" in found[0]
