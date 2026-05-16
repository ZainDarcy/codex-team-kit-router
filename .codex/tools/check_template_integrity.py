#!/usr/bin/env python3
"""Check local template integrity for codex-team-kit-router.

This is not an official Codex/OpenAI rules validator. It does not access the
network, and it does not try to prove that current upstream Codex behavior is
unchanged. It only checks this kit's local structure and conventions.

When official alignment matters, ask AI to check the current OpenAI Codex docs
before changing this template.
"""

from __future__ import annotations

import re
import sys
import ast
import json
import os
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".codex/team-kit.toml"

ROUTES = ["Quick", "Project", "Team", "Team-Init", "Review", "Agent-Setup"]

DISPATCH_PHRASES = [
    "Delegation Card",
    "Team Assignment Map",
    "运行时线程 / 系统 nickname",
    "压缩上下文包",
    "用户是否明确授权子代理",
    "主线程保留的关键路径",
    "所有本波子代理状态",
    "不超过 6 个文件引用、12 条证据要点和 4000 字",
]

WRITING_AGENTS = {
    "implementation_engineer",
    "docs_keeper",
    "gameplay_engineer",
    "ui_engineer",
    "technical_artist",
}

GAME_PACK_AGENTS = [
    "balance-designer.toml",
    "combat-designer.toml",
    "game-art-director.toml",
    "game-designer.toml",
    "gameplay-engineer.toml",
    "level-designer.toml",
    "playtest-researcher.toml",
    "technical-artist.toml",
    "ui-artist.toml",
    "ui-engineer.toml",
]

LOCAL_AGENT_REQUIRED_FIELDS = [
    "name",
    "description",
    "developer_instructions",
]

PUBLIC_AGENT_PHRASES = [
    "Do not modify public files",
    ".codex/team-kit.toml [public_files]",
    "source of truth",
    "Do not spawn subagents",
    "Docs/03-团队/Agents/工作记录",
]

PUBLIC_LOCK_DOC_PHRASES = [
    "唯一事实源",
    ".codex/team-kit.toml",
    "[public_files]",
    "渲染",
]

PROMPT_TEMPLATE_PHRASES = [
    "{public_files_forbidden_list}",
    "{member_display_name}",
    "{member_profile_path}",
    "{work_log_path}",
    "[public_files].paths",
    "[public_files].globs",
    "建议回写",
]

GAME_README_PHRASES = [
    "任务场景矩阵",
    "早期玩法原型",
    "UI/HUD 改造",
    "Unity/Cocos 引擎迁移评估",
    "LLM NPC",
    "派发模板索引",
    "数值平衡派发模板",
    "浏览器试玩验收模板",
    "试玩验收契约",
]

PLAYTEST_CONTRACT_PHRASES = [
    "launch result",
    "playable URL",
    "core loop judgment",
    "input feedback",
    "HUD blocks the play area",
    "failure/win/results feedback",
    "screenshot or browser-check evidence",
    "uncovered devices/browsers",
]

WORK_LOG_HEADINGS = [
    "日期",
    "Agent 岗位",
    "显示昵称",
    "参与者贡献",
    "输入材料",
    "完成内容",
    "改动文件",
    "验证记录",
    "发现的问题",
    "建议回写",
    "下一次更懂项目的地方",
]

EXPECTED_GAME_CHOICES = {"none", "game-basic", "game-full", "custom"}

CHOICE_KEY_DOCS = [
    "README.md",
    "CHANGELOG.md",
    "Docs/02-执行/AI执行手册.md",
    "Docs/03-团队/开发团队.md",
    "Docs/03-团队/行业扩展包/README.md",
]

