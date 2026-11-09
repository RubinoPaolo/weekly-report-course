from pathlib import Path
import pytest
from report.parse import parse_report, load_reports, parse_date
from report import ReportError

REPORTS = Path(__file__).resolve().parents[1] / "reports"
INBOX = Path(__file__).resolve().parents[1] / "inbox"

def test_parse_iso_report():
    r = parse_report(REPORTS / "2026-W44_alpha.md")
    assert r.project == "Alpha" and r.status == "green"
    assert r.budget_used == 1.2 and r.budget_total == 2.0
    assert r.milestone_date.isoformat() == "2026-11-20"

def test_parse_delta_w44_swiss_date_format():
    # authors sometimes write dates as DD.MM.YYYY; the parser must accept both forms
    r = parse_report(INBOX / "2026-W44_delta_late.md")
    assert r.milestone_date.isoformat() == "2026-12-05"

def test_unreadable_date_raises():
    with pytest.raises(ReportError):
        parse_date("next week")

def test_load_all_reports():
    rs = load_reports(REPORTS)
    assert len(rs) >= 12
