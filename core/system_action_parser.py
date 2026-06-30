"""Natural language parser for system actions.

Extracted from core/intent_analyzer.py to reduce module size.
Maintains full backward compatibility.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.ai_brain import AIBrain
from core.system_capabilities import SystemCapabilityRegistry

logger = logging.getLogger(__name__)


class SystemActionParser:
    """Convert natural language requests to structured system/Desktop actions."""

    def __init__(self, registry: SystemCapabilityRegistry):
        self.registry = registry
        self.ai_brain = AIBrain()

        self.click_patterns = [
            r'click\s+(?:on\s+)?["\']([^"\']+)["\']',
            r'click\s+(?:on\s+)?(\w+)',
            r'کلیک\s+(?:روی\s+)?["\']([^"\']+)["\']',
            r'کلیک\s+(?:روی\s+)?(\S+)',
            r'press\s+(?:on\s+)?["\']([^"\']+)["\']',
            r'press\s+(?:on\s+)?(\w+)',
            r'بزن\s+(?:روی\s+)?["\']([^"\']+)["\']',
            r'بزن\s+(?:روی\s+)?(\S+)',
        ]

        self.type_patterns = [
            r'type\s+["\']([^"\']+)["\']',
            r'تایپ\s+["\']([^"\']+)["\']',
            r'write\s+["\']([^"\']+)["\']',
            r'بنویس\s+["\']([^"\']+)["\']',
            r'enter\s+["\']([^"\']+)["\']',
            r'type\s+(\S.+?)(?:\.|,| and | then |$)',
            r'write\s+(\S.+?)(?:\.|,| and | then |$)',
            r'enter\s+(\S.+?)(?:\.|,| and | then |$)',
        ]

        self.drag_patterns = [
            r'drag\s+["\']?([^"\']+?)["\']?\s+to\s+["\']?([^"\']+)["\']?',
            r'بکش\s+["\']?([^"\']+?)["\']?\s+به\s+["\']?([^"\']+)["\']?',
            r'move\s+["\']?([^"\']+?)["\']?\s+to\s+["\']?([^"\']+)["\']?',
        ]

        self.logger = logger

    async def parse_request(self, user_request: str) -> list[dict[str, Any]]:
        logger.info("Processing request with AI: %s", user_request)
        try:
            ai_response = await self.ai_brain.interpret_system_request(user_request)
            if ai_response and isinstance(ai_response, list):
                logger.info("AI extracted %d actions", len(ai_response))
                return ai_response
            logger.warning("AI returned invalid response, trying fallback")
        except Exception as e:
            logger.error("AI interpretation failed: %s", e)

        actions = await self._simple_fallback_parse(user_request)
        logger.info("Extracted %d actions from fallback", len(actions))
        return actions

    async def _simple_fallback_parse(self, user_request: str) -> list[dict[str, Any]]:
        user_lower = user_request.lower()
        actions = []

        if any(kw in user_lower for kw in ['open', 'launch', 'start', 'run', 'باز', 'اجرا', 'شروع']):
            app_name = await self._ai_extract_app_name(user_request)
            if app_name:
                actions.append({
                    "type": "LaunchApp",
                    "params": {"app_name": app_name, "arguments": [], "require_consent": False},
                    "priority": "normal",
                    "description": f"Open {app_name}"
                })

        if any(kw in user_lower for kw in ['install', 'setup', 'نصب']):
            package = await self._ai_extract_package_name(user_request)
            if package:
                actions.append({
                    "type": "InstallPackage",
                    "params": {"package_name": package, "package_manager": "winget", "silent": True},
                    "priority": "normal",
                    "description": f"Install {package}"
                })

        if any(kw in user_lower for kw in ['close', 'kill', 'terminate', 'stop', 'بستن', 'توقف']):
            process = await self._ai_extract_app_name(user_request)
            if process:
                actions.append({
                    "type": "TerminateProcess",
                    "params": {"process_name": process, "force": False},
                    "priority": "normal",
                    "description": f"Close {process}"
                })

        if any(kw in user_lower for kw in ['create', 'make', 'new', 'build', 'ایجاد', 'ساخت', 'جدید']):
            # ── Resolve target location via _detect_location ───────────
            location = self._detect_location(user_request)
            if not location:
                location = str(Path.home() / "Desktop")

            # ── Create folder ──────────────────────────────────────────
            folder_keywords = ['folder', 'directory', 'پوشه', 'دایرکتوری']
            if any(kw in user_lower for kw in folder_keywords):
                folder_name = self._extract_name_after_keyword(
                    user_request, ['folder', 'directory', 'پوشه', 'دایرکتوری called', 'named', 'نام'])
                if not folder_name:
                    folder_name = "New Folder"
                folder_path = str(Path(location) / folder_name)
                actions.append({
                    "type": "ExecuteCommand",
                    "params": {
                        "command": f'mkdir "{folder_path}" 2>nul',
                        "shell": "cmd",
                        "timeout": 10
                    },
                    "priority": "normal",
                    "description": f"Create folder '{folder_name}' ({location})"
                })

            # ── Create file ────────────────────────────────────────────
            file_keywords = ['file', 'document', 'text', 'فایل', 'متن']
            if any(kw in user_lower for kw in file_keywords):
                file_name = self._extract_name_after_keyword(
                    user_request, ['file', 'document', 'فایل', 'document called', 'named', 'نام'])
                if not file_name:
                    file_name = "new_file.txt"
                file_path = str(Path(location) / file_name)
                actions.append({
                    "type": "ExecuteCommand",
                    "params": {
                        "command": f'type nul > "{file_path}" 2>nul',
                        "shell": "cmd",
                        "timeout": 10
                    },
                    "priority": "normal",
                    "description": f"Create file '{file_name}' ({location})"
                })

        if any(kw in user_lower for kw in ['hardware', 'سخت‌افزار', 'cpu', 'ram', 'memory', 'info']):
            actions.append({
                "type": "QueryHardware",
                "params": {"query_type": "all"},
                "priority": "normal",
                "description": "Get hardware information"
            })

        click_action = self._parse_click_action(user_request)
        if click_action:
            actions.append(click_action)

        type_action = self._parse_type_action(user_request)
        if type_action:
            actions.append(type_action)

        drag_action = self._parse_drag_action(user_request)
        if drag_action:
            actions.append(drag_action)

        wait_action = self._parse_wait_action(user_request)
        if wait_action:
            actions.append(wait_action)

        hotkey_action = self._parse_hotkey_action(user_request)
        if hotkey_action:
            actions.append(hotkey_action)

        scroll_action = self._parse_scroll_action(user_request)
        if scroll_action:
            actions.append(scroll_action)

        return actions

    def _parse_click_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['click', 'کلیک', 'press', 'بزن']):
            return None

        for pattern in self.click_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                button = "left"
                if any(kw in request_lower for kw in ['right', 'راست']):
                    button = "right"
                elif any(kw in request_lower for kw in ['middle', 'وسط']):
                    button = "middle"
                clicks = 2 if any(kw in request_lower for kw in ['double', 'دوبار', 'دابل']) else 1
                return {
                    "type": "DesktopClick",
                    "params": {"target": target, "button": button, "clicks": clicks},
                    "priority": "normal",
                    "description": f"Click on '{target}'"
                }
        return None

    def _parse_type_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['type', 'تایپ', 'write', 'بنویس', 'enter']):
            return None

        for pattern in self.type_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                target = None
                target_pattern = r'(?:in|into|at|در|توی)\s+["\']?(.+?)["\']?(?:\s|$)'
                target_match = re.search(target_pattern, request, re.IGNORECASE)
                if target_match:
                    target = target_match.group(1).strip()
                return {
                    "type": "DesktopType",
                    "params": {"text": text, "target": target},
                    "priority": "normal",
                    "description": f"Type '{text[:30]}...'" if len(text) > 30 else f"Type '{text}'"
                }
        return None

    def _parse_drag_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['drag', 'بکش', 'move']):
            return None
        for pattern in self.drag_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                source = match.group(1).strip()
                target = match.group(2).strip()
                return {
                    "type": "DesktopDragDrop",
                    "params": {"source": source, "target": target},
                    "priority": "normal",
                    "description": f"Drag '{source}' to '{target}'"
                }
        return None

    def _parse_wait_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['wait', 'صبر', 'انتظار']):
            return None

        wait_type = "time"
        target: Any = 3.0
        if any(kw in request_lower for kw in ['for', 'until', 'برای', 'تا']):
            element_pattern = r'(?:for|until|برای|تا)\s+["\']?(.+?)["\']?(?:\s|$)'
            match = re.search(element_pattern, request, re.IGNORECASE)
            if match:
                wait_type = "element"
                target = match.group(1).strip()
        else:
            time_pattern = r'(\d+(?:\.\d+)?)\s*(?:second|sec|ثانیه)?'
            match = re.search(time_pattern, request)
            if match:
                target = float(match.group(1))

        return {
            "type": "DesktopWait",
            "params": {"wait_type": wait_type, "target": target, "timeout": 30},
            "priority": "normal",
            "description": f"Wait for {target}"
        }

    def _parse_hotkey_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        hotkey_map = {
            'copy': ['ctrl', 'c'], 'کپی': ['ctrl', 'c'],
            'paste': ['ctrl', 'v'], 'پیست': ['ctrl', 'v'],
            'cut': ['ctrl', 'x'], 'برش': ['ctrl', 'x'],
            'undo': ['ctrl', 'z'], 'بازگشت': ['ctrl', 'z'],
            'redo': ['ctrl', 'y'],
            'save': ['ctrl', 's'], 'ذخیره': ['ctrl', 's'],
            'select all': ['ctrl', 'a'],
            'find': ['ctrl', 'f'], 'جستجو': ['ctrl', 'f'],
            'alt tab': ['alt', 'tab'], 'تعویض پنجره': ['alt', 'tab'],
        }
        for phrase, keys in hotkey_map.items():
            if phrase in request_lower:
                return {
                    "type": "DesktopHotkey",
                    "params": {"keys": keys},
                    "priority": "normal",
                    "description": f"Press {'+'.join(keys)}"
                }

        hotkey_pattern = r'(ctrl|alt|shift|win)[\s+]+(ctrl|alt|shift|win|[a-z0-9])'
        match = re.search(hotkey_pattern, request_lower)
        if match:
            keys = [match.group(1), match.group(2)]
            return {
                "type": "DesktopHotkey",
                "params": {"keys": keys},
                "priority": "normal",
                "description": f"Press {'+'.join(keys)}"
            }
        return None

    def _parse_scroll_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['scroll', 'اسکرول']):
            return None

        direction = "down"
        if any(kw in request_lower for kw in ['up', 'بالا']):
            direction = "up"
        elif any(kw in request_lower for kw in ['down', 'پایین']):
            direction = "down"
        elif any(kw in request_lower for kw in ['left', 'چپ']):
            direction = "left"
        elif any(kw in request_lower for kw in ['right', 'راست']):
            direction = "right"

        clicks = 3
        amount_pattern = r'(\d+)\s*(?:time|times|بار)?'
        match = re.search(amount_pattern, request)
        if match:
            clicks = int(match.group(1))

        return {
            "type": "DesktopScroll",
            "params": {"direction": direction, "clicks": clicks},
            "priority": "normal",
            "description": f"Scroll {direction} {clicks} times"
        }

    async def _ai_extract_app_name(self, request: str) -> Optional[str]:
        try:
            prompt = f"""Extract the application name from this request and return ONLY the executable name with .exe extension.
