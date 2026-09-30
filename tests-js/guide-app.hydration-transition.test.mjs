import assert from "node:assert/strict";
import { test } from "bun:test";
import { bootApp, deferred, settle, stateKey } from "./helpers/guide-app-harness.mjs";

const nav = state => ({ vng: true, ...state });

test("transition progress refreshes after background route hydration", async () => {
  const delayed = deferred();
  let requestedB = false;
  const guide = {
    title: "Hydration VN",
    routes: [
      {
        id: "a",
        title: "Alpha",
        steps: [{ simpleJp: "A1" }, { simpleJp: "A2" }],
      },
      { id: "b", title: "Beta" },
    ],
  };
  const saved = {
    currentRoute: "a",
    progress: { a: 1 },
    seenProgress: { a: 1 },
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
      { state: nav({ view: "transition", fromRouteId: "a", toRouteId: "b", origin: "forward" }), url: "/game/#view=transition&from=a&to=b&origin=forward" },
    ],
  });

  assert.equal(requestedB, true);
  assert.equal(app.window.history.state.view, "transition");
  assert.equal(app.window.document.getElementById("slide-route-title").textContent, "次へ · 50%");

  delayed.resolve([
    { simpleJp: "B1" },
    { simpleJp: "B2" },
    { simpleJp: "B3" },
  ]);
  await settle();

  assert.equal(app.window.history.state.view, "transition");
  assert.equal(app.window.document.getElementById("slide-route-title").textContent, "次へ · 33%");
  assert.match(app.window.document.getElementById("simple-instruction").textContent, /Beta/);

  app.dom.window.close();
});
