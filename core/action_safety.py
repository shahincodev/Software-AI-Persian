# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""سیستم ایمنی و فیلتر اقدامات (Action Safety).

این ماژول مسئول بررسی و فیلتر کردن اقدامات خطرناک قبل از اجرا است.
هدف: جلوگیری از آسیب به سیستم یا حذف فایل‌های مهم.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ActionSafety:
    """فیلتر ایمنی برای بررسی اقدامات قبل از اجرا.
    
    این کلاس اقدامات خطرناک را شناسایی و مسدود می‌کند:
    - حذف فایل‌های سیستمی
    - اجرای دستورات مخرب
    - دسترسی به پوشه‌های حساس
    - فرمت کردن دیسک
    - تغییر تنظیمات امنیتی
    
    Example:
        >>> safety = ActionSafety()
        >>> is_safe = safety.validate_action({
        ...     "type": "DeleteFile",
        ...     "params": {"path": "C:/Windows/System32/kernel32.dll"}
        ... })
        >>> print(is_safe)  # False - فایل سیستمی
    """
    
    def __init__(self, strict_mode: bool = True):
        """مقداردهی اولیه فیلتر ایمنی.
        
        Args:
            strict_mode: اگر True باشد، محدودیت‌های بیشتری اعمال می‌شود
        """
        self.strict_mode = strict_mode
        
        # پوشه‌های ممنوعه (نباید دستکاری شوند)
        self.forbidden_paths = [
            r"C:\\Windows\\System32",
            r"C:\\Windows\\SysWOW64",
            r"C:\\Program Files\\Windows",
            r"C:\\ProgramData\\Microsoft\\Windows",
            r"/System",  # macOS
            r"/Library/System",  # macOS
            r"/bin",  # Linux
            r"/sbin",  # Linux
            r"/usr/bin",  # Linux
        ]
        
        # دستورات ممنوعه (نباید اجرا شوند)
        self.forbidden_commands = [
            "format",
            "del /f /s /q C:\\",
            "rm -rf /",
            "rd /s /q C:\\",
            "rmdir /s /q",
            "shutdown",
            "restart",
            "taskkill /f /im explorer.exe",
            "reg delete",
            "bcdedit",
            "diskpart",
        ]
        
        # فرآیندهای حیاتی (نباید kill شوند)
        self.critical_processes = [
            "explorer.exe",
            "winlogon.exe",
            "csrss.exe",
            "services.exe",
            "lsass.exe",
            "svchost.exe",
            "System",
        ]
        
        # پسوندهای فایل مشکوک
        self.suspicious_extensions = [
            ".exe",
            ".bat",
            ".cmd",
            ".vbs",
            ".ps1",
            ".msi",
            ".scr",
            ".com",
        ]
    
    def validate_action(self, action: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی یک اقدام.
        
        Args:
            action: اقدام مورد نظر (dict با type و params)
        
        Returns:
            (is_safe, reason): 
                - is_safe: True اگر اقدام ایمن باشد
                - reason: دلیل عدم ایمنی (در صورت وجود)
        
        Example:
            >>> safety = ActionSafety()
            >>> is_safe, reason = safety.validate_action({
            ...     "type": "TerminateProcess",
            ...     "params": {"process_name": "explorer.exe"}
            ... })
            >>> print(is_safe, reason)  # (False, "Critical process: explorer.exe")
        """
        action_type = action.get("type", "")
        params = action.get("params", {})
        
        logger.debug(f"🔍 Validating action: {action_type}")
        
        # بررسی بر اساس نوع اقدام
        if action_type == "DeleteFile":
            return self._check_delete_file(params)
        
        elif action_type == "TerminateProcess":
            return self._check_terminate_process(params)
        
        elif action_type == "ExecuteCommand":
            return self._check_execute_command(params)
        
        elif action_type == "ModifyRegistry":
            return self._check_modify_registry(params)
        
        elif action_type == "DownloadFile":
            return self._check_download_file(params)
        
        elif action_type == "LaunchApp":
            return self._check_launch_app(params)
        
        elif action_type == "InstallPackage":
            return self._check_install_package(params)
        
        # اقدامات دیگر به طور پیش‌فرض ایمن هستند
        logger.debug(f"✅ Action {action_type} is safe by default")
        return True, ""
    
    def _check_delete_file(self, params: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی حذف فایل.
        
        Args:
            params: {"path": "C:/path/to/file"}
        
        Returns:
            (is_safe, reason)
        """
        path = params.get("path", "")
        
        if not path:
            return False, "No path specified"
        
        # بررسی پوشه‌های ممنوعه
        for forbidden in self.forbidden_paths:
            if re.search(forbidden, path, re.IGNORECASE):
                logger.warning(f"❌ Forbidden path: {path}")
                return False, f"Forbidden system path: {path}"
        
        # بررسی فایل‌های سیستمی ویندوز
        if re.search(r"C:\\Windows\\.*\.(dll|sys|exe)", path, re.IGNORECASE):
            logger.warning(f"❌ System file: {path}")
            return False, f"Cannot delete system file: {path}"
        
        logger.debug(f"✅ Delete file is safe: {path}")
        return True, ""
    
    def _check_terminate_process(self, params: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی kill کردن فرآیند.
        
        Args:
            params: {"process_name": "app.exe"}
        
        Returns:
            (is_safe, reason)
        """
        process_name = params.get("process_name", "")
        
        if not process_name:
            return False, "No process name specified"
        
        # بررسی فرآیندهای حیاتی
        for critical in self.critical_processes:
            if critical.lower() == process_name.lower():
                logger.warning(f"❌ Critical process: {process_name}")
                return False, f"Cannot terminate critical process: {process_name}"
        
        logger.debug(f"✅ Terminate process is safe: {process_name}")
        return True, ""
    
    def _check_execute_command(self, params: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی اجرای دستور.
        
        Args:
            params: {"command": "del C:\\file.txt"}
        
        Returns:
            (is_safe, reason)
        """
        command = params.get("command", "")
        
        if not command:
            return False, "No command specified"
        
        # بررسی دستورات ممنوعه
        for forbidden in self.forbidden_commands:
            if forbidden.lower() in command.lower():
                logger.warning(f"❌ Forbidden command: {command}")
                return False, f"Forbidden command detected: {forbidden}"
        
        # بررسی دستورات مشکوک
        suspicious_patterns = [
            r"format\s+[A-Z]:",  # format C:
            r"del\s+/[fqs]+.*C:\\",  # del /f /s /q C:\
            r"rm\s+-rf\s+/",  # rm -rf /
            r"shutdown\s+",  # shutdown
            r"restart\s+",  # restart
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(f"❌ Suspicious command: {command}")
                return False, f"Suspicious command pattern detected"
        
        logger.debug(f"✅ Execute command is safe: {command}")
        return True, ""
    
    def _check_modify_registry(self, params: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی تغییر رجیستری.
        
        Args:
            params: {"key": "HKLM\\...", "value": "..."}
        
        Returns:
            (is_safe, reason)
        """
        key = params.get("key", "")
        
        if not key:
            return False, "No registry key specified"
        
        # کلیدهای حساس رجیستری
        sensitive_keys = [
            r"HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            r"HKLM\\SYSTEM\\CurrentControlSet\\Services",
            r"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
            r"HKLM\\SYSTEM\\CurrentControlSet\\Control\\SafeBoot",
        ]
        
        for sensitive in sensitive_keys:
            if re.search(sensitive, key, re.IGNORECASE):
                if self.strict_mode:
                    logger.warning(f"❌ Sensitive registry key: {key}")
                    return False, f"Cannot modify sensitive registry key: {key}"
                else:
                    logger.warning(f"⚠️ Warning: Modifying sensitive registry key: {key}")
        
        logger.debug(f"✅ Modify registry is safe: {key}")
        return True, ""
    
    def _check_download_file(self, params: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی دانلود فایل.
        
        Args:
            params: {"url": "https://...", "destination": "C:/..."}
        
        Returns:
            (is_safe, reason)
        """
        url = params.get("url", "")
        destination = params.get("destination", "")
        
        if not url:
            return False, "No URL specified"
        
        # بررسی پروتکل امن
        if not (url.startswith("https://") or url.startswith("http://")):
            logger.warning(f"❌ Unsafe protocol: {url}")
            return False, f"Only HTTP/HTTPS protocols allowed"
        
        # بررسی پسوند فایل مشکوک
        if destination:
            ext = Path(destination).suffix.lower()
            if ext in self.suspicious_extensions:
                if self.strict_mode:
                    logger.warning(f"❌ Suspicious file extension: {ext}")
                    return False, f"Suspicious file extension: {ext}"
                else:
                    logger.warning(f"⚠️ Warning: Downloading executable file: {ext}")
        
        logger.debug(f"✅ Download file is safe: {url}")
        return True, ""
    
    def _check_launch_app(self, params: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی اجرای برنامه.
        
        Args:
            params: {"app_name": "app.exe", "arguments": []}
        
        Returns:
            (is_safe, reason)
        """
        app_name = params.get("app_name", "")
        arguments = params.get("arguments", [])
        
        if not app_name:
            return False, "No app name specified"
        
        # بررسی آرگومان‌های مشکوک
        if arguments:
            args_str = " ".join(str(arg) for arg in arguments)
            
            # بررسی دستورات ممنوعه در آرگومان‌ها
            for forbidden in self.forbidden_commands:
                if forbidden.lower() in args_str.lower():
                    logger.warning(f"❌ Forbidden argument: {args_str}")
                    return False, f"Forbidden command in arguments: {forbidden}"
        
        logger.debug(f"✅ Launch app is safe: {app_name}")
        return True, ""
    
    def _check_install_package(self, params: dict[str, Any]) -> tuple[bool, str]:
        """بررسی ایمنی نصب پکیج.
        
        Args:
            params: {"package_name": "git", "package_manager": "winget"}
        
        Returns:
            (is_safe, reason)
        """
        package_name = params.get("package_name", "")
        package_manager = params.get("package_manager", "")
        
        if not package_name:
            return False, "No package name specified"
        
        # فقط package manager های معتبر
        valid_managers = ["winget", "choco", "scoop", "pip", "npm", "apt", "brew"]
        if package_manager and package_manager not in valid_managers:
            logger.warning(f"❌ Unknown package manager: {package_manager}")
            return False, f"Unknown package manager: {package_manager}"
        
        logger.debug(f"✅ Install package is safe: {package_name}")
        return True, ""
    
    def validate_batch(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        """بررسی ایمنی یک دسته اقدام.
        
        Args:
            actions: لیستی از اقدامات
        
        Returns:
            {
                "all_safe": bool,
                "safe_actions": list[dict],
                "unsafe_actions": list[dict],
                "reasons": dict[int, str]  # {index: reason}
            }
        
        Example:
            >>> safety = ActionSafety()
            >>> result = safety.validate_batch([
            ...     {"type": "LaunchApp", "params": {"app_name": "notepad.exe"}},
            ...     {"type": "TerminateProcess", "params": {"process_name": "explorer.exe"}}
            ... ])
            >>> print(result["all_safe"])  # False
            >>> print(len(result["safe_actions"]))  # 1
            >>> print(len(result["unsafe_actions"]))  # 1
        """
        safe_actions = []
        unsafe_actions = []
        reasons = {}
        
        for i, action in enumerate(actions):
            is_safe, reason = self.validate_action(action)
            
            if is_safe:
                safe_actions.append(action)
            else:
                unsafe_actions.append(action)
                reasons[i] = reason
        
        all_safe = len(unsafe_actions) == 0
        
        logger.info(
            f"📊 Batch validation: {len(safe_actions)}/{len(actions)} safe, "
            f"{len(unsafe_actions)} unsafe"
        )
        
        return {
            "all_safe": all_safe,
            "safe_actions": safe_actions,
            "unsafe_actions": unsafe_actions,
            "reasons": reasons,
        }
