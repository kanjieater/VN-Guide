import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "bun:test";
import { JSDOM } from "jsdom";

import { landingGames, renderLanding } from "../tools/generate.mjs";

const APP_URL = new URL("../landing-app.js", import.meta.url).href;

function install(window) {
  for (const [name, value] of Object.entries({
    window,
    document: window.document,
    localStorage: window.localStorage,
    location: window.location,
    fetch: window.fetch,
  })) {
    Object.defineProperty(globalThis, name, {
      configurable: true,
      writable: true,
      value,
    });
  }
}

test("landing app covers search, sorting, visits, guide state, filters, and card variants", async () => {
  const games = {
    one: {
      slug: "日本語-game",
      title: "Roman One",
      alttitle: "日本語一",
      has_guide: true,
      cover_url: "cover.jpg",
    },
    two: {
      slug: "two",
      title: "Roman Two",
      alttitle: "",
      has_guide: false,
      cover_url: "",
    },
    three: {
      slug: "three",
      title: "Roman Three",
      alttitle: "日本語三",
      has_guide: true,
      cover_url: "",
    },
  };
  const template = await readFile(new URL("../templates/landing.html", import.meta.url), "utf8");
  const html = renderLanding(template, games);
  assert.match(html, /window\.VN_GUIDE_GAMES = \[/);
  assert.match(html, /<script src="\.\/landing-app\.js"><\/script>/);

  const dom = new JSDOM(html, {
    url: "https://example.test/",
    runScripts: "outside-only",
  });
  const { window } = dom;
  const calls = [];
  window.fetch = async url => {
    calls.push(String(url));
    if (String(url).includes("日本語-game")) {
      return {
        ok: true,
        async json() {
          return {
            routes: [
              { id: "route", stepCount: 4 },
              { id: "other", stepCount: 2 },
            ],
          };
        },
      };
    }
    if (String(url).includes("three")) {
      return {
        ok: true,
        async json() {
          return { routes: [{ id: "route", stepCount: 2 }] };
        },
      };
    }
    return { ok: false, async json() { return null; } };
  };
  window.VN_GUIDE_GAMES = landingGames(games);
  install(window);
  await import(APP_URL);

  await window.render();
  let text = window.document.getElementById("game-list").textContent;
  assert.match(text, /日本語一/);
  assert.match(text, /Roman Two/);
  assert.match(window.document.getElementById("game-list").innerHTML, /cover\.jpg/);
  assert.match(window.document.getElementById("game-list").innerHTML, /game-cover-placeholder/);
  assert.match(text, /攻略あり/);
  assert.match(text, /作成中/);

  window.recordVisit("two");
  assert.ok(JSON.parse(window.localStorage.getItem("vn-guide-visited")).two > 0);
  window.setSort("recent");
  assert.equal(window.localStorage.getItem("vn-guide-sort"), "recent");
  window.setSort("alpha");
  assert.equal(window.localStorage.getItem("vn-guide-sort"), "alpha");

  window.document.getElementById("search").value = "three";
  await window.render();
  text = window.document.getElementById("game-list").textContent;
  assert.match(text, /日本語三/);
  assert.doesNotMatch(text, /日本語一/);

  window.document.getElementById("search").value = "missing";
  await window.render();
  assert.match(window.document.getElementById("game-list").textContent, /該当するゲームがありません/);

  const encodedPath = new URL("./%E6%97%A5%E6%9C%AC%E8%AA%9E-game/", window.location.href).pathname;
  window.localStorage.setItem(
    "guide_" + encodedPath.replace(/\//g, "_"),
    JSON.stringify({ progress: { route: 1 } })
  );
  const twoKey = "guide_" + new URL("./two/", window.location.href).pathname.replace(/\//g, "_");
  window.localStorage.setItem(twoKey, "{invalid json");

  window.document.getElementById("search").value = "";
  window.setFilter("playing");
  await new Promise(resolve => setTimeout(resolve, 0));
  text = window.document.getElementById("game-list").textContent;
  assert.match(text, /日本語一/);
  assert.doesNotMatch(text, /Roman Two/);
  assert.equal(window.localStorage.getItem("vn-guide-filter"), "playing");

  window.localStorage.setItem(
    "guide_" + new URL("./three/", window.location.href).pathname.replace(/\//g, "_"),
    JSON.stringify({ progress: { route: 1 } })
  );
  window.VN_GUIDE_GAMES.find(g => g.slug === "three").has_guide = true;
  await window.render();
  assert.ok(calls.some(url => url.includes("guide.json")));

  window.setFilter("all");
  await window.render();
  assert.match(window.document.getElementById("game-list").textContent, /Roman Two/);

  dom.window.close();
});
