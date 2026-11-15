// Pure cover-selection rules shared by metadata refresh and tests.
// The original game's pinned edition must already be verified by the caller.
export const COVER_RANK = Object.freeze({ portrait: 0, square: 1, landscape: 2 });

export function coverAspect(dims) {
  if (!Array.isArray(dims) || dims.length !== 2 ||
      !dims.every(n => Number.isFinite(n) && n > 0)) return null;
  const ratio = dims[1] / dims[0];
  return ratio >= 1.15 ? "portrait" : ratio >= 0.88 ? "square" : "landscape";
}

export function isVndbCoverUrl(value) {
  try {
    const u = new URL(value);
    return u.protocol === "https:" &&
      (u.hostname === "vndb.org" || u.hostname.endsWith(".vndb.org"));
  } catch {
    return false;
  }
}

export function bestReleaseCover(release, id) {
  const images = (release?.images || []).filter(i =>
    i && isVndbCoverUrl(i.url) && (!i.vn || i.vn === id) &&
    (!i.languages || i.languages.includes("ja")) &&
    ["pkgfront", "dig"].includes(i.type) && coverAspect(i.dims));
  for (const aspect of ["portrait", "square", "landscape"]) {
    for (const type of ["pkgfront", "dig"]) {
      const matching = images.filter(i =>
        coverAspect(i.dims) === aspect && i.type === type);
      const urls = [...new Set(matching.map(i => i.url))];
      if (urls.length > 1) return null; // Do not resolve equal-priority ties by guessing.
      if (urls.length === 1) {
        return {
          url: urls[0],
          aspect,
          type,
          dimensions: matching[0].dims,
        };
      }
    }
  }
  return null;
}

export function currentCoverAspect(meta, release, id) {
  const fromMetadata = meta?.cover_selection?.aspect;
  if (Object.hasOwn(COVER_RANK, fromMetadata)) return fromMetadata;
  const fromDimensions = coverAspect(meta?.cover_selection?.dimensions);
  if (fromDimensions) return fromDimensions;
  // The URL must correspond exactly to a verified image in the selected release.
  const images = (release?.images || []).filter(i =>
    i?.url === meta?.cover_url && (!i.vn || i.vn === id) &&
    ["pkgfront", "dig"].includes(i.type));
  const aspects = [...new Set(images.map(i => coverAspect(i.dims)).filter(Boolean))];
  return aspects.length === 1 ? aspects[0] : null;
}

export function coverUpdateDecision(meta, proposal, release, id) {
  if (!meta || !proposal) return { update: false, reason: "no-target-or-candidate" };
  if (!meta.cover_url) return { update: true, reason: "missing-cover" };
  if (meta.cover_url === proposal.url) return { update: false, reason: "already-selected" };
  const currentAspect = currentCoverAspect(meta, release, id);
  if (!currentAspect) return { update: false, reason: "unverified-current-aspect" };
  // Same shape is NOT a reason to discard an already reviewed composition.
  // Only a strictly better aspect on this exact release can auto-replace it.
  if (COVER_RANK[proposal.aspect] >= COVER_RANK[currentAspect]) {
    return { update: false, reason: "equal-or-worse-aspect" };
  }
  return { update: true, reason: "better-aspect" };
}

export function vndbCoverProvenance(proposal, release) {
  return {
    aspect: proposal.aspect,
    source: "VNDB Kana exact-release cover",
    release_url: "https://vndb.org/" + release.id,
    image_type: proposal.type,
    dimensions: proposal.dimensions,
  };
}
