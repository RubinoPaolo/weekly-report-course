from pathlib import Path
from report.parse import load_reports
from report.summary import render
from report.status import latest_week

REPORTS = Path(__file__).resolve().parents[1] / "reports"

def test_latest_week():
    assert latest_week(load_reports(REPORTS)) == "2026-W44"

def test_render_lists_every_project_once():
    out = render(load_reports(REPORTS))
    for p in ("Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot"):
        assert out.count(f"**{p}**") == 1
