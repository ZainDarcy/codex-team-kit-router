# Changelog

## Workflow Context Iteration

- Added a compact medium/large iteration planning gate: scope first, explicit approval, then `pre-implementation` before runtime writes.
- Kept the planning gate in existing route and execution docs, with no project-specific examples or extra rule files.
- Clarified that medium/large work enters `Team + Implementation-Plan` automatically, and `pre-implementation` now requires approved plans to record Team-route evidence.
- Added tree-style and Mermaid workflow views to make routing, initialization, and Team execution easier to inspect visually.
- Added `game-pack-v2` planning scaffolds: scenario matrix, game task dispatch templates, playtest evidence contract, and safer public-file source-of-truth guidance.
- Slimmed README, AI execution, dispatch, and game prompt templates to reduce default context load and added local line-budget checks for key runtime docs.
- Added Team Assignment Map as a required pre-dispatch identity gate so runtime threads bind to stable team members before spawning.
- Added reinitialization / upgrade guidance that preserves existing member identities, history, and work logs while applying newer template rules.
- Moved game-specific dispatch wording out of the global prompt template and into the game pack, reducing non-game context pollution.
- Added official `.codex/hooks.json` Codex lifecycle hooks plus `.codex/hooks/` fallback gates for post-init, pre-team-dispatch, and pre-final checks.
- Added a repo-local pre-commit hook that runs the local integrity check and whitespace diff check before template commits.
- Added a repo-local pre-push hook with syntax compilation and `.DS_Store` checks for the final publish gate.
- Reduced the daily `Team` route default read set to `Team运行卡.md`, with dispatch/model/public-lock docs loaded only when needed.
- Kept target-project routes focused on Quick / Project / Team / Team-Init / Review / Agent-Setup; template-source maintenance belongs outside copied target placeholders.
- Added Router-only trial wording, initialization report requirements, merge decision rules, rollback requirements, and industry-pack choice guidance.
- Clarified read-only / dry-run exceptions so no team records are written when no subagents run and no files change.
- Added template-local checks for initialization config, Team route slimness, target-placeholder cleanliness, and public-file source wording.

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