PROJECT_PROGRESS_FORBIDDEN_PHRASES = [
    "模板维护状态",
    "Router 基础版",
    "Staging 接入",
    "Team 轻量化",
    "game-pack-v2",
    "公共写锁事实源",
    "2026-05-15",
    "2026-05-16",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def parse_toml_subset(text: str) -> dict:
    """Parse the small TOML subset used by .codex/team-kit.toml.

    This avoids making the integrity check depend on Python 3.11+ or external
    packages. Supported forms are sections, quoted strings, integers, booleans,
    and multi-line arrays of quoted strings.
    """

    data: dict[str, dict] = {}
    current: dict | None = None
    pending_array: tuple[dict, str, list[str]] | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if pending_array:
            target, key, values = pending_array
            if line.startswith("]"):
                target[key] = values
                pending_array = None
                continue
            match = re.match(r'(".*")\s*,?$', line)
            if not match:
                fail(f"Unsupported array item in .codex/team-kit.toml: {raw_line}")
            values.append(ast.literal_eval(match.group(1)))
            continue

        section = re.match(r"^\[([A-Za-z0-9_-]+)\]$", line)
        if section:
            current = data.setdefault(section.group(1), {})
            continue

        if current is None:
            fail("Key found before any section in .codex/team-kit.toml")

        pair = re.match(r"^([A-Za-z0-9_-]+)\s*=\s*(.*)$", line)
        if not pair:
            fail(f"Unsupported line in .codex/team-kit.toml: {raw_line}")
        key, value = pair.group(1), pair.group(2).strip()

        if value == "[":
            pending_array = (current, key, [])
            continue
        if value.startswith('"') and value.endswith('"'):
            current[key] = ast.literal_eval(value)
            continue
        if value in {"true", "false"}:
            current[key] = value == "true"
            continue
        if re.match(r"^-?\d+$", value):
            current[key] = int(value)
            continue
        fail(f"Unsupported value in .codex/team-kit.toml: {raw_line}")

    if pending_array:
        fail("Unclosed array in .codex/team-kit.toml")

    return data


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        fail("Missing .codex/team-kit.toml")
    return parse_toml_subset(CONFIG_PATH.read_text(encoding="utf-8"))


CONFIG = load_config()


def cfg(section: str, key: str, default=None):
    return CONFIG.get(section, {}).get(key, default)


def cfg_path(key: str) -> str:
    value = cfg("paths", key)
    if not isinstance(value, str) or not value:
        fail(f".codex/team-kit.toml missing [paths].{key}")
    return value


def configured_public_files() -> list[str]:
    public = CONFIG.get("public_files", {})
    paths = public.get("paths", [])
    globs = public.get("globs", [])
    if not isinstance(paths, list) or not isinstance(globs, list):
        fail(".codex/team-kit.toml [public_files] paths/globs must be lists")
    return [str(path) for path in [*paths, *globs]]


def check_initialization_config() -> None:
    for key in [
        "project_entry",
        "legacy_agent_doc",
        "docs_root",
        "project_spec",
        "project_progress",
        "ai_workflow",
        "implementation_plan_root",
        "team_dir",
        "init_report_dir",
    ]:
        cfg_path(key)
    if cfg("initialization", "state") != "template-source":
        fail(".codex/team-kit.toml [initialization].state must be template-source in the template repo")
    if cfg("initialization", "install_mode") != "template-source":
        fail(".codex/team-kit.toml [initialization].install_mode must be template-source in the template repo")
    if cfg("initialization", "template_version_applied") != "":
        fail(".codex/team-kit.toml [initialization].template_version_applied must be blank in the template repo")
    if cfg("initialization", "team_ready_required_for_team_route") is not True:
        fail(".codex/team-kit.toml must require team-ready state before Team route")
    if cfg("initialization", "status_file") != cfg_path("team_roster"):
        fail(".codex/team-kit.toml [initialization].status_file must match team_roster")
    if cfg("planning_gate", "required_for_medium_large") is not True:
        fail(".codex/team-kit.toml must enable the medium/large planning gate")
    values = cfg("planning_gate", "approval_status_values", [])
    if not isinstance(values, list) or "approved" not in values:
        fail(".codex/team-kit.toml planning gate must include approval_status_values with approved")
    ready_values = cfg("planning_gate", "implementation_ready_status_values", [])
    if not isinstance(ready_values, list) or "approved" not in ready_values:
        fail(".codex/team-kit.toml planning gate must include implementation_ready_status_values with approved")


def required_paths() -> list[str]:
    required = [
        "AGENTS.md",
        "README.md",
        "Docs/README.md",
        ".codex/hooks.json",
        ".codex/hooks/codex_workflow_hook.py",
        ".codex/hooks/post-init",
        ".codex/hooks/pre-final",
        ".codex/hooks/pre-implementation",
        ".codex/hooks/pre-team-dispatch",
        ".githooks/pre-commit",
        ".githooks/pre-push",
        ".codex/config.toml",
        ".codex/team-kit.toml",
        ".codex/tools/check_template_integrity.py",
        ".codex/tools/check_workflow_runtime.py",
        ".codex/team/dispatch-protocol.md",
        ".codex/team/model-routing.md",
        ".codex/team/public-file-lock.md",
        ".codex/team/role-taxonomy.md",
        ".codex/team/spawn-prompt-templates.md",
        ".codex/agent-packs/README.md",
        "Docs/03-团队/行业扩展包/README.md",
        cfg_path("project_spec"),
        cfg_path("project_progress"),
        cfg_path("execution_manual"),
        f"{cfg_path('implementation_plan_root')}/README.md",
        cfg_path("routing_doc"),
        cfg_path("team_run_card"),
        cfg_path("team_doc"),
        cfg_path("team_init"),
        cfg_path("team_roster"),
        cfg_path("member_profile_template"),
        cfg_path("work_log_template"),
    ]

    mode = cfg("kit", "default_install_mode", "team-ready")
    if mode in {"team-ready", "full"}:
        required.append(cfg_path("agent_root"))
    for pack in CONFIG.get("industry_packs", {}).get("available", []):
        required.extend(
            [
                f".codex/agent-packs/{pack}/README.md",
                f".codex/agent-packs/{pack}/pack.toml",
            ]
        )
    if mode == "full":
        required.extend(
            [
                "Docs/03-团队/Agents/交付模板/策划交付模板.md",
                "Docs/03-团队/Agents/交付模板/程序交付模板.md",
                "Docs/03-团队/Agents/交付模板/设计交付模板.md",
                "Docs/03-团队/Agents/交付模板/QA验收模板.md",
                "Docs/03-团队/Agents/交付模板/研究分析模板.md",
            ]
        )
    return required


def check_required_paths() -> None:
    missing = [path for path in required_paths() if not (ROOT / path).exists()]
    if missing:
        fail("Missing required paths: " + ", ".join(missing))


def check_target_project_placeholders() -> None:
    progress_path = ROOT / cfg_path("project_progress")
    progress = progress_path.read_text(encoding="utf-8")
    for phrase in ["目标项目", "待填写", "不记录本模板源仓库的维护历史"]:
        if phrase not in progress:
            fail(f"{cfg_path('project_progress')} must stay a target-project placeholder; missing phrase: {phrase}")
    for phrase in PROJECT_PROGRESS_FORBIDDEN_PHRASES:
        if phrase in progress:
            fail(f"{cfg_path('project_progress')} must not contain template-source progress phrase: {phrase}")

    roster = (ROOT / cfg_path("team_roster")).read_text(encoding="utf-8")
    if "状态：pending" not in roster or "待随机生成" not in roster:
        fail(f"{cfg_path('team_roster')} must stay pending in the template")
    for nickname in ["林知远", "周明衡", "陈思远", "赵明轩", "何子涵", "沈清和", "陆景然"]:
        if nickname in roster:
            fail(f"{cfg_path('team_roster')} must not contain real source-project member: {nickname}")

    member_dir = ROOT / "Docs/03-团队/Agents/成员档案"
    work_log_dir = ROOT / "Docs/03-团队/Agents/工作记录"
    member_files = sorted(path.name for path in member_dir.glob("*.md"))
    work_log_files = sorted(path.name for path in work_log_dir.glob("*.md"))
    if member_files != ["_成员档案模板.md"]:
        fail("Template must not ship initialized member profiles: " + ", ".join(member_files))
    if work_log_files != ["_工作记录模板.md"]:
        fail("Template must not ship real work logs: " + ", ".join(work_log_files))


def check_docs_root_case() -> None:
    docs_root = cfg_path("docs_root")
    if not (ROOT / docs_root).is_dir():
        fail(f"Configured docs_root does not exist: {docs_root}")

    docs_like = sorted(path.name for path in ROOT.iterdir() if path.is_dir() and path.name.lower() == "docs")
    if len(docs_like) > 1:
        fail("Both Docs/docs style directories exist: " + ", ".join(docs_like))
    if docs_like and docs_like[0] != docs_root:
        fail(f"Configured docs_root={docs_root!r} does not match actual directory {docs_like[0]!r}")


def check_truth_sources() -> None:
    truth_sources = CONFIG.get("truth_sources", {})
    for group, candidates in truth_sources.items():
        if not isinstance(candidates, list):
            fail(f".codex/team-kit.toml truth source group must be a list: {group}")
        existing_by_inode: dict[tuple[int, int], list[str]] = {}
        for path in candidates:
            candidate = ROOT / path
            if candidate.exists():
                stat = os.stat(candidate)
                existing_by_inode.setdefault((stat.st_dev, stat.st_ino), []).append(path)
        if len(existing_by_inode) > 1:
            existing = [aliases[0] for aliases in existing_by_inode.values()]
            fail(f"Multiple truth sources for {group}: " + ", ".join(existing))


def check_no_ds_store() -> None:
    matches = sorted(path.relative_to(ROOT) for path in ROOT.rglob(".DS_Store"))
    if matches:
        fail("Template must not contain .DS_Store: " + ", ".join(str(path) for path in matches))


def check_no_forbidden_staging_dirs() -> None:
    forbidden = CONFIG.get("staging", {}).get("forbidden_final_dirs", [])
    if not isinstance(forbidden, list):
        fail(".codex/team-kit.toml [staging].forbidden_final_dirs must be a list")
    matches = []
    for name in forbidden:
        candidate = ROOT / str(name)
        if candidate.exists() and candidate.resolve() != ROOT.resolve():
            matches.append(str(candidate.relative_to(ROOT)))
    if matches:
        fail("Template must not contain leftover staging dirs: " + ", ".join(matches))


def text_files() -> list[Path]:
    skipped_parts = {".git", "__pycache__", "node_modules"}
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or skipped_parts.intersection(path.parts):
            continue
        if path.suffix.lower() in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".tar", ".gz"}:
            continue
        result.append(path)
    return result


