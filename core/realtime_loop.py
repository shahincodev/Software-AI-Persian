#!/usr/bin/env python3
# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved

"""حلقه سبک زمان‌واقعی برای مشاهده صفحه و تصمیم‌گیری محدود.

این ماژول یک کلاس RealtimeLoop ارائه می‌کند که می‌تواند با نرخ پایین از صفحه
تصویر بگیرد، تفسیر ساده انجام دهد، و در صورت مجاز بودن اقدام‌های کم‌خطر را
فراخوانی کند. طراحی به‌صورت تزریقی است تا وابستگی به جزئیات بینایی/اکشن
حداقل شود و در تست با mock پوشش داده شود.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from core.action_controller import ActionController
from core.desktop_vision import DesktopVision
from core.realtime_interpreter import RealtimeInterpreter


@dataclass
class RealtimeSnapshot:
    """خروجی مرحله capture."""

    timestamp: float
    meta: Dict[str, Any]


@dataclass
class RealtimeDecision:
    """نتیجه مرحله interpret."""

    action: str  # "noop" | "hint" | "act"
    risk_score: float = 50.0
    payload: Optional[Dict[str, Any]] = None
    message: str = ""


class RealtimeLoop:
    """حلقه سبک زمان‌واقعی.

    پارامترها:
        vision: ماژول بینایی (برای capture سبک)
        action_controller: کنترل‌کننده اکشن‌ها (اختیاری)
        session_control: مدیریت ایمنی/توقف
        fps: نرخ اجرای حلقه (پیشنهادی: 1-2)
        max_actions: سقف اقدام متوالی بدون ارزیابی مجدد
        action_callback: تابع اختیاری برای اجرای اکشن، تزریق‌شده برای تست یا سفارشی‌سازی
        interpreter: تفسیرکننده snapshot‌ها (اختیاری، ایجاد خودکار)
    """

    def __init__(
        self,
        vision: DesktopVision,
        session_control: Any,
        action_controller: Optional[ActionController] = None,
        fps: float = 1.0,
        max_actions: int = 3,
        action_callback: Optional[Callable[[RealtimeDecision], Awaitable[None]]] = None,
        interpreter: Optional[RealtimeInterpreter] = None,
    ) -> None:
        self.vision = vision
        self.session_control = session_control
        self.action_controller = action_controller
        self.fps = max(0.2, min(fps, 10.0))  # محدودیت برای جلوگیری از فشار
        self.max_actions = max(1, max_actions)
        self.action_callback = action_callback
        self.interpreter = interpreter or RealtimeInterpreter(vision=vision)
        self._actions_since_eval = 0
        self._running = False

    async def run_loop(self) -> None:
        """اجرای حلقه زمان‌واقعی تا توقف."""
        self._running = True
        try:
            while self._running and not self.session_control.stopped:
                if self.session_control.paused:
                    await asyncio.sleep(0.2)
                    continue

                snapshot = await self._capture()
                decision = await self._interpret(snapshot)
                await self._act_if_allowed(decision)

                await asyncio.sleep(1.0 / self.fps)
        finally:
            self._running = False

    def stop(self) -> None:
        """توقف نرم حلقه."""
        self._running = False

    async def _capture(self) -> RealtimeSnapshot:
        """گرفتن snapshot سبک. اگر capture شکست بخورد، meta خالی برمی‌گردد."""
        meta: Dict[str, Any] = {}
        ts = time.time()
        try:
            # تلاش برای ثبت اسکرین کوچک؛ اگر تابع موجود نبود، بی‌صدا رد می‌شود.
            if hasattr(self.vision, "save_screenshot"):
                self.vision.save_screenshot("data/logs/cache/realtime_last.png")
                meta["screenshot"] = "data/logs/cache/realtime_last.png"
        except Exception:
            meta["error"] = "capture_failed"
        return RealtimeSnapshot(timestamp=ts, meta=meta)

    async def _interpret(self, snapshot: RealtimeSnapshot) -> RealtimeDecision:
        """تفسیر هوشمند با RealtimeInterpreter: OCR + تشخیص تغییرات + ریسک‌سنجی."""
        try:
            # استفاده از تفسیرکننده برای تحلیل snapshot
            interp_result = await self.interpreter.interpret(
                safety_mode=self.session_control.safety_mode,
                risk_threshold=getattr(self.session_control, "risk_threshold", 70),
            )

            # تبدیل نتیجه تفسیرکننده به RealtimeDecision
            return RealtimeDecision(
                action=interp_result.action,
                risk_score=interp_result.risk_score,
                payload={
                    "confidence": interp_result.confidence,
                    "changed": interp_result.changed,
                    "context": self.interpreter.get_context(),
                },
                message=f"Action: {interp_result.action} (confidence: {interp_result.confidence:.1f}, risk: {interp_result.risk_score:.0f})",
            )
        except Exception as e:
            # در صورت خرابی، بازگشت به تصمیم ایمن
            return RealtimeDecision(
                action="hint",
                risk_score=30,
                message=f"Interpreter error: {str(e)[:50]}",
            )

    async def _act_if_allowed(self, decision: RealtimeDecision) -> None:
        """اجرا بر اساس تصمیم و سقف ریسک/سقف اکشن."""
        # ثبت تصمیم در لاگ (تابع موجود در main.py)
        try:
            from core.realtime_loop import RealtimeDecision as _RD  # type: ignore
            # جلوگیری از import چرخه‌ای با session_control/log_risk_decision در main
            pass
        except Exception:
            pass

        if decision.action == "noop":
            return

        if decision.action in ("hint", "act"):
            # در حالت Safe، هیچ اکشن واقعی انجام نشود
            if self.session_control.safety_mode == "safe":
                return

            # سقف اکشن‌های متوالی
            if self._actions_since_eval >= self.max_actions:
                self._actions_since_eval = 0
                return

            self._actions_since_eval += 1

            # اگر callback تزریق شده باشد، از آن استفاده کن
            if self.action_callback:
                await self.action_callback(decision)
                return

            # در غیر این صورت، اگر action_controller موجود است و اقدام ساده داریم
            if self.action_controller and hasattr(self.action_controller, "noop"):
                try:
                    self.action_controller.noop()  # نوعی heartbeat/آماده‌باش
                except Exception:
                    pass

        return
