"""
Refresh the Claude Code OAuth access token using the stored refresh token.
Reads/writes ~/.claude/.credentials.json in place.
Called by entrypoint.sh before guide_gen.py so the token is always fresh.
"""
import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

CREDS_FILE = Path.home() / ".claude" / ".credentials.json"
TOKEN_ENDPOINT = "https://platform.claude.com/v1/oauth/token"
CLIENT_ID = "https://claude.ai/oauth/claude-code-client-metadata"
# Refresh if token expires within this many seconds
REFRESH_THRESHOLD = 300


def log(msg: str) -> None:
    print(f"[refresh_oauth] {msg}", flush=True)


def refresh() -> bool:
    if not CREDS_FILE.exists():
        log("No credentials file found, skipping")
        return False

    try:
        creds = json.loads(CREDS_FILE.read_text())
    except Exception as e:
        log(f"Failed to read credentials: {e}")
        return False

    oauth = creds.get("claudeAiOauth", {})
    refresh_token = oauth.get("refreshToken")
    expires_at = oauth.get("expiresAt", 0)
    refresh_expires_at = oauth.get("refreshTokenExpiresAt", 0)

    if not refresh_token:
        log("No refresh token found")
        return False

    now_ms = int(time.time() * 1000)

    if refresh_expires_at and now_ms > refresh_expires_at:
        log("Refresh token has expired — manual re-auth required")
        return False

    if expires_at and (expires_at - now_ms) > REFRESH_THRESHOLD * 1000:
        log(f"Access token still valid for {(expires_at - now_ms) // 1000}s, skipping refresh")
        return True

    log("Refreshing access token...")
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
    }).encode()

    req = urllib.request.Request(
        TOKEN_ENDPOINT,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        log(f"Token refresh request failed: {e}")
        return False

    if "access_token" not in data:
        log(f"Unexpected response: {list(data.keys())}")
        return False

    expires_in = data.get("expires_in", 3600)
    oauth["accessToken"] = data["access_token"]
    oauth["expiresAt"] = now_ms + expires_in * 1000
    if "refresh_token" in data:
        oauth["refreshToken"] = data["refresh_token"]
    if "refresh_token_expires_in" in data:
        oauth["refreshTokenExpiresAt"] = now_ms + data["refresh_token_expires_in"] * 1000

    creds["claudeAiOauth"] = oauth
    CREDS_FILE.write_text(json.dumps(creds, indent=2))
    log(f"Token refreshed, valid for {expires_in}s")
    return True


if __name__ == "__main__":
    ok = refresh()
    sys.exit(0 if ok else 1)
