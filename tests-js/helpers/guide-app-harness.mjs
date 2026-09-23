import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const APP_URL = pathToFileURL(resolve(ROOT, "guide-app.js")).href;

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

export async function settle() {
  await new Promise(resolvePromise => setTimeout(resolvePromise, 5));
  await new Promise(resolvePromise => setImmediate(resolvePromise));
}

export function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

export async function moveHistory(window, direction) {
  const popstate = new Promise((resolvePromise, rejectPromise) => {
    const timeout = setTimeout(
      () => rejectPromise(new Error(`Timed out waiting for popstate after history.${direction}()`)),
      500
    );
    window.addEventListener("popstate", event => {
      clearTimeout(timeout);
      resolvePromise(event);
    }, { once: true });
  });
  window.history[direction]();
  await popstate;
  await settle();
}

export function stateKey(pathname) {
  return "guide_" + pathname.replace(/\//g, "_");
}

export function readState(window, pathname = "/game/") {
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

export async function bootApp({
  guide,
  routes = {},
  sidecar = null,
  pathname = "/game/",
  storage = {},
  guideFetchOk = true,
  routeFetchers = {},
  initialHistory = [],
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

  if (initialHistory.length) {
    const [first, ...rest] = initialHistory;
    window.history.replaceState(clone(first.state), "", first.url);
    for (const entry of rest) {
      window.history.pushState(clone(entry.state), "", entry.url);
    }
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
      const routeId = match[1];
      if (routeFetchers[routeId]) {
        return response(await routeFetchers[routeId](), true);
      }
      const route = routes[routeId];
      return route ? response(route, true) : response({}, false);
    }

    return response({}, false);
  };

  installBrowserGlobals(window);
  await import(APP_URL);
  await settle();

  return { dom, window, fetchCalls };
}
