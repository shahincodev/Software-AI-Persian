# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های جامع برای MouseController.

این فایل تست شامل:
- تست‌های واحد (Unit Tests)
- تست‌های یکپارچگی (Integration Tests)  
- تست‌های امنیتی (Security Tests)
- تست‌های عملکردی (Performance Tests)
"""

import pytest
import time
from unittest.mock import Mock, patch
from core.mouse_control import (
    MouseController,
    MouseButton,
    ClickPattern,
    MouseAction,
)


class TestMouseController:
    """تست‌های اصلی MouseController."""
    
    def setup_method(self):
        """راه‌اندازی قبل از هر تست."""
        self.mouse = MouseController(
            safety_enabled=True,
            human_behavior=False  # برای تست deterministic بودن
        )
    
    def teardown_method(self):
        """پاک‌سازی بعد از هر تست."""
        self.mouse = None
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Safety & Validation Tests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_is_safe_position_valid(self):
        """تست موقعیت‌های امن."""
        assert self.mouse.is_safe_position(100, 100) is True
        assert self.mouse.is_safe_position(500, 300) is True
    
    def test_is_safe_position_invalid(self):
        """تست موقعیت‌های غیرامن."""
        # خارج از حد بالا
        assert self.mouse.is_safe_position(-10, 100) is False
        # خارج از حد پایین  
        assert self.mouse.is_safe_position(5, 5) is False
        # Y زیاد (نزدیک taskbar)
        bounds_max_y = self.mouse.safe_bounds['max_y']
        assert self.mouse.is_safe_position(100, bounds_max_y + 100) is False
    
    def test_validate_coordinates_success(self):
        """تست اعتبارسنجی مختصات معتبر."""
        x, y = self.mouse.validate_coordinates(100, 100)
        assert x == 100
        assert y == 100
    
    def test_validate_coordinates_failure(self):
        """تست اعتبارسنجی مختصات نامعتبر."""
        with pytest.raises(ValueError) as exc_info:
            self.mouse.validate_coordinates(-10, -10)
        assert "Unsafe position" in str(exc_info.value)
    
    def test_safety_disabled(self):
        """تست غیرفعال کردن امنیت."""
        mouse_unsafe = MouseController(safety_enabled=False)
        # باید موقعیت غیرامن را قبول کند
        assert mouse_unsafe.is_safe_position(-100, -100) is True
        x, y = mouse_unsafe.validate_coordinates(-100, -100)
        assert x == -100
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Human Behavior Tests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_human_variation_disabled(self):
        """تست غیرفعال بودن نویز انسانی."""
        x, y = self.mouse._add_human_variation(100, 100)
        # هیچ نویزی اضافه نمی‌شود
        assert x == 100
        assert y == 100
    
    def test_human_variation_enabled(self):
        """تست فعال بودن نویز انسانی."""
        mouse_human = MouseController(human_behavior=True)
        
        # چند بار تست کن برای اطمینان از تصادفی بودن
        variations = []
        for _ in range(10):
            x, y = mouse_human._add_human_variation(100, 100)
            variations.append((x, y))
        
        # حداقل یکی از موارد باید متفاوت باشد
        assert any(x != 100 or y != 100 for x, y in variations)
        
        # همه باید در محدوده باشند (±2 پیکسل)
        for x, y in variations:
            assert 98 <= x <= 102
            assert 98 <= y <= 102
    
    def test_get_human_delay(self):
        """تست تاخیرهای انسانی."""
        mouse_human = MouseController(human_behavior=True)
        
        # Instant باید 0 باشد حتی با human_behavior
        delay = mouse_human._get_human_delay(ClickPattern.INSTANT)
        assert delay == 0.0
        
        # سایر الگوها باید تاخیر داشته باشند
        delay_fast = mouse_human._get_human_delay(ClickPattern.HUMAN_FAST)
        assert 0.05 <= delay_fast <= 0.1
        
        delay_normal = mouse_human._get_human_delay(ClickPattern.HUMAN_NORMAL)
        assert 0.1 <= delay_normal <= 0.2
        
        delay_slow = mouse_human._get_human_delay(ClickPattern.HUMAN_SLOW)
        assert 0.2 <= delay_slow <= 0.5
    
    def test_bezier_curve_simple(self):
        """تست منحنی Bezier ساده."""
        start = (0, 0)
        end = (100, 100)
        
        # بدون human behavior باید خطی باشد
        points = self.mouse._bezier_curve(start, end, steps=10)
        assert len(points) == 2  # فقط شروع و پایان
        assert points[0] == start
        assert points[1] == end
    
    def test_bezier_curve_smooth(self):
        """تست منحنی Bezier هموار."""
        mouse_human = MouseController(human_behavior=True)
        start = (0, 0)
        end = (100, 100)
        
        points = mouse_human._bezier_curve(start, end, steps=20)
        assert len(points) == 21  # 20 + 1
        assert points[0] == start
        assert points[-1] == end
        
        # نقاط میانی باید در محدوده باشند
        for x, y in points:
            assert 0 <= x <= 100
            assert 0 <= y <= 100
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Core Operations Tests (با Mock)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @patch('core.mouse_control.pyautogui')
    def test_get_position(self, mock_pyautogui):
        """تست دریافت موقعیت."""
        mock_pyautogui.position.return_value = (150, 200)
        
        x, y = self.mouse.get_position()
        assert x == 150
        assert y == 200
        mock_pyautogui.position.assert_called_once()
    
    @patch('core.mouse_control.pyautogui')
    def test_move_simple(self, mock_pyautogui):
        """تست حرکت ساده."""
        mock_pyautogui.size.return_value = (1920, 1080)
        
        result = self.mouse.move(500, 300, duration=0.5, smooth=False)
        
        assert result is True
        mock_pyautogui.moveTo.assert_called_once_with(500, 300, duration=0.5)
        assert self.mouse.stats['total_moves'] == 1
    
    @patch('core.mouse_control.pyautogui')
    def test_move_with_invalid_position(self, mock_pyautogui):
        """تست حرکت به موقعیت نامعتبر."""
        mock_pyautogui.size.return_value = (1920, 1080)
        
        result = self.mouse.move(-100, -100, duration=0.5)
        
        assert result is False
        assert self.mouse.stats['failed_actions'] == 1
    
    @patch('core.mouse_control.pyautogui')
    def test_click_at_position(self, mock_pyautogui):
        """تست کلیک در موقعیت مشخص."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        result = self.mouse.click(100, 100, button=MouseButton.LEFT, clicks=1)
        
        assert result is True
        assert self.mouse.stats['total_clicks'] == 1
        mock_pyautogui.click.assert_called_once()
    
    @patch('core.mouse_control.pyautogui')
    def test_click_double(self, mock_pyautogui):
        """تست دوبل کلیک."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        result = self.mouse.click(100, 100, clicks=2)
        
        assert result is True
        assert self.mouse.stats['total_clicks'] == 2
    
    @patch('core.mouse_control.pyautogui')
    def test_click_right_button(self, mock_pyautogui):
        """تست کلیک راست."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        result = self.mouse.click(100, 100, button=MouseButton.RIGHT)
        
        assert result is True
        args = mock_pyautogui.click.call_args
        assert args[1]['button'] == 'right'
    
    @patch('time.sleep')
    @patch('core.mouse_control.pyautogui')
    def test_click_human(self, mock_pyautogui, mock_sleep):
        """تست کلیک انسانی."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mouse_human = MouseController(human_behavior=True)
        mock_pyautogui.position.return_value = (0, 0)
        
        result = mouse_human.click_human(
            100, 100,
            pattern=ClickPattern.HUMAN_NORMAL
        )
        
        assert result is True
        # باید sleep فراخوانی شود (برای تاخیر)
        assert mock_sleep.call_count >= 1
    
    @patch('core.mouse_control.pyautogui')
    def test_drag(self, mock_pyautogui):
        """تست کشیدن."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        result = self.mouse.drag(100, 100, 500, 300)
        
        assert result is True
        assert self.mouse.stats['total_drags'] == 1
        mock_pyautogui.drag.assert_called_once()
    
    @patch('core.mouse_control.pyautogui')
    def test_scroll(self, mock_pyautogui):
        """تست اسکرول."""
        result = self.mouse.scroll(5)
        
        assert result is True
        assert self.mouse.stats['total_scrolls'] == 1
        mock_pyautogui.scroll.assert_called_once_with(5)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Vision-Guided Operations Tests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def test_click_on_text_no_vision(self):
        """تست کلیک روی متن بدون Vision system."""
        with pytest.raises(ValueError) as exc_info:
            self.mouse.click_on_text("OK")
        assert "Vision system not configured" in str(exc_info.value)
    
    @patch('core.mouse_control.pyautogui')
    def test_click_on_text_success(self, mock_pyautogui):
        """تست کلیک موفق روی متن."""
        # Mock Vision system
        mock_vision = Mock()
        mock_text_box = Mock()
        mock_text_box.center = (150, 200)
        mock_vision.find_text_boxes.return_value = [mock_text_box]
        
        mock_pyautogui.size.return_value = (1920, 1080)
        mouse_with_vision = MouseController(vision_system=mock_vision)
        mock_pyautogui.position.return_value = (0, 0)
        
        result = mouse_with_vision.click_on_text("OK")
        
        assert result is True
        mock_vision.find_text_boxes.assert_called_once_with("OK")
    
    @patch('core.mouse_control.pyautogui')
    def test_click_on_text_not_found(self, mock_pyautogui):
        """تست کلیک روی متن که پیدا نمی‌شود."""
        mock_vision = Mock()
        mock_vision.find_text_boxes.return_value = []  # خالی
        
        mock_pyautogui.size.return_value = (1920, 1080)
        mouse_with_vision = MouseController(vision_system=mock_vision)
        
        with pytest.raises(RuntimeError) as exc_info:
            mouse_with_vision.click_on_text("NotFound")
        assert "Text not found" in str(exc_info.value)
    
    @patch('core.mouse_control.pyautogui')
    def test_click_on_image_success(self, mock_pyautogui):
        """تست کلیک موفق روی تصویر."""
        mock_vision = Mock()
        mock_box = Mock()
        mock_box.center = (300, 400)
        mock_vision.find_image.return_value = mock_box
        
        mock_pyautogui.size.return_value = (1920, 1080)
        mouse_with_vision = MouseController(vision_system=mock_vision)
        mock_pyautogui.position.return_value = (0, 0)
        
        result = mouse_with_vision.click_on_image("button.png")
        
        assert result is True
        mock_vision.find_image.assert_called_once_with("button.png", confidence=0.8)
    
    @patch('core.mouse_control.pyautogui')
    def test_click_on_image_not_found(self, mock_pyautogui):
        """تست کلیک روی تصویر که پیدا نمی‌شود."""
        mock_vision = Mock()
        mock_vision.find_image.return_value = None
        
        mock_pyautogui.size.return_value = (1920, 1080)
        mouse_with_vision = MouseController(vision_system=mock_vision)
        
        with pytest.raises(RuntimeError) as exc_info:
            mouse_with_vision.click_on_image("notfound.png")
        assert "Image not found" in str(exc_info.value)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Stats & History Tests
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    @patch('core.mouse_control.pyautogui')
    def test_action_history(self, mock_pyautogui):
        """تست ذخیره history."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        # چند اقدام انجام بده
        self.mouse.click(100, 100)
        self.mouse.scroll(5)
        
        # بررسی history - click شامل move هم می‌شود
        assert len(self.mouse.action_history) >= 2
        # آخرین اقدام scroll باشد
        assert self.mouse.action_history[-1].action_type == 'scroll'
        # یکی از اقدام‌ها click باشد
        assert any(a.action_type == 'click' for a in self.mouse.action_history)
    
    @patch('core.mouse_control.pyautogui')
    def test_get_stats(self, mock_pyautogui):
        """تست دریافت آمار."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        # چند اقدام
        self.mouse.click(100, 100)
        self.mouse.click(200, 200)
        self.mouse.scroll(5)
        
        stats = self.mouse.get_stats()
        
        assert stats['total_clicks'] == 2
        assert stats['total_scrolls'] == 1
        # total_actions شامل move ها هم می‌شود
        assert stats['total_actions'] >= 3
        assert float(stats['success_rate'].rstrip('%')) == 100.0
    
    def test_reset_stats(self):
        """تست بازنشانی آمار."""
        self.mouse.stats['total_clicks'] = 10
        self.mouse.action_history.append(MouseAction(action_type='click'))
        
        self.mouse.reset_stats()
        
        assert self.mouse.stats['total_clicks'] == 0
        assert len(self.mouse.action_history) == 0


