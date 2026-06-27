# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Dialog Manager - سازگار با عقب (Backward Compatible Wrapper)

این ماژول برای backward compatibility حفظ شده است.
تمامی قابلیت‌ها به core.intent_analyzer منتقل شده‌اند.

مثال جدید:
    >>> from core.intent_analyzer import IntentAnalyzer
    >>> analyzer = IntentAnalyzer()
    >>> result = await analyzer.analyze("بازی کن تا برگردم")
    >>> if result.requires_clarification:
    ...     result = await analyzer.collect_missing_info(result)
"""

import warnings
from .intent_analyzer import (
    DialogState,
    QuestionType,
    DialogQuestion,
    DialogResponse,
    DialogSession,
    IntentAnalyzer as _IntentAnalyzer,
)

warnings.warn(
    "core.dialog_manager is deprecated. Use core.intent_analyzer.IntentAnalyzer "
    "with collect_missing_info() instead.",
    DeprecationWarning,
    stacklevel=2,
)


class DialogManager:
    """Deprecated: Use IntentAnalyzer.collect_missing_info() instead."""

    def __init__(self, ai_brain=None):
        self._inner = _IntentAnalyzer(ai_brain=ai_brain)

    async def collect_missing_info(self, intent_result, user_language="fa", max_clarifications=3):
        return await self._inner.collect_missing_info(intent_result, user_language, max_clarifications)

    async def clarify_field(self, field_name, current_value, intent, user_language="fa"):
        return await self._inner.clarify_field(field_name, current_value, intent, user_language)

    async def get_suggestions(self, field_name, intent, user_language="fa"):
        return await self._inner.get_suggestions(field_name, intent, user_language)
