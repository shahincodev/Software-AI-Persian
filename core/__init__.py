# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

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
from .desktop_vision import DesktopVision
from .action_controller import ActionController
from .desktop_actions import (
    ClickAction,
    TypeAction,
    WaitAction,
    DragDropAction,
    HotkeyAction,
    ScrollAction,
)

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

# Phase 4: Multi-Step Planning
from .plan_generator import PlanGenerator, ExecutionPlan, ExecutionStep, StepType, ExecutionMode
from .plan_validator import PlanValidator, ValidationLevel, ValidationStatus
from .step_tracker import StepTracker, StepStatus, StepResult
from .workflow_engine import WorkflowEngine, WorkflowResult

# Phase 5: Persistent Memory
from .memory_integrator import MemoryManager, MemoryItem, ShortTermMemory, LongTermMemory

# New Architecture: Intelligent Engines
from .mouse_engine import MouseEngine, MouseButton, ClickPattern, ClickResult, TargetInfo
from .keyboard_engine import KeyboardEngine, TypingMode, TypingSpeed, TypeResult, Hotkeys
from .security_engine import SecurityEngine, RiskLevel as SecurityRiskLevel, TrustLevel, SecurityDecision, SecurityAssessment
from .reasoning_pipeline import ReasoningPipeline, PipelineStage, PlanStep, AgentResult
from .uia_provider import UIAProvider, UIAElement, UIATreeSnapshot
from .reliability import ReliabilityManager, SystemState, Checkpoint, DiagnosticEntry

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
    "ActionController",
    "ClickAction",
    "TypeAction",
    "WaitAction",
    "DragDropAction",
    "HotkeyAction",
    "ScrollAction",
    # Week 2: Safety & Recovery
    "ActionSafety",
    "ActionRecovery",
    "RecoveryConfig",
    "RecoveryStrategy",
    "ErrorSeverity",
    "RecoveryActionResult",
    # Phase 4: Multi-Step Planning
    "PlanGenerator",
    "ExecutionPlan",
    "ExecutionStep",
    "StepType",
    "ExecutionMode",
    "PlanValidator",
    "ValidationLevel",
    "ValidationStatus",
    "StepTracker",
    "StepStatus",
    "StepResult",
    "WorkflowEngine",
    "WorkflowResult",
    # Phase 5: Persistent Memory
    "MemoryManager",
    "MemoryItem",
    "ShortTermMemory",
    "LongTermMemory",
    # New Architecture: Intelligent Engines
    "MouseEngine",
    "MouseButton",
    "ClickPattern",
    "ClickResult",
    "TargetInfo",
    "KeyboardEngine",
    "TypingMode",
    "TypingSpeed",
    "TypeResult",
    "Hotkeys",
    "SecurityEngine",
    "SecurityRiskLevel",
    "TrustLevel",
    "SecurityDecision",
    "SecurityAssessment",
    "ReasoningPipeline",
    "PipelineStage",
    "ExecutionPlan",
    "PlanStep",
    "AgentResult",
    "UIAProvider",
    "UIAElement",
    "UIATreeSnapshot",
    "ReliabilityManager",
    "SystemState",
    "Checkpoint",
    "DiagnosticEntry",
]
