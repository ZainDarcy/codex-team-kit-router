# codex-team-kit-router

`codex-team-kit-router` 是一套路由式 Codex 子代理团队模板。它的目标不是把一大堆规则一次性塞进主线程，而是让 Codex 先通过瘦 `AGENTS.md` 判断任务类型，再按需读取 `Docs/` 和 `.codex/` 中的具体规则。

这套模板适合已经有项目文档、项目进度、`AGENTS.md` / `AGENT.md` 或 `.codex/` 的项目。接入时必须先放到临时 staging 目录，探测目标项目后按清单合并，完成体检后删除 staging，避免把模板仓库直接塞进项目根目录。

## 30 秒接入

1. 复制仓库地址：`https://github.com/ZainDarcy/codex-team-kit-router`
2. 把下方“推荐接入方式”里的 prompt 发给目标项目里的 AI，不要自己在终端把仓库直接 clone 到项目根目录。
3. 等 AI 给出初始化完成报告，检查：staging 已删除、团队名册和成员档案已创建、行业包选择已说明、rollback 入口已保留。

## 一句话理解

- `AGENTS.md`：Codex 入口路由器，只放最短硬规则。
- `Docs/`：项目文档、团队说明、初始化说明、成员档案和工作记录模板。
- `.codex/`：Codex 运行配置、agent TOML、行业扩展包、派发协议和体检脚本。
- `.codex/agents/`：已经启用的 agent 定义。
- `.codex/agent-packs/`：可选行业扩展包模板源，初始化选择后才复制到 `.codex/agents/`。

## 推荐接入方式

把下面这段发给目标项目里的 AI：

```text
请参考并接入这个 Codex 团队模板：
https://github.com/ZainDarcy/codex-team-kit-router

要求：
1. 不要把模板仓库直接拉到项目根目录；先新建临时 staging 目录拉取模板，优先放在项目根目录外。
2. 先探测目标项目已有 AGENTS.md、AGENT.md、docs/Docs、项目规范、项目进度和 .codex/，不要直接覆盖。
3. 在 .codex/team-kit.toml 里确定 docs_root、项目规范、项目进度、团队目录、公共文件清单和 staging 策略。
4. 选择初始化模式；默认用团队就绪模式。Router-only 试接入不算团队初始化完成。
5. 必须选择行业扩展包：none、game-basic、game-full 或 custom；不要默认偷偷加入。
6. 按我的项目语言习惯随机给团队成员起真实人名，并初始化团队名册和成员档案。
7. 按合并清单把需要的文件融入项目，运行模板体检，删除 staging 目录，再汇报真相源、改动文件、未生成/未迁移内容和 staging 清理结果。
```

初始化完成后，普通任务可以直接说：

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

什么时候不用团队流程：

- 小问答、小检查、小修复：用轻量模式。
- 只想要方案：用“只规划分工，不执行”。
- 跨模块、高风险、需要审查或并行工作：再用团队流程。

## 工作流程总览

```text
用户需求
  -> AGENTS.md 判断路由
  -> 按路由读取 Docs/ 和 .codex/team/ 中的必要文件
  -> 如需日常团队流程，读取 Team 运行卡；如团队未初始化，切到 Team-Init
  -> 输出 Delegation Card
  -> 派发子代理，子代理只拿压缩上下文包
  -> 等待本波子代理全部完成
  -> 主线程整合、验证、更新公共文件
  -> 落盘本波工作记录，按参与者更新团队名册，必要时更新成员档案
  -> 向用户汇报谁做了什么、产出了什么、验证了什么
```

## 非侵入式 Staging 接入

接入已有项目时，模板仓库只能作为临时来源，不能成为目标项目的一部分。

必须遵守：

