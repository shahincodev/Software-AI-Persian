# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""سیستم تشخیص و اجرای هوشمند اقدامات سیستمی با AI.

این ماژول از LLM برای تفسیر درخواست‌های کاربر و تبدیل آن‌ها به اقدامات سیستمی استفاده می‌کند.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

from .ai_brain import AIBrain
from .execution_manager import ExecutionManager, ExecutionPriority
from .system_actions import (
    InstallPackageAction,
    LaunchAppAction,
    QueryHardwareAction,
    TerminateProcessAction,
    ExecuteCommandAction,
)
from .system_capabilities import SystemCapabilityRegistry
from .desktop_actions import (
    ClickAction,
    TypeAction,
    WaitAction,
    DragDropAction,
    HotkeyAction,
    ScrollAction,
)
from .action_controller import ActionController

logger = logging.getLogger(__name__)


class SystemActionParser:
    """تبدیل درخواست‌های طبیعی کاربر به اقدامات سیستمی و Desktop."""
    
    def __init__(self, registry: SystemCapabilityRegistry):
        self.registry = registry
        self.ai_brain = AIBrain()
        
        # الگوهای رایج برای Desktop Actions
        self.click_patterns = [
            r'click\s+(?:on\s+)?["\']([^"\']+)["\']',  # با گیومه
            r'click\s+(?:on\s+)?(\w+)',  # بدون گیومه
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
        ]
        
        self.drag_patterns = [
            r'drag\s+["\']?([^"\']+?)["\']?\s+to\s+["\']?([^"\']+)["\']?',
            r'بکش\s+["\']?([^"\']+?)["\']?\s+به\s+["\']?([^"\']+)["\']?',
            r'move\s+["\']?([^"\']+?)["\']?\s+to\s+["\']?([^"\']+)["\']?',
        ]
    
    async def parse_request(self, user_request: str) -> list[dict[str, Any]]:
        """تجزیه درخواست کاربر و استخراج اقدامات با AI.
        
        این متد از هوش مصنوعی برای تفسیر درخواست استفاده می‌کند.
        
        Returns:
            لیستی از اقدامات در قالب دیکشنری
        """
        logger.info("🤖 Processing request with AI: %s", user_request)
        
        # استفاده از AI برای تجزیه درخواست
        try:
            ai_response = await self.ai_brain.interpret_system_request(user_request)
            
            if ai_response and isinstance(ai_response, list):
                logger.info("✅ AI extracted %d actions", len(ai_response))
                return ai_response
            
            logger.warning("⚠️ AI returned invalid response, trying fallback")
            
        except Exception as e:
            logger.error("❌ AI interpretation failed: %s", e)
        
        # Fallback: تلاش برای تشخیص ساده
        actions = await self._simple_fallback_parse(user_request)
        logger.info("Extracted %d actions from fallback", len(actions))
        return actions
    
    async def _simple_fallback_parse(self, user_request: str) -> list[dict[str, Any]]:
        """تجزیه ساده بدون AI برای موارد اضطراری."""
        user_lower = user_request.lower()
        actions = []
        
        # Desktop Actions با Regex
        click_action = self._parse_click_action(user_request)
        if click_action:
            return [click_action]
        
        type_action = self._parse_type_action(user_request)
        if type_action:
            return [type_action]
        
        drag_action = self._parse_drag_action(user_request)
        if drag_action:
            return [drag_action]
        
        wait_action = self._parse_wait_action(user_request)
        if wait_action:
            return [wait_action]
        
        hotkey_action = self._parse_hotkey_action(user_request)
        if hotkey_action:
            return [hotkey_action]
        
        scroll_action = self._parse_scroll_action(user_request)
        if scroll_action:
            return [scroll_action]
        
        # System Actions - استفاده از AI برای استخراج نام
        if any(kw in user_lower for kw in ['open', 'launch', 'start', 'run', 'باز', 'اجرا', 'شروع']):
            app_name = await self._ai_extract_app_name(user_request)
            if app_name:
                actions.append({
                    "type": "LaunchApp",
                    "params": {"app_name": app_name, "arguments": []},
                    "priority": "normal",
                    "description": f"Open {app_name}"
                })
        
        elif any(kw in user_lower for kw in ['install', 'setup', 'نصب']):
            package = await self._ai_extract_package_name(user_request)
            if package:
                actions.append({
                    "type": "InstallPackage",
                    "params": {"package_name": package, "package_manager": "winget", "silent": True},
                    "priority": "normal",
                    "description": f"Install {package}"
                })
        
        elif any(kw in user_lower for kw in ['close', 'kill', 'terminate', 'stop', 'بستن', 'توقف']):
            process = await self._ai_extract_app_name(user_request)
            if process:
                actions.append({
                    "type": "TerminateProcess",
                    "params": {"process_name": process, "force": False},
                    "priority": "normal",
                    "description": f"Close {process}"
                })
        
        elif any(kw in user_lower for kw in ['create', 'make', 'new', 'build', 'ایجاد', 'ساخت', 'جدید']):
            folder_keywords = ['folder', 'directory', 'پوشه', 'دایرکتوری']
            file_keywords = ['file', 'document', 'text', 'فایل', 'متن']
            is_folder = any(kw in user_lower for kw in folder_keywords)
            is_file = any(kw in user_lower for kw in file_keywords)
            
            if is_folder:
                # Extract folder name or generate a default one
                folder_name = self._extract_name_after_keyword(user_request, ['folder', 'directory', 'پوشه', 'دایرکتوری called', 'named', 'نام'])
                if not folder_name:
                    folder_name = "New Folder"
                
                # Determine location
                location = "desktop"
                if 'desktop' in user_lower or 'میز' in user_lower or 'دسکتاپ' in user_lower:
                    desktop = str(Path.home() / "Desktop")
                    folder_path = str(Path(desktop) / folder_name)
                else:
                    location_path = self._extract_path(user_request)
                    if location_path:
                        folder_path = str(Path(location_path) / folder_name)
                    else:
                        folder_path = str(Path.home() / "Desktop" / folder_name)
                
                actions.append({
                    "type": "ExecuteCommand",
                    "params": {
                        "command": f'mkdir "{folder_path}" 2>nul',
                        "shell": "cmd",
                        "timeout": 10
                    },
                    "priority": "normal",
                    "description": f"Create folder '{folder_name}' on {location}"
                })
            elif is_file:
                file_name = self._extract_name_after_keyword(user_request, ['file', 'document', 'فایل', 'document called', 'named', 'نام'])
                if not file_name:
                    file_name = "new_file.txt"
                
                if 'desktop' in user_lower or 'میز' in user_lower or 'دسکتاپ' in user_lower:
                    file_path = str(Path.home() / "Desktop" / file_name)
                else:
                    location_path = self._extract_path(user_request)
                    if location_path:
                        file_path = str(Path(location_path) / file_name)
                    else:
                        file_path = str(Path.home() / "Desktop" / file_name)
                
                actions.append({
                    "type": "ExecuteCommand",
                    "params": {
                        "command": f'type nul > "{file_path}" 2>nul',
                        "shell": "cmd",
                        "timeout": 10
                    },
                    "priority": "normal",
                    "description": f"Create file '{file_name}' on desktop"
                })
        
        elif any(kw in user_lower for kw in ['hardware', 'سخت‌افزار', 'cpu', 'ram', 'memory', 'info']):
            actions.append({
                "type": "QueryHardware",
                "params": {"query_type": "all"},
                "priority": "normal",
                "description": "Get hardware information"
            })
        
        return actions
    
    def _parse_click_action(self, request: str) -> Optional[dict[str, Any]]:
        """استخراج Click Action از درخواست."""
        request_lower = request.lower()
        
        # بررسی کلمات کلیدی
        if not any(kw in request_lower for kw in ['click', 'کلیک', 'press', 'بزن']):
            return None
        
        # استخراج target با regex
        for pattern in self.click_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                
                # تشخیص نوع دکمه
                button = "left"
                if any(kw in request_lower for kw in ['right', 'راست']):
                    button = "right"
                elif any(kw in request_lower for kw in ['middle', 'وسط']):
                    button = "middle"
                
                # تشخیص double click
                clicks = 2 if any(kw in request_lower for kw in ['double', 'دوبار', 'دابل']) else 1
                
                return {
                    "type": "DesktopClick",
                    "params": {
                        "target": target,
                        "button": button,
                        "clicks": clicks
                    },
                    "priority": "normal",
                    "description": f"Click on '{target}'"
                }
        
        return None
    
    def _parse_type_action(self, request: str) -> Optional[dict[str, Any]]:
        """استخراج Type Action از درخواست."""
        request_lower = request.lower()
        
        # بررسی کلمات کلیدی
        if not any(kw in request_lower for kw in ['type', 'تایپ', 'write', 'بنویس', 'enter']):
            return None
        
        # استخراج متن با regex
        for pattern in self.type_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                
                # استخراج target اگر وجود داشته باشد
                target = None
                target_pattern = r'(?:in|into|at|در|توی)\s+["\']?(.+?)["\']?(?:\s|$)'
                target_match = re.search(target_pattern, request, re.IGNORECASE)
                if target_match:
                    target = target_match.group(1).strip()
                
                return {
                    "type": "DesktopType",
                    "params": {
                        "text": text,
                        "target": target
                    },
                    "priority": "normal",
                    "description": f"Type '{text[:30]}...'" if len(text) > 30 else f"Type '{text}'"
                }
        
        return None
    
    def _parse_drag_action(self, request: str) -> Optional[dict[str, Any]]:
        """استخراج Drag & Drop Action از درخواست."""
        request_lower = request.lower()
        
        # بررسی کلمات کلیدی
        if not any(kw in request_lower for kw in ['drag', 'بکش', 'move']):
            return None
        
        # استخراج source و target
        for pattern in self.drag_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                source = match.group(1).strip()
                target = match.group(2).strip()
                
                return {
                    "type": "DesktopDragDrop",
                    "params": {
                        "source": source,
                        "target": target
                    },
                    "priority": "normal",
                    "description": f"Drag '{source}' to '{target}'"
                }
        
        return None
    
    def _parse_wait_action(self, request: str) -> Optional[dict[str, Any]]:
        """استخراج Wait Action از درخواست."""
        request_lower = request.lower()
        
        # بررسی کلمات کلیدی
        if not any(kw in request_lower for kw in ['wait', 'صبر', 'انتظار']):
            return None
        
        # استخراج نوع wait
        wait_type = "time"
        target = 3.0  # پیش‌فرض: 3 ثانیه
        
        # انتظار برای عنصر
        if any(kw in request_lower for kw in ['for', 'until', 'برای', 'تا']):
            element_pattern = r'(?:for|until|برای|تا)\s+["\']?(.+?)["\']?(?:\s|$)'
            match = re.search(element_pattern, request, re.IGNORECASE)
            if match:
                wait_type = "element"
                target = match.group(1).strip()
        else:
            # انتظار زمانی - استخراج عدد
            time_pattern = r'(\d+(?:\.\d+)?)\s*(?:second|sec|ثانیه)?'
            match = re.search(time_pattern, request)
            if match:
                target = float(match.group(1))
        
        return {
            "type": "DesktopWait",
            "params": {
                "wait_type": wait_type,
                "target": target,
                "timeout": 30
            },
            "priority": "normal",
            "description": f"Wait for {target}"
        }
    
    def _parse_hotkey_action(self, request: str) -> Optional[dict[str, Any]]:
        """استخراج Hotkey Action از درخواست."""
        request_lower = request.lower()
        
        # الگوهای شناخته شده
        hotkey_map = {
            'copy': ['ctrl', 'c'],
            'کپی': ['ctrl', 'c'],
            'paste': ['ctrl', 'v'],
            'پیست': ['ctrl', 'v'],
            'cut': ['ctrl', 'x'],
            'برش': ['ctrl', 'x'],
            'undo': ['ctrl', 'z'],
            'بازگشت': ['ctrl', 'z'],
            'redo': ['ctrl', 'y'],
            'save': ['ctrl', 's'],
            'ذخیره': ['ctrl', 's'],
            'select all': ['ctrl', 'a'],
            'find': ['ctrl', 'f'],
            'جستجو': ['ctrl', 'f'],
            'alt tab': ['alt', 'tab'],
            'تعویض پنجره': ['alt', 'tab'],
        }
        
        for phrase, keys in hotkey_map.items():
            if phrase in request_lower:
                return {
                    "type": "DesktopHotkey",
                    "params": {
                        "keys": keys
                    },
                    "priority": "normal",
                    "description": f"Press {'+'.join(keys)}"
                }
        
        # الگوی عمومی: Ctrl+C
        hotkey_pattern = r'(ctrl|alt|shift|win)[\s+]+(ctrl|alt|shift|win|[a-z0-9])'
        match = re.search(hotkey_pattern, request_lower)
        if match:
            keys = [match.group(1), match.group(2)]
            return {
                "type": "DesktopHotkey",
                "params": {
                    "keys": keys
                },
                "priority": "normal",
                "description": f"Press {'+'.join(keys)}"
            }
        
        return None
    
    def _parse_scroll_action(self, request: str) -> Optional[dict[str, Any]]:
        """استخراج Scroll Action از درخواست."""
        request_lower = request.lower()
        
        # بررسی کلمات کلیدی
        if not any(kw in request_lower for kw in ['scroll', 'اسکرول']):
            return None
        
        # تشخیص جهت
        direction = "down"  # پیش‌فرض
        if any(kw in request_lower for kw in ['up', 'بالا']):
            direction = "up"
        elif any(kw in request_lower for kw in ['down', 'پایین']):
            direction = "down"
        elif any(kw in request_lower for kw in ['left', 'چپ']):
            direction = "left"
        elif any(kw in request_lower for kw in ['right', 'راست']):
            direction = "right"
        
        # تشخیص مقدار
        clicks = 3  # پیش‌فرض
        amount_pattern = r'(\d+)\s*(?:time|times|بار)?'
        match = re.search(amount_pattern, request)
        if match:
            clicks = int(match.group(1))
        
        return {
            "type": "DesktopScroll",
            "params": {
                "direction": direction,
                "clicks": clicks
            },
            "priority": "normal",
            "description": f"Scroll {direction} {clicks} times"
        }
    
    
    async def _ai_extract_app_name(self, request: str) -> Optional[str]:
        """استخراج نام برنامه با AI."""
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
                # پاکسازی و استخراج نام exe
                # Response should be a string from ai_brain.ask()
                # If it's not a string, try to extract the content
                if isinstance(response, str):
                    exe_name = response.strip().lower()
                elif hasattr(response, 'content'):
                    exe_name = response.content.strip().lower()
                elif hasattr(response, 'completion'):
                    exe_name = response.completion.strip().lower()
                else:
                    logger.error("Unexpected response type: %s", type(response))
                    exe_name = str(response).strip().lower()
                
                # Clean up any quotation marks or extra whitespace
                exe_name = exe_name.strip("\"'` \n\t")
                
                if not exe_name.endswith('.exe'):
                    exe_name += '.exe'
                logger.info("🤖 AI extracted app name: %s", exe_name)
                return exe_name
        
        except Exception as e:
            logger.error("AI app extraction failed: %s", e)
        
        return None
    
    async def _ai_extract_package_name(self, request: str) -> Optional[str]:
        """استخراج نام پکیج با AI."""
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
                logger.info("🤖 AI extracted package: %s", package)
                return package
        
        except Exception as e:
            logger.error("AI package extraction failed: %s", e)
        
        return None
    
    def _extract_app_name(self, request: str) -> Optional[str]:
        """DEPRECATED: Use _ai_extract_app_name instead."""
        # فقط برای سازگاری با کد قدیمی - چک می‌کند .exe در متن باشد
        import re
        exe_match = re.search(r'(\w+\.exe)', request, re.IGNORECASE)
        if exe_match:
            return exe_match.group(1)
        return None
    
    def _extract_package_name(self, request: str) -> Optional[str]:
        """DEPRECATED: Use _ai_extract_package_name instead."""
        # آخرین کلمه را برمی‌گرداند
        words = request.split()
        if words:
            return words[-1]
        return None
    
    def _extract_process_name(self, request: str) -> Optional[str]:
        """DEPRECATED: Use _ai_extract_app_name instead."""
        return self._extract_app_name(request)
    
    def _extract_name_after_keyword(self, request: str, keywords: list[str]) -> Optional[str]:
        location_words = ['on', 'in', 'at', 'to', 'into', 'onto', 'under', 'روی', 'در', 'به', 'توی']
        for kw in keywords:
            # Try single or double quoted name: folder "My Folder" or folder 'My Folder'
            quoted = re.search(rf"""{re.escape(kw)}\s+["'""]([^"'""]+)["'""]""", request, re.IGNORECASE)
            if quoted:
                return quoted.group(1).strip()
            # Try "called/named X" pattern
            called = re.search(rf'{re.escape(kw)}\s+(?:called|named|به\s+نام)\s+["\']?([^"\']+?)["\']?(?:\s+|$)', request, re.IGNORECASE)
            if called:
                name = called.group(1).strip()
                if name and len(name) < 100 and name.lower() not in location_words:
                    return name
            # Skip if immediately followed by a location word
            for loc in location_words:
                if re.search(rf'{re.escape(kw)}\s+{re.escape(loc)}\b', request, re.IGNORECASE):
                    break
            else:
                # Not followed by location word — capture next word(s) as name
                word_after = re.search(rf'{re.escape(kw)}\s+(\S+)', request, re.IGNORECASE)
                if word_after:
                    name = word_after.group(1).strip().rstrip('.,;:\'"')
                    if name and len(name) < 100 and name.lower() not in location_words:
                        return name
        return None

    def _extract_path(self, request: str) -> Optional[str]:
        """استخراج مسیر از درخواست کاربر.

        Args:
            request: متن درخواست کاربر

        Returns:
            مسیر استخراج شده یا None
        """
        path_patterns = [
            r'(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?(?:[A-Za-z]:\\[^\s"\']+)["\']?',
            r'(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?(?:\\\\[^\s"\']+)["\']?',
        ]
        for pattern in path_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                path = re.sub(r'^(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?', '', match.group(0))
                path = path.strip().strip('"\'')
                if Path(path).exists():
                    return path
        return None

    def _build_system_context(self) -> str:
        """ساخت اطلاعات زمینه‌ای سیستم."""
        context_parts = ["Current system information:"]
        
        # اطلاعات سخت‌افزار
        if self.registry.has_capability("os"):
            os_cap = self.registry.get_capability("os")
            if os_cap:
                context_parts.append(f"- Operating System: {os_cap.metadata.get('system')} {os_cap.version}")
        
        if self.registry.has_capability("cpu"):
            cpu_cap = self.registry.get_capability("cpu")
            if cpu_cap:
                cores = cpu_cap.metadata.get("logical_cores")
                context_parts.append(f"- CPU: {cores} cores")
        
        if self.registry.has_capability("memory"):
            mem_cap = self.registry.get_capability("memory")
            if mem_cap:
                total = mem_cap.metadata.get("total_gb")
                context_parts.append(f"- RAM: {total} GB")
        
        # برنامه‌های نصب‌شده
        apps = self.registry.list_capabilities(type_filter="app")
        if apps:
            app_names = [app.name for app in apps[:10]]
            context_parts.append(f"- Installed applications: {', '.join(app_names)}")
        
        # ابزارها
        tools = self.registry.list_capabilities(type_filter="tool")
        if tools:
            tool_names = [f"{t.name}" for t in tools]
            context_parts.append(f"- Tools: {', '.join(tool_names)}")
        
        return "\n".join(context_parts)
    