def check_no_cross_project_paths() -> None:
    fragments = cfg("checks", "forbidden_absolute_path_fragments", [])
    if not fragments:
        return
    for path in text_files():
        if path == CONFIG_PATH:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for fragment in fragments:
            if fragment and fragment in text:
                fail(f"Found forbidden absolute path fragment in {path.relative_to(ROOT)}: {fragment}")


def check_markdown_links() -> None:
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for md_file in sorted(ROOT.rglob("*.md")):
        if ".git" in md_file.parts:
            continue
        text = md_file.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip()
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            if " " in target:
                target = target.split(" ", 1)[0]
            target = target.strip("<>")
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            if target.startswith("/"):
                fail(f"{md_file.relative_to(ROOT)} contains absolute markdown link: {raw_target}")
            candidate = (md_file.parent / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                fail(f"{md_file.relative_to(ROOT)} links outside template: {raw_target}")
            if not candidate.exists():
                fail(f"{md_file.relative_to(ROOT)} has broken markdown link: {raw_target}")


def check_agents_md_router() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    max_lines = int(cfg("checks", "max_agents_md_lines", 150))
    if line_count > max_lines:
        fail(f"AGENTS.md should stay router-sized, got {line_count} lines")
    team_route_line = next((line for line in text.splitlines() if line.startswith("| `Team` |")), "")
    if cfg_path("team_init") in team_route_line or "行业扩展包/README.md" in team_route_line:
        fail("AGENTS.md Team route must not load initialization or industry-pack docs")
    if ".codex/team/" in team_route_line or "Docs/03-团队/开发团队.md" in team_route_line:
        fail("AGENTS.md Team route should only point to the Team run card by default")
    for route in ROUTES:
        if route not in text:
            fail(f"AGENTS.md missing route: {route}")
    for phrase in ["Router Only", "路由表", "公共文件写锁", "子代理触发门槛", "Team + Implementation-Plan"]:
        if phrase not in text:
            fail(f"AGENTS.md missing router phrase: {phrase}")
    if cfg_path("team_run_card") not in text:
        fail("AGENTS.md Team route must point to the Team run card")
    if cfg_path("team_init") not in text:
        fail("AGENTS.md Team-Init route must point to the team initialization doc")
    team_init_line = next((line for line in text.splitlines() if line.startswith("| `Team-Init` |")), "")
    if ".codex/team-kit.toml" not in team_init_line:
        fail("AGENTS.md Team-Init route must include .codex/team-kit.toml")
    if ".codex/team/dispatch-protocol.md" in team_init_line:
        fail("AGENTS.md Team-Init route should not load dispatch protocol by default")
    old_forced_load = "开始任何需求、实现、调研、评审或文档更新前"
    if old_forced_load in text:
        fail("AGENTS.md still contains the old forced full-context load rule")
    public_lock_section = re.search(r"## 公共文件写锁\n(.*?)\n## ", text, re.DOTALL)
    if public_lock_section:
        for mirror in [".codex/agent-packs/**/*.toml", ".codex/agents/*.toml", "Docs/01-项目/项目规范.md"]:
            if mirror in public_lock_section.group(1):
                fail("AGENTS.md public-lock section should summarize public files instead of mirroring full paths")


def check_config() -> None:
    config = (ROOT / ".codex/config.toml").read_text(encoding="utf-8")
    if "[agents]" not in config:
        fail(".codex/config.toml missing local [agents] section")
    if not re.search(r"max_threads\s*=\s*6", config):
        fail(".codex/config.toml missing local template default max_threads = 6")
    if not re.search(r"max_depth\s*=\s*1", config):
        fail(".codex/config.toml missing local template default max_depth = 1")


def check_local_hooks() -> None:
    pre_commit = (ROOT / ".githooks/pre-commit").read_text(encoding="utf-8")
    for phrase in ["check_template_integrity.py", "git diff --check"]:
        if phrase not in pre_commit:
            fail(f".githooks/pre-commit missing hook command: {phrase}")

    pre_push = (ROOT / ".githooks/pre-push").read_text(encoding="utf-8")
    for phrase in ["check_template_integrity.py", "git diff --check", "PYTHONDONTWRITEBYTECODE", ".DS_Store"]:
        if phrase not in pre_push:
            fail(f".githooks/pre-push missing hook command: {phrase}")
    for hook_path in [ROOT / ".githooks/pre-commit", ROOT / ".githooks/pre-push"]:
        if not os.access(hook_path, os.X_OK):
            fail(f"{hook_path.relative_to(ROOT)} must be executable")

    for hook_name in ["post-init", "pre-final", "pre-implementation", "pre-team-dispatch"]:
        hook_path = ROOT / ".codex/hooks" / hook_name
        text = hook_path.read_text(encoding="utf-8")
        if "check_workflow_runtime.py" not in text or f"--gate {hook_name}" not in text:
            fail(f".codex/hooks/{hook_name} must call check_workflow_runtime.py --gate {hook_name}")
        if not os.access(hook_path, os.X_OK):
            fail(f".codex/hooks/{hook_name} must be executable")


def check_official_codex_hooks() -> None:
    hooks_path = ROOT / ".codex/hooks.json"
    try:
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f".codex/hooks.json is invalid JSON: {exc}")

    hook_map = hooks.get("hooks")
    if not isinstance(hook_map, dict):
        fail(".codex/hooks.json must have a top-level hooks object")

    for event in ["SessionStart", "UserPromptSubmit", "PreToolUse", "PermissionRequest", "PostToolUse", "Stop"]:
        groups = hook_map.get(event)
        if not isinstance(groups, list) or not groups:
            fail(f".codex/hooks.json missing hook event: {event}")
        found_handler = False
        for group in groups:
            if not isinstance(group, dict):
                continue
            for handler in group.get("hooks", []):
                command = handler.get("command", "") if isinstance(handler, dict) else ""
                if "codex_workflow_hook.py" in command and f"--event {event}" in command:
                    found_handler = True
                    if handler.get("type") != "command":
                        fail(f".codex/hooks.json {event} handler must be type=command")
                    if handler.get("timeout") != 30:
                        fail(f".codex/hooks.json {event} handler must use timeout 30")
        if not found_handler:
            fail(f".codex/hooks.json {event} must call codex_workflow_hook.py --event {event}")

    handler_path = ROOT / ".codex/hooks/codex_workflow_hook.py"
    if not os.access(handler_path, os.X_OK):
        fail(".codex/hooks/codex_workflow_hook.py must be executable")
    text = handler_path.read_text(encoding="utf-8")
    for phrase in [
        "hookSpecificOutput",
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PermissionRequest",
        "PostToolUse",
        "Stop",
        "additionalContext",
        "permissionDecision",
        "Team Assignment Map",
        "pre-final",
        "suppressOutput",
    ]:
        if phrase not in text:
            fail(f".codex/hooks/codex_workflow_hook.py missing phrase: {phrase}")


