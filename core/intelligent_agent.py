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

logger = logging.getLogger(__name__)


class SystemActionParser:
    """تبدیل درخواست‌های طبیعی کاربر به اقدامات سیستمی."""
    
    def __init__(self, registry: SystemCapabilityRegistry):
        self.registry = registry
        self.ai_brain = AIBrain()
    
    async def parse_request(self, user_request: str) -> list[dict[str, Any]]:
        """تجزیه درخواست کاربر و استخراج اقدامات.
        
        برای نسخه اولیه، از pattern matching ساده استفاده می‌کنیم.
        در نسخه‌های بعدی، از LLM برای تجزیه پیچیده‌تر استفاده خواهد شد.
        
        Returns:
            لیستی از اقدامات در قالب دیکشنری
        """
        user_lower = user_request.lower()
        actions = []
        
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
                    "description": f"باز کردن {app_name}"
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
                    "description": f"نصب {package_name}"
                })
        
        # الگو 3: اطلاعات سخت‌افزار
        elif any(keyword in user_lower for keyword in ['hardware', 'سخت‌افزار', 'cpu', 'ram', 'memory', 'حافظه', 'disk', 'مشخصات', 'info', 'اطلاعات']):
            actions.append({
                "type": "QueryHardware",
                "params": {
                    "query_type": "all"
                },
                "priority": "normal",
                "description": "دریافت اطلاعات سخت‌افزار"
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
                    "description": f"بستن {process_name}"
                })
        
        logger.info("تعداد %d اقدام از درخواست استخراج شد", len(actions))
        return actions
    
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
        context_parts = ["اطلاعات سیستم فعلی:"]
        
        # اطلاعات سخت‌افزار
        if self.registry.has_capability("os"):
            os_cap = self.registry.get_capability("os")
            if os_cap:
                context_parts.append(f"- سیستم‌عامل: {os_cap.metadata.get('system')} {os_cap.version}")
        
        if self.registry.has_capability("cpu"):
            cpu_cap = self.registry.get_capability("cpu")
            if cpu_cap:
                cores = cpu_cap.metadata.get("logical_cores")
                context_parts.append(f"- CPU: {cores} هسته")
        
        if self.registry.has_capability("memory"):
            mem_cap = self.registry.get_capability("memory")
            if mem_cap:
                total = mem_cap.metadata.get("total_gb")
                context_parts.append(f"- RAM: {total} GB")
        
        # برنامه‌های نصب‌شده
        apps = self.registry.list_capabilities(type_filter="app")
        if apps:
            app_names = [app.name for app in apps[:10]]
            context_parts.append(f"- برنامه‌های نصب‌شده: {', '.join(app_names)}")
        
        # ابزارها
        tools = self.registry.list_capabilities(type_filter="tool")
        if tools:
            tool_names = [f"{t.name}" for t in tools]
            context_parts.append(f"- ابزارها: {', '.join(tool_names)}")
        
        return "\n".join(context_parts)
    


class IntelligentSystemAgent:
    """عامل هوشمند برای اتوماسیون سیستم با AI."""
    
    def __init__(self, dry_run: bool = False):
        """
        Args:
            dry_run: اگر True باشد، هیچ اقدامی واقعاً اجرا نمی‌شود
        """
        self.registry = SystemCapabilityRegistry()
        self.parser = SystemActionParser(self.registry)
        self.executor = ExecutionManager(dry_run=dry_run)
        self.dry_run = dry_run
        
        # کش اسکن سیستم
        if self.registry.needs_refresh():
            logger.info("اسکن سیستم برای کشف قابلیت‌ها...")
            self.registry.scan_system()
    
    async def process_request(self, user_request: str) -> str:
        """پردازش درخواست کاربر و اجرای اقدامات.
        
        Args:
            user_request: درخواست طبیعی کاربر
        
        Returns:
            پاسخ نهایی برای کاربر
        """
        logger.info("پردازش درخواست: %s", user_request)
        
        # تجزیه درخواست به اقدامات
        actions_data = await self.parser.parse_request(user_request)
        
        if not actions_data:
            return "متأسفم، نتوانستم درخواست شما را درک کنم. لطفاً واضح‌تر بیان کنید."
        
        # تبدیل به اقدامات واقعی
        results = []
        for action_data in actions_data:
            action = self._create_action(action_data)
            if action:
                # اضافه کردن به صف
                priority = self._parse_priority(action_data.get("priority", "normal"))
                action_id = self.executor.submit(action, priority=priority)
                
                description = action_data.get("description", action.describe())
                results.append(f"✓ {description}")
            else:
                logger.warning("نتوانستیم اقدام بسازیم: %s", action_data)
        
        if not results:
            return "هیچ اقدام قابل اجرایی شناسایی نشد."
        
        # اجرای تمام اقدامات
        execution_results = await self.executor.execute_all()
        
        # ساخت پاسخ
        response_parts = ["نتایج اجرا:"]
        
        for i, exec_result in enumerate(execution_results):
            if exec_result.success:
                response_parts.append(f"✅ اقدام {i+1}: موفق")
                if exec_result.output and not self.dry_run:
                    # محدود کردن طول خروجی
                    output_preview = exec_result.output[:200]
                    response_parts.append(f"   خروجی: {output_preview}...")
            else:
                response_parts.append(f"❌ اقدام {i+1}: ناموفق")
                if exec_result.error:
                    response_parts.append(f"   خطا: {exec_result.error}")
        
        # اضافه کردن آمار
        stats = self.executor.get_stats()
        response_parts.append(f"\n📊 آمار: {stats['total_succeeded']} موفق، {stats['total_failed']} ناموفق")
        
        return "\n".join(response_parts)
    
    def _create_action(self, action_data: dict[str, Any]) -> Optional[Any]:
        """ساخت شیء اقدام از دیکشنری."""
        action_type = action_data.get("type")
        params = action_data.get("params", {})
        
        try:
            if action_type == "LaunchApp":
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
                logger.warning("نوع اقدام ناشناخته: %s", action_type)
                return None
        
        except Exception as e:
            logger.exception("خطا در ساخت اقدام %s: %s", action_type, e)
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
