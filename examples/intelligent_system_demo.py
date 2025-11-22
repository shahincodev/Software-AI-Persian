#!/usr/bin/env python3
# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""نمایش قابلیت‌های عامل هوشمند سیستم با AI.

این مثال نشان می‌دهد چگونه سیستم می‌تواند درخواست‌های طبیعی کاربر را
به صورت هوشمند تفسیر و اجرا کند.
"""

import asyncio
import logging
from pathlib import Path
import sys

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.intelligent_agent import IntelligentSystemAgent
from core.logging_config import setup_logging


async def demo_natural_language_requests():
    """نمایش درخواست‌های طبیعی."""
    print("=" * 70)
    print("🤖 نمایش عامل هوشمند سیستم با AI")
    print("=" * 70)
    print("\nدر این دمو، درخواست‌های طبیعی به صورت خودکار به اقدامات سیستمی")
    print("تبدیل می‌شوند، بدون نیاز به دستورات دستی!\n")
    
    # ایجاد عامل (با dry_run=True برای امنیت)
    agent = IntelligentSystemAgent(dry_run=True)
    
    # درخواست‌های نمونه
    test_requests = [
        "باز کردن Notepad",
        "open calculator",
        "نصب Git از طریق winget",
        "show me CPU and memory information",
        "بستن همه پروسه‌های Chrome",
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'─' * 70}")
        print(f"📝 درخواست {i}: {request}")
        print('─' * 70)
        
        try:
            result = await agent.process_request(request)
            print(f"\n{result}")
        except Exception as e:
            print(f"❌ خطا: {e}")
            logging.exception("Request failed")
        
        # فاصله بین درخواست‌ها
        await asyncio.sleep(1)
    
    print("\n" + "=" * 70)
    print("✅ تمام درخواست‌ها پردازش شدند")
    print("=" * 70)


async def demo_mixed_scenario():
    """سناریوی ترکیبی: نصب و اجرا."""
    print("\n\n" + "=" * 70)
    print("🎯 سناریوی ترکیبی: نصب و اجرای برنامه")
    print("=" * 70)
    
    agent = IntelligentSystemAgent(dry_run=True)
    
    scenario = """
    من می‌خوام Python 3.11 رو نصب کنم،
    بعدش Visual Studio Code رو باز کنم،
    و در آخر مشخصات سیستمم رو ببینم
    """
    
    print(f"\n📋 سناریو:\n{scenario}")
    print("\n" + "─" * 70)
    
    result = await agent.process_request(scenario)
    print(f"\n{result}")


async def demo_hardware_query():
    """نمایش سوالات سخت‌افزاری."""
    print("\n\n" + "=" * 70)
    print("💻 نمایش سوالات سخت‌افزاری")
    print("=" * 70)
    
    agent = IntelligentSystemAgent(dry_run=False)  # این یکی واقعاً اجرا می‌شود
    
    queries = [
        "چقدر RAM دارم؟",
        "What's my CPU usage?",
        "Show all running processes",
    ]
    
    for query in queries:
        print(f"\n❓ {query}")
        print("─" * 70)
        
        result = await agent.process_request(query)
        print(f"\n{result}")
        
        await asyncio.sleep(1)


async def demo_system_summary():
    """نمایش خلاصه سیستم."""
    print("\n\n" + "=" * 70)
    print("📊 خلاصه وضعیت سیستم")
    print("=" * 70)
    
    agent = IntelligentSystemAgent()
    summary = agent.get_system_summary()
    
    print(f"\n{summary}")


async def main():
    """اجرای همه نمایش‌ها."""
    # راه‌اندازی لاگ
    setup_logging(level=logging.INFO)
    
    try:
        # نمایش ۱: درخواست‌های طبیعی
        await demo_natural_language_requests()
        
        # نمایش ۲: سناریوی ترکیبی
        await demo_mixed_scenario()
        
        # نمایش ۳: سوالات سخت‌افزاری (واقعی)
        await demo_hardware_query()
        
        # نمایش ۴: خلاصه سیستم
        await demo_system_summary()
        
        print("\n\n" + "=" * 70)
        print("🎉 تمام نمایش‌ها با موفقیت اجرا شدند!")
        print("=" * 70)
        print("\n💡 نکات مهم:")
        print("  • درخواست‌ها به صورت طبیعی (فارسی/انگلیسی) نوشته می‌شوند")
        print("  • AI خودش تشخیص می‌دهد چه اقدامی لازم است")
        print("  • فیلتر امنیتی قبل از هر اجرا بررسی می‌کند")
        print("  • در حالت dry_run، هیچ تغییری اعمال نمی‌شود")
        print("\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  توقف توسط کاربر")
    except Exception as e:
        print(f"\n\n❌ خطای کلی: {e}")
        logging.exception("Demo failed")


if __name__ == "__main__":
    asyncio.run(main())