def check_workflow_runtime_checker() -> None:
    text = (ROOT / ".codex/tools/check_workflow_runtime.py").read_text(encoding="utf-8")
    for phrase in [
        "pre-team-dispatch",
        "post-init",
        "pre-final",
        "pre-implementation",
        "planning_gate",
        "implementation_ready_status_values",
        "批准执行",
        "No implementation plan package",
        "Approved implementation plan must record Team route evidence",
        "Team route requires [initialization].state = initialized",
        "Team Assignment Map",
        ".DS_Store",
    ]:
        if phrase not in text:
            fail(f".codex/tools/check_workflow_runtime.py missing phrase: {phrase}")


def check_no_stale_context_rules() -> None:
    stale_phrases = {
        "README.md": ["需要派发：Delegation Card ->"],
        cfg_path("execution_manual"): ["走 `Team` 路由或启用子代理时，必须确认至少一份工作记录"],
        cfg_path("team_doc"): ["Team 任务结束后，在", "走 `Team` 路由或启用子代理时，执行 Team-lite"],
        cfg_path("team_roster"): ["每次走 `Team` 路由或启用任何子代理后"],
        ".codex/team/role-taxonomy.md": ["新角色必须写工作记录"],
        ".codex/team/dispatch-protocol.md": ["不把“写工作记录”当成可选项"],
    }
    for path, phrases in stale_phrases.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase in text:
                fail(f"{path} still contains stale context/team rule: {phrase}")


