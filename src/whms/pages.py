# @covers AC-UI-10, AC-UI-20, AC-UI-30
"""The four screens as HTML. The words are the words in design/."""
import datetime
from html import escape
from typing import Dict, List, Optional, Tuple

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
FOOTER = "Your records are in a file on this machine and nowhere else."

CSS = """
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,"Helvetica Neue",Helvetica,sans-serif;background:#f6f3ec;color:#1b1a17}
a{color:#2f5d4a}a:hover{color:#1f4232}
input,button{font:inherit}
.panel{min-height:100vh;padding:56px 24px 28px;display:flex;flex-direction:column;gap:20px;background:#f6f3ec}
@media (min-width:600px){
body{padding:40px 0}
.panel{max-width:440px;min-height:0;margin:0 auto;border:1px solid #e2ddd1;border-radius:16px;box-shadow:0 8px 30px rgba(27,26,23,.08);padding:40px 28px 28px}
}
.head{display:flex;flex-direction:column;gap:4px}
h1{margin:0;font-family:Georgia,'Times New Roman',serif;font-size:30px;line-height:1.1;font-weight:400}
.sub{font-size:15px;color:#5b574f}
.list{display:flex;flex-direction:column;gap:12px}
.card{display:flex;flex-direction:column;gap:10px;padding:16px;background:#fff;border:1px solid #e2ddd1;border-radius:12px}
.row{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.name{font-size:18px;font-weight:600}
.days{font-size:13px;color:#5b574f;font-weight:600}
.days.old{color:#8a4b1f}
.small{font-size:15px;color:#5b574f}
.outline{align-self:flex-start;display:inline-flex;align-items:center;height:44px;padding:0 16px;border:1px solid #2f5d4a;border-radius:10px;font-size:15px;font-weight:600;text-decoration:none;color:#2f5d4a}
.back{align-self:flex-start;display:inline-flex;align-items:center;height:44px;font-size:15px;text-decoration:none}
.primary{display:flex;align-items:center;justify-content:center;height:52px;background:#2f5d4a;color:#fff;border:0;border-radius:12px;font-size:17px;font-weight:600;text-decoration:none;cursor:pointer;width:100%}
.empty{align-items:center;gap:8px;padding:48px 24px;text-align:center}
.empty .name{font-family:Georgia,'Times New Roman',serif;font-size:24px;font-weight:400}
.grow{flex-grow:1}
form{display:contents}
.fields{display:flex;flex-direction:column;gap:16px}
.field{display:flex;flex-direction:column;gap:6px}
label{font-size:14px;font-weight:600}
input[type=text]{height:48px;padding:0 14px;border:1px solid #c9c3b5;border-radius:10px;background:#fff;font-size:17px;color:#1b1a17;width:100%}
input.bad{border-color:#a8391f}
.hint{font-size:13px;color:#5b574f}
.err{font-size:13px;color:#a8391f}
.foot{display:flex;flex-direction:column;gap:4px;padding-top:8px;border-top:1px solid #e2ddd1;font-size:12px;color:#5b574f}
"""


def format_date(iso: str) -> str:
    """'2026-07-14' as 'Jul 14, 2026'; anything unreadable is shown as it is."""
    try:
        d = datetime.datetime.strptime(iso, "%Y-%m-%d")
    except (TypeError, ValueError):
        return iso
    return "%s %d, %d" % (MONTHS[d.month - 1], d.day, d.year)


def parse_date(text: str) -> Optional[str]:
    """'Sep 20, 2026' or 'YYYY-MM-DD' as 'YYYY-MM-DD'; None when it is neither."""
    text = (text or "").strip()
    try:
        return datetime.datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        pass
    parts = text.replace(",", " ").split()
    if len(parts) == 3 and parts[0].title()[:3] in MONTHS and len(parts[0]) <= 9:
        try:
            d = datetime.date(int(parts[2]), MONTHS.index(parts[0].title()[:3]) + 1, int(parts[1]))
            return d.isoformat()
        except ValueError:
            return None
    return None


def days_out(date_out: str, today: datetime.date) -> str:
    try:
        n = (today - datetime.datetime.strptime(date_out, "%Y-%m-%d").date()).days
    except (TypeError, ValueError):
        return ""
    n = max(n, 0)
    return "%d day%s" % (n, "" if n == 1 else "s")


