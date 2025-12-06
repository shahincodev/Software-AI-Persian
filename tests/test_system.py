#!/usr/bin/env python3
# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""تست کامل سیستم Software-AI.

این اسکریپت تمام اجزای سیستم را تست می‌کند و گزارش می‌دهد.
"""

import sys
import os
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


def print_header(text: str):
    """چاپ هدر."""
    print("\n" + "=" * 70)
    print(f"{Fore.CYAN}{Style.BRIGHT}🔍 {text}{Style.RESET_ALL}")
    print("=" * 70)


def print_success(text: str):
    """چاپ موفقیت."""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """چاپ خطا."""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")


def print_warning(text: str):
    """چاپ هشدار."""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")


def test_imports():
    """تست import ها."""
    print_header("Testing Imports")
    
    modules = [
        ("core.advanced_logging", "Advanced Logging"),
        ("core.logging_decorators", "Logging Decorators"),
        ("core.intelligent_agent", "Intelligent Agent"),
        ("core.ai_brain", "AI Brain"),
        ("core.desktop_vision", "Desktop Vision"),
        ("core.keyboard_control", "Keyboard Control"),
        ("core.mouse_control", "Mouse Control"),
        ("core.action_controller", "Action Controller"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for module, name in modules:
        try:
            __import__(module)
            print_success(f"{name}: OK")
            success_count += 1
        except Exception as e:
            print_error(f"{name}: {str(e)}")
            fail_count += 1
    
    print(f"\n📊 Results: {success_count} passed, {fail_count} failed")
    return fail_count == 0


def test_logging_system():
    """تست سیستم لاگ."""
    print_header("Testing Logging System")
    
    try:
        from core.advanced_logging import get_advanced_logger, close_advanced_logger
        from core.logging_decorators import log_function_call, LogContext
        
        logger = get_advanced_logger()
        print_success("Logger initialized")
        
        # تست لاگ‌های مختلف
        logger.log_system("Test system message")
        print_success("System log: OK")
        
        logger.log_user_action("test_action", {"param": "value"})
        print_success("User action log: OK")
        
        logger.log_error("Test error", "TestError", {"detail": "test"})
        print_success("Error log: OK")
        
        # تست decorator
        @log_function_call()
        def test_func():
            return "OK"
        
        result = test_func()
        print_success("Decorator log: OK")
        
        # تست context
        with LogContext("test_context"):
            pass
        print_success("Context log: OK")
        
        # بررسی فایل‌های لاگ
        log_dir = Path("data/logs")
        if log_dir.exists():
            log_files = list(log_dir.glob("*.jsonl")) + list(log_dir.glob("*.log"))
            print_success(f"Log files created: {len(log_files)} files")
        else:
            print_warning("Log directory not found")
        
        close_advanced_logger()
        print_success("Logger closed")
        
        return True
    
    except Exception as e:
        print_error(f"Logging system error: {str(e)}")
        return False


def test_core_components():
    """تست اجزای اصلی."""
    print_header("Testing Core Components")
    
    results = {}
    
    # تست Desktop Vision
    try:
        from core.desktop_vision import DesktopVision
        vision = DesktopVision()
        print_success("Desktop Vision: OK")
        results['vision'] = True
    except Exception as e:
        print_error(f"Desktop Vision: {str(e)}")
        results['vision'] = False
    
    # تست Keyboard Control
    try:
        from core.keyboard_control import KeyboardController
        kb = KeyboardController()
        print_success("Keyboard Control: OK")
        results['keyboard'] = True
    except Exception as e:
        print_error(f"Keyboard Control: {str(e)}")
        results['keyboard'] = False
    
    # تست Mouse Control
    try:
        from core.mouse_control import MouseController
        mouse = MouseController()
        print_success("Mouse Control: OK")
        results['mouse'] = True
    except Exception as e:
        print_error(f"Mouse Control: {str(e)}")
        results['mouse'] = False
    
    # تست Action Controller
    try:
        from core.action_controller import ActionController
        controller = ActionController()
        print_success("Action Controller: OK")
        results['controller'] = True
    except Exception as e:
        print_error(f"Action Controller: {str(e)}")
        results['controller'] = False
    
    success = all(results.values())
    passed = sum(results.values())
    total = len(results)
    print(f"\n📊 Results: {passed}/{total} components working")
    
    return success


def test_configuration():
    """تست پیکربندی."""
    print_header("Testing Configuration")
    
    # بررسی فایل‌های مورد نیاز
    required_files = [
        ("requirements.txt", "Dependencies"),
        ("pyproject.toml", "Project Config"),
        ("main.py", "Main Script"),
        (".env", "Environment (optional)"),
    ]
    
    for file_path, name in required_files:
        if Path(file_path).exists():
            print_success(f"{name}: Found")
        else:
            if "optional" in name.lower():
                print_warning(f"{name}: Not found (optional)")
            else:
                print_error(f"{name}: Not found")
    
    # بررسی دایرکتوری‌ها
    required_dirs = [
        ("core", "Core modules"),
        ("data", "Data directory"),
        ("docs", "Documentation"),
        ("examples", "Examples"),
        ("tests", "Tests"),
    ]
    
    for dir_path, name in required_dirs:
        if Path(dir_path).exists():
            print_success(f"{name}: Found")
        else:
            print_error(f"{name}: Not found")
    
    return True


def test_log_analyzer():
    """تست ابزار تحلیل لاگ."""
    print_header("Testing Log Analyzer")
    
    analyzer_path = Path("tools/log_analyzer.py")
    
    if analyzer_path.exists():
        print_success("Log analyzer script: Found")
        
        try:
            # Import test
            sys.path.insert(0, str(analyzer_path.parent.parent))
            from tools.log_analyzer import LogAnalyzer
            print_success("LogAnalyzer class: OK")
            
            # Test instantiation
            analyzer = LogAnalyzer()
            print_success("LogAnalyzer instantiation: OK")
            
            return True
        except Exception as e:
            print_error(f"Log analyzer error: {str(e)}")
            return False
    else:
        print_error("Log analyzer not found")
        return False


def main():
    """تابع اصلی."""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║           Software-AI (Persian Version) - System Test            ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)
    
    results = {}
    
    # اجرای تست‌ها
    results['imports'] = test_imports()
    results['logging'] = test_logging_system()
    results['core'] = test_core_components()
    results['config'] = test_configuration()
    results['analyzer'] = test_log_analyzer()
    
    # نمایش نتیجه نهایی
    print_header("Final Results")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        color = Fore.GREEN if passed else Fore.RED
        print(f"{color}{test_name.upper()}: {status}{Style.RESET_ALL}")
    
    print("\n" + "=" * 70)
    
    if passed_tests == total_tests:
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ ALL TESTS PASSED ({passed_tests}/{total_tests}){Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}🚀 System is ready to use!{Style.RESET_ALL}")
        print(f"\nTo start: {Fore.YELLOW}python main.py --input-mode text{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  SOME TESTS FAILED ({passed_tests}/{total_tests}){Style.RESET_ALL}")
        print(f"\n{Fore.RED}Please fix the issues before using the system.{Style.RESET_ALL}")
    
    print("=" * 70)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
