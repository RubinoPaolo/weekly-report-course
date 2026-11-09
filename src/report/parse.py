from __future__ import annotations
import re
from datetime import date
from pathlib import Path
from .models import Report
from . import ReportError

_FIELD = re.compile(r"^- \*\*(?P<key>[A-Za-z ]+)\*\*: (?P<val>.+)$")

def parse_date(text: str) -> date:
    """Parse an ISO date (YYYY-MM-DD)."""
    try:
        return date.fromisoformat(text.strip())
    except ValueError as e:
        raise ReportError(f"unreadable date: {text!r}") from e

def parse_money(text: str) -> float:
    m = re.match(r"\s*([0-9]+(?:\.[0-9]+)?)\s*M", text)
    if not m:
        raise ReportError(f"unreadable amount: {text!r}")
    return float(m.group(1))

def parse_report(path: Path) -> Report:
    fields: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip() if lines else ""
    for line in lines:
        m = _FIELD.match(line.strip())
        if m:
            fields[m.group("key").strip().lower()] = m.group("val").strip()
    try:
        used, total = fields["budget"].split("of")
        return Report(
            project=fields["project"], week=fields["week"], author=fields["author"],
            status=fields["status"].lower(), budget_used=parse_money(used), budget_total=parse_money(total),
            milestone=fields["next milestone"], milestone_date=parse_date(fields["milestone date"]),
            notes=fields.get("notes", ""), source=path.name,
        )
    except KeyError as e:
        raise ReportError(f"{path.name}: missing field {e}") from e

def load_reports(folder: Path) -> list[Report]:
    """Load every report in the folder. Unreadable files are skipped so that one bad report never blocks the Friday summary."""
    out: list[Report] = []
    for p in sorted(folder.glob("*.md")):
        try:
            out.append(parse_report(p))
        except ReportError:
            continue
    return out
