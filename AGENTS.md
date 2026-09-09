<!-- web-ci-dev-base:start -->
## Web 主脑开发闭环

- 默认开发路径为 `ChatGPT Web → feature branch → GitHub Actions → Web Review → PR → 人类确认 → 受保护分支`。
- ChatGPT、Codex 或其他工程 Agent 不得把普通实现或测试变更直接写入受保护分支。
- 普通自动验证优先使用 GitHub Actions；需要 Windows / 本机环境时优先使用 `scripts/run-local-tests.ps1`。
- 本地 Runner 只测试当前工作树，不得自动执行 `git pull`、`git checkout`、`git switch` 或 `git reset`，不得安装依赖，也不得主动修改源码。
- 测试失败后应通过新的修复提交解决，不得绕过失败结果直接合并。
- 只有普通 CI / 本地 Runner 无法复制的特殊工具或环境行为才升级到对应的真实环境验证。
<!-- web-ci-dev-base:end -->
