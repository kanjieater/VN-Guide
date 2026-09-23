import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "bun:test";
import { JSDOM } from "jsdom";

import { findGeneratedDrift } from "../tools/generate.mjs";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

test("committed generated artifacts are synchronized", async () => {
  assert.deepEqual(await findGeneratedDrift(ROOT), []);
});

test("agent docs contain no provider-specific model references", async () => {
  const files = [
    "AGENTS.md",
    "README.md",
    "agents/guide-standards.md",
    "agents/guide-author.md",
    "agents/authoring-contracts.md",
    "agents/guide-reviewer-structural.md",
    "agents/guide-reviewer-accuracy.md",
    "agents/guide-review.md",
    "black-matrix-oo/prompt_supplement.md"
  ];
  for (const file of files) {
    const content = await readFile(join(ROOT, file), "utf8");
    assert.doesNotMatch(content, /claude/i, file);
    assert.doesNotMatch(content, /\.claude\//i, file);
  }
});

test("all guide directories use the shared bootstrap shell", async () => {
  const shell = await readFile(join(ROOT, "templates", "guide.html"), "utf8");
  const entries = await readdir(ROOT, { withFileTypes: true });
  const guides = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    try {
      await readFile(join(ROOT, entry.name, "guide.json"), "utf8");
      guides.push(entry.name);
    } catch {}
  }

  assert.ok(guides.length > 0);
  for (const slug of guides) {
    assert.equal(await readFile(join(ROOT, slug, "index.html"), "utf8"), shell, slug);
  }
});


test("shared guide shell cache-busts both shared assets with one per-load version", async () => {
  const shell = await readFile(join(ROOT, "templates", "guide.html"), "utf8");
  const dom = new JSDOM(shell, {
    url: "https://example.test/game/",
    runScripts: "dangerously",
  });

  const style = dom.window.document.querySelector('link[rel="stylesheet"]');
  const app = [...dom.window.document.scripts].find(script =>
    script.src.includes("guide-app.js?v=")
  );

  assert.ok(style, "guide shell should inject the shared stylesheet");
  assert.ok(app, "guide shell should inject the shared app script");

  const styleUrl = new URL(style.href);
  const appUrl = new URL(app.src);
  const styleVersion = styleUrl.searchParams.get("v");
  const appVersion = appUrl.searchParams.get("v");

  assert.match(styleUrl.pathname, /\/style\.css$/);
  assert.match(appUrl.pathname, /\/guide-app\.js$/);
  assert.match(styleVersion, /^\d+$/);
  assert.equal(appVersion, styleVersion);
  assert.equal(Number(dom.window.__guideAssetVersion), Number(styleVersion));

  dom.window.close();
});
