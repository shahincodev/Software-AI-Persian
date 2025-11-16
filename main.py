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
from core.memory_system import MemoryManager
from core.task_engine import TaskEngine
from core.voice_io import VoiceManager
from dotenv import load_dotenv
from core.logging_config import setup_logging, install_exception_hook

colorama_init(autoreset=True) # در ویندوز، فعال کردن مدیریت ANSI
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
        logger.error(f"Khata dar Namayeshe Banner: {str(e)}")
        print(color + str(text) + Style.RESET_ALL)

async def process_user_input(task_engine: TaskEngine, memory: MemoryManager, mode: str, input_mode: str, voice: VoiceManager) -> None:
    """پردازش ورودی کاربر در یک حلقه تعاملی بهبود یافته با پشتیبانی از چندزبانگی."""

    print_banner(banner, color=Fore.CYAN)
    welcome_message = "Hello! Welcome to the Artificial Intelligence System."
    current_lang = "en"  # زبان پیش‌فرض
    if input_mode == "voice":
        voice.speak(welcome_message, lang=current_lang, block=True)
    
    print(f"\n{welcome_message}")
    print("Please enter your tasks. Type 'run' or 'start' to execute them. Use Ctrl+C to exit.\n")

    try:
        while True:
            user_text = ""
            if input_mode == "voice":
                print("Listening for a new task...")
                user_text, detected_lang = voice.listen(timeout=10)
                if user_text and detected_lang:
                    current_lang = detected_lang
                else:
                    print("No voice input detected. Say 'run' to start tasks or add a new one.")
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
            else:
                # افزودن تسک جدید
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

        # راه‌اندازی اجزای اصلی
        task_engine = TaskEngine(concurrency=args.concurrency)
        memory = MemoryManager()
        voice = VoiceManager(tts_provider=args.tts_provider)

        # پردازش ورودی کاربر و اجرای تسک‌ها
        await process_user_input(task_engine, memory, args.mode, args.input_mode, voice)

    except Exception as e:
        logger.exception("Khataaye mohalek rokh daad")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
