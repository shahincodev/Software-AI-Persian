"""Unified tool schema registry for structured tool calling.

This module defines the canonical tool names, parameter schemas, and validation
rules used by the AI agent to generate and validate structured tool calls.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolParam:
    """Definition of a single tool parameter."""
    name: str
    type: str  # "str", "int", "float", "bool", "list", "str|int|tuple"
    required: bool = True
    default: Any = None
    description: str = ""


@dataclass
class ToolDefinition:
    """Definition of a single tool available to the AI agent."""
    name: str
    description: str
    params: list[ToolParam]
    action_type: str  # Maps to action_factory type (e.g., "LaunchApp", "DesktopClick")
    risk_level: str = "low"  # "safe", "low", "medium", "high"

    def to_prompt_schema(self) -> str:
        """Generate a compact schema string for the LLM prompt."""
        param_parts = []
        for p in self.params:
            req = "REQUIRED" if p.required else f"optional, default={p.default}"
            param_parts.append(f'"{p.name}" ({p.type}): {p.description} [{req}]')
        params_str = ", ".join(param_parts)
        return f'{self.name}: {self.description}. Params: {params_str}'

    def to_json_example(self) -> dict[str, Any]:
        """Generate a JSON example for the LLM prompt."""
        example_params = {}
        for p in self.params:
            if p.name == "command":
                example_params[p.name] = "dir"
            elif p.name == "app_name":
                example_params[p.name] = "notepad.exe"
            elif p.name == "process_name":
                example_params[p.name] = "notepad.exe"
            elif p.name == "package_name":
                example_params[p.name] = "git"
            elif p.name == "package_manager":
                example_params[p.name] = "winget"
            elif p.name == "text":
                example_params[p.name] = "hello world"
            elif p.name == "target":
                example_params[p.name] = "OK"
            elif p.name == "keys":
                example_params[p.name] = ["ctrl", "c"]
            elif p.name == "direction":
                example_params[p.name] = "down"
            elif p.name == "path":
                example_params[p.name] = "C:\\Users"
            elif p.name == "query_type":
                example_params[p.name] = "all"
            elif p.name == "button":
                example_params[p.name] = "left"
            elif p.name == "clicks":
                example_params[p.name] = 1
            elif p.name == "shell":
                example_params[p.name] = "cmd"
            elif p.name == "wait_type":
                example_params[p.name] = "element"
            elif p.name == "duration":
                example_params[p.name] = 0.5
            elif p.name == "source":
                example_params[p.name] = "file.txt"
            elif p.name == "interval":
                example_params[p.name] = 0.05
            elif p.name == "hold_duration":
                example_params[p.name] = 0.0
            elif p.name == "smooth":
                example_params[p.name] = False
            elif p.name == "clear_first":
                example_params[p.name] = False
            elif p.name == "use_clipboard":
                example_params[p.name] = False
            elif p.name == "verify":
                example_params[p.name] = True
            elif p.name == "confidence":
                example_params[p.name] = 0.8
            elif p.name == "timeout":
                example_params[p.name] = 10
            elif p.name == "check_interval":
                example_params[p.name] = 0.5
            elif p.name == "inverse":
                example_params[p.name] = False
            elif p.name == "force":
                example_params[p.name] = False
            elif p.name == "silent":
                example_params[p.name] = True
            elif p.name == "version":
                example_params[p.name] = None
            elif p.name == "app_path":
                example_params[p.name] = None
            elif p.name == "arguments":
                example_params[p.name] = []
            elif p.name == "working_directory":
                example_params[p.name] = None
            elif p.name == "timeout_seconds":
                example_params[p.name] = 30
            elif p.name == "dry_run":
                example_params[p.name] = False
            elif p.name == "require_consent":
                example_params[p.name] = True
            elif p.default is not None:
                example_params[p.name] = p.default
        return {"tool": self.name, "params": example_params}


# ─────────────────────────────────────────────────────────────────────────────
# Canonical Tool Registry
# ─────────────────────────────────────────────────────────────────────────────

TOOLS: dict[str, ToolDefinition] = {}


def _register(tool: ToolDefinition) -> None:
    TOOLS[tool.name] = tool


# --- System Tools ---

_register(ToolDefinition(
    name="execute_command",
    description="Run a shell/cmd/PowerShell command",
    action_type="ExecuteCommand",
    risk_level="medium",
    params=[
        ToolParam("command", "str", required=True, description="The shell command to execute"),
        ToolParam("shell", "str", required=False, default="cmd", description="Shell type: 'cmd' or 'powershell'"),
        ToolParam("working_directory", "str", required=False, default=None, description="Working directory for the command"),
        ToolParam("timeout", "int", required=False, default=30, description="Timeout in seconds"),
    ],
))

_register(ToolDefinition(
    name="launch_app",
    description="Open/launch a Windows application",
    action_type="LaunchApp",
    risk_level="low",
    params=[
        ToolParam("app_name", "str", required=True, description="Application name or executable (e.g. 'notepad.exe', 'Chrome')"),
        ToolParam("app_path", "str", required=False, default=None, description="Full path to executable (optional)"),
        ToolParam("arguments", "list", required=False, default=[], description="Command-line arguments"),
        ToolParam("working_directory", "str", required=False, default=None, description="Working directory"),
    ],
))

_register(ToolDefinition(
    name="close_app",
    description="Close/terminate a running application",
    action_type="TerminateProcess",
    risk_level="medium",
    params=[
        ToolParam("process_name", "str", required=True, description="Process name to terminate (e.g. 'notepad.exe')"),
        ToolParam("force", "bool", required=False, default=False, description="Force termination"),
    ],
))

_register(ToolDefinition(
    name="install_package",
    description="Install software via package manager (winget/choco/pip/npm)",
    action_type="InstallPackage",
    risk_level="medium",
    params=[
        ToolParam("package_name", "str", required=True, description="Package name to install"),
        ToolParam("package_manager", "str", required=False, default="winget", description="Package manager: winget, choco, pip, npm"),
        ToolParam("version", "str", required=False, default=None, description="Specific version (optional)"),
        ToolParam("silent", "bool", required=False, default=True, description="Silent installation"),
    ],
))

_register(ToolDefinition(
    name="query_hardware",
    description="Get system hardware information (CPU, RAM, GPU, disk, network)",
    action_type="QueryHardware",
    risk_level="safe",
    params=[
        ToolParam("query_type", "str", required=False, default="all", description="Type: all, cpu, memory, gpu, disk, network, processes"),
    ],
))

# --- Desktop UI Tools ---

_register(ToolDefinition(
    name="click",
    description="Click on a UI element by text or coordinates",
    action_type="DesktopClick",
    risk_level="low",
    params=[
        ToolParam("target", "str|int|tuple", required=True, description="Text to click on, or (x, y) coordinates"),
        ToolParam("button", "str", required=False, default="left", description="Mouse button: left, right, middle"),
        ToolParam("clicks", "int", required=False, default=1, description="Number of clicks (1=single, 2=double)"),
    ],
))

_register(ToolDefinition(
    name="type_text",
    description="Type text into the active field or a specific target",
    action_type="DesktopType",
    risk_level="low",
    params=[
        ToolParam("text", "str", required=True, description="Text to type"),
        ToolParam("target", "str", required=False, default=None, description="Target field (None = active field)"),
        ToolParam("clear_first", "bool", required=False, default=False, description="Clear field before typing"),
        ToolParam("use_clipboard", "bool", required=False, default=False, description="Use clipboard for faster typing"),
    ],
))

_register(ToolDefinition(
    name="hotkey",
    description="Press a keyboard shortcut (e.g. Ctrl+C, Alt+Tab)",
    action_type="DesktopHotkey",
    risk_level="low",
    params=[
        ToolParam("keys", "list", required=True, description="List of keys to press (e.g. ['ctrl', 'c'])"),
    ],
))

_register(ToolDefinition(
    name="scroll",
    description="Scroll the screen or a specific element",
    action_type="DesktopScroll",
    risk_level="safe",
    params=[
        ToolParam("direction", "str", required=True, description="Direction: up, down, left, right"),
        ToolParam("clicks", "int", required=False, default=3, description="Scroll intensity (1-20)"),
        ToolParam("target", "str", required=False, default=None, description="Target element (optional)"),
    ],
))

_register(ToolDefinition(
    name="wait",
    description="Wait for an element, time, or condition",
    action_type="DesktopWait",
    risk_level="safe",
    params=[
        ToolParam("wait_type", "str", required=True, description="Type: element, change, window, process, time"),
        ToolParam("target", "str", required=False, default=None, description="Target to wait for (required for non-time types)"),
        ToolParam("timeout", "int", required=False, default=30, description="Max wait time in seconds"),
    ],
))

_register(ToolDefinition(
    name="drag_drop",
    description="Drag from source and drop to target",
    action_type="DesktopDragDrop",
    risk_level="medium",
    params=[
        ToolParam("source", "str|int|tuple", required=True, description="Source: text or (x, y)"),
        ToolParam("target", "str|int|tuple", required=True, description="Target: text or (x, y)"),
        ToolParam("duration", "float", required=False, default=0.5, description="Drag duration in seconds"),
    ],
))

# --- Read-only Tools ---

_register(ToolDefinition(
    name="list_directory",
    description="List files and folders in a directory",
    action_type=None,
    risk_level="safe",
    params=[
        ToolParam("path", "str", required=False, default=".", description="Directory path"),
    ],
))

_register(ToolDefinition(
    name="read_file",
    description="Read the contents of a text file",
    action_type=None,
    risk_level="safe",
    params=[
        ToolParam("path", "str", required=True, description="File path to read"),
    ],
))

# --- Vision Tools (Phase 3) ---

_register(ToolDefinition(
    name="screenshot",
    description="Take a screenshot of the current screen or a specific region",
    action_type=None,
    risk_level="safe",
    params=[
        ToolParam("region", "str", required=False, default=None, description="Region to capture: 'full', or 'x,y,w,h' for specific area"),
    ],
))

_register(ToolDefinition(
    name="read_screen",
    description="Read all visible text on screen using OCR",
    action_type=None,
    risk_level="safe",
    params=[],
))

_register(ToolDefinition(
    name="find_element",
    description="Find a UI element on screen by text or image",
    action_type=None,
    risk_level="safe",
    params=[
        ToolParam("text", "str", required=False, default=None, description="Text to search for on screen"),
        ToolParam("image", "str", required=False, default=None, description="Path to template image to find"),
        ToolParam("fuzzy", "bool", required=False, default=False, description="Use fuzzy text matching"),
    ],
))

_register(ToolDefinition(
    name="verify_action",
    description="Verify that an action achieved its expected outcome by checking the screen",
    action_type=None,
    risk_level="safe",
    params=[
        ToolParam("expected", "str", required=True, description="Description of expected outcome to verify"),
    ],
))

_register(ToolDefinition(
    name="describe_screen",
    description="Get a detailed description of what is currently visible on screen",
    action_type=None,
    risk_level="safe",
    params=[],
))


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_tool_call(tool_call: dict[str, Any]) -> tuple[bool, str]:
    """Validate a tool call dict against the schema.

    Args:
        tool_call: Dict with 'tool' and 'params' keys.

    Returns:
        (is_valid, error_message)
    """
    tool_name = tool_call.get("tool", "")
    params = tool_call.get("params", {})

    if not tool_name:
        return False, "Missing 'tool' field"

    if tool_name not in TOOLS:
        valid_names = ", ".join(TOOLS.keys())
        return False, f"Unknown tool '{tool_name}'. Valid tools: {valid_names}"

    tool_def = TOOLS[tool_name]

    for param_def in tool_def.params:
        if param_def.required and param_def.name not in params:
            return False, f"Missing required param '{param_def.name}' for tool '{tool_name}'"

    known_param_names = {p.name for p in tool_def.params}
    for key in params:
        if key not in known_param_names:
            return False, f"Unknown param '{key}' for tool '{tool_name}'"

    return True, "Valid"


def get_tool_prompt_block() -> str:
    """Generate the tool definitions block for the LLM prompt."""
    lines = []
    for name, tool in TOOLS.items():
        lines.append(f"- {tool.to_prompt_schema()}")
    return "\n".join(lines)


def get_tool_json_example(tool_name: str) -> dict[str, Any] | None:
    """Get a JSON example for a specific tool."""
    tool = TOOLS.get(tool_name)
    if tool:
        return tool.to_json_example()
    return None


def get_all_tool_names() -> list[str]:
    """Get list of all valid tool names."""
    return list(TOOLS.keys())


def get_tools_by_action_type() -> dict[str, str]:
    """Map action_type -> tool_name for tools that go through action_factory."""
    result = {}
    for name, tool in TOOLS.items():
        if tool.action_type:
            result[tool.action_type] = name
    return result
