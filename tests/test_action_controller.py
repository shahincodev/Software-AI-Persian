# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های جامع برای ActionController.

این تست‌ها قابلیت‌های Week 2 Day 4 را بررسی می‌کنند:
- High-Level Actions (click_on_text, click_on_image, type_in_field, select_menu_item)
- Complex Workflows (fill_form, drag_and_drop, navigate_ui)
- State Management (save/restore/checkpoint)
"""

import pytest
import time
from unittest.mock import Mock, MagicMock

from core.action_controller import (
    ActionController,
    ActionResult,
    ActionState,
)
from core.desktop_vision import ImageMatch
from core.smart_wait import WaitResult, WaitStrategy


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fixtures
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_wait_result(success=True, result=(200, 300)):
    """Helper برای ساخت WaitResult."""
    return WaitResult(
        success=success,
        strategy=WaitStrategy.ELEMENT.value,
        duration=0.5,
        attempts=1,
        result=result if success else None,
        error=None if success else "Not found"
    )

@pytest.fixture
def mock_mouse():
    """Mock MouseController."""
    mouse = MagicMock()
    mouse.click = MagicMock()
    mouse.move = MagicMock()
    mouse.drag = MagicMock()
    mouse.get_position = MagicMock(return_value=(100, 100))
    return mouse


@pytest.fixture
def mock_keyboard():
    """Mock KeyboardController."""
    keyboard = MagicMock()
    keyboard.type_text = MagicMock()
    keyboard.press = MagicMock()
    keyboard.hotkey = MagicMock()
    return keyboard


@pytest.fixture
def mock_vision():
    """Mock DesktopVision."""
    vision = MagicMock()
    vision.capture_screen = MagicMock(return_value=Mock(save=MagicMock()))
    vision.find_text = MagicMock(return_value=(200, 300))
    vision.find_image = MagicMock(return_value=ImageMatch(100, 200, 50, 30, 0.95))
    vision.find_input_field = MagicMock(return_value=(150, 250))
    vision.verify_click_success = MagicMock(return_value=True)
    vision.verify_text_typed = MagicMock(return_value=True)
    vision.wait_for_image = MagicMock(return_value=ImageMatch(100, 200, 50, 30, 0.95))
    return vision


@pytest.fixture
def mock_waiter():
    """Mock SmartWait."""
    waiter = MagicMock()
    # برگرداندن WaitResult به جای tuple
    waiter.wait_for_element = MagicMock(return_value=create_wait_result())
    waiter.wait_for_color = MagicMock(return_value=True)
    return waiter


@pytest.fixture
def controller(mock_mouse, mock_keyboard, mock_vision, mock_waiter, tmp_path):
    """ActionController با dependencies مانع شده."""
    return ActionController(
        mouse=mock_mouse,
        keyboard=mock_keyboard,
        vision=mock_vision,
        waiter=mock_waiter,
        enable_state_tracking=True,
        screenshot_dir=tmp_path / "screenshots"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 1: High-Level Actions Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestClickOnText:
    """تست‌های click_on_text."""
    
    def test_click_on_text_success(self, controller, mock_waiter, mock_mouse, mock_vision):
        """تست کلیک موفق روی متن."""
        # Setup
        mock_waiter.wait_for_element.return_value = create_wait_result()
        mock_vision.verify_click_success.return_value = True
        
        # Execute
        result = controller.click_on_text("OK", verify=True)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert result.position == (200, 300)
        assert "OK" in result.message
        mock_waiter.wait_for_element.assert_called_once()
        mock_mouse.click.assert_called_once_with(200, 300, button="left", clicks=1)
        mock_vision.verify_click_success.assert_called_once()
    
    def test_click_on_text_not_found(self, controller, mock_waiter):
        """تست متن پیدا نشود."""
        # Setup
        mock_waiter.wait_for_element.return_value = create_wait_result(success=False)
        
        # Execute
        result = controller.click_on_text("NonExistent", timeout=5.0)
        
        # Verify
        assert result.result == ActionResult.NOT_FOUND
        assert "not found" in result.message.lower()
        assert result.position is None
    
    def test_click_on_text_verification_failed(self, controller, mock_waiter, mock_vision):
        """تست شکست تایید بعد از کلیک."""
        # Setup
        mock_waiter.wait_for_element.return_value = create_wait_result()
        mock_vision.verify_click_success.return_value = False
        
        # Execute
        result = controller.click_on_text("Button", verify=True)
        
        # Verify
        assert result.result == ActionResult.VERIFICATION_FAILED
        assert "not verified" in result.message.lower()
    
    def test_click_on_text_double_click(self, controller, mock_waiter, mock_mouse):
        """تست دوبل کلیک."""
        # Setup
        mock_waiter.wait_for_element.return_value = create_wait_result(result=(200, 300))
        
        # Execute
        result = controller.click_on_text("File", clicks=2, verify=False)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_mouse.click.assert_called_once_with(200, 300, button="left", clicks=2)
    
    def test_click_on_text_right_click(self, controller, mock_waiter, mock_mouse):
        """تست کلیک راست."""
        # Setup
        mock_waiter.wait_for_element.return_value = create_wait_result(result=(200, 300))
        
        # Execute
        result = controller.click_on_text("Item", button="right", verify=False)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_mouse.click.assert_called_once_with(200, 300, button="right", clicks=1)


class TestClickOnImage:
    """تست‌های click_on_image."""
    
    def test_click_on_image_success(self, controller, mock_vision, mock_mouse):
        """تست کلیک موفق روی تصویر."""
        # Setup
        match = ImageMatch(x=100, y=200, width=50, height=30, confidence=0.95)
        mock_vision.wait_for_image.return_value = match
        mock_vision.verify_click_success.return_value = True
        
        # Execute
        result = controller.click_on_image("button.png", verify=True)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert result.position == match.center
        mock_mouse.click.assert_called_once_with(*match.center, button="left", clicks=1)
    
    def test_click_on_image_not_found(self, controller, mock_vision):
        """تست تصویر پیدا نشود."""
        # Setup
        mock_vision.wait_for_image.return_value = None
        
        # Execute
        result = controller.click_on_image("missing.png", timeout=5.0)
        
        # Verify
        assert result.result == ActionResult.NOT_FOUND
        assert "not found" in result.message.lower()
    
    def test_click_on_image_low_confidence(self, controller, mock_vision):
        """تست با confidence پایین."""
        # Setup
        match = ImageMatch(x=100, y=200, width=50, height=30, confidence=0.95)
        mock_vision.wait_for_image.return_value = match
        
        # Execute
        result = controller.click_on_image("icon.png", confidence=0.9, verify=False)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_vision.wait_for_image.assert_called_once()


class TestTypeInField:
    """تست‌های type_in_field."""
    
    def test_type_in_field_success(self, controller, mock_vision, mock_mouse, mock_keyboard):
        """تست تایپ موفق در فیلد."""
        # Setup
        mock_vision.find_input_field.return_value = (150, 250)
        mock_vision.verify_text_typed.return_value = True
        
        # Execute
        result = controller.type_in_field("Username", "admin", verify=True)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert result.position == (150, 250)
        mock_mouse.click.assert_called_once_with(150, 250)
        mock_keyboard.hotkey.assert_called_with('ctrl', 'a')
        mock_keyboard.type_text.assert_called_once_with("admin")
    
    def test_type_in_field_not_found(self, controller, mock_vision):
        """تست فیلد پیدا نشود."""
        # Setup
        mock_vision.find_input_field.return_value = None
        
        # Execute
        result = controller.type_in_field("NonExistent", "text")
        
        # Verify
        assert result.result == ActionResult.NOT_FOUND
    
    def test_type_in_field_no_clear(self, controller, mock_vision, mock_keyboard):
        """تست بدون پاک کردن محتوای قبلی."""
        # Setup
        mock_vision.find_input_field.return_value = (150, 250)
        
        # Execute
        result = controller.type_in_field("Field", "text", clear_first=False, verify=False)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        # نباید ctrl+a فراخوانی شود
        mock_keyboard.hotkey.assert_not_called()
        mock_keyboard.type_text.assert_called_once_with("text")
    
    def test_type_in_field_persian(self, controller, mock_vision, mock_keyboard):
        """تست تایپ متن فارسی."""
        # Setup
        mock_vision.find_input_field.return_value = (150, 250)
        
        # Execute
        result = controller.type_in_field("نام", "احمد", verify=False)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_keyboard.type_text.assert_called_once_with("احمد")


class TestSelectMenuItem:
    """تست‌های select_menu_item."""
    
    def test_select_menu_item_single(self, controller, mock_waiter, mock_mouse):
        """تست انتخاب یک آیتم ساده."""
        # Setup
        mock_waiter.wait_for_element.return_value = create_wait_result(result=(200, 300))
        
        # Execute
        result = controller.select_menu_item(["File"])
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_waiter.wait_for_element.assert_called_once()
        mock_mouse.click.assert_called_once()
    
    def test_select_menu_item_nested(self, controller, mock_waiter, mock_mouse):
        """تست پیمایش منوی چند سطحی."""
        # Setup
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(100, 100)),
            create_wait_result(result=(200, 200)),
            create_wait_result(result=(300, 300))
        ]
        
        # Execute
        result = controller.select_menu_item(["File", "New", "Project"])
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert mock_waiter.wait_for_element.call_count == 3
        assert mock_mouse.click.call_count == 3
        assert "File > New > Project" in result.message
    
    def test_select_menu_item_not_found(self, controller, mock_waiter):
        """تست آیتم منو پیدا نشود."""
        # Setup
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(100, 100)),
            create_wait_result(success=False)
        ]
        
        # Execute
        result = controller.select_menu_item(["File", "Missing"])
        
        # Verify
        assert result.result == ActionResult.NOT_FOUND
        assert "Missing" in result.message
        assert "step 2/2" in result.message


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 2: Complex Workflows Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestFillForm:
    """تست‌های fill_form."""
    
    def test_fill_form_success(self, controller, mock_vision, mock_keyboard):
        """تست پر کردن فرم موفق."""
        # Setup
        mock_vision.find_input_field.side_effect = [(100, 100), (200, 200), (300, 300)]
        mock_vision.verify_text_typed.return_value = True
        
        # Execute
        result = controller.fill_form({
            "Username": "admin",
            "Password": "pass123",
            "Email": "test@example.com"
        }, verify=True)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert "3/3" in result.message
        assert mock_vision.find_input_field.call_count == 3
        assert mock_keyboard.type_text.call_count == 3
    
    def test_fill_form_with_submit(self, controller, mock_vision, mock_mouse, mock_waiter):
        """تست پر کردن فرم با کلیک روی دکمه ارسال."""
        # Setup
        mock_vision.find_input_field.side_effect = [(100, 100), (200, 200)]
        mock_vision.verify_text_typed.return_value = True
        mock_waiter.wait_for_element.return_value = create_wait_result(result=(400, 400))
        mock_vision.verify_click_success.return_value = True
        
        # Execute
        result = controller.fill_form({
            "Username": "admin",
            "Password": "pass123"
        }, submit_button="Login", verify=True)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_waiter.wait_for_element.assert_called_once_with("Login", timeout=10.0, confidence=0.8)
        mock_mouse.click.assert_called()
    
    def test_fill_form_partial_success(self, controller, mock_vision):
        """تست فرمی که بعضی فیلدهایش پر نمی‌شود."""
        # Setup
        mock_vision.find_input_field.side_effect = [(100, 100), None, (300, 300)]
        mock_vision.verify_text_typed.return_value = True
        
        # Execute
        result = controller.fill_form({
            "Field1": "value1",
            "Field2": "value2",
            "Field3": "value3"
        }, verify=True)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert "2/3" in result.message
        metadata = result.metadata
        assert len(metadata["filled_fields"]) == 2
        assert len(metadata["failed_fields"]) == 1
    
    def test_fill_form_with_tab(self, controller, mock_vision, mock_keyboard):
        """تست استفاده از Tab بین فیلدها."""
        # Setup
        mock_vision.find_input_field.return_value = (100, 100)
        mock_vision.verify_text_typed.return_value = True
        
        # Execute
        result = controller.fill_form({
            "Field1": "value1",
            "Field2": "value2"
        }, tab_between_fields=True, verify=False)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        # فیلد اول با find_input_field، بقیه با Tab
        # اما در verify=False، find_input_field صدا نمی‌شود چون tab_between_fields=True
        # پس تنها یکبار برای فیلد اول
        assert mock_keyboard.type_text.call_count == 2


class TestDragAndDrop:
    """تست‌های drag_and_drop."""
    
    def test_drag_and_drop_coordinates(self, controller, mock_mouse, mock_vision):
        """تست drag and drop با مختصات."""
        # Setup
        mock_vision.verify_click_success.return_value = True
        
        # Execute
        result = controller.drag_and_drop((100, 200), (500, 600), verify=True)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_mouse.drag.assert_called_once_with(100, 200, 500, 600, duration=1.0)
    
    def test_drag_and_drop_text_targets(self, controller, mock_waiter, mock_mouse):
        """تست drag and drop با متن."""
        # Setup
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(100, 100)),
            create_wait_result(result=(500, 500))
        ]
        
        # Execute
        result = controller.drag_and_drop("File.txt", "Folder", verify=False)
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert mock_waiter.wait_for_element.call_count == 2
        mock_mouse.drag.assert_called_once_with(100, 100, 500, 500, duration=1.0)
    
    def test_drag_and_drop_images(self, controller, mock_vision, mock_mouse):
        """تست drag and drop با تصویر."""
        # Setup
        match1 = ImageMatch(100, 100, 50, 30, 0.95)
        match2 = ImageMatch(500, 500, 50, 30, 0.95)
        mock_vision.find_image.side_effect = [match1, match2]
        
        # Execute
        result = controller.drag_and_drop(
            "icon1.png", "icon2.png",
            source_is_image=True,
            target_is_image=True,
            verify=False
        )
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        mock_mouse.drag.assert_called_once_with(
            *match1.center, *match2.center, duration=1.0
        )
    
    def test_drag_and_drop_source_not_found(self, controller, mock_waiter):
        """تست source پیدا نشود."""
        # Setup
        mock_waiter.wait_for_element.return_value = create_wait_result(success=False)
        
        # Execute
        result = controller.drag_and_drop("Missing", "Target")
        
        # Verify
        assert result.result == ActionResult.NOT_FOUND
        assert "Source" in result.message


class TestNavigateUI:
    """تست‌های navigate_ui."""
    
    def test_navigate_ui_success(self, controller, mock_waiter, mock_vision, mock_mouse, mock_keyboard):
        """تست workflow موفق."""
        # Setup - هر click_text یک wait_for_element صدا می‌زند
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(200, 300)),  # File
            create_wait_result(result=(250, 350)),  # New
            create_wait_result(result=(400, 450))   # Create
        ]
        mock_vision.find_input_field.return_value = (150, 250)
        mock_vision.verify_click_success.return_value = True
        mock_vision.verify_text_typed.return_value = True
        
        # Execute
        result = controller.navigate_ui([
            {"type": "click_text", "params": {"text": "File", "verify": False}},
            {"type": "click_text", "params": {"text": "New", "verify": False}},
            {"type": "type_field", "params": {"field_text": "Name", "content": "MyProject", "verify": False}},
            {"type": "click_text", "params": {"text": "Create", "verify": False}}
        ])
        
        # Verify
        assert result.result == ActionResult.SUCCESS
        assert "4 navigation steps" in result.message
        assert len(result.metadata["executed_steps"]) == 4
    
    def test_navigate_ui_with_wait(self, controller):
        """تست workflow با wait."""
        # Execute
        result = controller.navigate_ui([
            {"type": "wait", "params": {"duration": 0.1}}
        ])
        
        # Verify
        assert result.result == ActionResult.SUCCESS
    
    def test_navigate_ui_stop_on_error(self, controller, mock_waiter):
        """تست توقف workflow در صورت خطا."""
        # Setup
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(200, 300)),
            create_wait_result(success=False)
        ]
        
        # Execute
        result = controller.navigate_ui([
            {"type": "click_text", "params": {"text": "OK", "verify": False}},
            {"type": "click_text", "params": {"text": "Missing", "verify": False}},
            {"type": "click_text", "params": {"text": "Next", "verify": False}}
        ], stop_on_error=True)
        
        # Verify
        assert result.result == ActionResult.FAILED
        assert "step 2/3" in result.message
        metadata = result.metadata
        assert len(metadata["executed_steps"]) == 1
        assert len(metadata["failed_steps"]) == 1
    
    def test_navigate_ui_continue_on_error(self, controller, mock_waiter):
        """تست ادامه workflow با وجود خطا."""
        # Setup
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(200, 300)),
            create_wait_result(success=False),
            create_wait_result(result=(400, 400))
        ]
        
        # Execute
        result = controller.navigate_ui([
            {"type": "click_text", "params": {"text": "OK", "verify": False}},
            {"type": "click_text", "params": {"text": "Missing", "verify": False}},
            {"type": "click_text", "params": {"text": "Next", "verify": False}}
        ], stop_on_error=False)
        
        # Verify
        assert result.result == ActionResult.FAILED
        metadata = result.metadata
        assert len(metadata["executed_steps"]) == 2
        assert len(metadata["failed_steps"]) == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 3: State Management Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestStateManagement:
    """تست‌های State Management."""
    
    def test_save_state(self, controller, mock_mouse, mock_vision):
        """تست ذخیره وضعیت."""
        # Execute
        state = controller.save_state()
        
        # Verify
        assert isinstance(state, ActionState)
        assert state.timestamp is not None
        assert state.mouse_position == (100, 100)
        assert len(controller._states) == 1
    
    def test_save_state_with_name(self, controller):
        """تست ذخیره وضعیت با نام."""
        # Execute
        state = controller.save_state(name="checkpoint1")
        
        # Verify
        assert "checkpoint1" in controller._checkpoints
        assert controller._checkpoints["checkpoint1"] == state
    
    def test_restore_state(self, controller, mock_mouse):
        """تست بازگشت به وضعیت."""
        # Setup
        state = controller.save_state()
        
        # Execute
        success = controller.restore_state(state)
        
        # Verify
        assert success is True
        mock_mouse.move.assert_called_once_with(100, 100)
    
    def test_restore_checkpoint(self, controller, mock_mouse):
        """تست بازگشت به checkpoint."""
        # Setup
        controller.save_state(name="before_action")
        mock_mouse.get_position.return_value = (500, 500)
        
        # Execute
        success = controller.restore_state(checkpoint_name="before_action")
        
        # Verify
        assert success is True
        mock_mouse.move.assert_called_with(100, 100)
    
    def test_restore_checkpoint_not_found(self, controller):
        """تست checkpoint پیدا نشود."""
        # Execute
        success = controller.restore_state(checkpoint_name="nonexistent")
        
        # Verify
        assert success is False
    
    def test_create_checkpoint(self, controller):
        """تست ایجاد checkpoint."""
        # Execute
        state = controller.create_checkpoint("test_checkpoint")
        
        # Verify
        assert isinstance(state, ActionState)
        assert "test_checkpoint" in controller._checkpoints
    
    def test_list_checkpoints(self, controller):
        """تست لیست checkpointها."""
        # Setup
        controller.create_checkpoint("cp1")
        controller.create_checkpoint("cp2")
        controller.create_checkpoint("cp3")
        
        # Execute
        checkpoints = controller.list_checkpoints()
        
        # Verify
        assert len(checkpoints) == 3
        assert "cp1" in checkpoints
        assert "cp2" in checkpoints
        assert "cp3" in checkpoints


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 4: Integration & Statistics Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestIntegration:
    """تست‌های یکپارچگی."""
    
    def test_full_workflow_integration(self, controller, mock_waiter, mock_vision, mock_mouse, mock_keyboard):
        """تست workflow کامل: باز کردن برنامه، پر کردن فرم، ذخیره."""
        # Setup - تمام wait_for_element فراخوانی‌ها
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(100, 100)),  # File
            create_wait_result(result=(200, 200)),  # New
            create_wait_result(result=(400, 400))   # Create
        ]
        mock_vision.find_input_field.side_effect = [(150, 250), (160, 260)]
        mock_vision.verify_click_success.return_value = True
        mock_vision.verify_text_typed.return_value = True
        
        # 1. Save initial state
        controller.save_state(name="initial")
        
        # 2. Open File menu
        result1 = controller.select_menu_item(["File", "New"])
        assert result1.result == ActionResult.SUCCESS
        
        # 3. Fill form
        result2 = controller.fill_form({
            "Name": "MyProject",
            "Location": "C:\\Projects"
        }, verify=True)
        assert result2.result == ActionResult.SUCCESS
        
        # 4. Click Create
        result3 = controller.click_on_text("Create", verify=True)
        assert result3.result == ActionResult.SUCCESS
        
        # Verify all steps succeeded
        stats = controller.get_stats()
        assert stats["successful_actions"] >= 3


class TestStatistics:
    """تست‌های آمار."""
    
    def test_get_stats_initial(self, controller):
        """تست آمار اولیه."""
        stats = controller.get_stats()
        
        assert stats["actions_executed"] == 0
        assert stats["successful_actions"] == 0
        assert stats["failed_actions"] == 0
        assert stats["success_rate"] == 0.0
    
    def test_get_stats_after_actions(self, controller, mock_waiter):
        """تست آمار بعد از چند اکشن."""
        # Setup
        mock_waiter.wait_for_element.side_effect = [
            create_wait_result(result=(200, 300)),  # Success
            create_wait_result(success=False),      # Failed
            create_wait_result(result=(400, 400))   # Success
        ]
        
        # Execute actions
        controller.click_on_text("OK", verify=False)  # Success
        controller.click_on_text("Missing", verify=False)  # Failed
        controller.click_on_text("Next", verify=False)  # Success
        
        # Get stats
        stats = controller.get_stats()
        
        # Verify
        assert stats["actions_executed"] == 3
        assert stats["successful_actions"] == 2
        assert stats["failed_actions"] == 1
        assert stats["success_rate"] == 2/3


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 5: Error Handling Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestErrorHandling:
    """تست‌های مدیریت خطا."""
    
    def test_exception_in_click_on_text(self, controller, mock_waiter):
        """تست استثنا در click_on_text."""
        # Setup
        mock_waiter.wait_for_element.side_effect = Exception("Test error")
        
        # Execute
        result = controller.click_on_text("Button")
        
        # Verify
        assert result.result == ActionResult.FAILED
        assert result.error == "Test error"
    
    def test_exception_in_fill_form(self, controller, mock_vision):
        """تست استثنا در fill_form."""
        # Setup
        mock_vision.find_input_field.side_effect = Exception("Vision error")
        
        # Execute
        result = controller.fill_form({"Field": "value"})
        
        # Verify
        assert result.result == ActionResult.FAILED
        # exception در type_in_field catch میشه و به عنوان failed_field ذخیره میشه
        # ولی fill_form خودش exception رو catch نمی‌کنه چون type_in_field catch کرده
        assert len(result.metadata.get("failed_fields", [])) > 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بخش 6: Performance Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestPerformance:
    """تست‌های عملکرد."""
    
    def test_action_duration_tracking(self, controller, mock_waiter):
        """تست ردیابی زمان اجرا."""
        # Setup
        mock_waiter.wait_for_element.return_value = (200, 300)
        
        # Execute
        result = controller.click_on_text("OK", verify=False)
        
        # Verify
        assert result.duration > 0
        assert result.duration < 5.0  # نباید بیش از 5 ثانیه طول بکشد
    
    def test_multiple_actions_performance(self, controller, mock_waiter):
        """تست عملکرد با چند اکشن."""
        # Setup
        mock_waiter.wait_for_element.return_value = (200, 300)
        
        # Execute 10 actions
        start_time = time.time()
        for i in range(10):
            controller.click_on_text(f"Button{i}", verify=False)
        total_time = time.time() - start_time
        
        # Verify
        stats = controller.get_stats()
        assert stats["actions_executed"] == 10
        assert total_time < 10.0  # حداکثر 1 ثانیه به ازای هر اکشن


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
