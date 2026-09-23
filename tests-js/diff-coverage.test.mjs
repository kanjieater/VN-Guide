import assert from "node:assert/strict";
import { test } from "bun:test";

import {
  isProductionSource,
  parseChangedLines,
  parseLcov,
  uncoveredChangedLines,
} from "../tools/check-diff-coverage.mjs";

test("production source scope is dynamic and intentional exclusions are explicit", () => {
  assert.equal(isProductionSource("guide-app.js"), true);
  assert.equal(isProductionSource("landing-app.js"), true);
  assert.equal(isProductionSource("future/new-runtime.mjs"), true);
  assert.equal(isProductionSource("tools/generate.mjs"), true);
  assert.equal(isProductionSource("tools/generate-cli.mjs"), false);
  assert.equal(isProductionSource("tools/check-diff-coverage.mjs"), false);
  assert.equal(isProductionSource("tests-js/new-runtime.test.mjs"), false);
  assert.equal(isProductionSource("README.md"), false);
});

test("diff coverage discovers future executable sources without an allowlist", () => {
  const diff = [
    "+++ b/guide-app.js",
    "@@ -10,0 +11,3 @@",
    "+++ b/README.md",
    "@@ -1,0 +2,4 @@",
    "+++ b/future/new-runtime.mjs",
    "@@ -0,0 +1,2 @@",
    "+++ b/tools/generate.mjs",
    "@@ -20 +20,2 @@",
  ].join("\n");

  const changed = parseChangedLines(diff);
  assert.deepEqual([...changed.get("guide-app.js")], [11, 12, 13]);
  assert.deepEqual([...changed.get("future/new-runtime.mjs")], [1, 2]);
  assert.deepEqual([...changed.get("tools/generate.mjs")], [20, 21]);
  assert.equal(changed.has("README.md"), false);

  const coverage = parseLcov([
    "SF:guide-app.js",
    "DA:11,1",
    "DA:13,0",
    "end_of_record",
    "SF:/repo/tools/generate.mjs",
    "DA:20,1",
    "end_of_record",
  ].join("\n"));

  assert.deepEqual(uncoveredChangedLines(changed, coverage), [
    "guide-app.js:13",
    "future/new-runtime.mjs: missing from LCOV",
  ]);
});

test("deleted executable sources do not create impossible coverage requirements", () => {
  const changed = parseChangedLines([
    "+++ /dev/null",
    "@@ -1,2 +0,0 @@",
  ].join("\n"));
  assert.equal(changed.size, 0);
});
