"""Factory for creating action objects from dictionaries."""

from __future__ import annotations

import logging
from typing import Any, Optional

from core.desktop_actions import (
    ClickAction, TypeAction, WaitAction,
    DragDropAction, HotkeyAction, ScrollAction
)
from core.system_actions import (
    InstallPackageAction, LaunchAppAction,
    QueryHardwareAction, TerminateProcessAction, ExecuteCommandAction
)

logger = logging.getLogger(__name__)


def create_action_from_data(
    action_data: dict[str, Any],
    dry_run: bool = False
) -> Optional[Any]:
    """Create an action object from a dictionary specification.

    Args:
        action_data: Dictionary with 'type' and 'params' keys
        dry_run: If True, actions are created in dry-run mode

    Returns:
        An action object (ClickAction, TypeAction, etc.) or None if unknown type
    """
    action_type = action_data.get("type")
    params = action_data.get("params", {})

    try:
        if action_type == "DesktopClick":
            return ClickAction(
                target=params.get("target", ""),
                button=params.get("button", "left"),
                clicks=params.get("clicks", 1),
                verify=params.get("verify", True),
                confidence=params.get("confidence", 0.8),
                timeout=params.get("timeout", 10),
            )
        elif action_type == "DesktopType":
            return TypeAction(
                text=params.get("text", ""),
                target=params.get("target"),
                clear_first=params.get("clear_first", False),
                interval=params.get("interval", 0.05),
                verify=params.get("verify", True),
                use_clipboard=params.get("use_clipboard", False),
            )
        elif action_type == "DesktopWait":
            return WaitAction(
                wait_type=params.get("wait_type", "time"),
                target=params.get("target"),
                timeout=params.get("timeout", 30),
                check_interval=params.get("check_interval", 0.5),
                inverse=params.get("inverse", False),
            )
        elif action_type == "DesktopDragDrop":
            return DragDropAction(
                source=params.get("source", ""),
                target=params.get("target", ""),
                duration=params.get("duration", 0.5),
                verify=params.get("verify", True),
                button=params.get("button", "left"),
            )
        elif action_type == "DesktopHotkey":
            return HotkeyAction(
                keys=params.get("keys", []),
                interval=params.get("interval", 0.1),
                hold_duration=params.get("hold_duration", 0.0),
            )
        elif action_type == "DesktopScroll":
            return ScrollAction(
                direction=params.get("direction", "down"),
                clicks=params.get("clicks", 3),
                target=params.get("target"),
                smooth=params.get("smooth", False),
            )
        elif action_type == "LaunchApp":
            return LaunchAppAction(
                app_name=params.get("app_name", ""),
                app_path=params.get("app_path"),
                arguments=params.get("arguments", []),
                working_directory=params.get("working_directory"),
                dry_run=dry_run,
                require_consent=params.get("require_consent", True),
            )
        elif action_type == "InstallPackage":
            return InstallPackageAction(
                package_name=params.get("package_name", ""),
                package_manager=params.get("package_manager", "winget"),
                version=params.get("version"),
                silent=params.get("silent", True),
                dry_run=dry_run,
                require_consent=params.get("require_consent", True),
            )
        elif action_type == "QueryHardware":
            return QueryHardwareAction(
                query_type=params.get("query_type", "all"),
                dry_run=dry_run,
                require_consent=params.get("require_consent", True),
            )
        elif action_type == "TerminateProcess":
            return TerminateProcessAction(
                process_name=params.get("process_name"),
                process_id=params.get("process_id"),
                force=params.get("force", False),
                dry_run=dry_run,
                require_consent=params.get("require_consent", True),
            )
        elif action_type == "ExecuteCommand":
            return ExecuteCommandAction(
                command=params.get("command", ""),
                shell=params.get("shell", "cmd"),
                working_directory=params.get("working_directory"),
                timeout=params.get("timeout", 30),
                dry_run=dry_run,
                require_consent=params.get("require_consent", True),
            )
        else:
            logger.warning("Unknown action type: %s", action_type)
            return None

    except Exception as e:
        logger.exception("Error creating action %s: %s", action_type, e)
        return None
