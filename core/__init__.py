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

# Week 2: Action Layer (Days 1-10)
from .mouse_control import MouseController
from .keyboard_control import KeyboardController
from .smart_wait import SmartWaiter, WaitStrategy
from .desktop_vision import DesktopVision, MatchMethod
from .action_controller import ActionController
from .desktop_actions import DesktopActions

# Week 2: Safety & Recovery (Day 7)
from .action_safety import ActionSafety
from .action_recovery import (
    ActionRecovery,
    RecoveryConfig,
    RecoveryStrategy,
    ErrorSeverity,
    ActionResult as RecoveryActionResult,
)

# Week 2: Advanced Features (Days 8-9)
from .multi_monitor import MultiMonitor, MonitorInfo
from .context_aware_actions import (
    ContextAwareActions,
    ContextInfo,
    SystemState,
    ApplicationCategory,
)

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
    # Week 2: Action Layer
    "MouseController",
    "KeyboardController",
    "SmartWaiter",
    "WaitStrategy",
    "DesktopVision",
    "MatchMethod",
    "ActionController",
    "DesktopActions",
    # Week 2: Safety & Recovery
    "ActionSafety",
    "ActionRecovery",
    "RecoveryConfig",
    "RecoveryStrategy",
    "ErrorSeverity",
    "RecoveryActionResult",
    # Week 2: Advanced Features
    "MultiMonitor",
    "MonitorInfo",
    "ContextAwareActions",
    "ContextInfo",
    "SystemState",
    "ApplicationCategory",
]
