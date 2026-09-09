# Web + CI 基座接入与极简短片实战验收

## 结论

本轮接入通过验收，可以进入 `main`。

仓库已采用 `web-ci-dev-base V0.1` 作为通用开发闭环，并用一个真实的 schema v2 极简短片项目验证了从资产、场次、镜头契约到七层提示词、项目校验、提示词审计、Linux CI 与 Windows 本地 Runner 的完整链路。

## 极简实战样例

样例目录：`examples/minimal-short-film/`。

短片为 6 秒、1 个场次、1 个镜头：雨夜维修站中，夜班维修员梅发现湿地上的一把黄铜钥匙，右手拾起后看向道路方向，状态由疲惫转为警觉。

样例包含：

- 角色、道具、地点资产与资产状态；
- 场次状态与空间地图；
- 镜头契约、动作 beat sheet、audio cues；
- `continuity_in / continuity_out`；
- `must_hold / changes_here / must_not_appear`；
- `camera_start / camera_path / camera_end`；
- L1～L7 七层平台无关提示词；
- prompt-index 与提示词内容指纹。

## 自动验收结果

最终 feature branch 验证：

- Linux GitHub Actions：`48 passed`；
- Windows Server 2025：生成的 `scripts/run-local-tests.ps1` 真实执行，`48 passed`；
- 极简样例：`validate_project.py --strict-v2 --json` 通过；
- 七层视频提示词：`audit_prompt.py --medium video --json` 结构评分 `100/100`。

Windows 验收 workflow 只用于本轮消费者验证，验证通过后已从分支删除，不进入长期 `main` 配置。

## 本轮实战暴露并修复的问题

### 基座层

1. Windows PowerShell 5.1 的 `TrimEnd` 反斜杠参数兼容问题：已在 `web-ci-dev-base` 上游修复。
2. pytest / Python 缓存导致只读 Runner 误报工作树变化：已由 Python Adapter managed ignore 修复。
3. Windows Python 默认本地代码页导致中文 UTF-8 文件和 subprocess 文本失败：已在基座 Runner 中统一 `PYTHONUTF8=1` 与 `PYTHONIOENCODING=utf-8`，并增加真实中文 fixture 回归。

### Hell Grind 工程层

1. `prompt-index.csv` 现在校验 `master_prompt_path` 是否存在，并校验 `prompt_sha256`。
2. 提示词指纹改为规范化 UTF-8 / LF 文本哈希，避免 Windows CRLF 与 Linux LF 导致同内容不同哈希。
3. `beat-sheet.csv` 的 `audio_cue_id` 现在校验到 `audio-cues.csv`。
4. `actor_or_source` 与 `contact_target` 中的资产版本引用现在校验到合法 `asset_version_id`。
5. 同一场次相邻镜头新增保守的 `continuity_out → continuity_in` 交接检查；不一致以 warning 报告，不擅自改写创作事实。
6. Prompt Auditor 的“参考”识别已收窄到实际参考资产语义，普通“参考槽”等平台适配描述不再误触发 `P-REFERENCE-SCOPE`。

## 保留边界

以下内容不应被本轮验收误读为已经解决：

- `100/100` 是提示词结构完整度，不代表某个生成模型一定得到理想画面；
- 连续性交接检查目前是确定性文本契约检查，不替代语义级连续性审片；
- `web-ci-dev-base` 是私有基座，而本仓库是公开仓库，因此本仓库的默认 `GITHUB_TOKEN` 不能跨仓库 checkout 私有基座。基座 installer / ownership / 幂等契约在基座自己的 Windows CI 中验证；消费者仓库只长期保留生成后的 CI 与本地 Runner。

## 最终开发闭环

```text
Web / 开发者
    ↓
feature branch
    ↓
GitHub Actions 普通回归
    ↓
Review / 修复
    ↓
PR
    ↓
确认后合并 main
```

Windows 本地验证继续使用：

```powershell
.\scripts\run-local-tests.ps1
```

Runner 只测试当前工作树，不自动 pull、checkout、switch、reset 或安装依赖；报告只写入被忽略的 `.ai-results/`。
