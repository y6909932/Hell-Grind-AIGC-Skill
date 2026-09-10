from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "skill" / "hell-grind-aigc-skill"
DEPLOYMENT = ROOT / "deployment" / "codex"


def test_canonical_skill_is_single_repository_authority():
    assert (CANONICAL / "SKILL.md").is_file()
    assert not (ROOT / ".agents" / "skills" / "hell-grind-aigc-skill").exists()

    skill_text = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    assert "name: hell-grind-aigc-skill" in skill_text
    assert "description:" in skill_text


def test_codex_metadata_explicitly_allows_implicit_invocation():
    metadata = (CANONICAL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "policy:" in metadata
    assert "allow_implicit_invocation: true" in metadata


def test_codex_deployment_scripts_exist_and_use_canonical_source_and_user_skill_root():
    for name in ("install.ps1", "update.ps1", "status.ps1"):
        path = DEPLOYMENT / name
        assert path.is_file(), f"missing deployment script: {name}"
        text = path.read_text(encoding="utf-8")
        assert "skill/hell-grind-aigc-skill" in text.replace("\\", "/")
        assert ".agents" in text
        assert "skills" in text
        assert "DestinationRoot" in text


def test_codex_deployment_documentation_exists():
    readme = DEPLOYMENT / "README.md"
    assert readme.is_file()
    text = readme.read_text(encoding="utf-8")
    assert "$hell-grind-aigc-skill" in text
    assert "/skills" in text
    assert "GitHub" in text
    assert "main" in text
