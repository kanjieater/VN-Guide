import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

/**
 * Existing games.json entries are a compatibility catalog. New games live in
 * <slug>/catalog.json and never require a shared-file change.
 */
export async function loadCatalog(root) {
  const legacy = JSON.parse(await readFile(join(root, "games.json"), "utf8"));
  const catalog = { ...legacy };
  const dirs = (await readdir(root, { withFileTypes: true }))
    .filter(item => item.isDirectory() && !item.name.startsWith("."))
    .map(item => item.name).sort();

  for (const slug of dirs) {
    let metadata;
    try {
      metadata = JSON.parse(await readFile(join(root, slug, "catalog.json"), "utf8"));
    } catch (error) {
      if (error.code === "ENOENT") continue;
      throw new Error(`Invalid ${slug}/catalog.json: ${error.message}`);
    }
    if (!metadata || typeof metadata !== "object" || Array.isArray(metadata))
      throw new Error(`Invalid ${slug}/catalog.json: expected object`);
    const id = metadata.vndb_id;
    if (typeof id !== "string" || !/^(?:v[0-9]+|game:[a-z0-9]+(?:-[a-z0-9]+)*)$/.test(id))
      throw new Error(`Invalid ${slug}/catalog.json: vndb_id required`);
    if (metadata.slug && metadata.slug !== slug)
      throw new Error(`Invalid ${slug}/catalog.json: slug must equal directory name`);
    if (catalog[id] && catalog[id].slug !== slug)
      throw new Error(`Duplicate VNDB id ${id}: ${catalog[id].slug} and ${slug}`);
    const guide = JSON.parse(await readFile(join(root, slug, "guide.json"), "utf8"));
    if (guide.vndb_id !== id || !Array.isArray(guide.routes) || !guide.routes.length)
      throw new Error(`Invalid ${slug}/guide.json: id/routes mismatch`);
    const reviewed = guide.routes.every(route => route.reviewed === true);
    const entry = { ...metadata, slug, has_guide: reviewed };
    delete entry.vndb_id;
    // Per-directory metadata is authoritative when migrating a legacy game.
    catalog[id] = entry;
  }
  return catalog;
}
