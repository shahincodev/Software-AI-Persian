# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های RealtimeInterpreter."""

import asyncio
import pytest
from pathlib import Path

from core.realtime_interpreter import (
    RealtimeInterpreter,
    StateSnapshot,
    InterpretationResult,
)
from core.desktop_vision import DesktopVision, WindowInfo, TextBox


class FakeVision:
    """Mock vision برای تست بدون وابستگی."""

    def __init__(self):
        self.call_count = 0
        self.active_window = WindowInfo(
            title="Test Window", x=0, y=0, width=800, height=600, is_active=True
        )
        self.texts = ["Hello", "World", "Test"]

    def get_active_window(self) -> WindowInfo:
        return self.active_window

    def get_all_text_boxes(self) -> list:
        return [
            TextBox(text=t, x=100, y=100, width=50, height=20, confidence=0.95)
            for t in self.texts
        ]


@pytest.mark.asyncio
async def test_interpreter_initialization():
    """تست ایجاد instance."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision, ocr_enabled=True)

    assert interpreter.vision is vision
    assert interpreter.ocr_enabled is True
    assert interpreter.text_threshold == 3
    assert interpreter.max_texts == 10


@pytest.mark.asyncio
async def test_capture_snapshot():
    """تست گرفتن snapshot."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    snapshot = await interpreter._capture_snapshot()

    assert snapshot is not None
    assert snapshot.timestamp > 0
    assert snapshot.active_window is not None
    assert snapshot.active_window.title == "Test Window"
    assert len(snapshot.screen_texts) > 0
    assert snapshot.raw_metadata["text_count"] > 0


@pytest.mark.asyncio
async def test_detect_state_change_no_previous():
    """تست تشخیص تغییر بدون snapshot قبلی."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    curr = await interpreter._capture_snapshot()
    changed = interpreter._detect_state_change(curr)

    # بدون snapshot قبلی، تغییری نیست
    assert changed is False


@pytest.mark.asyncio
async def test_detect_state_change_window_title():
    """تست تشخیص تغییر عنوان پنجره."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    # snapshot اول
    prev = await interpreter._capture_snapshot()
    interpreter.prev_snapshot = prev

    # تغییر عنوان پنجره
    vision.active_window.title = "Different Window"

    # snapshot دوم
    curr = await interpreter._capture_snapshot()
    changed = interpreter._detect_state_change(curr)

    assert changed is True


@pytest.mark.asyncio
async def test_detect_state_change_texts():
    """تست تشخیص تغییر متن‌ها."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    # snapshot اول
    prev = await interpreter._capture_snapshot()
    interpreter.prev_snapshot = prev

    # تغییر متن‌ها
    vision.texts = ["Different", "Texts"]

    # snapshot دوم
    curr = await interpreter._capture_snapshot()
    changed = interpreter._detect_state_change(curr)

    assert changed is True


@pytest.mark.asyncio
async def test_interpret_safe_mode():
    """تست تفسیر در حالت Safe."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    result = await interpreter.interpret(safety_mode="safe")

    assert isinstance(result, InterpretationResult)
    assert result.action == "hint"
    assert result.risk_score == 30.0


@pytest.mark.asyncio
async def test_interpret_power_mode_changed():
    """تست تفسیر در حالت Power با تغییر state."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    # snapshot اول
    await interpreter.interpret(safety_mode="power")

    # تغییر پنجره
    vision.active_window.title = "New Window"

    # snapshot دوم
    result = await interpreter.interpret(safety_mode="power")

    assert result.action == "act"
    assert result.changed is True
    assert result.risk_score == 55.0


@pytest.mark.asyncio
async def test_interpret_power_mode_stable():
    """تست تفسیر در حالت Power بدون تغییر."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    # دو snapshot یکسان
    result1 = await interpreter.interpret(safety_mode="power")
    result2 = await interpreter.interpret(safety_mode="power")

    assert result2.action == "hint"
    assert result2.changed is False
    assert result2.risk_score == 35.0


@pytest.mark.asyncio
async def test_get_context():
    """تست دریافت سیاق."""
    vision = FakeVision()
    interpreter = RealtimeInterpreter(vision=vision)

    context = interpreter.get_context()

    assert isinstance(context, dict)
    assert "prev_window" in context
    assert "prev_text_count" in context
    assert "ocr_enabled" in context
    assert context["ocr_enabled"] is True


@pytest.mark.asyncio
async def test_text_threshold():
    """تست فیلتر کردن متن‌های کوتاه."""
    vision = FakeVision()
    vision.texts = ["a", "hello", "x", "world", "test"]  # mix of short and long
    interpreter = RealtimeInterpreter(vision=vision, text_threshold=3)

    snapshot = await interpreter._capture_snapshot()

    # فقط متن‌های 3+ کاراکتری: "hello", "world", "test"
    assert len(snapshot.screen_texts) <= 3
    for text in snapshot.screen_texts:
        assert len(text) >= 3


@pytest.mark.asyncio
async def test_max_texts_limit():
    """تست محدودیت حداکثر متن‌ها."""
    vision = FakeVision()
    vision.texts = [f"text_{i}" for i in range(20)]  # 20 متن
    interpreter = RealtimeInterpreter(vision=vision, max_texts=5)

    snapshot = await interpreter._capture_snapshot()

    assert len(snapshot.screen_texts) <= 5
