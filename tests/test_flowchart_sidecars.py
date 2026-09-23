import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def route_steps(game_dir: Path, route_id: str):
    path = game_dir / f"route_{route_id}.json"
    if not path.exists():
        raise AssertionError(f"Missing route file for sidecar ref: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_ref(game_dir: Path, guide: dict, synthetic_ids: set[str], ref: dict):
    if not isinstance(ref, dict):
        raise AssertionError(f"Sidecar ref must be an object: {ref!r}")

    synthetic = ref.get("synthetic")
    if synthetic is not None:
        if synthetic not in synthetic_ids:
            raise AssertionError(f"Unknown synthetic sidecar node: {synthetic}")
        return

    route_id = ref.get("route")
    route_ids = {route["id"] for route in guide.get("routes", [])}
    if route_id not in route_ids:
        raise AssertionError(f"Unknown sidecar route: {route_id}")

    if ref.get("start") is True:
        return

    steps = route_steps(game_dir, route_id)

    if "save" in ref:
        expected = f"セーブ{ref['save']}"
        if not any(step.get("simpleJp") == expected for step in steps):
            raise AssertionError(f"Missing save anchor {expected!r} in {route_id}")
        return

    step_ref = ref.get("step")
    if isinstance(step_ref, dict) and step_ref.get("simpleJp"):
        label = step_ref["simpleJp"]
        occurrence = int(step_ref.get("occurrence", 1))
        matches = [step for step in steps if step.get("simpleJp") == label]
        if len(matches) < occurrence:
            raise AssertionError(
                f"Missing step anchor {label!r} occurrence {occurrence} in {route_id}"
            )
        return

    raise AssertionError(f"Unsupported sidecar ref: {ref!r}")


class FlowchartSidecarTests(unittest.TestCase):
    def test_all_sidecar_refs_resolve_against_current_routes(self):
        sidecars = sorted(ROOT.glob("*/flowchart.json"))
        self.assertTrue(sidecars, "Expected at least one flowchart sidecar fixture")

        for path in sidecars:
            with self.subTest(sidecar=path.parent.name):
                sidecar = json.loads(path.read_text(encoding="utf-8"))
                guide = json.loads((path.parent / "guide.json").read_text(encoding="utf-8"))
                self.assertEqual(sidecar.get("version"), 1)

                synthetic_nodes = sidecar.get("syntheticNodes", [])
                synthetic_ids = {node.get("id") for node in synthetic_nodes}
                self.assertNotIn(None, synthetic_ids)
                self.assertEqual(len(synthetic_ids), len(synthetic_nodes))

                for node in synthetic_nodes:
                    self.assertTrue(node.get("label"))
                    resolve_ref(path.parent, guide, synthetic_ids, node.get("near"))
                    if node.get("jumpTo") is not None:
                        resolve_ref(path.parent, guide, synthetic_ids, node["jumpTo"])

                for group in sidecar.get("groups", []):
                    members = group.get("members", [])
                    self.assertGreaterEqual(len(members), 2)
                    for ref in members:
                        resolve_ref(path.parent, guide, synthetic_ids, ref)

                for edge in (
                    sidecar.get("addEdges", [])
                    + sidecar.get("routeLinks", [])
                    + sidecar.get("removeEdges", [])
                ):
                    resolve_ref(path.parent, guide, synthetic_ids, edge.get("from"))
                    resolve_ref(path.parent, guide, synthetic_ids, edge.get("to"))

    def test_himawari_sidecar_captures_known_flattened_topology(self):
        sidecar = json.loads(
            (ROOT / "himawari" / "flowchart.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            "明香の家だ！",
            {node["label"] for node in sidecar["syntheticNodes"]},
        )

        groups = {group["id"]: group for group in sidecar["groups"]}
        self.assertEqual(
            len(groups["asuka-late-visits"]["members"]),
            3,
        )

        links = sidecar["routeLinks"]
        self.assertEqual(len(links), 4)
        self.assertEqual(
            [link["to"]["route"] for link in links],
            ["akari", "aqua", "asuka", "completion"],
        )


if __name__ == "__main__":
    unittest.main()
