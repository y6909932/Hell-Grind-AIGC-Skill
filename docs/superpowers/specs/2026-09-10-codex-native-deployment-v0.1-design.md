# Hell Grind Codex Native Deployment V0.1 设计

## 目标

把现有 `skill/hell-grind-aigc-skill/` 保持为唯一权威 Skill 源，同时增加一个可重复、可验证、可回滚的 Codex 用户级部署层，使用户在不打开 ChatGPT Web 的情况下，也能在任意本地项目中通过 Codex 独立调用 Hell Grind。

## 权威关系

- `GitHub main` 是 Hell Grind System 的唯一权威版本。
- `skill/hell-grind-aigc-skill/` 是唯一权威 Skill 目录；不得维护第二份 Web 版或 Codex 版业务规则。
- ChatGPT Web 主要承担架构、维护、Review，也可直接按仓库规则使用 Skill。
- Codex 主要承担本地执行，也可以通过 feature branch / CI / PR 参与维护权威仓库。
- `$HOME/.agents/skills/hell-grind-aigc-skill/` 只是受控部署副本，不是权威源。

## Codex 发现方式

按 OpenAI 当前 Skill 机制，Codex 会扫描用户级 `$HOME/.agents/skills`，Skill 目录必须包含带 `name` 和 `description` 的 `SKILL.md`。Hell Grind 已满足这一结构；`agents/openai.yaml` 继续提供 UI 元数据和 invocation policy。

V0.1 明确允许 implicit invocation，同时保留 `$hell-grind-aigc-skill` 显式调用。原生语义路由的最终 smoke 必须在真实 Codex 环境完成，普通 pytest 只验证静态契约与部署行为。

## 部署模型

新增：

```text
deployment/codex/
├─ install.ps1
├─ update.ps1
├─ status.ps1
└─ README.md
```

默认目标：

```text
$HOME/.agents/skills/hell-grind-aigc-skill/
```

三个脚本都允许传 `-DestinationRoot`，用于 CI / 临时环境验证；默认仍指向用户级 `.agents/skills`。

### install.ps1

- 从当前仓库的 `skill/hell-grind-aigc-skill/` 复制。
- 默认要求当前 Git 分支为 `main`、工作树干净，并在 `git fetch origin main` 后要求 `HEAD == origin/main`。
- 目标不存在时才安装；若已存在则 fail closed，并提示使用 `update.ps1`。
- 使用 staging 目录完成复制，避免半安装状态。
- 写入 `.hell-grind-deployment.json`，记录 source repo、source commit、Skill version、安装内容 digest 和安装时间。

### update.ps1

- 使用与 install 相同的 source authority 检查。
- 要求目标存在且包含合法 deployment manifest。
- 更新前计算当前已安装内容 digest；若与 manifest 不一致，视为本地漂移并 fail closed，不覆盖用户修改。
- 通过 staging 替换旧部署，更新 manifest。

### status.ps1

只读检查并输出：

- installed / not installed
- installed version / source version
- installed commit / source commit
- clean / local drift
- current / update available

不得修改 Git、Skill 或目标目录。

## Invocation policy

在 `skill/hell-grind-aigc-skill/agents/openai.yaml` 中显式写：

```yaml
policy:
  allow_implicit_invocation: true
```

这样 Codex 可在 AIGC 视频生产、资产/场次/镜头/提示词/连续性/验收等任务与 `description` 匹配时隐式进入 Hell Grind；用户仍可用 `$hell-grind-aigc-skill` 强制显式调用。

## 治理规则

根 `AGENTS.md` 增加 Hell Grind 权威治理段：

```text
GitHub main = 唯一权威
Web / Codex = 客户端与维护者
本地部署副本 ≠ 权威
任何系统修改 = feature branch → CI → Review → PR → main
```

Codex 在真实项目中发现系统缺陷时，可以维护本仓库，但必须走同一开发闭环。

## 测试与验收

自动测试覆盖：

1. canonical Skill 保持唯一；仓库不提交第二份 `.agents/skills/hell-grind-aigc-skill`。
2. `SKILL.md` 仍含正确 `name` / `description`。
3. `openai.yaml` 显式允许 implicit invocation。
4. install / update / status 脚本存在并指向 canonical source 与用户级 target。
5. Windows 临时环境真实执行：install 成功、重复 install fail closed、status current、update 幂等、人工修改部署副本后 update fail closed。
6. 全仓普通测试继续通过。

真实 Codex Native smoke 不由 CI 冒充；部署完成后在用户本机 Codex 使用 `/skills` / `$hell-grind-aigc-skill` 和一组 implicit prompts 做最终发现验证。

## 非目标

- V0.1 不发布 ChatGPT Plugin。
- 不复制第二套 Skill 业务规则。
- 不自动修改 `~/.codex/config.toml`。
- 不自动切换 CC Switch / provider。
- 不自动 `git pull` 或 reset 用户项目。
- 不把本地安装目录当成系统权威。
