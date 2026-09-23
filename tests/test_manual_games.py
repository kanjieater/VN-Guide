import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


guide_gen = load_module("vn_guide_gen_manual_games", ROOT / "scripts" / "guide_gen.py")
generate = load_module("vn_generate_manual_games", ROOT / "scripts" / "generate.py")


class ManualGameIsolationTests(unittest.TestCase):
    def test_guide_gen_ignores_namespaced_non_vn_game(self):
        with tempfile.TemporaryDirectory() as td:
            games_json = Path(td) / "games.json"
            games_json.write_text(
                json.dumps(
                    {
                        "game:manual-test": {
                            "slug": "manual-test",
                            "title": "Manual Test Game",
                            "has_guide": False,
                            "guide_target": {
                                "label": "Manual Test Game",
                                "platform": "Test Platform",
                                "url": "https://example.com/manual-test",
                            },
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
                patch.object(guide_gen, "generate_guide") as generate_guide,
            ):
                guide_gen.run()

            generate_guide.assert_not_called()

    def test_generate_does_not_query_vndb_for_manual_game_cover(self):
        with tempfile.TemporaryDirectory() as td:
            games_json = Path(td) / "games.json"
            games_json.write_text(
                json.dumps(
                    {
                        "game:manual-test": {
                            "slug": "manual-test",
                            "title": "Manual Test Game",
                            "alttitle": "手動テストゲーム",
                            "cover_url": "",
                            "has_guide": False,
                        }
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(generate, "GAMES_JSON", games_json),
                patch.object(generate.pull_vndb, "fetch_playing_list", return_value=[]),
                patch.object(generate.pull_vndb, "lookup_vn_by_id") as lookup,
                patch.object(generate, "scaffold_guide"),
                patch.object(generate, "generate_landing"),
            ):
                generate.run()

            lookup.assert_not_called()


class SharedGuideShellTests(unittest.TestCase):
    def test_committed_guide_shells_all_match_shared_template(self):
        template = (ROOT / "scripts" / "templates" / "guide_stub.html").read_text(
            encoding="utf-8"
        )
        guide_dirs = sorted(
            path for path in ROOT.iterdir()
            if path.is_dir() and (path / "guide.json").exists()
        )
        self.assertTrue(guide_dirs)
        for guide_dir in guide_dirs:
            with self.subTest(guide=guide_dir.name):
                self.assertEqual(
                    (guide_dir / "index.html").read_text(encoding="utf-8"),
                    template,
                )

    def test_shared_template_fixes_metadata_order(self):
        template = (ROOT / "scripts" / "templates" / "guide_stub.html").read_text(
            encoding="utf-8"
        )
        updated = template.index('id="guide-updated"')
        target = template.index('id="guide-target"')
        self.assertLess(updated, target)
        self.assertIn('class="guide-meta"', template)

    def test_scaffold_uses_exact_shared_html_shell(self):
        with tempfile.TemporaryDirectory() as td:
            repo_path = Path(td)
            template = repo_path / "guide_stub.html"
            template.write_text(
                '<link rel="stylesheet" href="../style.css">\n'
                '<script src="../guide-app.js"></script>\n',
                encoding="utf-8",
            )

            with (
                patch.object(generate, "REPO_PATH", repo_path),
                patch.object(generate, "STUB_TMPL", template),
            ):
                generate.scaffold_guide("sample-game", "Sample Game", "game:sample")

            generated = (repo_path / "sample-game" / "index.html").read_text(
                encoding="utf-8"
            )
            self.assertEqual(generated, template.read_text(encoding="utf-8"))
            self.assertNotIn("guide-app.js?v=", generated)
            self.assertNotIn("style.css?v=", generated)


if __name__ == "__main__":
    unittest.main()
