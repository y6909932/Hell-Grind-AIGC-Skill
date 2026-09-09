import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = REPO_ROOT / "examples" / "minimal-short-film"
SKILL_ROOT = REPO_ROOT / "skill" / "hell-grind-aigc-skill"
VALIDATE = SKILL_ROOT / "scripts" / "validate_project.py"
AUDIT = SKILL_ROOT / "scripts" / "audit_prompt.py"
PROMPT = EXAMPLE / "05_prompts" / "SC001-SH001-P001.md"


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


def test_minimal_example_passes_strict_v2_validation() -> None:
    result, payload = run_json(str(VALIDATE), str(EXAMPLE), "--strict-v2", "--json")
    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["valid"] is True
    assert payload["error_count"] == 0
    assert payload["counts"]["assets"] == 3
    assert payload["counts"]["scenes"] == 1
    assert payload["counts"]["shots"] == 1
    assert payload["counts"]["prompts"] == 1


def test_minimal_example_prompt_passes_video_audit() -> None:
    result, payload = run_json(str(AUDIT), str(PROMPT), "--medium", "video", "--json")
    assert result.returncode == 0, result.stdout + result.stderr
    assert payload["valid_for_review"] is True
    assert payload["score"] == 100
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
    assert expected.issubset(set(payload["detected_modules"]))


def test_prompt_index_hash_matches_master_prompt() -> None:
    with (EXAMPLE / "05_prompts" / "prompt-index.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        row = next(csv.DictReader(handle))
    actual = canonical_text_sha256(PROMPT)
    assert row["prompt_sha256"] == actual
