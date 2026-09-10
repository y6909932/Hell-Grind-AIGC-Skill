# Hell Grind Codex Native Skill 部署

本目录把仓库中的唯一 canonical Skill：

```text
skill/hell-grind-aigc-skill/
```

部署到 Codex 用户级 Skill 目录。**GitHub `main` 始终是权威；用户目录里的副本只负责执行。**

OpenAI 当前 Codex Skill 机制会扫描 `$HOME/.agents/skills`。安装后默认位置为：

```text
$HOME/.agents/skills/hell-grind-aigc-skill/
```

## 首次安装

先确保本地仓库处于最新、干净的 `main`：

```powershell
git switch main
git pull --ff-only
.\deployment\codex\install.ps1
```

安装器默认会检查：

- 当前分支必须是 `main`；
- 工作树必须干净；
- 本地 `HEAD` 必须与 `origin/main` 一致；
- 目标目录不得已经存在。

## 更新

当 GitHub `main` 升级后：

```powershell
git switch main
git pull --ff-only
.\deployment\codex\update.ps1
```

更新前会校验部署 manifest 与已安装内容 digest。如果你直接手改了用户级 Skill 副本，更新会 fail closed，不会静默覆盖。正确做法是把系统修改提交回本仓库 feature branch，经 CI / Review / PR 合入 `main`，再重新部署。

## 查看状态

```powershell
.\deployment\codex\status.ps1
```

可能返回：

```text
status=current
status=update-available
status=local-drift
status=not-installed
```

`status.ps1` 不会修改 Git、Codex 配置或 Skill 内容。

## 在 Codex 中使用

Codex 检测新 Skill 后，可通过：

```text
/skills
```

确认 `hell-grind-aigc-skill` 已出现；也可以显式调用：

```text
$hell-grind-aigc-skill
```

例如：

```text
$hell-grind-aigc-skill 用 Hell Grind 给这个 30 秒悬疑短片建立资产、场次、镜头契约和 L1～L7 提示词。
```

Skill 也允许 implicit invocation：当任务明确属于 AIGC 视频生产、资产/场次/镜头/提示词/连续性/审计范围时，Codex 可以依据 `SKILL.md` 的 `description` 自动选择它。

如果安装后没有立即出现，重启 Codex 再检查。Native discovery 与 implicit routing 属于真实 Codex 行为，最终必须在本机 Codex 做 smoke；普通 pytest 不能替代这一层。

## CI / 测试参数

三个脚本都接受：

```powershell
-DestinationRoot <path>
```

用于把 Skill 部署到临时目录，不触碰真实 `$HOME/.agents/skills`。

`-SkipRemoteCheck` 只用于 CI / 临时验证或明确的离线场景；它跳过 `main == origin/main` 的远端权威检查，但仍要求当前源工作树干净。日常安装和更新不要使用这个参数。

## 不做什么

部署脚本不会：

- 修改 `~/.codex/config.toml`；
- 修改 CC Switch / provider；
- 登录或切换 OpenAI 账号；
- 自动修改任何 AIGC 项目工作树；
- 把用户级部署目录提升为权威源。
