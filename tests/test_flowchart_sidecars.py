import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLOWCHART = ROOT / "flowchart.js"

NODE_RUNNER = r"""
const fs = require("fs");
const vm = require("vm");
global.window = {};
const source = fs.readFileSync(process.argv[1], "utf8");
vm.runInThisContext(source, { filename: process.argv[1] });

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => input += chunk);
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    const graph = window.VNFlowchart.buildEnhancedGraph(payload.guide, payload.sidecar);
    process.stdout.write(JSON.stringify({
      ok: true,
      nodes: graph.nodes,
      edges: graph.edges,
      maxDepth: graph.maxDepth,
      maxRow: graph.maxRow,
    }));
  } catch (error) {
    process.stdout.write(JSON.stringify({
      ok: false,
      error: String(error && error.message ? error.message : error),
    }));
  }
});
"""


def load_game_payload(game_dir: Path):
    guide = json.loads((game_dir / "guide.json").read_text(encoding="utf-8"))
    for route in guide.get("routes", []):
        route["steps"] = json.loads(
            (game_dir / f"route_{route['id']}.json").read_text(encoding="utf-8")
        )
    sidecar = json.loads((game_dir / "flowchart.json").read_text(encoding="utf-8"))
    return guide, sidecar


def run_runtime(guide: dict, sidecar: dict):
    result = subprocess.run(
        ["node", "-e", NODE_RUNNER, str(FLOWCHART)],
        input=json.dumps({"guide": guide, "sidecar": sidecar}, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


class FlowchartSidecarTests(unittest.TestCase):
    def test_all_sidecars_validate_with_runtime_renderer_contract(self):
        sidecars = sorted(ROOT.glob("*/flowchart.json"))
        self.assertTrue(sidecars, "Expected at least one flowchart sidecar fixture")

        for path in sidecars:
            with self.subTest(sidecar=path.parent.name):
                guide, sidecar = load_game_payload(path.parent)
                result = run_runtime(guide, sidecar)
                self.assertTrue(result["ok"], result.get("error"))

    def test_runtime_rejects_save_ref_that_would_not_render_as_branch(self):
        guide = {
            "routes": [
                {
                    "id": "route-a",
                    "title": "A",
                    "steps": [
                        {"simpleJp": "セーブ1"},
                        {"simpleJp": "進む"},
                    ],
                }
            ]
        }
        sidecar = {
            "version": 1,
            "addEdges": [
                {
                    "from": {"route": "route-a", "save": "1"},
                    "to": {"route": "route-a", "step": {"simpleJp": "進む"}},
                }
            ],
        }
        result = run_runtime(guide, sidecar)
        self.assertFalse(result["ok"])
        self.assertIn("Unresolved flowchart sidecar ref", result["error"])

    def test_runtime_rejects_semantically_invalid_sidecars(self):
        guide = {
            "routes": [
                {
                    "id": "a",
                    "title": "A",
                    "steps": [{"simpleJp": "A1"}, {"simpleJp": "A2"}],
                },
                {
                    "id": "b",
                    "title": "B",
                    "steps": [{"simpleJp": "B1"}],
                },
            ]
        }

        invalid_sidecars = [
            {
                "version": 1,
                "syntheticNodes": [
                    {
                        "id": "bad-offset",
                        "label": "x",
                        "near": {"route": "a", "step": {"simpleJp": "A1"}},
                        "laneOffset": "oops",
                    }
                ],
            },
            {
                "version": 1,
                "syntheticNodes": [
                    {
                        "id": "duplicate",
                        "label": "x",
                        "near": {"route": "a", "step": {"simpleJp": "A1"}},
                    }
                ],
                "groups": [
                    {
                        "id": "duplicate",
                        "members": [
                            {"route": "a", "step": {"simpleJp": "A1"}},
                            {"route": "a", "step": {"simpleJp": "A2"}},
                        ],
                    }
                ],
            },
            {
                "version": 1,
                "groups": [
                    {
                        "id": "cross-route",
                        "members": [
                            {"route": "a", "step": {"simpleJp": "A1"}},
                            {"route": "b", "step": {"simpleJp": "B1"}},
                        ],
                    }
                ],
            },
            {
                "version": 1,
                "addEdges": [
                    {
                        "from": {
                            "route": "a",
                            "step": {"simpleJp": "A1", "occurrence": 0},
                        },
                        "to": {"route": "a", "step": {"simpleJp": "A2"}},
                    }
                ],
            },
        ]

        for sidecar in invalid_sidecars:
            with self.subTest(sidecar=sidecar):
                result = run_runtime(guide, sidecar)
                self.assertFalse(result["ok"])

    def test_cross_route_synthetic_jump_keeps_route_and_step_paired(self):
        guide = {
            "routes": [
                {
                    "id": "a",
                    "title": "A",
                    "steps": [{"simpleJp": "A1"}],
                },
                {
                    "id": "b",
                    "title": "B",
                    "steps": [{"simpleJp": "B1"}, {"simpleJp": "B2"}],
                },
            ]
        }
        sidecar = {
            "version": 1,
            "syntheticNodes": [
                {
                    "id": "jump",
                    "label": "Jump",
                    "near": {"route": "a", "step": {"simpleJp": "A1"}},
                    "jumpTo": {"route": "b", "step": {"simpleJp": "B2"}},
                }
            ],
        }
        result = run_runtime(guide, sidecar)
        self.assertTrue(result["ok"], result.get("error"))
        node = next(node for node in result["nodes"] if node["id"] == "sidecar-jump")
        self.assertEqual(node["routeId"], "b")
        self.assertEqual(node["stepIndex"], 1)

    def test_himawari_sidecar_captures_non_flat_topology(self):
        guide, sidecar = load_game_payload(ROOT / "himawari")
        result = run_runtime(guide, sidecar)
        self.assertTrue(result["ok"], result.get("error"))

        nodes = {node["id"]: node for node in result["nodes"]}
        by_label = {}
        for node in result["nodes"]:
            by_label.setdefault(node["label"], []).append(node)

        self.assertIn("sidecar-aries-smoke-rain-asuka-house", nodes)
        self.assertEqual(
            nodes["sidecar-asuka-late-visits"]["items"],
            [
                "アリエスとアクアの様子を見てみる",
                "明香と明の所に行く",
                "部長とジョニーが心配だ",
            ],
        )

        edge_labels = {
            (
                nodes[edge["from"]]["label"],
                nodes[edge["to"]]["label"],
                edge.get("kind", "normal"),
            )
            for edge in result["edges"]
        }

        self.assertIn(("STORY", "2048-2050", "unlock"), edge_labels)
        self.assertIn(("クリア後", "Tips", "normal"), edge_labels)
        self.assertNotIn(("かげろう", "2048-2050", "normal"), edge_labels)
        self.assertNotIn(("2048-2050", "Tips", "normal"), edge_labels)


if __name__ == "__main__":
    unittest.main()
