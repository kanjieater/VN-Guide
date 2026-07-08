#!/usr/bin/env bash
set -euo pipefail

REPO_PATH="${REPO_PATH:-/app/repo}"
RUN_INTERVAL_HOURS="${RUN_INTERVAL_HOURS:-6}"
GIT_EMAIL="${GIT_EMAIL:-vn-guide-bot@shke.xyz}"
GIT_NAME="${GIT_NAME:-VN Guide Bot}"

# Trust the mounted repo (container runs as root, repo owned by host user)
git config --global --add safe.directory "${REPO_PATH}"

# Accept GitHub's SSH host key so git push works without interactive prompt
mkdir -p ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts 2>/dev/null
chmod 600 ~/.ssh/known_hosts

# Switch remote to HTTPS and configure token auth so we don't need SSH keys
if [ -n "${GITHUB_TOKEN:-}" ]; then
    git -C "${REPO_PATH}" remote set-url origin \
        "https://github.com/kanjieater/VN-Guide.git"
    printf 'machine github.com\nlogin %s\npassword %s\n' \
        "${VNDB_USER:-kanjieater}" "${GITHUB_TOKEN}" > ~/.netrc
    chmod 600 ~/.netrc
fi

git -C "${REPO_PATH}" config user.email "${GIT_EMAIL}"
git -C "${REPO_PATH}" config user.name "${GIT_NAME}"

run_pipeline() {
    echo "[$(date -Iseconds)] Starting VN guide sync"
    python3 /app/scripts/generate.py
    python3 /app/scripts/guide_gen.py
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
