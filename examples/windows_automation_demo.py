# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""نمونه استفاده از سیستم اتوماسیون ویندوز.

این فایل نحوه استفاده از قابلیت‌های جدید را نمایش می‌دهد:
- ساخت و اجرای اقدامات سیستمی
- کشف قابلیت‌های سیستم
- نظارت بر منابع
- اجرای ایمن با فیلترهای امنیتی
"""

import asyncio
import logging
from pathlib import Path

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from core.system_actions import (
    LaunchAppAction,
    QueryHardwareAction,
    InstallPackageAction,
)
from core.system_capabilities import SystemCapabilityRegistry
from core.execution_manager import ExecutionManager, ExecutionPriority
from core.monitoring_service import MonitoringService
from core.safety_filter import SafetyFilter, UserConsentManager


async def demo_hardware_query():
    """نمونه: دریافت اطلاعات سخت‌افزار"""
    print("\n" + "="*60)
    print("🖥️  نمونه 1: دریافت اطلاعات سخت‌افزار")
    print("="*60)
    
    # ساخت مدیر اجرا
    manager = ExecutionManager(dry_run=False)
    
    # ساخت اقدام
    action = QueryHardwareAction(query_type="all")
    
    # ارسال به صف
    action_id = manager.submit(action, priority=ExecutionPriority.HIGH)
    print(f"✅ اقدام به صف اضافه شد: {action_id}")
    
    # اجرا
    result = await manager.execute_next()
    
    if result and result.success:
        print(f"\n✅ اطلاعات سخت‌افزار:\n{result.output}")
    else:
        print(f"\n❌ خطا: {result.error if result else 'نامشخص'}")


async def demo_launch_app():
    """نمونه: باز کردن برنامه (با تایید کاربر)"""
    print("\n" + "="*60)
    print("📝 نمونه 2: باز کردن Notepad")
    print("="*60)
    
    # ساخت مدیر اجرا با فیلتر امنیتی
    safety_filter = SafetyFilter(strict_mode=False)
    consent_manager = UserConsentManager(auto_approve_safe=False)
    manager = ExecutionManager(
        safety_filter=safety_filter,
        consent_manager=consent_manager,
        dry_run=False,
    )
    
    # ساخت اقدام
    action = LaunchAppAction(
        app_name="notepad.exe",
        require_consent=True,
    )
    
    # ارسال و اجرا
    action_id = manager.submit(action)
    print(f"✅ اقدام به صف اضافه شد: {action_id}")
    
    result = await manager.execute_next()
    
    if result and result.success:
        print(f"\n✅ موفقیت: {result.output}")
    else:
        print(f"\n❌ خطا یا لغو: {result.error if result else 'نامشخص'}")


async def demo_dry_run_install():
    """نمونه: شبیه‌سازی نصب بسته (dry-run)"""
    print("\n" + "="*60)
    print("📦 نمونه 3: شبیه‌سازی نصب بسته")
    print("="*60)
    
    # ساخت مدیر در حالت dry-run
    manager = ExecutionManager(dry_run=True)
    
    # ساخت اقدام
    action = InstallPackageAction(
        package_name="git",
        package_manager="winget",
        silent=True,
    )
    
    action_id = manager.submit(action)
    print(f"✅ اقدام به صف اضافه شد (DRY-RUN): {action_id}")
    
    result = await manager.execute_next()
    
    print(f"\n🔍 نتیجه Dry-Run: {result.output if result else 'خالی'}")


def demo_capability_discovery():
    """نمونه: کشف قابلیت‌های سیستم"""
    print("\n" + "="*60)
    print("🔍 نمونه 4: کشف قابلیت‌های سیستم")
    print("="*60)
    
    # ساخت رجیستری
    registry = SystemCapabilityRegistry()
    
    # اسکن سیستم
    print("📡 در حال اسکن سیستم...")
    registry.scan_system(force=True)
    
    # نمایش خلاصه
    print(f"\n{registry.get_summary()}")
    
    # لیست برنامه‌های کشف‌شده
    apps = registry.list_capabilities(type_filter="app")
    if apps:
        print(f"\n📱 برنامه‌های کشف‌شده ({len(apps)}):")
        for app in apps[:5]:  # فقط 5 تای اول
            print(f"  - {app.name}: {app.path}")
    
    # لیست ابزارها
    tools = registry.list_capabilities(type_filter="tool")
    if tools:
        print(f"\n🔧 ابزارها ({len(tools)}):")
        for tool in tools:
            version = f" (v{tool.version})" if tool.version else ""
            print(f"  - {tool.name}{version}")


def demo_monitoring():
    """نمونه: نظارت بر منابع سیستم"""
    print("\n" + "="*60)
    print("📊 نمونه 5: نظارت بر منابع سیستم")
    print("="*60)
    
    try:
        # ساخت سرویس نظارت
        def alert_handler(message: str):
            print(f"⚠️  ALERT: {message}")
        
        monitor = MonitoringService(
            interval_seconds=2.0,
            alert_callback=alert_handler,
        )
        
        # شروع نظارت
        print("🔄 شروع نظارت...")
        monitor.start()
        
        # نمایش وضعیت برای چند ثانیه
        import time
        for i in range(5):
            time.sleep(2)
            print(f"\n⏱️  ثانیه {(i+1)*2}:")
            print(monitor.get_summary())
        
        # نمایش میانگین
        avg = monitor.get_average_usage(last_n=5)
        print(f"\n📈 میانگین استفاده:")
        print(f"  CPU: {avg['cpu_percent']:.1f}%")
        print(f"  RAM: {avg['memory_percent']:.1f}%")
        
        # توقف
        print("\n🛑 توقف سرویس نظارت...")
        monitor.stop()
        print("✅ نظارت متوقف شد")
    
    except RuntimeError as e:
        print(f"❌ خطا: {e}")
        print("💡 نکته: psutil باید نصب باشد: pip install psutil")


async def main():
    """اجرای تمام نمونه‌ها"""
    print("\n" + "🎯"*30)
    print("🚀 نمونه‌های سیستم اتوماسیون ویندوز - Sofware-AI")
    print("🎯"*30)
    
    # 1. کشف قابلیت‌ها
    demo_capability_discovery()
    
    # 2. دریافت اطلاعات سخت‌افزار
    await demo_hardware_query()
    
    # 3. Dry-run نصب
    await demo_dry_run_install()
    
    # 4. نظارت
    demo_monitoring()
    
    # 5. باز کردن برنامه (نیاز به تایید)
    print("\n" + "="*60)
    print("⚠️  نمونه بعدی نیاز به تایید کاربر دارد")
    print("="*60)
    response = input("آیا می‌خواهید نمونه 'باز کردن Notepad' را اجرا کنید؟ (y/n): ")
    
    if response.lower() in ['y', 'yes', 'بله']:
        await demo_launch_app()
    else:
        print("⏭️  رد شد")
    
    print("\n" + "✅"*30)
    print("🎉 تمام نمونه‌ها اجرا شدند!")
    print("✅"*30)


if __name__ == "__main__":
    # اجرای async
    asyncio.run(main())
