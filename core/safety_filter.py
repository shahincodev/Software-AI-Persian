# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""فیلتر امنیتی برای اعتبارسنجی و مجوزدهی اقدامات سیستمی.

این ماژول از اجرای اقدامات خطرناک جلوگیری می‌کند و سیاست‌های امنیتی را اعمال می‌نماید.
شامل whitelist مسیرها، blacklist فرآیندها، و بررسی سطح ریسک.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Optional

from .system_actions import (
    InstallPackageAction,
    LaunchAppAction,
    QueryHardwareAction,
    RiskLevel,
    SystemAction,
    TerminateProcessAction,
)

logger = logging.getLogger(__name__)


class SafetyPolicy:
    """سیاست‌های امنیتی برای فیلتر کردن اقدامات."""
    
    def __init__(self):
        # مسیرهای مجاز برای اجرای برنامه
        self.allowed_paths: list[str] = [
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("APPDATA", ""),
            "C:\\Windows\\System32",
            "C:\\Windows\\SysWOW64",
        ]
        
        # برنامه‌های مجاز (whitelist)
        # نکته: explorer.exe همیشه مجاز است چون برای file management ضروری است
        self.allowed_apps: set[str] = {
            "notepad.exe", "calc.exe", "mspaint.exe", "explorer.exe",
            "code.exe", "chrome.exe", "firefox.exe", "edge.exe",
            "photoshop.exe", "illustrator.exe", "winword.exe", "excel.exe",
            "powershell.exe", "cmd.exe",  # System tools
        }
        
        # پسوندهای مجاز برای فایل‌های قابل اجرا
        self.allowed_extensions: set[str] = {
            ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".js"
        }
        
        # برنامه‌های همیشه مجاز (بدون محدودیت)
        self.always_allowed: set[str] = {
            "notepad.exe", "calc.exe", "mspaint.exe", "explorer.exe"
        }
        
        # فرآیندهای ممنوع برای بستن (blacklist)
        self.protected_processes: set[str] = {
            "system", "smss.exe", "csrss.exe", "wininit.exe", "services.exe",
            "lsass.exe", "winlogon.exe", "svchost.exe", "dwm.exe",
        }
        
        # نام بسته‌های مشکوک
        self.suspicious_packages: set[str] = {
            "mimikatz", "metasploit", "nmap", "wireshark",  # ابزارهای امنیتی
        }
        
        # الگوهای مشکوک در آرگومان‌ها
        self.suspicious_patterns: list[re.Pattern] = [
            re.compile(r"rm\s+-rf", re.IGNORECASE),
            re.compile(r"del\s+/f\s+/s\s+/q", re.IGNORECASE),
            re.compile(r"format\s+[a-z]:", re.IGNORECASE),
            re.compile(r"reg\s+delete", re.IGNORECASE),
            re.compile(r"shutdown\s+/s", re.IGNORECASE),
        ]
        
        # حداکثر سطح ریسک مجاز بدون تایید کاربر
        # SAFE/LOW: Auto-approve (no user confirmation needed)
        # MEDIUM: Auto-approve for trusted apps (notepad, calc, etc.)
        # HIGH/CRITICAL: Always require approval
        self.max_auto_approve_risk = RiskLevel.MEDIUM  # Changed from LOW to MEDIUM


