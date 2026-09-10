import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = REPO_ROOT / "examples" / "multishot-last-key"
SKILL_ROOT = REPO_ROOT / "skill" / "hell-grind-aigc-skill"
VALIDATE = SKILL_ROOT / "scripts" / "validate_project.py"
AUDIT = SKILL_ROOT / "scripts" / "audit_prompt.py"
PROMPTS = [EXAMPLE / "05_prompts" / f"SC001-SH00{i}-P001.md" for i in range(1, 5)]


def run_json(*args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [sys.executable, *args],
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    return result, payload


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def test_multishot_example_passes_strict_v2_validation() -> None:
    result, payload = run_json(str(VALIDATE), str(EXAMPLE), "--strict-v2", "--json")
    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["valid"] is True
    assert payload["error_count"] == 0
    assert payload["counts"]["assets"] == 3
    assert payload["counts"]["scenes"] == 1
    assert payload["counts"]["shots"] == 4
    assert payload["counts"]["prompts"] == 4
    assert "CONTINUITY_HANDOFF_MISMATCH" not in {
        entry["code"] for entry in payload["issues"]
    }


def test_all_multishot_prompts_pass_video_audit() -> None:
    for prompt in PROMPTS:
        result, payload = run_json(str(AUDIT), str(prompt), "--medium", "video", "--json")
        assert result.returncode == 0, f"{prompt.name}: {result.stdout}{result.stderr}"
        assert payload["valid_for_review"] is True, prompt.name
        assert payload["score"] >= 90, prompt.name
        expected = {
            "subject",
            "quantity",
            "duration",
            "camera",
            "camera_end",
            "audio",
            "lighting_color_material",
            "action_performance",
            "continuity_constraints",
            "platform_adapter",
        }
        assert expected.issubset(set(payload["detected_modules"])), prompt.name


def test_multishot_prompt_index_hashes_match_master_prompts() -> None:
    index_path = EXAMPLE / "05_prompts" / "prompt-index.csv"
    with index_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    by_id = {row["prompt_id"]: row for row in rows}
    for prompt in PROMPTS:
        prompt_id = prompt.stem
        assert prompt_id in by_id
        assert by_id[prompt_id]["prompt_sha256"] == canonical_text_sha256(prompt)


def test_multishot_handoffs_match_exactly_between_adjacent_shots() -> None:
    shots_path = EXAMPLE / "04_shots" / "shots.csv"
    with shots_path.open(newline="", encoding="utf-8") as handle:
        shots = sorted(list(csv.DictReader(handle)), key=lambda row: int(row["shot_order"]))
    assert len(shots) == 4
    for previous, current in zip(shots, shots[1:]):
        assert previous["continuity_out"]
        assert previous["continuity_out"] == current["continuity_in"]