- 禁止把 `codex-team-kit-router/` 直接 clone 到目标项目根目录并长期保留。
- 禁止在目标项目根目录做整目录覆盖式复制。
- AI 必须先在 staging 目录中读取模板、探测目标项目、生成合并清单。
- staging 优先放在项目根目录外。
- 如果只能临时放在项目内，使用 `_codex-team-kit-router-staging/`，写入 `.gitignore`，完成后删除。
- 合并到目标项目时，只落盘被选择的文件和被选择的行业扩展 agents。
- 完成后必须删除 staging；删除失败时，最终汇报必须列出残留路径和原因。

## 初始化模式

| 模式 | 适合场景 | 会生成什么 |
| --- | --- | --- |
| Router-only 试接入 | 只想先接入 Router 和基础规则，不算团队初始化完成 | `AGENTS.md`、核心 `.codex/`、公共写锁、派发协议、体检脚本；首次 Team 路由前必须再补团队档案 |
| 团队就绪模式 | 推荐默认，准备正常使用团队流程 | Router 基础内容，加团队名册和核心 agent 成员档案；不创建虚假的初始工作记录 |
| 完整模式 | 长期项目，需要完整团队沉淀 | 团队就绪模式内容，加交付模板和完整团队文档结构 |

初始化报告必须说明采用哪种模式。

## 行业扩展包

行业扩展包是可选的。初始化时必须明确选择，不允许默认偷偷加入。

当前选择项：

| 选择 | 含义 |
| --- | --- |
| `none` | 非垂直项目或暂不需要行业专家时使用 |
| `game-basic` | 游戏原型、早期玩法验证时推荐；加入 `game_designer`、`gameplay_engineer`、`ui_artist`、`playtest_researcher` |
| `game-full` | 长期游戏项目推荐；加入策划、程序、美术、验证全部分组 |
| `custom` | 已明确只需要某些岗位时使用，例如只加战斗策划、数值策划和 UI |

游戏行业包分组：

| 分组 | Agents | 职责 |
| --- | --- | --- |
| 策划 | `game_designer`、`combat_designer`、`balance_designer`、`level_designer` | 核心玩法、战斗、数值、关卡 |
| 程序 | `gameplay_engineer`、`ui_engineer` | 玩法系统、UI/HUD、运行时实现 |
| 美术 | `game_art_director`、`ui_artist`、`technical_artist` | 美术方向、UI 视觉、资产接入、技术美术 |
| 验证 | `playtest_researcher` | 可玩性、手感、节奏、玩家反馈 |

未选择的扩展包只保留在 `.codex/agent-packs/` 作为模板源，不进入 `.codex/agents/`、团队名册或成员档案。

## 路由类型

| 路由 | 适用场景 | 主要读取 |
| --- | --- | --- |
| `Quick` | 简单问答、小检查、无需改动 | `AGENTS.md` 和用户点名文件 |
| `Project` | 普通实现、规划、局部修复、文档更新 | 项目规范、项目进度、AI 执行手册 |
| `Team` | 已初始化项目的日常团队流程、子代理、并行 agent | Team 运行卡，再按卡片追加调度文件 |
| `Team-Init` | 团队初始化、模板接入、迁移、扩展包选择 | 团队初始化、行业扩展包、开发团队、AI 执行手册、工程结构与文档路由、派发协议 |
| `Review` | 审查、QA、安全、回归、验收 | AI 执行手册、公共写锁、QA 模板 |
| `Agent-Setup` | 搭建或调整团队模板、agent 定义、行业包 | 角色分类、模型路由、公共写锁、agent TOML、行业扩展包 |
| `Template-Maintenance` | 维护本 kit 源仓库、README、体检脚本或模板发布 | `.codex/team-kit.toml`、工程结构与文档路由和相关模板文件 |

## 文件说明

### 根目录

| 文件 | 作用 |
| --- | --- |
| `AGENTS.md` | Codex 的瘦入口。只保留路由表、公共文件写锁摘要、子代理触发门槛和最终交付要求 |
| `README.md` | 面向人类使用者的总说明，解释接入方式、目录职责和工作流程 |
| `CHANGELOG.md` | 模板变更记录 |
| `.gitignore` | 忽略 `.DS_Store`、缓存、依赖、临时 staging 目录等 |

