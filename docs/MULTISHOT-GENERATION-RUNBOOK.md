# 多镜头真实生成 Runbook V0.1

## 原则

本 Runbook 用于把 `examples/multishot-last-key/` 的四份平台无关 master prompt 送入真实视频 Provider。核心契约保持模型无关；Provider 只负责执行，不拥有剧情事实或连续性真相。

## 推荐首轮 Provider

优先使用能够接收参考图、首尾帧或角色一致性控制的视频 Provider。若使用 Higgsfield，可在其模型层选择适合当前镜头约束的视频模型；若使用其他 Provider，也沿用同一回填格式。模型选择只写在平台适配层，不反向修改 master prompt 的剧情事实与连续性硬约束。

## 执行顺序

### 1. 生成 SH001

使用 `SC001-SH001-P001.md`。首轮只验证：梅的身份、维修站空间、唯一地面钥匙、半开卷帘门和 camera_end。

从候选中只选一个通过基础身份门的结果，记录 generation 与 selection。该结果的稳定人物/场景参考可作为后续镜头参考输入。

### 2. 生成 SH002

使用 `SC001-SH002-P001.md`，继承 SH001 已批准的人物与场景参考。唯一允许的关键状态变化是：钥匙从地面转移到梅的右手，梅从站立进入半蹲。

若出现左手拾取、第二把钥匙、卷帘门变化或身份漂移，记录 failure code 并迭代，不修改 continuity 契约迁就错误结果。

### 3. 生成 SH003

使用 `SC001-SH003-P001.md`，继承 SH002 的右手持钥匙终态。唯一主要变化是梅从半蹲起身，并把注意方向锁到道路左侧。

不得新增可见车辆或第二个人。

### 4. 生成 SH004

使用 `SC001-SH004-P001.md`，继承 SH003 的人物、右手钥匙、道路左侧视线与半开卷帘门。只允许后退半步并停稳。

## 每次真实生成后的回填

写入 `06_generations/generation-log.csv`：

- `generation_id`
- `shot_id`
- `prompt_id`
- `batch_id`
- `provider`
- `model`
- `seed`
- `parameters_json`
- `created_at`
- `status`
- `output_path`
- `cost`
- `currency`
- `failure_codes`

若改变 prompt 参数或约束，写入 `iteration-log.csv`。若选片，写入 `selection-log.csv`。若发现跨镜头视觉问题，写入 `continuity-matrix.csv.open_issues`。

## 视觉验收顺序

先查硬错误：人物数量、钥匙数量、左右手、卷帘门、服装身份。再查空间与视线。最后才评估表演、节奏和质感。

100/100 Prompt Auditor 分数只代表结构完整，不代表模型输出质量。文本 handoff 一致只代表契约一致，不代表像素级或语义级连续性已经通过。
