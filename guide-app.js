// ── App state ─────────────────────────────────────────────────────────────────
const STORAGE_KEY = "guide_" + location.pathname.replace(/\//g, "_");
const SETTINGS_KEY = "vng_settings";

let guideData = { routes: [] };
let state = { currentRoute: null, progress: {} };
let settings = { blurPortraits: true };
let pendingNextRoute = null;
let transitionFromRoute = null;
let flowchartScriptPromise = null;

function mountAppShell() {
  const app = document.getElementById("app");
  if (!app) return;

  app.innerHTML = `
    <div id="view-home" class="view active">
      <div class="view-header">
        <a href="../">← 戻る</a>
        <h3 id="game-title"></h3>
        <button id="btn-flowchart" class="icon-button" onclick="showFlowchart()" style="display:none" aria-label="分岐図" title="分岐図"><svg class="flowchart-button-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="2" width="6" height="5" rx="1"></rect><rect x="2" y="17" width="7" height="5" rx="1"></rect><rect x="15" y="17" width="7" height="5" rx="1"></rect><path d="M12 7v5M5.5 17v-3h13v3"></path></svg></button>
        <button onclick="showSettings()">⚙</button>
      </div>
      <div class="home-content">
        <p id="home-status">ガイド作成中…<br>しばらくお待ちください</p>
        <p id="total-progress"></p>
        <ul id="route-list"></ul>
        <div class="guide-meta">
          <p id="guide-updated"></p>
          <p id="guide-target"></p>
        </div>
      </div>
    </div>

    <div id="view-slide" class="view">
      <div class="view-header">
        <button onclick="goHome()">🏠</button>
        <h3 id="slide-route-title"></h3>
        <button onclick="showSettings()">⚙</button>
        <button onclick="showJump()">一覧</button>
      </div>
      <div class="step-container">
        <div id="step-counter"></div>
        <div id="simple-instruction"></div>
        <button id="toggle-details" onclick="toggleDetails()">詳細を表示</button>
        <div id="details-section">
          <div class="detail-block" id="detail-jp1"></div>
          <div class="detail-block" id="detail-jp2"></div>
          <div class="detail-block" id="detail-en"></div>
          <div class="detail-block bad-end-block" id="detail-bad-end" style="display:none"></div>
        </div>
      </div>
      <div class="nav-buttons">
        <button id="btn-prev" onclick="prevStep()">◀ 前へ</button>
        <button id="btn-next" onclick="nextStep()" class="primary">次へ ▶</button>
      </div>
    </div>

    <div id="view-jump" class="view">
      <div class="view-header">
        <button onclick="resumeSlide()">◀ 戻る</button>
        <h3 id="jump-route-title"></h3>
      </div>
      <div id="jump-list-container">
        <ul id="jump-list"></ul>
      </div>
    </div>

    <div id="view-flowchart" class="view">
      <div class="view-header">
        <button onclick="renderHome()">◀ 戻る</button>
        <h3>分岐図</h3>
      </div>
      <div id="flowchart-content" class="flowchart-body">
        <p class="flowchart-loading">分岐図を準備中…</p>
      </div>
    </div>

    <div id="view-settings" class="view">
      <div class="view-header">
        <button onclick="goHome()">◀ 戻る</button>
        <h3>設定</h3>
        <div style="width:50px"></div>
      </div>
      <div class="settings-body">
        <div class="setting-row" onclick="toggleSetting('blurPortraits')">
          <div>
            <div class="setting-label">キャラクター画像をぼかす</div>
            <div class="setting-desc">未開始のルートの画像を隠す（ネタバレ防止）</div>
          </div>
          <div id="toggle-blurPortraits" class="toggle-pill"></div>
        </div>
      </div>
    </div>
  `;
}

function loadState() {
  try { const s = localStorage.getItem(STORAGE_KEY); if (s) state = JSON.parse(s); } catch {}
}

function saveState() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch {}
}

function loadSettings() {
  try { const s = localStorage.getItem(SETTINGS_KEY); if (s) settings = { ...settings, ...JSON.parse(s) }; } catch {}
}

function saveSettings() {
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); } catch {}
}


