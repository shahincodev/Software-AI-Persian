# Phase 2 Report — Structured Tool Calling

**Date**: 2026-07-02  
**Version**: 0.3.0  
**Status**: ✅ Completed

---

## Summary

Phase 2 replaced the ad-hoc chat-based tool calling with a unified, validated, and retry-capable structured tool calling system. The AI agent now behaves as an **action planner** rather than a chatbot.

---

## Problem Statement

Before Phase 2, the codebase had three disconnected action schemas:

1. **`agent_chat()` path** — LLM returned `{"action": "tool_call", "tool_calls": [...]}` with tool names like `execute_command`, `launch_app`, etc. These were dispatched by `ToolExecutor._dispatch()` which reconstructed natural-language strings and called `action_controller.process_request()` — a method that **did not exist**.

2. **`interpret_system_request()` path** — LLM returned `[{"type": "LaunchApp", "params": {...}}]` using action factory types. This path worked but was unused by the main agent loop.

3. **Fallback parser** — Regex-based keyword detection that was called whenever AI returned non-JSON, which happened frequently.

The result: most tool calls failed silently, and the system fell back to chat responses for actions that should have been executed.

---

## Changes Made

### 1. New File: `core/tool_schema.py`

Unified tool registry defining 13 canonical tools:

| Tool Name | Action Type | Description |
|-----------|-------------|-------------|
| `execute_command` | ExecuteCommand | Run shell/cmd/PowerShell commands |
| `launch_app` | LaunchApp | Open Windows applications |
| `close_app` | TerminateProcess | Close/terminate processes |
| `install_package` | InstallPackage | Install software via package managers |
| `query_hardware` | QueryHardware | Get system hardware info |
| `click` | DesktopClick | Click UI elements by text or coordinates |
| `type_text` | DesktopType | Type text into fields |
| `hotkey` | DesktopHotkey | Press keyboard shortcuts |
| `scroll` | DesktopScroll | Scroll the screen |
| `wait` | DesktopWait | Wait for elements/conditions |
| `drag_drop` | DesktopDragDrop | Drag and drop elements |
| `list_directory` | (direct) | List directory contents |
| `read_file` | (direct) | Read file contents |

Each tool includes:
- Parameter schema (name, type, required/optional, defaults)
- Validation rules
- Prompt generation for LLM
- JSON examples for few-shot learning

### 2. Modified: `core/ai_brain.py`

**`agent_chat()` method rewritten** with:
- Unified tool schema prompt (uses `get_tool_prompt_block()`)
- Schema validation after every LLM response
- Auto-retry with error context (max 2 retries)
- Structured error messages sent back to LLM on retry

**Flow:**
```
User Request → Build prompt with tool schema → LLM returns JSON
    → Parse JSON → Validate against schema
        → Valid: Execute tool calls
        → Invalid: Retry with error context (up to 2 times)
        → All retries exhausted: Return chat reply error
```

### 3. Modified: `main.py` — `ToolExecutor`

**Completely rewritten** to use proper execution path:
- `tool_schema.TOOLS` for tool lookup
- `action_factory.create_action_from_data()` for creating `SystemAction` objects
- `ActionController.execute_action()` for execution with safety checks

**Removed:** All broken `process_request()` calls that referenced a non-existent method.

### 4. Modified: `core/action_factory.py`

Added `TOOL_NAME_TO_ACTION_TYPE` alias map:
```python
TOOL_NAME_TO_ACTION_TYPE = {
    "launch_app": "LaunchApp",
    "close_app": "TerminateProcess",
    "install_package": "InstallPackage",
    "query_hardware": "QueryHardware",
    "click": "DesktopClick",
    "type_text": "DesktopType",
    "hotkey": "DesktopHotkey",
    "scroll": "DesktopScroll",
    "wait": "DesktopWait",
    "drag_drop": "DesktopDragDrop",
    "execute_command": "ExecuteCommand",
}
```

### 5. Modified: `core/system_action_parser.py`

- Added documentation explaining this is the **legacy path**
- Fallback parser (`_simple_fallback_parse`) now explicitly labeled as **emergency-only**
- Only called when AI completely fails after all retry attempts

---

## Architecture Change

### Before (Broken)
```
agent_chat() → LLM → ToolExecutor._dispatch()
    → reconstructs NL strings
    → calls process_request() [DOESN'T EXIST]
    → fails silently
    → falls back to chat_reply
```

### After (Fixed)
```
agent_chat() → LLM → schema validation → retry if invalid
    → action_factory.create_action_from_data()
    → ActionController.execute_action()
    → proper result with safety checks
```

---

## Testing

All integration tests passed:

```
=== Phase 2 Integration Test ===

Step 1: Validate tool calls against schema
  [PASS] launch_app: Valid
  [PASS] type_text: Valid
  [PASS] hotkey: Valid
  [PASS] execute_command: Valid

Step 2: Create actions via action_factory
  [launch_app] -> LaunchApp -> LaunchAppAction
  [type_text] -> DesktopType -> TypeAction
  [hotkey] -> DesktopHotkey -> HotkeyAction
  [execute_command] -> ExecuteCommand -> ExecuteCommandAction

Total tools: 13
Tool aliases: 11

=== ALL TESTS PASSED ===
```

---

## Version Bump

- **0.2.0** → **0.3.0**
- Updated in `main.py` (argparse version and banner)

---

## Files Changed

| File | Action | Lines Changed |
|------|--------|---------------|
| `core/tool_schema.py` | Created | ~280 lines |
| `core/ai_brain.py` | Modified | `agent_chat()` rewritten (~80 lines) |
| `main.py` | Modified | `ToolExecutor` rewritten (~100 lines), version bump |
| `core/action_factory.py` | Modified | Added alias map (~20 lines) |
| `core/system_action_parser.py` | Modified | Documentation + relabeling (~15 lines) |
| `ROADMAP.md` | Modified | Phase 2 marked complete |

---

## Next Steps (Phase 3)

Phase 3 will build the **Autonomous Vision Loop**:
- Integrate `DesktopVision` into the execution loop
- Implement visual verification after actions
- Detect UI failures automatically
- Retry with alternative actions when needed

---

*Report generated for Software-AI v0.3.0*
