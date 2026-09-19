import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


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

    def test_missing_target_defaults_to_newest_japanese_release(self):
        target = {
            "label": "Newest Japanese",
            "platform": "Windows",
            "url": "https://vndb.org/r123",
        }
        with (
            patch.dict(guide_gen.os.environ, {}, clear=True),
            patch.object(
                guide_gen,
                "fetch_newest_japanese_guide_target",
                return_value=target,
            ) as fetch_default,
        ):
            self.assertEqual(guide_gen.resolve_guide_target({}, "v123"), target)
        fetch_default.assert_called_once_with("v123")

    def test_incomplete_caller_target_is_rejected(self):
        with patch.dict(
            guide_gen.os.environ,
            {
                "GUIDE_TARGET_VID": "v123",
                "GUIDE_TARGET_LABEL": "Edition",
                "GUIDE_PLATFORM": "Nintendo Switch",
            },
            clear=True,
        ):
            guide_gen.os.environ.pop("GUIDE_TARGET_URL", None)
            self.assertIsNone(guide_gen.resolve_guide_target({}, "v123"))

    def test_default_target_skips_newer_non_japanese_release(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps(
            {
                "results": [
                    {
                        "id": "r200",
                        "title": "Newer localization",
                        "alttitle": None,
                        "released": "2020-05-20",
                        "platforms": ["win"],
                        "languages": [{"lang": "en", "mtl": False}],
                        "official": True,
                        "patch": False,
                        "vns": [{"id": "v123", "rtype": "complete"}],
                    },
                    {
                        "id": "r123",
                        "title": "Japanese release",
                        "alttitle": "日本語版",
                        "released": "2016-02-12",
                        "platforms": ["win"],
                        "languages": [{"lang": "ja", "mtl": False}],
                        "official": True,
                        "patch": False,
                        "vns": [{"id": "v123", "rtype": "complete"}],
                    },
                ]
            }
        ).encode("utf-8")
        with patch.object(guide_gen.urllib_request, "urlopen", return_value=response):
            self.assertEqual(
                guide_gen.fetch_newest_japanese_guide_target("v123"),
                {
                    "label": "日本語版 (2016-02-12 Windows)",
                    "platform": "Windows",
                    "url": "https://vndb.org/r123",
                },
            )

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


class TargetInvalidationTests(unittest.TestCase):
    def test_real_target_change_invalidates_stale_routes_and_review_state(self):
        target_a = {
            "label": "Edition A",
            "platform": "PC",
            "url": "https://vndb.org/r100",
        }
        target_b = {
            "label": "Edition B",
            "platform": "Nintendo Switch",
            "url": "https://vndb.org/r200",
        }

        with tempfile.TemporaryDirectory() as td:
            guide_dir = Path(td)
            (guide_dir / "research.json").write_text(
                json.dumps(
                    {
                        "guide_target": target_a,
                        "routes": [{"id": "route", "title": "Route"}],
                    }
                ),
                encoding="utf-8",
            )
            (guide_dir / "guide.json").write_text(
                json.dumps(
                    {
                        "guide_target": target_a,
                        "routes": [{"id": "route", "reviewed": True}],
                    }
                ),
                encoding="utf-8",
            )
            (guide_dir / "route_route.json").write_text(
                json.dumps([{"simpleJp": "Old target step"}]),
                encoding="utf-8",
            )
            (guide_dir / "route_route_session.txt").write_text("session")
            (guide_dir / "research_session.txt").write_text("session")

            self.assertTrue(
                guide_gen.invalidate_for_target_change(guide_dir, target_b)
            )
            self.assertFalse((guide_dir / "research.json").exists())
            self.assertFalse((guide_dir / "guide.json").exists())
            self.assertFalse((guide_dir / "route_route.json").exists())
            self.assertFalse((guide_dir / "route_route_session.txt").exists())
            self.assertFalse((guide_dir / "research_session.txt").exists())

    def test_same_explicit_target_preserves_existing_generated_state(self):
        target = {
            "label": "Edition A",
            "platform": "PC",
            "url": "https://vndb.org/r100",
        }

        with tempfile.TemporaryDirectory() as td:
            guide_dir = Path(td)
            (guide_dir / "research.json").write_text(
                json.dumps({"guide_target": target, "routes": [{"id": "route"}]}),
                encoding="utf-8",
            )
            (guide_dir / "guide.json").write_text(
                json.dumps(
                    {
                        "guide_target": target,
                        "routes": [{"id": "route", "reviewed": True}],
                    }
                ),
                encoding="utf-8",
            )
            route_file = guide_dir / "route_route.json"
            route_file.write_text(
                json.dumps([{"simpleJp": "Existing step"}]),
                encoding="utf-8",
            )

            self.assertFalse(
                guide_gen.invalidate_for_target_change(guide_dir, target)
            )
            self.assertTrue((guide_dir / "research.json").exists())
            self.assertTrue((guide_dir / "guide.json").exists())
            self.assertTrue(route_file.exists())


class TargetPersistenceTests(unittest.TestCase):
    def test_caller_target_must_publish_before_research(self):
        with tempfile.TemporaryDirectory() as td:
            games_json = Path(td) / "games.json"
            games_json.write_text(
                json.dumps(
                    {
                        "v123": {
                            "slug": "game",
                            "title": "Game",
                            "has_guide": False,
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(guide_gen, "GAMES_JSON", games_json),
                patch.object(
                    guide_gen.agent_runner,
                    "credentials_available",
                    return_value=True,
                ),
                patch.object(guide_gen, "run_deploy", return_value=False) as deploy,
                patch.object(guide_gen, "generate_guide") as generate,
                patch.dict(
                    guide_gen.os.environ,
                    {
                        "GUIDE_TARGET_VID": "v123",
                        "GUIDE_TARGET_LABEL": "Edition",
                        "GUIDE_PLATFORM": "Nintendo Switch",
                        "GUIDE_TARGET_URL": "https://vndb.org/r123",
                    },
                    clear=True,
                ),
            ):
                guide_gen.run()

            persisted = json.loads(games_json.read_text(encoding="utf-8"))
            self.assertEqual(
                persisted["v123"]["guide_target"],
                {
                    "label": "Edition",
                    "platform": "Nintendo Switch",
                    "url": "https://vndb.org/r123",
                },
            )
            deploy.assert_called_once_with()
            generate.assert_not_called()


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
