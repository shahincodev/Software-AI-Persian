# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تعریف اقدامات سیستمی برای اتوماسیون ویندوز.

این ماژول شامل کلاس‌های پایه‌ای برای تعریف اقدامات قابل اجرا روی سیستم‌عامل است.
هر اقدام شامل اعتبارسنجی، سطح ریسک، و متادیتا برای لاگینگ می‌باشد.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """سطح ریسک اقدامات سیستمی."""
    SAFE = "safe"  # بدون خطر (مثل خواندن اطلاعات)
    LOW = "low"  # خطر کم (مثل باز کردن برنامه)
    MEDIUM = "medium"  # خطر متوسط (مثل نصب نرم‌افزار)
    HIGH = "high"  # خطر بالا (مثل تغییر رجیستری)
    CRITICAL = "critical"  # خطر حیاتی (مثل حذف فایل‌های سیستمی)


class ActionStatus(Enum):
    """وضعیت اجرای یک اقدام."""
    PENDING = "pending"
    VALIDATING = "validating"
    APPROVED = "approved"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRY_RUN = "dry_run"


@dataclass
class ActionResult:
    """نتیجه اجرای یک اقدام سیستمی."""
    action_id: str
    status: ActionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float | None:
        """مدت زمان اجرا به ثانیه."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def success(self) -> bool:
        """آیا اجرا موفق بوده است؟"""
        return self.status == ActionStatus.SUCCESS


@dataclass
class SystemAction(ABC):
    """کلاس پایه برای تمام اقدامات سیستمی.
    
    هر اقدام باید:
    - قابل اعتبارسنجی باشد (validate)
    - سطح ریسک مشخصی داشته باشد
    - قابل تبدیل به توضیح انسانی باشد (describe)
    """
    
    action_id: str = field(default_factory=lambda: f"act_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
    dry_run: bool = False
    require_consent: bool = True
    timeout_seconds: int = 30
    
    @abstractmethod
    def get_risk_level(self) -> RiskLevel:
        """سطح ریسک این اقدام را برمی‌گرداند."""
        pass
    
    @abstractmethod
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی پارامترهای اقدام.
        
        Returns:
            (valid, message): آیا معتبر است و پیام توضیحی
        """
        pass
    
    @abstractmethod
    def describe(self) -> str:
        """توضیح انسانی از اقدام برای نمایش به کاربر."""
        pass
    
    def to_dict(self) -> dict[str, Any]:
        """تبدیل به دیکشنری برای لاگینگ."""
        return {
            "action_id": self.action_id,
            "action_type": self.__class__.__name__,
            "risk_level": self.get_risk_level().value,
            "dry_run": self.dry_run,
            "require_consent": self.require_consent,
            "description": self.describe(),
        }


@dataclass
class LaunchAppAction(SystemAction):
    """اقدام برای باز کردن یک برنامه."""
    
    app_name: str = ""
    app_path: Optional[str] = None
    arguments: list[str] = field(default_factory=list)
    working_directory: Optional[str] = None
    
    def get_risk_level(self) -> RiskLevel:
        """باز کردن برنامه معمولاً خطر کمی دارد."""
        # اگر آرگومان‌های مشکوک داشته باشد، ریسک بالاتر است
        if any(arg.startswith("-") or "/" in arg for arg in self.arguments):
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
    
    def validate(self) -> tuple[bool, str]:
        """بررسی معتبر بودن نام یا مسیر برنامه."""
        if not self.app_name and not self.app_path:
            return False, "The name or path of the program must be specified"
        
        # بررسی کاراکترهای غیرمجاز
        forbidden_chars = ["<", ">", "|", "&", ";"]
        check_str = self.app_name + (self.app_path or "")
        if any(char in check_str for char in forbidden_chars):
            return False, f"Invalid characters in program name or path: {forbidden_chars}"
        
        return True, "Valid"
    
    def describe(self) -> str:
        """توضیح انسانی."""
        target = self.app_path or self.app_name
        args_str = f" with arguments {' '.join(self.arguments)}" if self.arguments else ""
        return f"Launching application '{target}'{args_str}"


