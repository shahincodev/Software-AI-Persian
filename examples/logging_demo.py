#!/usr/bin/env python3
# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""مثال ساده از استفاده سیستم لاگ‌گیری پیشرفته.

این اسکریپت نحوه استفاده از سیستم لاگ‌گیری را نشان می‌دهد.
"""

import sys
import asyncio
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.advanced_logging import get_advanced_logger, close_advanced_logger
from core.logging_decorators import (
    log_function_call,
    log_async_function_call,
    log_user_action,
    LogContext
)


# ==================== مثال 1: لاگ دستی ====================

def manual_logging_example():
    """مثال لاگ‌گیری دستی."""
    logger = get_advanced_logger()
    
    # لاگ سیستمی
    logger.log_system("Example script started")
    
    # لاگ اقدام کاربر
    logger.log_user_action(
        "test_action",
        {"param1": "value1", "param2": "value2"},
        success=True
    )
    
    # لاگ خطا
    logger.log_error(
        "This is a test error",
        "TestError",
        {"details": "Some error details"}
    )
    
    # لاگ امنیتی
    logger.log_security(
        "Test security event",
        "low",
        {"ip": "127.0.0.1"}
    )
    
    print("✅ Manual logging completed. Check data/logs/")


# ==================== مثال 2: استفاده از Decorator ====================

@log_function_call(log_args=True, log_result=True)
def decorated_function(x, y):
    """این تابع به طور خودکار لاگ می‌شود."""
    return x + y


@log_user_action("calculation")
def user_calculation(a, b):
    """اقدام کاربر با decorator."""
    result = a * b
    print(f"Result: {result}")
    return result


# ==================== مثال 3: Async Function ====================

@log_async_function_call(log_args=True)
async def async_operation(delay: float):
    """عملیات async با لاگ خودکار."""
    await asyncio.sleep(delay)
    return f"Completed after {delay}s"


# ==================== مثال 4: Context Manager ====================

def context_example():
    """استفاده از LogContext."""
    with LogContext("batch_processing", {"batch_size": 100}):
        # کد شما اینجا
        for i in range(5):
            print(f"Processing item {i}")
        
        # شبیه‌سازی خطا (optional)
        # raise ValueError("Test error in context")
    
    print("✅ Context logging completed")


# ==================== مثال 5: Exception Logging ====================

def exception_example():
    """مثال لاگ کردن استثنا."""
    logger = get_advanced_logger()
    
    try:
        # شبیه‌سازی خطا
        result = 10 / 0
    except Exception as e:
        logger.log_exception(e, "Division by zero error", {
            "operation": "10 / 0"
        })
        print("✅ Exception logged")


# ==================== مثال 6: Performance Logging ====================

def performance_example():
    """مثال لاگ عملکرد."""
    import time
    logger = get_advanced_logger()
    
    start = time.time()
    
    # عملیات شما
    time.sleep(0.5)
    
    duration = time.time() - start
    logger.log_performance(
        "sleep_operation",
        duration,
        {"expected": 0.5, "actual": duration}
    )
    
    print(f"✅ Performance logged: {duration:.3f}s")


# ==================== Main ====================

def main():
    """تابع اصلی."""
    print("=" * 60)
    print("🚀 Advanced Logging System - Examples")
    print("=" * 60)
    
    try:
        # مثال 1: لاگ دستی
        print("\n1️⃣ Manual Logging:")
        manual_logging_example()
        
        # مثال 2: Decorator
        print("\n2️⃣ Decorated Functions:")
        result = decorated_function(5, 3)
        print(f"   5 + 3 = {result}")
        user_calculation(4, 7)
        
        # مثال 3: Async
        print("\n3️⃣ Async Functions:")
        asyncio.run(async_operation(0.2))
        print("   Async operation completed")
        
        # مثال 4: Context
        print("\n4️⃣ Context Manager:")
        context_example()
        
        # مثال 5: Exception
        print("\n5️⃣ Exception Logging:")
        exception_example()
        
        # مثال 6: Performance
        print("\n6️⃣ Performance Logging:")
        performance_example()
        
        # نمایش آمار
        print("\n" + "=" * 60)
        logger = get_advanced_logger()
        stats = logger.get_stats()
        print("📊 Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # تولید گزارش
        print("\n" + "=" * 60)
        report = logger.generate_error_report()
        if report:
            print(f"📄 Error report: {report}")
        
        print("\n✅ All examples completed!")
        print(f"📁 Check logs in: data/logs/")
        print(f"   - full_trace.jsonl (همه چیز)")
        print(f"   - errors.log (خطاها)")
        print(f"   - user_actions.jsonl (اقدامات کاربر)")
        print(f"   - session_*.jsonl (این session)")
    
    finally:
        # بستن لاگر
        close_advanced_logger()
        print("\n👋 Logging system closed")


if __name__ == "__main__":
    main()