class SafetyFilter:
    """فیلتر امنیتی برای بررسی اقدامات قبل از اجرا."""
    
    def __init__(self, policy: Optional[SafetyPolicy] = None, strict_mode: bool = True):
        """
        Args:
            policy: سیاست امنیتی (اگر None باشد، پیش‌فرض استفاده می‌شود)
            strict_mode: اگر True باشد، محدودیت‌ها سخت‌گیرانه‌تر هستند
        """
        self.policy = policy or SafetyPolicy()
        self.strict_mode = strict_mode
    
    def validate(self, action: SystemAction) -> tuple[bool, str, bool]:
        """اعتبارسنجی اقدام.
        
        Returns:
            (is_safe, reason, needs_consent): 
            - is_safe: آیا اقدام امن است؟
            - reason: دلیل رد یا قبول
            - needs_consent: آیا نیاز به تایید کاربر دارد؟
        """
        # ابتدا خود اقدام را اعتبارسنجی کن
        is_valid, validation_msg = action.validate()
        if not is_valid:
            return False, f"Validation failed: {validation_msg}", False
        
        # بررسی سطح ریسک
        risk_level = action.get_risk_level()
        
        # اگر ریسک CRITICAL است، همیشه رد کن در حالت strict
        if self.strict_mode and risk_level == RiskLevel.CRITICAL:
            return False, "Risk level is CRITICAL - execution is forbidden in strict mode", False
        
        # بررسی نیاز به تایید - فقط برای HIGH و CRITICAL
        # SAFE, LOW, MEDIUM: Auto-approve
        needs_consent = (
            risk_level.value > RiskLevel.MEDIUM.value  # Only HIGH and CRITICAL need approval
            or action.require_consent
        )
        
        # بررسی خاص بر اساس نوع اقدام
        if isinstance(action, LaunchAppAction):
            return self._validate_launch_app(action, needs_consent)
        elif isinstance(action, InstallPackageAction):
            return self._validate_install_package(action, needs_consent)
        elif isinstance(action, TerminateProcessAction):
            return self._validate_terminate_process(action, needs_consent)
        elif isinstance(action, QueryHardwareAction):
            # خواندن اطلاعات سخت‌افزاری همیشه ایمن است 
            return True, "Retrieving hardware information is safe", False
        
        # برای اقدامات ناشناخته، احتیاط کن
        return True, "Type not registered - needs checking", needs_consent
    
    def _validate_launch_app(
        self, action: LaunchAppAction, needs_consent: bool
    ) -> tuple[bool, str, bool]:
        """بررسی امنیت باز کردن برنامه."""
        app_name = action.app_name.lower() if action.app_name else ""
        app_path = action.app_path.lower() if action.app_path else ""
        
        # بررسی آرگومان‌های مشکوک
        for arg in action.arguments:
            for pattern in self.policy.suspicious_patterns:
                if pattern.search(arg):
                    return False, f"Suspicious argument detected: {arg}", False
        
        # در حالت strict، فقط برنامه‌های whitelist مجاز هستند
        if self.strict_mode:
            # بررسی پسوند فایل
            import os
            _, ext = os.path.splitext(app_name)
            
            # اگر پسوند مجاز باشد (مثل .bat, .cmd)، اجازه بده
            if ext.lower() in self.policy.allowed_extensions:
                # فایل‌های .bat و .cmd نیاز به تایید دارند
                if ext.lower() in {'.bat', '.cmd', '.ps1', '.vbs'}:
                    needs_consent = True
                    logger.info(f"Script file detected: {app_name} - requires approval")
                return True, f"Script file '{app_name}' allowed with approval", needs_consent
            
            # بررسی برنامه‌های always_allowed (notepad, calc, etc.) - بدون تایید!
            if app_name in self.policy.always_allowed:
                logger.info(f"✅ Trusted app auto-approved: {app_name}")
                return True, f"Trusted application '{app_name}' auto-approved", False  # No consent needed!
            
            # بررسی نام برنامه در whitelist
            if app_name and app_name not in self.policy.allowed_apps:
                # اگر مسیر کامل داده شده، بررسی کن در مسیرهای مجاز باشد
                if app_path:
                    is_in_allowed_path = any(
                        app_path.startswith(allowed.lower())
                        for allowed in self.policy.allowed_paths
                        if allowed
                    )
                    if not is_in_allowed_path:
                        return (
                            False,
                            f"Application '{action.app_name}' is not in allowed paths",
                            False,
                        )
                else:
                    return (
                        False,
                        f"Application '{action.app_name}' is not in the allowed list",
                        False,
                    )
        
        return True, "Application is considered safe", needs_consent
    
    def _validate_install_package(
        self, action: InstallPackageAction, needs_consent: bool
    ) -> tuple[bool, str, bool]:
        """بررسی امنیت نصب بسته."""
        package_name = action.package_name.lower()
        
        # بررسی نام‌های مشکوک
        if package_name in self.policy.suspicious_packages:
            return (
                False,
                f"Package '{action.package_name}' is recognized as suspicious",
                False,
            )
        
        # نصب بسته همیشه نیاز به تایید دارد
        return True, "Installing a package requires user consent", True
    
    def _validate_terminate_process(
        self, action: TerminateProcessAction, needs_consent: bool
    ) -> tuple[bool, str, bool]:
        """ایمنی خاتمه دادن به یک فرآیند را بررسی کنید."""
        process_name = action.process_name.lower() if action.process_name else ""
        
        # جلوگیری از بستن فرآیندهای حیاتی
        if process_name in self.policy.protected_processes:
            return (
                False,
                f"Process '{action.process_name}' is critical and cannot be terminated",
                False,
            )
        
        # بستن اجباری فرآیند نیاز به تایید دارد
        if action.force:
            return True, "Forcefully terminating a process requires user consent", True
        
        return True, "Terminating the process is safe", needs_consent
    
    def get_approval_message(self, action: SystemAction) -> str:
        """پیام درخواست تایید را برای اقدام می‌سازد."""
        risk_emoji = {
            RiskLevel.SAFE: "✅",
            RiskLevel.LOW: "🟢",
            RiskLevel.MEDIUM: "🟡",
            RiskLevel.HIGH: "🟠",
            RiskLevel.CRITICAL: "🔴",
        }
        
        emoji = risk_emoji.get(action.get_risk_level(), "⚠️")
        risk_text = {
            RiskLevel.SAFE: "No Risk",
            RiskLevel.LOW: "Low Risk",
            RiskLevel.MEDIUM: "Medium Risk",
            RiskLevel.HIGH: "High Risk",
            RiskLevel.CRITICAL: "Critical Risk",
        }
        
        return f"""
{emoji} System Action Approval Request
───────────────────────────────
Description: {action.describe()}
Risk Level: {risk_text.get(action.get_risk_level(), 'Unknown')}
ID: {action.action_id}
Do you approve this action?
(y/n): """