def check_team_assignment_map_shape() -> None:
    dispatch = (ROOT / ".codex/team/dispatch-protocol.md").read_text(encoding="utf-8")
    for phrase in ["check_template_integrity.py", "git diff --check"]:
        if phrase not in (ROOT / ".githooks/pre-commit").read_text(encoding="utf-8"):
            fail(f".githooks/pre-commit missing hook command: {phrase}")
    assignment_match = re.search(r"## Team Assignment Map\n(.*?)## Delegation Card", dispatch, re.DOTALL)
    if not assignment_match:
        fail(".codex/team/dispatch-protocol.md missing Team Assignment Map block before Delegation Card")
    for phrase in ["agent", "显示昵称", "运行时线程 / 系统 nickname", "成员档案路径", "工作记录路径", "sandbox / 写入权限"]:
        if phrase not in assignment_match.group(1):
            fail(f"Team Assignment Map missing field: {phrase}")


def check_public_lock_source() -> None:
    lock_doc = (ROOT / ".codex/team/public-file-lock.md").read_text(encoding="utf-8")
    prompt_template = (ROOT / ".codex/team/spawn-prompt-templates.md").read_text(encoding="utf-8")
    public_entries = configured_public_files()
    if not public_entries:
        fail(".codex/team-kit.toml [public_files] must not be empty")
    for public_path in CONFIG.get("public_files", {}).get("paths", []):
        if not (ROOT / public_path).exists():
            fail(f".codex/team-kit.toml public file path does not exist: {public_path}")
    for public_glob in CONFIG.get("public_files", {}).get("globs", []):
        if not list(ROOT.glob(public_glob)):
            fail(f".codex/team-kit.toml public file glob matches nothing: {public_glob}")
    for phrase in PUBLIC_LOCK_DOC_PHRASES:
        if phrase not in lock_doc:
            fail(f".codex/team/public-file-lock.md missing source-of-truth phrase: {phrase}")
    for phrase in PROMPT_TEMPLATE_PHRASES:
        if phrase not in prompt_template:
            fail(f".codex/team/spawn-prompt-templates.md missing rendered public-file phrase: {phrase}")
    for old_mirror_path in ["Docs/01-项目/项目规范.md", ".codex/agent-packs/**/*.toml"]:
        if old_mirror_path in lock_doc:
            fail(".codex/team/public-file-lock.md should not mirror full public-file paths; use [public_files]")


def read_toml_string(text: str, field: str) -> str | None:
    triple = re.search(rf'(?m)^{field}\s*=\s*"""(.*?)"""', text, re.DOTALL)
    if triple:
        return triple.group(1)
    single = re.search(rf'(?m)^{field}\s*=\s*"([^"]*)"', text)
    if single:
        return single.group(1)
    return None


