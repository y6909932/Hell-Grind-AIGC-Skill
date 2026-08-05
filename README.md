# Hell Grind AIGC Skill

一套模型无关的 AIGC 视频生产工作流：把项目搭建、资产与镜头管理、图片/视频提示词生成与润色、生成记录、连续性检查和交付验收整合到一个 Codex Skill 中。

仓库内只有一个可发现的父 Skill：`hell-grind-aigc-skill`。它内部包含：

- 生产管理工作流：brief → 故事 → 资产 → 场次 → 镜头 → 提示词 → 生成记录 → 评审 → 剪辑 → 交付。
- 提示词创作工作流：图片/视频 × 从零生成/润色扩写，支持精简版、标准版和导演版。

默认不调用付费模型、不上传、不发布；项目初始化和校验都是本地操作，网络请求与数据库读写均为 0。

## 核心能力

- 十阶段项目目录和稳定 ID 体系。
- 人物、生物、道具、场景、视效、场次、镜头与生成记录分表管理。
- 图片提示词 11 类信息结构。
- 视频提示词 12 段镜头契约。
- 原始意图与硬约束保护，润色时附修改摘要。
- 平台无关主提示词与模型/平台适配层分离。
- 连续性矩阵、选片记录、质量评分和交付质量门。
- 安全初始化器与只读项目校验器。

## 安装

要求：macOS/Linux、Git、Python 3.10 或更高版本。Skill 本身没有第三方 Python 依赖。

```bash
git clone https://github.com/renmu2017/Hell-Grind-AIGC-Skill.git
cd Hell-Grind-AIGC-Skill
./scripts/install.sh
```

默认安装到 `${CODEX_HOME}/skills/hell-grind-aigc-skill`；未设置 `CODEX_HOME` 时安装到 `~/.codex/skills/hell-grind-aigc-skill`。安装后重新打开一个 Codex 任务，让 Skill 列表刷新。

更新：

```bash
git pull --ff-only
./scripts/install.sh --update
```

`--update` 会先把旧版本移动到同一 Skills 根目录下的 `.backups/`，再安装新版本。

## 使用

### 搭建一个视频项目

对 Codex 说：

```text
使用 $hell-grind-aigc-skill，把这份短片 brief 搭成完整项目，先建立资产、场次和镜头结构，不调用生成模型。
```

也可以直接初始化空模板：

```bash
python3 ~/.codex/skills/hell-grind-aigc-skill/scripts/init_project.py \
  --name "My AIGC Film" \
  --output /absolute/path/My-AIGC-Film \
  --project-id PRJ-MY-FILM-001 \
  --aspect-ratio 16:9
```

校验项目结构和引用：

```bash
python3 ~/.codex/skills/hell-grind-aigc-skill/scripts/validate_project.py \
  /absolute/path/My-AIGC-Film
```

需要机器可读结果时追加 `--json`。

### 从零生成图片提示词

```text
使用 $hell-grind-aigc-skill，为“雨夜便利店门口的疲惫女快递员”写一份标准版图片提示词。模型未知，保持平台无关。
```

### 润色视频提示词

```text
使用 $hell-grind-aigc-skill 润色下面的视频提示词，保留人物数量、逐字台词和 6 秒时长，输出导演版、修改摘要和质量评分：……
```

### 审核现有项目

```text
使用 $hell-grind-aigc-skill 审核这个项目的镜头表、生成记录和连续性矩阵，只读检查，不生成、不上传。
```

## 目录

```text
skill/hell-grind-aigc-skill/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── init_project.py
│   └── validate_project.py
├── references/
└── assets/project-template/
```

## 方法来源与内容边界

这套方法论受到 Higgsfield 公开项目 [Hell Grind](https://higgsfield.ai/@higgsfield.studio/projects/hell-grind) 的制作结构启发，并结合对公开画布中生成记录、提示词结构、资产组织和连续性方法的归纳。

本仓库只发布自行整理的模型无关工作流、模板、脚本和自写示例，不包含《Hell Grind》原视频、原始资产、全量提示词或可替代原项目的数据集。公开可访问不代表获得了再分发许可。

## 许可状态

仓库当前未附开源许可证。安装和查看方式已公开，但在仓库所有者选定许可证之前，不应推定获得复制、修改或再分发授权。
