# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""ماژول سیستم اتوماسیون ویندوز.

این ماژول امکان اتوماسیون کامل ویندوز را با استفاده از AI فراهم می‌کند.
"""

# اقدامات سیستمی
from .system_actions import (
    RiskLevel,
    ActionStatus,
    ActionResult,
    SystemAction,
    LaunchAppAction,
    InstallPackageAction,
    QueryHardwareAction,
    TerminateProcessAction,
)

# ابزارهای اجرایی
from .system_tools import SystemToolAdapter

# فیلتر امنیتی
from .safety_filter import SafetyFilter, SafetyPolicy, UserConsentManager

# رجیستری قابلیت‌ها
from .system_capabilities import SystemCapability, SystemCapabilityRegistry

# مدیر اجرا
from .execution_manager import ExecutionManager, ExecutionPriority, QueuedAction

# سرویس نظارت
from .monitoring_service import MonitoringService, SystemSnapshot

# AI Brain
from .ai_brain import AIBrain

__all__ = [
    # Actions
    "RiskLevel",
    "ActionStatus",
    "ActionResult",
    "SystemAction",
    "LaunchAppAction",
    "InstallPackageAction",
    "QueryHardwareAction",
    "TerminateProcessAction",
    # Tools
    "SystemToolAdapter",
    # Safety
    "SafetyFilter",
    "SafetyPolicy",
    "UserConsentManager",
    # Capabilities
    "SystemCapability",
    "SystemCapabilityRegistry",
    # Execution
    "ExecutionManager",
    "ExecutionPriority",
    "QueuedAction",
    # Monitoring
    "MonitoringService",
    "SystemSnapshot",
    # AI
    "AIBrain",
]
