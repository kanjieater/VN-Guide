import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, moveHistory, readState, stateKey } from "./helpers/guide-app-harness.mjs";

const nav = state => ({ vng: true, ...state });

test("reload on route B preserves history so Back returns to the A→B transition", async () => {
  const guide = {
    title: "History VN",
    routes: [
      { id: "a", title: "Alpha", steps: [{ simpleJp: "A1" }, { simpleJp: "A2" }] },
      { id: "b", title: "Beta", steps: [{ simpleJp: "B1" }] },
    ],
  };
  const saved = {
    currentRoute: "b",
    progress: { a: 1, b: 0 },
    seenProgress: { a: 1, b: 0 },
  };

  const app = await bootApp({
    guide,
    storage: { [stateKey("/game/")]: JSON.stringify(saved) },
    initialHistory: [
      { state: nav({ view: "home" }), url: "/game/" },
      { state: nav({ view: "route", routeId: "a", step: 1, fromView: "home" }), url: "/game/#view=route&route=a&step=1&from=home" },
      { state: nav({ view: "transition", fromRouteId: "a", toRouteId: "b", origin: "forward" }), url: "/game/#view=transition&from=a&to=b&origin=forward" },
      { state: nav({ view: "route", routeId: "b", step: 0, fromView: "transition" }), url: "/game/#view=route&route=b&step=0&from=transition" },
    ],
  });

  assert.match(app.window.document.getElementById("slide-route-title").textContent, /Beta/);
  assert.equal(app.window.history.state.view, "route");
  assert.equal(app.window.history.state.routeId, "b");

  await moveHistory(app.window, "back");

  assert.equal(app.window.history.state.view, "transition");
  assert.equal(app.window.history.state.fromRouteId, "a");
  assert.equal(app.window.history.state.toRouteId, "b");
  assert.equal(app.window.document.getElementById("step-counter").textContent, "ルート完了");
  assert.match(app.window.document.getElementById("simple-instruction").textContent, /Beta/);
  assert.equal(readState(app.window).currentRoute, "a");

  app.dom.window.close();
});