def read_pack_choice_keys(pack_toml: Path) -> set[str]:
    text = pack_toml.read_text(encoding="utf-8")
    in_choices = False
    keys: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        section = re.match(r"^\[([A-Za-z0-9_-]+)\]$", line)
        if section:
            in_choices = section.group(1) == "choices"
            continue
        if not in_choices:
            continue
        pair = re.match(r'^([A-Za-z0-9_-]+)\s*=\s*"[^"]*"\s*$', line)
        if not pair:
            fail(f"{pack_toml.relative_to(ROOT)} has invalid [choices] line: {raw_line}")
        keys.add(pair.group(1))
    if not keys:
        fail(f"{pack_toml.relative_to(ROOT)} missing [choices] entries")
    return keys


def ensure_choice_keys_present(text: str, source_path: str, keys: set[str]) -> None:
    for key in sorted(keys):
        if key not in text:
            fail(f"{source_path} missing game pack choice key: {key}")


def check_agent_file(agent_file: Path) -> None:
    text = agent_file.read_text(encoding="utf-8")
    if "localized_nickname" in text:
        fail(f"{agent_file.relative_to(ROOT)} should keep localized naming policy in Docs, not custom TOML fields")
    for field in LOCAL_AGENT_REQUIRED_FIELDS:
        if field not in text:
            fail(f"{agent_file.relative_to(ROOT)} missing local template field: {field}")
    for field in LOCAL_AGENT_REQUIRED_FIELDS:
        if not read_toml_string(text, field):
            fail(f"{agent_file.relative_to(ROOT)} has invalid local template field: {field}")
    name = read_toml_string(text, "name")
    sandbox_mode = read_toml_string(text, "sandbox_mode")
    if not name:
        fail(f"{agent_file.relative_to(ROOT)} has invalid agent name")
    expected_sandbox = "workspace-write" if name in WRITING_AGENTS else "read-only"
    if sandbox_mode != expected_sandbox:
        fail(
            f"{agent_file.relative_to(ROOT)} expected sandbox_mode = "
            f"{expected_sandbox!r} for agent {name!r}, got {sandbox_mode!r}"
        )
    instructions = read_toml_string(text, "developer_instructions")
    if not instructions:
        fail(f"{agent_file.relative_to(ROOT)} has invalid developer_instructions")
    for phrase in PUBLIC_AGENT_PHRASES:
        if phrase not in instructions:
            fail(f"{agent_file.relative_to(ROOT)} missing lock phrase: {phrase}")


def check_agents() -> None:
    agents_dir = ROOT / ".codex/agents"
    agent_files = sorted(agents_dir.glob("*.toml"))
    if not agent_files:
        fail("No .codex/agents/*.toml files found")

    for agent_file in agent_files:
        check_agent_file(agent_file)


def check_industry_packs() -> None:
    packs = CONFIG.get("industry_packs", {})
    if packs.get("required_selection") is not True:
        fail(".codex/team-kit.toml must require industry pack selection")
    available = packs.get("available", [])
    if not isinstance(available, list) or "game" not in available:
        fail(".codex/team-kit.toml must list the game industry pack")

    game_dir = ROOT / ".codex/agent-packs/game"
    missing = [name for name in GAME_PACK_AGENTS if not (game_dir / name).exists()]
    if missing:
        fail("Game pack missing agents: " + ", ".join(missing))
    for agent_file in sorted(game_dir.glob("*.toml")):
        if agent_file.name == "pack.toml":
            continue
        check_agent_file(agent_file)

    pack_toml = game_dir / "pack.toml"
    choice_keys = read_pack_choice_keys(pack_toml)
    if choice_keys != EXPECTED_GAME_CHOICES:
        fail(
            ".codex/agent-packs/game/pack.toml [choices] keys mismatch; "
            f"expected {sorted(EXPECTED_GAME_CHOICES)}, got {sorted(choice_keys)}"
        )

    for doc_path in [*CHOICE_KEY_DOCS, cfg_path("team_init")]:
        text = (ROOT / doc_path).read_text(encoding="utf-8")
        ensure_choice_keys_present(text, doc_path, choice_keys)

    pack_doc = (ROOT / "Docs/03-团队/行业扩展包/README.md").read_text(encoding="utf-8")
    for phrase in ["none", "game-basic", "game-full", "custom", "策划", "程序", "美术", "数值"]:
        if phrase not in pack_doc:
            fail(f"Docs/03-团队/行业扩展包/README.md missing phrase: {phrase}")
    for phrase in ["Unity/Cocos", "试玩验收", "可试玩 URL", "未覆盖设备和浏览器"]:
        if phrase not in pack_doc:
            fail(f"Docs/03-团队/行业扩展包/README.md missing game-pack-v2 phrase: {phrase}")

    game_readme = (game_dir / "README.md").read_text(encoding="utf-8")
    for phrase in GAME_README_PHRASES:
        if phrase not in game_readme:
            fail(f".codex/agent-packs/game/README.md missing game-pack-v2 phrase: {phrase}")

    playtest = (game_dir / "playtest-researcher.toml").read_text(encoding="utf-8")
    for phrase in PLAYTEST_CONTRACT_PHRASES:
        if phrase not in playtest:
            fail(f".codex/agent-packs/game/playtest-researcher.toml missing playtest contract phrase: {phrase}")

    prompt_template = (ROOT / ".codex/team/spawn-prompt-templates.md").read_text(encoding="utf-8")
    for phrase in ["玩法原型派发模板", "UI/HUD 派发模板", "浏览器试玩验收模板", "Unity/Cocos 引擎迁移评估模板"]:
        if phrase in prompt_template:
            fail(f".codex/team/spawn-prompt-templates.md should not carry game-specific dispatch template: {phrase}")
        if phrase not in game_readme:
            fail(f".codex/agent-packs/game/README.md missing game dispatch template: {phrase}")


