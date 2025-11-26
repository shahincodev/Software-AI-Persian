#!/usr/bin/env python3
# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""
نقطه ورودی اصلی سیستم نرم‌افزاری هوش مصنوعی.
این ماژول یک رابط خط فرمان (CLI) برای تعامل با قابلیت‌های اصلی سیستم فراهم می‌کند.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import shutil
import sys
from pathlib import Path
from typing import Optional
from pyfiglet import Figlet
from colorama import init as colorama_init, Fore, Style


from core.agent_core import create_agent
from core.intelligent_agent import IntelligentSystemAgent
from core.memory_system import MemoryManager
from core.task_engine import TaskEngine
from core.voice_io import VoiceManager
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController
from core.smart_wait import SmartWaiter
from dotenv import load_dotenv
from core.logging_config import setup_logging, install_exception_hook

colorama_init(autoreset=True) # در ویندوز، فعال کردن مدیریت ANSI

logger = logging.getLogger(__name__)


async def _is_system_request(user_text: str, system_agent: IntelligentSystemAgent) -> bool:
    """تشخیص هوشمند آیا درخواست کاربر مربوط به سیستم است یا نه.
    
    Args:
        user_text: متن درخواست کاربر
        system_agent: عامل سیستم برای دسترسی به AIBrain
    
    Returns:
        True اگر درخواست سیستمی باشد
    """
    # کلمات کلیدی سیستمی (فارسی و انگلیسی)
    system_keywords = [
        # Actions
        "open", "launch", "start", "run", "باز", "اجرا", "شروع",
        "install", "نصب", "setup",
        "close", "kill", "terminate", "stop", "بستن", "توقف",
        "hardware", "سخت‌افزار", "cpu", "ram", "memory", "disk", "gpu",
        # Apps
        "notepad", "calculator", "chrome", "firefox", "edge",
        "photoshop", "فتوشاپ", "word", "excel", "powerpoint",
        "vscode", "visual studio", "برنامه",
        # System operations
        "process", "فرآیند", "task manager", "مدیریت", "system", "سیستم"
    ]
    
    user_lower = user_text.lower()
    
    # چک سریع با کلمات کلیدی
    for keyword in system_keywords:
        if keyword in user_lower:
            return True
    
    return False


def _summarize_for_voice(result_text: str) -> str:
    """خلاصه‌سازی پاسخ طولانی برای خروجی صوتی.
    
    Args:
        result_text: متن کامل نتیجه
    
    Returns:
        خلاصه مناسب برای گفتار
    """
    # اگر خیلی کوتاه است، همان را برگردان
    if len(result_text) < 150:
        return result_text
    
    # استخراج خط اول که معمولاً خلاصه است
    lines = result_text.split('\n')
    first_meaningful_line = ""
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('```'):
            first_meaningful_line = line
            break
    
    if first_meaningful_line:
        return first_meaningful_line
    
    # اگر نتوانستیم، ۱۵۰ کاراکتر اول
    return result_text[:150] + "..."


async def handle_mouse_command(
    command: str,
    mouse: MouseController,
    voice: VoiceManager,
    lang: str,
    input_mode: str
) -> None:
    """پردازش دستورات موس."""
    try:
        cmd_lower = command.lower()
        
        if "position" in cmd_lower or "موقعیت" in cmd_lower:
            x, y = mouse.get_position()
            msg = f"🖱️ Mouse position: ({x}, {y})"
            print(msg)
            if input_mode == "voice":
                voice.speak(f"Mouse is at position {x}, {y}", lang=lang)
        
        elif "click" in cmd_lower or "کلیک" in cmd_lower:
            x, y = mouse.get_position()
            mouse.click(x, y)
            msg = f"🖱️ Clicked at ({x}, {y})"
            print(msg)
            if input_mode == "voice":
                voice.speak("Click executed", lang=lang)
        
        else:
            msg = "❓ Unknown mouse command. Try: 'mouse position' or 'mouse click'"
            print(msg)
            if input_mode == "voice":
                voice.speak("Unknown mouse command", lang=lang)
    
    except Exception as e:
        error_msg = f"❌ Mouse error: {e}"
        print(error_msg)
        logger.exception("Mouse command failed")


