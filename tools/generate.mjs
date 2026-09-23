import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

export const REPO_ROOT = resolve(import.meta.dir, "..");

export function landingGames(games) {
  return Object.values(games).map(entry => ({
    slug: entry.slug,
    title: entry.title || entry.slug,
    alttitle: entry.alttitle || "",
    has_guide: Boolean(entry.has_guide),
    cover_url: entry.cover_url || "",
  }));
}

function inlineJson(value) {
  if (Array.isArray(value)) return `[${value.map(inlineJson).join(", ")}]`;
  if (value && typeof value === "object") {
    return `{${Object.entries(value)
      .map(([key, item]) => `${JSON.stringify(key)}: ${inlineJson(item)}`)
      .join(", ")}}`;
  }
  return JSON.stringify(value);
}

export function renderLanding(template, games) {
  return template.replace("/* GAMES_DATA */", inlineJson(landingGames(games)));
}

export function buildManifest(title) {
  return {
    name: `${title} ガイド`,
    short_name: "VN Guide",
    start_url: "./",
    scope: "./",
    display: "standalone",
    background_color: "#121212",
    theme_color: "#121212",
    icons: [
      { src: "../icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "../icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
    ],
  };
}

export async function expectedGeneratedFiles(root = REPO_ROOT) {
  const [gamesText, landingTemplate, guideTemplate] = await Promise.all([
    readFile(join(root, "games.json"), "utf8"),
    readFile(join(root, "templates", "landing.html"), "utf8"),
    readFile(join(root, "templates", "guide.html"), "utf8"),
  ]);
  const games = JSON.parse(gamesText);
  const expected = new Map([["index.html", renderLanding(landingTemplate, games)]]);

  for (const entry of Object.values(games)) {
    expected.set(`${entry.slug}/index.html`, guideTemplate);
    expected.set(
      `${entry.slug}/manifest.json`,
      JSON.stringify(buildManifest(entry.title || entry.slug), null, 2)
    );
  }

  return expected;
}

export async function findGeneratedDrift(root = REPO_ROOT) {
  const expected = await expectedGeneratedFiles(root);
  const drift = [];

  for (const [relativePath, expectedContent] of expected) {
    const fullPath = join(root, relativePath);
    const actual = existsSync(fullPath) ? await readFile(fullPath, "utf8") : null;
    if (actual !== expectedContent) drift.push({ relativePath, expectedContent });
  }

  return drift;
}

export async function syncGeneratedFiles(root = REPO_ROOT, { check = false } = {}) {
  const drift = await findGeneratedDrift(root);

  if (check && drift.length) {
    throw new Error(
      `Generated files are stale: ${drift.map(item => item.relativePath).join(", ")}`
    );
  }

  if (!check) {
    await Promise.all(drift.map(async ({ relativePath, expectedContent }) => {
      const fullPath = join(root, relativePath);
      await mkdir(dirname(fullPath), { recursive: true });
      await writeFile(fullPath, expectedContent);
    }));
  }

  return drift.map(item => item.relativePath);
}
