#!/usr/bin/env python3
# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
اسکریپت تست سریع برای بررسی تمام قابلیت‌ها قبل از ضبط ویدئو.
این فایل به شما کمک می‌کند مطمئن شوید همه چیز کار می‌کند.
"""

import sys
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)

def check_imports():
    """بررسی تمام import های ضروری."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Checking Imports...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    required_modules = [
        ("colorama", "pip install colorama"),
        ("pyfiglet", "pip install pyfiglet"),
        ("dotenv", "pip install python-dotenv"),
        ("asyncio", "Built-in"),
    ]
    
    all_ok = True
    
    for module, install_cmd in required_modules:
        try:
            __import__(module)
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {module:20} : OK")
        except ImportError:
            print(f"{Fore.RED}✗{Style.RESET_ALL} {module:20} : MISSING ({install_cmd})")
            all_ok = False
    
    return all_ok

def check_core_modules():
    """بررسی ماژول‌های اصلی پروژه."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Checking Core Modules...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    core_modules = [
        "core.intent_analyzer",
        "core.dialog_manager",
        "core.plan_generator",
        "core.plan_validator",
        "core.memory_integrator",
        "core.intelligent_agent",
        "core.autonomous_agent",
        "core.mouse_control",
        "core.keyboard_control",
        "core.desktop_vision",
    ]
    
    all_ok = True
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {module:30} : OK")
        except ImportError as e:
            print(f"{Fore.RED}✗{Style.RESET_ALL} {module:30} : ERROR ({str(e)})")
            all_ok = False
    
    return all_ok

def check_files():
    """بررسی فایل‌های مهم."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Checking Required Files...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    required_files = [
        "main.py",
        "banner.txt",
        "requirements.txt",
        "DEMO_GUIDE.md",
        "core/__init__.py",
        "data/.gitkeep"
    ]
    
    all_ok = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {str(path):30} : EXISTS")
        else:
            print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {str(path):30} : MISSING (optional)")
            if file_path == "main.py":
                all_ok = False
    
    return all_ok

def check_directories():
    """بررسی پوشه‌های ضروری."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Checking Directories...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    dirs = ["data", "data/logs", "core", "tests", "examples", "docs"]
    
    for dir_name in dirs:
        path = Path(dir_name)
        if path.exists() and path.is_dir():
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {dir_name:20} : EXISTS")
        else:
            print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {dir_name:20} : MISSING (will be created)")
            path.mkdir(parents=True, exist_ok=True)

def print_demo_commands():
    """نمایش دستورات دمو."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Demo Commands (copy & paste):{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    commands = [
        ("Basic mode", "python main.py"),
        ("Intent Planning", "python main.py --intent-planning"),
        ("Full features", "python main.py --full"),
        ("Debug mode", "python main.py --debug"),
    ]
    
    for desc, cmd in commands:
        print(f"{Fore.YELLOW}{desc:20}{Style.RESET_ALL} : {Fore.GREEN}{cmd}{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}Inside the app:{Style.RESET_ALL}")
    demo_cmds = [
        "help",
        "plan open notepad",
        "stats",
        "goal go to E: and create MyDocs",
        "exit"
    ]
    
    for cmd in demo_cmds:
        print(f"  {Fore.GREEN}{cmd}{Style.RESET_ALL}")

def main():
    """تابع اصلی."""
    print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'SOFTWARE-AI PRE-VIDEO CHECK':^80}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    
    results = []
    
    # بررسی imports
    results.append(("Imports", check_imports()))
    
    # بررسی ماژول‌های اصلی
    results.append(("Core Modules", check_core_modules()))
    
    # بررسی فایل‌ها
    results.append(("Files", check_files()))
    
    # بررسی پوشه‌ها
    check_directories()
    
    # نمایش دستورات دمو
    print_demo_commands()
    
    # خلاصه نهایی
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'SUMMARY':^80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    all_passed = True
    for name, passed in results:
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if passed else f"{Fore.RED}FAIL{Style.RESET_ALL}"
        print(f"  {name:20} : {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ All checks passed! Ready for video recording!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Some checks failed. Please fix issues before recording.{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
