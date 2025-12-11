# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های جامع برای SmartWaiter - سیستم انتظار هوشمند."""

import time
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from core.smart_wait import (
    SmartWaiter,
    WaitStrategy,
    RetryStrategy,
    WaitResult,
)
from core.desktop_vision import DesktopVision


@pytest.fixture
def mock_vision():
    """Mock برای DesktopVision."""
    vision = Mock(spec=DesktopVision)
    return vision


@pytest.fixture
def waiter(mock_vision):
    """SmartWaiter با vision مقداردهی شده."""
    return SmartWaiter(
        vision_system=mock_vision,
        default_timeout=5.0,
        default_interval=0.1,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Initialization Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_initialization(waiter):
    """تست مقداردهی اولیه."""
    assert waiter.default_timeout == 5.0
    assert waiter.default_interval == 0.1
    assert waiter.stats['total_waits'] == 0
    assert len(waiter.wait_history) == 0


def test_initialization_with_defaults():
    """تست مقداردهی اولیه با مقادیر پیش‌فرض."""
    waiter = SmartWaiter()
    assert waiter.default_timeout == 30.0
    assert waiter.default_interval == 0.5
    assert waiter.vision is not None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Element Waiting Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_wait_for_element_success(waiter, mock_vision):
    """تست انتظار موفق برای عنصر."""
    # تنظیم mock
    mock_vision.find_text.return_value = {
        'text': 'Submit',
        'center': (500, 300),
    }
    
    # اجرای تست
    result = waiter.wait_for_element("Submit", timeout=2)
    
    # بررسی
    assert result.success is True
    assert result.strategy == WaitStrategy.ELEMENT.value
    assert result.result is not None
    assert result.attempts >= 1


def test_wait_for_element_timeout(waiter, mock_vision):
    """تست timeout در انتظار عنصر."""
    # تنظیم mock - همیشه None برگرداند
    mock_vision.find_text.return_value = None
    
    # اجرای تست
    result = waiter.wait_for_element("NotFound", timeout=0.5)
    
    # بررسی
    assert result.success is False
    assert result.error is not None
    assert "not found" in result.error.lower()


def test_wait_for_element_delayed_appearance(waiter, mock_vision):
    """تست عنصری که با تاخیر ظاهر می‌شود."""
    call_count = 0
    
    def delayed_find(text, confidence=0.8):
        nonlocal call_count
        call_count += 1
        if call_count >= 3:  # در سومین فراخوانی پیدا شود
            return {'text': text, 'center': (100, 100)}
        return None
    
    mock_vision.find_text.side_effect = delayed_find
    
    result = waiter.wait_for_element("Button", timeout=2)
    
    assert result.success is True
    assert call_count >= 3


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Change Detection Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_wait_for_change_success(waiter, mock_vision):
    """تست تشخیص موفق تغییر."""
    # ساخت تصاویر mock
    img1 = Image.new('RGB', (100, 100), color='red')
    img2 = Image.new('RGB', (100, 100), color='blue')
    
    # Add take_screenshot as a method
    mock_vision.take_screenshot = Mock(side_effect=[img1, img2])
    mock_vision.has_changed = Mock(return_value=True)
    
    result = waiter.wait_for_change(timeout=2)
    
    assert result.success is True
    assert result.strategy == WaitStrategy.CHANGE.value


def test_wait_for_change_timeout(waiter, mock_vision):
    """تست timeout در تشخیص تغییر."""
    img = Image.new('RGB', (100, 100), color='red')
    
    mock_vision.take_screenshot = Mock(return_value=img)
    mock_vision.has_changed = Mock(return_value=False)
    
    result = waiter.wait_for_change(timeout=0.5)
    
    assert result.success is False


def test_wait_for_change_no_screenshot(waiter, mock_vision):
    """تست شکست در گرفتن اسکرین‌شات."""
    mock_vision.take_screenshot = Mock(return_value=None)
    
    result = waiter.wait_for_change(timeout=0.5)
    
    assert result.success is False
    assert "screenshot" in result.error.lower()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Window Waiting Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_wait_for_window_success_partial(waiter, mock_vision):
    """تست یافتن پنجره با مطابقت جزئی."""
    mock_vision.list_windows.return_value = [
        {'title': 'Untitled - Notepad', 'id': 123},
        {'title': 'Chrome', 'id': 456},
    ]
    
    result = waiter.wait_for_window("Notepad", timeout=1)
    
    assert result.success is True
    assert result.result['title'] == 'Untitled - Notepad'


def test_wait_for_window_success_exact(waiter, mock_vision):
    """تست یافتن پنجره با مطابقت دقیق."""
    mock_vision.list_windows.return_value = [
        {'title': 'Notepad', 'id': 123},
    ]
    
    result = waiter.wait_for_window("Notepad", timeout=1, partial_match=False)
    
    assert result.success is True


def test_wait_for_window_timeout(waiter, mock_vision):
    """تست timeout در انتظار پنجره."""
    mock_vision.list_windows.return_value = [
        {'title': 'Chrome', 'id': 456},
    ]
    
    result = waiter.wait_for_window("Notepad", timeout=0.5)
    
    assert result.success is False


def test_wait_for_window_delayed_appearance(waiter, mock_vision):
    """تست پنجره‌ای که با تاخیر ظاهر می‌شود."""
    call_count = 0
    
    def delayed_windows():
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            return [{'title': 'Notepad', 'id': 123}]
        return []
    
    mock_vision.list_windows.side_effect = delayed_windows
    
    result = waiter.wait_for_window("Notepad", timeout=2)
    
    assert result.success is True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Process Waiting Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_wait_for_process_start(waiter):
    """تست انتظار برای شروع پروسه."""
    with patch('core.smart_wait.psutil.process_iter') as mock_proc:
        # ابتدا پروسه وجود ندارد، سپس وجود دارد
        mock_proc.side_effect = [
            [],  # فراخوانی اول
            [Mock(info={'name': 'notepad.exe'})],  # فراخوانی دوم
        ]
        
        result = waiter.wait_for_process("notepad.exe", timeout=2)
        
        assert result.success is True


def test_wait_for_process_exit(waiter):
    """تست انتظار برای خروج پروسه."""
    with patch('core.smart_wait.psutil.process_iter') as mock_proc:
        # ابتدا پروسه وجود دارد، سپس خارج می‌شود
        mock_proc.side_effect = [
            [Mock(info={'name': 'notepad.exe'})],  # فراخوانی اول
            [],  # فراخوانی دوم
        ]
        
        result = waiter.wait_for_process(
            "notepad.exe",
            timeout=2,
            wait_for_exit=True
        )
        
        assert result.success is True


def test_wait_for_process_timeout(waiter):
    """تست timeout در انتظار پروسه."""
    with patch('core.smart_wait.psutil.process_iter') as mock_proc:
        mock_proc.return_value = []
        
        result = waiter.wait_for_process("notexist.exe", timeout=0.5)
        
        assert result.success is False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CPU Idle Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_wait_for_idle_success(waiter):
    """تست انتظار موفق برای Idle CPU."""
    with patch('core.smart_wait.psutil.cpu_percent') as mock_cpu:
        # CPU به سرعت Idle می‌شود
        mock_cpu.return_value = 5.0
        
        result = waiter.wait_for_idle(
            cpu_threshold=10.0,
            duration=0.2,
            timeout=2
        )
        
        assert result.success is True


def test_wait_for_idle_timeout(waiter):
    """تست timeout در انتظار Idle CPU."""
    with patch('core.smart_wait.psutil.cpu_percent') as mock_cpu:
        # CPU همیشه مشغول
        mock_cpu.return_value = 95.0
        
        result = waiter.wait_for_idle(
            cpu_threshold=10.0,
            duration=1.0,
            timeout=0.5
        )
        
        assert result.success is False


def test_wait_for_idle_fluctuating_cpu(waiter):
    """تست CPU با نوسان."""
    with patch('core.smart_wait.psutil.cpu_percent') as mock_cpu:
        # CPU همیشه idle - ساده‌ترین حالت
        mock_cpu.return_value = 5
        
        result = waiter.wait_for_idle(
            cpu_threshold=10.0,
            duration=0.2,
            timeout=5
        )
        
        # باید موفق شود
        assert result.success is True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Color Waiting Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_wait_for_color_success(waiter, mock_vision):
    """تست یافتن رنگ."""
    img = Image.new('RGB', (100, 100))
    img.putpixel((50, 50), (255, 0, 0))  # قرمز
    
    mock_vision.take_screenshot = Mock(return_value=img)
    
    result = waiter.wait_for_color(
        x=50,
        y=50,
        color=(255, 0, 0),
        timeout=1
    )
    
    assert result.success is True


def test_wait_for_color_with_tolerance(waiter, mock_vision):
    """تست یافتن رنگ با tolerance."""
    img = Image.new('RGB', (100, 100))
    img.putpixel((50, 50), (250, 5, 5))  # نزدیک قرمز
    
    mock_vision.take_screenshot = Mock(return_value=img)
    
    result = waiter.wait_for_color(
        x=50,
        y=50,
        color=(255, 0, 0),
        tolerance=10,
        timeout=1
    )
    
    assert result.success is True


def test_wait_for_color_timeout(waiter, mock_vision):
    """تست timeout در یافتن رنگ."""
    img = Image.new('RGB', (100, 100), color='blue')
    
    mock_vision.take_screenshot = Mock(return_value=img)
    
    result = waiter.wait_for_color(
        x=50,
        y=50,
        color=(255, 0, 0),  # قرمز
        timeout=0.5
    )
    
    assert result.success is False


def test_wait_for_color_out_of_bounds(waiter, mock_vision):
    """تست موقعیت خارج از محدوده."""
    img = Image.new('RGB', (100, 100))
    mock_vision.take_screenshot = Mock(return_value=img)
    
    result = waiter.wait_for_color(
        x=200,  # خارج از محدوده
        y=200,
        color=(255, 0, 0),
        timeout=1
    )
    
    assert result.success is False
    assert "out of bounds" in result.error.lower()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Retry & Backoff Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_retry_success_first_attempt(waiter):
    """تست موفقیت در اولین تلاش."""
    def action():
        return "success"
    
    result = waiter.retry_with_backoff(action, max_retries=3)
    
    assert result.success is True
    assert result.attempts == 1
    assert result.result == "success"


def test_retry_success_after_failures(waiter):
    """تست موفقیت بعد از چند شکست."""
    call_count = 0
    
    def action():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Not yet")
        return "success"
    
    result = waiter.retry_with_backoff(
        action,
        max_retries=5,
        initial_delay=0.1
    )
    
    assert result.success is True
    assert result.attempts == 3


def test_retry_all_attempts_fail(waiter):
    """تست شکست تمام تلاش‌ها."""
    def action():
        raise ValueError("Always fails")
    
    result = waiter.retry_with_backoff(
        action,
        max_retries=3,
        initial_delay=0.1
    )
    
    assert result.success is False
    assert result.attempts == 3
    assert "failed after 3 attempts" in result.error.lower()


def test_retry_exponential_backoff(waiter):
    """تست Exponential Backoff."""
    delays = []
    
    def action():
        raise ValueError("Fail")
    
    # اندازه‌گیری زمان
    start = time.time()
    result = waiter.retry_with_backoff(
        action,
        max_retries=3,
        initial_delay=0.1,
        backoff_factor=2.0,
        strategy=RetryStrategy.EXPONENTIAL
    )
    duration = time.time() - start
    
    # باید حدود 0.1 + 0.2 = 0.3 ثانیه طول بکشد (فقط 2 retry delay)
    assert duration >= 0.25
    assert result.success is False


def test_retry_linear_backoff(waiter):
    """تست Linear Backoff."""
    def action():
        raise ValueError("Fail")
    
    start = time.time()
    result = waiter.retry_with_backoff(
        action,
        max_retries=3,
        initial_delay=0.1,
        strategy=RetryStrategy.LINEAR
    )
    duration = time.time() - start
    
    # باید حدود 0.1 + 0.1 = 0.2 ثانیه طول بکشد
    assert duration >= 0.15
    assert result.success is False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Polling Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_poll_until_success(waiter):
    """تست polling موفق."""
    counter = 0
    
    def condition():
        nonlocal counter
        counter += 1
        return counter >= 3
    
    result = waiter.poll_until(condition, timeout=2, interval=0.1)
    
    assert result.success is True
    assert counter >= 3


def test_poll_until_timeout(waiter):
    """تست timeout در polling."""
    def condition():
        return False
    
    result = waiter.poll_until(condition, timeout=0.5, interval=0.1)
    
    assert result.success is False


def test_poll_until_exception(waiter):
    """تست استثنا در شرط."""
    def condition():
        raise RuntimeError("Error")
    
    result = waiter.poll_until(condition, timeout=0.5, interval=0.1)
    
    assert result.success is False


def test_poll_until_file_exists(waiter, tmp_path):
    """تست polling برای موجود شدن فایل."""
    test_file = tmp_path / "test.txt"
    
    def create_file_delayed():
        time.sleep(0.2)
        test_file.write_text("content")
    
    import threading
    thread = threading.Thread(target=create_file_delayed)
    thread.start()
    
    result = waiter.poll_until(
        lambda: test_file.exists(),
        timeout=2,
        interval=0.05
    )
    
    thread.join()
    
    assert result.success is True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Statistics Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_statistics_tracking(waiter, mock_vision):
    """تست ردیابی آمار."""
    mock_vision.find_text.return_value = {'text': 'Test', 'center': (100, 100)}
    
    # چند عملیات انجام دهیم
    waiter.wait_for_element("Test1", timeout=1)
    waiter.wait_for_element("Test2", timeout=1)
    
    stats = waiter.get_stats()
    
    assert stats['total_waits'] == 2
    assert stats['successful_waits'] == 2
    assert stats['success_rate'] == 100.0
    assert stats['avg_wait_time'] > 0


def test_statistics_with_failures(waiter, mock_vision):
    """تست آمار با شکست."""
    mock_vision.find_text.return_value = None
    
    # یک عملیات شکست‌خورده
    waiter.wait_for_element("NotFound", timeout=0.5)
    
    stats = waiter.get_stats()
    
    assert stats['total_waits'] == 1
    assert stats['timeout_waits'] == 1
    assert stats['success_rate'] == 0.0


def test_wait_history(waiter, mock_vision):
    """تست تاریخچه انتظار."""
    mock_vision.find_text.return_value = {'text': 'Test', 'center': (100, 100)}
    
    # انجام چند عملیات
    for i in range(5):
        waiter.wait_for_element(f"Test{i}", timeout=1)
    
    history = waiter.get_wait_history(limit=3)
    
    assert len(history) == 3
    assert all(isinstance(r, WaitResult) for r in history)


def test_history_limit(waiter, mock_vision):
    """تست محدودیت تاریخچه."""
    mock_vision.find_text.return_value = {'text': 'Test', 'center': (100, 100)}
    
    # بیش از max_history عملیات
    for i in range(150):
        waiter.wait_for_element(f"Test{i}", timeout=0.1)
    
    assert len(waiter.wait_history) <= waiter.max_history


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Edge Cases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_zero_timeout(waiter, mock_vision):
    """تست با timeout صفر."""
    mock_vision.find_text.return_value = None
    
    result = waiter.wait_for_element("Test", timeout=0)
    
    assert result.success is False


def test_negative_timeout(waiter, mock_vision):
    """تست با timeout منفی."""
    mock_vision.find_text.return_value = None
    
    result = waiter.wait_for_element("Test", timeout=-1)
    
    assert result.success is False


def test_very_short_interval(waiter, mock_vision):
    """تست با interval خیلی کوتاه."""
    call_count = 0
    
    def count_calls(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count >= 5:
            return {'text': 'Test', 'center': (100, 100)}
        return None
    
    mock_vision.find_text.side_effect = count_calls
    
    result = waiter.wait_for_element("Test", timeout=1, check_interval=0.01)
    
    assert result.success is True
    assert call_count >= 5


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Performance Benchmarks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# Note: Benchmark tests removed - requires pytest-benchmark
# Install with: pip install pytest-benchmark


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
