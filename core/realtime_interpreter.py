# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تفسیرکننده سبک برای حلقه زمان‌واقعی.

این ماژول قابلیت تفسیر snapshot‌های صفحه را فراهم می‌کند:
- استخراج OCR سبک (عنوان پنجره، متن‌های درشت)
- شناسایی تغییرات state (قبل/بعد)
- حفظ سیاق تاریخی برای یادگیری
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from core.desktop_vision import DesktopVision, TextBox, WindowInfo

logger = logging.getLogger(__name__)


@dataclass
class StateSnapshot:
    """snapshot حالت صفحه در یک لحظه."""

    timestamp: float
    active_window: Optional[WindowInfo] = None
    screen_texts: List[str] = field(default_factory=list)
    detected_elements: Dict[str, Any] = field(default_factory=dict)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterpretationResult:
    """نتیجه تفسیر snapshot."""

    action: str  # "noop" | "hint" | "act"
    risk_score: float = 50.0
    confidence: float = 0.5
    changed: bool = False  # آیا state تغییر کرده
    payload: Optional[Dict[str, Any]] = None
    message: str = ""
    prev_snapshot: Optional[StateSnapshot] = None
    curr_snapshot: Optional[StateSnapshot] = None


class RealtimeInterpreter:
    """تفسیرکننده هوشمند برای حلقه زمان‌واقعی.

    پارامترها:
        vision: ماژول بینایی (DesktopVision)
        ocr_enabled: فعال‌سازی OCR سبک (پیش‌فرض: True)
        text_threshold: حداقل طول متن برای ثبت (پیش‌فرض: 3)
        max_texts: حداکثر متن‌هایی که ثبت شود (پیش‌فرض: 10)
    """

    def __init__(
        self,
        vision: DesktopVision,
        ocr_enabled: bool = True,
        text_threshold: int = 3,
        max_texts: int = 10,
    ) -> None:
        self.vision = vision
        self.ocr_enabled = ocr_enabled
        self.text_threshold = text_threshold
        self.max_texts = max_texts
        self.prev_snapshot: Optional[StateSnapshot] = None
        self.prev_window_title: Optional[str] = None

    async def interpret(
        self,
        safety_mode: str = "safe",
        risk_threshold: float = 70.0,
    ) -> InterpretationResult:
        """تفسیر وضعیت صفحه و تصمیم‌گیری.

        Args:
            safety_mode: حالت ایمنی ("safe" | "power")
            risk_threshold: آستانه ریسک برای اقدام

        Returns:
            نتیجه تفسیر شامل تصمیم و سیاق
        """
        # مرحله 1: گرفتن snapshot فعلی
        curr_snapshot = await self._capture_snapshot()

        # مرحله 2: تشخیص تغییرات
        changed = self._detect_state_change(curr_snapshot)

        # مرحله 3: تفسیر بر اساس حالت و تغییرات
        if safety_mode == "safe":
            decision = "hint"
            risk = 30.0
        else:
            # در Power: اگر تغییر بود، احتمال act بیشتر است
            if changed:
                decision = "act"
                risk = 55.0
            else:
                decision = "hint"
                risk = 35.0

        # مرحله 4: بسته‌بندی نتیجه
        result = InterpretationResult(
            action=decision,
            risk_score=risk,
            confidence=0.6 if changed else 0.4,
            changed=changed,
            message=f"State {'changed' if changed else 'stable'}",
            prev_snapshot=self.prev_snapshot,
            curr_snapshot=curr_snapshot,
        )

        # ذخیره برای مقایسه بعدی
        self.prev_snapshot = curr_snapshot

        return result

    async def _capture_snapshot(self) -> StateSnapshot:
        """گرفتن snapshot فعلی صفحه."""
        snapshot = StateSnapshot(timestamp=0)

        try:
            # دریافت زمان (تقریبی)
            import time

            snapshot.timestamp = time.time()

            # شناسایی پنجره فعال
            if hasattr(self.vision, "get_active_window"):
                try:
                    window = self.vision.get_active_window()
                    # ایجاد copy برای جلوگیری از مشکلات reference
                    if window:
                        snapshot.active_window = copy.deepcopy(window)
                except Exception as e:
                    logger.debug(f"Failed to get active window: {e}")

            # OCR سبک اگر فعال باشد
            if self.ocr_enabled:
                try:
                    texts = self._extract_texts_lightweight()
                    snapshot.screen_texts = texts
                except Exception as e:
                    logger.debug(f"OCR extraction failed: {e}")

            # ذخیره metadata
            snapshot.raw_metadata = {
                "window_title": snapshot.active_window.title
                if snapshot.active_window
                else None,
                "text_count": len(snapshot.screen_texts),
            }

        except Exception as e:
            logger.warning(f"Snapshot capture failed: {e}")

        return snapshot

    def _extract_texts_lightweight(self) -> List[str]:
        """استخراج متن‌های سبک (تنها متن‌های درشت و عنوان).

        این متد برای کاهش مصرف OCR:
        - فقط متن‌های بزرگتر از text_threshold را اخذ می‌کند
        - حداکثر max_texts متن را برمی‌گرداند
        """
        texts = []

        try:
            if hasattr(self.vision, "get_all_text_boxes"):
                try:
                    boxes = self.vision.get_all_text_boxes()
                    if boxes:
                        for box in boxes:
                            # بررسی اینکه box دارای text است
                            text = None
                            if isinstance(box, TextBox):
                                text = box.text
                            elif hasattr(box, "text"):
                                text = box.text
                            
                            if text and len(text) >= self.text_threshold:
                                texts.append(text.strip())
                                if len(texts) >= self.max_texts:
                                    break
                except Exception as e:
                    logger.debug(f"get_all_text_boxes failed: {e}")

        except Exception as e:
            logger.debug(f"Text extraction failed: {e}")

        return texts

    def _detect_state_change(self, curr_snapshot: StateSnapshot) -> bool:
        """تشخیص تغییر state با مقایسه snapshot‌ها.

        معیارهای تغییر:
        - تغییر عنوان پنجره فعال
        - تغییر متن‌های روی صفحه
        """
        if not self.prev_snapshot:
            # اولین snapshot؛ هنوز تغییری نیست
            return False

        # معیار 1: تغییر عنوان پنجره
        prev_title = (
            self.prev_snapshot.active_window.title
            if self.prev_snapshot.active_window
            else None
        )
        curr_title = (
            curr_snapshot.active_window.title
            if curr_snapshot.active_window
            else None
        )

        if prev_title != curr_title:
            logger.debug(f"Window title changed: {prev_title} → {curr_title}")
            return True

        # معیار 2: تغییر متن‌های روی صفحه (حداقل 1 متن جدید یا حذف شده)
        prev_texts = set(self.prev_snapshot.screen_texts)
        curr_texts = set(curr_snapshot.screen_texts)

        if prev_texts != curr_texts:
            logger.debug(f"Screen texts changed: {len(prev_texts)} → {len(curr_texts)}")
            return True

        return False

    def get_context(self) -> Dict[str, Any]:
        """دریافت سیاق فعلی برای لاگ یا تصمیم‌گیری."""
        return {
            "prev_window": self.prev_snapshot.active_window.title
            if self.prev_snapshot and self.prev_snapshot.active_window
            else None,
            "prev_text_count": len(self.prev_snapshot.screen_texts)
            if self.prev_snapshot
            else 0,
            "ocr_enabled": self.ocr_enabled,
            "text_threshold": self.text_threshold,
        }
