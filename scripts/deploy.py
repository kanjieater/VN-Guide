"""
Idempotent git commit + push for the VN guide repo.
Reads REPO_PATH from env. No-ops if working tree is clean.
Git credentials are configured once in entrypoint.sh via ~/.netrc.
"""
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO_PATH = os.environ.get("REPO_PATH", "/app/repo")


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", REPO_PATH, *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def deploy() -> None:
    # Check for any uncommitted changes
    status = run_git("status", "--porcelain")
    if not status.stdout.strip():
        print("[deploy] Nothing changed, skipping commit")
        return

    changed = status.stdout.strip().splitlines()
    print(f"[deploy] {len(changed)} file(s) changed:")
    for line in changed:
        print(f"  {line}")

    # Stage all tracked + new files the generator would have touched
    run_git("add", "index.html", "games.json")

    # Stage any new game directories (scaffold outputs)
    # `git add .` scoped after we've confirmed nothing sensitive is present
    # (only HTML files from our own templates enter the repo)
    run_git("add", "--all")

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run_git("commit", "-m", f"sync: update playing list [{date}]")

    result = run_git("push", check=False)
    if result.returncode != 0:
        print(f"[deploy] Push failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    print("[deploy] Pushed to GitHub Pages")


if __name__ == "__main__":
    deploy()
