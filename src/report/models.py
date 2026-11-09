from __future__ import annotations
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Report:
    project: str
    week: str            # e.g. "2026-W44"
    author: str
    status: str          # green | amber | red, as written by the author
    budget_used: float   # in M CHF
    budget_total: float  # in M CHF
    milestone: str
    milestone_date: date
    notes: str
    source: str          # file name