@dataclass
class InstallPackageAction(SystemAction):
    """اقدام برای نصب نرم‌افزار از طریق مدیر بسته."""
    
    package_name: str = ""
    package_manager: str = "winget"  # winget, choco, pip, npm
    version: Optional[str] = None
    silent: bool = True
    
    def get_risk_level(self) -> RiskLevel:
        """نصب نرم‌افزار خطر متوسط دارد."""
        return RiskLevel.MEDIUM
    
    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی نام بسته و مدیر بسته."""
        if not self.package_name:
            return False, "Package name must not be empty"
        
        valid_managers = ["winget", "choco", "pip", "npm"]
        if self.package_manager not in valid_managers:
            return False, f"Invalid package manager. Valid options: {valid_managers}"
        
        # بررسی کاراکترهای مشکوک
        if any(char in self.package_name for char in ["&", "|", ";", ">", "<"]):
            return False, "Suspicious characters in package name"
        
        return True, "Valid"
    
    def describe(self) -> str:
        """Human-readable description."""
        version_str = f" version {self.version}" if self.version else ""
        return f"Installing package '{self.package_name}'{version_str} using {self.package_manager}"


@dataclass
class QueryHardwareAction(SystemAction):
    """اقدام برای دریافت اطلاعات سخت‌افزار."""
    
    query_type: str = "all"  # all, cpu, memory, gpu, disk, network
    
    def get_risk_level(self) -> RiskLevel:
        """خواندن اطلاعات سخت‌افزار بدون خطر است."""
        return RiskLevel.SAFE
    
    def validate(self) -> tuple[bool, str]:
        """بررسی نوع درخواست."""
        valid_types = ["all", "cpu", "memory", "gpu", "disk", "network", "processes"]
        if self.query_type not in valid_types:
            return False, f"Invalid query type. Valid options: {valid_types}"
        return True, "Valid"
    
    def describe(self) -> str:
        """Human-readable description."""
        type_names = {
            "all": "all information",
            "cpu": "CPU",
            "memory": "RAM memory",
            "gpu": "graphics card",
            "disk": "disk",
            "network": "network",
            "processes": "processes",
        }
        return f"Retrieving information about {type_names.get(self.query_type, self.query_type)}"


@dataclass
class TerminateProcessAction(SystemAction):
    """اقدام برای بستن یک فرآیند."""
    
    process_name: Optional[str] = None
    process_id: Optional[int] = None
    force: bool = False
    
    def get_risk_level(self) -> RiskLevel:
        """بستن فرآیند بسته به نوع آن می‌تواند خطرناک باشد."""
        # فرآیندهای سیستمی حیاتی
        critical_processes = [
            "explorer.exe", "csrss.exe", "winlogon.exe", "services.exe",
            "lsass.exe", "smss.exe", "wininit.exe", "system", "dwm.exe"
        ]
        
        if self.process_name and self.process_name.lower() in critical_processes:
            return RiskLevel.CRITICAL
        
        return RiskLevel.MEDIUM if self.force else RiskLevel.LOW
    
    def validate(self) -> tuple[bool, str]:
        """بررسی مشخص بودن هدف."""
        if not self.process_name and not self.process_id:
            return False, "A process name or ID must be specified"
        
        if self.process_id and self.process_id < 0:
            return False, "Invalid process ID"
        
        return True, "Valid"
    
    def describe(self) -> str:
        """توضیح انسانی."""
        target = f"'{self.process_name}'" if self.process_name else f"PID={self.process_id}"
        force_str = " (forced)" if self.force else ""
        return f"Terminating process {target}{force_str}"


# برای راحتی، تایپ‌های اقدامات را export می‌کنیم
__all__ = [
    "RiskLevel",
    "ActionStatus",
    "ActionResult",
    "SystemAction",
    "LaunchAppAction",
    "InstallPackageAction",
    "QueryHardwareAction",
    "TerminateProcessAction",
]
