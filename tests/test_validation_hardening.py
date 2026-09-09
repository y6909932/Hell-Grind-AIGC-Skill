import csv
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
AUDIT_SCRIPT = SKILL_ROOT / "scripts" / "audit_prompt.py"


def run_script(script: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def write_csv_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        headers = next(csv.reader(handle))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


class ValidationHardeningTests(unittest.TestCase):
    def init_project(self, root: Path) -> Path:
        project = root / "demo"
        result = run_script(
            INIT_SCRIPT,
            "--name", "Hardening Demo",
            "--output", str(project),
            "--project-id", "PRJ-HARDEN-001",
            "--aspect-ratio", "16:9",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return project

    def test_prompt_index_checks_master_prompt_file_and_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.init_project(Path(temporary))
            prompt_path = project / "05_prompts" / "SC001-SH001-P001.md"
            prompt_path.write_text("画面中一名维修员。", encoding="utf-8")
            wrong_hash = "0" * 64
            write_csv_rows(project / "05_prompts/prompt-index.csv", [
                {
                    "prompt_id": "SC001-SH001-P001",
                    "shot_id": "SC001-SH001",
                    "version": "v001",
                    "status": "draft",
                    "master_prompt_path": "05_prompts/SC001-SH001-P001.md",
                    "prompt_sha256": wrong_hash,
                },
                {
                    "prompt_id": "SC001-SH002-P001",
                    "shot_id": "SC001-SH002",
                    "version": "v001",
                    "status": "draft",
                    "master_prompt_path": "05_prompts/missing.md",
                    "prompt_sha256": hashlib.sha256(b"missing").hexdigest(),
                },
            ])
            result = run_script(VALIDATE_SCRIPT, str(project), "--strict-v2", "--json")
            payload = json.loads(result.stdout)
            codes = {entry["code"] for entry in payload["issues"]}
            self.assertIn("PROMPT_HASH_MISMATCH", codes)
            self.assertIn("MISSING_PROMPT_FILE", codes)

    def test_beat_sheet_checks_audio_and_asset_version_references(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.init_project(Path(temporary))
            write_csv_rows(project / "04_shots/beat-sheet.csv", [{
                "shot_id": "SC001-SH001",
                "beat_order": "1",
                "start_seconds": "0",
                "end_seconds": "1",
                "actor_or_source": "AST-CHAR-MISSING@v001",
                "contact_target": "AST-PROP-MISSING@v001",
                "audio_cue_id": "AUD-MISSING",
            }])
            result = run_script(VALIDATE_SCRIPT, str(project), "--strict-v2", "--json")
            messages = "\n".join(entry["message"] for entry in json.loads(result.stdout)["issues"])
            self.assertIn("actor_or_source", messages)
            self.assertIn("contact_target", messages)
            self.assertIn("audio_cue_id", messages)

    def test_consecutive_shots_warn_on_continuity_handoff_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.init_project(Path(temporary))
            write_csv_rows(project / "04_shots/shots.csv", [
                {
                    "shot_id": "SC001-SH001",
                    "scene_id": "SC001",
                    "shot_order": "1",
                    "duration_seconds": "5",
                    "status": "planned",
                    "continuity_out": "右手握钥匙;卷帘门半开",
                },
                {
                    "shot_id": "SC001-SH002",
                    "scene_id": "SC001",
                    "shot_order": "2",
                    "duration_seconds": "5",
                    "status": "planned",
                    "continuity_in": "左手握钥匙;卷帘门关闭",
                },
            ])
            result = run_script(VALIDATE_SCRIPT, str(project), "--strict-v2", "--json")
            issues = json.loads(result.stdout)["issues"]
            matches = [entry for entry in issues if entry["code"] == "CONTINUITY_HANDOFF_MISMATCH"]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["severity"], "warning")

    def test_generic_reference_word_does_not_trigger_reference_scope_warning(self) -> None:
        prompt = (
            "总时长 5 秒。画面中恰好一名女维修员。"
            "摄影机从眼平中景缓慢推进，最终停在她的脸部近景。"
            "只有环境音，无对白、无配乐、无字幕。"
            "平台适配层：实际接入提供方时，只在适配层补充模型名和参考槽，不覆盖硬约束。"
        )
        result = run_script(AUDIT_SCRIPT, "-", "--medium", "video", "--json", input_text=prompt)
        payload = json.loads(result.stdout)
        codes = {entry["code"] for entry in payload["issues"]}
        self.assertNotIn("P-REFERENCE-SCOPE", codes)


if __name__ == "__main__":
    unittest.main()
