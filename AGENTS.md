# Codex 项目团队入口（Router Only）

本文件是 repo-local Codex 团队模板的瘦入口。它只保留最高优先级规则和文档路由，避免把所有团队规范常驻塞进主线程上下文。

## 常驻规则

- 先判断任务路由，再按需读取文档；不要在每个任务开始时一次性读取全部 `Docs/` 和 `.codex/team/`。
- 目标项目的文档根目录、真相源和公共文件清单以 `.codex/team-kit.toml` 为准；不要混写 `Docs/` 和 `docs/`。
- 用户明确要求“只规划”“只测评”“不改代码”时，不得擅自实现。
- 只有用户明确要求“子代理”“并行 agent”“团队流程”或“允许使用子代理”时，主线程才派发子代理。
- 主线程负责需求理解、路由选择、子代理派发、结果整合、公共文件更新和最终交付。
- 子代理只处理被派发的局部任务，不修改公共文件，不启动下一层子代理。
- 修改前列出预计涉及文件；完成后列出实际涉及文件和验证情况。

## 路由表

| 路由 | 适用场景 | 按需读取 |
| --- | --- | --- |
| `Quick` | 简单问答、小范围检查、无需改动的快速判断 | 本文件和用户点名文件 |
| `Project` | 普通规划、实现、文档更新、局部修复 | `Docs/01-项目/项目规范.md`、`Docs/01-项目/项目进度.md`、`Docs/02-执行/AI执行手册.md` |
| `Team` | 用户明确要求团队流程、子代理、并行 agent | `Docs/03-团队/Agents/团队初始化.md`、`Docs/03-团队/开发团队.md`、`Docs/02-执行/AI执行手册.md`、`.codex/team/dispatch-protocol.md`、`.codex/team/model-routing.md`、`.codex/team/public-file-lock.md` |
| `Review` | 审查、QA、安全、回归、验收 | `Docs/02-执行/AI执行手册.md`、`.codex/team/public-file-lock.md`、`Docs/03-团队/Agents/交付模板/QA验收模板.md` |
| `Agent-Setup` | 搭建、扩展、调整团队模板或 agent 定义 | `Docs/03-团队/开发团队.md`、`Docs/02-执行/工程结构与文档路由.md`、`.codex/team/role-taxonomy.md`、`.codex/team/model-routing.md`、`.codex/team/public-file-lock.md`、`.codex/team/spawn-prompt-templates.md`、`.codex/agents/*.toml` |

## 公共文件写锁

以下文件只能由 Codex 主线程修改：

- `AGENTS.md`
- `Docs/01-项目/项目规范.md`
- `Docs/01-项目/项目进度.md`
- `Docs/03-团队/开发团队.md`
- `Docs/02-执行/AI执行手册.md`
- `Docs/02-执行/工程结构与文档路由.md`
- `.codex/config.toml`
- `.codex/team-kit.toml`
- `.codex/agents/*.toml`
- `.codex/team/*.md`

子代理如需更新公共文件，只能在结果或工作记录中提出“建议回写”，由主线程验收后决定是否采纳。

## 子代理触发门槛

- 不为简单任务启动子代理。
- 不把主线程下一步立即需要的关键路径交给子代理。
- 优先把探索、代码映射、审查、验证、资料整理等读重任务交给子代理。
- 写入型子代理必须有互不重叠的允许路径和明确验收标准。
- 派发前必须按 `.codex/team/dispatch-protocol.md` 写清 Delegation Card。

## 验证与交付

- 任务完成前，运行与改动范围匹配的测试、检查或人工验证。
- 如果验证不能运行，说明原因、影响和剩余风险。
- 最终回复必须说明：改了什么、涉及哪些文件、验证了什么、没有验证什么、还有什么风险。
- 最终回复必须包含团队贡献汇报：谁干了什么、产出了什么、哪些验证或建议进入最终交付；没有启用子代理时，也要说明由 Codex 主线程完成。
