import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = REPO_ROOT / "skill" / "hell-grind-aigc-skill" / "scripts" / "audit_prompt.py"


def run_auditor(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDIT_SCRIPT), *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def issue_codes(payload: dict) -> set[str]:
    return {entry["code"] for entry in payload["issues"]}


class PromptAuditTests(unittest.TestCase):
    def test_json_contract_and_empty_prompt(self) -> None:
        result = run_auditor("-", "--medium", "video", "--json", input_text="")
        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        for key in [
            "valid_for_review",
            "score",
            "issues",
            "detected_modules",
            "assumptions",
            "network_requests",
            "database_operations",
        ]:
            self.assertIn(key, payload)
        self.assertFalse(payload["valid_for_review"])
        self.assertIn("P-EMPTY", issue_codes(payload))
        self.assertEqual(payload["network_requests"], 0)
        self.assertEqual(payload["database_operations"], 0)

    def test_medium_is_required_and_restricted(self) -> None:
        missing = run_auditor("-", input_text="一个人物")
        invalid = run_auditor("-", "--medium", "audio", input_text="一个人物")
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(invalid.returncode, 2)

    def test_image_requires_a_visible_subject(self) -> None:
        result = run_auditor("-", "--medium", "image", "--json", input_text="高级，震撼，电影感。")
        self.assertEqual(result.returncode, 1)
        self.assertIn("P-MISSING-SUBJECT", issue_codes(json.loads(result.stdout)))

    def test_video_requires_duration_camera_end_and_audio_boundary(self) -> None:
        result = run_auditor(
            "-",
            "--medium",
            "video",
            "--json",
            input_text="画面中一名女人站在门前。中景摄影机缓慢推进。",
        )
        self.assertEqual(result.returncode, 1)
        codes = issue_codes(json.loads(result.stdout))
        self.assertTrue({"P-MISSING-DURATION", "P-MISSING-CAMERA-END", "P-MISSING-AUDIO"}.issubset(codes))

    def test_file_input_is_read_only_and_text_output_reports_io_counts(self) -> None:
        prompt = (
            "画面中恰好一名女人站在门前。5 秒。"
            "摄影机从眼平中景缓慢推进，最终停在她的右手与门把同框的近景。"
            "只有室内环境音，无配乐、无字幕。"
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "prompt.md"
            path.write_text(prompt)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            result = run_auditor(str(path), "--medium", "video")
            after = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(before, after)
            self.assertIn("Network requests: 0; database operations: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
