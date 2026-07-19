# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""Reliability system for autonomous desktop interaction.

Every subsystem should support:
- Retries with intelligent backoff
- Rollback when possible
- Structured logging and diagnostics
- Failure recovery
- Graceful degradation

This module provides the reliability infrastructure that all
other modules can use.
"""

from __future__ import annotations

import logging
import time
import traceback
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Callable

logger = logging.getLogger(__name__)


__all__ = [
    "SystemState",
    "DiagnosticEntry",
    "Checkpoint",
    "ReliabilityManager",
]


class SystemState(Enum):
    """Overall system health state."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    CRITICAL = "critical"


@dataclass
class DiagnosticEntry:
    """A single diagnostic entry for tracking system behavior."""
    timestamp: datetime = field(default_factory=datetime.now)
    component: str = ""
    event_type: str = ""  # error, warning, recovery, checkpoint, rollback
    message: str = ""
    severity: str = "info"
    metadata: dict = field(default_factory=dict)

    def to_log_string(self) -> str:
        return (
            f"[{self.timestamp.strftime('%H:%M:%S')}] "
            f"[{self.severity.upper()}] "
            f"{self.component}: {self.message}"
        )


@dataclass
class Checkpoint:
    """A saved state that can be rolled back to."""
    checkpoint_id: str
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    state_data: dict = field(default_factory=dict)
    screenshot_path: Optional[str] = None
    description: str = ""

    def age_seconds(self) -> float:
        return (datetime.now() - self.timestamp).total_seconds()


