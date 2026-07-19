# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""Windows UI Automation provider for semantic desktop understanding.

This module integrates with Windows UI Automation (UIA) to provide
the agent with semantic understanding of the desktop, beyond what
OCR coordinates can offer.

Key capabilities:
- Access to the Windows accessibility tree
- Semantic element identification (buttons, text fields, menus)
- Element state detection (enabled, focused, visible)
- Reliable element location without coordinates
- Fallback to OCR when UIA is unavailable

The accessibility tree is the PRIMARY source for element location.
Coordinates from OCR are a FALLBACK.

Example:
    >>> provider = UIAProvider()
    >>> elements = provider.find_elements(name="Submit")
    >>> if elements:
    ...     elem = elements[0]
    ...     elem.click()  # Uses UIA's built-in click
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Any

logger = logging.getLogger(__name__)

__all__ = [
    "UIAElement",
    "UIATreeSnapshot",
    "UIAProvider",
]

UIA_AVAILABLE = False
try:
    import comtypes
    import comtypes.client
    from ctypes import windll  # noqa: F401
    UIA_AVAILABLE = True
except ImportError:
    logger.warning("comtypes not available. UIA integration disabled.")

if UIA_AVAILABLE:
    try:
        UIAutomationCore = comtypes.client.GetModule('UIAutomationCore.dll')
        CUIAutomation = comtypes.CoCreateInstance(
            '{FF48DBA4-60EF-4201-AA87-54103EEF594E}',
            None,
            comtypes.CLSCTX_INPROC_SERVER,
            UIAutomationCore.IUIAutomation,
        )
    except Exception as e:
        logger.warning("Failed to initialize UIA: %s", e)
        UIA_AVAILABLE = False


@dataclass
class UIAElement:
    """A UI element from the Windows accessibility tree."""
    name: str = ""
    control_type: str = ""
    automation_id: str = ""
    class_name: str = ""
    is_enabled: bool = True
    is_visible: bool = True
    is_focusable: bool = False
    has_keyboard_focus: bool = False
    bounding_rect: Optional[tuple[int, int, int, int]] = None
    children_count: int = 0
    depth: int = 0
    raw_element: Any = None

    @property
    def center(self) -> Optional[tuple[int, int]]:
        if self.bounding_rect:
            x, y, w, h = self.bounding_rect
            return (x + w // 2, y + h // 2)
        return None

    @property
    def is_clickable(self) -> bool:
        return self.control_type.lower() in {
            'button', 'menuitem', 'tabitem', ' hyperlink',
            'image', 'radiobutton', 'checkbox', 'togglebutton',
            'splitbutton', 'menubutton', 'toolbarbutton',
        }

    @property
    def is_input(self) -> bool:
        return self.control_type.lower() in {
            'edit', 'combobox', 'spinbutton', 'password',
        }

    def click(self) -> bool:
        if self.raw_element and UIA_AVAILABLE:
            try:
                self.raw_element.Click()
                return True
            except Exception as e:
                logger.error("UIA click failed: %s", e)
        return False

    def set_focus(self) -> bool:
        if self.raw_element and UIA_AVAILABLE:
            try:
                self.raw_element.SetFocus()
                return True
            except Exception as e:
                logger.error("UIA focus failed: %s", e)
        return False

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'control_type': self.control_type,
            'automation_id': self.automation_id,
            'class_name': self.class_name,
            'enabled': self.is_enabled,
            'visible': self.is_visible,
            'center': self.center,
            'clickable': self.is_clickable,
            'input': self.is_input,
        }


@dataclass
class UIATreeSnapshot:
    """A snapshot of the UI Automation tree at a point in time."""
    timestamp: float = field(default_factory=time.time)
    root_elements: list[UIAElement] = field(default_factory=list)
    all_elements: list[UIAElement] = field(default_factory=list)
    focused_element: Optional[UIAElement] = None
    active_window_title: str = ""

    @property
    def element_count(self) -> int:
        return len(self.all_elements)

    def find_elements(
        self,
        name: Optional[str] = None,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
        class_name: Optional[str] = None,
        clickable_only: bool = False,
        enabled_only: bool = True,
    ) -> list[UIAElement]:
        """Find elements matching the given criteria."""
        results = []
        for elem in self.all_elements:
            if name and name.lower() not in elem.name.lower():
                continue
            if control_type and elem.control_type.lower() != control_type.lower():
                continue
            if automation_id and elem.automation_id != automation_id:
                continue
            if class_name and class_name.lower() not in elem.class_name.lower():
                continue
            if clickable_only and not elem.is_clickable:
                continue
            if enabled_only and not elem.is_enabled:
                continue
            results.append(elem)
        return results

    def get_interactive_elements(self) -> list[UIAElement]:
        """Get all interactive elements (buttons, inputs, links)."""
        return [
            e for e in self.all_elements
            if e.is_clickable or e.is_input or e.is_focusable
        ]


