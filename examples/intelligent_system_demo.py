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
    print("🤖 Intelligent agent display system with AI")
    print("=" * 70)
    print("\nIn this demo, natural requests are automatically routed to system actions")
    print("and converted, without the need for manual commands!\n")
    
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
        print(f"📝 Request {i}: {request}")
        print('─' * 70)
        
        try:
            result = await agent.process_request(request)
            print(f"\n{result}")
        except Exception as e:
            print(f"❌ Error: {e}")
            logging.exception("Request failed")
        
        # فاصله بین درخواست‌ها
        await asyncio.sleep(1)
    
    print("\n" + "=" * 70)
    print("✅ All requests have been processed")
    print("=" * 70)


async def demo_mixed_scenario():
    """سناریوی ترکیبی: نصب و اجرا."""
    print("\n\n" + "=" * 70)
    print("🎯 Combined scenario: installing and running the program")
    print("=" * 70)
    
    agent = IntelligentSystemAgent(dry_run=True)
    
    scenario = """
    من می‌خوام Python 3.11 رو نصب کنم،
    بعدش Visual Studio Code رو باز کنم،
    و در آخر مشخصات سیستمم رو ببینم
    """
    
    print(f"\n📋 Scenario:\n{scenario}")
    print("\n" + "─" * 70)
    
    result = await agent.process_request(scenario)
    print(f"\n{result}")


async def demo_hardware_query():
    """نمایش سوالات سخت‌افزاری."""
    print("\n\n" + "=" * 70)
    print("💻 Show Hardware Questions")
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
    print("📊 System Status Summary")
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
        print("🎉 All demos have been successfully executed!")
        print("=" * 70)
        print("\n💡 Important notes:")
        print("  • Requests are written naturally (Persian/English)")
        print("  • AI automatically determines the necessary actions")
        print("  • Security filter checks before each execution")
        print("  • In dry_run mode, no changes are made")
        print("\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n\n❌ General error: {e}")
        logging.exception("Demo failed")


if __name__ == "__main__":
    asyncio.run(main())