def check_work_log_template() -> None:
    work_log = (ROOT / cfg_path("work_log_template")).read_text(encoding="utf-8")
    for heading in WORK_LOG_HEADINGS:
        if heading not in work_log:
            fail(f"{cfg_path('work_log_template')} missing work-log heading: {heading}")


def check_team_docs() -> None:
    team_doc = (ROOT / cfg_path("team_doc")).read_text(encoding="utf-8")
    for phrase in ["等待本波全部完成", "关闭完成的子代理线程", "公共文件只由 Codex 主线程修改", "按参与者更新最近任务和任务次数", "Team Assignment Map"]:
        if phrase not in team_doc:
            fail(f"{cfg_path('team_doc')} missing phrase: {phrase}")

    ai_manual = (ROOT / cfg_path("execution_manual")).read_text(encoding="utf-8")
    for phrase in [
        "预计涉及文件",
        "实际涉及文件",
        "何时必须先问用户",
        "子代理派发要求",
        "团队贡献汇报",
        "docs_root",
        "真相源策略",
        "staging",
        "行业扩展包",
        "install_mode",
        "重新初始化",
        "Team Assignment Map",
        "按参与者更新最近任务和任务次数",
        "中大型迭代方案门禁",
        "Team + Implementation-Plan",
        "批准执行",
        "pre-implementation",
    ]:
        if phrase not in ai_manual:
            fail(f"{cfg_path('execution_manual')} missing phrase: {phrase}")

    plan_index = (ROOT / f"{cfg_path('implementation_plan_root')}/README.md").read_text(encoding="utf-8")
    for phrase in ["实施方案索引", "中大型迭代", "防臃肿约束", "pre-implementation", "行业专属示例"]:
        if phrase not in plan_index:
            fail(f"{cfg_path('implementation_plan_root')}/README.md missing phrase: {phrase}")

    run_card = (ROOT / cfg_path("team_run_card")).read_text(encoding="utf-8")
    for phrase in ["已初始化项目", "默认不读取", "Team-Init", "Team + Implementation-Plan", "Team Assignment Map", "按参与者更新最近任务和任务次数", "只读 / dry-run"]:
        if phrase not in run_card:
            fail(f"{cfg_path('team_run_card')} missing phrase: {phrase}")

    routing_doc = (ROOT / cfg_path("routing_doc")).read_text(encoding="utf-8")
    for route in ROUTES:
        if route not in routing_doc:
            fail(f"{cfg_path('routing_doc')} missing route: {route}")
    team_section_match = re.search(r"### Team\n(.*?)\n### Team-Init", routing_doc, re.DOTALL)
    if not team_section_match:
        fail(f"{cfg_path('routing_doc')} missing bounded Team section before Team-Init")
    team_section = team_section_match.group(1)
    if cfg_path("team_init") in team_section or "行业扩展包/README.md" in team_section:
        fail(f"{cfg_path('routing_doc')} Team section must not load initialization or industry-pack docs")
    if cfg_path("team_run_card") not in routing_doc:
        fail(f"{cfg_path('routing_doc')} Team route must include Team run card")
    if "Team + Implementation-Plan" not in routing_doc:
        fail(f"{cfg_path('routing_doc')} must route M/L work to Team + Implementation-Plan")
    if cfg_path("team_init") not in routing_doc:
        fail(f"{cfg_path('routing_doc')} Team-Init route must include team initialization")
    init_doc = (ROOT / cfg_path("team_init")).read_text(encoding="utf-8")
    for phrase in [
        "GitHub 地址",
        "随机生成",
        "真实团队成员的人名",
        "不使用本模板文档中的示例名作为固定输出",
        "探测目标项目",
        "staging",
        "Router-only 试接入",
        "完整模式",
        "game-basic",
        "game-full",
        "已有文件合并决策表",
        "初始化完成报告模板",
        "rollback",
        "初始化演练检查点",
        "公共文件清单",
        "AGENTS.md` / `AGENT.md` 决策",
        "重新初始化 / 升级接入",
        "保留已有显示昵称",
        "未选择的扩展包源码默认不复制进目标项目",
    ]:
        if phrase not in init_doc:
            fail(f"{cfg_path('team_init')} missing phrase: {phrase}")

    roster = (ROOT / cfg_path("team_roster")).read_text(encoding="utf-8")
    for phrase in ["状态：pending", "待随机生成", "初始化时由 AI 随机起名并建档", "最近任务和任务次数"]:
        if phrase not in roster:
            fail(f"{cfg_path('team_roster')} missing initialization phrase: {phrase}")

    dispatch = (ROOT / ".codex/team/dispatch-protocol.md").read_text(encoding="utf-8")
    for phrase in DISPATCH_PHRASES:
        if phrase not in dispatch:
            fail(f".codex/team/dispatch-protocol.md missing phrase: {phrase}")


