#!/usr/bin/env python3
"""Non-destructive audit of every VN-Guide landing-card cover URL.

Run with: python tools/audit-covers.py
Outputs cover-audit.json and cover-audit-contact-sheet.jpg in /tmp/cover-audit
(or COVER_AUDIT_DIR). The report never modifies game metadata.
"""
import concurrent.futures
import io
import json
import os
import pathlib
import urllib.request
from PIL import Image, ImageDraw, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(os.environ.get("COVER_AUDIT_DIR", "/tmp/cover-audit"))
OUT.mkdir(parents=True, exist_ok=True)

catalog = json.loads((ROOT / "games.json").read_text())
for path in ROOT.glob("*/catalog.json"):
    data = json.loads(path.read_text())
    catalog[data["vndb_id"]] = dict(data, slug=path.parent.name)
games = [(key, data) for key, data in catalog.items() if data.get("cover_url")]


def check(entry):
    key, data = entry
    url = data["cover_url"]
    if url.startswith("./"):
        source = (ROOT / url.removeprefix("./")).read_bytes()
    else:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; VN-Guide-cover-audit/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            source = response.read(10_000_000)
    with Image.open(io.BytesIO(source)) as original:
        im = original.convert("RGB")
        w, h = im.size
        ratio = h / w
        aspect = "portrait" if ratio >= 1.15 else ("square" if ratio >= 0.90 else "landscape")
        thumb = ImageOps.fit(im, (128, 180), method=Image.Resampling.LANCZOS)
    return {
        "vndb_id": key, "slug": data["slug"], "url": url,
        "dimensions": [w, h], "aspect": aspect,
        "status": "ok", "image": thumb,
    }


results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    jobs = {pool.submit(check, e): e for e in games}
    for future in concurrent.futures.as_completed(jobs):
        key, data = jobs[future]
        try:
            results.append(future.result())
        except Exception as exc:
            results.append({
                "vndb_id": key, "slug": data["slug"], "url": data["cover_url"],
                "status": "unverified", "reason": str(exc)[:300],
            })

results.sort(key=lambda r: r["slug"])
cols = 6
rows = (len(results) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 165, rows * 220), "#f3f3f3")
draw = ImageDraw.Draw(sheet)
for index, item in enumerate(results):
    x, y = (index % cols) * 165, (index // cols) * 220
    image = item.pop("image", None)
    if image is not None:
        sheet.paste(image, (x + 19, y + 5))
    else:
        draw.rectangle((x + 19, y + 5, x + 147, y + 185), fill="#ccc", outline="#888")
    draw.text((x + 5, y + 189), item["slug"][:24], fill="black")
    draw.text((x + 5, y + 203), item.get("aspect", "UNVERIFIED") + " " +
              "x".join(map(str, item.get("dimensions", []))), fill="black")
    print(f'{item["slug"]}: {item["status"]} {item.get("aspect", "")} '
          f'{item.get("dimensions", "")} {item.get("reason", "")}')
sheet.save(OUT / "cover-audit-contact-sheet.jpg", quality=90)
(OUT / "cover-audit.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f'Checked {len(results)} covers: {sum(r["status"] == "ok" for r in results)} fetched, '
      f'{sum(r["status"] != "ok" for r in results)} inaccessible; '
      f'{sum(r.get("aspect") == "landscape" for r in results)} confirmed landscape.')
