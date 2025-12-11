# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""کنترلر اکشن‌های سطح بالا برای اتوماسیون Desktop ویندوز.

این ماژول لایه‌ای از انتزاع بالا روی Mouse، Keyboard، Vision و Smart Wait
فراهم می‌کند تا بتوان اکشن‌های پیچیده را به صورت ساده اجرا کرد.

این همان چیزی است که browser-use برای وب است، اما برای Desktop ویندوز:
- کلیک روی متن یا تصویر
- پر کردن فرم‌ها
- پیمایش منوها
- اجرای Workflow‌های پیچیده

مثال:
    >>> from core.action_controller import ActionController
    >>> controller = ActionController()
    >>> 
    >>> # کلیک روی دکمه OK
    >>> controller.click_on_text("OK")
    >>> 
    >>> # پر کردن فرم
    >>> controller.fill_form({
    ...     "username": "admin",
    ...     "password": "pass123"
    ... })
    >>> 
    >>> # باز کردن منو File > New > Project
    >>> controller.select_menu_item(["File", "New", "Project"])
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union

# Import core components
from core.mouse_control import MouseController, MouseButton
from core.keyboard_control import KeyboardController
from core.desktop_vision import DesktopVision, ImageMatch
from core.smart_wait import SmartWaiter
from core.system_actions import SystemAction, RiskLevel, ActionStatus
from core.desktop_actions import (
    ClickAction, TypeAction, WaitAction,
    DragDropAction, HotkeyAction, ScrollAction
)

logger = logging.getLogger(__name__)


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


