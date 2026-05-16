#!/usr/bin/env python3
"""Target-project workflow gates for codex-team-kit-router.

These checks are local template conventions, not official Codex hooks. They are
safe to run after the kit has been initialized in a target project.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".codex/team-kit.toml"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def parse_toml_subset(text: str) -> dict:
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
        elif value.startswith('"') and value.endswith('"'):
            current[key] = ast.literal_eval(value)
        elif value in {"true", "false"}:
            current[key] = value == "true"
        elif re.match(r"^-?\d+$", value):
            current[key] = int(value)
        else:
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


def plan_root_path() -> str:
    value = cfg("paths", "implementation_plan_root", "Docs/02-执行/实施方案")
    if not isinstance(value, str) or not value:
        fail(".codex/team-kit.toml [paths].implementation_plan_root must be a non-empty string")
    return value


def require_path(path: str) -> Path:
    candidate = ROOT / path
    if not candidate.exists():
        fail(f"Missing required workflow path: {path}")
    return candidate


def check_common() -> None:
    require_path(cfg_path("project_entry"))
    require_path(cfg_path("team_roster"))
    require_path(".codex/team/dispatch-protocol.md")
    require_path(".codex/team/spawn-prompt-templates.md")

    matches = sorted(path.relative_to(ROOT) for path in ROOT.rglob(".DS_Store"))
    if matches:
        fail("Project must not contain .DS_Store: " + ", ".join(str(path) for path in matches))

    forbidden = CONFIG.get("staging", {}).get("forbidden_final_dirs", [])
    if not isinstance(forbidden, list):
        fail(".codex/team-kit.toml [staging].forbidden_final_dirs must be a list")
    leftovers = [name for name in forbidden if (ROOT / str(name)).exists()]
    if leftovers:
        fail("Staging directories still present: " + ", ".join(leftovers))


def check_assignment_map() -> None:
    dispatch = require_path(".codex/team/dispatch-protocol.md").read_text(encoding="utf-8")
    prompt_template = require_path(".codex/team/spawn-prompt-templates.md").read_text(encoding="utf-8")
    for phrase in [
        "Team Assignment Map",
        "显示昵称",
        "运行时线程 / 系统 nickname",
        "成员档案路径",
        "工作记录路径",
        "sandbox / 写入权限",
    ]:
        if phrase not in dispatch:
            fail(f"dispatch-protocol missing identity field: {phrase}")
    for placeholder in ["{member_display_name}", "{member_profile_path}", "{work_log_path}"]:
        if placeholder not in prompt_template:
            fail(f"spawn prompt missing identity placeholder: {placeholder}")


def check_team_ready() -> None:
    state = cfg("initialization", "state")
    if state != "initialized":
        fail(f"Team route requires [initialization].state = initialized, got {state!r}")
    roster = require_path(cfg_path("team_roster")).read_text(encoding="utf-8")
    if "状态：pending" in roster or "待随机生成" in roster:
        fail("Team roster is still pending; run Team-Init before dispatch")
    member_root = ROOT / "Docs/03-团队/Agents/成员档案"
    member_files = [path for path in member_root.glob("*.md") if not path.name.startswith("_")]
    if not member_files:
        fail("No initialized member profiles found")


def approval_status_values() -> list[str]:
    values = cfg("planning_gate", "approval_status_values", ["draft", "reviewed", "approved", "in_progress", "done"])
    if not isinstance(values, list) or not values:
        fail(".codex/team-kit.toml planning_gate.approval_status_values must be a non-empty list")
    return [str(value).lower() for value in values]


def implementation_ready_status_values() -> list[str]:
    allowed = set(approval_status_values())
    values = cfg("planning_gate", "implementation_ready_status_values", ["approved", "in_progress", "done"])
    if not isinstance(values, list) or not values:
        fail(".codex/team-kit.toml planning_gate.implementation_ready_status_values must be a non-empty list")
    ready = [str(value).lower() for value in values]
    unexpected = sorted(value for value in ready if value not in allowed)
    if unexpected:
        fail(".codex/team-kit.toml implementation-ready values must be listed in approval_status_values: " + ", ".join(unexpected))
    return ready


def has_approved_scope(text: str) -> bool:
    ready_values = implementation_ready_status_values()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        approval = re.search(r"批准执行\s*[:：]\s*(.+)$", line)
        if approval:
            value = approval.group(1).strip()
            if value and "待填写" not in value and "<" not in value and ">" not in value:
                return True
        if any(key in lower for key in ["状态", "status", "approval", "approved_for_implementation"]):
            for value in ready_values:
                if re.search(rf"[:：=]\s*`?{re.escape(value)}`?(?:\s|$|[,，.;；。])", lower):
                    return True
        if "状态：已批准" in line:
            return True
    return False


def has_team_route_evidence(text: str) -> bool:
    return any(
        phrase in text
        for phrase in [
            "Team + Implementation-Plan",
            "Team Assignment Map",
            "Delegation Card",
            "团队讨论",
            "团队触发依据",
        ]
    )


def check_pre_implementation_ready() -> None:
    if cfg("planning_gate", "required_for_medium_large", True) is not True:
        return

    plan_root_rel = plan_root_path()
    plan_root = ROOT / plan_root_rel
    if not plan_root.exists():
        fail(f"Missing implementation plan root for M/L work: {plan_root_rel}")

    require_path(f"{plan_root_rel}/README.md")
    candidates = []
    candidates.extend(sorted(plan_root.glob("*/README.md")))
    if not candidates:
        fail(f"No implementation plan package found under {plan_root_rel}")

    approved_texts = [(path, path.read_text(encoding="utf-8")) for path in candidates]
    approved = [(path, text) for path, text in approved_texts if has_approved_scope(text)]
    if not approved:
        fail(
            "No approved implementation scope found. Mark the plan with "
            "`批准执行：<方案名/版本>` or an approved status before writing runtime code."
        )
    if not any(has_team_route_evidence(text) for _, text in approved):
        fail(
            "Approved implementation plan must record Team route evidence before runtime writes: "
            "Team + Implementation-Plan, Team Assignment Map, Delegation Card, or 团队讨论."
        )


def run_gate(gate: str) -> None:
    check_common()
    check_assignment_map()
    if gate == "pre-team-dispatch":
        check_team_ready()
    elif gate == "pre-implementation":
        check_pre_implementation_ready()
    elif gate == "post-init":
        if cfg("initialization", "state") == "template-source":
            fail("Target project still has template-source initialization state")
    elif gate == "pre-final":
        pass
    else:
        fail(f"Unknown workflow gate: {gate}")
    print(f"[OK] workflow gate passed: {gate}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True, choices=["post-init", "pre-team-dispatch", "pre-implementation", "pre-final"])
    args = parser.parse_args()
    run_gate(args.gate)


if __name__ == "__main__":
    main()
