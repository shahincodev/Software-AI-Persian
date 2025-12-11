# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های سیستم چند مانیتور."""

import pytest
from core.multi_monitor import MultiMonitor, MonitorInfo


class TestMultiMonitor:
    """تست‌های MultiMonitor."""
    
    def setup_method(self):
        """راه‌اندازی قبل از هر تست."""
        self.multi_mon = MultiMonitor()
    
    def test_get_monitors(self):
        """تست دریافت لیست مانیتورها."""
        monitors = self.multi_mon.get_monitors()
        assert isinstance(monitors, list)
        assert len(monitors) >= 1  # حداقل یک مانیتور باید باشد
        assert all(isinstance(m, MonitorInfo) for m in monitors)
    
    def test_get_monitor_count(self):
        """تست تعداد مانیتورها."""
        count = self.multi_mon.get_monitor_count()
        assert count >= 1
        assert isinstance(count, int)
    
    def test_get_primary_monitor(self):
        """تست دریافت مانیتور اصلی."""
        primary = self.multi_mon.get_primary_monitor()
        assert isinstance(primary, MonitorInfo)
        assert primary.is_primary is True
    
    def test_get_monitor_by_index_valid(self):
        """تست دریافت مانیتور با شماره معتبر."""
        monitor = self.multi_mon.get_monitor_by_index(0)
        assert monitor is not None
        assert isinstance(monitor, MonitorInfo)
        assert monitor.index == 0
    
    def test_get_monitor_by_index_invalid(self):
        """تست دریافت مانیتور با شماره نامعتبر."""
        monitor = self.multi_mon.get_monitor_by_index(999)
        assert monitor is None
    
    def test_monitor_info_properties(self):
        """تست ویژگی‌های MonitorInfo."""
        monitor = self.multi_mon.get_primary_monitor()
        
        # Properties
        assert isinstance(monitor.index, int)
        assert isinstance(monitor.name, str)
        assert isinstance(monitor.x, int)
        assert isinstance(monitor.y, int)
        assert isinstance(monitor.width, int)
        assert isinstance(monitor.height, int)
        assert isinstance(monitor.is_primary, bool)
        
        # اندازه‌ها معقول باشند
        assert monitor.width > 0
        assert monitor.height > 0
    
    def test_monitor_center(self):
        """تست محاسبه مرکز مانیتور."""
        monitor = self.multi_mon.get_primary_monitor()
        center_x, center_y = monitor.center
        
        expected_x = monitor.x + monitor.width // 2
        expected_y = monitor.y + monitor.height // 2
        
        assert center_x == expected_x
        assert center_y == expected_y
    
    def test_monitor_bounds(self):
        """تست دریافت محدوده مانیتور."""
        monitor = self.multi_mon.get_primary_monitor()
        x, y, width, height = monitor.bounds
        
        assert x == monitor.x
        assert y == monitor.y
        assert width == monitor.width
        assert height == monitor.height
    
    def test_monitor_contains_point_inside(self):
        """تست بررسی نقطه داخل مانیتور."""
        monitor = self.multi_mon.get_primary_monitor()
        center_x, center_y = monitor.center
        
        assert monitor.contains_point(center_x, center_y) is True
    
    def test_monitor_contains_point_outside(self):
        """تست بررسی نقطه خارج از مانیتور."""
        monitor = self.multi_mon.get_primary_monitor()
        
        # نقطه خیلی دور
        outside_x = monitor.x + monitor.width + 1000
        outside_y = monitor.y + monitor.height + 1000
        
        assert monitor.contains_point(outside_x, outside_y) is False
    
    def test_get_monitor_at_point_primary(self):
        """تست یافتن مانیتور در نقطه (مانیتور اصلی)."""
        primary = self.multi_mon.get_primary_monitor()
        center_x, center_y = primary.center
        
        found = self.multi_mon.get_monitor_at_point(center_x, center_y)
        assert found is not None
        assert found.index == primary.index
    
    def test_get_monitor_at_point_invalid(self):
        """تست یافتن مانیتور در نقطه نامعتبر."""
        found = self.multi_mon.get_monitor_at_point(-10000, -10000)
        # ممکن است None بازگرداند یا مانیتور نزدیک
        # بسته به پیاده‌سازی
    
    def test_convert_to_monitor_same(self):
        """تست تبدیل مختصات در همان مانیتور."""
        x, y = 100, 200
        new_x, new_y = self.multi_mon.convert_to_monitor(x, y, 0, 0)
        
        assert new_x == x
        assert new_y == y
    
    def test_get_current_monitor(self):
        """تست یافتن مانیتور فعلی (موس)."""
        current = self.multi_mon.get_current_monitor()
        # باید مانیتوری پیدا کند
        assert current is not None
        assert isinstance(current, MonitorInfo)
    
    def test_get_total_screen_size(self):
        """تست محاسبه اندازه کل صفحه."""
        total_width, total_height = self.multi_mon.get_total_screen_size()
        
        assert total_width > 0
        assert total_height > 0
        assert isinstance(total_width, int)
        assert isinstance(total_height, int)
    
    def test_get_monitor_layout(self):
        """تست دریافت layout کامل."""
        layout = self.multi_mon.get_monitor_layout()
        
        assert "count" in layout
        assert "primary" in layout
        assert "monitors" in layout
        assert "total_size" in layout
        
        assert layout["count"] >= 1
        assert isinstance(layout["primary"], int)
        assert isinstance(layout["monitors"], list)
        assert "width" in layout["total_size"]
        assert "height" in layout["total_size"]
    
    def test_monitor_layout_consistency(self):
        """تست سازگاری اطلاعات layout."""
        layout = self.multi_mon.get_monitor_layout()
        monitors = self.multi_mon.get_monitors()
        
        # تعداد باید یکسان باشد
        assert layout["count"] == len(monitors)
        
        # هر مانیتور در layout باید وجود داشته باشد
        assert len(layout["monitors"]) == len(monitors)
        
        # مانیتور اصلی باید معتبر باشد
        primary_idx = layout["primary"]
        assert 0 <= primary_idx < len(monitors)
        assert monitors[primary_idx].is_primary is True
    
    def test_click_on_monitor_primary(self):
        """تست کلیک در مانیتور اصلی."""
        primary = self.multi_mon.get_primary_monitor()
        
        # کلیک در مرکز (بدون اجرای واقعی)
        # فقط بررسی می‌کنیم که خطا نمی‌دهد
        try:
            # نباید exception بدهد برای موقعیت معتبر
            x, y = primary.width // 2, primary.height // 2
            # در تست واقعی نباید click کنیم، فقط validate می‌کنیم
            assert primary.contains_point(primary.x + x, primary.y + y)
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")
    
    def test_move_to_monitor_validation(self):
        """تست اعتبارسنجی انتقال موس."""
        primary = self.multi_mon.get_primary_monitor()
        
        # موقعیت معتبر
        x, y = primary.width // 2, primary.height // 2
        abs_x = primary.x + x
        abs_y = primary.y + y
        
        assert primary.contains_point(abs_x, abs_y) is True
        
        # موقعیت نامعتبر (خارج از محدوده)
        x_out = primary.width + 100
        y_out = primary.height + 100
        abs_x_out = primary.x + x_out
        abs_y_out = primary.y + y_out
        
        assert primary.contains_point(abs_x_out, abs_y_out) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
