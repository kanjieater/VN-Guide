import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "bun:test";

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
