---
name: hell-grind-aigc-skill
description: Model-agnostic AIGC video production management and prompt creation workflow. Use when Codex needs to initialize, structure, audit, or manage an AI video project; create or polish image prompts; create or polish video prompts; preserve prompt intent and hard constraints; track assets, scenes, shots, generations, continuity, review, and delivery; or turn a loose creative brief into a production-ready AIGC workflow.
---

# Hell Grind AIGC Skill

Use one parent Skill with two internal workflows. Keep the deliverable model-independent and separate project truth from provider-specific settings.

## Route the request

- For project setup, planning, tracking, audit, continuity, or delivery, use the **生产管理工作流**. Read `references/production-workflow.md` and `references/project-schemas.md`; also read `references/project-qa-gates.md` for audits or delivery checks.
- For 图片从零生成 or 图片润色扩写, use the **提示词创作工作流**. Read `references/image-prompt-crafting.md`, `references/prompt-preservation.md`, and `references/prompt-quality-rubric.md`.
- For 视频从零生成 or 视频润色扩写, use the **提示词创作工作流**. Read `references/video-prompt-contract.md`, `references/prompt-preservation.md`, and `references/prompt-quality-rubric.md`.
- Read `references/prompt-examples.md` only when an example materially helps.
- When prompt work belongs to an existing project, first read its asset, scene, shot, and continuity records. Carry stable IDs and approved facts into the prompt.

## Work in this order

1. Classify the request by workflow, medium, operation, and richness: concise, standard, or director.
2. Extract the user's intent, hard constraints, reference scope, output use, and unresolved choices.
3. Ask only for a missing fact that would materially change the result. Otherwise state a conservative assumption.
4. Apply the selected workflow and keep platform-independent content separate from the platform adapter.
5. Validate IDs, references, continuity, prompt completeness, contradictions, and delivery gates.
6. Return the requested artifact plus the fixed output fields defined in the relevant reference.

## Initialize or audit a project

Run the bundled scripts when local file creation is requested:

```bash
python3 scripts/init_project.py --name "Project name" --output /absolute/project/path
python3 scripts/validate_project.py /absolute/project/path
```

The initializer must refuse a non-empty target. The validator must remain read-only. Do not replace these safety behaviors with ad hoc file operations.

## Preserve boundaries

- 默认不调用付费模型，不上传、不发布、不部署。
- Do not treat prompt writing as authorization to generate media.
- Do not invent an authorization, budget, provider, reference right, or delivery approval.
- Do not copy project-specific Hell Grind characters, assets, or long source prompts into a new project unless the user separately supplies rights and requests reuse.
- Keep each local initialize/validate operation at 0 network requests and 0 database operations.

If the user explicitly requests generation or publication, treat it as a separate action and follow the active tool's confirmation, cost, and safety rules.
