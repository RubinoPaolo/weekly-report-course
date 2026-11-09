#!/usr/bin/env python3
"""Stop hook with a baseline.

Blocks the end of the turn (exit 2) only for tests that FAIL NOW but PASSED
at the commit the session started from. Tests that were already failing
are reported to the user, never sent back to the agent as a task.
After 3 blocks in the same session it lets the turn end and says so,
so a disagreement between the rule and the task cannot loop forever."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

MAX_BLOCKS = 3
data = json.load(sys.stdin) if not sys.stdin.isatty() else {}
root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
state = root / ".claude" / "state"
state.mkdir(parents=True, exist_ok=True)
sid = data.get("session_id", "default")

def git(*args, cwd=root):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout.strip()

def failing_tests(cwd):
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rfE", "-p", "no:cacheprovider"],
                         cwd=cwd, capture_output=True, text=True)
    text = out.stdout + out.stderr
    ids = set(re.findall(r"^(?:FAILED|ERROR) (\S+)", text, re.M))
    return ids, text

base_file = state / f"base_{sid}.txt"
base = base_file.read_text().strip() if base_file.exists() else git("rev-parse", "HEAD")

cache = state / f"baseline_{base}.json"
if cache.exists():
    baseline = set(json.loads(cache.read_text()))
else:
    tmp = tempfile.mkdtemp(prefix="baseline_")
    git("worktree", "add", "--detach", tmp, base)
    try:
        baseline, _ = failing_tests(tmp)
    finally:
        git("worktree", "remove", "--force", tmp)
    cache.write_text(json.dumps(sorted(baseline)))

now, output = failing_tests(root)
if "No module named pytest" in output:
    # without pytest every test run looks clean: say so instead of passing silently
    print(json.dumps({"systemMessage": "Stop hook: the tests could not run because pytest is not installed. Run: pip install -e ."}))
    sys.exit(0)
new = sorted(now - baseline)
old = sorted(now & baseline)

if new:
    counter = state / f"blocks_{sid}.txt"
    n = int(counter.read_text()) + 1 if counter.exists() else 1
    counter.write_text(str(n))
    if n <= MAX_BLOCKS:
        msg = ["Tests that passed when this session started are now failing. Fix them before finishing:"]
        msg += [f"  - {t}" for t in new]
        if old:
            msg.append("Already failing before this session (not your task unless you were asked): " + ", ".join(old))
        msg.append(output[-1500:])
        print("\n".join(msg), file=sys.stderr)
        sys.exit(2)
    print(json.dumps({"systemMessage": f"Stop hook: {len(new)} test(s) broken in this session are still failing after {MAX_BLOCKS} attempts: {', '.join(new)}. Turn ended; please review."}))
    sys.exit(0)

if old:
    print(json.dumps({"systemMessage": "Stop hook: no new test failures. Already failing before this session: " + ", ".join(old)}))
sys.exit(0)
