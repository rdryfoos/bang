from whms.cli import main

GOOD = ["add", "--name", "ladder", "--borrower", "Pat", "--date-out", "2026-01-05"]


def test_AC_LEND_10_saved_item_appears_in_outstanding_list_immediately(data_file, capsys):
    assert main(GOOD) == 0
    capsys.readouterr()
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "ladder" in out and "Pat" in out and "2026-01-05" in out


def test_AC_LEND_20_item_without_borrower_is_refused_with_reason(data_file, capsys):
    for extra in ([], ["--borrower", ""], ["--borrower", "   "]):
        assert main(["add", "--name", "ladder", "--date-out", "2026-01-05"] + extra) == 2
        assert "borrower" in capsys.readouterr().err
    assert not data_file.exists()


def test_AC_LEND_20_refused_save_leaves_existing_records_untouched(data_file, capsys):
    assert main(GOOD) == 0
    before = data_file.read_bytes()
    assert main(["add", "--name", "drill", "--date-out", "2026-01-06"]) == 2
    assert data_file.read_bytes() == before


def test_FR_LEND_10_item_record_holds_name_borrower_and_date_out(data_file, capsys):
    assert main(GOOD) == 0
    assert main(GOOD) == 0  # lending the same thing twice is kept
    import json
    items = json.loads(data_file.read_text())
    assert items == [{"name": "ladder", "borrower": "Pat", "date_out": "2026-01-05"}] * 2
    capsys.readouterr()
    before = data_file.read_bytes()
    bad = [
        (["add", "--borrower", "Pat", "--date-out", "2026-01-05"], "name"),
        (["add", "--name", "ladder", "--borrower", "Pat"], "date"),
        (["add", "--name", "ladder", "--borrower", "Pat", "--date-out", "2026-02-31"], "real date"),
    ]
    for argv, word in bad:
        assert main(argv) == 2
        assert word in capsys.readouterr().err
    assert data_file.read_bytes() == before
