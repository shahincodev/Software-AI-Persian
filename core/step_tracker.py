# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Step Tracker - Track execution progress of multi-step workflows.

Provides real-time progress tracking, step status management, and
execution history for workflow_engine.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of an individual execution step."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class StepResult:
    """Result of executing a single step."""
    step_id: str
    step_order: int
    action: str
    status: StepStatus
    output: str = ""
    error: str = ""
    duration_ms: float = 0.0
    attempts: int = 1
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "step_order": self.step_order,
            "action": self.action,
            "status": self.status.value,
            "output": self.output[:500],
            "error": self.error[:500],
            "duration_ms": round(self.duration_ms, 2),
            "attempts": self.attempts,
            "timestamp": self.timestamp.isoformat(),
        }


class StepTracker:
    """Track execution progress of a workflow plan.

    Usage:
        tracker = StepTracker(plan_id="plan_1", total_steps=5)
        tracker.start_step("step_1", 1, "Open Chrome")
        tracker.complete_step("step_1", output="Chrome opened")
        # ... more steps ...
        summary = tracker.get_summary()
    """

    def __init__(self, plan_id: str, total_steps: int, description: str = ""):
        self.plan_id = plan_id
        self.total_steps = total_steps
        self.description = description
        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        self.results: List[StepResult] = []
        self._step_start_times: Dict[str, float] = {}
        self._current_step_id: Optional[str] = None

        logger.info(
            "StepTracker created: plan=%s, steps=%d",
            plan_id, total_steps,
        )

    @property
    def completed_count(self) -> int:
        return sum(
            1 for r in self.results
            if r.status in (StepStatus.SUCCESS, StepStatus.FAILED, StepStatus.SKIPPED)
        )

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.status == StepStatus.SUCCESS)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if r.status == StepStatus.FAILED)

    @property
    def progress_percent(self) -> float:
        if self.total_steps == 0:
            return 100.0
        return (self.completed_count / self.total_steps) * 100

    @property
    def is_complete(self) -> bool:
        return self.completed_count >= self.total_steps

    @property
    def has_failures(self) -> bool:
        return self.failed_count > 0

    @property
    def elapsed_ms(self) -> float:
        if not self.started_at:
            return 0.0
        end = self.finished_at or datetime.now()
        return (end - self.started_at).total_seconds() * 1000

    def start(self) -> None:
        """Mark workflow execution as started."""
        self.started_at = datetime.now()
        logger.info("Workflow started: %s", self.plan_id)

    def finish(self) -> None:
        """Mark workflow execution as finished."""
        self.finished_at = datetime.now()
        elapsed = self.elapsed_ms
        logger.info(
            "Workflow finished: %s (%.0fms, %d/%d succeeded)",
            self.plan_id, elapsed, self.success_count, self.total_steps,
        )

    def start_step(self, step_id: str, order: int, action: str) -> None:
        """Mark a step as running."""
        self._step_start_times[step_id] = time.monotonic()
        self._current_step_id = step_id
        logger.info("Step %d started: %s", order, action[:80])

    def complete_step(
        self,
        step_id: str,
        output: str = "",
        error: str = "",
    ) -> StepResult:
        """Mark a step as completed (success or failure)."""
        start_time = self._step_start_times.pop(step_id, time.monotonic())
        duration_ms = (time.monotonic() - start_time) * 1000

        # Find existing result or create new
        existing = next((r for r in self.results if r.step_id == step_id), None)
        if existing:
            existing.status = StepStatus.SUCCESS if not error else StepStatus.FAILED
            existing.output = output
            existing.error = error
            existing.duration_ms = duration_ms
            result = existing
        else:
            status = StepStatus.SUCCESS if not error else StepStatus.FAILED
            result = StepResult(
                step_id=step_id,
                step_order=0,
                action="",
                status=status,
                output=output,
                error=error,
                duration_ms=duration_ms,
            )
            self.results.append(result)

        self._current_step_id = None
        log_fn = logger.info if not error else logger.warning
        log_fn(
            "Step completed: %s (%.0fms) %s",
            step_id, duration_ms,
            "OK" if not error else f"FAILED: {error[:80]}",
        )
        return result

    def fail_step(self, step_id: str, error: str) -> StepResult:
        """Mark a step as failed."""
        start_time = self._step_start_times.pop(step_id, time.monotonic())
        duration_ms = (time.monotonic() - start_time) * 1000

        result = StepResult(
            step_id=step_id,
            step_order=0,
            action="",
            status=StepStatus.FAILED,
            error=error,
            duration_ms=duration_ms,
        )
        self.results.append(result)
        self._current_step_id = None
        logger.warning("Step failed: %s (%.0fms) %s", step_id, duration_ms, error[:80])
        return result

    def skip_step(self, step_id: str, reason: str = "") -> StepResult:
        """Mark a step as skipped."""
        result = StepResult(
            step_id=step_id,
            step_order=0,
            action="",
            status=StepStatus.SKIPPED,
            output=f"Skipped: {reason}" if reason else "Skipped",
        )
        self.results.append(result)
        logger.info("Step skipped: %s (%s)", step_id, reason[:80])
        return result

    def retry_step(self, step_id: str) -> None:
        """Mark a step as retrying."""
        result = next((r for r in self.results if r.step_id == step_id), None)
        if result:
            result.status = StepStatus.RETRYING
            result.attempts += 1
        logger.info("Step retrying: %s (attempt %d)", step_id, result.attempts if result else 1)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow execution."""
        return {
            "plan_id": self.plan_id,
            "description": self.description,
            "total_steps": self.total_steps,
            "completed": self.completed_count,
            "succeeded": self.success_count,
            "failed": self.failed_count,
            "skipped": sum(1 for r in self.results if r.status == StepStatus.SKIPPED),
            "progress_percent": round(self.progress_percent, 1),
            "elapsed_ms": round(self.elapsed_ms, 2),
            "is_complete": self.is_complete,
            "has_failures": self.has_failures,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "steps": [r.to_dict() for r in self.results],
        }

    def get_status_line(self) -> str:
        """Get a one-line status for display."""
        return (
            f"[{self.plan_id}] "
            f"{self.completed_count}/{self.total_steps} steps "
            f"({self.progress_percent:.0f}%) "
            f"{'OK' if not self.has_failures else 'FAILED'}"
        )

    def get_results_by_status(self, status: StepStatus) -> List[StepResult]:
        """Get all results with a specific status."""
        return [r for r in self.results if r.status == status]

    def get_failed_steps(self) -> List[StepResult]:
        """Get all failed steps."""
        return self.get_results_by_status(StepStatus.FAILED)

    def get_successful_steps(self) -> List[StepResult]:
        """Get all successful steps."""
        return self.get_results_by_status(StepStatus.SUCCESS)
