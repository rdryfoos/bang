import json

from whms.cli import main


def _write(path, items):
    path.write_text(json.dumps(items))


def _item(name, date_out, date_back=None):
    item = {"name": name, "borrower": "Pat", "date_out": date_out}
    if date_back:
        item["date_back"] = date_back
    return item


def test_AC_OUT_10_item_marked_returned_no_longer_appears_in_outstanding_list(data_file, capsys):
    _write(data_file, [_item("ladder", "2026-01-05", "2026-01-20"), _item("drill", "2026-01-06")])
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "drill" in out
    assert "ladder" not in out


def test_FR_OUT_10_outstanding_list_shows_every_unreturned_item_oldest_first(data_file, capsys):
    _write(data_file, [
        _item("newest", "2026-03-01"),
        _item("oldest", "2026-01-01"),
        _item("gone", "2026-01-15", "2026-02-01"),
        _item("middle", "2026-02-01"),
    ])
    assert main(["list"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split("\t")[0] for line in lines] == ["oldest", "middle", "newest"]


def test_AC_OUT_20_empty_outstanding_list_says_so_in_words(data_file, capsys):
    cases = [None, [], [_item("ladder", "2026-01-05", "2026-01-20")]]
    for items in cases:
        if items is not None:
            _write(data_file, items)
        assert main(["list"]) == 0
        out = capsys.readouterr().out
        assert out.strip() and "\t" not in out
        assert "nothing" in out.lower()


def test_US_OUT_10_unreadable_records_are_an_error_not_an_empty_list(data_file, capsys):
    data_file.write_text("{not json")
    assert main(["list"]) != 0
    captured = capsys.readouterr()
    assert captured.err.strip()
    assert "nothing" not in captured.out.lower()
