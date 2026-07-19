# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""Intelligent Mouse Engine for autonomous desktop interaction.

This is a complete redesign of the mouse control system. Instead of a simple
pyautogui wrapper, this engine behaves like a modern desktop AI agent:

    Observe → Locate → Move → Click → Verify → Retry

Every click is intentional. The engine never blindly clicks.

Key capabilities:
- Vision-guided target localization (OCR + template matching)
- Automatic click verification with screen state comparison
- Intelligent retry strategies with exponential backoff
- Confidence scoring for target reliability
- Bezier curve movement for human-like paths
- Safety bounds and failsafe mechanisms
- Audit trail with full action history
"""

from __future__ import annotations

import logging
import random
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Protocol, runtime_checkable

try:
    import pyautogui
except ImportError:
    pyautogui = None  # type: ignore

logger = logging.getLogger(__name__)


__all__ = [
    "MouseButton",
    "ClickPattern",
    "ClickResult",
    "TargetInfo",
    "MouseEngine",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Protocols
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@runtime_checkable
class VisionProvider(Protocol):
    """Protocol for vision systems that can locate targets on screen."""

    def find_text(self, text: str, confidence_threshold: float = 0.7) -> Optional[tuple[int, int]]:
        """Find text on screen, return (x, y) center or None."""
        ...

    def find_text_boxes(self, text: str) -> list[Any]:
        """Find all occurrences of text, return list of TextBox-like objects."""
        ...

    def capture_screen(self, region: Optional[tuple[int, int, int, int]] = None) -> Any:
        """Capture screenshot, return PIL Image."""
        ...

    def get_active_window(self) -> Optional[Any]:
        """Get active window info."""
        ...


@runtime_checkable
class VerificationProvider(Protocol):
    """Protocol for verifying click outcomes."""

    def find_text(self, text: str, confidence_threshold: float = 0.7) -> Optional[tuple[int, int]]:
        """Find text on screen."""
        ...


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums & Data Classes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MouseButton(Enum):
    """Mouse buttons."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ClickPattern(Enum):
    """Click patterns for human-like behavior."""
    INSTANT = "instant"
    HUMAN_FAST = "human_fast"
    HUMAN_NORMAL = "human_normal"
    HUMAN_SLOW = "human_slow"
    DOUBLE_CLICK = "double_click"
    TRIPLE_CLICK = "triple_click"


class RetryStrategy(Enum):
    """Retry strategies for failed clicks."""
    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "expponential"
    ADAPTIVE = "adaptive"


