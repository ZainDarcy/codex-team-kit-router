#!/usr/bin/env python3
"""Official Codex lifecycle hook handler for codex-team-kit-router.

This script writes only valid hook JSON to stdout. Human-facing docs stay in
Chinese, but hook output is concise English because it is machine/AI-facing.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

WORKFLOW_MARKERS = [
    "AGENTS.md",
    ".codex/config.toml",
    ".codex/team-kit.toml",
    ".codex/agents/",
    ".codex/agent-packs/",
    ".codex/team/",
    ".codex/hooks",
    ".codex/tools/",
    "Docs/01-",
    "Docs/02-",
    "Docs/03-",
]

TEAM_PROMPT_MARKERS = [
    "团队",
    "子代理",
    "并行",
    "agent",
    "Team",
    "初始化",
    "重新初始化",
    "reinit",
    "hook",
    "工作流",
]

PLAN_PROMPT_MARKERS = [
    "中大型",
    "大改",
    "重构",
    "实施方案",
    "方案包",
    "批准执行",
    "开始实施",
    "按文档做",
]


def emit(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


def load_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        emit({"systemMessage": f"codex-team-kit hook ignored invalid JSON input: {exc}"})
        sys.exit(0)
    return payload if isinstance(payload, dict) else {}


def as_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        command = value.get("command")
        if isinstance(command, str):
            return command
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, list):
        return "\n".join(as_text(item) for item in value)
    return "" if value is None else str(value)


def tool_text(payload: dict[str, Any]) -> str:
    return as_text(payload.get("tool_input"))


def touches_workflow(text: str) -> bool:
    return any(marker in text for marker in WORKFLOW_MARKERS)


def blocks_core_delete(text: str) -> str | None:
    compact = re.sub(r"\s+", " ", text)
    if re.search(r"\bgit\s+reset\s+--hard\b", compact):
        return "Blocked: git reset --hard can discard user or workflow state."
    if re.search(r"\bgit\s+checkout\s+--\s+(AGENTS\.md|Docs|\.codex)", compact):
        return "Blocked: direct checkout of public workflow files needs explicit user approval."
    if re.search(r"\brm\s+-[^\n]*[rf][^\n]*\s+(AGENTS\.md|\.codex(?:/|\s|$)|Docs(?:/|\s|$))", compact):
        return "Blocked: destructive removal of core workflow files needs explicit user approval."
    if "*** Delete File: AGENTS.md" in text or "*** Delete File: .codex/" in text:
        return "Blocked: deleting core workflow files needs explicit user approval."
    return None


def hook_context_for_prompt(prompt: str) -> str | None:
    prompt_markers = [*TEAM_PROMPT_MARKERS, *PLAN_PROMPT_MARKERS]
    if not any(marker in prompt for marker in prompt_markers):
        return None

    if any(marker in prompt for marker in ["初始化", "重新初始化", "reinit"]):
        return (
            "Team-Init route reminder: stage the kit, probe existing truth sources, "
            "preserve member identities on reinit, merge selected files only, then run post-init."
        )
    if any(marker in prompt for marker in PLAN_PROMPT_MARKERS):
        return (
            "Planning gate reminder: medium/large iterations need a scoped plan, explicit "
            "approval for that scope, then pre-implementation before runtime writes."
        )
    if any(marker in prompt for marker in ["团队", "子代理", "并行", "agent", "Team"]):
        return (
            "Team route reminder: before spawning subagents, write Team Assignment Map "
            "and Delegation Card, then send only compressed task context."
        )
    if any(marker in prompt for marker in ["hook", "工作流"]):
        return (
            "Hook reminder: Codex loads project hooks from .codex/hooks.json after /hooks trust; "
            ".codex/hooks/* scripts are handlers or manual fallback gates."
        )
    return "Use the slim route docs; avoid loading full team history unless the task needs it."


def handle_session_start() -> None:
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "codex-team-kit-router is active: route first, load docs on demand, "
                    "and bind Team Assignment Map before any subagent dispatch."
                ),
            }
        }
    )


def handle_user_prompt_submit(payload: dict[str, Any]) -> None:
    prompt = as_text(payload.get("prompt"))
    context = hook_context_for_prompt(prompt)
    if context:
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            }
        )
    else:
        emit({})


def handle_pre_tool_use(payload: dict[str, Any]) -> None:
    text = tool_text(payload)
    reason = blocks_core_delete(text)
    if reason:
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
        return

    if touches_workflow(text):
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        "Workflow files are in scope: public files stay main-thread-owned; "
                        "sync project progress for rule or structure changes."
                    ),
                }
            }
        )
    else:
        emit({})


def handle_permission_request(payload: dict[str, Any]) -> None:
    text = tool_text(payload)
    reason = blocks_core_delete(text)
    if reason:
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "decision": {"behavior": "deny", "message": reason},
                }
            }
        )
        return

    if "git push" in text:
        emit({"systemMessage": "Before approving publish, confirm integrity and pre-push gates passed."})
    else:
        emit({})


def handle_post_tool_use(payload: dict[str, Any]) -> None:
    text = tool_text(payload)
    if touches_workflow(text):
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "Workflow files changed or were inspected; run the final workflow gate "
                        "before replying, and keep the user-facing summary compact."
                    ),
                }
            }
        )
    else:
        emit({})


def pre_final_errors() -> list[str]:
    checker = ROOT / ".codex/tools/check_workflow_runtime.py"
    if not checker.exists():
        return ["Missing .codex/tools/check_workflow_runtime.py"]
    result = subprocess.run(
        [sys.executable, str(checker), "--gate", "pre-final"],
        cwd=str(ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return []
    output = "\n".join(part.strip() for part in [result.stdout, result.stderr] if part.strip())
    if not output:
        output = f"pre-final exited with code {result.returncode}"
    return [output[:900]]


def handle_stop(payload: dict[str, Any]) -> None:
    if payload.get("stop_hook_active"):
        emit({"continue": True, "suppressOutput": True})
        return

    errors = pre_final_errors()
    if errors:
        emit(
            {
                "decision": "block",
                "reason": "Workflow pre-final gate failed; fix before final response: " + "; ".join(errors),
            }
        )
    else:
        emit({"continue": True, "suppressOutput": True})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", default="")
    args = parser.parse_args()

    payload = load_payload()
    event = args.event or as_text(payload.get("hook_event_name"))

    handlers = {
        "SessionStart": lambda: handle_session_start(),
        "UserPromptSubmit": lambda: handle_user_prompt_submit(payload),
        "PreToolUse": lambda: handle_pre_tool_use(payload),
        "PermissionRequest": lambda: handle_permission_request(payload),
        "PostToolUse": lambda: handle_post_tool_use(payload),
        "Stop": lambda: handle_stop(payload),
    }
    handler = handlers.get(event)
    if handler is None:
        emit({})
        return
    handler()


if __name__ == "__main__":
    main()