async def handle_keyboard_command(
    command: str,
    keyboard: KeyboardController,
    voice: VoiceManager,
    lang: str,
    input_mode: str
) -> None:
    """پردازش دستورات کیبورد."""
    try:
        # استخراج متن برای تایپ
        if "type" in command.lower() or "تایپ" in command:
            # استخراج متن بعد از "type"
            text_to_type = command.split(maxsplit=1)[1] if len(command.split()) > 1 else ""
            
            if text_to_type:
                msg = f"⌨️ Typing in 3 seconds: {text_to_type}"
                print(msg)
                if input_mode == "voice":
                    voice.speak("Typing in 3 seconds", lang=lang)
                
                await asyncio.sleep(3)
                keyboard.type_text(text_to_type)
                
                success_msg = "✅ Text typed successfully"
                print(success_msg)
                if input_mode == "voice":
                    voice.speak("Text typed", lang=lang)
            else:
                print("❓ Usage: type <your text here>")
        
        elif "hotkey" in command.lower() or "میانبر" in command:
            msg = "⌨️ Example: Ctrl+C executed"
            print(msg)
            keyboard.hotkey('ctrl', 'c')
            if input_mode == "voice":
                voice.speak("Hotkey executed", lang=lang)
        
        else:
            msg = "❓ Unknown keyboard command. Try: 'type <text>' or 'hotkey'"
            print(msg)
    
    except Exception as e:
        error_msg = f"❌ Keyboard error: {e}"
        print(error_msg)
        logger.exception("Keyboard command failed")


async def handle_wait_command(
    command: str,
    smart_wait: SmartWaiter,
    voice: VoiceManager,
    lang: str,
    input_mode: str
) -> None:
    """پردازش دستورات انتظار هوشمند."""
    try:
        cmd_lower = command.lower()
        
        if "idle" in cmd_lower or "بیکار" in cmd_lower:
            msg = "⏳ Waiting for system to be idle..."
            print(msg)
            if input_mode == "voice":
                voice.speak("Waiting for idle", lang=lang)
            
            result = smart_wait.wait_for_idle(cpu_threshold=10.0, timeout=30)
            
            if result.success:
                success_msg = f"✅ System is idle (waited {result.duration:.1f}s)"
                print(success_msg)
                if input_mode == "voice":
                    voice.speak("System is now idle", lang=lang)
            else:
                timeout_msg = f"⏱️ Timeout waiting for idle"
                print(timeout_msg)
        
        elif "window" in cmd_lower or "پنجره" in cmd_lower:
            # استخراج نام پنجره
            window_name = command.split(maxsplit=1)[1] if len(command.split()) > 1 else "Notepad"
            
            msg = f"⏳ Waiting for window: {window_name}"
            print(msg)
            if input_mode == "voice":
                voice.speak(f"Waiting for {window_name}", lang=lang)
            
            result = smart_wait.wait_for_window(window_name, timeout=30)
            
            if result.success:
                success_msg = f"✅ Window found: {window_name}"
                print(success_msg)
                if input_mode == "voice":
                    voice.speak("Window found", lang=lang)
            else:
                timeout_msg = f"⏱️ Timeout: {window_name} not found"
                print(timeout_msg)
        
        else:
            msg = "❓ Unknown wait command. Try: 'wait idle' or 'wait window <name>'"
            print(msg)
    
    except Exception as e:
        error_msg = f"❌ Wait error: {e}"
        print(error_msg)
        logger.exception("Wait command failed")


with open('banner.txt', 'r', encoding='utf-8') as file:
    banner = file.read()

# پیکربندی ثبت وقایع در هنگام راه‌اندازی اولیه تنظیم می‌شود (به `setup_logging` مراجعه کنید)
logger = logging.getLogger(__name__)

def setup_environment() -> None:
    """مقداردهی اولیه متغیرهای محیطی و ایجاد پوشه‌های مورد نیاز."""
    # بارگذاری متغیرهای محیطی از فایل .env
    load_dotenv()
    
    # اطمینان از وجود پوشه‌های مورد نیاز
    for dir_path in ["data/logs", "data/logs/cache"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def parse_arguments() -> argparse.Namespace:
    """تجزیه و تحلیل آرگومان‌های خط فرمان."""
    parser = argparse.ArgumentParser(
        description="سیستم نرم‌افزاری هوش مصنوعی - پردازش هوشمند تسک‌ها",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--mode",
        choices=["browser", "code"],
        default="browser",
        help="حالت عملیات: 'browser' برای تعامل با وب، 'code' برای تحلیل کد"
    )
    
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="تعداد تسک‌های همزمان قابل اجرا (پیش‌فرض: 3)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="فعال‌سازی لاگ‌های دیباگ"
    )
    parser.add_argument(
        "--input-mode",
        choices=["text", "voice"],
        default="voice",
        help="انتخاب نوع ورودی: 'text' برای کیبورد، 'voice' برای میکروفون"
    )
    parser.add_argument(
        "--tts-provider",
        choices=["google-cloud", "gtts", "elevenlabs"],
        default="gtts",
        help="انتخاب سرویس تبدیل متن به گفتار: 'google-cloud' (پولی، کیفیت بالا)، 'gtts' (رایگان) یا 'elevenlabs' (پولی، کیفیت بالا)"
    )
    parser.add_argument(
        "--enable-automation",
        action="store_true",
        help="فعال‌سازی قابلیت‌های خودکارسازی دسکتاپ (Mouse, Keyboard, Smart Wait)"
    )
    parser.add_argument(
        "--demo-gui",
        action="store_true",
        help="اجرای رابط کاربری گرافیکی نمایشی"
    )

    return parser.parse_args()

