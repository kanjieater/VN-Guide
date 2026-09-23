import { readFile } from "node:fs/promises";

const TARGETS = new Set(["guide-app.js", "flowchart.js", "tools/generate.mjs"]);

export function parseLcov(text, files = new Map()) {
  let current = null;

  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith("SF:")) {
      current = line.slice(3).replaceAll("\\", "/");
      while (current.startsWith("./")) current = current.slice(2);
      if (!files.has(current)) files.set(current, new Map());
    } else if (current && line.startsWith("DA:")) {
      const [lineNumber, count] = line.slice(3).split(",").map(Number);
      const existing = files.get(current).get(lineNumber) || 0;
      files.get(current).set(lineNumber, existing + count);
    } else if (line === "end_of_record") {
      current = null;
    }
  }

  return files;
}

export function parseChangedLines(diff) {
  const changed = new Map();
  let file = null;

  for (const line of diff.split(/\r?\n/)) {
    if (line.startsWith("+++ b/")) {
      file = line.slice(6);
      if (TARGETS.has(file) && !changed.has(file)) changed.set(file, new Set());
      continue;
    }

    if (!file || !TARGETS.has(file) || !line.startsWith("@@")) continue;
    const match = line.match(/\+(\d+)(?:,(\d+))?/);
    if (!match) continue;

    const start = Number(match[1]);
    const count = match[2] === undefined ? 1 : Number(match[2]);
    for (let number = start; number < start + count; number++) {
      changed.get(file).add(number);
    }
  }

  return changed;
}

function coverageFor(files, file) {
  if (files.has(file)) return files.get(file);
  const suffix = `/${file}`;
  const match = [...files.entries()].find(([name]) => name.endsWith(suffix));
  return match ? match[1] : null;
}

export function uncoveredChangedLines(changed, coverage) {
  const uncovered = [];

  for (const [file, changedLines] of changed) {
    const fileCoverage = coverageFor(coverage, file);
    if (!fileCoverage) {
      uncovered.push(`${file}: missing from LCOV`);
      continue;
    }

    for (const line of changedLines) {
      if (fileCoverage.has(line) && fileCoverage.get(line) === 0) {
        uncovered.push(`${file}:${line}`);
      }
    }
  }

  return uncovered;
}

async function main() {
  const base = process.argv.slice(2).find(arg => arg !== "--");
  if (!base) throw new Error("Usage: bun tools/check-diff-coverage.mjs <base-ref>");

  const proc = Bun.spawnSync([
    "git", "diff", "--unified=0", "--no-color", `${base}...HEAD`, "--",
    "guide-app.js", "flowchart.js", "tools/generate.mjs",
  ]);
  if (proc.exitCode !== 0) throw new Error(proc.stderr.toString());

  const lcov = await readFile("coverage/lcov.info", "utf8");
  const uncovered = uncoveredChangedLines(
    parseChangedLines(proc.stdout.toString()),
    parseLcov(lcov)
  );

  if (uncovered.length) {
    console.error("Changed executable lines without coverage:");
    uncovered.forEach(item => console.error(`  ${item}`));
    process.exit(1);
  }
  console.log("100% changed-line coverage for executable app/generator code.");
}

if (import.meta.main) {
  main().catch(error => {
    console.error(error.message);
    process.exit(1);
  });
}
