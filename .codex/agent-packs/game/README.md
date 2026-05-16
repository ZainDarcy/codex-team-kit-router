# 游戏行业扩展包

本扩展包用于游戏项目。初始化时必须显式选择：

- `none`：不加入游戏行业 agents。
- `game-basic`：加入基础游戏小队，适合早期原型和轻量迭代。
- `game-full`：加入完整游戏小队，适合长期项目、复杂系统或多工种协作。
- `custom`：只选择需要的分组或单个 agent。

## 分组

| 分组 | Agents | 适用场景 |
| --- | --- | --- |
| 策划 | `game_designer`, `combat_designer`, `balance_designer`, `level_designer` | 核心玩法、战斗、数值、关卡节奏 |
| 程序 | `gameplay_engineer`, `ui_engineer` | 玩法系统、交互、HUD、菜单和运行时实现 |
| 美术 | `game_art_director`, `ui_artist`, `technical_artist` | 美术风格、UI 视觉、资产接入和技术美术 |
| 验证 | `playtest_researcher` | 可玩性、手感、节奏和玩家反馈 |

## 推荐选择

- `game-basic`：`game_designer`, `gameplay_engineer`, `ui_artist`, `playtest_researcher`
- `game-full`：本目录所有 agents

初始化选择后，主线程应把被选中的 `.toml` 复制到 `.codex/agents/`，并为每个新增 agent 创建成员档案。

## 任务场景矩阵

| 场景 | 推荐选择 | 建议角色 | 交付重点 |
| --- | --- | --- | --- |
| 早期玩法原型 | `game-basic` | `game_designer`, `gameplay_engineer`, `ui_artist`, `playtest_researcher` | 核心循环、最小可玩增量、首屏反馈、试玩证据 |
| UI/HUD 改造 | `game-basic` 或 `custom` | `ui_artist`, `ui_engineer`, `playtest_researcher` | HUD 遮挡、可读性、输入反馈、目标视口验证 |
| 战斗/关卡迭代 | `game-full` 或 `custom` | `combat_designer`, `level_designer`, `balance_designer`, `playtest_researcher` | 战斗节奏、关卡路径、数值假设、试玩风险 |
| 长期 GDD 项目 | `game-full` | 策划、程序、美术、验证全部分组 | GDD 拆解、里程碑、制作风险、验收口径 |
| Unity/Cocos 引擎迁移评估 | `custom` | `gameplay_engineer`, `technical_artist`, `game_designer` | 代码优先/编辑器依赖、资源管线、迁移收益和代价 |
| LLM NPC / 叙事系统评估 | `custom` | `game_designer`, `researcher`, `gameplay_engineer` | 是否服务核心循环、最小验证方案、成本和降级风险 |

## 通用输出格式

游戏 agent 默认按以下结构返回：

- 确认目标
- 当前证据
- 建议改动
- 验收标准
- 风险和未确认项

## 派发模板索引

- 玩法原型派发模板：`game_designer`, `gameplay_engineer`, `ui_artist`, `playtest_researcher`；交付核心循环、最小可玩增量和试玩风险。
- 数值平衡派发模板：`balance_designer`，必要时追加战斗/关卡/试玩角色；交付数值证据、调参建议、指标和回滚方式。
- UI/HUD 派发模板：`ui_artist`, `ui_engineer`, `playtest_researcher`；交付遮挡、可读性、目标视口和残余风险。
- 浏览器试玩验收模板：`playtest_researcher`；交付启动结果、可试玩 URL、核心循环、输入反馈、HUD 遮挡、结果反馈、截图或浏览器证据。
- Unity/Cocos 引擎迁移评估模板：`gameplay_engineer`, `technical_artist`, `game_designer`；交付代码优先、编辑器依赖、资源管线、迁移收益和代价。
- LLM NPC / 叙事系统评估模板：`game_designer`, `researcher`, `gameplay_engineer`；交付适用结论、最小验证、成本和降级风险。

## 试玩验收契约

`playtest_researcher` 负责把 QA 从文字审查推进到试玩体验验收。Web 游戏或可运行原型任务中，交付必须覆盖：

- 启动结果
- 可试玩 URL
- 核心循环判断
- 输入反馈
- HUD 是否遮挡玩法区域
- 失败、胜利、结算反馈
- 截图或浏览器检查证据
- 未覆盖设备和浏览器

如果无法启动或无法打开浏览器，也必须说明阻塞原因和缺失证据，不得把未验证内容写成已通过。
