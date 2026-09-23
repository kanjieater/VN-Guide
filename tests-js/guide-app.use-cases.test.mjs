import assert from "node:assert/strict";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { test } from "bun:test";

import { JSDOM } from "jsdom";


const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const APP_PATH = resolve(ROOT, "guide-app.js");
const APP_URL = pathToFileURL(APP_PATH).href;
let importCounter = 0;


function clone(value) {
  return value == null ? value : JSON.parse(JSON.stringify(value));
}


function response(body, ok = true) {
  return {
    ok,
    async json() {
      return clone(body);
    },
  };
}


async function settle() {
  await new Promise(resolvePromise => setTimeout(resolvePromise, 5));
  await new Promise(resolvePromise => setImmediate(resolvePromise));
}


function stateKey(pathname) {
  return "guide_" + pathname.replace(/\//g, "_");
}


function readState(window, pathname = "/game/") {
  const raw = window.localStorage.getItem(stateKey(pathname));
  return raw ? JSON.parse(raw) : null;
}

function installBrowserGlobals(window) {
  const values = {
    window,
    document: window.document,
    navigator: window.navigator,
    location: window.location,
    history: window.history,
    localStorage: window.localStorage,
    fetch: window.fetch,
    requestAnimationFrame: window.requestAnimationFrame.bind(window),
    cancelAnimationFrame: window.cancelAnimationFrame.bind(window),
  };
  for (const [name, value] of Object.entries(values)) {
    Object.defineProperty(globalThis, name, {
      configurable: true,
      writable: true,
      value,
    });
  }
}


async function bootApp({
  guide,
  routes = {},
  sidecar = null,
  pathname = "/game/",
  storage = {},
  guideFetchOk = true,
} = {}) {
  const dom = new JSDOM("<!doctype html><html><head></head><body><div id=\"app\"></div></body></html>", {
    url: `https://example.test${pathname}`,
    runScripts: "outside-only",
    pretendToBeVisual: true,
  });
  const { window } = dom;

  for (const [key, value] of Object.entries(storage)) {
    window.localStorage.setItem(key, value);
  }

  Object.defineProperty(window, "innerHeight", {
    configurable: true,
    writable: true,
    value: 900,
  });
  Object.defineProperty(window.navigator, "wakeLock", {
    configurable: true,
    value: {
      async request() {
        return { released: false };
      },
    },
  });

  window.requestAnimationFrame = callback => {
    callback(0);
    return 1;
  };
  window.cancelAnimationFrame = () => {};

  const fetchCalls = [];
  window.fetch = async input => {
    const url = String(input);
    fetchCalls.push(url);

    if (url.startsWith("./guide.json")) {
      return response(guide || { routes: [] }, guideFetchOk);
    }
    if (url.startsWith("./flowchart.json")) {
      return sidecar == null ? response({}, false) : response(sidecar, true);
    }

    const match = url.match(/^\.\/route_(.+?)\.json/);
    if (match) {
      const route = routes[match[1]];
      return route ? response(route, true) : response({}, false);
    }

    return response({}, false);
  };

  installBrowserGlobals(window);
  await import(`${APP_URL}?test=${++importCounter}`);
  await settle();

  return { dom, window, fetchCalls };
}


test.serial("reader can start, advance, reload, finish, and backtrack through a route transition", async () => {
  const guide = {
    title: "Demo VN",
    generated_at: "2026-09-23T12:00:00Z",
    guide_target: {
      label: "Demo Edition",
      platform: "Nintendo Switch",
      url: "https://example.test/release",
    },
    routes: [
      { id: "a", title: "Alpha", portrait: "alpha.jpg", stepCount: 2, reviewed: true },
      { id: "b", title: "Beta", portrait: "beta.jpg", stepCount: 1, reviewed: false },
    ],
  };
  const routes = {
    a: [{ simpleJp: "A1" }, { simpleJp: "A2" }],
    b: [{ simpleJp: "B1" }],
  };

  const first = await bootApp({ guide, routes });

  assert.equal(first.window.document.title, "Demo VN ガイド");
  assert.match(first.window.document.getElementById("route-list").textContent, /ルート 1/);
  assert.doesNotMatch(first.window.document.getElementById("route-list").textContent, /Alpha/);
  assert.match(first.window.document.getElementById("guide-target").textContent, /Demo Edition/);

  await first.window.startRoute("a");
  assert.equal(first.window.document.getElementById("step-counter").textContent, "1 / 2 (50%)");

  await first.window.nextStep();
  assert.equal(readState(first.window).progress.a, 1);
  const persistedState = first.window.localStorage.getItem(stateKey("/game/"));

  const second = await bootApp({
    guide,
    routes,
    storage: { [stateKey("/game/")]: persistedState },
  });

  await second.window.startRoute("a");
  assert.equal(second.window.document.getElementById("step-counter").textContent, "2 / 2 (100%)");

  await second.window.nextStep();
  assert.equal(second.window.document.getElementById("step-counter").textContent, "ルート完了");
  assert.match(second.window.document.getElementById("simple-instruction").textContent, /Beta/);

  await second.window.prevStep();
  await settle();
  assert.equal(second.window.document.getElementById("step-counter").textContent, "2 / 2 (100%)");
  assert.equal(readState(second.window).progress.a, 1);

  await second.window.nextStep();
  await second.window.nextStep();
  assert.equal(readState(second.window).currentRoute, "b");
  assert.equal(readState(second.window).progress.b, 0);
  assert.equal(second.window.document.getElementById("step-counter").textContent, "1 / 1 (100%)");

  second.window.goHome();
  assert.equal(readState(second.window).currentRoute, null);
  assert.match(second.window.document.getElementById("route-list").textContent, /Alpha/);
  first.dom.window.close();
  second.dom.window.close();
});


test.serial("flowchart exploration is preview-only until the reader explicitly continues", async () => {
  const guide = {
    title: "Preview VN",
    routes: [
      {
        id: "a",
        title: "Alpha",
        reviewed: true,
        steps: [
          { simpleJp: "A1" },
          { simpleJp: "A2" },
          { simpleJp: "A3" },
          { simpleJp: "A4" },
        ],
      },
    ],
  };

  const app = await bootApp({ guide });

  await app.window.startRoute("a");
  await app.window.nextStep();
  assert.equal(readState(app.window).progress.a, 1);

  let renderArgs = null;
  app.window.VNFlowchart = {
    render(...args) {
      renderArgs = args;
      args[0].textContent = "rendered";
    },
  };

  await app.window.showFlowchart();
  assert.equal(app.window.document.getElementById("flowchart-content").textContent, "rendered");
  assert.equal(renderArgs[4].current.a, 1);
  assert.equal(renderArgs[4].seen.a, 1);

  await app.window.jumpFromFlowchart("a", 2);
  assert.equal(readState(app.window).progress.a, 1);
  assert.match(app.window.document.getElementById("step-counter").textContent, /3 \/ 4 .*プレビュー/);
  assert.equal(app.window.document.getElementById("btn-next").textContent, "ここから進む ▶");

  await app.window.prevStep();
  assert.equal(readState(app.window).progress.a, 1);
  assert.match(app.window.document.getElementById("step-counter").textContent, /2 \/ 4 .*プレビュー/);

  await app.window.jumpFromFlowchart("a", 2);
  await app.window.nextStep();
  assert.equal(readState(app.window).progress.a, 3);
  assert.equal(readState(app.window).seenProgress.a, 3);
  assert.equal(app.window.document.getElementById("step-counter").textContent, "4 / 4 (100%)");
  app.dom.window.close();
});


test.serial("spoiler protection, settings persistence, and linear-game behavior match the reader model", async () => {
  const guide = {
    title: "Spoiler VN",
    routes: [
      { id: "a", title: "Secret Heroine", portrait: "secret.jpg", stepCount: 2 },
    ],
  };
  const routes = {
    a: [{ simpleJp: "First" }, { simpleJp: "Second" }],
  };

  const app = await bootApp({ guide, routes });

  let routeList = app.window.document.getElementById("route-list");
  assert.match(routeList.textContent, /ルート 1/);
  assert.ok(routeList.querySelector("img").classList.contains("locked"));

  app.window.showSettings();
  app.window.toggleSetting("blurPortraits");
  assert.deepEqual(JSON.parse(app.window.localStorage.getItem("vng_settings")), {
    blurPortraits: false,
  });

  app.window.goHome();
  routeList = app.window.document.getElementById("route-list");
  assert.match(routeList.textContent, /Secret Heroine/);
  assert.equal(routeList.querySelector("img").classList.contains("locked"), false);

  const linear = await bootApp({
    guide: {
      title: "Linear Game",
      vndb_id: "game:arc-the-lad-2",
      routes: [{ id: "chapter-1", title: "Chapter 1", stepCount: 1 }],
    },
    routes: { "chapter-1": [{ simpleJp: "Proceed" }] },
  });

  assert.match(linear.window.document.getElementById("route-list").textContent, /Chapter 1/);
  assert.equal(linear.window.document.getElementById("btn-flowchart").style.display, "none");
  await linear.window.showFlowchart();
  assert.ok(linear.window.document.getElementById("view-home").classList.contains("active"));
  app.dom.window.close();
  linear.dom.window.close();
});


test.serial("bad-end instructions remain understandable in both slide and jump-list views", async () => {
  const guide = {
    title: "Bad End VN",
    routes: [
      {
        id: "a",
        title: "Alpha",
        steps: [
          {
            simpleJp: "危険な選択",
            badEndPath: "BAD END 1",
            badEnd: { choice: "<危険>", end: "GAME OVER" },
            jpGuide1: "攻略①",
          },
          { simpleJp: "セーブ1にロード", isLoad: true },
          { simpleJp: "安全な選択", enGuide: "Safe choice" },
        ],
      },
    ],
  };

  const app = await bootApp({ guide });

  await app.window.startRoute("a");
  const badEnd = app.window.document.getElementById("detail-bad-end");
  assert.match(badEnd.textContent, /<危険>.*GAME OVER/);
  assert.match(badEnd.innerHTML, /&lt;危険&gt;/);

  app.window.toggleDetails();
  assert.equal(app.window.document.getElementById("details-section").style.display, "block");
  app.window.toggleDetails();
  assert.equal(app.window.document.getElementById("details-section").style.display, "none");

  await app.window.nextStep();
  assert.match(
    app.window.document.getElementById("simple-instruction").textContent,
    /BAD END 1 ⚠ セーブ1にロード/
  );

  app.window.showJump();
  assert.match(
    app.window.document.getElementById("jump-list").textContent,
    /BAD END 1 ⚠ セーブ1にロード/
  );

  app.window.jumpTo(2);
  assert.equal(readState(app.window).progress.a, 2);
  assert.equal(app.window.document.getElementById("simple-instruction").textContent, "安全な選択");
  app.dom.window.close();
});


test.serial("failed guide and route fetches leave the user on a recoverable home view", async () => {
  const failedGuide = await bootApp({
    guide: { routes: [] },
    guideFetchOk: false,
  });

  assert.ok(failedGuide.window.document.getElementById("view-home").classList.contains("active"));
  assert.match(failedGuide.window.document.getElementById("home-status").textContent, /ガイド作成中/);

  const missingRoute = await bootApp({
    guide: {
      title: "Incomplete",
      routes: [{ id: "missing", title: "Missing", stepCount: 2 }],
    },
  });

  await missingRoute.window.startRoute("missing");
  assert.ok(missingRoute.window.document.getElementById("view-home").classList.contains("active"));
  assert.match(missingRoute.window.document.getElementById("home-status").textContent, /生成中/);
  assert.deepEqual(readState(missingRoute.window), {
    currentRoute: null,
    progress: {},
    seenProgress: {},
  });
  failedGuide.dom.window.close();
  missingRoute.dom.window.close();
});