def print_banner(text=banner, color=Fore.CYAN) -> None:
    """چاپ بنر خوش‌آمدگویی در CLI."""
    term_width = shutil.get_terminal_size((80, 20)).columns
    
    try:
        # اگر متن از قبل ASCII art است، مستقیماً آن را نمایش می‌دهیم
        lines = str(text).splitlines()
        for line in lines:
            # محاسبه فاصله لازم برای مرکز قرار دادن متن
            padding = (term_width - len(line)) // 2
            if padding > 0:
                print(color + " " * padding + line + Style.RESET_ALL)
            else:
                print(color + line + Style.RESET_ALL)
    except Exception as e:
        logger.error(F"Error displaying banner: {str(e)}")
        print(color + str(text) + Style.RESET_ALL)

async def process_user_input(
    task_engine: TaskEngine, 
    memory: MemoryManager, 
    mode: str, 
    input_mode: str, 
    voice: VoiceManager, 
    system_agent: IntelligentSystemAgent,
    mouse: Optional[MouseController] = None,
    keyboard: Optional[KeyboardController] = None,
    smart_wait: Optional[SmartWaiter] = None
) -> None:
    """پردازش ورودی کاربر در یک حلقه تعاملی بهبود یافته با پشتیبانی از چندزبانگی و خودکارسازی."""

    print_banner(banner, color=Fore.CYAN)
    welcome_message = "Hello! Welcome to the Artificial Intelligence System."
    current_lang = "en"  # زبان پیش‌فرض
    if input_mode == "voice":
        voice.speak(welcome_message, lang=current_lang, block=True)
    
    print(f"\n{welcome_message}")
    print("Please enter your tasks. ask or Type 'start' to execute them. Use Ctrl+C to exit.\n")
    
    # نمایش وضعیت خودکارسازی
    if mouse or keyboard or smart_wait:
        automation_status = f"{Fore.GREEN}🤖 Desktop Automation: ENABLED{Style.RESET_ALL}"
        print(automation_status)
        automation_features = []
        if mouse:
            automation_features.append("Mouse Control")
        if keyboard:
            automation_features.append("Keyboard Control")
        if smart_wait:
            automation_features.append("Smart Wait")
        print(f"   Features: {', '.join(automation_features)}\n")

    try:
        while True:
            user_text = ""
            if input_mode == "voice":
                print("Listening for a new task...")
                user_text, detected_lang = voice.listen(timeout=10)
                if user_text and detected_lang:
                    current_lang = detected_lang
                else:
                    print("No voice input detected. Say 'start' to start tasks or add a new one.")
                    continue
            else:
                user_text = input("New Task (or 'run' to start) > ").strip()
                # برای ورودی متنی، زبان را انگلیسی فرض می‌کنیم
                current_lang = "en"

            if not user_text:
                continue

            # کلمات کلیدی برای اجرا یا خروج
            if user_text.lower() in ["run", "start", "اجرا کن"]:
                if not task_engine.queue:
                    message = "No tasks to run. Please add tasks first."
                    print(message)
                    if input_mode == "voice":
                        voice.speak(message, lang=current_lang)
                    continue
                
                # اجرای تسک‌ها
                exec_message = "Executing tasks..."
                print(f"\n{exec_message}")
                if input_mode == "voice":
                    voice.speak(exec_message, lang=current_lang)

                tasks_list = list(task_engine.queue)
                results = await task_engine.run_all()

                # پردازش و ذخیره نتایج
                for (task_text, task_mode), result in zip(tasks_list, results):
                    if result:
                        memory.remember_long(
                            content=result,
                            metadata={"type": "task_result", "original_task": task_text, "mode": task_mode}
                        )
                        result_message = f"Task Result: {result}"
                        print(f"\n{result_message}\n")
                        if input_mode == "voice":
                            voice.speak(f"The task is complete. The result is: {result}", lang=current_lang, block=True)
                    else:
                        error_message = f"Task '{task_text}' failed or had no result."
                        print(f"\n{error_message}\n")
                        if input_mode == "voice":
                            voice.speak(error_message, lang=current_lang, block=True)
                
                task_engine.queue.clear()
                print("\nAll tasks processed. You can add new tasks or exit.")

            elif user_text.lower() in ["exit", "quit", "خروج"]:
                break
            
            # دستورات خودکارسازی
            elif user_text.lower().startswith(("mouse", "موس")) and mouse:
                await handle_mouse_command(user_text, mouse, voice, current_lang, input_mode)
                continue
            
            elif user_text.lower().startswith(("type", "تایپ", "keyboard", "کیبورد")) and keyboard:
                await handle_keyboard_command(user_text, keyboard, voice, current_lang, input_mode)
                continue
            
            elif user_text.lower().startswith(("wait", "صبر", "انتظار")) and smart_wait:
                await handle_wait_command(user_text, smart_wait, voice, current_lang, input_mode)
                continue
            
            else:
                # تشخیص هوشمند: آیا این یک درخواست سیستمی است؟
                is_system_task = await _is_system_request(user_text, system_agent)
                
                if is_system_task:
                    # پردازش مستقیم با عامل سیستم
                    processing_msg = "Processing system request with AI..."
                    print(f"\n🤖 {processing_msg}")
                    if input_mode == "voice":
                        voice.speak("Processing your system request.", lang=current_lang)
                    
                    try:
                        # اجرای هوشمند با AI
                        system_result = await system_agent.process_request(user_text)
                        
                        # ذخیره در حافظه
                        memory.remember_long(
                            content=system_result,
                            metadata={"type": "system_result", "original_request": user_text}
                        )
                        
                        # نمایش نتیجه
                        print(f"\n{system_result}\n")
                        if input_mode == "voice":
                            # خلاصه‌سازی پاسخ برای صدا
                            summary = _summarize_for_voice(system_result)
                            voice.speak(summary, lang=current_lang, block=True)
                    
                    except Exception as e:
                        error_msg = f"Error executing system task: {str(e)}"
                        print(f"\n❌ {error_msg}\n")
                        logger.exception("System task execution failed")
                        if input_mode == "voice":
                            voice.speak("Sorry, the system task failed.", lang=current_lang)
                else:
                    # تسک عادی (browser/code) - افزودن به صف
                    memory.remember_short(
                        content=user_text,
                        ttl=3600,
                        metadata={"type": "user_task", "mode": mode, "lang": current_lang}
                    )
                    task_engine.add_task(user_text, mode=mode)
                    added_message = f"Task added: {user_text}"
                    print(added_message)
                    if input_mode == "voice":
                        voice.speak(added_message, lang=current_lang)

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        memory.shutdown()
        voice.shutdown()

