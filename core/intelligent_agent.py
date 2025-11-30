# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""سیستم تشخیص و اجرای هوشمند اقدامات سیستمی با AI.

این ماژول از LLM برای تفسیر درخواست‌های کاربر و تبدیل آن‌ها به اقدامات سیستمی استفاده می‌کند.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from .ai_brain import AIBrain
from .execution_manager import ExecutionManager, ExecutionPriority
from .system_actions import (
    InstallPackageAction,
    LaunchAppAction,
    QueryHardwareAction,
    TerminateProcessAction,
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
        """تجزیه درخواست کاربر و استخراج اقدامات.
        
        این متد هم اقدامات سیستمی (نصب، اجرا) و هم اقدامات Desktop (کلیک، تایپ) را پشتیبانی می‌کند.
        
        Returns:
            لیستی از اقدامات در قالب دیکشنری
        """
        user_lower = user_request.lower()
        actions = []
        
        # ========== Desktop Actions (اولویت بالاتر) ==========
        
        # الگو: کلیک
        click_action = self._parse_click_action(user_request)
        if click_action:
            actions.append(click_action)
            return actions  # معمولاً یک کلیک کافیه
        
        # الگو: تایپ
        type_action = self._parse_type_action(user_request)
        if type_action:
            actions.append(type_action)
            return actions
        
        # الگو: Drag & Drop
        drag_action = self._parse_drag_action(user_request)
        if drag_action:
            actions.append(drag_action)
            return actions
        
        # الگو: انتظار
        wait_action = self._parse_wait_action(user_request)
        if wait_action:
            actions.append(wait_action)
            return actions
        
        # الگو: میانبر کیبورد
        hotkey_action = self._parse_hotkey_action(user_request)
        if hotkey_action:
            actions.append(hotkey_action)
            return actions
        
        # الگو: اسکرول
        scroll_action = self._parse_scroll_action(user_request)
        if scroll_action:
            actions.append(scroll_action)
            return actions
        
        # ========== System Actions (قدیمی) ==========
        
        # الگو 1: باز کردن برنامه
        if any(keyword in user_lower for keyword in ['open', 'launch', 'start', 'run', 'باز', 'اجرا', 'شروع']):
            # استخراج نام برنامه
            app_name = self._extract_app_name(user_request)
            if app_name:
                actions.append({
                    "type": "LaunchApp",
                    "params": {
                        "app_name": app_name,
                        "arguments": []
                    },
                    "priority": "normal",
                    "description": f"Open {app_name}"
                })
        
        # الگو 2: نصب نرم‌افزار
        elif any(keyword in user_lower for keyword in ['install', 'setup', 'نصب']):
            package_name = self._extract_package_name(user_request)
            if package_name:
                actions.append({
                    "type": "InstallPackage",
                    "params": {
                        "package_name": package_name,
                        "package_manager": "winget",
                        "silent": True
                    },
                    "priority": "normal",
                    "description": f"Install {package_name}"
                })
        
        # الگو 3: اطلاعات سخت‌افزار
        elif any(keyword in user_lower for keyword in ['hardware', 'سخت‌افزار', 'cpu', 'ram', 'memory', 'حافظه', 'disk', 'مشخصات', 'info', 'اطلاعات']):
            actions.append({
                "type": "QueryHardware",
                "params": {
                    "query_type": "all"
                },
                "priority": "normal",
                "description": "Get hardware information"
            })
        
        # الگو 4: بستن فرآیند
        elif any(keyword in user_lower for keyword in ['close', 'kill', 'terminate', 'stop', 'بستن', 'توقف']):
            process_name = self._extract_process_name(user_request)
            if process_name:
                actions.append({
                    "type": "TerminateProcess",
                    "params": {
                        "process_name": process_name,
                        "force": False
                    },
                    "priority": "normal",
                    "description": f"Close {process_name}"
                })
        
        logger.info("Extracted %d actions from request", len(actions))
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
    
    def _extract_app_name(self, request: str) -> Optional[str]:
        """استخراج نام برنامه از درخواست."""
        request_lower = request.lower()
        
        # لیست برنامه‌های شناخته‌شده
        known_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'calc': 'calc.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'vscode': 'code.exe',
            'code': 'code.exe',
            'photoshop': 'photoshop.exe',
            'فتوشاپ': 'photoshop.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
        }
        
        for app_key, app_exe in known_apps.items():
            if app_key in request_lower:
                return app_exe
        
        # اگر .exe در درخواست بود
        import re
        exe_match = re.search(r'(\w+\.exe)', request, re.IGNORECASE)
        if exe_match:
            return exe_match.group(1)
        
        return None
    
    def _extract_package_name(self, request: str) -> Optional[str]:
        """استخراج نام بسته از درخواست."""
        request_lower = request.lower()
        
        # پکیج‌های محبوب
        known_packages = ['git', 'python', 'nodejs', 'node', 'vscode', 'chrome', 'firefox', 'docker']
        
        for pkg in known_packages:
            if pkg in request_lower:
                return pkg
        
        # اگر نام خاصی نبود، آخرین کلمه را برمی‌گردانیم
        words = request.split()
        if words:
            return words[-1]
        
        return None
    
    def _extract_process_name(self, request: str) -> Optional[str]:
        """استخراج نام فرآیند از درخواست."""
        # مشابه _extract_app_name
        return self._extract_app_name(request)
    
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
