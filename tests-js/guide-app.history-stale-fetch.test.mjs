import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, deferred, moveHistory, readState, settle, stateKey } from "./helpers/guide-app-harness.mjs";

const nav = state => ({ vng: true, ...state });

test("browser Back wins over a delayed next-route fetch", async () => {
  const delayed = deferred();
  let requestedB = false;
  const guide = {
    title: "Race VN",
    routes: [
      { id: "a", title: "Alpha", steps: [{ simpleJp: "A1" }] },
      { id: "b", title: "Beta", stepCount: 1 },
    ],
  };
  const saved = {
    currentRoute: "a",
    progress: { a: 0 },
    seenProgress: { a: 0 },
  };

  const app = await bootApp({
    guide,
    storage: { [stateKey("/game/")]: JSON.stringify(saved) },
    routeFetchers: {
      b: async () => {
        requestedB = true;
        return delayed.promise;
      },
    },
    initialHistory: [
      { state: nav({ view: "route", routeId: "a", step: 0, fromView: "home" }), url: "/game/#view=route&route=a&step=0&from=home" },
      { state: nav({ view: "transition", fromRouteId: "a", toRouteId: "b", origin: "forward" }), url: "/game/#view=transition&from=a&to=b&origin=forward" },
    ],
  });

  assert.equal(app.window.history.state.view, "transition");
  const startB = app.window.nextStep();
  await settle();
  assert.equal(requestedB, true);

  await moveHistory(app.window, "back");
  assert.equal(app.window.history.state.view, "route");
  assert.equal(app.window.history.state.routeId, "a");
  assert.match(app.window.document.getElementById("slide-route-title").textContent, /Alpha/);

  delayed.resolve([{ simpleJp: "B1" }]);
  await startB;
  await settle();

  assert.equal(app.window.history.state.view, "route");
  assert.equal(app.window.history.state.routeId, "a");
  assert.equal(readState(app.window).currentRoute, "a");
  assert.match(app.window.document.getElementById("simple-instruction").textContent, /A1/);

  app.dom.window.close();
});