async def main() -> None:
    """نقطه ورود اصلی برنامه."""
    try:
        # تجزیه آرگومان‌های خط فرمان
        args = parse_arguments()

        # راه‌اندازی محیط
        setup_environment()

        # مقداردهی اولیه گزارش‌گیری پس از آماده‌سازی محیط. با توجه به پرچم --debug
        setup_logging(level=logging.DEBUG if args.debug else None)
        install_exception_hook()

        # بررسی اجرای GUI دمو
        if args.demo_gui:
            logger.info("Launching demo GUI...")
            import demo_gui
            demo_gui.main()
            return
        
        # راه‌اندازی اجزای اصلی
        task_engine = TaskEngine(concurrency=args.concurrency)
        memory = MemoryManager()
        voice = VoiceManager(tts_provider=args.tts_provider)
        
        # راه‌اندازی عامل هوشمند سیستم
        system_agent = IntelligentSystemAgent(dry_run=args.debug)
        logger.info("Intelligent system agent initialized")
        
        # راه‌اندازی قابلیت‌های خودکارسازی (Week 2)
        mouse = None
        keyboard = None
        smart_wait = None
        
        if args.enable_automation:
            try:
                mouse = MouseController()
                keyboard = KeyboardController()
                smart_wait = SmartWaiter()
                logger.info("✅ Desktop automation enabled (Mouse, Keyboard, Smart Wait)")
                print(f"{Fore.GREEN}✅ قابلیت‌های خودکارسازی دسکتاپ فعال شد{Style.RESET_ALL}")
            except Exception as e:
                logger.warning(f"Failed to initialize automation components: {e}")
                print(f"{Fore.YELLOW}⚠️ خطا در فعال‌سازی خودکارسازی: {e}{Style.RESET_ALL}")

        # پردازش ورودی کاربر و اجرای تسک‌ها
        await process_user_input(
            task_engine, 
            memory, 
            args.mode, 
            args.input_mode, 
            voice, 
            system_agent,
            mouse=mouse,
            keyboard=keyboard,
            smart_wait=smart_wait
        )

    except Exception as e:
        logger.exception("A fatal error occurred.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
