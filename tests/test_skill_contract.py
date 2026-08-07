import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skill" / "hell-grind-aigc-skill"


class SkillContractTests(unittest.TestCase):
    def test_v2_version_and_router_cover_all_entry_modes(self) -> None:
        self.assertEqual((SKILL_ROOT / "VERSION").read_text().strip(), "2.0.0")
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        for phrase in [
            "生产管理",
            "图片从零生成",
            "图片润色扩写",
            "视频从零生成",
            "视频润色扩写",
            "失败诊断",
            "精简版",
            "标准版",
            "导演版",
        ]:
            self.assertIn(phrase, skill)

    def test_skill_frontmatter_is_trigger_focused_and_body_is_compact(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text()
        description = re.search(r"(?m)^description: (.+)$", text).group(1)
        self.assertTrue(description.startswith("Use when"))
        self.assertLessEqual(len(text.splitlines()), 500)

    def test_core_methodology_references_define_evidence_and_seven_layers(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        evidence_path = SKILL_ROOT / "references" / "methodology-evidence.md"
        architecture_path = SKILL_ROOT / "references" / "prompt-architecture.md"
        self.assertTrue(evidence_path.is_file())
        self.assertTrue(architecture_path.is_file())
        evidence = evidence_path.read_text()
        architecture = architecture_path.read_text()
        for phrase in ["115,450", "7,482", "15.41", "规则匹配", "因果"]:
            self.assertIn(phrase, evidence)
        for layer in range(1, 8):
            self.assertRegex(architecture, rf"(?m)^### L{layer} ")
        for phrase in ["必须保持", "本镜变化", "禁止出现", "冲突优先级", "平台适配层"]:
            self.assertIn(phrase, architecture)
        for relative in ["references/methodology-evidence.md", "references/prompt-architecture.md"]:
            self.assertIn(relative, skill)

    def test_single_parent_skill_routes_both_internal_workflows(self) -> None:
        skill_files = list((REPO_ROOT / "skill").rglob("SKILL.md"))
        self.assertEqual(skill_files, [SKILL_ROOT / "SKILL.md"])
        text = skill_files[0].read_text()
        self.assertRegex(text, r"(?m)^name: hell-grind-aigc-skill$")
        self.assertIn("生产管理工作流", text)
        self.assertIn("提示词创作工作流", text)
        self.assertIn("图片从零生成", text)
        self.assertIn("图片润色扩写", text)
        self.assertIn("视频从零生成", text)
        self.assertIn("视频润色扩写", text)
        self.assertIn("不调用付费模型", text)

    def test_prompt_contracts_cover_image_11_and_video_12_modules(self) -> None:
        image = (SKILL_ROOT / "references" / "image-prompt-crafting.md").read_text()
        video = (SKILL_ROOT / "references" / "video-prompt-contract.md").read_text()
        image_items = re.findall(r"(?m)^\d+\. ", image)
        video_items = re.findall(r"(?m)^\d+\. ", video)
        self.assertEqual(len(image_items), 11)
        self.assertEqual(len(video_items), 12)

    def test_ui_metadata_and_default_prompt_are_discoverable(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text()
        self.assertIn('display_name: "Hell Grind AIGC Skill"', metadata)
        self.assertIn("$hell-grind-aigc-skill", metadata)
        description = re.search(r'short_description: "([^"]+)"', metadata).group(1)
        self.assertGreaterEqual(len(description), 25)
        self.assertLessEqual(len(description), 64)

    def test_references_include_safety_and_fixed_outputs(self) -> None:
        preserve = (SKILL_ROOT / "references" / "prompt-preservation.md").read_text()
        rubric = (SKILL_ROOT / "references" / "prompt-quality-rubric.md").read_text()
        workflow = (SKILL_ROOT / "references" / "production-workflow.md").read_text()
        for phrase in ["硬约束", "修改摘要", "平台适配层"]:
            self.assertIn(phrase, preserve)
        for phrase in ["质量评分", "负面约束", "假设与待确认项"]:
            self.assertIn(phrase, rubric)
        self.assertIn("0 个网络请求", workflow)
        self.assertIn("0 次数据库读写", workflow)


if __name__ == "__main__":
    unittest.main()
