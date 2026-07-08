"""Fetch a user's VNDB list by label and return structured VN metadata."""
import json
import os
import re
import time
import urllib.request
import urllib.error
import urllib.parse

VNDB_API = "https://api.vndb.org/kana"


def _get(endpoint: str, params: dict) -> dict:
    qs = urllib.parse.urlencode(params)
    url = f"{VNDB_API}/{endpoint}?{qs}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _post(endpoint: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{VNDB_API}/{endpoint}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def resolve_user_id(username: str) -> str:
    """Convert a VNDB username to its u<number> ID.

    The /ulist endpoint requires the u-prefixed numeric form (e.g. 'u196330'),
    not a plain username string.
    """
    if username.startswith("u") and username[1:].isdigit():
        return username
    result = _get("user", {"q": username})
    if username in result:
        return result[username]["id"]
    raise ValueError(f"VNDB user not found: {username!r}")


def _parse_cover(vn: dict) -> str | None:
    img = vn.get("image") or {}
    return img.get("url") if (img.get("sexual", 0) or 0) < 2 else None


def fetch_playing_list(user: str) -> list[dict]:
    """Return list of VNs from the user's VNDB list for the configured label.

    Label is read from VNDB_LABEL env var (default 31).
    Each entry: { vndb_id, title, alttitle, cover_url }
    cover_url is None if the cover is flagged sexual >= 2.
    """
    uid = resolve_user_id(user)
    label = int(os.environ.get("VNDB_LABEL", "31"))
    results = []
    page = 1
    while True:
        try:
            # ulist entry: { id: "v1234", vn: { title, alttitle, image{} } }
            body = _post("ulist", {
                "user": uid,
                "filters": ["label", "=", label],
                "fields": "vn{id,title,alttitle,image{url,sexual,violence}}",
                "results": 100,
                "page": page,
            })
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"[pull_vndb] Rate limited, sleeping 60s")
                time.sleep(60)
                continue
            raise

        for entry in body.get("results", []):
            vndb_id = entry["id"]  # top-level id IS the VN id in ulist responses
            vn = entry.get("vn") or {}
            results.append({
                "vndb_id": vndb_id,
                "title": vn.get("title", ""),
                "alttitle": vn.get("alttitle") or "",
                "cover_url": _parse_cover(vn),
            })

        if not body.get("more"):
            break
        page += 1
        time.sleep(1)

    return results


def lookup_vn_by_id(vndb_id: str) -> dict | None:
    """Fetch metadata for a single VN by ID."""
    try:
        body = _post("vn", {
            "filters": ["id", "=", vndb_id],
            "fields": "id,title,alttitle,image{url,sexual,violence}",
            "results": 1,
        })
        if body.get("results"):
            vn = body["results"][0]
            img = vn.get("image") or {}
            cover_url = img.get("url") if (img.get("sexual", 0) or 0) < 2 else None
            return {
                "vndb_id": vn["id"],
                "title": vn.get("title", ""),
                "alttitle": vn.get("alttitle") or "",
                "cover_url": cover_url,
            }
    except Exception as e:
        print(f"[pull_vndb] Failed to lookup {vndb_id}: {e}")
    return None


def title_to_slug(title: str) -> str | None:
    """Convert a VN title to a URL-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or None


if __name__ == "__main__":
    user = os.environ.get("VNDB_USER", "kanjieater")
    items = fetch_playing_list(user)
    print(json.dumps(items, ensure_ascii=False, indent=2))