class TestMouseActionDataclass:
    """تست‌های MouseAction dataclass."""
    
    def test_creation_with_defaults(self):
        """تست ساخت با مقادیر پیش‌فرض."""
        action = MouseAction(action_type='click')
        
        assert action.action_type == 'click'
        assert action.x is None
        assert action.y is None
        assert action.button is None
        assert action.timestamp is not None  # auto-generated
        assert action.duration == 0.0
        assert action.success is False
    
    def test_creation_with_values(self):
        """تست ساخت با مقادیر."""
        from datetime import datetime
        now = datetime.now()
        
        action = MouseAction(
            action_type='move',
            x=100,
            y=200,
            timestamp=now,
            duration=0.5,
            success=True
        )
        
        assert action.action_type == 'move'
        assert action.x == 100
        assert action.y == 200
        assert action.timestamp == now
        assert action.duration == 0.5
        assert action.success is True


class TestMouseEnums:
    """تست‌های Enum ها."""
    
    def test_mouse_button_enum(self):
        """تست MouseButton enum."""
        assert MouseButton.LEFT.value == 'left'
        assert MouseButton.RIGHT.value == 'right'
        assert MouseButton.MIDDLE.value == 'middle'
    
    def test_click_pattern_enum(self):
        """تست ClickPattern enum."""
        assert ClickPattern.INSTANT.value == 'instant'
        assert ClickPattern.HUMAN_FAST.value == 'human_fast'
        assert ClickPattern.HUMAN_NORMAL.value == 'human_normal'
        assert ClickPattern.HUMAN_SLOW.value == 'human_slow'
        assert ClickPattern.DOUBLE_CLICK.value == 'double_click'
        assert ClickPattern.TRIPLE_CLICK.value == 'triple_click'


