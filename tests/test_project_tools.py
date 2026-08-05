import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skill" / "hell-grind-aigc-skill"
INIT_SCRIPT = SKILL_ROOT / "scripts" / "init_project.py"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_project.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


class ProjectToolsTests(unittest.TestCase):
    def init_project(self, root: Path) -> Path:
        project = root / "demo-project"
        result = run_script(
            INIT_SCRIPT,
            "--name",
            "Demo Film",
            "--output",
            str(project),
            "--project-id",
            "PRJ-DEMO-001",
            "--aspect-ratio",
            "16:9",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return project

    def test_init_creates_full_project_that_passes_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.init_project(Path(temporary))
            expected_stages = [f"{index:02d}_{name}" for index, name in enumerate([
                "brief", "story", "assets", "scenes", "shots", "prompts",
                "generations", "review", "edit", "delivery",
            ])]
            self.assertEqual([item.name for item in sorted(project.iterdir()) if item.is_dir()], expected_stages)
            config = (project / "00_brief" / "project.yaml").read_text()
            self.assertIn("project_id: PRJ-DEMO-001", config)
            self.assertIn('project_name: "Demo Film"', config)
            self.assertIn('aspect_ratio: "16:9"', config)

            validation = run_script(VALIDATE_SCRIPT, str(project), "--json")
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            payload = json.loads(validation.stdout)
            self.assertTrue(payload["valid"])
            self.assertEqual(payload["issues"], [])
            self.assertEqual(payload["network_requests"], 0)
            self.assertEqual(payload["database_operations"], 0)

    def test_init_refuses_to_overwrite_non_empty_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "existing"
            project.mkdir()
            marker = project / "keep.txt"
            marker.write_text("user data")
            result = run_script(INIT_SCRIPT, "--name", "Blocked", "--output", str(project))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), "user data")

    def test_validator_reports_bad_header_duplicate_id_and_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.init_project(Path(temporary))
            (project / "02_assets" / "assets.csv").write_text("wrong_header\n")
            (project / "04_shots" / "shots.csv").write_text(
                "shot_id,scene_id,shot_order,duration_seconds,status,prompt_version,selected_generation_id,notes\n"
                "SC001-SH001,SC999,1,5,planned,v001,,first\n"
                "SC001-SH001,SC999,2,5,planned,v001,,duplicate\n"
            )
            validation = run_script(VALIDATE_SCRIPT, str(project), "--json")
            self.assertEqual(validation.returncode, 1)
            codes = {issue["code"] for issue in json.loads(validation.stdout)["issues"]}
            self.assertTrue({"MISSING_COLUMN", "DUPLICATE_ID", "MISSING_REFERENCE"}.issubset(codes))

    def test_validator_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.init_project(Path(temporary))
            before = tree_digest(project)
            result = run_script(VALIDATE_SCRIPT, str(project), "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(tree_digest(project), before)


if __name__ == "__main__":
    unittest.main()
