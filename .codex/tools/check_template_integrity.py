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
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".codex/team-kit.toml"

ROUTES = ["Quick", "Project", "Team", "Review", "Agent-Setup"]

DISPATCH_PHRASES = [
    "Delegation Card",
    "压缩上下文包",
    "用户是否明确授权子代理",
    "主线程保留的关键路径",
    "所有本波子代理状态",
]

WRITING_AGENTS = {"implementation_engineer", "docs_keeper"}

LOCAL_AGENT_REQUIRED_FIELDS = [
    "name",
    "description",
    "developer_instructions",
]

PUBLIC_LOCK_PHRASES = [
    "Do not modify public files",
    "Docs/01-项目/项目进度.md",
    "Docs/02-执行/AI执行手册.md",
    "Docs/02-执行/工程结构与文档路由.md",
    ".codex/agents/*.toml",
    "Do not spawn subagents",
    "Docs/03-团队/Agents/工作记录",
]

WORK_LOG_HEADINGS = [
    "日期",
    "Agent 岗位",
    "显示昵称",
    "输入材料",
    "完成内容",
    "改动文件",
    "验证记录",
    "发现的问题",
    "建议回写",
    "下一次更懂项目的地方",
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


def required_paths() -> list[str]:
    required = [
        "AGENTS.md",
        "README.md",
        "Docs/README.md",
        ".codex/config.toml",
        ".codex/team-kit.toml",
        ".codex/tools/check_template_integrity.py",
        ".codex/team/dispatch-protocol.md",
        ".codex/team/model-routing.md",
        ".codex/team/public-file-lock.md",
        ".codex/team/role-taxonomy.md",
        ".codex/team/spawn-prompt-templates.md",
        cfg_path("project_spec"),
        cfg_path("project_progress"),
        cfg_path("execution_manual"),
        cfg_path("routing_doc"),
        cfg_path("team_doc"),
        cfg_path("team_init"),
        cfg_path("team_roster"),
        cfg_path("member_profile_template"),
        cfg_path("work_log_template"),
    ]

    mode = cfg("kit", "default_install_mode", "team-ready")
    if mode in {"team-ready", "full"}:
        required.append(cfg_path("agent_root"))
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


def check_agents_md_router() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    max_lines = int(cfg("checks", "max_agents_md_lines", 150))
    if line_count > max_lines:
        fail(f"AGENTS.md should stay router-sized, got {line_count} lines")
    for route in ROUTES:
        if route not in text:
            fail(f"AGENTS.md missing route: {route}")
    for phrase in ["Router Only", "路由表", "公共文件写锁", "子代理触发门槛"]:
        if phrase not in text:
            fail(f"AGENTS.md missing router phrase: {phrase}")
    if cfg_path("team_init") not in text:
        fail("AGENTS.md Team route must point to the team initialization doc")
    old_forced_load = "开始任何需求、实现、调研、评审或文档更新前"
    if old_forced_load in text:
        fail("AGENTS.md still contains the old forced full-context load rule")


def check_config() -> None:
    config = (ROOT / ".codex/config.toml").read_text(encoding="utf-8")
    if "[agents]" not in config:
        fail(".codex/config.toml missing local [agents] section")
    if not re.search(r"max_threads\s*=\s*6", config):
        fail(".codex/config.toml missing local template default max_threads = 6")
    if not re.search(r"max_depth\s*=\s*1", config):
        fail(".codex/config.toml missing local template default max_depth = 1")


def check_public_lock_source() -> None:
    lock_doc = (ROOT / ".codex/team/public-file-lock.md").read_text(encoding="utf-8")
    prompt_template = (ROOT / ".codex/team/spawn-prompt-templates.md").read_text(encoding="utf-8")
    for path in configured_public_files():
        if path not in lock_doc:
            fail(f".codex/team/public-file-lock.md missing public file: {path}")
        if path not in prompt_template:
            fail(f".codex/team/spawn-prompt-templates.md missing forbidden path: {path}")


def read_toml_string(text: str, field: str) -> str | None:
    triple = re.search(rf'(?m)^{field}\s*=\s*"""(.*?)"""', text, re.DOTALL)
    if triple:
        return triple.group(1)
    single = re.search(rf'(?m)^{field}\s*=\s*"([^"]*)"', text)
    if single:
        return single.group(1)
    return None


def check_agents() -> None:
    agents_dir = ROOT / ".codex/agents"
    agent_files = sorted(agents_dir.glob("*.toml"))
    if not agent_files:
        fail("No .codex/agents/*.toml files found")

    for agent_file in agent_files:
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
        for phrase in PUBLIC_LOCK_PHRASES:
            if phrase not in instructions:
                fail(f"{agent_file.relative_to(ROOT)} missing lock phrase: {phrase}")


def check_work_log_template() -> None:
    work_log = (ROOT / cfg_path("work_log_template")).read_text(encoding="utf-8")
    for heading in WORK_LOG_HEADINGS:
        if heading not in work_log:
            fail(f"{cfg_path('work_log_template')} missing work-log heading: {heading}")


def check_team_docs() -> None:
    team_doc = (ROOT / cfg_path("team_doc")).read_text(encoding="utf-8")
    for phrase in ["等待本波全部完成", "关闭完成的子代理线程", "公共文件只由 Codex 主线程修改"]:
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
    ]:
        if phrase not in ai_manual:
            fail(f"{cfg_path('execution_manual')} missing phrase: {phrase}")

    routing_doc = (ROOT / cfg_path("routing_doc")).read_text(encoding="utf-8")
    for route in ROUTES:
        if route not in routing_doc:
            fail(f"{cfg_path('routing_doc')} missing route: {route}")
    if cfg_path("team_init") not in routing_doc:
        fail(f"{cfg_path('routing_doc')} Team route must include team initialization")

    init_doc = (ROOT / cfg_path("team_init")).read_text(encoding="utf-8")
    for phrase in [
        "GitHub 地址",
        "随机生成",
        "真实团队成员的人名",
        "不使用本模板文档中的示例名作为固定输出",
        "探测目标项目",
        "最小模式",
        "完整模式",
    ]:
        if phrase not in init_doc:
            fail(f"{cfg_path('team_init')} missing phrase: {phrase}")

    roster = (ROOT / cfg_path("team_roster")).read_text(encoding="utf-8")
    for phrase in ["状态：pending", "待随机生成", "初始化时由 AI 随机起名并建档"]:
        if phrase not in roster:
            fail(f"{cfg_path('team_roster')} missing initialization phrase: {phrase}")

    dispatch = (ROOT / ".codex/team/dispatch-protocol.md").read_text(encoding="utf-8")
    for phrase in DISPATCH_PHRASES:
        if phrase not in dispatch:
            fail(f".codex/team/dispatch-protocol.md missing phrase: {phrase}")


def main() -> None:
    check_required_paths()
    check_docs_root_case()
    check_truth_sources()
    check_no_ds_store()
    check_no_cross_project_paths()
    check_agents_md_router()
    check_config()
    check_public_lock_source()
    check_agents()
    check_work_log_template()
    check_team_docs()
    print("[OK] local codex-team-kit-router template integrity check passed")


if __name__ == "__main__":
    main()
