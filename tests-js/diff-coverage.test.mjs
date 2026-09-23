import assert from "node:assert/strict";
import { test } from "bun:test";

import { parseChangedLines, parseLcov, uncoveredChangedLines } from "../tools/check-diff-coverage.mjs";

test("diff coverage evaluates executable changed lines in tracked source files", () => {
  const diff = [
    "+++ b/guide-app.js",
    "@@ -10,0 +11,3 @@",
    "+++ b/README.md",
    "@@ -1,0 +2,4 @@",
    "+++ b/tools/generate.mjs",
    "@@ -20 +20,2 @@"
  ].join("\n");
  const changed = parseChangedLines(diff);
  assert.deepEqual([...changed.get("guide-app.js")], [11, 12, 13]);
  assert.deepEqual([...changed.get("tools/generate.mjs")], [20, 21]);
  assert.equal(changed.has("README.md"), false);

  const coverage = parseLcov([
    "SF:guide-app.js",
    "DA:11,1",
    "DA:13,0",
    "end_of_record",
    "SF:/repo/tools/generate.mjs",
    "DA:20,1",
    "end_of_record"
  ].join("\n"));

  assert.deepEqual(uncoveredChangedLines(changed, coverage), ["guide-app.js:13"]);
});

test("diff coverage fails closed when changed source is absent from LCOV", () => {
  const changed = new Map([["flowchart.js", new Set([5])]]);
  assert.deepEqual(uncoveredChangedLines(changed, new Map()), ["flowchart.js: missing from LCOV"]);
});
