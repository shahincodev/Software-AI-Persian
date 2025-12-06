# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""نمایش قابلیت‌های Autonomous Agent - Vision-Based Windows Control

این دمو نشون میده چطور Agent می‌تونه با پرامپت‌های ساده کار کنه،
مثل browser-use اما برای Windows!

مثال‌ها:
    1. "برو This PC باز کن E:" 
    2. "فولدر MyDocs بساز توی E:"
    3. "نوت‌پد باز کن بنویس سلام ذخیره کن"
"""

import asyncio
import logging
import sys
from pathlib import Path

# اضافه کردن root به path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.autonomous_agent import AutonomousAgent
from core.logging_config import setup_logging

# تنظیم logging
setup_logging()
logger = logging.getLogger(__name__)


async def demo_simple_tasks():
    """دمو کارهای ساده."""
    print("\n" + "="*60)
    print("🎯 Demo 1: Simple Tasks (کارهای ساده)")
    print("="*60 + "\n")
    
    agent = AutonomousAgent()
    
    # تست 1: باز کردن نوت‌پد
    print("\n📝 Test 1: Open Notepad")
    print("-" * 40)
    result = await agent.execute_goal("Open Notepad")
    print(f"✅ Result: {result['success']}")
    if result['success']:
        for step in result['steps']:
            print(f"  Step {step['number']}: {step['description']} → {step['result']}")
    
    await asyncio.sleep(2)
    
    # تست 2: تایپ متن
    print("\n📝 Test 2: Type text in Notepad")
    print("-" * 40)
    result = await agent.execute_goal("Type 'Hello from Autonomous Agent!' in the active window")
    print(f"✅ Result: {result['success']}")
    
    await asyncio.sleep(2)


async def demo_file_explorer():
    """دمو کار با File Explorer."""
    print("\n" + "="*60)
    print("🗂️ Demo 2: File Explorer Navigation")
    print("="*60 + "\n")
    
    agent = AutonomousAgent()
    
    # تست: باز کردن This PC و رفتن به E:
    print("\n📂 Opening This PC and navigating to E: drive")
    print("-" * 40)
    
    result = await agent.execute_goal(
        "Open This PC (File Explorer) and click on E: drive"
    )
    
    print(f"✅ Result: {result['success']}")
    if result['success']:
        print(f"Completed {len(result['steps'])} steps:")
        for step in result['steps']:
            print(f"  {step['number']}. {step['description']}")
            if step['result']:
                print(f"     → {step['result']}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


async def demo_create_folder():
    """دمو ساخت فولدر."""
    print("\n" + "="*60)
    print("📁 Demo 3: Create Folder (ساخت فولدر)")
    print("="*60 + "\n")
    
    agent = AutonomousAgent()
    
    # تست: ساخت فولدر در E:
    print("\n📁 Creating folder 'MyDocs' in E: drive")
    print("-" * 40)
    
    result = await agent.execute_goal(
        "Go to E: drive and create a new folder called MyDocs"
    )
    
    print(f"✅ Result: {result['success']}")
    if result['success']:
        print(f"Completed {len(result['steps'])} steps:")
        for step in result['steps']:
            print(f"  {step['number']}. {step['description']}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


async def demo_persian_commands():
    """دمو دستورات فارسی."""
    print("\n" + "="*60)
    print("🇮🇷 Demo 4: Persian Commands (دستورات فارسی)")
    print("="*60 + "\n")
    
    agent = AutonomousAgent()
    
    # تست 1: باز کردن برنامه
    print("\n📝 تست ۱: نوت‌پد رو باز کن")
    print("-" * 40)
    result = await agent.execute_goal("نوت‌پد رو باز کن")
    print(f"✅ نتیجه: {'موفق' if result['success'] else 'ناموفق'}")
    
    await asyncio.sleep(2)
    
    # تست 2: تایپ فارسی
    print("\n📝 تست ۲: بنویس سلام دنیا")
    print("-" * 40)
    result = await agent.execute_goal("بنویس سلام دنیا")
    print(f"✅ نتیجه: {'موفق' if result['success'] else 'ناموفق'}")
    
    await asyncio.sleep(2)
    
    # تست 3: کار پیچیده
    print("\n📂 تست ۳: برو This PC باز کن E:")
    print("-" * 40)
    result = await agent.execute_goal("برو This PC باز کن E:")
    print(f"✅ نتیجه: {'موفق' if result['success'] else 'ناموفق'}")


async def demo_screen_understanding():
    """دمو فهم صفحه."""
    print("\n" + "="*60)
    print("👁️ Demo 5: Screen Understanding (فهم صفحه)")
    print("="*60 + "\n")
    
    agent = AutonomousAgent()
    
    print("\n👁️ Agent is looking at the screen...")
    print("-" * 40)
    
    description = await agent.describe_screen()
    print(f"\n🤖 Agent says: {description}")


async def demo_complex_workflow():
    """دمو workflow پیچیده."""
    print("\n" + "="*60)
    print("🚀 Demo 6: Complex Workflow (کار پیچیده)")
    print("="*60 + "\n")
    
    agent = AutonomousAgent()
    
    # تست: یه workflow کامل
    print("\n🚀 Complex task: Open Notepad, type message, save")
    print("-" * 40)
    
    workflow = """
    Open Notepad application.
    Type 'This is a test from Autonomous Agent'.
    Press Ctrl+S to save.
    Type 'test.txt' as filename.
    Press Enter to confirm.
    """
    
    result = await agent.execute_goal(workflow)
    
    print(f"✅ Result: {result['success']}")
    if result['success']:
        print(f"Completed workflow with {len(result['steps'])} steps")
    else:
        print(f"❌ Failed at step {result.get('completed_steps', 0)}")


async def interactive_mode():
    """حالت تعاملی - کاربر خودش پرامپت می‌ده."""
    print("\n" + "="*60)
    print("🎮 Interactive Mode (حالت تعاملی)")
    print("="*60)
    print("\nبهم بگو چیکار کنم! (برای خروج 'exit' بزن)\n")
    
    agent = AutonomousAgent()
    
    while True:
        try:
            # دریافت دستور
            command = input("\n🎯 Your command: ").strip()
            
            if not command:
                continue
                
            if command.lower() in ['exit', 'quit', 'خروج']:
                print("\n👋 Goodbye!")
                break
            
            # اجرا
            print(f"\n🤖 Executing: {command}")
            print("-" * 40)
            
            result = await agent.execute_goal(command)
            
            if result['success']:
                print(f"\n✅ Success! Completed {len(result['steps'])} steps:")
                for step in result['steps']:
                    print(f"  {step['number']}. {step['description']}")
            else:
                print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """اجرای تمام دموها."""
    print("\n" + "="*60)
    print("🤖 Autonomous Agent Demo")
    print("Vision-Based Windows Control - Like browser-use!")
    print("="*60)
    
    # منوی انتخاب
    print("\nChoose demo:")
    print("  1. Simple Tasks (کارهای ساده)")
    print("  2. File Explorer Navigation")
    print("  3. Create Folder (ساخت فولدر)")
    print("  4. Persian Commands (دستورات فارسی)")
    print("  5. Screen Understanding (فهم صفحه)")
    print("  6. Complex Workflow (کار پیچیده)")
    print("  7. Interactive Mode (حالت تعاملی) ⭐")
    print("  8. Run All Demos")
    print("  0. Exit")
    
    choice = input("\nYour choice: ").strip()
    
    if choice == "1":
        await demo_simple_tasks()
    elif choice == "2":
        await demo_file_explorer()
    elif choice == "3":
        await demo_create_folder()
    elif choice == "4":
        await demo_persian_commands()
    elif choice == "5":
        await demo_screen_understanding()
    elif choice == "6":
        await demo_complex_workflow()
    elif choice == "7":
        await interactive_mode()
    elif choice == "8":
        # همه دموها
        await demo_simple_tasks()
        await asyncio.sleep(3)
        await demo_file_explorer()
        await asyncio.sleep(3)
        await demo_create_folder()
        await asyncio.sleep(3)
        await demo_persian_commands()
        await asyncio.sleep(3)
        await demo_screen_understanding()
        await asyncio.sleep(3)
        await demo_complex_workflow()
    elif choice == "0":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice!")
        return
    
    print("\n" + "="*60)
    print("✅ Demo completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