class UIAProvider:
    """Windows UI Automation provider for semantic desktop understanding.

    This provider gives the agent access to the Windows accessibility tree,
    which is far more reliable than OCR for finding UI elements.

    The provider falls back gracefully when UIA is not available.
    """

    def __init__(self):
        self.available = UIA_AVAILABLE
        self._last_snapshot: Optional[UIATreeSnapshot] = None

        if self.available:
            logger.info("UIAProvider initialized (UIA available)")
        else:
            logger.warning("UIAProvider initialized (UIA NOT available - using OCR fallback)")

    def capture_tree(self, max_depth: int = 5) -> Optional[UIATreeSnapshot]:
        """Capture a snapshot of the current UI Automation tree.

        Args:
            max_depth: Maximum depth to traverse in the tree

        Returns:
            UIATreeSnapshot or None if UIA is not available
        """
        if not self.available:
            return None

        try:
            root = CUIAutomation.GetRootElement()
            snapshot = UIATreeSnapshot()

            focused = CUIAutomation.GetFocusedElement()
            if focused:
                snapshot.focused_element = self._element_from_com(focused, 0)

            self._traverse_tree(root, snapshot, depth=0, max_depth=max_depth)

            self._last_snapshot = snapshot
            logger.info("UIA tree captured: %d elements", snapshot.element_count)
            return snapshot

        except Exception as e:
            logger.error("Failed to capture UIA tree: %s", e)
            return None

    def _traverse_tree(self, com_element, snapshot: UIATreeSnapshot, depth: int, max_depth: int):
        if depth > max_depth:
            return

        try:
            children = com_element.FindAll(
                UIAutomationCore.TreeScope_Children,
                CUIAutomation.CreateTrueCondition(),
            )

            if children:
                for i in range(children.Length):
                    child = children.GetElement(i)
                    elem = self._element_from_com(child, depth)
                    snapshot.all_elements.append(elem)

                    if depth == 0:
                        snapshot.root_elements.append(elem)

                    self._traverse_tree(child, snapshot, depth + 1, max_depth)

        except Exception:
            pass

    def _element_from_com(self, com_element, depth: int) -> UIAElement:
        elem = UIAElement(depth=depth, raw_element=com_element)

        try:
            elem.name = com_element.CurrentName or ""
        except Exception:
            pass

        try:
            elem.control_type = com_element.CurrentLocalizedControlType or ""
        except Exception:
            pass

        try:
            elem.automation_id = com_element.CurrentAutomationId or ""
        except Exception:
            pass

        try:
            elem.class_name = com_element.CurrentClassName or ""
        except Exception:
            pass

        try:
            elem.is_enabled = bool(com_element.CurrentIsEnabled)
        except Exception:
            pass

        try:
            elem.is_visible = bool(com_element.CurrentIsOffscreen) is False
        except Exception:
            pass

        try:
            rect = com_element.CurrentBoundingRectangle
            if rect:
                elem.bounding_rect = (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
        except Exception:
            pass

        return elem

    def find_elements(self, name: str, **kwargs) -> list[UIAElement]:
        """Find elements by name. Uses cached tree or captures fresh."""
        snapshot = self._last_snapshot
        if snapshot is None:
            snapshot = self.capture_tree()

        if snapshot is None:
            return []

        return snapshot.find_elements(name=name, **kwargs)

    def find_clickable(self, name: str) -> list[UIAElement]:
        """Find clickable elements matching a name."""
        return self.find_elements(name=name, clickable_only=True)

    def find_input(self, name: str) -> list[UIAElement]:
        """Find input fields matching a name."""
        return self.find_elements(name=name, control_type="Edit")

    def get_focused_element(self) -> Optional[UIAElement]:
        """Get the currently focused element."""
        if not self.available:
            return None

        try:
            focused = CUIAutomation.GetFocusedElement()
            if focused:
                return self._element_from_com(focused, 0)
        except Exception as e:
            logger.warning("Failed to get focused element: %s", e)

        return None

    def get_active_window_title(self) -> str:
        """Get the title of the active window."""
        try:
            import pygetwindow as gw
            active = gw.getActiveWindow()
            if active:
                return active.title
        except Exception:
            pass
        return ""

    def to_context_string(self) -> str:
        """Get the current UI tree as context for AI prompts."""
        snapshot = self._last_snapshot or self.capture_tree()
        if snapshot is None:
            return "UIA not available"

        parts = []
        if snapshot.active_window_title:
            parts.append(f"Active window: {snapshot.active_window_title}")
        if snapshot.focused_element:
            parts.append(f"Focused: {snapshot.focused_element.control_type} '{snapshot.focused_element.name}'")

        interactive = snapshot.get_interactive_elements()[:15]
        if interactive:
            parts.append(f"Interactive elements ({len(interactive)}):")
            for elem in interactive:
                center = elem.center
                pos = f"at ({center[0]},{center[1]})" if center else ""
                parts.append(f"  - [{elem.control_type}] '{elem.name}' {pos}")

        return "\n".join(parts) if parts else "No UI elements found"
