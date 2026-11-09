from __future__ import annotations
from .models import Report
from .status import by_project, latest_week, budget_ratio

def render(reports: list[Report]) -> str:
    week = latest_week(reports)
    lines = [f"# Weekly management summary · {week}", ""]
    for project, rs in sorted(by_project(reports, week).items()):
        r = rs[0]
        lines.append(f"- **{project}** · {r.status} · budget {r.budget_used:.1f} of {r.budget_total:.1f} M ({budget_ratio(r):.0%}) · next: {r.milestone} on {r.milestone_date.isoformat()}")
    return "\n".join(lines) + "\n"