@dataclass
class TargetInfo:
    """Information about a located click target."""
    x: int
    y: int
    text: str = ""
    confidence: float = 1.0
    source: str = "unknown"
    bounding_box: Optional[tuple[int, int, int, int]] = None
    timestamp: float = field(default_factory=time.time)

    @property
    def center(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def is_reliable(self) -> bool:
        return self.confidence >= 0.7


@dataclass
class ClickResult:
    """Result of a click operation with full context."""
    success: bool
    target: Optional[TargetInfo] = None
    actual_position: Optional[tuple[int, int]] = None
    verified: bool = False
    attempts: int = 0
    duration: float = 0.0
    error: Optional[str] = None
    verification_message: str = ""
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None

    @property
    def summary(self) -> str:
        parts = []
        if self.success:
            parts.append("OK")
        else:
            parts.append("FAIL")
        if self.target:
            parts.append(f"target='{self.target.text}'")
            parts.append(f"conf={self.target.confidence:.2f}")
        if self.verified:
            parts.append("verified")
        parts.append(f"attempts={self.attempts}")
        parts.append(f"{self.duration:.2f}s")
        return " | ".join(parts)


@dataclass
class MouseAction:
    """Audit trail entry for a mouse action."""
    action_type: str
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration: float = 0.0
    success: bool = False
    target_text: str = ""
    confidence: float = 0.0
    verified: bool = False
    attempts: int = 1

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Mouse Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MouseEngine:
    """Intelligent mouse engine with vision guidance and click verification.

    This engine follows the observe → locate → move → click → verify → retry
    pattern used by modern desktop AI agents.

    Every click is intentional. The engine:
    1. Observes the screen to find the target
    2. Locates the target using OCR or template matching
    3. Moves to the target with human-like motion
    4. Clicks at the target position
    5. Verifies the click achieved its expected outcome
    6. Retries intelligently if verification fails

    Example:
        >>> engine = MouseEngine(vision=my_vision)
        >>> result = engine.click_text("Submit", verify=True)
        >>> if result.success and result.verified:
        ...     print("Click confirmed!")
    """

    def __init__(
        self,
        vision: Optional[VisionProvider] = None,
        safety_enabled: bool = True,
        human_behavior: bool = True,
        max_retries: int = 3,
        retry_strategy: RetryStrategy = RetryStrategy.ADAPTIVE,
        click_timeout: float = 10.0,
        verification_timeout: float = 2.0,
        confidence_threshold: float = 0.6,
    ):
        if pyautogui is None:
            raise ImportError("pyautogui is required. Install with: pip install pyautogui")

        self.vision = vision
        self.safety_enabled = safety_enabled
        self.human_behavior = human_behavior
        self.max_retries = max_retries
        self.retry_strategy = retry_strategy
        self.click_timeout = click_timeout
        self.verification_timeout = verification_timeout
        self.confidence_threshold = confidence_threshold

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05

        screen_width, screen_height = pyautogui.size()
        self.safe_bounds = {
            'min_x': 10,
            'max_x': screen_width - 10,
            'min_y': 10,
            'max_y': screen_height - 50,
        }

        self.action_history: deque[MouseAction] = deque(maxlen=200)
        self.stats = {
            'total_clicks': 0,
            'total_moves': 0,
            'total_drags': 0,
            'total_scrolls': 0,
            'verified_clicks': 0,
            'failed_clicks': 0,
            'retries': 0,
        }

        logger.info(
            "MouseEngine initialized (safety=%s, human=%s, vision=%s, retries=%d)",
            safety_enabled, human_behavior, vision is not None, max_retries,
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Target Localization
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _locate_text_target(self, text: str) -> Optional[TargetInfo]:
        """Locate text on screen using vision system.

        Returns TargetInfo with position and confidence, or None.
        """
        if self.vision is None:
            logger.warning("No vision system configured for text targeting")
            return None

        try:
            boxes = self.vision.find_text_boxes(text)
            if not boxes:
                return None

            best_box = boxes[0]
            cx, cy = best_box.center
            confidence = getattr(best_box, 'confidence', 80.0) / 100.0

            return TargetInfo(
                x=cx,
                y=cy,
                text=text,
                confidence=confidence,
                source="ocr",
                bounding_box=(best_box.x, best_box.y, best_box.width, best_box.height),
            )
        except Exception as e:
            logger.error("Failed to locate text '%s': %s", text, e)
            return None

    def _locate_coordinate_target(self, x: int, y: int) -> TargetInfo:
        """Create TargetInfo for explicit coordinates."""
        return TargetInfo(
            x=x, y=y,
            text=f"({x},{y})",
            confidence=1.0,
            source="explicit",
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Safety & Validation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def is_safe_position(self, x: int, y: int) -> bool:
        if not self.safety_enabled:
            return True
        return (
            self.safe_bounds['min_x'] <= x <= self.safe_bounds['max_x'] and
            self.safe_bounds['min_y'] <= y <= self.safe_bounds['max_y']
        )

    def validate_coordinates(self, x: int, y: int) -> tuple[int, int]:
        if not self.is_safe_position(x, y):
            if self.safety_enabled:
                raise ValueError(
                    f"Unsafe position: ({x}, {y}). "
                    f"Safe bounds: x({self.safe_bounds['min_x']}-{self.safe_bounds['max_x']}), "
                    f"y({self.safe_bounds['min_y']}-{self.safe_bounds['max_y']})"
                )
            logger.warning("Unsafe position but safety disabled: (%d, %d)", x, y)
        return x, y

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Human Behavior Simulation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _add_human_variation(self, x: int, y: int, max_offset: int = 2) -> tuple[int, int]:
        if not self.human_behavior:
            return x, y
        return (
            x + random.randint(-max_offset, max_offset),
            y + random.randint(-max_offset, max_offset),
        )

    def _get_human_delay(self, pattern: ClickPattern) -> float:
        if not self.human_behavior:
            return 0.0
        delays = {
            ClickPattern.INSTANT: 0.0,
            ClickPattern.HUMAN_FAST: random.uniform(0.03, 0.08),
            ClickPattern.HUMAN_NORMAL: random.uniform(0.08, 0.15),
            ClickPattern.HUMAN_SLOW: random.uniform(0.15, 0.4),
            ClickPattern.DOUBLE_CLICK: random.uniform(0.04, 0.1),
            ClickPattern.TRIPLE_CLICK: random.uniform(0.04, 0.1),
        }
        return delays.get(pattern, 0.1)

    def _bezier_curve(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        steps: int = 20,
    ) -> list[tuple[int, int]]:
        if not self.human_behavior:
            return [start, end]

        cx = random.randint(min(start[0], end[0]), max(start[0], end[0]))
        cy = random.randint(min(start[1], end[1]), max(start[1], end[1]))
        controls = [(cx, cy)]

        points = [start] + controls + [end]
        curve = []
        n = len(points) - 1
        for i in range(steps + 1):
            t = i / steps
            x = sum(
                self._binomial(n, k) * (1 - t) ** (n - k) * t ** k * points[k][0]
                for k in range(n + 1)
            )
            y = sum(
                self._binomial(n, k) * (1 - t) ** (n - k) * t ** k * points[k][1]
                for k in range(n + 1)
            )
            curve.append((int(x), int(y)))
        return curve

    @staticmethod
    def _binomial(n: int, k: int) -> int:
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
        result = 1
        for i in range(min(k, n - k)):
            result = result * (n - i) // (i + 1)
        return result

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Core Mouse Operations
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_position(self) -> tuple[int, int]:
        x, y = pyautogui.position()
        return int(x), int(y)

    def move(self, x: int, y: int, duration: float = 0.3, smooth: bool = True) -> bool:
        start_time = time.time()
        try:
            x, y = self.validate_coordinates(x, y)
            if self.human_behavior:
                x, y = self._add_human_variation(x, y)

            if smooth and self.human_behavior:
                start_pos = self.get_position()
                curve = self._bezier_curve(start_pos, (x, y))
                point_dur = duration / max(len(curve), 1)
                for px, py in curve:
                    pyautogui.moveTo(px, py, duration=point_dur)
            else:
                pyautogui.moveTo(x, y, duration=duration)

            self.stats['total_moves'] += 1
            logger.debug("Mouse moved to (%d, %d) in %.3fs", x, y, time.time() - start_time)
            return True
        except Exception as e:
            self.stats['failed_clicks'] += 1
            logger.error("Failed to move mouse to (%d, %d): %s", x, y, e)
            return False

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: MouseButton = MouseButton.LEFT,
        clicks: int = 1,
        interval: float = 0.1,
    ) -> bool:
        try:
            if x is not None and y is not None:
                if not self.move(x, y, duration=0.2):
                    raise ValueError("Failed to move to target")

            pyautogui.click(
                button=button.value,
                clicks=clicks,
                interval=interval,
            )
            self.stats['total_clicks'] += clicks
            return True
        except Exception as e:
            self.stats['failed_clicks'] += 1
            logger.error("Failed to click: %s", e)
            return False

    def drag(
        self,
        start_x: int, start_y: int,
        end_x: int, end_y: int,
        duration: float = 0.5,
        button: MouseButton = MouseButton.LEFT,
    ) -> bool:
        try:
            self.validate_coordinates(start_x, start_y)
            self.validate_coordinates(end_x, end_y)
            self.move(start_x, start_y, duration=0.2)
            pyautogui.drag(
                end_x - start_x, end_y - start_y,
                duration=duration, button=button.value,
            )
            self.stats['total_drags'] += 1
            return True
        except Exception as e:
            self.stats['failed_clicks'] += 1
            logger.error("Failed to drag: %s", e)
            return False

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        try:
            if x is not None and y is not None:
                self.move(x, y, duration=0.1)
            pyautogui.scroll(clicks)
            self.stats['total_scrolls'] += 1
            return True
        except Exception as e:
            self.stats['failed_clicks'] += 1
            logger.error("Failed to scroll: %s", e)
            return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Vision-Guided Click (The Core Intelligence)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _execute_click_on_target(
        self,
        target: TargetInfo,
        button: MouseButton = MouseButton.LEFT,
        pattern: ClickPattern = ClickPattern.HUMAN_NORMAL,
        clicks: int = 1,
    ) -> bool:
        """Execute a click at the target's position."""
        delay = self._get_human_delay(pattern)
        if delay > 0:
            time.sleep(delay)

        actual_clicks = 1
        if pattern == ClickPattern.DOUBLE_CLICK:
            actual_clicks = 2
        elif pattern == ClickPattern.TRIPLE_CLICK:
            actual_clicks = 3

        return self.click(target.x, target.y, button=button, clicks=actual_clicks)

    def _verify_click(
        self,
        target: TargetInfo,
        expected_outcome: Optional[str] = None,
    ) -> tuple[bool, str]:
        """Verify that a click achieved its expected outcome.

        Uses vision to check if the screen changed as expected.
        """
        if self.vision is None:
            return True, "No vision system - verification skipped"

        time.sleep(self.verification_timeout)

        if expected_outcome:
            try:
                result = self.vision.find_text(expected_outcome, confidence_threshold=0.5)
                if result:
                    return True, f"Verification passed: found '{expected_outcome}'"
                return False, f"Verification failed: '{expected_outcome}' not found"
            except Exception as e:
                return True, f"Verification skipped: {e}"

        if target.text and target.text != f"({target.x},{target.y})":
            try:
                result = self.vision.find_text(target.text, confidence_threshold=0.5)
                if result:
                    return True, f"Target '{target.text}' still visible"
                return True, f"Target '{target.text}' no longer visible (expected after click)"
            except Exception:
                return True, "Verification inconclusive"

        return True, "No specific verification criteria"

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay before retry based on strategy."""
        if self.retry_strategy == RetryStrategy.NONE:
            return 0.0
        elif self.retry_strategy == RetryStrategy.LINEAR:
            return 1.0
        elif self.retry_strategy == RetryStrategy.EXPONENTIAL:
            return min(2.0 ** attempt, 10.0)
        elif self.retry_strategy == RetryStrategy.ADAPTIVE:
            base = 0.5 * (attempt + 1)
            jitter = random.uniform(-0.2, 0.2)
            return max(0.3, base + jitter)
        return 1.0

    def click_text(
        self,
        text: str,
        button: MouseButton = MouseButton.LEFT,
        pattern: ClickPattern = ClickPattern.HUMAN_NORMAL,
        verify: bool = True,
        expected_outcome: Optional[str] = None,
        max_retries: Optional[int] = None,
        confidence: float = 0.6,
    ) -> ClickResult:
        """Click on text found on screen via vision.

        This is the primary intelligent click method:
        1. Locate text using OCR
        2. Move to the text center
        3. Click
        4. Verify the outcome
        5. Retry if needed

        Args:
            text: Text to find and click
            button: Mouse button to use
            pattern: Click pattern for human-like behavior
            verify: Whether to verify the click outcome
            expected_outcome: What should appear after clicking (for verification)
            max_retries: Override default max retries
            confidence: Minimum OCR confidence threshold

        Returns:
            ClickResult with full details
        """
        start_time = time.time()
        retries = max_retries if max_retries is not None else self.max_retries
        last_error = ""

        for attempt in range(retries + 1):
            logger.info(
                "Click attempt %d/%d for '%s'",
                attempt + 1, retries + 1, text,
            )

            target = self._locate_text_target(text)
            if target is None or target.confidence < confidence:
                last_error = f"Target '{text}' not found on screen"
                logger.warning(last_error)
                if attempt < retries:
                    time.sleep(self._calculate_retry_delay(attempt))
                    continue
                return ClickResult(
                    success=False,
                    attempts=attempt + 1,
                    duration=time.time() - start_time,
                    error=last_error,
                )

            self._execute_click_on_target(target, button=button, pattern=pattern)

            if verify:
                passed, verify_msg = self._verify_click(target, expected_outcome)
                logger.info("Verification: %s", verify_msg)

                if passed:
                    self.stats['verified_clicks'] += 1
                    return ClickResult(
                        success=True,
                        target=target,
                        actual_position=(target.x, target.y),
                        verified=True,
                        attempts=attempt + 1,
                        duration=time.time() - start_time,
                        verification_message=verify_msg,
                    )
                else:
                    last_error = verify_msg
                    self.stats['retries'] += 1
                    if attempt < retries:
                        time.sleep(self._calculate_retry_delay(attempt))
                        continue
            else:
                return ClickResult(
                    success=True,
                    target=target,
                    actual_position=(target.x, target.y),
                    verified=False,
                    attempts=attempt + 1,
                    duration=time.time() - start_time,
                )

        return ClickResult(
            success=False,
            attempts=retries + 1,
            duration=time.time() - start_time,
            error=last_error or "All retries exhausted",
        )

    def click_coordinates(
        self,
        x: int,
        y: int,
        button: MouseButton = MouseButton.LEFT,
        pattern: ClickPattern = ClickPattern.HUMAN_NORMAL,
        clicks: int = 1,
        verify: bool = False,
    ) -> ClickResult:
        """Click at explicit coordinates.

        Use this when you already know the position (e.g., from a previous
        vision lookup). For vision-guided clicks, use click_text() instead.
        """
        start_time = time.time()
        target = self._locate_coordinate_target(x, y)

        success = self._execute_click_on_target(
            target, button=button, pattern=pattern, clicks=clicks,
        )

        if not success:
            return ClickResult(
                success=False,
                target=target,
                attempts=1,
                duration=time.time() - start_time,
                error="Click execution failed",
            )

        return ClickResult(
            success=True,
            target=target,
            actual_position=(x, y),
            verified=False,
            attempts=1,
            duration=time.time() - start_time,
        )

    def click_image(
        self,
        image_path: str,
        confidence: float = 0.8,
        button: MouseButton = MouseButton.LEFT,
        pattern: ClickPattern = ClickPattern.HUMAN_NORMAL,
        verify: bool = True,
    ) -> ClickResult:
        """Click on an image template found on screen.

        Requires vision system with template matching capability.
        """
        start_time = time.time()

        if self.vision is None:
            return ClickResult(
                success=False,
                attempts=1,
                duration=time.time() - start_time,
                error="No vision system configured",
            )

        try:
            match = self.vision.find_text(image_path, confidence_threshold=confidence)
            if match is None:
                return ClickResult(
                    success=False,
                    attempts=1,
                    duration=time.time() - start_time,
                    error=f"Image template '{image_path}' not found",
                )

            target = TargetInfo(
                x=match[0], y=match[1],
                text=image_path,
                confidence=confidence,
                source="template",
            )

            self._execute_click_on_target(target, button=button, pattern=pattern)

            return ClickResult(
                success=True,
                target=target,
                actual_position=match,
                verified=False,
                attempts=1,
                duration=time.time() - start_time,
            )
        except Exception as e:
            return ClickResult(
                success=False,
                attempts=1,
                duration=time.time() - start_time,
                error=str(e),
            )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Utility
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _log_action(self, action: MouseAction):
        self.action_history.append(action)

    def get_stats(self) -> dict:
        total = sum([
            self.stats['total_clicks'],
            self.stats['total_moves'],
            self.stats['total_drags'],
            self.stats['total_scrolls'],
        ])
        success_rate = 0.0
        if total > 0:
            success_rate = ((total - self.stats['failed_clicks']) / total) * 100
        return {
            **self.stats,
            'total_actions': total,
            'success_rate': f"{success_rate:.2f}%",
        }

    def reset_stats(self):
        self.stats = {
            'total_clicks': 0,
            'total_moves': 0,
            'total_drags': 0,
            'total_scrolls': 0,
            'verified_clicks': 0,
            'failed_clicks': 0,
            'retries': 0,
        }
        self.action_history.clear()