// ── Viewport sizing ───────────────────────────────────────────────────────────
// Some Android split-screen/browser combinations can leave CSS dynamic viewport
// units stale until the window is manually resized. Mirror the visual viewport
// into a CSS variable and refresh it after resize transitions settle.
let viewportSyncTimer = null;

function syncViewportHeight() {
  const visualHeight = window.visualViewport && window.visualViewport.height;
  const height = visualHeight || window.innerHeight;
  if (height > 0) {
    document.documentElement.style.setProperty("--app-height", `${Math.round(height)}px`);
  }
}

function scheduleViewportSync() {
  syncViewportHeight();
  requestAnimationFrame(syncViewportHeight);
  clearTimeout(viewportSyncTimer);
  viewportSyncTimer = setTimeout(syncViewportHeight, 250);
}

window.addEventListener("resize", scheduleViewportSync, { passive: true });
window.addEventListener("orientationchange", scheduleViewportSync, { passive: true });
window.addEventListener("pageshow", scheduleViewportSync);
if (window.visualViewport) {
  window.visualViewport.addEventListener("resize", scheduleViewportSync, { passive: true });
}

// ── View management ───────────────────────────────────────────────────────────
function showView(id) {
  syncViewportHeight();
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

// ── Home ──────────────────────────────────────────────────────────────────────
async function init() {
  loadSettings();
  loadState();
  try {
    const res = await fetch("./guide.json?v=" + Date.now());
    if (res.ok) {
      guideData = await res.json();
      if (guideData.title) document.title = guideData.title + " ガイド";
    }
  } catch {}
  renderHome();
  requestWakeLock();
}

function renderHome() {
  const list = document.getElementById("route-list");
  const status = document.getElementById("home-status");
  const titleEl = document.getElementById("game-title");
  if (titleEl && guideData.title) titleEl.textContent = guideData.title;

  const targetEl = document.getElementById("guide-target");
  const updatedEl = document.getElementById("guide-updated");
  const target = guideData.guide_target;
  if (targetEl && target && target.label && target.platform && target.url) {
    const display = target.label + " · " + target.platform;
    const link = document.createElement("a");
    link.href = target.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = display;
    targetEl.replaceChildren(
      document.createTextNode("対象版: "),
      link,
    );
    targetEl.style.display = "";
    targetEl.style.cssText =
      "margin:0;font-size:12px;color:#888;text-align:center;";
    link.style.color = "inherit";
    link.style.textDecoration = "underline";
  } else if (targetEl) {
    targetEl.style.display = "none";
  }
  if (!guideData.routes || guideData.routes.length === 0) {
    list.innerHTML = "";
    status.style.display = "";
    showView("view-home");
    return;
  }
  status.style.display = "none";
  const isLinearGame = isLinearGameGuide();
  const flowchartButton = document.getElementById("btn-flowchart");
  if (flowchartButton) flowchartButton.style.display = isLinearGame ? "none" : "";
  list.innerHTML = guideData.routes.map((r, routeIdx) => {
    const started = r.id in state.progress;
    const prog = state.progress[r.id] || 0;
    const total = r.steps ? r.steps.length : (r.stepCount || 0);
    const pct = (started && total > 0) ? Math.round(prog / Math.max(total - 1, 1) * 100) : 0;
    const hasProgress = started && prog > 0;
    const shouldBlur = settings.blurPortraits && !hasProgress;
    const portrait = r.portrait
      ? `<img src="${escHtml(r.portrait)}" class="route-portrait${shouldBlur ? ' locked' : ''}" alt="" loading="lazy">`
      : '';
    const displayTitle = (!isLinearGame && settings.blurPortraits && !hasProgress) ? `ルート ${routeIdx + 1}` : r.title;
    const statusIcon = r.reviewed === true
      ? '<span class="route-status-icon reviewed-icon" aria-label="検証済み"></span>'
      : '<span class="route-status-icon unreviewed-icon" aria-label="未検証"></span>';
    return `<li><button onclick="startRoute('${r.id}')">
      ${portrait}
      <div class="route-info">
        <span>${displayTitle}${statusIcon}</span>
        <span style="font-size:13px;color:#888;font-weight:400">${pct}%</span>
      </div>
    </button></li>`;
  }).join("");
  const totalPct = overallProgressPercent();
  const totalEl = document.getElementById("total-progress");
  if (totalEl) {
    totalEl.style.cssText = "margin:0;font-size:13px;color:#888;";
    totalEl.textContent = `全体進行度: ${totalPct}%`;
  }

  if (updatedEl && guideData.generated_at) {
    const d = new Date(guideData.generated_at);
    updatedEl.textContent = `最終更新: ${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`;
    updatedEl.style.cssText = "margin:16px 0 0;font-size:12px;color:#666;text-align:center;";
  }

  showView("view-home");
}

async function startRoute(id) {
  const route = guideData.routes.find(r => r.id === id);
  if (route && !route.steps) {
    try {
      const v = guideData.generated_at ? encodeURIComponent(guideData.generated_at) : Date.now();
      const res = await fetch(`./route_${id}.json?v=${v}`);
      if (res.ok) {
        route.steps = await res.json();
      } else {
        const statusEl = document.getElementById("home-status");
        statusEl.textContent = `${route ? route.title : id} のガイドは生成中です…`;
        statusEl.style.display = "";
        showView("view-home");
        return;
      }
    } catch { renderHome(); return; }
  }
  // Only update state after route loads successfully
  state.currentRoute = id;
  if (!(id in state.progress)) state.progress[id] = 0;
  saveState();
  renderSlide();
}

// ── Flowchart ──────────────────────────────────────────────────────────────────
async function loadRouteForFlowchart(route) {
  if (route.steps) return true;
  try {
    const v = guideData.generated_at ? encodeURIComponent(guideData.generated_at) : Date.now();
    const res = await fetch("./route_" + route.id + ".json?v=" + v);
    if (!res.ok) return false;
    route.steps = await res.json();
    return true;
  } catch {
    return false;
  }
}

async function loadFlowchartRenderer() {
  if (window.VNFlowchart) return;
  if (!flowchartScriptPromise) {
    flowchartScriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      const v = window.__guideAssetVersion || Date.now();
      script.src = "../flowchart.js?v=" + v;
      script.onload = resolve;
      script.onerror = () => {
        flowchartScriptPromise = null;
        reject(new Error("flowchart renderer failed to load"));
      };
      document.head.appendChild(script);
    });
  }
  await flowchartScriptPromise;
  if (!window.VNFlowchart) throw new Error("flowchart renderer unavailable");
}