class IntelligentSystemAgent:
    """عامل هوشمند برای اتوماسیون سیستم و Desktop با AI."""
    
    def __init__(self, dry_run: bool = False, action_controller: Optional[ActionController] = None):
        """
        Args:
            dry_run: اگر True باشد، هیچ اقدامی واقعاً اجرا نمی‌شود
            action_controller: کنترلر اقدامات Desktop (اگر None باشد، یکی جدید می‌سازد)
        """
        self.registry = SystemCapabilityRegistry()
        self.parser = SystemActionParser(self.registry)
        self.executor = ExecutionManager(dry_run=dry_run)
        self.action_controller = action_controller or ActionController()
        self.dry_run = dry_run
        
        # کش اسکن سیستم
        if self.registry.needs_refresh():
            logger.info("Scanning system for capabilities...")
            self.registry.scan_system()
    
    async def process_request(self, user_request: str) -> str:
        """پردازش درخواست کاربر و اجرای اقدامات.
        
        Args:
            user_request: درخواست طبیعی کاربر
        
        Returns:
            پاسخ نهایی برای کاربر
        """
        logger.info("Processing request: %s", user_request)
        
        # تجزیه درخواست به اقدامات
        actions_data = await self.parser.parse_request(user_request)
        
        if not actions_data:
            return "متأسفم، نتوانستم درخواست شما را درک کنم. لطفاً واضح‌تر بیان کنید."
        
        # تبدیل به اقدامات واقعی
        results = []
        for action_data in actions_data:
            action_type = action_data.get("type", "")
            action = self._create_action(action_data)
            
            if not action:
                logger.warning("Failed to create action: %s", action_data)
                continue
            
            description = action_data.get("description", "Unknown action")
            
            # Desktop Actions از طریق ActionController اجرا می‌شوند
            if action_type.startswith("Desktop"):
                try:
                    # استفاده از execute_action برای Desktop Actions
                    outcome = self.action_controller.execute_action(action, auto_consent=False)
                    
                    if outcome.result.value == "success":
                        results.append(f"✅ {description}")
                        if outcome.position:
                            results.append(f"   Position: {outcome.position}")
                    else:
                        results.append(f"❌ {description}")
                        if outcome.error:
                            results.append(f"   Error: {outcome.error}")
                        elif outcome.message:
                            results.append(f"   {outcome.message}")
                
                except Exception as e:
                    logger.exception("Error executing desktop action: %s", e)
                    results.append(f"❌ {description}")
                    results.append(f"   Error: {str(e)}")
            
            # System Actions از طریق ExecutionManager اجرا می‌شوند
            else:
                # اضافه کردن به صف
                priority = self._parse_priority(action_data.get("priority", "normal"))
                action_id = self.executor.submit(action, priority=priority)
                results.append(f"✓ {description}")
        
        # اگر System Actions هست، اجرا کن
        if any(not a.get("type", "").startswith("Desktop") for a in actions_data):
            execution_results = await self.executor.execute_all()
            
            # اضافه کردن نتایج system actions
            for i, exec_result in enumerate(execution_results):
                if exec_result.success:
                    if exec_result.output and not self.dry_run:
                        output_preview = exec_result.output[:200]
                        results.append(f"   Output: {output_preview}...")
                else:
                    if exec_result.error:
                        results.append(f"   Error: {exec_result.error}")
        
        if not results:
            return "No executable actions were identified."
        
        # ساخت پاسخ
        response = "\n".join(results)
        
        # اضافه کردن آمار
        stats = self.executor.get_stats()
        if stats['total_succeeded'] > 0 or stats['total_failed'] > 0:
            response += f"\n\n📊 System Actions: {stats['total_succeeded']} succeeded, {stats['total_failed']} failed"
        
        return response
    
    def _create_action(self, action_data: dict[str, Any]) -> Optional[Any]:
        """ساخت شیء اقدام از دیکشنری."""
        action_type = action_data.get("type")
        params = action_data.get("params", {})
        
        try:
            # ========== Desktop Actions ==========
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
            
            # ========== System Actions ==========
            elif action_type == "LaunchApp":
                return LaunchAppAction(
                    app_name=params.get("app_name", ""),
                    app_path=params.get("app_path"),
                    arguments=params.get("arguments", []),
                    working_directory=params.get("working_directory"),
                    dry_run=self.dry_run,
                )
            
            elif action_type == "InstallPackage":
                return InstallPackageAction(
                    package_name=params.get("package_name", ""),
                    package_manager=params.get("package_manager", "winget"),
                    version=params.get("version"),
                    silent=params.get("silent", True),
                    dry_run=self.dry_run,
                )
            
            elif action_type == "QueryHardware":
                return QueryHardwareAction(
                    query_type=params.get("query_type", "all"),
                    dry_run=self.dry_run,
                )
            
            elif action_type == "TerminateProcess":
                return TerminateProcessAction(
                    process_name=params.get("process_name"),
                    process_id=params.get("process_id"),
                    force=params.get("force", False),
                    dry_run=self.dry_run,
                )
            
            elif action_type == "ExecuteCommand":
                return ExecuteCommandAction(
                    command=params.get("command", ""),
                    shell=params.get("shell", "cmd"),
                    working_directory=params.get("working_directory"),
                    timeout=params.get("timeout", 30),
                    dry_run=self.dry_run,
                )
            
            else:
                logger.warning("Unknown action type: %s", action_type)
                return None
        
        except Exception as e:
            logger.exception("Error creating action %s: %s", action_type, e)
            return None
    
    def _parse_priority(self, priority_str: str) -> ExecutionPriority:
        """تبدیل رشته اولویت به enum."""
        priority_map = {
            "low": ExecutionPriority.LOW,
            "normal": ExecutionPriority.NORMAL,
            "high": ExecutionPriority.HIGH,
            "critical": ExecutionPriority.CRITICAL,
        }
        return priority_map.get(priority_str.lower(), ExecutionPriority.NORMAL)
    
    def get_system_summary(self) -> str:
        """دریافت خلاصه وضعیت سیستم."""
        return self.registry.get_summary()


__all__ = ["IntelligentSystemAgent", "SystemActionParser"]