class UserConsentManager:
    """مدیریت درخواست تایید از کاربر."""
    
    def __init__(self, auto_approve_safe: bool = True):
        """
        Args:
            auto_approve_safe: آیا اقدامات امن (SAFE) به صورت خودکار تایید شوند؟
        """
        self.auto_approve_safe = auto_approve_safe
        self.approval_history: dict[str, bool] = {}  # action_id -> approved
    
    def request_consent(self, action: SystemAction, filter: SafetyFilter) -> bool:
        """درخواست تایید از کاربر.
        
        Returns:
            True اگر کاربر تایید کرد، False در غیر این صورت
        """
        # اگر اقدام امن است و auto_approve فعال است
        if self.auto_approve_safe and action.get_risk_level() == RiskLevel.SAFE:
            logger.info("Safe action automatically approved: %s", action.action_id)
            self.approval_history[action.action_id] = True
            return True
        
        # نمایش پیام درخواست
        message = filter.get_approval_message(action)
        print(message, end="")
        
        # دریافت پاسخ از کاربر
        try:
            response = input().strip().lower()
            approved = response in ["y", "yes", "بله", "آره", "1"]
            
            self.approval_history[action.action_id] = approved
            
            if approved:
                logger.info("User approved the action: %s", action.action_id)
            else:
                logger.info("User rejected the action: %s", action.action_id)
            
            return approved
        
        except (EOFError, KeyboardInterrupt):
            logger.warning("User cancelled the approval request")
            self.approval_history[action.action_id] = False
            return False
    
    def get_approval_rate(self) -> float:
        """درصد اقداماتی که تایید شده‌اند."""
        if not self.approval_history:
            return 0.0
        approved_count = sum(1 for v in self.approval_history.values() if v)
        return (approved_count / len(self.approval_history)) * 100


__all__ = [
    "SafetyPolicy",
    "SafetyFilter",
    "UserConsentManager",
]
