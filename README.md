# codex-team-kit-router

把本目录内的文件合并到目标项目根目录后，即可获得一套路由式 Codex 子代理团队模板。新版采用瘦 `AGENTS.md` 入口，详细规则按任务路由到 `Docs/` 和 `.codex/team/`，避免主线程一开始就被过多上下文塞满。

## 使用方式

推荐用法是：用户把本仓库 GitHub 地址发给目标项目里的 AI，让 AI 完成接入和初始化。

```text
请参考并接入这个 Codex 团队模板：
https://github.com/ZainDarcy/codex-team-kit-router

要求：
1. 先探测目标项目已有 AGENTS.md、AGENT.md、docs/Docs、项目规范、项目进度和 .codex/，不要直接覆盖。
2. 在 .codex/team-kit.toml 里确定 docs_root、项目规范、项目进度、团队目录和公共文件清单。
3. 选择初始化模式；默认用团队就绪模式。
4. 按我的项目语言习惯随机给团队成员起真实人名，并初始化团队名册和成员档案。
5. 初始化后运行模板体检，并汇报真相源、改动文件和未生成/未迁移的内容。
```

AI 接入后，普通任务可以直接对 Codex 说：

```text
按轻量模式处理这个需求：...
```

需要团队流程或子代理时说：

```text
按开发团队流程执行这个需求，允许使用子代理：...
```

只想先规划时说：

```text
先给我一版子代理分工方案，不要执行：...
```

## 目录结构

```text
.
├── AGENTS.md
├── README.md
├── CHANGELOG.md
├── Docs/
│   ├── README.md
│   ├── 01-项目/
│   ├── 02-执行/
│   └── 03-团队/
└── .codex/
    ├── agents/
    ├── team/
    ├── team-kit.toml
    └── tools/
```

## 已有项目接入方式

如果目标项目已经有 `AGENTS.md`、`AGENT.md`、项目进度或项目规范，不要整目录覆盖，按合并方式接入：

1. 先盘点现有 `AGENTS.md`、`AGENT.md`、项目进度、项目规范、`.codex/`、`docs/Docs` 大小写和已有 AI 工作流文档。
2. 官方入口优先使用 `AGENTS.md`。如果项目只有 `AGENT.md`，新建瘦 `AGENTS.md`，并把旧 `AGENT.md` 作为按需读取的历史/团队手册。
3. 保留现有项目进度和项目规范；先确定唯一真相源，不创建内容重复的桥接副本，必要时只创建索引页。
4. 更新 `.codex/team-kit.toml`，把 `docs_root`、项目规范、项目进度、团队目录和公共文件清单渲染成目标项目的实际路径。
5. 如果已有 `.codex/`，逐项合并 `.codex/agents/`、`.codex/team/` 和 `.codex/tools/check_template_integrity.py`；不要直接覆盖 `.codex/config.toml`。
6. 执行 `Docs/03-团队/Agents/团队初始化.md`：按目标项目语言随机起真实人名，创建团队名册和成员档案。
7. 合并后运行本地模板体检；如果需要确认官方行为，先查当前 OpenAI Codex 官方文档。

## 初始化模式

- 最小模式：只接入 Router、公共文件写锁、派发协议、核心 agents 和体检脚本；第一次 Team 路由前再创建成员档案和工作记录目录。
- 团队就绪模式：推荐默认。初始化时随机起名并创建团队名册和成员档案，不创建虚假的初始工作记录。
- 完整模式：在团队就绪模式基础上保留交付模板，适合长期团队沉淀。

## 核心约定

- `AGENTS.md` 是 Codex 主线程瘦入口，只保留路由和硬规则。
- `.codex/team-kit.toml` 是目标项目路径、真相源和公共文件清单的配置源。
- `Docs/README.md` 是文档目录导航。
- `Docs/02-执行/AI执行手册.md` 记录执行前判断、子代理派发、验证和交付规则。
- `Docs/02-执行/工程结构与文档路由.md` 记录 Quick / Project / Team / Review / Agent-Setup 五类路由。
- `.codex/agents/*.toml` 是项目级 custom subagents。
- `Docs/03-团队/开发团队.md` 记录团队结构、协作关系和验收门禁。
- 公共文件只由 Codex 主线程修改。
- 团队成员人名由目标项目里的 AI 初始化时随机生成，模板不固定默认姓名。
- 子代理只处理被派发的专业任务；团队流程结束时必须沉淀团队名册、成员档案和工作记录。
- `read-only` 子代理返回压缩草稿，由 Codex 主线程或 `docs_keeper` 代写记录。
- Codex 主线程等待一波子代理全部完成后，再验收、关闭完成线程、更新公共文档。
- 每次任务完成后，最终回复都要汇报谁干了什么、产出了什么、验证了什么；没有启用子代理时说明由主线程完成。

## 本地模板体检

复制或调整模板后运行：

```bash
python3 .codex/tools/check_template_integrity.py
```

该脚本只做本地模板结构体检，不修改文件、不联网，也不代表 OpenAI/Codex 官方规则校验。需要对齐官方规则时，应让 AI 先查当前 OpenAI Codex 官方文档，再更新模板。

## 当前版本不包含 hooks

当前版本先用 `AGENTS.md`、TOML 指令、团队协议和本地模板体检约束流程。后续可以添加 hooks 做强制路径拦截。
