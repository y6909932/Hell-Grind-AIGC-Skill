# 多镜头真实生成实验 V0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在保留单镜头基线的同时，新增一个 4 镜头、16 秒、可直接送入真实视频 Provider 的跨镜头连续性实验样例，并用自动化测试证明 schema、提示词和交接契约成立。

**Architecture:** 新增 `examples/multishot-last-key/` 作为第二个消费者样例，不修改 `examples/minimal-short-film/`。四个镜头共用同一组已锁定资产，通过相邻 `continuity_out` / `continuity_in` 精确交接；真实生成结果仍由现有 generation / selection / continuity 记录格式承接，不把具体 Provider 固化进核心代码。

**Tech Stack:** Python 3.10、pytest、CSV/Markdown schema v2、现有 `validate_project.py`、现有 `audit_prompt.py`、GitHub Actions、Windows PowerShell Runner。

**Spec:** `docs/superpowers/specs/2026-09-10-multishot-generation-experiment-v0.1-design.md`

## Global Constraints

- 不修改或删除现有 `examples/minimal-short-film/` 单镜头回归样例。
- 新样例固定 1 场、4 镜头、总时长 16 秒、3 个资产：梅、黄铜钥匙、路边维修站。
- 不伪造任何真实 Provider 成功生成记录。
- 每个 master prompt 必须通过现有 video Prompt Auditor。
- 所有 prompt SHA256 使用规范化 UTF-8/LF 内容哈希。
- Web 只在 feature branch 上修改；最终通过 CI 与 PR 合并到 `main`。

---

### Task 1: 先建立多镜头验收测试

**Files:**
- Create: `tests/test_multishot_example.py`

**Interfaces:**
- Consumes: `validate_project.py` CLI、`audit_prompt.py` CLI。
- Produces: 对新样例目录、4 个 prompt、连续性交接与哈希的回归契约。

- [ ] **Step 1: 写失败测试**

测试固定要求：`examples/multishot-last-key` 存在；strict v2 返回 `shots == 4`、`prompts == 4`、`assets == 3`；四份 prompt 都能通过 auditor；prompt index 中四个哈希与文件一致；validator 不返回 `CONTINUITY_HANDOFF_MISMATCH`。

- [ ] **Step 2: 运行测试验证 RED**

Run: `python -m pytest -q tests/test_multishot_example.py`

Expected: FAIL，因为 `examples/multishot-last-key/` 尚不存在。

- [ ] **Step 3: 提交测试**

Commit: `test: define multishot generation experiment acceptance`

### Task 2: 建立 4 镜头 schema v2 样例

**Files:**
- Create: `examples/multishot-last-key/00_brief/project.yaml`
- Create: `examples/multishot-last-key/00_brief/brief.md`
- Create: `examples/multishot-last-key/01_story/story-bible.md`
- Create: `examples/multishot-last-key/02_assets/assets.csv`
- Create: `examples/multishot-last-key/02_assets/reference-scope.csv`
- Create: `examples/multishot-last-key/02_assets/asset-state-matrix.csv`
- Create: `examples/multishot-last-key/03_scenes/scenes.csv`
- Create: `examples/multishot-last-key/03_scenes/spatial-map.csv`
- Create: `examples/multishot-last-key/04_shots/shots.csv`
- Create: `examples/multishot-last-key/04_shots/beat-sheet.csv`
- Create: `examples/multishot-last-key/04_shots/audio-cues.csv`
- Create: `examples/multishot-last-key/05_prompts/prompt-template.md`
- Create: `examples/multishot-last-key/06_generations/generation-log.csv`
- Create: `examples/multishot-last-key/06_generations/iteration-log.csv`
- Create: `examples/multishot-last-key/07_review/selection-log.csv`
- Create: `examples/multishot-last-key/07_review/continuity-matrix.csv`
- Create: `examples/multishot-last-key/07_review/waivers.csv`
- Create: `examples/multishot-last-key/07_review/qa-checklist.md`
- Create: `examples/multishot-last-key/08_edit/edit-notes.md`
- Create: `examples/multishot-last-key/09_delivery/delivery-checklist.md`