If the app is common, use standard Windows executable names.

Request: {request}

Examples:
- "open steam" → steam.exe
- "باز کن استیم" → steam.exe
- "launch chrome" → chrome.exe
- "run notepad" → notepad.exe
- "اجرا کن فتوشاپ" → photoshop.exe

Return ONLY the .exe filename, nothing else:"""

            response = await self.ai_brain.ask(prompt, mode="system", max_tokens=50)

            if response:
                if isinstance(response, str):
                    exe_name = response.strip().lower()
                elif hasattr(response, 'content'):
                    exe_name = response.content.strip().lower()
                elif hasattr(response, 'completion'):
                    exe_name = response.completion.strip().lower()
                else:
                    logger.error("Unexpected response type: %s", type(response))
                    exe_name = str(response).strip().lower()

                exe_name = exe_name.strip("\"'` \n\t")
                if not exe_name.endswith('.exe'):
                    exe_name += '.exe'
                logger.info("AI extracted app name: %s", exe_name)
                return exe_name
        except Exception as e:
            logger.error("AI app extraction failed: %s", e)

        match = re.search(r'(?:open|launch|start|run|باز|اجرا|شروع)\s+(\w+)', request, re.IGNORECASE)
        if match:
            app_name = match.group(1).lower()
            if not app_name.endswith('.exe'):
                app_name += '.exe'
            logger.info("Regex fallback extracted app name: %s", app_name)
            return app_name
        return None

    async def _ai_extract_package_name(self, request: str) -> Optional[str]:
        try:
            prompt = f"""Extract the package/software name from this installation request.
