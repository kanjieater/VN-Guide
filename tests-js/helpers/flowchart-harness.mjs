import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const FLOWCHART_URL = pathToFileURL(resolve(ROOT, "flowchart.js")).href;

export async function createFlowchartRuntime() {
  const dom = new JSDOM("<!doctype html><html><body><div id=\"chart\"></div></body></html>", {
    url: "https://example.test/game/",
    pretendToBeVisual: true,
  });
  const { window } = dom;
  window.requestAnimationFrame = callback => {
    callback(0);
    return 1;
  };
  window.cancelAnimationFrame = () => {};
  Object.defineProperty(globalThis, "requestAnimationFrame", {
    configurable: true,
    writable: true,
    value: window.requestAnimationFrame.bind(window),
  });
  Object.defineProperty(globalThis, "cancelAnimationFrame", {
    configurable: true,
    writable: true,
    value: window.cancelAnimationFrame.bind(window),
  });
  Object.defineProperty(globalThis, "window", {
    configurable: true,
    writable: true,
    value: window,
  });
  Object.defineProperty(globalThis, "document", {
    configurable: true,
    writable: true,
    value: window.document,
  });

  await import(FLOWCHART_URL);
  return { dom, window, api: window.VNFlowchart };
}

export function resetChart(runtime) {
  runtime.window.document.body.innerHTML = '<div id="chart"></div>';
  return runtime.window.document.getElementById("chart");
}
