#!/usr/bin/env python3
# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست ذخیره لاگ‌ها با Kill کردن Terminal.

این اسکریپت نشان می‌دهد که لاگ‌ها حتی با Kill کردن برنامه هم ذخیره می‌شوند.
"""

import sys
import time
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.advanced_logging import get_advanced_logger, close_advanced_logger
from core.logging_decorators import log_function_call, LogContext
from colorama import init, Fore, Style

init(autoreset=True)


@log_function_call(log_args=True)
def test_operation(number: int):
    """عملیات تست که لاگ می‌شه."""
    time.sleep(0.1)
    return number * 2


def main():
    """تابع اصلی."""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 70)
    print("🧪 Test: Logging Persistence with Terminal Kill")
    print("=" * 70)
    print(Style.RESET_ALL)
    
    logger = get_advanced_logger()
    
    print(f"\n{Fore.YELLOW}📝 Instructions:{Style.RESET_ALL}")
    print("1. This program will log 30 times (every 2 seconds)")
    print("2. After a few logs, Kill the Terminal (Ctrl+C or X)")
    print("3. Then run this command:")
    print(f"   {Fore.GREEN}python tools/log_analyzer.py search 'kill_test'{Style.RESET_ALL}")
    print("4. You should see the logs - they were saved! ✅")
    print()
    
    try:
        session_id = logger.session_id
        print(f"{Fore.CYAN}Session ID: {session_id}{Style.RESET_ALL}\n")
        
        logger.log_system("Starting kill test", {
            "message": "This log persists even with Ctrl+C",
            "session": session_id
        })
        
        for i in range(1, 31):
            with LogContext(f"kill_test_iteration_{i}"):
                # لاگ شماره
                logger.log_user_action(
                    "kill_test",
                    {
                        "iteration": i,
                        "session": session_id,
                        "message": f"Test #{i} - Saved immediately!"
                    }
                )
                
                # عملیات تست
                result = test_operation(i)
                
                # نمایش پیشرفت
                print(f"{Fore.GREEN}✅ Log #{i}/30 saved{Style.RESET_ALL} "
                      f"(Result: {result}) "
                      f"{Fore.YELLOW}[You can Kill now!]{Style.RESET_ALL}")
                
                time.sleep(2)
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ All 30 logs saved!{Style.RESET_ALL}")
        logger.log_system("Kill test completed successfully")
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Program interrupted with Ctrl+C{Style.RESET_ALL}")
        logger.log_system("Kill test interrupted by user")
        print(f"\n{Fore.CYAN}📊 Now run this command:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}python tools/log_analyzer.py search 'kill_test'{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}✅ You should see the logs - they persisted even after Kill!{Style.RESET_ALL}")
    
    finally:
        print(f"\n{Fore.CYAN}🔍 To view logs:{Style.RESET_ALL}")
        print(f"   python tools/log_analyzer.py search 'kill_test'")
        print(f"   python tools/log_analyzer.py recent -n 50")
        print(f"\n{Fore.CYAN}📁 Log files:{Style.RESET_ALL}")
        print(f"   data/logs/session_{session_id}.jsonl")
        print(f"   data/logs/user_actions.jsonl")
        print(f"   data/logs/full_trace.jsonl")
        
        # بستن logger
        close_advanced_logger()


if __name__ == "__main__":
    main()