Return ONLY the package name that can be used with winget or pip.

Request: {request}

Examples:
- "install git" → git
- "نصب پایتون" → python
- "setup nodejs" → nodejs
- "نصب کن docker" → docker

Return ONLY the package name:"""

            response = await self.ai_brain.ask(prompt, mode="system", max_tokens=30)
            if response:
                package = response.strip().lower()
                logger.info("AI extracted package: %s", package)
                return package
        except Exception as e:
            logger.error("AI package extraction failed: %s", e)
        return None

    def _extract_app_name(self, request: str) -> Optional[str]:
        exe_match = re.search(r'(\w+\.exe)', request, re.IGNORECASE)
        if exe_match:
            return exe_match.group(1)
        return None

    def _extract_package_name(self, request: str) -> Optional[str]:
        words = request.split()
        if words:
            return words[-1]
        return None

    def _extract_process_name(self, request: str) -> Optional[str]:
        return self._extract_app_name(request)

    def _extract_name_after_keyword(self, request: str, keywords: list[str]) -> Optional[str]:
        location_words = ['on', 'in', 'at', 'to', 'into', 'onto', 'under', 'روی', 'در', 'به', 'توی']
        for kw in keywords:
            quoted = re.search(
                rf"""\b{re.escape(kw)}\s+["'""]([^"'""]+)["'""]""",
                request, re.IGNORECASE
            )
            if quoted:
                return quoted.group(1).strip()
            else:
                word_after = re.search(rf'\b{re.escape(kw)}\s+(\S+)', request, re.IGNORECASE)
                if word_after:
                    name = word_after.group(1).strip().rstrip('.,;:\'"')
                    if name and len(name) < 100 and name.lower() not in location_words:
                        return name
        return None

    def _detect_location(self, request: str) -> Optional[str]:
        """Detect a filesystem location from natural language.

        Understands:
          "drive D", "D drive", "D:"          → D:\\
          "Desktop"                            → C:\\Users\\<user>\\Desktop
          "Downloads"                          → C:\\Users\\<user>\\Downloads
          "Documents"                          → C:\\Users\\<user>\\Documents
          "C:\\path\\to\\folder"              → C:\\path\\to\\folder
          Persian equivalents of the above
        """
        req_lower = request.lower()
        home = Path.home()

        # ── Drive-letter patterns ──────────────────────────────────────
        # "drive D", "D drive", "D:", "in D:"
        drive_pats = [
            r'drive\s+([A-Za-z])\b',
            r'\b([A-Za-z])\s+drive\b',
            r'\b([A-Za-z]):(?=\s|\\|/|$|\.)',
        ]
        for pat in drive_pats:
            m = re.search(pat, request, re.IGNORECASE)
            if m:
                letter = m.group(1).upper()
                if 'A' <= letter <= 'Z':
                    return f"{letter}:\\"

        # ── Known shell folders (English + Persian) ────────────────────
        known = {
            'desktop':   home / 'Desktop',
            'میز':       home / 'Desktop',
            'دسکتاپ':    home / 'Desktop',
            'downloads': home / 'Downloads',
            'دانلود':    home / 'Downloads',
            'documents': home / 'Documents',
            'اسناد':     home / 'Documents',
            'مدارک':     home / 'Documents',
        }
        for keyword, resolved in known.items():
            if keyword in req_lower:
                return str(resolved)

        # ── Explicit absolute Windows paths ────────────────────────────
        abs_pats = [
            r'(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?([A-Za-z]:\\[^\s"\']+)["\']?',
            r'(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?(\\\\[^\s"\']+)["\']?',
            r'([A-Za-z]:\\[^\s"\']+)',
        ]
        for pat in abs_pats:
            m = re.search(pat, request, re.IGNORECASE)
            if m:
                raw = m.group(1).strip().strip('"\'')
                try:
                    p = Path(raw)
                    if not any(ch in raw for ch in '*?<>|'):
                        return str(p)
                except Exception:
                    pass

        return None

    def _extract_path(self, request: str) -> Optional[str]:
        """Legacy wrapper -- delegates to _detect_location."""
        return self._detect_location(request)