async function showFlowchart() {
  if (isLinearGameGuide()) return;
  const content = document.getElementById("flowchart-content");
  if (!content) return;

  content.innerHTML = '<p class="flowchart-loading">分岐図を生成中…</p>';
  showView("view-flowchart");

  try {
    await Promise.all((guideData.routes || []).map(loadRouteForFlowchart));
    await loadFlowchartRenderer();
    window.VNFlowchart.render(content, guideData, jumpFromFlowchart);
  } catch {
    content.innerHTML = '<p class="flowchart-error">分岐図を読み込めませんでした。</p>';
  }
}

async function jumpFromFlowchart(routeId, stepIndex) {
  const route = (guideData.routes || []).find(r => r.id === routeId);
  if (!route || !(await loadRouteForFlowchart(route)) || !route.steps.length) return;

  const target = stepIndex < 0
    ? 0
    : Math.max(0, Math.min(stepIndex, route.steps.length - 1));

  state.currentRoute = route.id;
  state.progress[route.id] = target;
  saveState();
  renderSlide();
}

// ── Slide ─────────────────────────────────────────────────────────────────────
function currentRoute() {
  return guideData.routes.find(r => r.id === state.currentRoute);
}

function isLinearGameGuide() {
  return String(guideData.vndb_id || "").startsWith("game:");
}

function nextRoute() {
  const idx = guideData.routes.findIndex(r => r.id === state.currentRoute);
  return idx >= 0 && idx < guideData.routes.length - 1
    ? guideData.routes[idx + 1]
    : null;
}

function previousRoute() {
  const idx = guideData.routes.findIndex(r => r.id === state.currentRoute);
  return idx > 0 ? guideData.routes[idx - 1] : null;
}

