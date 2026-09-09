# 极简实战：最后一把钥匙

这是一个 **6 秒、1 场、1 镜、1 人、1 个关键道具** 的 schema v2 最小项目，用来展示 Hell Grind AIGC Skill 从资产到提示词的完整闭环。

## 故事

雨后的深夜，维修员梅独自在路边维修站值班。她听见脚边一声轻微金属响，发现一把不属于她的旧黄铜钥匙。她捡起钥匙，抬眼望向黑暗道路，警觉起来。

## 生产链

```text
资产
  ↓
资产状态版本
  ↓
场次 + 空间
  ↓
镜头契约
  ↓
beat timeline + audio cues
  ↓
七层平台无关提示词
  ↓
strict-v2 校验 + prompt audit
```

关键文件：

- `02_assets/assets.csv`：角色、钥匙、地点。
- `02_assets/asset-state-matrix.csv`：当前版本状态。
- `03_scenes/scenes.csv`：场次 open/close state。
- `03_scenes/spatial-map.csv`：前中后景、屏幕关系与光源。
- `04_shots/shots.csv`：完整镜头契约。
- `04_shots/beat-sheet.csv`：6 秒动作节拍。
- `04_shots/audio-cues.csv`：环境音与钥匙拟音。
- `05_prompts/SC001-SH001-P001.md`：七层提示词完整输出。
- `07_review/continuity-matrix.csv`：镜头入/出连续性。

## 验证

仓库测试会自动运行：

```bash
python -m pytest -q
```

其中 `tests/test_minimal_example.py` 会额外验证本样例：

```bash
python skill/hell-grind-aigc-skill/scripts/validate_project.py \
  examples/minimal-short-film --strict-v2 --json

python skill/hell-grind-aigc-skill/scripts/audit_prompt.py \
  examples/minimal-short-film/05_prompts/SC001-SH001-P001.md \
  --medium video --json
```

本样例不调用任何生成模型，因此只验收**生产结构与提示词契约**，不声称验证了真实生成质量。