**Interfaces:**
- Consumes: 现有 schema v2 列定义。
- Produces: 可被 validator 读取的 1 场 4 镜头项目骨架。

- [ ] **Step 1: 按 spec 写 4 个镜头与连续性交接**
- [ ] **Step 2: strict v2 校验项目结构**

Run: `python skill/hell-grind-aigc-skill/scripts/validate_project.py examples/multishot-last-key --strict-v2 --json`

Expected: 只允许因为 prompt 文件尚未完成而产生对应失败，不允许资产、镜头、beat、audio、continuity 外键错误。

- [ ] **Step 3: 提交项目骨架**

Commit: `feat: add four-shot continuity experiment skeleton`

### Task 3: 写四份逐镜 L1～L7 master prompt

**Files:**
- Create: `examples/multishot-last-key/05_prompts/SC001-SH001-P001.md`
- Create: `examples/multishot-last-key/05_prompts/SC001-SH002-P001.md`
- Create: `examples/multishot-last-key/05_prompts/SC001-SH003-P001.md`
- Create: `examples/multishot-last-key/05_prompts/SC001-SH004-P001.md`
- Create: `examples/multishot-last-key/05_prompts/prompt-index.csv`

**Interfaces:**
- Consumes: `shots.csv` 中的 camera / continuity / must_hold / must_not_appear。
- Produces: 四份 provider-agnostic master prompt 与规范化哈希索引。

- [ ] **Step 1: 写四份 prompt**

每份都必须包含主体数量、4 秒时长、单一主运镜、起止构图、动作 beat、环境/材质、连续性硬约束、禁止项、Provider 适配层。

- [ ] **Step 2: 对四份 prompt 逐一运行 auditor**

Run: `python skill/hell-grind-aigc-skill/scripts/audit_prompt.py <prompt> --medium video --json`

Expected: 四份均 `valid_for_review == true`。

- [ ] **Step 3: 计算 canonical UTF-8/LF SHA256 并写入 prompt-index**
- [ ] **Step 4: 运行 Task 1 测试转 GREEN**

Run: `python -m pytest -q tests/test_multishot_example.py`

Expected: PASS。

- [ ] **Step 5: 提交 prompt**

Commit: `feat: add four-shot provider-agnostic master prompts`

### Task 4: 文档化真实 Provider 运行协议

**Files:**
- Create: `examples/multishot-last-key/README.md`
- Create: `docs/MULTISHOT-GENERATION-RUNBOOK.md`

**Interfaces:**
- Consumes: 四份 master prompt 与现有 generation / selection / continuity schema。
- Produces: 用户连接 Higgsfield/其他视频 Provider 后可直接执行的逐镜运行顺序和回填规则。

- [ ] **Step 1: 写运行顺序**

固定顺序：先生成 SH001 并选定角色/场景参考 → SH002 继承已批准参考 → SH003 继承 SH002 结束状态 → SH004 继承 SH003 结束状态。每次运行只改变当前镜头允许变化的变量。

- [ ] **Step 2: 写回填要求**

生成后必须写 `generation-log.csv`；选片后写 `selection-log.csv`；出现问题写 `iteration-log.csv`；视觉连续性异常写 `continuity-matrix.csv.open_issues`，不能通过修改文本契约掩盖生成缺陷。

- [ ] **Step 3: 提交文档**

Commit: `docs: add multishot provider runbook`

### Task 5: 全仓回归、CI、PR 与合并

**Files:**
- No production files beyond previous tasks.

**Interfaces:**
- Consumes: 全部新增样例与测试。
- Produces: 可合并的 feature branch。

- [ ] **Step 1: 运行完整 pytest**

Run: `python -m pytest -q`

Expected: 现有 48 条加新增多镜头测试全部通过。

- [ ] **Step 2: 推送 feature branch，读取 GitHub Actions 结果**
- [ ] **Step 3: Review diff，确认未修改单镜头样例与核心 schema 接口**
- [ ] **Step 4: 创建 PR 到 `main`**
- [ ] **Step 5: PR CI 通过后 squash merge**
- [ ] **Step 6: 读取 merge 后 `main` CI，只有它再次通过才宣布完成**
