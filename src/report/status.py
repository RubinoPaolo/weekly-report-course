from __future__ import annotations
from datetime import date
from .models import Report

def budget_ratio(r: Report) -> float:
    return r.budget_used / r.budget_total if r.budget_total else 0.0

def latest_week(reports: list[Report]) -> str:
    return max(r.week for r in reports)

def by_project(reports: list[Report], week: str) -> dict[str, list[Report]]:
    out: dict[str, list[Report]] = {}
    for r in reports:
        if r.week == week:
            out.setdefault(r.project, []).append(r)
    return out