### `Docs/`

`Docs/` 是文档层，给人和 Codex 主线程按需阅读，也保存团队沉淀记录。

| 路径 | 作用 |
| --- | --- |
| `Docs/README.md` | `Docs/` 导航，说明文档分层和读取原则 |
| `Docs/01-项目/项目规范.md` | 目标项目的稳定规范模板，记录长期不频繁变化的约束 |
| `Docs/01-项目/项目进度.md` | 目标项目的动态进度模板，记录当前状态、已完成事项、阻塞和下一步 |
| `Docs/02-执行/AI执行手册.md` | 主线程执行流程，包含执行前判断、何时问用户、子代理派发、验证和最终汇报 |
| `Docs/02-执行/工程结构与文档路由.md` | Quick / Project / Team / Team-Init / Review / Agent-Setup 路由的文档导航 |
| `Docs/02-执行/Team运行卡.md` | 已初始化项目的日常 Team 轻量运行规则，避免每次读取初始化和迁移文档 |
| `Docs/03-团队/开发团队.md` | 团队结构、默认核心小队、行业扩展选择、执行流程、验收门禁和团队沉淀规则 |
| `Docs/03-团队/行业扩展包/README.md` | 行业扩展包说明，当前包含游戏行业包和选择方式 |

### `Docs/03-团队/Agents/`

这里保存团队初始化和团队沉淀，不保存真正的 agent TOML 配置。

| 路径 | 作用 |
| --- | --- |
| `Docs/03-团队/Agents/团队初始化.md` | 初始化协议。规定 staging 接入、目标项目探测、初始化模式、行业扩展包选择、随机起名和建档 |
| `Docs/03-团队/Agents/团队名册.md` | 团队成员轻量索引。模板内是 `pending`，目标项目初始化后由 AI 填入真实随机人名 |
| `Docs/03-团队/Agents/成员档案/_成员档案模板.md` | 成员档案模板。初始化时为每个启用 agent 生成具体档案 |
| `Docs/03-团队/Agents/工作记录/_工作记录模板.md` | 工作记录模板。每次 Team 路由或启用子代理后要落盘记录 |
| `Docs/03-团队/Agents/交付模板/策划交付模板.md` | 策划类 agent 的交付结构 |
| `Docs/03-团队/Agents/交付模板/程序交付模板.md` | 程序类 agent 的交付结构 |
| `Docs/03-团队/Agents/交付模板/设计交付模板.md` | 设计/UI/体验类 agent 的交付结构 |
| `Docs/03-团队/Agents/交付模板/QA验收模板.md` | QA / review 类 agent 的验收结构 |
| `Docs/03-团队/Agents/交付模板/研究分析模板.md` | 调研/研究类 agent 的分析结构 |

### `.codex/`

`.codex/` 是 Codex 运行配置层，给主线程和子代理系统使用。

| 路径 | 作用 |
| --- | --- |
| `.codex/config.toml` | 本地 agent 并发和深度配置，例如 `max_threads`、`max_depth` |
| `.codex/team-kit.toml` | 模板接入配置源，记录 `docs_root`、项目规范路径、项目进度路径、公共文件清单、staging 策略和行业包选择机制 |
| `.codex/tools/check_template_integrity.py` | 本地体检脚本。检查模板结构、路由、公共写锁、`.DS_Store`、staging 规则和行业扩展包结构 |

### `.codex/agents/`

这里是默认启用的核心 agent TOML。复制到目标项目后，这些 agent 会作为核心小队候选。

