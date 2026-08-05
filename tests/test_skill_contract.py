import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skill" / "hell-grind-aigc-skill"


class SkillContractTests(unittest.TestCase):
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
