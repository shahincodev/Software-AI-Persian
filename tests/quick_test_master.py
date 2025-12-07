"""
🎯 تست سریع Master AI Controller
===================================

این فایل یک تست سریع و ساده از Master Controller انجام می‌دهد.
مناسب برای چک کردن سریع عملکرد سیستم.

استفاده:
    python tests/quick_test_master.py
"""

import asyncio
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.master_controller import MasterAIController, ToolType
from core.intelligent_agent import IntelligentSystemAgent


def print_header(text: str):
    """چاپ هدر زیبا"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_result(test_name: str, request: str, result):
    """چاپ نتیجه تست"""
    print(f"🧪 تست: {test_name}")
    print(f"   👤 درخواست: \"{request}\"")
    print(f"   🔧 ابزار: {result.tool_used.value}")
    print(f"   ✅ موفقیت: {'بله' if result.success else 'خیر'}")
    print(f"   💬 پاسخ: {result.human_response}\n")
    print(f"   {'-'*60}\n")


async def quick_test():
    """تست سریع"""
    print_header("🚀 Master AI Controller - تست سریع")
    
    # مقداردهی اولیه
    print("⚙️  در حال مقداردهی اولیه...\n")
    system_agent = IntelligentSystemAgent()
    master = MasterAIController(system_agent=system_agent)
    print("✅ آماده!\n")
    
    # تست‌های اصلی
    tests = [
        ("گفتگو ساده", "سلام، حالت چطوره؟", ToolType.CHAT),
        ("اطلاعات CPU", "CPU چقدره؟", ToolType.SYSTEM),
        ("باز کردن برنامه", "باز کن notepad", ToolType.DESKTOP),
        ("سوال AI", "هوش مصنوعی چیست؟", ToolType.CHAT),
        ("حافظه سیستم", "چقدر RAM دارم؟", ToolType.SYSTEM),
    ]
    
    print_header("📋 اجرای تست‌ها")
    
    passed = 0
    failed = 0
    
    for test_name, request, expected_tool in tests:
        try:
            result = await master.process_request(request)
            print_result(test_name, request, result)
            
            if result.tool_used == expected_tool:
                passed += 1
            else:
                failed += 1
                print(f"   ⚠️  انتظار: {expected_tool.value}, دریافت: {result.tool_used.value}\n")
        
        except Exception as e:
            failed += 1
            print(f"   ❌ خطا: {e}\n")
        
        # کمی صبر کنیم
        await asyncio.sleep(0.5)
    
    # نتیجه نهایی
    print_header("📊 نتیجه")
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ موفق: {passed}/{total}")
    print(f"❌ ناموفق: {failed}/{total}")
    print(f"📈 درصد موفقیت: {success_rate:.1f}%\n")
    
    if success_rate >= 80:
        print("🎉 عالی! Master Controller به خوبی کار می‌کند!\n")
    elif success_rate >= 60:
        print("⚠️  قابل قبول، اما نیاز به بهبود دارد.\n")
    else:
        print("❌ مشکلاتی وجود دارد. لطفاً API keys و تنظیمات را بررسی کنید.\n")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       🧠 Master AI Controller - Quick Test 🧪           ║
    ║                                                          ║
    ║       این تست چند دستور ساده را بررسی می‌کند          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(quick_test())
    except KeyboardInterrupt:
        print("\n\n⚠️  تست توسط کاربر متوقف شد.\n")
    except Exception as e:
        print(f"\n\n❌ خطا: {e}\n")
        sys.exit(1)
