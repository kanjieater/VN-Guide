import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { expectedGeneratedFiles, REPO_ROOT } from "./generate.mjs";

export async function syncLandingIndex(root = REPO_ROOT, { check = false } = {}) {
  const expected = (await expectedGeneratedFiles(root)).get("index.html");
  const path = join(root, "index.html");
  const current = await readFile(path, "utf8").catch(error => {
    if (error.code === "ENOENT") return null;
    throw error;
  });
  if (current === expected) return false;
  if (check) throw new Error("Root index.html is out of sync with game directories");
  await writeFile(path, expected);
  return true;
}

if (import.meta.main) {
  const changed = await syncLandingIndex(REPO_ROOT, { check: process.argv.includes("--check") });
  console.log(changed ? "Updated root index.html" : "Root index.html already current");
}
