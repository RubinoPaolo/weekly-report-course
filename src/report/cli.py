from __future__ import annotations
import sys
from pathlib import Path
from .parse import load_reports
from .summary import render

def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows writes cp1252 to files and pipes otherwise
    folder = Path(argv[0]) if argv else Path("reports")
    print(render(load_reports(folder)), end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