def check_staging_docs() -> None:
    staging = CONFIG.get("staging", {})
    if staging.get("required") is not True:
        fail(".codex/team-kit.toml must require staging")
    if staging.get("delete_after_merge") is not True:
        fail(".codex/team-kit.toml must require deleting staging after merge")
    if not staging.get("fallback_dir"):
        fail(".codex/team-kit.toml missing [staging].fallback_dir")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    init_doc = (ROOT / cfg_path("team_init")).read_text(encoding="utf-8")
    ai_manual = (ROOT / cfg_path("execution_manual")).read_text(encoding="utf-8")
    for phrase in ["不要把模板仓库直接拉到项目根目录", "staging", "删除 staging"]:
        if phrase not in readme:
            fail(f"README.md missing staging phrase: {phrase}")
    for phrase in ["Staging 接入协议", "不得把模板仓库直接拉取到目标项目根目录", "删除 staging 目录"]:
        if phrase not in init_doc:
            fail(f"{cfg_path('team_init')} missing staging phrase: {phrase}")
    for phrase in ["禁止直接 clone/解压到目标项目根目录", "删除 staging 目录"]:
        if phrase not in ai_manual:
            fail(f"{cfg_path('execution_manual')} missing staging phrase: {phrase}")


def check_readme_routes() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for route in ROUTES:
        if f"`{route}`" not in readme:
            fail(f"README.md missing route: {route}")
        if f'{route}"]' not in readme and route in {"Quick", "Project", "Team", "Team-Init", "Review", "Agent-Setup"}:
            fail(f"README.md workflow diagram missing route node: {route}")
    team_route_line = next((line for line in readme.splitlines() if line.startswith("| `Team` |")), "")
    if "团队初始化" in team_route_line or "行业扩展包" in team_route_line:
        fail("README.md Team route must not tell users to load initialization or industry-pack docs")
    for phrase in [
        "30 秒接入",
        "Team 运行卡",
        "Team Assignment Map -> Delegation Card",
        "Team + Implementation-Plan",
        "团队初始化",
        "按参与者更新团队名册",
        "新增可复用经验",
        "Router-only 试接入",
        "什么时候不用团队流程",
    ]:
        if phrase not in readme:
            fail(f"README.md missing workflow phrase: {phrase}")


def check_runtime_context_budget() -> None:
    budgets = {
        "README.md": int(cfg("checks", "max_readme_lines", 240)),
        cfg_path("execution_manual"): int(cfg("checks", "max_ai_manual_lines", 140)),
        f"{cfg_path('implementation_plan_root')}/README.md": int(cfg("checks", "max_implementation_plan_index_lines", 80)),
        cfg_path("team_run_card"): int(cfg("checks", "max_team_run_card_lines", 80)),
        cfg_path("routing_doc"): int(cfg("checks", "max_routing_doc_lines", 180)),
        cfg_path("team_doc"): int(cfg("checks", "max_team_doc_lines", 180)),
        ".codex/team/public-file-lock.md": int(cfg("checks", "max_public_file_lock_lines", 80)),
        cfg_path("team_init"): int(cfg("checks", "max_team_init_lines", 220)),
        ".codex/team/dispatch-protocol.md": int(cfg("checks", "max_dispatch_protocol_lines", 180)),
        ".codex/team/spawn-prompt-templates.md": int(cfg("checks", "max_spawn_prompt_templates_lines", 120)),
    }
    for path, max_lines in budgets.items():
        line_count = len((ROOT / path).read_text(encoding="utf-8").splitlines())
        if line_count > max_lines:
            fail(f"{path} exceeds local runtime context budget: {line_count} > {max_lines} lines")
    dispatch = (ROOT / ".codex/team/dispatch-protocol.md").read_text(encoding="utf-8")
    if "团队记忆" in dispatch:
        fail(".codex/team/dispatch-protocol.md must not use obsolete team memory wording")
    prompt_template = (ROOT / ".codex/team/spawn-prompt-templates.md").read_text(encoding="utf-8")
    readonly_match = re.search(r"## 只读探索模板\n(.*?)\n## ", prompt_template, re.DOTALL)
    if not readonly_match:
        fail(".codex/team/spawn-prompt-templates.md missing read-only exploration template section")
    if "写工作记录" in readonly_match.group(1):
        fail("Read-only exploration template must return a work-log draft instead of writing a work log")


def main() -> None:
    check_required_paths()
    check_target_project_placeholders()
    check_docs_root_case()
    check_initialization_config()
    check_truth_sources()
    check_no_ds_store()
    check_no_forbidden_staging_dirs()
    check_no_cross_project_paths()
    check_markdown_links()
    check_agents_md_router()
    check_config()
    check_official_codex_hooks()
    check_local_hooks()
    check_workflow_runtime_checker()
    check_no_stale_context_rules()
    check_team_assignment_map_shape()
    check_public_lock_source()
    check_agents()
    check_industry_packs()
    check_work_log_template()
    check_team_docs()
    check_staging_docs()
    check_readme_routes()
    check_runtime_context_budget()
    print("[OK] local codex-team-kit-router template integrity check passed")


if __name__ == "__main__":
    main()