@pytest.mark.slow
class TestPerformance:
    """تست‌های عملکردی (نیاز به --slow flag)."""
    
    def setup_method(self):
        self.mouse = MouseController()
    
    @patch('core.mouse_control.pyautogui')
    def test_click_performance(self, mock_pyautogui):
        """تست سرعت کلیک."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        start = time.time()
        
        for _ in range(100):
            self.mouse.click(100, 100)
        
        duration = time.time() - start
        
        # 100 کلیک باید کمتر از 1 ثانیه باشد
        assert duration < 1.0
        print(f"\n100 clicks in {duration:.3f}s ({100/duration:.1f} clicks/s)")
    
    @patch('core.mouse_control.pyautogui')
    def test_history_memory_limit(self, mock_pyautogui):
        """تست محدودیت حافظه history."""
        mock_pyautogui.size.return_value = (1920, 1080)
        mock_pyautogui.position.return_value = (0, 0)
        
        # بیشتر از max_history اقدام انجام بده
        for i in range(150):
            self.mouse.click(i, i)
        
        # باید به max_history محدود شود
        assert len(self.mouse.action_history) == self.mouse.max_history


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Integration Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.mark.integration
class TestMouseVisionIntegration:
    """تست‌های یکپارچگی Mouse + Vision."""
    
    def test_full_workflow(self):
        """تست workflow کامل با Vision."""
        # این تست نیاز به Vision system واقعی دارد
        # در CI/CD می‌توان skip کرد
        pytest.skip("Needs real Vision system")


if __name__ == "__main__":
    # اجرای تست‌ها
    pytest.main([__file__, "-v", "--tb=short"])