class ActionController:
    """کنترلر اصلی برای اکشن‌های سطح بالا.
    
    این کلاس Mouse، Keyboard، Vision و SmartWait را ترکیب می‌کند
    تا اکشن‌های پیچیده‌ای مثل "کلیک روی دکمه OK" یا "پر کردن فرم"
    را به صورت خودکار انجام دهد.
    """

    def __init__(
        self,
        mouse: Optional[MouseController] = None,
        keyboard: Optional[KeyboardController] = None,
        vision: Optional[DesktopVision] = None,
        waiter: Optional[SmartWaiter] = None,
        enable_state_tracking: bool = True,
        screenshot_dir: Optional[Path] = None
    ):
        """مقداردهی اولیه ActionController.
        
        Args:
            mouse: کنترلر موس (اگر None باشد، یکی جدید می‌سازد)
            keyboard: کنترلر کیبورد (اگر None باشد، یکی جدید می‌سازد)
            vision: سیستم بینایی (اگر None باشد، یکی جدید می‌سازد)
            waiter: سیستم انتظار هوشمند (اگر None باشد، یکی جدید می‌سازد)
            enable_state_tracking: فعال‌سازی ذخیره‌سازی وضعیت
            screenshot_dir: مسیر ذخیره اسکرین‌شات‌ها
        """
        self.mouse = mouse or MouseController()
        self.keyboard = keyboard or KeyboardController()
        self.vision = vision or DesktopVision()
        self.waiter = waiter or SmartWaiter(vision_system=self.vision)
        
        self.enable_state_tracking = enable_state_tracking
        self.screenshot_dir = screenshot_dir or Path("data/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # State management
        self._states: List[ActionState] = []
        self._checkpoints: Dict[str, ActionState] = {}
        
        # Statistics
        self._stats = {
            "actions_executed": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_duration": 0.0
        }
        
        logger.info("ActionController initialized")

    # ==================== HIGH-LEVEL ACTIONS ====================

    def click_on_text(
        self,
        text: str,
        button: str = "left",
        clicks: int = 1,
        verify: bool = True,
        timeout: float = 10.0,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> ActionOutcome:
        """پیدا کردن متن روی صفحه و کلیک روی آن.
        
        این متد معادل Desktop برای کلیک روی لینک یا دکمه در browser-use است.
        
        Args:
            text: متنی که باید پیدا شود (مثلا "OK", "Submit", "بستن")
            button: دکمه موس (left, right, middle)
            clicks: تعداد کلیک (1 = single, 2 = double)
            verify: آیا بعد از کلیک تایید شود؟
            timeout: حداکثر زمان انتظار (ثانیه)
            confidence: حداقل اطمینان OCR (0.0 تا 1.0)
            region: ناحیه جستجو (x, y, width, height)
        
        Returns:
            ActionOutcome با جزئیات کامل نتیجه
            
        Example:
            >>> controller.click_on_text("OK")
            >>> controller.click_on_text("بستن", verify=True)
            >>> controller.click_on_text("Submit", button="left", clicks=2)
        """
        start_time = time.time()
        logger.info(f"Attempting to click on text: '{text}'")
        
        try:
            # گرفتن اسکرین‌شات قبل از اکشن
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot("before")
            
            # انتظار برای ظاهر شدن متن
            wait_result = self.waiter.wait_for_element(
                text,
                timeout=timeout,
                confidence=confidence
            )
            
            if not wait_result.success or not wait_result.result:
                duration = time.time() - start_time
                self._update_stats(False, duration)
                return ActionOutcome(
                    result=ActionResult.NOT_FOUND,
                    message=f"Text '{text}' not found on screen",
                    duration=duration,
                    screenshot_before=screenshot_before
                )
            
            # کلیک روی موقعیت پیدا شده
            x, y = wait_result.result
            self.mouse.click(x, y, button=button, clicks=clicks)
            
            # انتظار برای اجرای عملیات
            time.sleep(0.5)
            
            # تایید اگر درخواست شده
            screenshot_after = None
            if verify:
                screenshot_after = self._save_screenshot("after")
                verified = self.vision.verify_click_success(region=(x-50, y-50, 100, 100))
                
                if not verified:
                    duration = time.time() - start_time
                    self._update_stats(False, duration)
                    return ActionOutcome(
                        result=ActionResult.VERIFICATION_FAILED,
                        message=f"Click on '{text}' was not verified",
                        duration=duration,
                        position=(x, y),
                        screenshot_before=screenshot_before,
                        screenshot_after=screenshot_after
                    )
            
            duration = time.time() - start_time
            self._update_stats(True, duration)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Successfully clicked on '{text}'",
                duration=duration,
                position=(x, y),
                screenshot_before=screenshot_before,
                screenshot_after=screenshot_after
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(False, duration)
            logger.error(f"Error clicking on text '{text}': {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message=f"Failed to click on '{text}'",
                duration=duration,
                error=str(e)
            )

    def click_on_image(
        self,
        image_path: Union[str, Path],
        button: str = "left",
        clicks: int = 1,
        verify: bool = True,
        timeout: float = 10.0,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> ActionOutcome:
        """پیدا کردن تصویر روی صفحه و کلیک روی آن.
        
        برای کلیک روی آیکون‌ها، دکمه‌های خاص یا عناصری که متن ندارند.
        
        Args:
            image_path: مسیر فایل تصویر (template)
            button: دکمه موس (left, right, middle)
            clicks: تعداد کلیک
            verify: آیا بعد از کلیک تایید شود؟
            timeout: حداکثر زمان انتظار (ثانیه)
            confidence: حداقل اطمینان تطبیق (0.0 تا 1.0)
            region: ناحیه جستجو
        
        Returns:
            ActionOutcome با جزئیات نتیجه
            
        Example:
            >>> controller.click_on_image("icons/close_button.png")
            >>> controller.click_on_image("assets/play_icon.png", verify=True)
        """
        start_time = time.time()
        logger.info(f"Attempting to click on image: '{image_path}'")
        
        try:
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot("before")
            
            # انتظار برای ظاهر شدن تصویر
            match = self.vision.wait_for_image(
                str(image_path),
                timeout=timeout,
                confidence=confidence
            )
            
            if not match:
                duration = time.time() - start_time
                self._update_stats(False, duration)
                return ActionOutcome(
                    result=ActionResult.NOT_FOUND,
                    message=f"Image '{image_path}' not found on screen",
                    duration=duration,
                    screenshot_before=screenshot_before
                )
            
            # کلیک روی مرکز تصویر
            x, y = match.center
            self.mouse.click(x, y, button=button, clicks=clicks)
            
            time.sleep(0.5)
            
            # تایید
            screenshot_after = None
            if verify:
                screenshot_after = self._save_screenshot("after")
                verified = self.vision.verify_click_success(
                    region=(match.x - 50, match.y - 50, 100, 100)
                )
                
                if not verified:
                    duration = time.time() - start_time
                    self._update_stats(False, duration)
                    return ActionOutcome(
                        result=ActionResult.VERIFICATION_FAILED,
                        message=f"Click on image '{image_path}' was not verified",
                        duration=duration,
                        position=(x, y),
                        screenshot_before=screenshot_before,
                        screenshot_after=screenshot_after
                    )
            
            duration = time.time() - start_time
            self._update_stats(True, duration)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Successfully clicked on image '{image_path}'",
                duration=duration,
                position=(x, y),
                screenshot_before=screenshot_before,
                screenshot_after=screenshot_after
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(False, duration)
            logger.error(f"Error clicking on image '{image_path}': {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message=f"Failed to click on image",
                duration=duration,
                error=str(e)
            )

    def type_in_field(
        self,
        field_text: str,
        content: str,
        verify: bool = True,
        clear_first: bool = True,
        timeout: float = 10.0,
        fuzzy_match: bool = False
    ) -> ActionOutcome:
        """پیدا کردن فیلد ورودی و تایپ متن در آن.
        
        Args:
            field_text: متن label فیلد یا placeholder
            content: محتوایی که باید تایپ شود
            verify: آیا محتوای تایپ شده تایید شود؟
            clear_first: آیا قبل از تایپ فیلد خالی شود؟
            timeout: حداکثر زمان انتظار
            fuzzy_match: استفاده از تطبیق فازی برای تایید
        
        Returns:
            ActionOutcome با جزئیات نتیجه
            
        Example:
            >>> controller.type_in_field("Username", "admin")
            >>> controller.type_in_field("نام کاربری", "احمد", verify=True)
        """
        start_time = time.time()
        logger.info(f"Attempting to type in field: '{field_text}'")
        
        try:
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot("before")
            
            # پیدا کردن فیلد
            field_position = self.vision.find_input_field(field_text)
            
            if not field_position:
                duration = time.time() - start_time
                self._update_stats(False, duration)
                return ActionOutcome(
                    result=ActionResult.NOT_FOUND,
                    message=f"Input field '{field_text}' not found",
                    duration=duration,
                    screenshot_before=screenshot_before
                )
            
            # کلیک روی فیلد
            x, y = field_position
            self.mouse.click(x, y)
            time.sleep(0.3)
            
            # پاک کردن محتوای قبلی
            if clear_first:
                self.keyboard.hotkey('ctrl', 'a')
                time.sleep(0.1)
                self.keyboard.press('backspace')
                time.sleep(0.2)
            
            # تایپ محتوا
            self.keyboard.type_text(content)
            time.sleep(0.5)
            
            # تایید
            screenshot_after = None
            if verify:
                screenshot_after = self._save_screenshot("after")
                verified = self.vision.verify_text_typed(
                    content,
                    region=(x - 100, y - 20, 200, 40),
                    fuzzy=fuzzy_match
                )
                
                if not verified:
                    duration = time.time() - start_time
                    self._update_stats(False, duration)
                    return ActionOutcome(
                        result=ActionResult.VERIFICATION_FAILED,
                        message=f"Text in field '{field_text}' was not verified",
                        duration=duration,
                        position=(x, y),
                        screenshot_before=screenshot_before,
                        screenshot_after=screenshot_after
                    )
            
            duration = time.time() - start_time
            self._update_stats(True, duration)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Successfully typed in field '{field_text}'",
                duration=duration,
                position=(x, y),
                screenshot_before=screenshot_before,
                screenshot_after=screenshot_after
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(False, duration)
            logger.error(f"Error typing in field '{field_text}': {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message=f"Failed to type in field",
                duration=duration,
                error=str(e)
            )

    def select_menu_item(
        self,
        menu_path: List[str],
        delay: float = 0.5,
        verify_each: bool = False
    ) -> ActionOutcome:
        """باز کردن منو و انتخاب آیتم از مسیر داده شده.
        
        Args:
            menu_path: لیست مسیر منو، مثلا ["File", "New", "Project"]
            delay: تاخیر بین هر کلیک (ثانیه)
            verify_each: آیا هر مرحله تایید شود؟
        
        Returns:
            ActionOutcome با جزئیات نتیجه
            
        Example:
            >>> controller.select_menu_item(["File", "Save"])
            >>> controller.select_menu_item(["Edit", "Preferences", "Settings"])
            >>> controller.select_menu_item(["فایل", "ذخیره"])
        """
        start_time = time.time()
        logger.info(f"Attempting to navigate menu: {' > '.join(menu_path)}")
        
        try:
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot("before")
            
            positions = []
            
            for i, menu_item in enumerate(menu_path):
                # پیدا کردن و کلیک روی آیتم منو
                wait_result = self.waiter.wait_for_element(
                    menu_item,
                    timeout=5.0
                )
                
                if not wait_result.success or not wait_result.result:
                    duration = time.time() - start_time
                    self._update_stats(False, duration)
                    return ActionOutcome(
                        result=ActionResult.NOT_FOUND,
                        message=f"Menu item '{menu_item}' not found (step {i+1}/{len(menu_path)})",
                        duration=duration,
                        screenshot_before=screenshot_before,
                        metadata={"failed_at": menu_item, "positions": positions}
                    )
                
                # کلیک روی موقعیت پیدا شده
                x, y = wait_result.result
                self.mouse.click(x, y, button="left", clicks=1)
                positions.append((x, y))
                
                # تاخیر برای باز شدن منو
                if i < len(menu_path) - 1:
                    time.sleep(delay)
            
            screenshot_after = self._save_screenshot("after") if self.enable_state_tracking else None
            duration = time.time() - start_time
            self._update_stats(True, duration)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Successfully navigated menu: {' > '.join(menu_path)}",
                duration=duration,
                screenshot_before=screenshot_before,
                screenshot_after=screenshot_after,
                metadata={"positions": positions}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(False, duration)
            logger.error(f"Error navigating menu: {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message=f"Failed to navigate menu",
                duration=duration,
                error=str(e)
            )

    # ==================== COMPLEX WORKFLOWS ====================

    def fill_form(
        self,
        fields: Dict[str, str],
        verify: bool = True,
        submit_button: Optional[str] = None,
        tab_between_fields: bool = False
    ) -> ActionOutcome:
        """پر کردن چندین فیلد فرم به صورت خودکار.
        
        Args:
            fields: دیکشنری از {label: value} برای پر کردن
            verify: آیا هر فیلد تایید شود؟
            submit_button: متن دکمه ارسال (اگر باشد کلیک می‌شود)
            tab_between_fields: استفاده از Tab بین فیلدها
        
        Returns:
            ActionOutcome با جزئیات نتیجه
            
        Example:
            >>> controller.fill_form({
            ...     "Username": "admin",
            ...     "Password": "pass123",
            ...     "Email": "admin@example.com"
            ... }, submit_button="Login")
        """
        start_time = time.time()
        logger.info(f"Attempting to fill form with {len(fields)} fields")
        
        try:
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot("before")
            
            filled_fields = []
            failed_fields = []
            
            for field_name, field_value in fields.items():
                if tab_between_fields and filled_fields:
                    # استفاده از Tab برای رفتن به فیلد بعدی
                    self.keyboard.press('tab')
                    time.sleep(0.3)
                    self.keyboard.type_text(field_value)
                    filled_fields.append(field_name)
                else:
                    # پیدا کردن و پر کردن فیلد
                    result = self.type_in_field(
                        field_name,
                        field_value,
                        verify=verify
                    )
                    
                    if result.result == ActionResult.SUCCESS:
                        filled_fields.append(field_name)
                    else:
                        failed_fields.append((field_name, result.message))
                        logger.warning(f"Failed to fill field '{field_name}': {result.message}")
            
            # کلیک روی دکمه ارسال اگر مشخص شده
            if submit_button:
                time.sleep(0.5)
                submit_result = self.click_on_text(submit_button, verify=True)
                
                if submit_result.result != ActionResult.SUCCESS:
                    duration = time.time() - start_time
                    return ActionOutcome(
                        result=ActionResult.FAILED,
                        message=f"Form filled but submit button '{submit_button}' failed",
                        duration=duration,
                        screenshot_before=screenshot_before,
                        metadata={
                            "filled_fields": filled_fields,
                            "failed_fields": failed_fields,
                            "submit_error": submit_result.message
                        }
                    )
            
            screenshot_after = self._save_screenshot("after") if self.enable_state_tracking else None
            duration = time.time() - start_time
            
            # موفقیت اگر حداقل یک فیلد پر شده
            if filled_fields:
                self._update_stats(True, duration)
                return ActionOutcome(
                    result=ActionResult.SUCCESS,
                    message=f"Form filled: {len(filled_fields)}/{len(fields)} fields successful",
                    duration=duration,
                    screenshot_before=screenshot_before,
                    screenshot_after=screenshot_after,
                    metadata={
                        "filled_fields": filled_fields,
                        "failed_fields": failed_fields
                    }
                )
            else:
                self._update_stats(False, duration)
                return ActionOutcome(
                    result=ActionResult.FAILED,
                    message="Failed to fill any fields",
                    duration=duration,
                    screenshot_before=screenshot_before,
                    metadata={"failed_fields": failed_fields}
                )
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(False, duration)
            logger.error(f"Error filling form: {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message="Failed to fill form",
                duration=duration,
                error=str(e)
            )

    def drag_and_drop(
        self,
        source: Union[str, Tuple[int, int]],
        target: Union[str, Tuple[int, int]],
        source_is_image: bool = False,
        target_is_image: bool = False,
        verify: bool = True,
        duration: float = 1.0
    ) -> ActionOutcome:
        """کشیدن و رها کردن بین دو نقطه.
        
        Args:
            source: متن یا مختصات مبدا
            target: متن یا مختصات مقصد
            source_is_image: آیا source یک مسیر تصویر است؟
            target_is_image: آیا target یک مسیر تصویر است؟
            verify: آیا تایید شود؟
            duration: مدت زمان drag (ثانیه)
        
        Returns:
            ActionOutcome با جزئیات نتیجه
            
        Example:
            >>> # کشیدن فایل به پوشه
            >>> controller.drag_and_drop("file.txt", "Documents")
            >>> 
            >>> # کشیدن بین دو مختصات
            >>> controller.drag_and_drop((100, 200), (500, 600))
        """
        start_time = time.time()
        logger.info(f"Attempting drag and drop: {source} -> {target}")
        
        try:
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot("before")
            
            # پیدا کردن مختصات source
            if isinstance(source, tuple):
                source_x, source_y = source
            elif source_is_image:
                match = self.vision.find_image(str(source))
                if not match:
                    return self._failed_outcome(
                        start_time,
                        f"Source image '{source}' not found",
                        ActionResult.NOT_FOUND,
                        screenshot_before
                    )
                source_x, source_y = match.center
            else:
                wait_result = self.waiter.wait_for_element(source, timeout=10.0)
                if not wait_result.success or not wait_result.result:
                    return self._failed_outcome(
                        start_time,
                        f"Source text '{source}' not found",
                        ActionResult.NOT_FOUND,
                        screenshot_before
                    )
                source_x, source_y = wait_result.result
            
            # پیدا کردن مختصات target
            if isinstance(target, tuple):
                target_x, target_y = target
            elif target_is_image:
                match = self.vision.find_image(str(target))
                if not match:
                    return self._failed_outcome(
                        start_time,
                        f"Target image '{target}' not found",
                        ActionResult.NOT_FOUND,
                        screenshot_before
                    )
                target_x, target_y = match.center
            else:
                wait_result = self.waiter.wait_for_element(target, timeout=10.0)
                if not wait_result.success or not wait_result.result:
                    return self._failed_outcome(
                        start_time,
                        f"Target text '{target}' not found",
                        ActionResult.NOT_FOUND,
                        screenshot_before
                    )
                target_x, target_y = wait_result.result
            
            # اجرای drag and drop
            self.mouse.drag(source_x, source_y, target_x, target_y, duration=duration)
            time.sleep(0.5)
            
            # تایید
            screenshot_after = None
            if verify:
                screenshot_after = self._save_screenshot("after")
                verified = self.vision.verify_click_success(
                    region=(target_x - 50, target_y - 50, 100, 100)
                )
                
                if not verified:
                    duration_elapsed = time.time() - start_time
                    self._update_stats(False, duration_elapsed)
                    return ActionOutcome(
                        result=ActionResult.VERIFICATION_FAILED,
                        message="Drag and drop was not verified",
                        duration=duration_elapsed,
                        position=(target_x, target_y),
                        screenshot_before=screenshot_before,
                        screenshot_after=screenshot_after
                    )
            
            duration_elapsed = time.time() - start_time
            self._update_stats(True, duration_elapsed)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"Successfully dragged from ({source_x},{source_y}) to ({target_x},{target_y})",
                duration=duration_elapsed,
                position=(target_x, target_y),
                screenshot_before=screenshot_before,
                screenshot_after=screenshot_after
            )
            
        except Exception as e:
            duration_elapsed = time.time() - start_time
            self._update_stats(False, duration_elapsed)
            logger.error(f"Error in drag and drop: {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message="Failed to perform drag and drop",
                duration=duration_elapsed,
                error=str(e)
            )

    def navigate_ui(
        self,
        steps: List[Dict[str, Any]],
        stop_on_error: bool = True
    ) -> ActionOutcome:
        """اجرای یک سری اکشن پشت سر هم (Workflow).
        
        Args:
            steps: لیست اکشن‌ها، هر کدام یک dict با type و params
            stop_on_error: آیا در صورت خطا متوقف شود؟
        
        Returns:
            ActionOutcome با جزئیات نتیجه
            
        Example:
            >>> controller.navigate_ui([
            ...     {"type": "click_text", "params": {"text": "File"}},
            ...     {"type": "click_text", "params": {"text": "New"}},
            ...     {"type": "type_field", "params": {"field_text": "Name", "content": "MyProject"}},
            ...     {"type": "click_text", "params": {"text": "Create"}}
            ... ])
        """
        start_time = time.time()
        logger.info(f"Starting UI navigation with {len(steps)} steps")
        
        try:
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot("before")
            
            executed_steps = []
            failed_steps = []
            
            for i, step in enumerate(steps):
                step_type = step.get("type")
                params = step.get("params", {})
                
                logger.info(f"Step {i+1}/{len(steps)}: {step_type}")
                
                # اجرای اکشن بر اساس نوع
                if step_type == "click_text":
                    result = self.click_on_text(**params)
                elif step_type == "click_image":
                    result = self.click_on_image(**params)
                elif step_type == "type_field":
                    result = self.type_in_field(**params)
                elif step_type == "menu":
                    result = self.select_menu_item(**params)
                elif step_type == "wait":
                    time.sleep(params.get("duration", 1.0))
                    result = ActionOutcome(
                        result=ActionResult.SUCCESS,
                        message="Wait completed",
                        duration=params.get("duration", 1.0)
                    )
                else:
                    logger.warning(f"Unknown step type: {step_type}")
                    continue
                
                if result.result == ActionResult.SUCCESS:
                    executed_steps.append({"step": i+1, "type": step_type})
                else:
                    failed_steps.append({"step": i+1, "type": step_type, "error": result.message})
                    
                    if stop_on_error:
                        duration = time.time() - start_time
                        self._update_stats(False, duration)
                        return ActionOutcome(
                            result=ActionResult.FAILED,
                            message=f"Navigation failed at step {i+1}/{len(steps)}: {step_type}",
                            duration=duration,
                            screenshot_before=screenshot_before,
                            metadata={
                                "executed_steps": executed_steps,
                                "failed_steps": failed_steps
                            }
                        )
            
            screenshot_after = self._save_screenshot("after") if self.enable_state_tracking else None
            duration = time.time() - start_time
            
            if failed_steps:
                self._update_stats(False, duration)
                return ActionOutcome(
                    result=ActionResult.FAILED,
                    message=f"Navigation completed with {len(failed_steps)} failures",
                    duration=duration,
                    screenshot_before=screenshot_before,
                    screenshot_after=screenshot_after,
                    metadata={
                        "executed_steps": executed_steps,
                        "failed_steps": failed_steps
                    }
                )
            else:
                self._update_stats(True, duration)
                return ActionOutcome(
                    result=ActionResult.SUCCESS,
                    message=f"Successfully completed {len(steps)} navigation steps",
                    duration=duration,
                    screenshot_before=screenshot_before,
                    screenshot_after=screenshot_after,
                    metadata={"executed_steps": executed_steps}
                )
            
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(False, duration)
            logger.error(f"Error in UI navigation: {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message="Failed to navigate UI",
                duration=duration,
                error=str(e)
            )

    # ==================== STATE MANAGEMENT ====================

    def save_state(self, name: Optional[str] = None) -> ActionState:
        """ذخیره وضعیت فعلی صفحه.
        
        Args:
            name: نام این state (برای ذخیره در checkpoints)
        
        Returns:
            ActionState ذخیره شده
        """
        state = ActionState(
            timestamp=datetime.now(),
            screenshot_path=self._save_screenshot("state"),
            mouse_position=self.mouse.get_position(),
            active_window=self.vision.get_active_window_title() if hasattr(self.vision, 'get_active_window_title') else None
        )
        
        self._states.append(state)
        
        if name:
            self._checkpoints[name] = state
            logger.info(f"State saved as checkpoint: '{name}'")
        
        return state

    def restore_state(self, state: Optional[ActionState] = None, checkpoint_name: Optional[str] = None) -> bool:
        """بازگشت به وضعیت قبلی.
        
        Args:
            state: وضعیتی که باید بازگردانده شود
            checkpoint_name: نام checkpoint ذخیره شده
        
        Returns:
            True اگر موفق بود
        """
        try:
            target_state = None
            
            if checkpoint_name:
                target_state = self._checkpoints.get(checkpoint_name)
                if not target_state:
                    logger.error(f"Checkpoint '{checkpoint_name}' not found")
                    return False
            elif state:
                target_state = state
            elif self._states:
                target_state = self._states[-1]
            else:
                logger.error("No state to restore")
                return False
            
            # بازگشت موس به موقعیت قبلی
            if target_state.mouse_position:
                x, y = target_state.mouse_position
                self.mouse.move(x, y)
            
            logger.info(f"State restored from {target_state.timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring state: {e}")
            return False

    def create_checkpoint(self, name: str) -> ActionState:
        """ایجاد یک checkpoint با نام مشخص.
        
        Args:
            name: نام checkpoint
        
        Returns:
            ActionState ذخیره شده
        """
        return self.save_state(name=name)

    def list_checkpoints(self) -> List[str]:
        """لیست همه checkpoint‌ها.
        
        Returns:
            لیست نام checkpoint‌ها
        """
        return list(self._checkpoints.keys())

    # ==================== UTILITIES ====================

    def _save_screenshot(self, prefix: str) -> Optional[str]:
        """ذخیره اسکرین‌شات با نام منحصر به فرد.
        
        Args:
            prefix: پیشوند نام فایل
        
        Returns:
            مسیر فایل ذخیره شده
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{prefix}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            screenshot = self.vision.capture_screen()
            if screenshot:
                screenshot.save(str(filepath))
                return str(filepath)
            
            return None
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return None

    def _failed_outcome(
        self,
        start_time: float,
        message: str,
        result: ActionResult,
        screenshot_before: Optional[str]
    ) -> ActionOutcome:
        """ایجاد ActionOutcome برای خطا (کمک‌کننده)."""
        duration = time.time() - start_time
        self._update_stats(False, duration)
        return ActionOutcome(
            result=result,
            message=message,
            duration=duration,
            screenshot_before=screenshot_before
        )

    def _update_stats(self, success: bool, duration: float):
        """به‌روزرسانی آمار."""
        self._stats["actions_executed"] += 1
        self._stats["total_duration"] += duration
        
        if success:
            self._stats["successful_actions"] += 1
        else:
            self._stats["failed_actions"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار اجرا.
        
        Returns:
            دیکشنری آمار
        """
        stats = self._stats.copy()
        if stats["actions_executed"] > 0:
            stats["success_rate"] = stats["successful_actions"] / stats["actions_executed"]
            stats["average_duration"] = stats["total_duration"] / stats["actions_executed"]
        else:
            stats["success_rate"] = 0.0
            stats["average_duration"] = 0.0
        
        return stats

    # ==================== DESKTOP ACTIONS EXECUTOR ====================

    def execute_action(
        self,
        action: SystemAction,
        auto_consent: bool = False
    ) -> ActionOutcome:
        """اجرای یک Desktop Action به صورت عمومی.
        
        این متد می‌تواند هر نوع Action از desktop_actions را اجرا کند:
        - ClickAction
        - TypeAction
        - WaitAction
        - DragDropAction
        - HotkeyAction
        - ScrollAction
        
        Args:
            action: یک نمونه از SystemAction (مثلاً ClickAction، TypeAction، ...)
            auto_consent: اگر True باشد، اقدامات با خطر MEDIUM+ بدون تایید اجرا می‌شوند
        
        Returns:
            ActionOutcome با جزئیات کامل نتیجه
            
        Example:
            >>> from core.desktop_actions import ClickAction, TypeAction
            >>> controller = ActionController()
            >>> 
            >>> # اجرای کلیک
            >>> click = ClickAction(target="OK", button="left")
            >>> result = controller.execute_action(click)
            >>> 
            >>> # اجرای تایپ
            >>> type_action = TypeAction(text="Hello World")
            >>> result = controller.execute_action(type_action)
        """
        start_time = time.time()
        action_type = type(action).__name__
        logger.info(f"Executing {action_type}: {action.describe()}")
        
        try:
            # اعتبارسنجی
            valid, msg = action.validate()
            if not valid:
                return ActionOutcome(
                    result=ActionResult.FAILED,
                    message=f"Validation failed: {msg}",
                    duration=time.time() - start_time,
                    error=msg
                )
            
            # بررسی سطح خطر
            risk = action.get_risk_level()
            # Auto-approve for SAFE and LOW risk actions
            # Only ask approval for MEDIUM, HIGH, CRITICAL
            needs_approval = risk.value > RiskLevel.LOW.value and action.require_consent
            
            # درخواست تایید اگر نیاز باشد
            if needs_approval and not auto_consent:
                # نمایش پیام درخواست تایید
                approval_msg = f"\n🟢 {action_type} Approval Request\n───────────────────────────────\nDescription: {action.describe()}\nRisk Level: {risk.name}\nDo you approve this action?\n(y/n): "
                print(approval_msg, end='', flush=True)
                
                # دریافت تایید از کاربر
                try:
                    user_input = input().strip().lower()
                    if user_input not in ['y', 'yes', 'yes please', 'approve']:
                        duration = time.time() - start_time
                        self._update_stats(False, duration)
                        return ActionOutcome(
                            result=ActionResult.FAILED,
                            message="Action cancelled by user",
                            duration=duration,
                            error="User declined approval"
                        )
                except Exception as e:
                    logger.error(f"Error getting user approval: {e}")
                    duration = time.time() - start_time
                    return ActionOutcome(
                        result=ActionResult.FAILED,
                        message="Failed to get user approval",
                        duration=duration,
                        error=str(e)
                    )
            
            # اسکرین‌شات قبل از اجرا
            screenshot_before = None
            if self.enable_state_tracking:
                screenshot_before = self._save_screenshot(f"before_{action_type}")
            
            # اجرای اقدام بر اساس نوع
            position = None
            
            if isinstance(action, ClickAction):
                position = self._execute_click_action(action)
            elif isinstance(action, TypeAction):
                self._execute_type_action(action)
            elif isinstance(action, WaitAction):
                self._execute_wait_action(action)
            elif isinstance(action, DragDropAction):
                position = self._execute_drag_drop_action(action)
            elif isinstance(action, HotkeyAction):
                self._execute_hotkey_action(action)
            elif isinstance(action, ScrollAction):
                self._execute_scroll_action(action)
            else:
                return ActionOutcome(
                    result=ActionResult.FAILED,
                    message=f"Unsupported action type: {action_type}",
                    duration=time.time() - start_time
                )
            
            # اسکرین‌شات بعد از اجرا
            screenshot_after = None
            if self.enable_state_tracking:
                screenshot_after = self._save_screenshot(f"after_{action_type}")
            
            # موفقیت
            duration = time.time() - start_time
            self._update_stats(True, duration)
            
            return ActionOutcome(
                result=ActionResult.SUCCESS,
                message=f"{action.describe()} executed successfully",
                duration=duration,
                position=position,
                screenshot_before=screenshot_before,
                screenshot_after=screenshot_after
            )
        
        except Exception as e:
            duration = time.time() - start_time
            self._update_stats(False, duration)
            logger.error(f"Error executing {action_type}: {e}", exc_info=True)
            
            return ActionOutcome(
                result=ActionResult.FAILED,
                message=f"Error: {str(e)}",
                duration=duration,
                error=str(e)
            )

    def _execute_click_action(self, action: ClickAction) -> Tuple[int, int]:
        """اجرای ClickAction."""
        if isinstance(action.target, tuple):
            # کلیک مستقیم روی مختصات
            x, y = action.target
            button_map = {"left": MouseButton.LEFT, "right": MouseButton.RIGHT, "middle": MouseButton.MIDDLE}
            self.mouse.click(x, y, button=button_map[action.button], clicks=action.clicks)
            return (x, y)
        else:
            # جستجو و کلیک روی متن
            wait_result = self.waiter.wait_for_element(
                action.target,
                timeout=action.timeout,
                confidence=action.confidence
            )
            
            if not wait_result.success or not wait_result.result:
                raise ValueError(f"Element '{action.target}' not found")
            
            x, y = wait_result.result
            button_map = {"left": MouseButton.LEFT, "right": MouseButton.RIGHT, "middle": MouseButton.MIDDLE}
            self.mouse.click(x, y, button=button_map[action.button], clicks=action.clicks)
            return (x, y)

    def _execute_type_action(self, action: TypeAction):
        """اجرای TypeAction."""
        # اگر target مشخص شده، ابتدا روی آن کلیک کنیم
        if action.target:
            if isinstance(action.target, tuple):
                x, y = action.target
                self.mouse.click(x, y, button=MouseButton.LEFT)
            else:
                wait_result = self.waiter.wait_for_element(action.target, timeout=10)
                if wait_result.success and wait_result.result:
                    x, y = wait_result.result
                    self.mouse.click(x, y, button=MouseButton.LEFT)
            time.sleep(0.3)
        
        # پاک کردن محتوای قبلی اگر درخواست شده
        if action.clear_first:
            self.keyboard.hotkey("ctrl", "a")
            time.sleep(0.1)
            self.keyboard.press_key("backspace")
            time.sleep(0.1)
        
        # تایپ متن
        if action.use_clipboard:
            import pyperclip
            pyperclip.copy(action.text or "")
            self.keyboard.hotkey("ctrl", "v")
        else:
            self.keyboard.type_text(action.text or "", interval=action.interval)

    def _execute_wait_action(self, action: WaitAction):
        """اجرای WaitAction."""
        if action.wait_type == "time":
            time.sleep(action.target if isinstance(action.target, (int, float)) else 1.0)
        elif action.wait_type == "element":
            wait_result = self.waiter.wait_for_element(
                str(action.target),
                timeout=int(action.timeout),
                check_interval=action.check_interval
            )
            if not wait_result.success:
                raise TimeoutError(f"Element '{action.target}' not found within {action.timeout}s")
        elif action.wait_type == "change":
            # انتظار برای تغییر ناحیه - پیاده‌سازی ساده
            time.sleep(action.timeout / 10)  # شبیه‌سازی
        # سایر انواع wait می‌توانند اضافه شوند

    def _execute_drag_drop_action(self, action: DragDropAction) -> Tuple[int, int]:
        """اجرای DragDropAction."""
        # پیدا کردن مختصات source
        if isinstance(action.source, tuple):
            start_x, start_y = action.source
        else:
            wait_result = self.waiter.wait_for_element(action.source, timeout=10)
            if not wait_result.success or not wait_result.result:
                raise ValueError(f"Source '{action.source}' not found")
            start_x, start_y = wait_result.result
        
        # پیدا کردن مختصات target
        if isinstance(action.target, tuple):
            end_x, end_y = action.target
        else:
            wait_result = self.waiter.wait_for_element(action.target, timeout=10)
            if not wait_result.success or not wait_result.result:
                raise ValueError(f"Target '{action.target}' not found")
            end_x, end_y = wait_result.result
        
        # اجرای drag & drop
        button_map = {"left": MouseButton.LEFT, "right": MouseButton.RIGHT, "middle": MouseButton.MIDDLE}
        self.mouse.drag_and_drop(
            start_x, start_y, end_x, end_y,
            button=button_map[action.button],
            duration=action.duration
        )
        
        return (end_x, end_y)

    def _execute_hotkey_action(self, action: HotkeyAction):
        """اجرای HotkeyAction."""
        if action.keys:
            self.keyboard.hotkey(*action.keys)

    def _execute_scroll_action(self, action: ScrollAction):
        """اجرای ScrollAction."""
        # اگر target مشخص شده، ابتدا موس را به آنجا ببریم
        if action.target:
            if isinstance(action.target, tuple):
                x, y = action.target
                self.mouse.move_to(x, y)
            else:
                wait_result = self.waiter.wait_for_element(action.target, timeout=10)
                if wait_result.success and wait_result.result:
                    x, y = wait_result.result
                    self.mouse.move_to(x, y)
        
        # اجرای اسکرول
        scroll_amount = action.clicks if action.direction in ["up", "down"] else action.clicks
        if action.direction == "down":
            self.mouse.scroll(-scroll_amount)
        elif action.direction == "up":
            self.mouse.scroll(scroll_amount)
        elif action.direction == "left":
            # اسکرول افقی - نیاز به پیاده‌سازی در MouseController
            pass
        elif action.direction == "right":
            # اسکرول افقی - نیاز به پیاده‌سازی در MouseController
            pass


# ==================== EXPORTS ====================

__all__ = [
    "ActionController",
    "ActionResult",
    "ActionState",
    "ActionOutcome"
]
