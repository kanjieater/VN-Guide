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
    const progress = payload.progressNodeId
      ? window.VNFlowchart.nodeProgressState(
          graph.nodes.find(node => node.id === payload.progressNodeId),
          payload.progressState || {}
        )
      : null;
    const derivedCurrent = payload.progressMap
      ? window.VNFlowchart.deriveCurrentProgress(
          payload.guide.routes || [],
          payload.progressMap
        )
      : null;
    process.stdout.write(JSON.stringify({
      ok: true,
      nodes: graph.nodes,
      edges: graph.edges,
      maxDepth: graph.maxDepth,
      maxRow: graph.maxRow,
      progress,
      derivedCurrent,
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


def run_runtime(
    guide: dict,
    sidecar: dict,
    progress_node_id: str | None = None,
    progress_state: dict | None = None,
    progress_map: dict | None = None,
):
    payload = {"guide": guide, "sidecar": sidecar}
    if progress_node_id is not None:
        payload["progressNodeId"] = progress_node_id
        payload["progressState"] = progress_state or {}
    if progress_map is not None:
        payload["progressMap"] = progress_map

    result = subprocess.run(
        ["node", "-e", NODE_RUNNER, str(FLOWCHART)],
        input=json.dumps(payload, ensure_ascii=False),
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

    def test_synthetic_node_progress_is_neutral_without_explicit_visit_identity(self):
        guide = {
            "routes": [
                {
                    "id": "a",
                    "title": "A",
                    "steps": [
                        {"simpleJp": "A1"},
                        {"simpleJp": "A2"},
                        {"simpleJp": "A3"},
                    ],
                }
            ]
        }
        sidecar = {
            "version": 1,
            "syntheticNodes": [
                {
                    "id": "alt",
                    "label": "Alternate",
                    "near": {"route": "a", "step": {"simpleJp": "A1"}},
                    "jumpTo": {"route": "a", "step": {"simpleJp": "A2"}},
                }
            ],
        }
        result = run_runtime(
            guide,
            sidecar,
            "sidecar-alt",
            {"seen": {"a": 2}, "current": {"a": 1}},
        )
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual(
            result["progress"],
            {"seen": False, "current": False, "known": False},
        )

    def test_non_navigable_synthetic_annotation_has_no_walkthrough_target(self):
        guide = {
            "routes": [
                {
                    "id": "a",
                    "title": "A",
                    "steps": [{"simpleJp": "A1"}],
                }
            ]
        }
        sidecar = {
            "version": 1,
            "syntheticNodes": [
                {
                    "id": "note",
                    "label": "Annotation",
                    "near": {"route": "a", "step": {"simpleJp": "A1"}},
                    "navigable": False,
                }
            ],
        }
        result = run_runtime(guide, sidecar)
        self.assertTrue(result["ok"], result.get("error"))
        node = next(node for node in result["nodes"] if node["id"] == "sidecar-note")
        self.assertIsNone(node["stepIndex"])

    def test_runtime_rejects_non_contiguous_group_members(self):
        guide = {
            "routes": [
                {
                    "id": "a",
                    "title": "A",
                    "steps": [
                        {"simpleJp": "A"},
                        {"simpleJp": "M1"},
                        {"simpleJp": "X"},
                        {"simpleJp": "M2"},
                        {"simpleJp": "Y"},
                        {"simpleJp": "M3"},
                        {"simpleJp": "Z"},
                    ],
                }
            ]
        }
        sidecar = {
            "version": 1,
            "groups": [
                {
                    "id": "bad-group",
                    "members": [
                        {"route": "a", "step": {"simpleJp": "M1"}},
                        {"route": "a", "step": {"simpleJp": "M2"}},
                        {"route": "a", "step": {"simpleJp": "M3"}},
                    ],
                }
            ],
        }
        result = run_runtime(guide, sidecar)
        self.assertFalse(result["ok"])
        self.assertIn("contiguous", result["error"])

    def test_completed_route_moves_current_marker_to_next_route_start(self):
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
                    "steps": [{"simpleJp": "B1"}, {"simpleJp": "B2"}],
                },
            ]
        }
        result = run_runtime(guide, {"version": 1}, progress_map={"a": 1})
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual(result["derivedCurrent"], {"b": -1})

        start = run_runtime(
            guide,
            {"version": 1},
            progress_node_id="b-0",
            progress_state={"current": {"b": -1}},
        )
        self.assertEqual(
            start["progress"],
            {"seen": False, "current": True, "known": True},
        )

    def test_all_routes_complete_leaves_no_current_marker(self):
        guide = {
            "routes": [
                {
                    "id": "a",
                    "title": "A",
                    "steps": [{"simpleJp": "A1"}, {"simpleJp": "A2"}],
                }
            ]
        }
        result = run_runtime(guide, {"version": 1}, progress_map={"a": 1})
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual(result["derivedCurrent"], {})

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
        self.assertIn(("【アリエス】END", "Tips追加（1周目クリア）", "unlock"), edge_labels)
        self.assertIn(("【星乃 明香里】END", "Tips更新（2周目クリア）", "unlock"), edge_labels)
        self.assertIn(("【アクア】END", "Tips更新（3周目クリア）", "unlock"), edge_labels)
        self.assertIn(("【西園寺明香】END", "Tips更新（4周目クリア）", "unlock"), edge_labels)
        self.assertIn(("クリア後", "Tips", "normal"), edge_labels)
        self.assertNotIn(("【アリエス】END", "Tips", "unlock"), edge_labels)
        self.assertNotIn(("【星乃 明香里】END", "Tips", "unlock"), edge_labels)
        self.assertNotIn(("【アクア】END", "Tips", "unlock"), edge_labels)
        self.assertNotIn(("【西園寺明香】END", "Tips", "unlock"), edge_labels)
        self.assertNotIn(("かげろう", "2048-2050", "normal"), edge_labels)
        self.assertNotIn(("2048-2050", "Tips", "normal"), edge_labels)

        for node_id in (
            "sidecar-tips-after-aries",
            "sidecar-tips-after-akari",
            "sidecar-tips-after-aqua",
            "sidecar-tips-after-asuka",
        ):
            self.assertIsNone(nodes[node_id]["stepIndex"])


if __name__ == "__main__":
    unittest.main()
