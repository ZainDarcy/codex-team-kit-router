# Changelog

## Workflow Context Iteration

- Reduced the daily `Team` route default read set to `Team运行卡.md`, with dispatch/model/public-lock docs loaded only when needed.
- Added `Template-Maintenance` guidance so maintaining this kit source repo does not trigger target-project team initialization.
- Added Router-only trial wording, initialization report requirements, merge decision rules, rollback requirements, and industry-pack choice guidance.
- Clarified read-only / dry-run exceptions so no team records are written when no subagents run and no files change.
- Added template-local checks for initialization config, Team route slimness, Template-Maintenance routing, and public-file source wording.

## Industry Packs And Staging Init

- Added a required staging-based initialization protocol: clone/download the template into a temporary staging directory, merge selected files into the target project, then delete staging.
- Added `.codex/agent-packs/` as the template source for optional industry agents.
- Added the first optional industry pack for games, with `game-basic`, `game-full`, `custom`, and `none` choices.
- Expanded game roles into planning, engineering, art, and validation groups, including combat design, balance design, UI engineering, UI art, and playtest research.
- Updated integrity checks to validate industry pack structure, required industry-pack selection, staging cleanup rules, and public-lock synchronization.

## Router Initialization Hardening

- Added `.codex/team-kit.toml` for `docs_root`, truth-source paths, public file locks, and install modes.
- Updated initialization flow to probe target projects before copying, avoid `Docs`/`docs` drift, and prevent duplicate project spec/progress truth sources.
- Added Router-only trial, team-ready, and full initialization modes.
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
