import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "guide_gen.py"
SPEC = importlib.util.spec_from_file_location("vn_guide_gen", MODULE_PATH)
guide_gen = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(guide_gen)


class GuideTargetTests(unittest.TestCase):
    def test_repo_guide_target_is_authoritative(self):
        target = {
            "label": "薄桜鬼 真改 風華伝",
            "platform": "Nintendo Switch",
            "url": "https://vndb.org/r56825",
        }
        with patch.dict(
            guide_gen.os.environ,
            {
                "GUIDE_TARGET_LABEL": "Other",
                "GUIDE_PLATFORM": "PC",
                "GUIDE_TARGET_URL": "https://example.com/other",
            },
            clear=False,
        ):
            self.assertEqual(
                guide_gen.resolve_guide_target(
                    {"guide_target": target},
                    "v1715",
                ),
                target,
            )

    def test_complete_caller_target_is_accepted(self):
        with patch.dict(
            guide_gen.os.environ,
            {
                "GUIDE_TARGET_VID": "v123",
                "GUIDE_TARGET_LABEL": "Edition",
                "GUIDE_PLATFORM": "Nintendo Switch",
                "GUIDE_TARGET_URL": "https://vndb.org/r123",
            },
            clear=False,
        ):
            self.assertEqual(
                guide_gen.resolve_guide_target({}, "v123"),
                {
                    "label": "Edition",
                    "platform": "Nintendo Switch",
                    "url": "https://vndb.org/r123",
                },
            )

    def test_missing_or_incomplete_target_is_rejected(self):
        keys = [
            "GUIDE_TARGET_VID",
            "GUIDE_TARGET_LABEL",
            "GUIDE_PLATFORM",
            "GUIDE_TARGET_URL",
        ]
        with patch.dict(guide_gen.os.environ, {}, clear=True):
            self.assertIsNone(guide_gen.resolve_guide_target({}, "v123"))

        with patch.dict(
            guide_gen.os.environ,
            {
                "GUIDE_TARGET_LABEL": "Edition",
                "GUIDE_PLATFORM": "Nintendo Switch",
            },
            clear=False,
        ):
            guide_gen.os.environ.pop("GUIDE_TARGET_URL", None)
            self.assertIsNone(guide_gen.resolve_guide_target({}, "v123"))

    def test_caller_target_is_scoped_to_one_pending_vn(self):
        with patch.dict(
            guide_gen.os.environ,
            {
                "GUIDE_TARGET_VID": "v1",
                "GUIDE_TARGET_LABEL": "Edition One",
                "GUIDE_PLATFORM": "Nintendo Switch",
                "GUIDE_TARGET_URL": "https://vndb.org/r1",
            },
            clear=True,
        ):
            first = guide_gen.resolve_guide_target({}, "v1")
            second = guide_gen.resolve_guide_target({}, "v2")

        self.assertEqual(
            first,
            {
                "label": "Edition One",
                "platform": "Nintendo Switch",
                "url": "https://vndb.org/r1",
            },
        )
        self.assertIsNone(second)

    def test_fresh_research_rejects_missing_or_mismatched_target(self):
        required = {
            "label": "Edition",
            "platform": "Nintendo Switch",
            "url": "https://vndb.org/r123",
        }

        bad_targets = [
            None,
            {
                "label": "Other Edition",
                "platform": "Nintendo Switch",
                "url": "https://vndb.org/r999",
            },
        ]

        for written_target in bad_targets:
            with self.subTest(written_target=written_target):
                with tempfile.TemporaryDirectory() as td:
                    guide_dir = Path(td)

                    def write_research(*args, **kwargs):
                        data = {
                            "title": "Game",
                            "vndb_id": "v123",
                            "routes": [{"id": "route", "title": "Route"}],
                        }
                        if written_target is not None:
                            data["guide_target"] = written_target
                        (guide_dir / "research.json").write_text(
                            json.dumps(data, ensure_ascii=False),
                            encoding="utf-8",
                        )
                        return True

                    with (
                        patch.object(guide_gen, "build_prompt", return_value="prompt"),
                        patch.object(
                            guide_gen,
                            "run_claude",
                            side_effect=write_research,
                        ),
                    ):
                        self.assertFalse(
                            guide_gen.phase_research(
                                "game",
                                "Game",
                                "v123",
                                guide_dir,
                                required,
                            )
                        )

    def test_fresh_research_accepts_exact_target(self):
        required = {
            "label": "Edition",
            "platform": "Nintendo Switch",
            "url": "https://vndb.org/r123",
        }
        with tempfile.TemporaryDirectory() as td:
            guide_dir = Path(td)

            def write_research(*args, **kwargs):
                (guide_dir / "research.json").write_text(
                    json.dumps(
                        {
                            "title": "Game",
                            "vndb_id": "v123",
                            "guide_target": required,
                            "routes": [{"id": "route", "title": "Route"}],
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return True

            with (
                patch.object(guide_gen, "build_prompt", return_value="prompt"),
                patch.object(
                    guide_gen,
                    "run_claude",
                    side_effect=write_research,
                ),
            ):
                self.assertTrue(
                    guide_gen.phase_research(
                        "game",
                        "Game",
                        "v123",
                        guide_dir,
                        required,
                    )
                )


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