def _page(title: str, body: str, status_class: str = "") -> str:
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n"
            '<div class="panel">\n%s\n</div>\n</body>\n</html>\n' % (escape(title), CSS, body))


def _foot() -> str:
    return '<div class="foot"><div>%s</div></div>' % FOOTER


def outstanding_page(rows: List[Tuple[int, Dict[str, str]]], today: datetime.date) -> str:
    """`rows` are (position in the file, item), already oldest first."""
    head = ('<div class="head"><h1>Who has my stuff</h1>'
            '<div class="sub">Everything still out, oldest first.</div></div>')
    if rows:
        cards = []
        for n, (index, item) in enumerate(rows):
            cards.append(
                '<div class="card"><div class="row"><div class="name">%s</div>'
                '<div class="days%s">%s</div></div>'
                '<div class="small">%s has it. Out since %s.</div>'
                '<a class="outline" href="/return/%d">Mark returned</a></div>'
                % (escape(item["name"]), " old" if n == 0 else "",
                   escape(days_out(item["date_out"], today)), escape(item["borrower"]),
                   escape(format_date(item["date_out"])), index))
        middle = '<div class="list">%s</div>' % "\n".join(cards)
    else:
        middle = ('<div class="card empty"><div class="name">Nothing is out.</div>'
                  '<div class="small">Everything you lent has come back, or you have not '
                  'lent anything yet.</div></div>')
    return _page("Outstanding" if rows else "Nothing out",
                 head + middle + '\n<div class="grow"></div>\n'
                 '<a class="primary" href="/lend">Lend something</a>\n' + _foot())


def lend_page(values: Dict[str, str], errors: Optional[Dict[str, str]] = None) -> str:
    errors = errors or {}

    def field(key, label, placeholder="", hint=""):
        bad = key in errors
        note = ('<div class="err">%s</div>' % escape(errors[key]) if bad
                else '<div class="hint">%s</div>' % escape(hint) if hint else "")
        return ('<div class="field"><label for="%s">%s</label>'
                '<input id="%s" name="%s" type="text" value="%s" placeholder="%s"%s>%s</div>'
                % (key, label, key, key, escape(values.get(key, ""), quote=True),
                   escape(placeholder, quote=True), ' class="bad"' if bad else "", note))

    body = ('<a class="back" href="/">Back to the list</a>\n'
            '<div class="head"><h1>Lend something</h1>'
            '<div class="sub">Write it down now, so you stop relying on memory.</div></div>\n'
            '<form method="post" action="/lend">\n<div class="fields">%s%s%s</div>\n'
            '<div class="grow"></div>\n<button class="primary" type="submit">Save</button>\n</form>'
            % (field("name", "What"), field("borrower", "To whom", "A name"),
               field("date_out", "Date out", hint="Today unless you change it.")))
    return _page("Lend something", body)


def return_page(index: int, item: Dict[str, str], date_back: str,
                error: Optional[str] = None) -> str:
    note = ('<div class="err">%s</div>' % escape(error) if error
            else '<div class="hint">Today unless you change it.</div>')
    body = ('<a class="back" href="/">Back to the list</a>\n'
            '<div class="head"><h1>Mark returned</h1>'
            '<div class="sub">It stops nagging you the moment you do.</div></div>\n'
            '<div class="card"><div class="name">%s</div>'
            '<div class="small">%s has it. Out since %s.</div></div>\n'
            '<form method="post" action="/return/%d">\n'
            '<div class="field"><label for="date_back">Date back</label>'
            '<input id="date_back" name="date_back" type="text" value="%s"%s>%s</div>\n'
            '<div class="grow"></div>\n<button class="primary" type="submit">Mark returned</button>\n'
            "</form>"
            % (escape(item["name"]), escape(item["borrower"]),
               escape(format_date(item["date_out"])), index,
               escape(date_back, quote=True), ' class="bad"' if error else "", note))
    return _page("Mark returned", body)


def error_page(message: str) -> str:
    return _page("Something went wrong",
                 '<a class="back" href="/">Back to the list</a>\n'
                 '<div class="head"><h1>Something went wrong</h1>'
                 '<div class="sub">%s</div></div>\n<div class="grow"></div>\n%s'
                 % (escape(message), _foot()))
