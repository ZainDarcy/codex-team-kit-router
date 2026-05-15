# 公共文件写锁

## 只能主线程修改的文件

- `AGENTS.md`
- `Docs/01-项目/项目规范.md`
- `Docs/01-项目/项目进度.md`
- `Docs/03-团队/开发团队.md`
- `Docs/02-执行/AI执行手册.md`
- `Docs/02-执行/工程结构与文档路由.md`
- `.codex/config.toml`
- `.codex/team-kit.toml`
- `.codex/agents/*.toml`
- `.codex/agent-packs/**/*.toml`
- `.codex/agent-packs/**/*.md`
- `.codex/team/*.md`
- `Docs/03-团队/行业扩展包/*.md`

## 子代理可以写的文件

- 主线程明确允许的业务文件。
- 主线程明确指派的 `docs_keeper` 可以更新已初始化的 `Docs/03-团队/Agents/团队名册.md`。
- 主线程明确指派的 `docs_keeper` 可以创建或更新 `Docs/03-团队/Agents/成员档案/*.md`。
- 主线程明确允许的子代理可以写 `Docs/03-团队/Agents/工作记录/*.md` 中自己的工作记录。
- `read-only` 子代理不能写文件，必须返回压缩草稿给主线程或 `docs_keeper`。

## 子代理禁止行为

- 不修改公共文件。
- 不修改其他子代理的工作记录。
- 不修改其他子代理的成员档案。
- 不创建或修改 `.codex/agents/*.toml`。
- 不创建或修改 `.codex/agent-packs/` 中的扩展包模板。
- 不修改 `.codex/config.toml`。
- 不修改 `.codex/team-kit.toml`。
- 不启动下一层子代理。

## 建议回写机制

如果子代理发现公共文件需要更新，在工作记录中写：

```markdown
## 建议回写

- 建议更新文件：
- 建议内容：
- 原因：
- 风险：
```

主线程验收后决定是否采纳。