function routeStepCount(route) {
  return route.steps ? route.steps.length : (route.stepCount || 0);
}

function overallProgressPercent() {
  const maxProgress = guideData.routes.reduce((sum, route) => {
    const count = routeStepCount(route);
    return sum + Math.max(count - 1, 1);
  }, 0);
  const doneSteps = guideData.routes.reduce((sum, route) => {
    const count = routeStepCount(route);
    const progress = state.progress[route.id];
    if (progress === undefined) return sum;
    if (count === 1) return sum + 1;
    return sum + Math.max(0, Math.min(progress, count - 1));
  }, 0);
  return maxProgress ? Math.round(doneSteps / maxProgress * 100) : 0;
}

function renderRouteTransition(route, fromRoute = currentRoute()) {
  pendingNextRoute = route;
  transitionFromRoute = fromRoute;

  document.getElementById("slide-route-title").textContent = `次へ · ${overallProgressPercent()}%`;
  document.getElementById("step-counter").textContent = "ルート完了";

  const instrEl = document.getElementById("simple-instruction");
  const portrait = route.portrait
    ? `<img src="${escHtml(route.portrait)}" class="route-transition-portrait" alt="" loading="lazy">`
    : "";
  instrEl.innerHTML = `<div class="route-transition">
    <div class="route-transition-kicker">次のルートへ</div>
    ${portrait}
    <div class="route-transition-title">${escHtml(route.title || route.id)}</div>
  </div>`;

  document.getElementById("toggle-details").style.display = "none";
  document.getElementById("details-section").style.display = "none";

  document.getElementById("btn-prev").disabled = false;
  const nextBtn = document.getElementById("btn-next");
  nextBtn.disabled = false;
  nextBtn.textContent = "始める ▶";

  showView("view-slide");
}

// Scan backward from a load step to find the bad-end label that triggered it.
// Stops at any preceding load step so nested chains don't bleed into each other.
function findBadEndLabel(steps, loadIdx) {
  for (let i = loadIdx - 1; i >= 0; i--) {
    if (steps[i].isLoad) break;
    if (steps[i].badEndPath) return steps[i].badEndPath;
  }
  return null;
}

function renderSlide() {
  pendingNextRoute = null;
  transitionFromRoute = null;
  const route = currentRoute();
  if (!route || !route.steps || !route.steps.length) { renderHome(); return; }
  const idx = state.progress[route.id] || 0;
  const step = route.steps[idx];
  const total = route.steps.length;

  document.getElementById("slide-route-title").textContent = `${route.title} · ${overallProgressPercent()}%`;
  document.getElementById("step-counter").textContent = `${idx + 1} / ${total} (${Math.round((idx + 1) / total * 100)}%)`;
  const instrEl = document.getElementById("simple-instruction");
  if (step.isLoad) {
    const label = findBadEndLabel(route.steps, idx);
    instrEl.textContent = label ? `${label} ⚠ ${step.simpleJp || ""}` : (step.simpleJp || "");
  } else {
    instrEl.textContent = step.simpleJp || "";
  }

  const hasDetails = step.jpGuide1 || step.jpGuide2 || step.enGuide || step.badEnd || step.badEndPath;
  document.getElementById("toggle-details").style.display = hasDetails ? "" : "none";
  document.getElementById("details-section").style.display = "none";
  document.getElementById("toggle-details").textContent = "詳細を表示";

  const setDetail = (id, label, text) => {
    const el = document.getElementById(id);
    el.style.display = text ? "" : "none";
    if (text) el.innerHTML = `<h4>${label}</h4>${escHtml(text)}`;
  };
  setDetail("detail-jp1", "攻略サイト①", step.jpGuide1 || "");
  setDetail("detail-jp2", "攻略サイト②", step.jpGuide2 || "");
  setDetail("detail-en", "English", step.enGuide || "");

  const badEndEl = document.getElementById("detail-bad-end");
  if (step.badEnd) {
    badEndEl.style.display = "";
    badEndEl.innerHTML = `<h4 class="bad-end-block" style="margin:0 0 6px;font-size:12px;color:#e05050;text-transform:uppercase;letter-spacing:.06em;">バッドエンド</h4><span class="bad-end-choice">${escHtml(step.badEnd.choice)}</span> を選ぶ → ${escHtml(step.badEnd.end)}<br><small style="color:#888">ルート後にここにロードして次の選択肢へ</small>`;
  } else {
    badEndEl.style.display = "none";
  }

  const priorRoute = previousRoute();
  document.getElementById("btn-prev").disabled = idx === 0 && !priorRoute;
  const nextBtn = document.getElementById("btn-next");
  const followingRoute = nextRoute();
  const atSectionEnd = idx === total - 1;
  nextBtn.disabled = atSectionEnd && !followingRoute;
  nextBtn.textContent = atSectionEnd && followingRoute ? "次のセクションへ ▶" : "次へ ▶";

  showView("view-slide");
}

