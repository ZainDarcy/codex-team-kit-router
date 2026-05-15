#!/usr/bin/env python3
"""Check local template integrity for codex-team-kit-router.

This is not an official Codex/OpenAI rules validator. It does not access the
network, and it does not try to prove that current upstream Codex behavior is
unchanged. It only checks this template's own local structure and conventions.

When official alignment matters, ask AI to check the current OpenAI Codex docs
before changing this template.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "AGENTS.md",
    "Docs/README.md",
    "Docs/01-项目/项目规范.md",
    "Docs/01-项目/项目进度.md",
    "Docs/03-团队/开发团队.md",
    "Docs/02-执行/AI执行手册.md",
    "Docs/02-执行/工程结构与文档路由.md",
    "Docs/03-团队/Agents/团队初始化.md",
    "Docs/03-团队/Agents/团队名册.md",
    "Docs/03-团队/Agents/成员档案/_成员档案模板.md",
    "Docs/03-团队/Agents/工作记录/_工作记录模板.md",
    "Docs/03-团队/Agents/交付模板/策划交付模板.md",
    "Docs/03-团队/Agents/交付模板/程序交付模板.md",
    "Docs/03-团队/Agents/交付模板/设计交付模板.md",
    "Docs/03-团队/Agents/交付模板/QA验收模板.md",
    "Docs/03-团队/Agents/交付模板/研究分析模板.md",
    ".codex/config.toml",
    ".codex/team/dispatch-protocol.md",
    ".codex/team/model-routing.md",
    ".codex/team/public-file-lock.md",
    ".codex/team/role-taxonomy.md",
    ".codex/team/spawn-prompt-templates.md",
]

ROUTES = ["Quick", "Project", "Team", "Review", "Agent-Setup"]

DISPATCH_PHRASES = [
    "Delegation Card",
    "压缩上下文包",
    "用户是否明确授权子代理",
    "主线程保留的关键路径",
]

LOCAL_PUBLIC_FILES = [
    "AGENTS.md",
    "Docs/01-项目/项目规范.md",
    "Docs/01-项目/项目进度.md",
    "Docs/03-团队/开发团队.md",
    "Docs/02-执行/AI执行手册.md",
    "Docs/02-执行/工程结构与文档路由.md",
    ".codex/config.toml",
    ".codex/agents/*.toml",
    ".codex/team/*.md",
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


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def check_required_paths() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        fail("Missing required paths: " + ", ".join(missing))


def check_no_ds_store() -> None:
    matches = sorted(path.relative_to(ROOT) for path in ROOT.rglob(".DS_Store"))
    if matches:
        fail("Template must not contain .DS_Store: " + ", ".join(str(path) for path in matches))


def check_agents_md_router() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    if line_count > 140:
        fail(f"AGENTS.md should stay router-sized, got {line_count} lines")
    for route in ROUTES:
        if route not in text:
            fail(f"AGENTS.md missing route: {route}")
    for phrase in ["Router Only", "路由表", "公共文件写锁", "子代理触发门槛"]:
        if phrase not in text:
            fail(f"AGENTS.md missing router phrase: {phrase}")
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
    for path in LOCAL_PUBLIC_FILES:
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


def check_team_docs() -> None:
    team_doc = (ROOT / "Docs/03-团队/开发团队.md").read_text(encoding="utf-8")
    for phrase in ["等待本波全部完成", "关闭完成的子代理线程", "公共文件只由 Codex 主线程修改"]:
        if phrase not in team_doc:
            fail(f"Docs/03-团队/开发团队.md missing phrase: {phrase}")

    ai_manual = (ROOT / "Docs/02-执行/AI执行手册.md").read_text(encoding="utf-8")
    for phrase in ["预计涉及文件", "实际涉及文件", "何时必须先问用户", "子代理派发要求", "团队贡献汇报"]:
        if phrase not in ai_manual:
            fail(f"Docs/02-执行/AI执行手册.md missing phrase: {phrase}")

    routing_doc = (ROOT / "Docs/02-执行/工程结构与文档路由.md").read_text(encoding="utf-8")
    for route in ROUTES:
        if route not in routing_doc:
            fail(f"Docs/02-执行/工程结构与文档路由.md missing route: {route}")

    init_doc = (ROOT / "Docs/03-团队/Agents/团队初始化.md").read_text(encoding="utf-8")
    for phrase in ["GitHub 地址", "随机生成", "真实团队成员的人名", "不使用本模板文档中的示例名作为固定输出"]:
        if phrase not in init_doc:
            fail(f"Docs/03-团队/Agents/团队初始化.md missing phrase: {phrase}")

    roster = (ROOT / "Docs/03-团队/Agents/团队名册.md").read_text(encoding="utf-8")
    for phrase in ["状态：pending", "待随机生成", "初始化时由 AI 随机起名并建档"]:
        if phrase not in roster:
            fail(f"Docs/03-团队/Agents/团队名册.md missing initialization phrase: {phrase}")

    dispatch = (ROOT / ".codex/team/dispatch-protocol.md").read_text(encoding="utf-8")
    for phrase in DISPATCH_PHRASES:
        if phrase not in dispatch:
            fail(f".codex/team/dispatch-protocol.md missing phrase: {phrase}")


def main() -> None:
    check_required_paths()
    check_no_ds_store()
    check_agents_md_router()
    check_config()
    check_public_lock_source()
    check_agents()
    check_team_docs()
    print("[OK] local codex-team-kit-router template integrity check passed")


if __name__ == "__main__":
    main()
