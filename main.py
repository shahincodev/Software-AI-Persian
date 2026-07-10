#!/usr/bin/env python3
# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Software-AI: Intelligent Windows Automation System

An AI agent with full system access that understands natural language
and executes actions autonomously on Windows.
"""

from __future__ import annotations

import argparse
import asyncio
import io
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Fix Windows console encoding for emoji/unicode support
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from colorama import init as colorama_init, Fore, Style
from dotenv import load_dotenv

from core.action_controller import ActionController
from core.action_factory import create_action_from_data
from core.action_types import ActionResult
from core.ai_brain import AIBrain
from core.capability_manager import CapabilityManager
from core.desktop_vision import DesktopVision
from core.intent_router import IntentRouter, RouteType
from core.keyboard_control import KeyboardController
from core.logging_config import install_exception_hook, setup_logging
from core.memory_integrator import MemoryIntegrator, MemoryManager
from core.session_manager import SessionManager
from core.windows_environment import WindowsEnvironment
from core.mouse_control import MouseController
from core.plan_generator import PlanGenerator, ExecutionPlan
from core.plan_validator import PlanValidator
from core.safety_consent_manager import SafetyConsentManager
from core.smart_wait import SmartWaiter
from core.step_tracker import StepTracker
from core.tool_schema import TOOLS
from core.vision_loop import VisionLoopManager
from core.voice_io import VoiceManager
from core.workflow_engine import WorkflowEngine

colorama_init(autoreset=True)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# System Context Builder
# ─────────────────────────────────────────────────────────────────────────────

class SystemContext:
    """Builds and maintains real-time system context for the AI agent."""

    def __init__(self):
        self.working_directory = os.getcwd()
        self.last_actions: list[dict[str, Any]] = []
        self.max_history = 10

    def record_action(self, action: dict[str, Any]) -> None:
        """Record an executed action for context."""
        self.last_actions.append(action)
        if len(self.last_actions) > self.max_history:
            self.last_actions = self.last_actions[-self.max_history:]

    def get_context(self) -> str:
        """Build system context string for AI injection."""
        sections = []

        # Working directory and files
        sections.append(f"Working Directory: {self.working_directory}")
        try:
            entries = list(Path(self.working_directory).iterdir())
            dirs = [e.name for e in entries if e.is_dir()][:15]
            files = [e.name for e in entries if e.is_file()][:15]
            if dirs:
                sections.append(f"Folders: {', '.join(dirs)}")
            if files:
                sections.append(f"Files: {', '.join(files)}")
        except PermissionError:
            sections.append("Files: (access denied)")

        # Key Windows locations
        user_profile = os.environ.get("USERPROFILE", "")
        if user_profile:
            locations = {
                "Desktop": Path(user_profile) / "Desktop",
                "Downloads": Path(user_profile) / "Downloads",
                "Documents": Path(user_profile) / "Documents",
            }
            for name, path in locations.items():
                if path.exists():
                    try:
                        count = len(list(path.iterdir()))
                        sections.append(f"{name}: {path} ({count} items)")
                    except PermissionError:
                        sections.append(f"{name}: {path}")

        # Available drives
        drives = []
        for letter in "CDEFGH":
            drive = Path(f"{letter}:\\")
            if drive.exists():
                drives.append(f"{letter}:")
        if drives:
            sections.append(f"Available drives: {', '.join(drives)}")

        # Recent actions
        if self.last_actions:
            sections.append("\nRecent actions:")
            for a in self.last_actions[-5:]:
                status = a.get("status", "unknown")
                desc = a.get("description", a.get("command", "unknown"))
                icon = "+" if status == "success" else "X" if status == "failed" else "~"
                sections.append(f"  [{icon}] {desc}")

        return "\n".join(sections)


# ─────────────────────────────────────────────────────────────────────────────
# Tool Executor
# ─────────────────────────────────────────────────────────────────────────────

class ToolExecutor:
    """Executes tool calls from the AI agent using action_factory + ActionController + VisionLoopManager.

    Supports both atomic tool calls and multi-step plan execution (Phase 4).
    """

    def __init__(
        self,
        action_controller: ActionController,
        vision_loop: VisionLoopManager,
        safety_mode: str = "safe",
        ai_brain: Optional[AIBrain] = None,
        memory_manager: Optional[MemoryManager] = None,
    ):
        self.action_controller = action_controller
        self.vision_loop = vision_loop
        self.safety_mode = safety_mode
        self.ai_brain = ai_brain
        self.memory_manager = memory_manager
        self.plan_generator: Optional[PlanGenerator] = None
        self.plan_validator: Optional[PlanValidator] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self._pending_plan: Optional[ExecutionPlan] = None

        # Initialize plan system if AI brain is available
        if ai_brain:
            self.plan_generator = PlanGenerator(ai_brain=ai_brain)
            self.plan_validator = PlanValidator(ai_brain=ai_brain)
            self.workflow_engine = WorkflowEngine(
                tool_executor=self,
                ai_brain=ai_brain,
                validate_before_execute=True,
                max_retries_per_step=2,
            )
            logger.info("Plan system initialized (PlanGenerator + PlanValidator + WorkflowEngine)")

    async def execute(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute a list of tool calls and return results."""
        results = []
        for tc in tool_calls:
            tool = tc.get("tool", "")
            params = tc.get("params", {})
            description = tc.get("description", tool)
            result = await self._dispatch(tool, params, description)
            results.append(result)
        return results

    async def execute_plan(self, plan: ExecutionPlan) -> dict[str, Any]:
        """Execute an entire ExecutionPlan via WorkflowEngine.

        Returns:
            A tool-call-compatible result dict with workflow summary.
        """
        if not self.workflow_engine:
            return {
                "status": "failed",
                "description": "Workflow engine not initialized",
                "error": "Plan system requires AI brain",
            }

        logger.info("Executing plan %s (%d steps)", plan.plan_id, len(plan.steps))

        workflow_result = await self.workflow_engine.execute(plan)

        return {
            "status": "success" if workflow_result.success else "failed",
            "description": f"Plan {plan.plan_id}: {workflow_result.completed_steps}/{workflow_result.total_steps} steps completed",
            "output": (
                f"Plan completed successfully.\n"
                f"Steps: {workflow_result.completed_steps}/{workflow_result.total_steps}\n"
                f"Failed: {workflow_result.failed_steps}\n"
                f"Skipped: {workflow_result.skipped_steps}\n"
                f"Time: {workflow_result.elapsed_ms:.0f}ms"
            ),
            "error": workflow_result.error_summary if workflow_result.error_summary else "",
            "plan_id": workflow_result.plan_id,
            "step_results": workflow_result.step_results,
        }

    async def generate_and_execute_plan(
        self,
        user_text: str,
        context_str: str = "",
        screen_context_str: str = "",
    ) -> dict[str, Any]:
        """Generate a plan from user text and execute it.

        This is the main entry point for multi-step requests.
        """
        if not self.plan_generator or not self.plan_validator or not self.workflow_engine:
            return {
                "status": "failed",
                "description": "Plan system not initialized",
                "error": "Plan system requires AI brain",
            }

        try:
            from core.intent_analyzer import Intent, IntentAnalysisResult

            # Create a minimal intent for plan generation
            intent = Intent(
                verb="execute",
                target=user_text,
                parameters={"user_request": user_text},
                confidence=0.9,
                raw_request=user_text,
                language="en",
            )

            # Generate plan
            plan = await self.plan_generator.generate_plan(intent)

            # Validate
            report = await self.plan_validator.validate(
                plan, intent=intent,
                check_security=True,
                check_resources=False,
            )

            if not report.is_valid:
                return {
                    "status": "failed",
                    "description": "Plan validation failed",
                    "error": f"Validation errors: {report.total_errors}",
                }

            # Execute
            self._pending_plan = plan
            return await self.execute_plan(plan)

        except Exception as e:
            logger.exception("Plan generation/execution failed: %s", e)
            return {
                "status": "failed",
                "description": "Plan generation failed",
                "error": str(e),
            }

    async def _dispatch(self, tool: str, params: dict, description: str) -> dict[str, Any]:
        """Dispatch a single tool call to the appropriate handler."""
        try:
            # Phase 4: Plan tools
            if tool == "execute_plan":
                return await self._handle_execute_plan(params, description)
            elif tool == "list_plan_steps":
                return await self._handle_list_plan_steps(params, description)

            # Phase 5: Memory tools
            elif tool == "remember":
                return self._handle_remember(params, description)
            elif tool == "recall":
                return self._handle_recall(params, description)
            elif tool == "forget":
                return self._handle_forget(params, description)

            # Read-only tools: execute directly (no action_factory needed)
            if tool == "list_directory":
                return await self._list_directory(params, description)
            elif tool == "read_file":
                return await self._read_file(params, description)
            elif tool == "execute_command":
                return await self._execute_command(params, description)

            # Vision tools (Phase 3)
            elif tool == "screenshot":
                return await self._screenshot(params, description)
            elif tool == "read_screen":
                return await self._read_screen(params, description)
            elif tool == "find_element":
                return await self._find_element(params, description)
            elif tool == "verify_action":
                return await self._verify_action(params, description)
            elif tool == "describe_screen":
                return await self._describe_screen(params, description)

            # Tools that go through action_factory -> ActionController
            tool_def = TOOLS.get(tool)
            if tool_def and tool_def.action_type:
                return await self._execute_via_action_factory(tool_def.action_type, params, description)

            return {"status": "failed", "description": description, "error": f"Unknown tool: {tool}"}

        except Exception as e:
            logger.exception("Tool execution failed: %s", e)
            return {"status": "failed", "description": description, "error": str(e)}

    async def _handle_execute_plan(self, params: dict, description: str) -> dict[str, Any]:
        """Handle execute_plan tool call."""
        user_request = params.get("request", "") or params.get("user_request", "")
        if not user_request:
            return {"status": "failed", "description": description, "error": "No request provided"}

        result = await self.generate_and_execute_plan(user_request)
        result["description"] = description
        return result

    async def _handle_list_plan_steps(self, params: dict, description: str) -> dict[str, Any]:
        """Handle list_plan_steps tool call."""
        if not self._pending_plan:
            return {
                "status": "failed",
                "description": description,
                "error": "No pending plan",
            }

        steps_info = []
        for step in sorted(self._pending_plan.steps, key=lambda s: s.order):
            deps = ", ".join(step.dependencies) if step.dependencies else "none"
            steps_info.append(
                f"[{step.order}] {step.action} "
                f"(type={step.step_type.value}, deps=[{deps}], timeout={step.timeout}s)"
            )

        return {
            "status": "success",
            "description": description,
            "output": "\n".join(steps_info),
        }

    # ── Memory Tools (Phase 5) ──────────────────────────────────────────

    def _handle_remember(self, params: dict, description: str) -> dict[str, Any]:
        """Handle remember tool call — save to long-term memory."""
        content = params.get("content", "")
        category = params.get("category", "general")
        if not content:
            return {"status": "failed", "description": description, "error": "No content to remember"}

        if not self.memory_manager:
            return {"status": "failed", "description": description, "error": "Memory system not initialized"}

        try:
            item = self.memory_manager.remember_long(
                content=content,
                metadata={"category": category, "source": "ai_tool"}
            )
            return {
                "status": "success",
                "description": description,
                "output": f"Remembered (id: {item.id[:8]}...): {content[:100]}",
                "memory_id": item.id,
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    def _handle_recall(self, params: dict, description: str) -> dict[str, Any]:
        """Handle recall tool call — search memory."""
        query = params.get("query", "")
        limit = params.get("limit", 5)
        if not query:
            return {"status": "failed", "description": description, "error": "No query provided"}

        if not self.memory_manager:
            return {"status": "failed", "description": description, "error": "Memory system not initialized"}

        try:
            results = self.memory_manager.recall(query, limit=limit)
            if not results:
                return {
                    "status": "success",
                    "description": description,
                    "output": "No memories found matching the query.",
                }

            lines = []
            for item in results:
                cat = item.metadata.get("category", "general")
                lines.append(f"[{item.id[:8]}...] ({cat}): {item.content[:200]}")

            return {
                "status": "success",
                "description": description,
                "output": f"Found {len(results)} memories:\n" + "\n".join(lines),
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    def _handle_forget(self, params: dict, description: str) -> dict[str, Any]:
        """Handle forget tool call — delete a memory."""
        memory_id = params.get("memory_id", "")
        if not memory_id:
            return {"status": "failed", "description": description, "error": "No memory_id provided"}

        if not self.memory_manager:
            return {"status": "failed", "description": description, "error": "Memory system not initialized"}

        try:
            deleted = self.memory_manager.forget_long(memory_id)
            if deleted:
                return {
                    "status": "success",
                    "description": description,
                    "output": f"Memory {memory_id[:8]}... forgotten.",
                }
            else:
                return {
                    "status": "failed",
                    "description": description,
                    "error": f"Memory {memory_id} not found",
                }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    async def _execute_via_action_factory(self, action_type: str, params: dict, description: str) -> dict[str, Any]:
        """Create a SystemAction via action_factory and execute via ActionController with vision verification."""
        action_data = {"type": action_type, "params": params}
        action = create_action_from_data(action_data)

        if action is None:
            return {"status": "failed", "description": description, "error": f"Failed to create action for type: {action_type}"}

        # Validate the action
        is_valid, msg = action.validate()
        if not is_valid:
            return {"status": "failed", "description": description, "error": f"Validation failed: {msg}"}

        # Observe screen before action
        screen_before = None
        try:
            screen_before = self.vision_loop.observe_screen()
        except Exception as e:
            logger.warning("Failed to observe screen before action: %s", e)

        # Execute via ActionController
        result = self.action_controller.execute_action(action)

        # Verify action with vision if it's a UI action
        verification_passed = True
        if result.result.value != "success":
            verification_passed = False
        elif screen_before and action_type in ("DesktopClick", "DesktopType", "DesktopHotkey"):
            try:
                verification_passed, verify_msg = self.vision_loop.verify_action(
                    description, screen_before
                )
                logger.info("Vision verification: %s", verify_msg)
            except Exception as e:
                logger.warning("Vision verification failed: %s", e)

        return {
            "status": "success" if result.result == ActionResult.SUCCESS and verification_passed else "failed",
            "description": description,
            "output": result.message or "",
            "error": result.error or ("" if verification_passed else "Visual verification failed"),
        }

    # ── Vision Tools (Phase 3) ──────────────────────────────────────────

    async def _screenshot(self, params: dict, description: str) -> dict[str, Any]:
        """Take a screenshot of the current screen."""
        try:
            region = params.get("region")
            screenshot = self.vision_loop.vision.capture_screen()
            path = f"data/screenshots/screenshot_{int(__import__('time').time())}.png"
            screenshot.save(path)
            return {
                "status": "success",
                "description": description,
                "output": f"Screenshot saved to: {path}",
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    async def _read_screen(self, params: dict, description: str) -> dict[str, Any]:
        """Read all visible text on screen using OCR."""
        try:
            state = self.vision_loop.observe_screen()
            return {
                "status": "success",
                "description": description,
                "output": state.ocr_text or "(no text found on screen)",
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    async def _find_element(self, params: dict, description: str) -> dict[str, Any]:
        """Find a UI element on screen by text or image."""
        try:
            text = params.get("text")
            image = params.get("image")
            fuzzy = params.get("fuzzy", False)

            if text:
                if fuzzy:
                    result = self.vision_loop.vision.find_text_fuzzy(text)
                else:
                    result = self.vision_loop.vision.find_text(text)

                if result:
                    return {
                        "status": "success",
                        "description": description,
                        "output": f"Found '{text}' at position: ({result[0]}, {result[1]})",
                        "position": list(result),
                    }
                else:
                    return {
                        "status": "failed",
                        "description": description,
                        "error": f"Element '{text}' not found on screen",
                    }
            elif image:
                result = self.vision_loop.vision.find_image(image)
                if result:
                    return {
                        "status": "success",
                        "description": description,
                        "output": f"Found image at position: ({result.x}, {result.y}), confidence: {result.confidence:.2f}",
                        "position": [result.x, result.y],
                    }
                else:
                    return {
                        "status": "failed",
                        "description": description,
                        "error": f"Image template '{image}' not found on screen",
                    }
            else:
                return {"status": "failed", "description": description, "error": "Either 'text' or 'image' parameter required"}

        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    async def _verify_action(self, params: dict, description: str) -> dict[str, Any]:
        """Verify that an action achieved its expected outcome."""
        try:
            expected = params.get("expected", "")
            passed, message = self.vision_loop.verify_action(expected)
            return {
                "status": "success" if passed else "failed",
                "description": description,
                "output": message,
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    async def _describe_screen(self, params: dict, description: str) -> dict[str, Any]:
        """Get a detailed description of what is currently visible on screen."""
        try:
            desc = self.vision_loop.describe_screen()
            return {
                "status": "success",
                "description": description,
                "output": desc,
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    async def _execute_command(self, params: dict, description: str) -> dict[str, Any]:
        command = params.get("command", "")
        if not command:
            return {"status": "failed", "description": description, "error": "No command provided"}

        shell_type = params.get("shell", "cmd")

        # Detect PowerShell-specific syntax and wrap properly
        is_powershell_cmd = self._needs_powershell_wrapper(command, shell_type)

        if is_powershell_cmd:
            # Wrap PowerShell commands with -Command flag to ensure they run in PowerShell
            if not command.strip().lower().startswith("powershell"):
                command = f'powershell -NoProfile -Command "{command}"'

        logger.info("Executing command: %s", command)
        try:
            proc = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = proc.stdout.strip() if proc.stdout else ""
            error = proc.stderr.strip() if proc.stderr else ""
            success = proc.returncode == 0

            result = {
                "status": "success" if success else "failed",
                "description": description,
                "command": command,
                "output": output[:2000] if output else "",
                "error": error[:1000] if error else "",
                "return_code": proc.returncode,
            }
            logger.info("Command %s: %s", "succeeded" if success else "failed", command)
            return result
        except subprocess.TimeoutExpired:
            return {"status": "failed", "description": description, "error": "Command timed out"}
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    @staticmethod
    def _needs_powershell_wrapper(command: str, shell_type: str = "cmd") -> bool:
        """Detect if a command needs PowerShell wrapper.

        Returns True if the command uses PowerShell syntax like:
        - PowerShell variables ($var = ...)
        - Here-strings (@' ... '@ or @" ... "@)
        - PowerShell cmdlets (Set-Content, Get-ChildItem, etc.)
        - Pipeline with PowerShell-only commands
        """
        if shell_type == "powershell":
            return True

        cmd_lower = command.lower().strip()

        # PowerShell variables
        if "$" in command and ("=" in command or "(" in command):
            return True

        # Here-string syntax
        if "@'" in command or "'@" in command or '@"' in command or '"@' in command:
            return True

        # Common PowerShell cmdlets
        ps_cmdlets = [
            "set-content", "get-content", "get-childitem", "new-item",
            "remove-item", "copy-item", "move-item", "test-path",
            "out-file", "write-output", "write-host", "get-process",
            "get-service", "get-wmiobject", "invoke-command",
            "foreach-object", "where-object", "select-object",
            "sort-object", "measure-object", "compare-object",
            "import-csv", "export-csv", "convertto-json", "convertfrom-json",
            "start-process", "stop-process", "get-date",
            "get-random", "systeminfo", "hostname",
        ]

        for cmdlet in ps_cmdlets:
            if cmdlet in cmd_lower:
                return True

        return False

    async def _list_directory(self, params: dict, description: str) -> dict[str, Any]:
        path = params.get("path", ".")
        try:
            p = Path(path)
            if not p.exists():
                return {"status": "failed", "description": description, "error": f"Path not found: {path}"}
            entries = []
            for item in sorted(p.iterdir()):
                prefix = "[DIR] " if item.is_dir() else "      "
                entries.append(f"{prefix}{item.name}")
            return {
                "status": "success",
                "description": description,
                "output": "\n".join(entries[:50]) if entries else "(empty directory)",
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}

    async def _read_file(self, params: dict, description: str) -> dict[str, Any]:
        path = params.get("path", "")
        max_size = params.get("max_size", 100_000)  # Default 100KB, but configurable
        try:
            p = Path(path)
            if not p.exists():
                return {"status": "failed", "description": description, "error": f"File not found: {path}"}
            file_size = p.stat().st_size
            if file_size > max_size:
                # Read in chunks - first chunk + summary
                content_parts = []
                chunk_size = max_size // 2  # Read first half
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    content_parts.append(f.read(chunk_size))
                content_parts.append(f"\n\n[... File truncated ({file_size} bytes total, showing first {chunk_size} bytes) ...]")
                content = "".join(content_parts)
            else:
                content = p.read_text(encoding="utf-8", errors="replace")
            return {
                "status": "success",
                "description": description,
                "output": content[:10000],  # Increased from 5000 to 10000
            }
        except Exception as e:
            return {"status": "failed", "description": description, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Software-AI: AI-Powered Windows Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Interactive agent mode
  python main.py --debug             # Debug logging
  python main.py --dry-run           # Simulate without executing
  python main.py --safety-mode power # Less restrictive safety
        """,
    )
    parser.add_argument("--version", action="version", version="Software-AI 1.0.0")
    parser.add_argument("--input-mode", choices=["text", "voice"], default="text")
    parser.add_argument("--tts-provider", choices=["google-cloud", "gtts", "elevenlabs"], default="gtts")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--safety-mode", choices=["safe", "power"], default="safe")
    parser.add_argument("--risk-threshold", type=int, default=70)
    parser.add_argument("--allow-app", action="append", default=[])
    parser.add_argument("--allow-path", action="append", default=[])
    return parser.parse_args()


def print_banner() -> None:
    try:
        banner_text = Path("banner.txt").read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        banner_text = "Software-AI"

    width = shutil.get_terminal_size((80, 20)).columns
    cyan = Fore.CYAN
    reset = Style.RESET_ALL

    print()
    for line in banner_text.splitlines():
        # Center the raw text, then wrap with color
        padded = line.center(width)
        try:
            print(f"{cyan}{padded}{reset}")
        except UnicodeEncodeError:
            print(padded)
    print()
    print(f"  {Fore.GREEN}Software-AI 1.0.0{reset}  |  AI-Powered Windows Agent")
    print(f"  {Fore.YELLOW}Type your request in natural language{reset}")
    print(f"  {Fore.YELLOW}Type 'help' for commands, 'exit' to quit{reset}")
    print(f"  {Fore.CYAN}Made By shahincodev{reset}")
    print()


def print_help() -> None:
    print(f"""
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
{Fore.CYAN}{'COMMANDS':^60}{Style.RESET_ALL}
{Fore.CYAN}{'='*60}{Style.RESET_ALL}

  {Fore.GREEN}Natural Language (Recommended):{Style.RESET_ALL}
    Just type what you want! Examples:
      Create a folder on D: named "project"
      Open Chrome and search for AI news
      What files are in my Downloads?
      Rename file X to Y
      Take a screenshot

  {Fore.YELLOW}Special Commands:{Style.RESET_ALL}
    help          Show this help
    clear         Clear the screen
    context       Show current system context
    screen        Show current screen state (OCR + elements)
    history       Show recent actions
    /new [name]   Create a new chat session
    /sessions     List all chat sessions
    /switch <id>  Switch to a different session
    /delete <id>  Delete a session
    /search <q>   Search across sessions
    /current      Show current session info
    /providers    Show API provider status
    /status       Show full system status (providers, health, memory)
    pause/resume  Pause or resume the session
    stop/exit     Exit the program

{Fore.CYAN}{'='*60}{Style.RESET_ALL}
""")


# ─────────────────────────────────────────────────────────────────────────────
# Main Agent Loop
# ─────────────────────────────────────────────────────────────────────────────

async def agent_loop(args: argparse.Namespace) -> None:
    """Main agent interaction loop — every input goes through the AI with system access."""

    # Initialize core components
    session_manager = SessionManager()

    # Try to load last session or create a new one
    recent_sessions = session_manager.get_recent_sessions(limit=1)
    if recent_sessions:
        current_session = recent_sessions[0]
        session_manager.set_current_session(current_session)
        print(f"{Fore.GREEN}Resumed session: {current_session.name}{Style.RESET_ALL}")
    else:
        current_session = session_manager.create_session()
        print(f"{Fore.GREEN}New session: {current_session.name}{Style.RESET_ALL}")

    memory = MemoryManager(session_id=current_session.id)
    voice = VoiceManager(tts_provider=args.tts_provider)
    action_controller = ActionController(dry_run=args.dry_run)
    intent_router = IntentRouter()
    ai_brain = AIBrain()
    windows_env = WindowsEnvironment()
    system_context = SystemContext()
    vision = DesktopVision()
    vision_loop = VisionLoopManager(vision=vision)
    tool_executor = ToolExecutor(action_controller, vision_loop, safety_mode=args.safety_mode, ai_brain=ai_brain, memory_manager=memory)
    chat_brain = AIBrain()

    # Safety
    session_control = SafetyConsentManager()

    print_banner()

    # Session state
    paused = False
    action_history: list[dict[str, Any]] = []

    def log_event(event: str, **data: Any) -> None:
        try:
            payload = " ".join(f"{k}={v}" for k, v in data.items()) if data else ""
            logger.info("TELEMETRY event=%s %s", event, payload)
        except Exception:
            pass

    try:
        while True:
            # Get user input
            if args.input_mode == "voice":
                print(f"{Fore.CYAN}Listening...{Style.RESET_ALL}")
                user_text, detected_lang = voice.listen(timeout=10)
                if not user_text:
                    print(f"{Fore.YELLOW}No voice input detected.{Style.RESET_ALL}")
                    continue
                print(f"{Fore.GREEN}> {user_text}{Style.RESET_ALL}")
            else:
                try:
                    user_text = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
                except (EOFError, KeyboardInterrupt):
                    break

            if not user_text:
                continue

            # Phase 8: Input sanitization — strip leading backslashes and control chars
            user_text = user_text.lstrip("\\").strip()
            if not user_text:
                continue

            cmd_lower = user_text.lower()

            # ── Session control commands ──
            if cmd_lower in ("exit", "quit", "q"):
                print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}\n")
                break

            if cmd_lower == "stop":
                print(f"{Fore.RED}Session stopped.{Style.RESET_ALL}\n")
                break

            if cmd_lower == "help":
                print_help()
                continue

            if cmd_lower == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue

            if cmd_lower == "pause":
                paused = True
                print(f"{Fore.YELLOW}Paused. Type 'resume' to continue.{Style.RESET_ALL}")
                continue

            if cmd_lower == "resume":
                paused = False
                print(f"{Fore.GREEN}Resumed.{Style.RESET_ALL}")
                continue

            if paused:
                print(f"{Fore.YELLOW}Paused. Type 'resume' to continue.{Style.RESET_ALL}")
                continue

            # ── Session management commands (Phase 6) ──
            if cmd_lower.startswith("/new"):
                parts = cmd_lower.split(maxsplit=1)
                name = parts[1] if len(parts) > 1 else None
                current_session = session_manager.create_session(name)
                memory.set_session_id(current_session.id)
                print(f"{Fore.GREEN}New session created: {current_session.name}{Style.RESET_ALL}")
                continue

            if cmd_lower == "/sessions":
                sessions = session_manager.list_sessions()
                if not sessions:
                    print(f"{Fore.YELLOW}No sessions found.{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.CYAN}Chat Sessions:{Style.RESET_ALL}")
                    for s in sessions:
                        marker = " * " if current_session and s.id == current_session.id else "   "
                        updated = datetime.fromtimestamp(s.updated_at).strftime("%Y-%m-%d %H:%M")
                        print(f"{marker}{Fore.GREEN}{s.name}{Style.RESET_ALL} ({s.message_count} msgs, {updated})")
                    print()
                continue

            if cmd_lower.startswith("/switch"):
                parts = cmd_lower.split(maxsplit=1)
                if len(parts) < 2:
                    print(f"{Fore.RED}Usage: /switch <session_name_or_id>{Style.RESET_ALL}")
                    continue
                identifier = parts[1].strip()
                session = session_manager.switch_session(identifier)
                if session:
                    current_session = session
                    memory.set_session_id(session.id)
                    print(f"{Fore.GREEN}Switched to: {session.name}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Session not found: {identifier}{Style.RESET_ALL}")
                continue

            if cmd_lower.startswith("/delete"):
                parts = cmd_lower.split(maxsplit=1)
                if len(parts) < 2:
                    print(f"{Fore.RED}Usage: /delete <session_name_or_id>{Style.RESET_ALL}")
                    continue
                identifier = parts[1].strip()
                if session_manager.delete_session_by_name(identifier) or session_manager.delete_session(identifier):
                    print(f"{Fore.GREEN}Session deleted: {identifier}{Style.RESET_ALL}")
                    if not current_session or (current_session and current_session.name == identifier):
                        current_session = session_manager.create_session()
                        memory.set_session_id(current_session.id)
                        print(f"{Fore.GREEN}New session: {current_session.name}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Session not found: {identifier}{Style.RESET_ALL}")
                continue

            if cmd_lower.startswith("/search"):
                parts = cmd_lower.split(maxsplit=1)
                if len(parts) < 2:
                    print(f"{Fore.RED}Usage: /search <query>{Style.RESET_ALL}")
                    continue
                query = parts[1].strip()
                results = session_manager.search_sessions(query)
                if not results:
                    print(f"{Fore.YELLOW}No sessions found matching: {query}{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.CYAN}Search Results ({len(results)} sessions):{Style.RESET_ALL}")
                    for s in results:
                        updated = datetime.fromtimestamp(s.updated_at).strftime("%Y-%m-%d %H:%M")
                        print(f"  {Fore.GREEN}{s.name}{Style.RESET_ALL} ({s.message_count} msgs, {updated})")
                    print()
                continue

            if cmd_lower == "/current":
                if current_session:
                    print(f"\n{Fore.CYAN}Current Session:{Style.RESET_ALL}")
                    print(f"  Name: {current_session.name}")
                    print(f"  ID: {current_session.id}")
                    print(f"  Messages: {current_session.message_count}")
                    created = datetime.fromtimestamp(current_session.created_at).strftime("%Y-%m-%d %H:%M:%S")
                    print(f"  Created: {created}")
                else:
                    print(f"{Fore.YELLOW}No active session.{Style.RESET_ALL}")
                print()
                continue

            if cmd_lower == "context":
                print(f"\n{Fore.CYAN}System Context:{Style.RESET_ALL}")
                print(system_context.get_context())
                print()
                continue

            if cmd_lower == "screen":
                print(f"\n{Fore.CYAN}Screen State:{Style.RESET_ALL}")
                try:
                    desc = vision_loop.describe_screen()
                    print(desc)
                except Exception as e:
                    print(f"{Fore.RED}Failed to observe screen: {e}{Style.RESET_ALL}")
                print()
                continue

            if cmd_lower == "history":
                if not action_history:
                    print(f"{Fore.YELLOW}No actions yet.{Style.RESET_ALL}\n")
                else:
                    print(f"\n{Fore.CYAN}Recent Actions:{Style.RESET_ALL}")
                    for a in action_history[-10:]:
                        status = a.get("status", "?")
                        desc = a.get("description", "unknown")
                        icon = f"{Fore.GREEN}+" if status == "success" else f"{Fore.RED}X" if status == "failed" else f"{Fore.YELLOW}~"
                        print(f"  {icon}{Style.RESET_ALL} {desc}")
                    print()
                continue

            # Phase 8: Provider status command
            if cmd_lower == "/providers":
                try:
                    from core.ai_brain import ProviderDetector, ModelCircuitBreaker
                    detector = ProviderDetector()
                    providers = detector.get_all_status()
                    print(f"\n{Fore.CYAN}API Provider Status:{Style.RESET_ALL}")
                    for name, status in providers.items():
                        icon = f"{Fore.GREEN}ACTIVE" if status.is_available else f"{Fore.RED}INACTIVE"
                        key_info = f"key: {status.api_key_env}" if status.api_key_set else "no key"
                        print(f"  {icon}{Style.RESET_ALL} {name:15s} ({key_info})")
                    available = detector.get_available_providers()
                    print(f"\n  {Fore.GREEN}{len(available)} active provider(s){Style.RESET_ALL}")

                    # Circuit breaker status
                    cb = ModelCircuitBreaker()
                    cb_status = cb.get_status()
                    if cb_status:
                        print(f"\n{Fore.CYAN}Circuit Breaker Status:{Style.RESET_ALL}")
                        for model, info in cb_status.items():
                            if info["locked"]:
                                print(f"  {Fore.RED}LOCKED{Style.RESET_ALL} {model} ({info['locked_seconds_remaining']}s remaining, {info['reason']})")
                            else:
                                print(f"  {Fore.YELLOW}failures={info['failures']}{Style.RESET_ALL} {model}")
                    print()
                except Exception as e:
                    print(f"{Fore.RED}Failed to get provider status: {e}{Style.RESET_ALL}")
                continue

            # Phase 9: System status command
            if cmd_lower == "/status":
                try:
                    from core.ai_brain import ProviderDetector, ModelCircuitBreaker, ResponseCache
                    from core.model_config import get_health_tracker
                    detector = ProviderDetector()
                    cb = ModelCircuitBreaker()
                    tracker = get_health_tracker()

                    available = detector.get_available_providers()
                    cb_status = cb.get_status()
                    health_report = tracker.get_health_report()

                    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}  Software-AI System Status  (v1.0.0){Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

                    # Providers
                    print(f"\n{Fore.WHITE}Providers:{Style.RESET_ALL}")
                    print(f"  Active: {Fore.GREEN}{len(available)}{Style.RESET_ALL}")
                    for p in available:
                        print(f"    {Fore.GREEN}+{Style.RESET_ALL} {p}")

                    # Circuit Breaker
                    locked_count = sum(1 for v in cb_status.values() if v["locked"])
                    print(f"\n{Fore.WHITE}Circuit Breaker:{Style.RESET_ALL}")
                    print(f"  Locked models: {Fore.RED if locked_count else Fore.GREEN}{locked_count}{Style.RESET_ALL}")

                    # Health Report
                    if health_report:
                        print(f"\n{Fore.WHITE}Model Health:{Style.RESET_ALL}")
                        for name, info in sorted(health_report.items(), key=lambda x: x[1]["score"], reverse=True):
                            color = Fore.GREEN if info["score"] >= 50 else Fore.YELLOW if info["score"] >= 20 else Fore.RED
                            print(f"  {color}{info['score']:3d}{Style.RESET_ALL} {name} ({info['rate']} success, {info['total']} attempts)")

                    # Memory
                    try:
                        from core.memory_integrator import MemoryManager
                        mm = MemoryManager()
                        conv_count = len(mm._conversation_history)
                        print(f"\n{Fore.WHITE}Memory:{Style.RESET_ALL}")
                        print(f"  Conversation messages: {conv_count}")
                    except Exception:
                        pass

                    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
                except Exception as e:
                    print(f"{Fore.RED}Failed to get status: {e}{Style.RESET_ALL}")
                continue

            # ── Agent Processing ──
            log_event("agent_start", text=user_text[:100])
            print(f"{Fore.CYAN}⏳ Analyzing request...{Style.RESET_ALL}", end="", flush=True)

            # Record user message in conversation history
            try:
                memory.add_conversation("user", user_text, metadata={"action_type": "pending"})
            except Exception:
                pass

            # Step 1: Build system context
            context_str = system_context.get_context()

            # Step 1.2: Add environment context (Phase 7)
            try:
                env_context = windows_env.get_context_summary()
                if env_context:
                    context_str = f"{context_str}\n\n{env_context}"
            except Exception as e:
                logger.warning("Failed to get environment context: %s", e)

            # Step 1.5: Observe screen for vision context (Phase 3)
            screen_context_str = ""
            try:
                screen_context_str = vision_loop.get_screen_context()
            except Exception as e:
                logger.warning("Failed to get screen context: %s", e)

            # Step 1.7: Build memory context (Phase 5)
            memory_context_str = ""
            try:
                memory_context_str = memory.get_memory_context(max_items=5)
            except Exception as e:
                logger.warning("Failed to get memory context: %s", e)

            # Step 2: AI decides what to do (with system + screen + memory context)
            print(f"{Fore.MAGENTA}Thinking...{Style.RESET_ALL}", end="", flush=True)

            agent_response = await ai_brain.agent_chat(
                user_message=user_text,
                system_context=context_str,
                last_actions=action_history,
                screen_context=screen_context_str,
                memory_context=memory_context_str,
            )

            action_type = agent_response.get("action", "chat_reply")
            print(f"\r{Fore.GREEN}✓ Analysis complete{Style.RESET_ALL}      ")

            # Step 3: Execute based on AI decision
            if action_type == "tool_call":
                tool_calls = agent_response.get("tool_calls", [])
                if tool_calls:
                    print(f"\r{Fore.CYAN}Executing {len(tool_calls)} action(s)...{Style.RESET_ALL}")
                    results = await tool_executor.execute(tool_calls)

                    # Display results
                    for r in results:
                        status = r.get("status", "unknown")
                        desc = r.get("description", "unknown")
                        output = r.get("output", "")
                        error = r.get("error", "")

                        if status == "success":
                            print(f"  {Fore.GREEN}+ {desc}{Style.RESET_ALL}")
                            if output:
                                # Show brief output
                                brief = output.split("\n")[0][:100]
                                print(f"    {Fore.WHITE}{brief}{Style.RESET_ALL}")
                        else:
                            print(f"  {Fore.RED}X {desc}: {error}{Style.RESET_ALL}")

                        # Record in history and context
                        action_record = {
                            "status": status,
                            "description": desc,
                            "command": r.get("command", ""),
                            "output": output[:200],
                            "timestamp": datetime.now().isoformat(),
                        }
                        action_history.append(action_record)
                        system_context.record_action(action_record)

                    # Step 4: AI summarizes what it did
                    results_summary = "\n".join(
                        f"- [{'OK' if r['status']=='success' else 'FAIL'}] {r['description']}"
                        + (f": {r.get('error','')}" if r.get('error') else "")
                        for r in results
                    )

                    summary_prompt = (
                        f"User asked: {user_text}\n\n"
                        f"Actions executed:\n{results_summary}\n\n"
                        f"Respond to the user in 1-2 sentences about what was done. "
                        f"Be concise and direct."
                    )
                    try:
                        summary = await chat_brain.ask_with_fallback(summary_prompt, mode="system", max_tokens=300)
                        if summary:
                            print(f"\n{Fore.CYAN}{summary}{Style.RESET_ALL}\n")
                            # Store assistant summary in conversation history
                            try:
                                memory.add_conversation("assistant", summary, metadata={"action_type": "tool_summary"})
                            except Exception:
                                pass
                    except Exception:
                        print()

                    log_event("agent_tool_exec", actions=len(tool_calls),
                              successes=sum(1 for r in results if r["status"] == "success"))
                else:
                    print(f"\r{Fore.YELLOW}No actions to execute.{Style.RESET_ALL}\n")

            elif action_type == "chat_reply":
                response_text = agent_response.get("response", "I couldn't process that.")
                print(f"\r{Fore.CYAN}{response_text}{Style.RESET_ALL}\n")
                log_event("agent_chat")
                # Store assistant response in conversation history
                try:
                    memory.add_conversation("assistant", response_text, metadata={"action_type": "chat_reply"})
                except Exception:
                    pass

            else:
                print(f"\r{Fore.YELLOW}Unknown response type.{Style.RESET_ALL}\n")

            # Record user request in memory
            try:
                memory.remember_short(
                    content=user_text, ttl=3600,
                    metadata={"type": "user_request", "action_type": action_type}
                )
            except Exception:
                pass

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted. Shutting down...{Style.RESET_ALL}")
    finally:
        try:
            session_manager.close()
            memory.shutdown()
            voice.shutdown()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    session_log = None
    try:
        args = parse_arguments()
        load_dotenv()

        # Ensure directories exist
        for d in ["data/logs", "data/logs/sessions", "data/logs/cache"]:
            Path(d).mkdir(parents=True, exist_ok=True)

        session_log, master_log = setup_logging(level=logging.DEBUG if args.debug else None)
        install_exception_hook()

        print(f"\n{Fore.CYAN}Logging:{Style.RESET_ALL} {session_log}")
        logger.info("Application started: input_mode=%s, safety=%s", args.input_mode, args.safety_mode)

        await agent_loop(args)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        logger.exception("Fatal error")
        sys.exit(1)
    finally:
        if session_log:
            logger.info("SESSION ENDED: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    asyncio.run(main())
