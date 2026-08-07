import hashlib
import json
import csv
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

    def test_init_creates_v2_single_sources_of_truth(self) -> None:
        expected_headers = {
            "02_assets/reference-scope.csv": [
                "reference_id", "asset_id", "source_path_or_url", "rights_status",
                "inherit_identity", "inherit_state", "inherit_material", "inherit_space",
                "inherit_composition", "inherit_camera", "inherit_lighting", "inherit_color",
                "exclude", "approval_status", "notes",
            ],
            "02_assets/asset-state-matrix.csv": [
                "asset_version_id", "asset_id", "version", "state_name", "identity_invariants",
                "state_variables", "costume_or_surface", "damage_or_weathering", "carried_props",
                "reference_ids", "approval_status", "notes",
            ],
            "03_scenes/spatial-map.csv": [
                "scene_id", "zone_id", "zone_name", "screen_relation", "depth_layer",
                "entry_exit", "anchor_objects", "allowed_assets", "lighting_source",
                "continuity_notes",
            ],
            "04_shots/beat-sheet.csv": [
                "shot_id", "beat_order", "start_seconds", "end_seconds", "actor_or_source",
                "trigger", "action", "contact_target", "reaction", "end_state", "dialogue_id",
                "audio_cue_id",
            ],
            "04_shots/audio-cues.csv": [
                "audio_cue_id", "shot_id", "start_seconds", "end_seconds", "category", "source",
                "content_or_effect", "spatial_position", "mix_priority", "continuity_key", "notes",
            ],
            "05_prompts/prompt-index.csv": [
                "prompt_id", "shot_id", "version", "status", "richness", "master_prompt_path",
                "adapter_path", "parent_version", "change_reason", "changed_variables",
                "prompt_sha256", "approved_by", "notes",
            ],
            "06_generations/iteration-log.csv": [
                "iteration_id", "shot_id", "prompt_id", "batch_id", "observed_failure_codes",
                "responsibility_layer", "changed_variables", "hypothesis", "expected_improvement",
                "result_generation_ids", "decision", "next_action",
            ],
            "07_review/waivers.csv": [
                "waiver_id", "shot_id", "gate_code", "issue", "rationale", "impact",
                "approved_by", "approved_at", "expires_or_scope", "notes",
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            project = self.init_project(Path(temporary))
            self.assertIn("schema_version: 2", (project / "00_brief" / "project.yaml").read_text())
            for relative, expected in expected_headers.items():
                path = project / relative
                self.assertTrue(path.is_file(), relative)
                with path.open(newline="", encoding="utf-8") as handle:
                    self.assertEqual(next(csv.reader(handle)), expected, relative)

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
