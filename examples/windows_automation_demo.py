# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""نمونه استفاده از سیستم اتوماسیون ویندوز.

این فایل نحوه استفاده از قابلیت‌های جدید را نمایش می‌دهد:
- ساخت و اجرای اقدامات سیستمی
- کشف قابلیت‌های سیستم
- نظارت بر منابع
- اجرای ایمن با فیلترهای امنیتی
"""

import asyncio
import logging

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from core.system_actions import (  # noqa: E402
    LaunchAppAction,
    QueryHardwareAction,
    InstallPackageAction,
)
from core.system_capabilities import SystemCapabilityRegistry  # noqa: E402
from core.execution_manager import ExecutionManager, ExecutionPriority  # noqa: E402
from core.monitoring_service import MonitoringService  # noqa: E402
from core.safety_filter import SafetyFilter, UserConsentManager  # noqa: E402


async def demo_hardware_query():
    """نمونه: دریافت اطلاعات سخت‌افزار"""
    print("\n" + "="*60)
    print("🖥️ Example 1: Getting hardware information")
    print("="*60)
    
    # ساخت مدیر اجرا
    manager = ExecutionManager(dry_run=False)
    
    # ساخت اقدام
    action = QueryHardwareAction(query_type="all")
    
    # ارسال به صف
    action_id = manager.submit(action, priority=ExecutionPriority.HIGH)
    print(f"✅ Action added to queue: {action_id}")
    
    # اجرا
    result = await manager.execute_next()
    
    if result and result.success:
        print(f"\n✅ Hardware information:\n{result.output}")
    else:
        print(f"\n❌ Error: {result.error if result else 'Unknown'}")


async def demo_launch_app():
    """نمونه: باز کردن برنامه (با تایید کاربر)"""
    print("\n" + "="*60)
    print("📝 Example 2: Launching Notepad")
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
    print(f"✅ Action added to queue: {action_id}")
    
    result = await manager.execute_next()
    
    if result and result.success:
        print(f"\n✅ Success: {result.output}")
    else:
        print(f"\n❌ Error or Cancelled: {result.error if result else 'Unknown'}")


async def demo_dry_run_install():
    """نمونه: شبیه‌سازی نصب بسته (dry-run)"""
    print("\n" + "="*60)
    print("📦 Example 3: Dry-run package installation")
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
    print(f"✅ Action added to queue (DRY-RUN): {action_id}")
    
    result = await manager.execute_next()
    
    print(f"\n🔍 Dry-Run result: {result.output if result else 'Empty'}")

def demo_capability_discovery():
    """نمونه: کشف قابلیت‌های سیستم"""
    print("\n" + "="*60)
    print("🔍 Example 4: Discovering System Capabilities")
    print("="*60)
    
    # ساخت رجیستری
    registry = SystemCapabilityRegistry()
    
    # اسکن سیستم
    print("📡 Scanning system...")
    registry.scan_system(force=True)
    
    # نمایش خلاصه
    print(f"\n{registry.get_summary()}")
    
    # لیست برنامه‌های کشف‌شده
    apps = registry.list_capabilities(type_filter="app")
    if apps:
        print(f"\n📱 Discovered apps ({len(apps)}):")
        for app in apps[:5]:  # فقط 5 تای اول
            print(f"  - {app.name}: {app.path}")
    
    # لیست ابزارها
    tools = registry.list_capabilities(type_filter="tool")
    if tools:
        print(f"\n🔧 Discovered tools ({len(tools)}):")
        for tool in tools:
            version = f" (v{tool.version})" if tool.version else ""
            print(f"  - {tool.name}{version}")


def demo_monitoring():
    """نمونه: نظارت بر منابع سیستم"""
    print("\n" + "="*60)
    print("📊 Example 5: Monitoring System Resources")
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
        print("🔄 Start monitoring...")
        monitor.start()
        
        # نمایش وضعیت برای چند ثانیه
        import time
        for i in range(5):
            time.sleep(2)
            print(f"\n⏱️ seconds {(i+1)*2}:")
            print(monitor.get_summary())
        
        # نمایش میانگین
        avg = monitor.get_average_usage(last_n=5)
        print("\n📈 Average usage:")
        print(f"  CPU: {avg['cpu_percent']:.1f}%")
        print(f"  RAM: {avg['memory_percent']:.1f}%")
        
        # توقف
        print("\n🛑 Stopping monitoring service...")
        monitor.stop()
        print("✅ Monitoring stopped")
    
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        print("💡 Tip: psutil must be installed: pip install psutil")


async def main():
    """اجرای تمام نمونه‌ها"""
    print("\n" + "🎯"*30)
    print("🚀 Windows Automation System Examples - Software-AI")
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
    print("⚠️ The next example requires user approval")
    print("="*60)
    response = input("Do you want to run the 'Open Notepad' sample? (y/n): ")
    
    if response.lower() in ['y', 'yes', 'بله']:
        await demo_launch_app()
    else:
        print("⏭️  Skipped")
    
    print("\n" + "✅"*30)
    print("🎉 All examples have been executed!")
    print("✅"*30)


if __name__ == "__main__":
    # اجرای async
    asyncio.run(main())
