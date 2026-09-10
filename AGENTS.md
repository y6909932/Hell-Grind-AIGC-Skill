<!-- web-ci-dev-base:start -->
## Web 主脑开发闭环

- 默认开发路径为 `ChatGPT Web → feature branch → GitHub Actions → Web Review → PR → 人类确认 → 受保护分支`。
- ChatGPT、Codex 或其他工程 Agent 不得把普通实现或测试变更直接写入受保护分支。
- 普通自动验证优先使用 GitHub Actions；需要 Windows / 本机环境时优先使用 `scripts/run-local-tests.ps1`。
- 本地 Runner 只测试当前工作树，不得自动执行 `git pull`、`git checkout`、`git switch` 或 `git reset`，不得安装依赖，也不得主动修改源码。
- 测试失败后应通过新的修复提交解决，不得绕过失败结果直接合并。
- 只有普通 CI / 本地 Runner 无法复制的特殊工具或环境行为才升级到对应的真实环境验证。
<!-- web-ci-dev-base:end -->

## Hell Grind 权威与执行治理

- GitHub `main` 是 Hell Grind System 的唯一权威版本；ChatGPT Web 会话、Codex 本地上下文和任何本地 Skill 副本都不是权威源。
- `skill/hell-grind-aigc-skill/` 是唯一 canonical Skill；不得另建一套 Web 版或 Codex 版业务规则。
- ChatGPT Web 主要承担系统架构、复杂维护和 Review，也可以直接按 canonical Skill 工作。
- Codex 主要承担本地执行；它也可以维护 Hell Grind，但任何系统修改必须走 `feature branch → CI → Review → PR → main`。
- `$HOME/.agents/skills/hell-grind-aigc-skill/` 只是 Codex 用户级部署副本。部署副本允许执行，不允许反向成为权威；发现系统问题时应修改本仓库 canonical source，而不是长期手改部署目录。
- Codex provider / CC Switch 路由由人类管理；本仓库脚本不得自动改写 `~/.codex/config.toml`、provider 或登录状态。
