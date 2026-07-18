#!/usr/bin/env bash
set -euo pipefail

REPO_PATH="${REPO_PATH:-/app/repo}"
RUN_INTERVAL_HOURS="${RUN_INTERVAL_HOURS:-6}"
GIT_EMAIL="${GIT_EMAIL:-vn-guide-bot@shke.xyz}"
GIT_NAME="${GIT_NAME:-VN Guide Bot}"

# Guide generation only runs between GUIDE_START_HOUR and GUIDE_END (HH:MM, 24h, same-day window)
# Defaults: 22:00 – 00:30. Set GUIDE_WINDOW_DISABLE=1 to remove the restriction.
GUIDE_START_HOUR="${GUIDE_START_HOUR:-22}"
GUIDE_END_HOUR="${GUIDE_END_HOUR:-0}"
GUIDE_END_MIN="${GUIDE_END_MIN:-30}"

# Returns 0 (true) if current local time is within the allowed window
in_guide_window() {
    local h m total_mins start_mins end_mins
    h=$(date +%H); m=$(date +%M)
    total_mins=$(( 10#$h * 60 + 10#$m ))
    start_mins=$(( 10#$GUIDE_START_HOUR * 60 ))
    end_mins=$(( 10#$GUIDE_END_HOUR * 60 + 10#$GUIDE_END_MIN ))

    if [ "${GUIDE_WINDOW_DISABLE:-0}" = "1" ]; then
        return 0
    fi

    # Window crosses midnight (e.g. 22:00 – 00:30)
    if [ "$start_mins" -gt "$end_mins" ]; then
        [ "$total_mins" -ge "$start_mins" ] || [ "$total_mins" -le "$end_mins" ]
    else
        [ "$total_mins" -ge "$start_mins" ] && [ "$total_mins" -le "$end_mins" ]
    fi
}

# Sleep until the next GUIDE_START_HOUR:00
sleep_until_window() {
    local h m total_mins start_mins sleep_mins
    h=$(date +%H); m=$(date +%M)
    total_mins=$(( 10#$h * 60 + 10#$m ))
    start_mins=$(( 10#$GUIDE_START_HOUR * 60 ))
    if [ "$total_mins" -lt "$start_mins" ]; then
        sleep_mins=$(( start_mins - total_mins ))
    else
        sleep_mins=$(( 1440 - total_mins + start_mins ))
    fi
    echo "[$(date -Iseconds)] Outside guide window (${GUIDE_START_HOUR}:00–${GUIDE_END_HOUR}:${GUIDE_END_MIN}), sleeping ${sleep_mins}m"
    sleep $(( sleep_mins * 60 ))
}

# .claude.json lives in ~ which is ephemeral; restore from the persistent named volume on each start
CLAUDE_BACKUP=$(ls -t ~/.claude/backups/.claude.json.backup.* 2>/dev/null | head -1)
if [ ! -f ~/.claude.json ] && [ -n "$CLAUDE_BACKUP" ]; then
    cp "$CLAUDE_BACKUP" ~/.claude.json
    echo "[startup] Restored .claude.json from $CLAUDE_BACKUP"
fi

# Trust the mounted repo (runs as uid 1000 matching host user)
git config --global --add safe.directory "${REPO_PATH}"

# Accept GitHub's SSH host key
mkdir -p ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts 2>/dev/null
chmod 600 ~/.ssh/known_hosts

# Switch remote to HTTPS and configure token auth
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
    # Refresh OAuth token if needed (no-op when ANTHROPIC_API_KEY is set)
    if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        python3 /app/scripts/refresh_oauth.py || true
    fi
    python3 /app/scripts/generate.py
    if in_guide_window; then
        python3 /app/scripts/guide_gen.py
    else
        echo "[$(date -Iseconds)] Skipping guide generation (outside window)"
    fi
    python3 /app/scripts/deploy.py
    echo "[$(date -Iseconds)] Sync complete"
}

# Run immediately on startup
run_pipeline || echo "[$(date -Iseconds)] Pipeline error (will retry next cycle)"

# Then loop — sleep until next window if outside, otherwise use normal interval
SLEEP_SECS=$(( RUN_INTERVAL_HOURS * 3600 ))
while true; do
    if in_guide_window; then
        sleep "${SLEEP_SECS}"
    else
        sleep_until_window
    fi
    run_pipeline || echo "[$(date -Iseconds)] Pipeline error (will retry next cycle)"
done
