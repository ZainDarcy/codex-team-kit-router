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

