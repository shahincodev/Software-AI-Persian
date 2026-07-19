"""Data models for action execution results and state management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple


class ActionResult(Enum):
    """نتیجه اجرای یک اکشن."""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"
    VERIFICATION_FAILED = "verification_failed"


@dataclass
class ActionState:
    """وضعیت صفحه در یک لحظه خاص - برای State Management."""
    timestamp: datetime
    screenshot_path: Optional[str] = None
    mouse_position: Optional[Tuple[int, int]] = None
    active_window: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionOutcome:
    """نتیجه یک اکشن با جزئیات کامل."""
    result: ActionResult
    message: str
    duration: float
    position: Optional[Tuple[int, int]] = None
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
