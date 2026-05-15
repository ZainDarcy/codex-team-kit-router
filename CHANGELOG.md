# Changelog

## Initial Router Release

- Reworked `AGENTS.md` as a Router Only entrypoint.
- Organized `Docs/` into `01-项目/`, `02-执行/`, and `03-团队/`.
- Added `Docs/02-执行/AI执行手册.md` for execution, delegation, verification, and final reporting rules.
- Added `Docs/02-执行/工程结构与文档路由.md` for Quick / Project / Team / Review / Agent-Setup routes.
- Added compressed subagent context and Delegation Card requirements.
- Aligned public file lock rules across `AGENTS.md`, `.codex/team/`, and `.codex/agents/*.toml`.
- Changed read-heavy agents to `read-only`; kept implementation and docs roles write-capable.
- Added local template integrity check at `.codex/tools/check_template_integrity.py`.
- Added concise team contribution reporting after every task.
