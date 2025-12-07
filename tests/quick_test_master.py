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
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

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
    print(f"🧪 Test: {test_name}")
    print(f"   👤 Request: \"{request}\"")
    print(f"   🔧 Tool: {result.tool_used.value}")
    print(f"   ✅ Success: {'Yes' if result.success else 'No'}")
    print(f"   💬 Response: {result.human_response}\n")
    print(f"   {'-'*60}\n")


async def quick_test():
    """تست سریع"""
    print_header("🚀 Master AI Controller - Quick Test")
    
    # مقداردهی اولیه
    print("⚙️  Initializing...\n")
    system_agent = IntelligentSystemAgent()
    master = MasterAIController(system_agent=system_agent)
    print("✅ Ready!\n")
    
    # تست‌های اصلی
    tests = [
        ("گفتگو ساده", "سلام، حالت چطوره؟", ToolType.CHAT),
        ("اطلاعات CPU", "CPU چقدره؟", ToolType.SYSTEM),
        ("باز کردن برنامه", "باز کن notepad", ToolType.DESKTOP),
        ("سوال AI", "هوش مصنوعی چیست؟", ToolType.CHAT),
        ("حافظه سیستم", "چقدر RAM دارم؟", ToolType.SYSTEM),
    ]
    
    print_header("📋 Running Tests")
    
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
                print(f"   ⚠️  Expected: {expected_tool.value}, Got: {result.tool_used.value}\n")
        
        except Exception as e:
            failed += 1
            print(f"   ❌ Error: {e}\n")
        
        # کمی صبر کنیم
        await asyncio.sleep(0.5)
    
    # نتیجه نهایی
    print_header("📊 Results")
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print(f"📈 Success Rate: {success_rate:.1f}%\n")
    
    if success_rate >= 80:
        print("🎉 Excellent! Master Controller is working great!\n")
    elif success_rate >= 60:
        print("⚠️  Acceptable, but needs improvement.\n")
    else:
        print("❌ Issues detected. Please check API keys and settings.\n")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       🧠 Master AI Controller - Quick Test 🧪           ║
    ║                                                          ║
    ║       This test checks basic functionality              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(quick_test())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        sys.exit(1)
