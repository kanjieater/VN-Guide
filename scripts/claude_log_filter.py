#!/usr/bin/env python3
"""
Read stream-json from claude -p --output-format stream-json on stdin,
print only the human-relevant lines: Claude's text narrations and tool calls.
"""
import json
import sys


def preview(inp: dict) -> str:
    for key in ("command", "url", "file_path", "query", "prompt"):
        if key in inp:
            return str(inp[key])[:120]
    return str(inp)[:120]


for raw in sys.stdin:
    raw = raw.strip()
    if not raw:
        continue
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        print(raw, flush=True)
        continue

    t = obj.get("type")

    if t == "assistant":
        for block in obj.get("message", {}).get("content", []):
            bt = block.get("type")
            if bt == "text" and block.get("text", "").strip():
                print(f"[claude] {block['text'].strip()[:300]}", flush=True)
            elif bt == "tool_use":
                name = block.get("name", "?")
                p = preview(block.get("input", {}))
                print(f"[tool:{name}] {p}", flush=True)

    elif t == "result":
        subtype = obj.get("subtype", "")
        if subtype == "error":
            print(f"[claude:error] {obj.get('error', '')}", flush=True)
        elif subtype == "success":
            print("[claude] done", flush=True)
