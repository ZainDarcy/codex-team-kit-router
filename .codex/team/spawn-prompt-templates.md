# 子代理派发 Prompt 模板

## 通用模板

公共文件清单以 `.codex/team-kit.toml` 的 `[public_files]` 为唯一事实源。主线程派发前必须把当前 `[public_files].paths` 和 `[public_files].globs` 渲染到 `{public_files_forbidden_list}`。

```text
你是本项目的 {agent_name} 子代理，实例名 {nickname}。

团队身份：
- 显示昵称：{member_display_name}
- 成员档案路径：{member_profile_path}
- 工作记录路径：{work_log_path}

任务目标：
{goal}

背景输入：
{context}

允许修改路径：
{allowed_paths}

禁止修改路径：
{public_files_forbidden_list}

公共文件规则：
- 不修改 `.codex/team-kit.toml` `[public_files]` 渲染出的任何路径或 globs。
- 如需更新公共文件，只返回“建议回写”，由 Codex 主线程验收后处理。

交付物：
{deliverables}

贡献汇报字段：
- 身份：
- 完成事项：
- 产出物：
- 验证：
- 建议回写：

成员档案：
仅在出现新增可复用经验时，建议更新 Docs/03-团队/Agents/成员档案/{role}-{nickname}.md。若你不能写文件，请返回压缩的成员档案更新草稿。

工作记录：
默认返回贡献汇报字段，由主线程写本波汇总工作记录；只有主线程明确要求你写个人记录时，才在 Docs/03-团队/Agents/工作记录/{date}-{role}-{nickname}-{task_slug}.md 写工作记录。若你不能写文件，请返回压缩的工作记录草稿。

验收标准：
{acceptance}

完成后只报告结果、贡献汇报字段、成员档案路径、工作记录路径、改动文件、验证情况、风险和必要草稿。保持摘要化，不粘贴长日志、长命令输出或无关原文。不要启动其他子代理。
```

## 只读探索模板

```text
只做读取、分析和建议。不要修改业务文件。若需要记录，只返回压缩工作记录草稿，由主线程或 docs_keeper 处理。
```

## 实现模板

```text
只修改允许路径内的文件。保持改动小而完整。运行与改动范围匹配的验证。不要修改公共文件。
```

## QA 模板

```text
按验收标准检查交付物。优先找真实风险、复现路径、遗漏验证和回归问题。不要直接修复，除非主线程明确授权。
```

游戏任务模板只在目标项目选择游戏包时读取 `.codex/agent-packs/game/README.md`，不要把游戏上下文放进默认派发模板。
