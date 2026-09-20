import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "review.py"
SPEC = importlib.util.spec_from_file_location("vn_guide_review", MODULE_PATH)
review = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(review)


class StructuralSignatureTests(unittest.TestCase):
    def test_source_only_changes_do_not_change_signature(self):
        with tempfile.TemporaryDirectory() as td:
            route_file = Path(td) / "route.json"
            base = [
                {
                    "simpleJp": "戦う",
                    "jpGuide1": "・戦う",
                    "jpGuide2": "戦う",
                    "enGuide": "",
                },
                {
                    "simpleJp": "セーブ1にロード",
                    "jpGuide1": "LOAD",
                    "jpGuide2": "LOAD",
                    "enGuide": "",
                    "isLoad": True,
                },
            ]
            route_file.write_text(json.dumps(base, ensure_ascii=False))
            original = review.structural_signature(route_file)

            source_only = json.loads(json.dumps(base))
            source_only[0]["jpGuide1"] = "・戦う（注記）"
            source_only[0]["jpGuide2"] = "別表記"
            source_only[0]["enGuide"] = "Fight"
            route_file.write_text(json.dumps(source_only, ensure_ascii=False))
            self.assertEqual(original, review.structural_signature(route_file))

    def test_structural_fields_change_signature(self):
        with tempfile.TemporaryDirectory() as td:
            route_file = Path(td) / "route.json"
            base = [{"simpleJp": "進む", "jpGuide1": "進む", "jpGuide2": "進む", "enGuide": ""}]
            route_file.write_text(json.dumps(base, ensure_ascii=False))
            original = review.structural_signature(route_file)

            simplejp = json.loads(json.dumps(base))
            simplejp[0]["simpleJp"] = "戻る"
            route_file.write_text(json.dumps(simplejp, ensure_ascii=False))
            self.assertNotEqual(original, review.structural_signature(route_file))

            bad_end = json.loads(json.dumps(base))
            bad_end[0]["badEndPath"] = "BAD END"
            route_file.write_text(json.dumps(bad_end, ensure_ascii=False))
            self.assertNotEqual(original, review.structural_signature(route_file))

            load = json.loads(json.dumps(base))
            load[0]["isLoad"] = True
            route_file.write_text(json.dumps(load, ensure_ascii=False))
            self.assertNotEqual(original, review.structural_signature(route_file))



class ReviewGateTests(unittest.TestCase):
    def _repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        slug = "game"
        game_dir = root / slug
        game_dir.mkdir()
        (game_dir / "guide.json").write_text(
            json.dumps(
                {
                    "routes": [
                        {"id": "route", "title": "Route", "reviewed": False}
                    ]
                }
            )
        )
        (game_dir / "route_route.json").write_text("[]")
        return temp, root, slug

    def test_no_structural_change_runs_each_gate_once(self):
        temp, root, slug = self._repo()
        self.addCleanup(temp.cleanup)

        with (
            patch.object(review, "REPO_PATH", root),
            patch.object(review, "structural_review_route", return_value=True) as structural,
            patch.object(review, "review_route", return_value=True) as accuracy,
            patch.object(
                review,
                "structural_signature",
                side_effect=[("same",), ("same",)],
            ),
            patch.object(review, "mark_route_reviewed", return_value=True) as mark,
            patch.object(review, "approval_only", return_value=True),
            patch.object(review, "run_deploy") as deploy,
        ):
            review.review_game(slug)

        self.assertEqual(structural.call_count, 1)
        self.assertEqual(accuracy.call_count, 1)
        mark.assert_called_once()
        deploy.assert_called_once()

    def test_structural_accuracy_fix_reruns_structural_and_accuracy(self):
        temp, root, slug = self._repo()
        self.addCleanup(temp.cleanup)

        with (
            patch.object(review, "REPO_PATH", root),
            patch.object(review, "structural_review_route", return_value=True) as structural,
            patch.object(review, "review_route", return_value=True) as accuracy,
            patch.object(
                review,
                "structural_signature",
                side_effect=[
                    ("before",),
                    ("after",),
                    ("after",),
                    ("after",),
                ],
            ),
            patch.object(review, "mark_route_reviewed", return_value=True) as mark,
            patch.object(review, "approval_only", return_value=True),
            patch.object(review, "run_deploy") as deploy,
        ):
            review.review_game(slug)

        self.assertEqual(structural.call_count, 2)
        self.assertEqual(accuracy.call_count, 2)
        mark.assert_called_once()
        deploy.assert_called_once()

    def test_open_structural_issue_blocks_reviewed_true(self):
        temp, root, slug = self._repo()
        self.addCleanup(temp.cleanup)
        guide_file = root / slug / "guide.json"

        with (
            patch.object(review, "REPO_PATH", root),
            patch.object(review, "get_open_issue_for_route", return_value=None),
            patch.object(review, "get_open_structural_issue_for_route", return_value=77),
        ):
            passed = review.mark_route_reviewed(
                guide_file, slug, "route", "Route"
            )

        self.assertFalse(passed)
        data = json.loads(guide_file.read_text())
        self.assertFalse(data["routes"][0]["reviewed"])


if __name__ == "__main__":
    unittest.main()