class ReliabilityManager:
    """Manages reliability across the entire system.

    Provides:
    - Structured diagnostic logging
    - Checkpoint creation and rollback
    - Failure tracking and pattern detection
    - Graceful degradation when components fail
    - Health monitoring

    Usage:
        >>> reliability = ReliabilityManager()
        >>> reliability.create_checkpoint("before_click", {"target": "OK"})
        >>> try:
        ...     do_click()
        ... except Exception as e:
        ...     reliability.rollback_to("before_click")
    """

    def __init__(self, max_diagnostics: int = 500):
        self.diagnostics: deque[DiagnosticEntry] = deque(maxlen=max_diagnostics)
        self.checkpoints: dict[str, Checkpoint] = {}
        self.failure_counts: dict[str, int] = {}
        self.recovery_counts: dict[str, int] = {}
        self.component_states: dict[str, SystemState] = {}

        self._rollback_handlers: dict[str, Callable] = {}

        logger.info("ReliabilityManager initialized")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Diagnostics
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def log_event(
        self,
        component: str,
        event_type: str,
        message: str,
        severity: str = "info",
        **metadata,
    ):
        entry = DiagnosticEntry(
            component=component,
            event_type=event_type,
            message=message,
            severity=severity,
            metadata=metadata,
        )
        self.diagnostics.append(entry)

        log_method = getattr(logger, severity, logger.info)
        log_method("%s: %s", component, message)

    def log_error(self, component: str, error: Exception, context: str = ""):
        self.failure_counts[component] = self.failure_counts.get(component, 0) + 1

        self.log_event(
            component=component,
            event_type="error",
            message=f"{type(error).__name__}: {error}",
            severity="error",
            context=context,
            traceback=traceback.format_exc(),
        )

        self._update_component_state(component)

    def log_recovery(self, component: str, strategy: str, success: bool):
        self.recovery_counts[component] = self.recovery_counts.get(component, 0) + 1

        self.log_event(
            component=component,
            event_type="recovery",
            message=f"Recovery attempt: {strategy} -> {'success' if success else 'failed'}",
            severity="info" if success else "warning",
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Checkpoints & Rollback
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def create_checkpoint(
        self,
        name: str,
        state_data: Optional[dict] = None,
        screenshot_path: Optional[str] = None,
        description: str = "",
    ) -> Checkpoint:
        import uuid
        checkpoint = Checkpoint(
            checkpoint_id=str(uuid.uuid4())[:8],
            name=name,
            state_data=state_data or {},
            screenshot_path=screenshot_path,
            description=description,
        )
        self.checkpoints[name] = checkpoint
        self.log_event("reliability", "checkpoint", f"Checkpoint created: {name}")
        return checkpoint

    def register_rollback_handler(self, checkpoint_name: str, handler: Callable):
        self._rollback_handlers[checkpoint_name] = handler

    def rollback_to(self, checkpoint_name: str) -> bool:
        checkpoint = self.checkpoints.get(checkpoint_name)
        if checkpoint is None:
            self.log_event(
                "reliability", "rollback",
                f"Checkpoint '{checkpoint_name}' not found",
                severity="warning",
            )
            return False

        handler = self._rollback_handlers.get(checkpoint_name)
        if handler:
            try:
                handler(checkpoint)
                self.log_event(
                    "reliability", "rollback",
                    f"Rollback to '{checkpoint_name}' executed",
                )
                return True
            except Exception as e:
                self.log_error("reliability", e, f"Rollback to '{checkpoint_name}' failed")
                return False

        self.log_event(
            "reliability", "rollback",
            f"No rollback handler for '{checkpoint_name}'",
            severity="warning",
        )
        return False

    def get_checkpoint(self, name: str) -> Optional[Checkpoint]:
        return self.checkpoints.get(name)

    def clear_checkpoints(self):
        self.checkpoints.clear()
        self._rollback_handlers.clear()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Health Monitoring
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _update_component_state(self, component: str):
        failures = self.failure_counts.get(component, 0)
        recoveries = self.recovery_counts.get(component, 0)

        if failures == 0:
            self.component_states[component] = SystemState.HEALTHY
        elif recoveries > failures * 0.8:
            self.component_states[component] = SystemState.DEGRADED
        elif failures > 10:
            self.component_states[component] = SystemState.CRITICAL
        elif failures > 3:
            self.component_states[component] = SystemState.FAILING
        else:
            self.component_states[component] = SystemState.DEGRADED

    def get_component_state(self, component: str) -> SystemState:
        return self.component_states.get(component, SystemState.HEALTHY)

    def get_system_health(self) -> dict:
        states = {}
        for comp, state in self.component_states.items():
            states[comp] = {
                'state': state.value,
                'failures': self.failure_counts.get(comp, 0),
                'recoveries': self.recovery_counts.get(comp, 0),
            }

        if not states:
            overall = SystemState.HEALTHY
        else:
            state_values = [s['state'] for s in states.values()]
            if 'critical' in state_values:
                overall = SystemState.CRITICAL
            elif 'failing' in state_values:
                overall = SystemState.FAILING
            elif 'degraded' in state_values:
                overall = SystemState.DEGRADED
            else:
                overall = SystemState.HEALTHY

        return {
            'overall': overall.value,
            'components': states,
            'total_failures': sum(self.failure_counts.values()),
            'total_recoveries': sum(self.recovery_counts.values()),
        }

    def should_degrade(self, component: str) -> bool:
        state = self.get_component_state(component)
        return state in (SystemState.FAILING, SystemState.CRITICAL)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Retry with Backoff
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def retry_with_backoff(
        self,
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        component: str = "unknown",
        on_retry: Optional[Callable] = None,
    ) -> tuple[bool, Any, str]:
        """Execute a function with retry and exponential backoff.

        Returns:
            (success, result, error_message) tuple
        """
        last_error = ""

        for attempt in range(max_retries + 1):
            try:
                result = func()
                if attempt > 0:
                    self.log_recovery(component, f"retry_attempt_{attempt}", True)
                return True, result, ""
            except Exception as e:
                last_error = str(e)
                self.log_event(
                    component, "retry",
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}",
                    severity="warning",
                )

                if attempt < max_retries:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    delay *= (0.8 + 0.4 * (attempt / max_retries))

                    if on_retry:
                        on_retry(attempt, delay)

                    time.sleep(delay)

        self.log_recovery(component, "all_retries_exhausted", False)
        return False, None, last_error

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Diagnostics Report
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_diagnostics(self, limit: int = 50, severity: Optional[str] = None) -> list[dict]:
        entries = list(self.diagnostics)
        if severity:
            entries = [e for e in entries if e.severity == severity]
        return [
            {
                'timestamp': e.timestamp.isoformat(),
                'component': e.component,
                'event_type': e.event_type,
                'message': e.message,
                'severity': e.severity,
            }
            for e in entries[-limit:]
        ]

    def get_summary(self) -> dict:
        health = self.get_system_health()
        recent_errors = self.get_diagnostics(limit=10, severity="error")

        return {
            'health': health,
            'recent_errors': recent_errors,
            'checkpoints': len(self.checkpoints),
            'diagnostic_entries': len(self.diagnostics),
        }
