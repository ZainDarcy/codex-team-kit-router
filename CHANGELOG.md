# Changelog

## Router Initialization Hardening

- Added `.codex/team-kit.toml` for `docs_root`, truth-source paths, public file locks, and install modes.
- Updated initialization flow to probe target projects before copying, avoid `Docs`/`docs` drift, and prevent duplicate project spec/progress truth sources.
- Added minimal, team-ready, and full initialization modes.
- Strengthened Team route gating: Delegation Card first, wait for all subagents, then public file updates.
- Made the integrity check configuration-driven and added checks for `.DS_Store`, duplicate truth sources, path drift, work-log headings, and cross-project absolute paths.

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
