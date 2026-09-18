import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "guide_gen.py"
SPEC = importlib.util.spec_from_file_location("vn_guide_gen", MODULE_PATH)
guide_gen = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(guide_gen)


class SaveOffsetTests(unittest.TestCase):
    def test_count_saves_excludes_bad_end_and_plain_loads(self):
        with tempfile.TemporaryDirectory() as td:
            route_file = Path(td) / "route.json"
            steps = []
            for slot in range(53, 61):
                steps.append({"simpleJp": f"セーブ{slot}"})
                steps.append(
                    {
                        "simpleJp": f"セーブ{slot}にロード",
                        "isLoad": True,
                    }
                )

            # Ordinary cross-route loads intentionally have no isLoad marker;
            # they must not count as new save slots either.
            steps.append({"simpleJp": "セーブ12にロード"})

            route_file.write_text(
                json.dumps(steps, ensure_ascii=False),
                encoding="utf-8",
            )

            self.assertEqual(guide_gen.count_saves_in_route(route_file), 8)

    def test_compute_save_offset_uses_actual_saves_only(self):
        with tempfile.TemporaryDirectory() as td:
            guide_dir = Path(td)
            (guide_dir / "route_a.json").write_text(
                json.dumps(
                    [
                        {"simpleJp": "セーブ1"},
                        {"simpleJp": "セーブ1にロード", "isLoad": True},
                        {"simpleJp": "セーブ2"},
                        {"simpleJp": "セーブ2にロード", "isLoad": True},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (guide_dir / "route_b.json").write_text(
                json.dumps(
                    [
                        {"simpleJp": "セーブ3"},
                        {"simpleJp": "セーブ3にロード", "isLoad": True},
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            routes = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
            self.assertEqual(
                guide_gen.compute_save_offset(routes, 2, guide_dir),
                3,
            )


if __name__ == "__main__":
    unittest.main()
