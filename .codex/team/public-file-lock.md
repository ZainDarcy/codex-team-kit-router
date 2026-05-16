# 公共文件写锁

本文件说明公共文件写锁的执行规则。公共文件清单的唯一事实源是 `.codex/team-kit.toml` 的 `[public_files]`，这里不再手工复制完整清单。

## 只能主线程修改的文件

- Codex 主线程在派发前读取 `.codex/team-kit.toml` 的 `[public_files].paths` 和 `[public_files].globs`。
- 主线程把读取结果渲染进 Delegation Card 和子代理 prompt 的“禁止修改路径”。
- 子代理不得修改渲染出的任何公共文件或匹配公共 globs 的文件。
- 如果目标项目初始化时改了 `docs_root` 或真相源路径，必须先更新 `.codex/team-kit.toml`，再渲染公共文件禁止清单。

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
- 不创建或修改 `.codex/team-kit.toml` `[public_files]` 渲染出的公共路径。
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
