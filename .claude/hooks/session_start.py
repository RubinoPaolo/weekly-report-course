#!/usr/bin/env python3
"""SessionStart hook: remember which commit the session started from.
The Stop hook compares test results against that commit, so failures that
were already there are not blamed on the agent."""
import json, os, subprocess, sys
from pathlib import Path

data = json.load(sys.stdin) if not sys.stdin.isatty() else {}
root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
state = root / ".claude" / "state"
state.mkdir(parents=True, exist_ok=True)
sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
sid = data.get("session_id", "default")
(state / f"base_{sid}.txt").write_text(sha)
sys.exit(0)
