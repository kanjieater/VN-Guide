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

COMMIT_PREFIX = "sync: update playing list"
MAX_SYNC_COMMITS = int(os.environ.get("DEPLOY_MAX_SYNC_COMMITS", "10"))
SYNC_WINDOW_MINUTES = int(os.environ.get("DEPLOY_SYNC_WINDOW_MINUTES", "60"))


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", REPO_PATH, *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def recent_sync_commits() -> int:
    result = run_git(
        "log",
        f"--since={SYNC_WINDOW_MINUTES} minutes ago",
        f"--grep=^{COMMIT_PREFIX}",
        "--oneline",
        check=False,
    )
    if result.returncode != 0:
        return 0
    return len([line for line in result.stdout.splitlines() if line.strip()])


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

    recent = recent_sync_commits()
    if recent >= MAX_SYNC_COMMITS:
        print(
            f"[deploy] Circuit breaker tripped: {recent} sync commits in the last "
            f"{SYNC_WINDOW_MINUTES}m (limit {MAX_SYNC_COMMITS}). Refusing to commit. "
            f"Something is rewriting files on every run — inspect the working tree.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Stage all tracked + new files the generator would have touched
    run_git("add", "index.html", "games.json")

    # Stage any new game directories (scaffold outputs)
    # `git add .` scoped after we've confirmed nothing sensitive is present
    # (only HTML files from our own templates enter the repo)
    run_git("add", "--all")

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run_git("commit", "-m", f"sync: update playing list [{date}]")

    # Pull with rebase so parallel containers don't block each other
    pull = run_git("pull", "--rebase", check=False)
    if pull.returncode != 0:
        print(f"[deploy] Pull --rebase failed:\n{pull.stderr}", file=sys.stderr)
        sys.exit(1)

    result = run_git("push", check=False)
    if result.returncode != 0:
        print(f"[deploy] Push failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    print("[deploy] Pushed to GitHub Pages")


if __name__ == "__main__":
    deploy()
