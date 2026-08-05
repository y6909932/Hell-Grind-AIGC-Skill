#!/usr/bin/env python3
"""Read-only validation for a Hell Grind AIGC project directory."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_TEXT_FILES = [
    "00_brief/project.yaml",
    "01_story/story-bible.md",
    "05_prompts/prompt-template.md",
    "07_review/qa-checklist.md",
    "08_edit/edit-notes.md",
    "09_delivery/delivery-checklist.md",
]

CSV_SCHEMAS = {
    "02_assets/assets.csv": ["asset_id", "asset_type", "name", "version", "status", "reference_path", "notes"],
    "03_scenes/scenes.csv": ["scene_id", "scene_order", "title", "location_id", "time_of_day", "story_goal", "status", "notes"],
    "04_shots/shots.csv": ["shot_id", "scene_id", "shot_order", "duration_seconds", "status", "prompt_version", "selected_generation_id", "notes"],
    "06_generations/generation-log.csv": ["generation_id", "shot_id", "prompt_version", "provider", "model", "seed", "created_at", "status", "output_path", "cost", "notes"],
    "07_review/selection-log.csv": ["selection_id", "shot_id", "generation_id", "decision", "reviewer", "reviewed_at", "notes"],
    "07_review/continuity-matrix.csv": ["shot_id", "character_ids", "asset_ids", "screen_direction", "costume_state", "injury_state", "prop_state", "environment_state", "notes"],
}

ID_PATTERNS = {
    "asset_id": re.compile(r"^(CHR|CRT|PROP|LOC|VFX)-[A-Z0-9][A-Z0-9-]*$"),
    "scene_id": re.compile(r"^SC\d{3}$"),
    "shot_id": re.compile(r"^SC\d{3}-SH\d{3}$"),
    "generation_id": re.compile(r"^GEN-[A-Z0-9][A-Z0-9-]*$"),
    "selection_id": re.compile(r"^SEL-[A-Z0-9][A-Z0-9-]*$"),
}


def issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def parse_project_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def read_csv(root: Path, relative: str, required: list[str], issues: list[dict[str, str]]) -> list[dict[str, str]]:
    path = root / relative
    if not path.is_file():
        issues.append(issue("MISSING_FILE", relative, "required CSV file is missing"))
        return []
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            for column in required:
                if column not in headers:
                    issues.append(issue("MISSING_COLUMN", relative, f"missing column: {column}"))
            return [{key: (value or "").strip() for key, value in row.items() if key is not None} for row in reader]
    except (OSError, csv.Error, UnicodeError) as error:
        issues.append(issue("INVALID_CSV", relative, str(error)))
        return []


def validate_ids(relative: str, rows: list[dict[str, str]], column: str, issues: list[dict[str, str]]) -> set[str]:
    values = [row.get(column, "") for row in rows if row.get(column, "")]
    for value, count in Counter(values).items():
        if count > 1:
            issues.append(issue("DUPLICATE_ID", relative, f"duplicate {column}: {value}"))
    pattern = ID_PATTERNS[column]
    for value in values:
        if not pattern.fullmatch(value):
            issues.append(issue("INVALID_ID", relative, f"invalid {column}: {value}"))
    return set(values)


def require_references(relative: str, rows: list[dict[str, str]], column: str, valid: set[str], issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(rows, start=2):
        value = row.get(column, "")
        if value and value not in valid:
            issues.append(issue("MISSING_REFERENCE", relative, f"row {index} references missing {column}: {value}"))


def validate_project(root: Path) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if not root.is_dir():
        issues.append(issue("MISSING_PROJECT", str(root), "project directory does not exist"))
        return {"valid": False, "project": str(root), "issues": issues, "counts": {}, "network_requests": 0, "database_operations": 0}

    for relative in REQUIRED_TEXT_FILES:
        if not (root / relative).is_file():
            issues.append(issue("MISSING_FILE", relative, "required file is missing"))

    config_path = root / "00_brief/project.yaml"
    if config_path.is_file():
        config = parse_project_yaml(config_path)
        for key in ["schema_version", "project_id", "project_name", "created_date", "aspect_ratio", "status"]:
            if not config.get(key):
                issues.append(issue("MISSING_CONFIG", "00_brief/project.yaml", f"missing value: {key}"))
        project_id = config.get("project_id", "")
        if project_id and not re.fullmatch(r"^PRJ-[A-Z0-9][A-Z0-9-]{1,61}$", project_id):
            issues.append(issue("INVALID_ID", "00_brief/project.yaml", f"invalid project_id: {project_id}"))

    tables = {relative: read_csv(root, relative, columns, issues) for relative, columns in CSV_SCHEMAS.items()}
    assets = tables["02_assets/assets.csv"]
    scenes = tables["03_scenes/scenes.csv"]
    shots = tables["04_shots/shots.csv"]
    generations = tables["06_generations/generation-log.csv"]
    selections = tables["07_review/selection-log.csv"]
    continuity = tables["07_review/continuity-matrix.csv"]

    asset_ids = validate_ids("02_assets/assets.csv", assets, "asset_id", issues)
    scene_ids = validate_ids("03_scenes/scenes.csv", scenes, "scene_id", issues)
    shot_ids = validate_ids("04_shots/shots.csv", shots, "shot_id", issues)
    generation_ids = validate_ids("06_generations/generation-log.csv", generations, "generation_id", issues)
    validate_ids("07_review/selection-log.csv", selections, "selection_id", issues)

    require_references("03_scenes/scenes.csv", scenes, "location_id", asset_ids, issues)
    require_references("04_shots/shots.csv", shots, "scene_id", scene_ids, issues)
    require_references("04_shots/shots.csv", shots, "selected_generation_id", generation_ids, issues)
    require_references("06_generations/generation-log.csv", generations, "shot_id", shot_ids, issues)
    require_references("07_review/selection-log.csv", selections, "shot_id", shot_ids, issues)
    require_references("07_review/selection-log.csv", selections, "generation_id", generation_ids, issues)
    require_references("07_review/continuity-matrix.csv", continuity, "shot_id", shot_ids, issues)

    counts = {
        "assets": len(assets),
        "scenes": len(scenes),
        "shots": len(shots),
        "generations": len(generations),
        "selections": len(selections),
        "continuity_rows": len(continuity),
    }
    return {
        "valid": not issues,
        "project": str(root),
        "issues": issues,
        "counts": counts,
        "network_requests": 0,
        "database_operations": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Project directory to validate")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_project(args.project.expanduser().resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["valid"] else "FAIL"
        print(f"{status}: {result['project']}")
        for entry in result["issues"]:
            print(f"- [{entry['code']}] {entry['path']}: {entry['message']}")
        print(f"Counts: {json.dumps(result['counts'], ensure_ascii=False)}")
        print("Network requests: 0; database operations: 0")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
