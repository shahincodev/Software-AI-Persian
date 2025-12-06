"""تست Master AI Controller"""

import asyncio
import logging
from core.master_controller import MasterAIController
from core.intelligent_agent import IntelligentSystemAgent

# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')


async def test_master_controller():
    """تست قابلیت‌های Master Controller"""
    
    print("="*70)
    print("🧪 Testing Master AI Controller")
    print("="*70)
    
    # مقداردهی اولیه
    system_agent = IntelligentSystemAgent(dry_run=False)
    master = MasterAIController(system_agent=system_agent)
    
    # تست‌های مختلف
    tests = [
        "سلام، حالت چطوره؟",  # CHAT
        "CPU چقدره؟",  # SYSTEM
        "باز کن نوت‌پد",  # DESKTOP
        "هوا امروز چطوره؟",  # BROWSER (فعلاً نمی‌تونه)
        "هوش مصنوعی چیست؟",  # CHAT
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/{len(tests)}: {test}")
        print(f"{'─'*70}")
        
        try:
            result = await master.process_request(test)
            
            print(f"\n📍 Tool: {result.tool_used.value}")
            print(f"✅ Success: {result.success}")
            print(f"\n💬 Human Response:")
            print(f"   {result.human_response}")
            
            if result.raw_output and result.tool_used.value == "system":
                print(f"\n🔧 Raw Output:")
                import json
                print(f"   {json.dumps(result.raw_output, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("✅ All tests completed!")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(test_master_controller())
