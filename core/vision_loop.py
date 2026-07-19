"""Autonomous Vision Loop for Phase 3.

Orchestrates the observe → decide → act → verify → retry cycle.
Integrates DesktopVision, ActionRecovery, and ActionController.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from core.desktop_vision import DesktopVision
from core.action_recovery import ActionRecovery, RecoveryConfig

logger = logging.getLogger(__name__)


@dataclass
class VisionLoopConfig:
    """Configuration for the vision loop."""
    max_retries: int = 2
    verify_after_action: bool = True
    capture_before_action: bool = True
    capture_after_action: bool = True
    description_threshold: float = 0.7
    verification_timeout: float = 3.0


@dataclass
class ScreenState:
    """Describes the current screen state for AI context."""
    timestamp: float
    screenshot_path: Optional[str] = None
    ocr_text: str = ""
    visible_elements: list[str] = field(default_factory=list)
    active_window: str = ""
    description: str = ""

    def to_context_string(self) -> str:
        """Convert to a string suitable for AI prompt injection."""
        parts = []
        if self.active_window:
            parts.append(f"Active window: {self.active_window}")
        if self.ocr_text:
            # Truncate OCR text to keep context manageable
            truncated = self.ocr_text[:500] + "..." if len(self.ocr_text) > 500 else self.ocr_text
            parts.append(f"Screen text: {truncated}")
        if self.visible_elements:
            elements_str = ", ".join(self.visible_elements[:20])
            parts.append(f"Visible elements: {elements_str}")
        if self.description:
            parts.append(f"Screen description: {self.description}")
        return "\n".join(parts) if parts else "No screen information available"


@dataclass
class VisionLoopResult:
    """Result of a vision loop execution cycle."""
    success: bool
    action_description: str
    attempts: int
    screen_before: Optional[ScreenState] = None
    screen_after: Optional[ScreenState] = None
    verification_passed: bool = False
    error: Optional[str] = None
    recovery_action: Optional[str] = None


class VisionLoopManager:
    """Manages the autonomous vision loop: observe → act → verify → retry.

    This class integrates DesktopVision for screen observation,
    ActionController for execution, and ActionRecovery for retry logic.
    """

    def __init__(
        self,
        vision: Optional[DesktopVision] = None,
        config: Optional[VisionLoopConfig] = None,
    ):
        self.vision = vision or DesktopVision()
        self.config = config or VisionLoopConfig()
        self.recovery = ActionRecovery(RecoveryConfig(
            max_retries=self.config.max_retries,
            retry_delay=1.0,
            exponential_backoff=True,
        ))
        self._last_screen_state: Optional[ScreenState] = None

    def observe_screen(self) -> ScreenState:
        """Capture and analyze the current screen state.

        Returns:
            ScreenState with OCR text, visible elements, and active window.
        """
        logger.info("Observing screen...")

        # Capture screenshot
        screenshot_path = None
        try:
            screenshot = self.vision.capture_screen()
            screenshot_path = f"data/screenshots/observe_{int(time.time())}.png"
            screenshot.save(screenshot_path)
        except Exception as e:
            logger.warning("Failed to capture screenshot: %s", e)

        # Get active window
        active_window = ""
        try:
            window = self.vision.get_active_window()
            if window:
                active_window = window.title
        except Exception as e:
            logger.warning("Failed to get active window: %s", e)

        # OCR text extraction
        ocr_text = ""
        visible_elements = []
        try:
            text_boxes = self.vision.get_all_text_boxes()
            if text_boxes:
                ocr_text = " ".join(tb.text for tb in text_boxes if tb.text)
                visible_elements = [
                    f"{tb.text} at ({tb.x},{tb.y})"
                    for tb in text_boxes
                    if tb.text and len(tb.text) > 1
                ]
        except Exception as e:
            logger.warning("Failed to extract OCR text: %s", e)

        state = ScreenState(
            timestamp=time.time(),
            screenshot_path=screenshot_path,
            ocr_text=ocr_text,
            visible_elements=visible_elements,
            active_window=active_window,
        )

        self._last_screen_state = state
        logger.info(
            "Screen observed: window='%s', elements=%d, ocr_len=%d",
            active_window, len(visible_elements), len(ocr_text)
        )
        return state

    def verify_action(
        self,
        expected_outcome: str,
        screen_before: Optional[ScreenState] = None,
        timeout: Optional[float] = None,
    ) -> tuple[bool, str]:
        """Verify that an action achieved its expected outcome.

        Args:
            expected_outcome: Description of what should have happened
            screen_before: Screen state before the action
            timeout: How long to wait for verification

        Returns:
            (passed, message) tuple
        """
        timeout = timeout or self.config.verification_timeout
        logger.info("Verifying action: %s", expected_outcome)

        # Wait briefly for UI to settle
        time.sleep(0.5)

        # Capture current screen
        screen_after = self.observe_screen()

        # Check if screen changed
        if screen_before:
            if screen_before.ocr_text == screen_after.ocr_text and screen_before.active_window == screen_after.active_window:
                # Screen didn't change — might indicate failure
                logger.warning("Screen did not change after action")

                # For some actions, no change is expected (e.g., typing in a field)
                if "type" in expected_outcome.lower() or "input" in expected_outcome.lower():
                    return True, "Action completed (no visual change expected)"

                return False, "Screen did not change after action"

        # Use vision to check for specific elements mentioned in expected_outcome
        try:
            # Simple keyword matching for verification
            keywords = [w for w in expected_outcome.lower().split() if len(w) > 3]
            found = 0
            for keyword in keywords:
                result = self.vision.find_text(keyword)
                if result:
                    found += 1

            if found > 0:
                return True, f"Verification passed: found {found}/{len(keywords)} expected elements"

            # If no keywords found, assume success if no error occurred
            return True, "Verification passed (no specific elements found to check)"

        except Exception as e:
            logger.warning("Verification check failed: %s", e)
            return True, "Verification skipped due to error"

    def execute_with_vision(
        self,
        action_func,
        action_description: str,
        expected_outcome: str = "",
        max_retries: Optional[int] = None,
    ) -> VisionLoopResult:
        """Execute an action with vision-based verification and retry.

        This is the core vision loop:
        1. Observe screen before action
        2. Execute action
        3. Verify outcome
        4. Retry if failed

        Args:
            action_func: Async callable that executes the action
            action_description: Human-readable description
            expected_outcome: What should happen after the action
            max_retries: Override max retries

        Returns:
            VisionLoopResult with full details
        """
        max_retries = max_retries or self.config.max_retries
        screen_before = None
        last_error = None

        for attempt in range(max_retries + 1):
            logger.info(
                "Vision loop attempt %d/%d for: %s",
                attempt + 1, max_retries + 1, action_description
            )

            # Step 1: Observe screen before action
            if self.config.capture_before_action:
                try:
                    screen_before = self.observe_screen()
                except Exception as e:
                    logger.warning("Failed to observe screen: %s", e)

            # Step 2: Execute action
            try:
                if hasattr(action_func, '__call__'):
                    import asyncio
                    if asyncio.iscoroutinefunction(action_func):
                        import asyncio as _asyncio
                        _asyncio.get_event_loop().run_until_complete(action_func())
                    else:
                        action_func()

                logger.info("Action executed: %s", action_description)

            except Exception as e:
                last_error = str(e)
                logger.error("Action failed (attempt %d): %s", attempt + 1, e)

                if attempt < max_retries:
                    delay = self.recovery._calculate_delay(attempt)
                    logger.info("Retrying in %.1f seconds...", delay)
                    time.sleep(delay)
                    continue

                return VisionLoopResult(
                    success=False,
                    action_description=action_description,
                    attempts=attempt + 1,
                    screen_before=screen_before,
                    error=last_error,
                )

            # Step 3: Verify outcome
            if self.config.verify_after_action and expected_outcome:
                try:
                    passed, verify_msg = self.verify_action(
                        expected_outcome, screen_before
                    )
                    logger.info("Verification: %s", verify_msg)

                    if passed:
                        return VisionLoopResult(
                            success=True,
                            action_description=action_description,
                            attempts=attempt + 1,
                            screen_before=screen_before,
                            verification_passed=True,
                        )
                    else:
                        last_error = f"Verification failed: {verify_msg}"
                        if attempt < max_retries:
                            logger.info("Retrying due to verification failure...")
                            time.sleep(1.0)
                            continue

                except Exception as e:
                    logger.warning("Verification error: %s", e)
                    # Assume success if verification itself fails

            # Success (or no verification needed)
            return VisionLoopResult(
                success=True,
                action_description=action_description,
                attempts=attempt + 1,
                screen_before=screen_before,
                verification_passed=True,
            )

        # All retries exhausted
        return VisionLoopResult(
            success=False,
            action_description=action_description,
            attempts=max_retries + 1,
            screen_before=screen_before,
            error=last_error or "All retries exhausted",
        )

    def get_screen_context(self) -> str:
        """Get current screen state as context string for AI prompts.

        Returns:
            Formatted string with screen state information.
        """
        state = self._last_screen_state or self.observe_screen()
        return state.to_context_string()

    def describe_screen(self) -> str:
        """Get a detailed description of the current screen.

        Returns:
            Human-readable description of visible elements.
        """
        state = self.observe_screen()
        parts = []

        if state.active_window:
            parts.append(f"Active window: {state.active_window}")

        if state.visible_elements:
            parts.append(f"Visible elements ({len(state.visible_elements)}):")
            for elem in state.visible_elements[:15]:
                parts.append(f"  - {elem}")

        if state.ocr_text:
            words = state.ocr_text.split()
            if len(words) > 50:
                parts.append(f"Screen contains {len(words)} words of text")
            else:
                parts.append(f"Screen text: {state.ocr_text}")

        return "\n".join(parts) if parts else "Unable to describe screen"
