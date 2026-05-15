# 角色分类表

## 核心小队

- `producer`：范围、目标、价值和最终验收。
- `project_manager`：任务拆解、依赖、进度、风险和席位管理。
- `product_strategist`：需求、用户、产品方案和验收口径。
- `tech_architect`：架构、技术方案、风险和工程边界。
- `ux_designer`：信息架构、流程、界面体验。
- `implementation_engineer`：受控代码实现。
- `qa_reviewer`：测试、审查、验收和风险报告。
- `docs_keeper`：文档草稿、沉淀、建议回写。
- `researcher`：代码/资料/竞品/技术文档探索。

## 领域扩展

行业扩展优先做成 `.codex/agent-packs/{industry}/` 下的可选包，初始化时选择后再复制到 `.codex/agents/`。不要把所有行业 agents 默认塞进每个项目。

| 领域 | 推荐新增角色 |
| --- | --- |
| 游戏策划 | game_designer, combat_designer, balance_designer, level_designer |
| 游戏程序 | gameplay_engineer, ui_engineer |
| 游戏美术 | game_art_director, ui_artist, technical_artist |
| 游戏验证 | playtest_researcher |
| Web/SaaS | frontend_engineer, backend_engineer, devops_engineer, data_analyst |
| App | mobile_engineer, release_manager, platform_integrator |
| AI/Data | data_engineer, ml_engineer, evaluation_engineer, mlops_engineer |
| 内容 | editor, visual_designer, content_ops, review_moderator |

## 添加新角色规则

- 先确认是否真有重复需求。
- 新角色必须有清晰边界。
- 新角色 TOML 必须禁止修改公共文件。
- 新角色必须写工作记录。
- 新行业角色先放入扩展包模板源；只有初始化明确选择后，才进入 `.codex/agents/`、团队名册和成员档案。
