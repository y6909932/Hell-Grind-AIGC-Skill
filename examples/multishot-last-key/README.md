# 最后一把钥匙｜4 镜头真实生成实验

这是 `minimal-short-film` 的多镜头扩展样例，但保留为独立目录，避免破坏单镜头最小回归。

## 镜头链

1. `SC001-SH001`：建立空间，梅注意到地面钥匙。
2. `SC001-SH002`：右手拾取唯一钥匙。
3. `SC001-SH003`：起身并看向道路左侧。
4. `SC001-SH004`：退入雨棚半步，保持警戒等待。

总目标时长 16 秒，每镜 4 秒。

## 运行前验证

```bash
python skill/hell-grind-aigc-skill/scripts/validate_project.py examples/multishot-last-key --strict-v2 --json
python -m pytest -q tests/test_multishot_example.py
```

## 真实生成

仓库不预填虚构 generation。连接 Provider 后按 `docs/MULTISHOT-GENERATION-RUNBOOK.md` 顺序逐镜执行，并将真实 provider、model、seed、参数、输出路径、费用和失败码写入 `06_generations/generation-log.csv`。

文本连续性通过不等于视觉连续性通过；实际视频仍必须人工检查身份、手持关系、空间、视线与道具数量。
