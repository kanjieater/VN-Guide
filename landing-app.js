(() => {
const GAMES = window.VN_GUIDE_GAMES || [];

const VISITED_KEY = "vn-guide-visited";
const GUIDE_META_CACHE = new Map();
const ROUTE_LENGTH_CACHE = new Map();
const root = document.documentElement;
let sortMode = root.dataset.vngSort || localStorage.getItem("vn-guide-sort") || "recent";
let filterMode = root.dataset.vngFilter || localStorage.getItem("vn-guide-filter") || "all";
let renderVersion = 0;

function applyControlState() {
  root.dataset.vngSort = sortMode;
  root.dataset.vngFilter = filterMode;
}

function getVisited() {
  try { return JSON.parse(localStorage.getItem(VISITED_KEY) || "{}"); } catch { return {}; }
}

function recordVisit(slug) {
  const v = getVisited();
  v[slug] = Date.now();
  localStorage.setItem(VISITED_KEY, JSON.stringify(v));
}

function displayName(g) {
  return g.alttitle || g.title;
}

function sortedGames() {
  const visited = getVisited();
  const games = [...GAMES];
  if (sortMode === "recent") {
    games.sort((a, b) => {
      const va = visited[a.slug] || 0;
      const vb = visited[b.slug] || 0;
      if (vb !== va) return vb - va;
      return displayName(a).localeCompare(displayName(b), "ja");
    });
  } else {
    games.sort((a, b) => displayName(a).localeCompare(displayName(b), "ja"));
  }
  return games;
}

function renderCard(g) {
  const name = displayName(g);
  const img = g.cover_url
    ? `<img class="game-cover" src="${g.cover_url}" alt="" loading="lazy">`
    : `<div class="game-cover-placeholder">📖</div>`;
  const badge = g.has_guide
    ? `<span class="game-badge badge-guide">攻略あり</span>`
    : `<span class="game-badge badge-wip">作成中</span>`;
  return `<a class="game-card" href="./${g.slug}/" onclick="recordVisit('${g.slug}')">
  ${img}
  <div class="game-info">
    <p class="game-title">${name}</p>
    ${badge}
  </div>
  <span class="game-arrow">›</span>
</a>`;
}

function guideStorageKey(slug) {
  const pathname = new URL(`./${encodeURIComponent(slug)}/`, location.href).pathname;
  return "guide_" + pathname.replace(/\//g, "_");
}

function savedGuideState(slug) {
  try {
    const raw = localStorage.getItem(guideStorageKey(slug));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

async function guideMeta(slug) {
  if (!GUIDE_META_CACHE.has(slug)) {
    GUIDE_META_CACHE.set(slug, fetch(`./${slug}/guide.json`, { cache: "no-store" })
      .then(res => res.ok ? res.json() : null)
      .catch(() => null));
  }
  return GUIDE_META_CACHE.get(slug);
}

async function routeLength(slug, route) {
  if (Array.isArray(route.steps)) return route.steps.length;

  const key = `${slug}:${route.id}`;
  if (!ROUTE_LENGTH_CACHE.has(key)) {
    ROUTE_LENGTH_CACHE.set(key, fetch(`./${slug}/route_${route.id}.json`, { cache: "no-store" })
      .then(res => res.ok ? res.json() : null)
      .then(steps => Array.isArray(steps) ? steps.length : null)
      .catch(() => null));
  }
  return ROUTE_LENGTH_CACHE.get(key);
}

async function isPlaying(g) {
  const saved = savedGuideState(g.slug);
  if (!saved || !saved.progress || Object.keys(saved.progress).length === 0) return false;

  const guide = await guideMeta(g.slug);
  if (!guide || !Array.isArray(guide.routes) || guide.routes.length === 0) return false;

  const startedRoutes = guide.routes.filter(route =>
    Object.prototype.hasOwnProperty.call(saved.progress, route.id)
  );
  if (startedRoutes.length === 0) return false;

  // Any valid started route means the game is currently playing, even when the
  // current step is 0 and the displayed overall percentage still rounds to 0%.
  if (startedRoutes.length < guide.routes.length) return true;

  // Every route has been started, so load the authoritative route arrays to
  // distinguish an in-progress game from one that is actually complete.
  const lengths = await Promise.all(
    guide.routes.map(route => routeLength(g.slug, route))
  );
  if (lengths.some(length => !Number.isInteger(length) || length < 1)) return true;

  return guide.routes.some((route, index) => {
    const progress = saved.progress[route.id];
    if (!Number.isInteger(progress) || progress < 0) return true;
    return progress < lengths[index] - 1;
  });
}

async function render() {
  const version = ++renderVersion;
  const list = document.getElementById("game-list");
  const q = (document.getElementById("search").value || "").trim().toLowerCase();
  let games = sortedGames();

  if (q) games = games.filter(g =>
    (g.title || "").toLowerCase().includes(q) ||
    (g.alttitle || "").toLowerCase().includes(q)
  );

  if (filterMode === "playing") {
    const matches = await Promise.all(games.map(async g => [g, await isPlaying(g)]));
    if (version !== renderVersion) return;
    games = matches.filter(([, playing]) => playing).map(([g]) => g);
  }

  const emptyText = filterMode === "playing"
    ? "プレイ中のゲームがありません"
    : (q ? "該当するゲームがありません" : "ゲームがありません");
  list.innerHTML = games.length
    ? games.map(renderCard).join("\n")
    : `<div class="empty-state">${emptyText}</div>`;

}

function setSort(mode) {
  sortMode = mode;
  localStorage.setItem("vn-guide-sort", mode);
  applyControlState();
  render();
}

function setFilter(mode) {
  filterMode = mode;
  localStorage.setItem("vn-guide-filter", mode);
  applyControlState();
  render();
}

Object.assign(window, {
  recordVisit,
  render,
  setSort,
  setFilter,
});

applyControlState();
render();
})();
