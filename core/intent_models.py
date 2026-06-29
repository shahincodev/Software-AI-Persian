"""Data models and enums for the intent analysis system."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DialogState(Enum):
    """وضعیت‌های یک نشست دیالوگ."""
    IDLE = "idle"
    QUESTIONING = "questioning"
    CONFIRMING = "confirming"
    CLARIFYING = "clarifying"
    COMPLETE = "complete"
    ERROR = "error"


class QuestionType(Enum):
    """نوع سوال در دیالوگ."""
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    CONFIRMATION = "confirmation"
    CLARIFICATION = "clarification"


class ConfidenceLevel(Enum):
    """سطوح اطمینان از پیش تعریف شده."""
    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.00


@dataclass
class DialogQuestion:
    """یک سوال برای ارائه به کاربر در حین شفاف‌سازی."""
    field_name: str
    question_text: str
    question_text_en: Optional[str] = None
    question_type: QuestionType = QuestionType.OPEN_ENDED
    suggestions: List[str] = field(default_factory=list)
    required: bool = True
    retries_allowed: int = 2


@dataclass
class DialogResponse:
    """پاسخ کاربر به یک سوال دیالوگ."""
    field_name: str
    answer: str
    confidence: float = 1.0
    clarification_needed: bool = False


@dataclass
class DialogSession:
    """مدیریت وضعیت یک مکالمه شفاف‌سازی."""
    session_id: str
    intent_result: IntentAnalysisResult
    questions_asked: List[DialogQuestion] = field(default_factory=list)
    responses: List[DialogResponse] = field(default_factory=list)
    state: DialogState = DialogState.IDLE
    complete_intent: Optional[Intent] = None

    def is_complete(self) -> bool:
        """بررسی کامل شدن نشست."""
        return self.state == DialogState.COMPLETE and self.complete_intent is not None


@dataclass
class Intent:
    """مدل اصلی نیت کاربر."""
    verb: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_request: str = ""
    language: str = "en"

    def is_confident(self, threshold: float = 0.70) -> bool:
        """بررسی اینکه آیا نیت با اطمینان کافی تشخیص داده شده است."""
        return self.confidence >= threshold

    def __str__(self) -> str:
        return f"Intent(verb={self.verb}, target={self.target}, conf={self.confidence:.0%})"


@dataclass
class IntentAnalysisResult:
    """نتیجه تحلیل کامل یک درخواست کاربر."""
    intent: Intent
    missing_fields: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    requires_clarification: bool = False


