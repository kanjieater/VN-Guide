#!/usr/bin/env bash
set -euo pipefail

REPO_PATH="${REPO_PATH:-/app/repo}"
RUN_INTERVAL_HOURS="${RUN_INTERVAL_HOURS:-6}"
GIT_EMAIL="${GIT_EMAIL:-vn-guide-bot@shke.xyz}"
GIT_NAME="${GIT_NAME:-VN Guide Bot}"

# Configure git credentials once via ~/.netrc (token never appears in remote URL or args)
if [ -n "${GITHUB_TOKEN:-}" ]; then
    printf 'machine github.com\nlogin %s\npassword %s\n' \
        "${VNDB_USER:-kanjieater}" "${GITHUB_TOKEN}" > ~/.netrc
    chmod 600 ~/.netrc
fi

git -C "${REPO_PATH}" config user.email "${GIT_EMAIL}"
git -C "${REPO_PATH}" config user.name "${GIT_NAME}"

run_pipeline() {
    echo "[$(date -Iseconds)] Starting VN guide sync"
    python3 /app/scripts/generate.py
    python3 /app/scripts/deploy.py
    echo "[$(date -Iseconds)] Sync complete"
}

# Run immediately on startup
run_pipeline || echo "[$(date -Iseconds)] Pipeline error (will retry next cycle)"

# Then loop on interval
SLEEP_SECS=$(( RUN_INTERVAL_HOURS * 3600 ))
while true; do
    sleep "${SLEEP_SECS}"
    run_pipeline || echo "[$(date -Iseconds)] Pipeline error (will retry next cycle)"
done