async function nextStep() {
  if (pendingNextRoute) {
    const route = pendingNextRoute;
    pendingNextRoute = null;
    await startRoute(route.id);
    return;
  }

  const route = currentRoute();
  if (!route) return;
  const idx = state.progress[route.id] || 0;
  if (idx < route.steps.length - 1) {
    state.progress[route.id] = idx + 1;
    saveState();
    renderSlide();
    return;
  }

  const followingRoute = nextRoute();
  if (followingRoute) renderRouteTransition(followingRoute);
}

async function prevStep() {
  if (pendingNextRoute) {
    const fromRoute = transitionFromRoute;
    pendingNextRoute = null;
    transitionFromRoute = null;

    if (fromRoute && fromRoute.id !== state.currentRoute) {
      await startRoute(fromRoute.id);
    } else {
      renderSlide();
    }
    return;
  }

  const route = currentRoute();
  if (!route) return;
  const idx = state.progress[route.id] || 0;
  if (idx > 0) {
    state.progress[route.id] = idx - 1;
    saveState();
    renderSlide();
    return;
  }

  const priorRoute = previousRoute();
  if (priorRoute) {
    renderRouteTransition(route, priorRoute);
  }
}

function toggleDetails() {
  const sec = document.getElementById("details-section");
  const btn = document.getElementById("toggle-details");
  const open = sec.style.display !== "none";
  sec.style.display = open ? "none" : "block";
  btn.textContent = open ? "詳細を表示" : "詳細を隠す";
}

function goHome() {
  state.currentRoute = null;
  saveState();
  renderHome();
}

// ── Jump list ─────────────────────────────────────────────────────────────────
function showJump() {
  const route = currentRoute();
  if (!route || !route.steps) return;
  document.getElementById("jump-route-title").textContent = route.title;
  const list = document.getElementById("jump-list");
  list.innerHTML = route.steps.map((s, i) => {
    let display = escHtml(s.simpleJp || '');
    let prefix = '';
    if (s.isLoad) {
      const label = findBadEndLabel(route.steps, i);
      if (label) { display = `${escHtml(label)} ⚠ ${display}`; }
      else { prefix = '↩ '; }
    }
    return `<li><button onclick="jumpTo(${i})">
      <span class="jump-num">${i + 1}</span>
      <span>${prefix}${display}</span>
    </button></li>`;
  }).join("");
  showView("view-jump");
}

function jumpTo(idx) {
  const route = currentRoute();
  if (!route) return;
  state.progress[route.id] = idx;
  saveState();
  renderSlide();
}

function resumeSlide() { renderSlide(); }

// ── Settings ──────────────────────────────────────────────────────────────────
function showSettings() {
  for (const [k, v] of Object.entries(settings)) {
    const el = document.getElementById(`toggle-${k}`);
    if (el) el.classList.toggle("on", !!v);
  }
  showView("view-settings");
}

function toggleSetting(key) {
  settings[key] = !settings[key];
  const el = document.getElementById(`toggle-${key}`);
  if (el) el.classList.toggle("on", settings[key]);
  saveSettings();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function escHtml(s) {
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

let wakeLock = null;
async function requestWakeLock() {
  try { wakeLock = await navigator.wakeLock.request("screen"); } catch {}
}
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    scheduleViewportSync();
    requestWakeLock();
  }
});

mountAppShell();
scheduleViewportSync();
init();
