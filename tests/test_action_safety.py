# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های سیستم ایمنی اقدامات."""

import pytest
from core.action_safety import ActionSafety


class TestActionSafety:
    """تست‌های ActionSafety."""
    
    def setup_method(self):
        """راه‌اندازی قبل از هر تست."""
        self.safety = ActionSafety(strict_mode=True)
    
    # Test DeleteFile
    def test_delete_safe_file(self):
        """تست حذف فایل معمولی (ایمن)."""
        action = {
            "type": "DeleteFile",
            "params": {"path": "C:/Users/test/document.txt"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
        assert reason == ""
    
    def test_delete_system_file(self):
        """تست حذف فایل سیستمی (خطرناک)."""
        action = {
            "type": "DeleteFile",
            "params": {"path": "C:/Windows/System32/kernel32.dll"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
        assert "system" in reason.lower()
    
    def test_delete_forbidden_path(self):
        """تست حذف از پوشه ممنوعه."""
        action = {
            "type": "DeleteFile",
            "params": {"path": "C:/Windows/SysWOW64/test.dll"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
        assert "forbidden" in reason.lower()
    
    # Test TerminateProcess
    def test_terminate_normal_process(self):
        """تست بستن فرآیند معمولی (ایمن)."""
        action = {
            "type": "TerminateProcess",
            "params": {"process_name": "notepad.exe"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    def test_terminate_critical_process(self):
        """تست بستن فرآیند حیاتی (خطرناک)."""
        action = {
            "type": "TerminateProcess",
            "params": {"process_name": "explorer.exe"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
        assert "critical" in reason.lower()
    
    def test_terminate_system_process(self):
        """تست بستن فرآیند سیستمی."""
        action = {
            "type": "TerminateProcess",
            "params": {"process_name": "csrss.exe"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
    
    # Test ExecuteCommand
    def test_execute_safe_command(self):
        """تست اجرای دستور ایمن."""
        action = {
            "type": "ExecuteCommand",
            "params": {"command": "dir C:\\Users"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    def test_execute_format_command(self):
        """تست اجرای دستور format (خطرناک)."""
        action = {
            "type": "ExecuteCommand",
            "params": {"command": "format C:"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
        assert "forbidden" in reason.lower()
    
    def test_execute_delete_all_command(self):
        """تست اجرای دستور del /f /s (خطرناک)."""
        action = {
            "type": "ExecuteCommand",
            "params": {"command": "del /f /s /q C:\\*"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
    
    def test_execute_shutdown_command(self):
        """تست اجرای دستور shutdown (خطرناک)."""
        action = {
            "type": "ExecuteCommand",
            "params": {"command": "shutdown /s /t 0"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
    
    # Test ModifyRegistry
    def test_modify_normal_registry(self):
        """تست تغییر کلید رجیستری معمولی."""
        action = {
            "type": "ModifyRegistry",
            "params": {"key": "HKCU\\Software\\MyApp\\Settings"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    def test_modify_sensitive_registry(self):
        """تست تغییر کلید حساس رجیستری."""
        action = {
            "type": "ModifyRegistry",
            "params": {"key": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False  # strict_mode=True
    
    # Test DownloadFile
    def test_download_https_file(self):
        """تست دانلود فایل با HTTPS (ایمن)."""
        action = {
            "type": "DownloadFile",
            "params": {
                "url": "https://example.com/file.txt",
                "destination": "C:/Users/test/download.txt"
            }
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    def test_download_executable_strict(self):
        """تست دانلود فایل اجرایی در strict mode."""
        action = {
            "type": "DownloadFile",
            "params": {
                "url": "https://example.com/setup.exe",
                "destination": "C:/Users/test/setup.exe"
            }
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False  # strict_mode=True
    
    def test_download_unsafe_protocol(self):
        """تست دانلود با پروتکل ناامن."""
        action = {
            "type": "DownloadFile",
            "params": {
                "url": "ftp://example.com/file.txt",
                "destination": "C:/Users/test/file.txt"
            }
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
    
    # Test LaunchApp
    def test_launch_normal_app(self):
        """تست اجرای برنامه معمولی."""
        action = {
            "type": "LaunchApp",
            "params": {"app_name": "notepad.exe", "arguments": []}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    def test_launch_app_dangerous_args(self):
        """تست اجرای برنامه با آرگومان‌های خطرناک."""
        action = {
            "type": "LaunchApp",
            "params": {"app_name": "cmd.exe", "arguments": ["format C:"]}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
    
    # Test InstallPackage
    def test_install_package_winget(self):
        """تست نصب پکیج با winget (ایمن)."""
        action = {
            "type": "InstallPackage",
            "params": {"package_name": "git", "package_manager": "winget"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    def test_install_package_unknown_manager(self):
        """تست نصب پکیج با package manager نامعتبر."""
        action = {
            "type": "InstallPackage",
            "params": {"package_name": "test", "package_manager": "unknown"}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is False
    
    # Test Batch Validation
    def test_validate_batch_all_safe(self):
        """تست اعتبارسنجی batch - همه ایمن."""
        actions = [
            {"type": "LaunchApp", "params": {"app_name": "notepad.exe"}},
            {"type": "InstallPackage", "params": {"package_name": "git", "package_manager": "winget"}},
        ]
        result = self.safety.validate_batch(actions)
        assert result["all_safe"] is True
        assert len(result["safe_actions"]) == 2
        assert len(result["unsafe_actions"]) == 0
    
    def test_validate_batch_mixed(self):
        """تست اعتبارسنجی batch - ترکیبی."""
        actions = [
            {"type": "LaunchApp", "params": {"app_name": "notepad.exe"}},
            {"type": "TerminateProcess", "params": {"process_name": "explorer.exe"}},
            {"type": "DeleteFile", "params": {"path": "C:/Users/test/file.txt"}},
        ]
        result = self.safety.validate_batch(actions)
        assert result["all_safe"] is False
        assert len(result["safe_actions"]) == 2
        assert len(result["unsafe_actions"]) == 1
        assert 1 in result["reasons"]
    
    def test_validate_batch_all_unsafe(self):
        """تست اعتبارسنجی batch - همه خطرناک."""
        actions = [
            {"type": "TerminateProcess", "params": {"process_name": "explorer.exe"}},
            {"type": "ExecuteCommand", "params": {"command": "format C:"}},
        ]
        result = self.safety.validate_batch(actions)
        assert result["all_safe"] is False
        assert len(result["safe_actions"]) == 0
        assert len(result["unsafe_actions"]) == 2
    
    # Test Unknown Actions
    def test_unknown_action_safe_by_default(self):
        """تست اقدام نامشخص (پیش‌فرض ایمن)."""
        action = {
            "type": "UnknownAction",
            "params": {}
        }
        is_safe, reason = self.safety.validate_action(action)
        assert is_safe is True
    
    # Test Strict Mode
    def test_strict_mode_vs_normal(self):
        """تست تفاوت strict mode و normal mode."""
        action = {
            "type": "DownloadFile",
            "params": {
                "url": "https://example.com/setup.exe",
                "destination": "C:/Users/test/setup.exe"
            }
        }
        
        # Strict mode
        safety_strict = ActionSafety(strict_mode=True)
        is_safe_strict, _ = safety_strict.validate_action(action)
        
        # Normal mode
        safety_normal = ActionSafety(strict_mode=False)
        is_safe_normal, _ = safety_normal.validate_action(action)
        
        assert is_safe_strict is False
        assert is_safe_normal is True  # Warning اما می‌گذرد


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