| 文件 | 作用 |
| --- | --- |
| `producer.toml` | 总目标、范围、价值和最终验收 |
| `project-manager.toml` | 任务拆解、依赖、进度、风险和席位管理 |
| `product-strategist.toml` | 用户目标、产品方案、场景和验收口径 |
| `tech-architect.toml` | 架构、技术方案、风险和工程边界 |
| `ux-designer.toml` | 信息架构、流程和界面体验 |
| `implementation-engineer.toml` | 受控范围内的代码实现 |
| `qa-reviewer.toml` | 测试、审查、回归风险和验收结论 |
| `docs-keeper.toml` | 文档草稿、工作记录和团队知识沉淀 |
| `researcher.toml` | 资料、竞品、代码映射和证据收集 |

### `.codex/agent-packs/`

这里是可选行业扩展包模板源。它们不会默认生效。

| 路径 | 作用 |
| --- | --- |
| `.codex/agent-packs/README.md` | 行业扩展包通用规则 |
| `.codex/agent-packs/game/README.md` | 游戏行业包说明 |
| `.codex/agent-packs/game/pack.toml` | 游戏包元信息和选择项 |
| `.codex/agent-packs/game/*.toml` | 游戏行业可选 agents。选择 `game-basic`、`game-full` 或 `custom` 后才复制到 `.codex/agents/` |

### `.codex/team/`

这里是团队调度协议层，给主线程和子代理派发时引用。

| 文件 | 作用 |
| --- | --- |
| `dispatch-protocol.md` | 子代理派发协议，包含 Delegation Card、压缩上下文包、等待和关闭规则 |
| `model-routing.md` | 不同任务类型的推荐模型和 reasoning 策略 |
| `public-file-lock.md` | 公共文件写锁，规定哪些文件只能由主线程修改 |
| `role-taxonomy.md` | 核心角色和行业扩展角色分类 |
| `spawn-prompt-templates.md` | 派发子代理时可复用的 prompt 模板 |

## 团队任务必须产出什么

每次走 `Team` 路由或启用任何子代理，主线程最终回复前必须确认：

- 本波工作记录已按模板落盘，并逐一列出参与者、产出和验证。
- `Docs/03-团队/Agents/团队名册.md` 已按参与者更新最近任务和任务次数。
- 对应成员档案仅在新增可复用经验时创建或更新。
- 所有本波子代理状态已记录为 completed/closed，或说明例外原因。
- 最终回复说明谁干了什么、产出了什么、验证了什么、哪些建议被采纳。

如果本轮没有启用子代理，也要说明原因，例如任务较小、用户未授权或关键路径更适合主线程完成。

## 本地体检

复制、初始化或调整模板后运行：

```bash
python3 .codex/tools/check_template_integrity.py
```

该脚本只做本地模板结构体检，不修改文件、不联网，也不代表 OpenAI/Codex 官方规则校验。它会检查路由、链接、`.DS_Store`、行业包选择值和部分运行态文档体量预算，但不会精确测量真实 prompt token。需要确认当前官方行为时，应让 AI 先查当前 OpenAI Codex 官方文档，再更新模板。

## 维护原则

- 改入口路由：优先改 `AGENTS.md` 和 `Docs/02-执行/工程结构与文档路由.md`。
- 改执行流程：优先改 `Docs/02-执行/AI执行手册.md`。
- 改团队结构：优先改 `Docs/03-团队/开发团队.md` 和 `.codex/agents/*.toml`。
- 改行业扩展包：优先改 `.codex/agent-packs/{industry}/` 和 `Docs/03-团队/行业扩展包/README.md`。
- 改公共写锁：同步 `.codex/team/public-file-lock.md`、`AGENTS.md`、`.codex/team/spawn-prompt-templates.md` 和相关 agent TOML。
- 改完模板结构后，必须运行本地体检。

## 当前版本不包含 hooks

当前版本先用 `AGENTS.md`、TOML 指令、团队协议和本地体检脚本约束流程。后续如果要加入 hooks 或自动拦截，应作为单独版本设计，并先确认不会过度侵入目标项目。
