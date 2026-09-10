# Hell Grind Codex Native Deployment V0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 GitHub `main` 中唯一的 Hell Grind Skill 可以安全部署到 Codex 用户级 Skill 目录，并支持安装、更新、状态检查和真实 Windows 验证。

**Architecture:** canonical source 永远是 `skill/hell-grind-aigc-skill/`；Codex 用户级目录只是带 manifest 的受控副本。部署脚本默认只接受 clean + current `main` 作为源，更新前检测本地漂移并 fail closed。

**Tech Stack:** PowerShell 5.1+、Python 3.10+ / pytest、GitHub Actions、Codex local skills

**Spec:** `docs/superpowers/specs/2026-09-10-codex-native-deployment-v0.1-design.md`

## Global Constraints

- GitHub `main` 是唯一权威版本。
- canonical Skill 只允许 `skill/hell-grind-aigc-skill/` 一份。
- 默认 Codex target 为 `$HOME/.agents/skills/hell-grind-aigc-skill/`。
- 部署脚本不得修改 `~/.codex/config.toml`、CC Switch/provider 或用户项目工作树。
- 任何本地部署漂移必须 fail closed，不得静默覆盖。
- Native discovery / implicit routing 最终 smoke 只能由真实 Codex 验证，pytest 不冒充。

---

### Task 1: 部署契约 RED 测试

**Files:**
- Create: `tests/test_codex_native_deployment.py`

**Interfaces:**
- Consumes: canonical Skill metadata and planned deployment paths.
- Produces: static contract tests for the implementation.

- [ ] 写测试断言 canonical Skill 唯一、`openai.yaml` policy、三个脚本与 target/source contract。
- [ ] push 到 feature branch，确认 GitHub Actions 因缺少部署文件/metadata 而失败。
- [ ] 不修改产品代码来绕过失败。

### Task 2: Codex metadata 与治理规则

**Files:**
- Modify: `skill/hell-grind-aigc-skill/agents/openai.yaml`
- Modify: `AGENTS.md`

**Interfaces:**
- Produces: explicit implicit-invocation policy and authority governance.

- [ ] 在 `openai.yaml` 增加 `policy.allow_implicit_invocation: true`。
- [ ] 在 `AGENTS.md` 增加 GitHub main / Web / Codex / local deployment 权威关系。
- [ ] 运行静态部署测试，确认 metadata/governance 部分转绿。

### Task 3: 安装 / 更新 / 状态脚本

**Files:**
- Create: `deployment/codex/install.ps1`
- Create: `deployment/codex/update.ps1`
- Create: `deployment/codex/status.ps1`
- Create: `deployment/codex/README.md`

**Interfaces:**
- `install.ps1 [-DestinationRoot <path>] [-SkipRemoteCheck]`
- `update.ps1 [-DestinationRoot <path>] [-SkipRemoteCheck]`
- `status.ps1 [-DestinationRoot <path>] [-SkipRemoteCheck]`

- [ ] 实现 shared inline helpers：定位 repo/canonical source、Git authority 检查、SHA256 directory digest、manifest 读写。
- [ ] install：目标已存在则 fail closed；staging copy 后写 manifest。
- [ ] update：manifest 缺失/本地 drift 则 fail closed；通过 staging 更新。
- [ ] status：只读输出 installed/current/drift/update available，退出码 0/1 区分健康与需处理状态。
- [ ] 更新 README，写明 Codex `/skills`、`$hell-grind-aigc-skill` 与重启提示。
- [ ] 跑全仓 pytest。

### Task 4: 真实 Windows 部署 smoke

**Files:**
- Create temporary: `.github/workflows/codex-deployment-windows-validation.yml`
- Delete temporary after validation.

**Interfaces:**
- Uses `-DestinationRoot $env:RUNNER_TEMP\codex-skills` and `-SkipRemoteCheck` so CI never touches the runner user's real home.

- [ ] Windows Server 2025 安装 Python/pytest。
- [ ] 执行 install，断言 `SKILL.md`、`agents/openai.yaml` 和 manifest 存在。
- [ ] 第二次 install 必须非零退出。
- [ ] status 必须报告 current。
- [ ] update 必须成功且保持内容一致。
- [ ] 人工修改已部署 `SKILL.md` 后，update 必须非零退出且不得覆盖修改。
- [ ] 删除临时 workflow，再跑普通 CI。

### Task 5: PR / main 收口

**Files:**
- All files above.

- [ ] `compare main...feature` 确认只含 Codex deployment / governance / tests / docs。
- [ ] 创建 PR，等待 PR CI green。
- [ ] Review diff；没有 blocker 后 squash merge。
- [ ] 等待 merge 后 `main` CI green。
- [ ] 最终只声明“工程部署已验证”；真实 Codex Native discovery 仍需本机 smoke。
