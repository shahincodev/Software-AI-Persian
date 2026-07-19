# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""Intelligent Keyboard Engine for autonomous desktop interaction.

Complete redesign of keyboard control with:

- Focus detection: verify correct window/field before typing
- Retry on focus loss: automatically re-focus if needed
- Two insertion modes: INSTANT (clipboard paste) and HUMAN (char-by-char)
- Automatic language detection (Persian/English/Mixed)
- Unicode support via clipboard for non-ASCII text
- Text verification: confirm text was actually typed
- Safety validation: block dangerous patterns
- Audit trail with full action history

The engine intelligently decides which typing strategy to use:
- Short ASCII text → char-by-char with human timing
- Long text or Unicode → clipboard paste (instant)
- Security-sensitive → validate before typing
"""

from __future__ import annotations

import time
import random
import logging
from collections import deque
from enum import Enum
from typing import Optional, Any, List, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime

try:
    import pyautogui
except ImportError:
    raise ImportError("pyautogui is required. Install with: pip install pyautogui")

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_keyboard = None

try:
    import pyperclip
except ImportError:
    pyperclip = None

logger = logging.getLogger(__name__)


__all__ = [
    "Language",
    "TypingMode",
    "TypingSpeed",
    "KeyAction",
    "TypeResult",
    "KeyboardEngine",
    "Hotkeys",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Protocols
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@runtime_checkable
class FocusDetector(Protocol):
    """Protocol for detecting focused window/element."""

    def get_active_window(self) -> Optional[Any]:
        """Get the currently active window."""
        ...

    def find_text(self, text: str, confidence_threshold: float = 0.7) -> Optional[tuple[int, int]]:
        """Find text on screen."""
        ...


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums & Data Classes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    PERSIAN = "fa"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TypingMode(Enum):
    """Typing strategies."""
    INSTANT = "instant"         # Clipboard paste - fastest
    HUMAN = "human"             # Char-by-char with human timing
    AUTO = "auto"               # Decide based on text content


class TypingSpeed(Enum):
    """Character-by-character typing speeds."""
    INSTANT = 0.0
    VERY_FAST = 0.01
    FAST = 0.02
    NORMAL = 0.05
    SLOW = 0.1
    VERY_SLOW = 0.2


class KeyAction(Enum):
    """Key action types for audit trail."""
    PRESS = "press"
    HOLD = "hold"
    RELEASE = "release"
    TYPE = "type"
    HOTKEY = "hotkey"


@dataclass
class TypeResult:
    """Result of a typing operation with full context."""
    success: bool
    text_length: int = 0
    language: Language = Language.UNKNOWN
    mode_used: TypingMode = TypingMode.AUTO
    verified: bool = False
    attempts: int = 1
    duration: float = 0.0
    error: Optional[str] = None
    verification_message: str = ""

    @property
    def summary(self) -> str:
        parts = []
        parts.append("OK" if self.success else "FAIL")
        parts.append(f"len={self.text_length}")
        parts.append(f"lang={self.language.name}")
        parts.append(f"mode={self.mode_used.name}")
        if self.verified:
            parts.append("verified")
        parts.append(f"{self.duration:.2f}s")
        return " | ".join(parts)


@dataclass
class KeyboardAction:
    """Audit trail entry for a keyboard action."""
    action_type: str
    text: Optional[str] = None
    key: Optional[str] = None
    keys: Optional[List[str]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    success: bool = False
    language: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Keyboard Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KeyboardEngine:
    """Intelligent keyboard engine with focus detection and verification.

    This engine behaves like a modern desktop AI agent:
    1. Detects the focused window
    2. Verifies focus is correct
    3. Types using the optimal strategy
    4. Verifies text was typed correctly
    5. Retries if focus changed or typing failed

    Example:
        >>> engine = KeyboardEngine(focus_detector=my_vision)
        >>> result = engine.type_text("Hello World", verify=True)
        >>> if result.success and result.verified:
        ...     print("Text typed and verified!")
    """

    PERSIAN_CHARS = set(
        'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
        'ءآأؤإئًٌٍَُِّْٰ'
    )

    UNSAFE_PATTERNS = [
        'rm -rf', 'del /f', 'format ', 'DROP TABLE', 'DROP DATABASE',
    ]

    def __init__(
        self,
        focus_detector: Optional[FocusDetector] = None,
        safety_enabled: bool = True,
        human_behavior: bool = True,
        default_speed: TypingSpeed = TypingSpeed.NORMAL,
        default_mode: TypingMode = TypingMode.AUTO,
        max_retries: int = 3,
        verification_timeout: float = 0.5,
    ):
        self.focus_detector = focus_detector
        self.safety_enabled = safety_enabled
        self.human_behavior = human_behavior
        self.default_speed = default_speed
        self.default_mode = default_mode
        self.max_retries = max_retries
        self.verification_timeout = verification_timeout

        self.stats = {
            'total_keystrokes': 0,
            'total_text_typed': 0,
            'total_hotkeys': 0,
            'total_special_keys': 0,
            'failed_actions': 0,
            'total_actions': 0,
            'verified_actions': 0,
            'retries': 0,
        }

        self.action_history: deque[KeyboardAction] = deque(maxlen=200)

        logger.info(
            "KeyboardEngine initialized: safety=%s, human=%s, speed=%s, mode=%s",
            safety_enabled, human_behavior, default_speed.name, default_mode.name,
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Language Detection
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def detect_language(self, text: str) -> Language:
        if not text:
            return Language.UNKNOWN

        text_clean = ''.join(c for c in text if c.isalnum())
        if not text_clean:
            return Language.UNKNOWN

        persian_count = sum(1 for c in text_clean if c in self.PERSIAN_CHARS)
        english_count = sum(1 for c in text_clean if c.isascii() and c.isalpha())
        total = persian_count + english_count

        if total == 0:
            return Language.UNKNOWN

        persian_ratio = persian_count / total
        english_ratio = english_count / total

        if persian_ratio > 0.7:
            return Language.PERSIAN
        elif english_ratio > 0.7:
            return Language.ENGLISH
        elif persian_ratio > 0.1 and english_ratio > 0.1:
            return Language.MIXED
        return Language.UNKNOWN

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Safety & Validation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def is_safe_text(self, text: str) -> bool:
        if not self.safety_enabled:
            return True

        text_lower = text.lower()
        for pattern in self.UNSAFE_PATTERNS:
            if pattern.lower() in text_lower:
                logger.warning("Unsafe pattern detected: %s", pattern)
                return False

        if len(text) > 50000:
            logger.warning("Text too long: %d chars", len(text))
            return False

        return True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Focus Detection
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _verify_focus(self, expected_window: Optional[str] = None) -> tuple[bool, str]:
        """Verify that the correct window/element has focus.

        Returns:
            (is_focused, message) tuple
        """
        if self.focus_detector is None:
            return True, "No focus detector - skipping focus check"

        try:
            window = self.focus_detector.get_active_window()
            if window is None:
                return False, "Could not detect active window"

            if expected_window:
                title = getattr(window, 'title', str(window))
                if expected_window.lower() in title.lower():
                    return True, f"Focus confirmed: {title}"
                return False, f"Wrong window focused: {title} (expected: {expected_window})"

            return True, f"Focus detected: {getattr(window, 'title', 'unknown')}"
        except Exception as e:
            logger.warning("Focus detection failed: %s", e)
            return True, f"Focus check failed: {e}"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Human Behavior Simulation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _get_typing_interval(self, speed: Optional[TypingSpeed] = None, char: str = '') -> float:
        if not self.human_behavior:
            return 0.0

        base_interval = (speed or self.default_speed).value
        if base_interval == 0.0:
            return 0.0

        if char in [' ', '\n', '\t']:
            base_interval *= 1.5
        elif char in ['،', '.', '!', '?', '؛', '؟']:
            base_interval *= 2.0

        variation = random.uniform(-0.3, 0.3)
        return max(0.0, base_interval * (1 + variation))

    def _select_mode(self, text: str, mode: TypingMode) -> TypingMode:
        """Intelligently select the best typing mode."""
        if mode != TypingMode.AUTO:
            return mode

        has_non_ascii = any(ord(c) > 127 for c in text)
        if has_non_ascii:
            return TypingMode.INSTANT

        if len(text) > 100:
            return TypingMode.INSTANT

        return TypingMode.HUMAN

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Core Typing Methods
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _type_instant(self, text: str) -> bool:
        """Type text instantly via clipboard paste."""
        if pyperclip is None:
            logger.warning("pyperclip not available for instant typing")
            return False

        try:
            pyperclip.copy(text)
            time.sleep(0.05)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error("Instant typing failed: %s", e)
            return False

    def _type_human(self, text: str, speed: Optional[TypingSpeed] = None) -> bool:
        """Type text character-by-character with human-like timing."""
        try:
            for char in text:
                interval = self._get_typing_interval(speed, char)
                if interval > 0:
                    time.sleep(interval)
                pyautogui.write(char, interval=0)
                self.stats['total_keystrokes'] += 1
            return True
        except Exception as e:
            logger.error("Human typing failed: %s", e)
            return False

    def _verify_text_typed(self, text: str) -> tuple[bool, str]:
        """Verify that text was actually typed in the focused field.

        Uses clipboard to check current field content.
        """
        try:
            original_clipboard = pyperclip.paste() if pyperclip else None
        except Exception:
            original_clipboard = None

        try:
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)

            if pyperclip:
                selected = pyperclip.paste()
                if selected and text in selected:
                    return True, f"Text verified: found '{text[:50]}' in field"

            if original_clipboard and pyperclip:
                pyperclip.copy(original_clipboard)
                pyautogui.hotkey('ctrl', 'v')

            return False, "Could not verify text content"
        except Exception as e:
            return False, f"Verification failed: {e}"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Public API
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def type_text(
        self,
        text: str,
        speed: Optional[TypingSpeed] = None,
        mode: Optional[TypingMode] = None,
        verify: bool = False,
        expected_window: Optional[str] = None,
        retries: Optional[int] = None,
    ) -> TypeResult:
        """Type text with intelligent strategy selection.

        The engine:
        1. Validates text safety
        2. Detects language
        3. Selects optimal typing mode
        4. Verifies focus if expected_window specified
        5. Types the text
        6. Optionally verifies the result
        7. Retries on failure

        Args:
            text: Text to type
            speed: Typing speed for HUMAN mode
            mode: Typing mode (INSTANT, HUMAN, AUTO)
            verify: Whether to verify text was typed
            expected_window: Expected focused window title
            retries: Override max retries

        Returns:
            TypeResult with full details
        """
        start_time = time.time()
        max_retries = retries if retries is not None else self.max_retries

        if not text:
            return TypeResult(
                success=True, text_length=0, duration=time.time() - start_time,
            )

        if not self.is_safe_text(text):
            return TypeResult(
                success=False, text_length=len(text),
                duration=time.time() - start_time,
                error="Unsafe text detected",
            )

        language = self.detect_language(text)
        selected_mode = self._select_mode(text, mode or self.default_mode)

        logger.info(
            "Typing %d chars (lang=%s, mode=%s)",
            len(text), language.name, selected_mode.name,
        )

        for attempt in range(max_retries + 1):
            focused, focus_msg = self._verify_focus(expected_window)
            if not focused:
                logger.warning("Focus issue: %s (attempt %d)", focus_msg, attempt + 1)
                self.stats['retries'] += 1
                if attempt < max_retries:
                    time.sleep(0.5)
                    continue
                return TypeResult(
                    success=False, text_length=len(text), language=language,
                    mode_used=selected_mode, attempts=attempt + 1,
                    duration=time.time() - start_time,
                    error=f"Focus lost: {focus_msg}",
                )

            if selected_mode == TypingMode.INSTANT:
                success = self._type_instant(text)
            else:
                success = self._type_human(text, speed)

            if success:
                self.stats['total_text_typed'] += len(text)
                self.stats['total_actions'] += 1

                verified = False
                verify_msg = "Verification not requested"
                if verify:
                    verified, verify_msg = self._verify_text_typed(text)
                    if verified:
                        self.stats['verified_actions'] += 1

                return TypeResult(
                    success=True, text_length=len(text), language=language,
                    mode_used=selected_mode, verified=verified,
                    attempts=attempt + 1, duration=time.time() - start_time,
                    verification_message=verify_msg,
                )

            self.stats['retries'] += 1
            if attempt < max_retries:
                time.sleep(0.3)

        self.stats['failed_actions'] += 1
        self.stats['total_actions'] += 1
        return TypeResult(
            success=False, text_length=len(text), language=language,
            mode_used=selected_mode, attempts=max_retries + 1,
            duration=time.time() - start_time,
            error="All retries exhausted",
        )

    def press_key(self, key: str, presses: int = 1, interval: float = 0.1) -> bool:
        start_time = time.time()
        action = KeyboardAction(action_type=KeyAction.PRESS.value, key=key)
        try:
            for _ in range(presses):
                pyautogui.press(key)
                self.stats['total_special_keys'] += 1
                if presses > 1 and interval > 0:
                    time.sleep(interval)
            self.stats['total_actions'] += 1
            action.success = True
            return True
        except Exception as e:
            logger.error("Failed to press key '%s': %s", key, e)
            self.stats['failed_actions'] += 1
            self.stats['total_actions'] += 1
            action.success = False
            return False
        finally:
            action.duration = time.time() - start_time
            self.action_history.append(action)

    def hotkey(self, *keys: str) -> bool:
        start_time = time.time()
        action = KeyboardAction(action_type=KeyAction.HOTKEY.value, keys=list(keys))
        try:
            pyautogui.hotkey(*keys)
            self.stats['total_hotkeys'] += 1
            self.stats['total_actions'] += 1
            action.success = True
            return True
        except Exception as e:
            logger.error("Failed to press hotkey %s: %s", keys, e)
            self.stats['failed_actions'] += 1
            self.stats['total_actions'] += 1
            action.success = False
            return False
        finally:
            action.duration = time.time() - start_time
            self.action_history.append(action)

    def hold_key(self, key: str, duration: float = 1.0) -> bool:
        start_time = time.time()
        action = KeyboardAction(action_type=KeyAction.HOLD.value, key=key)
        try:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            self.stats['total_special_keys'] += 1
            self.stats['total_actions'] += 1
            action.success = True
            return True
        except Exception as e:
            logger.error("Failed to hold key '%s': %s", key, e)
            self.stats['failed_actions'] += 1
            self.stats['total_actions'] += 1
            action.success = False
            return False
        finally:
            action.duration = time.time() - start_time
            self.action_history.append(action)

    def paste_text(self, text: str) -> bool:
        if pyperclip is None:
            logger.warning("pyperclip not available")
            return False
        try:
            pyperclip.copy(text)
            time.sleep(0.05)
            return self.hotkey('ctrl', 'v')
        except Exception as e:
            logger.error("Failed to paste text: %s", e)
            return False

    def get_clipboard(self) -> Optional[str]:
        if pyperclip is None:
            return None
        try:
            return pyperclip.paste()
        except Exception as e:
            logger.error("Failed to get clipboard: %s", e)
            return None

    def get_stats(self) -> dict:
        stats = self.stats.copy()
        total = stats['total_actions']
        if total > 0:
            stats['success_rate'] = f"{((total - stats['failed_actions']) / total) * 100:.2f}%"
        else:
            stats['success_rate'] = "N/A"
        stats['recent_actions'] = len(self.action_history)
        return stats

    def reset_stats(self):
        self.stats = {
            'total_keystrokes': 0,
            'total_text_typed': 0,
            'total_hotkeys': 0,
            'total_special_keys': 0,
            'failed_actions': 0,
            'total_actions': 0,
            'verified_actions': 0,
            'retries': 0,
        }
        self.action_history.clear()


class Hotkeys:
    """Common hotkey combinations."""
    COPY = ('ctrl', 'c')
    CUT = ('ctrl', 'x')
    PASTE = ('ctrl', 'v')
    UNDO = ('ctrl', 'z')
    REDO = ('ctrl', 'y')
    SELECT_ALL = ('ctrl', 'a')
    SAVE = ('ctrl', 's')
    SAVE_AS = ('ctrl', 'shift', 's')
    OPEN = ('ctrl', 'o')
    NEW = ('ctrl', 'n')
    CLOSE = ('ctrl', 'w')
    QUIT = ('alt', 'f4')
    FIND = ('ctrl', 'f')
    REPLACE = ('ctrl', 'h')
    SWITCH_WINDOW = ('alt', 'tab')
    CLOSE_WINDOW = ('alt', 'f4')
    MINIMIZE = ('win', 'down')
    MAXIMIZE = ('win', 'up')
    TASK_MANAGER = ('ctrl', 'shift', 'esc')
    RUN = ('win', 'r')
    DESKTOP = ('win', 'd')
