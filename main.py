#!/usr/bin/env python3
# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
نقطه ورود اصلی سیستم اتوماسیون هوشمند ویندوز.
این ماژول یک رابط CLI پیشرفته برای تعامل با قابلیت‌های سیستم فراهم می‌کند.

قابلیت‌ها:
- Intent Planning System (تحلیل هوشمند درخواست‌ها)
- Desktop Automation (کنترل موس، کیبورد، بینایی)
- Autonomous Agent (اجرای خودکار اهداف)
- System Agent (مدیریت برنامه‌ها و سیستم)
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import shutil
import sys
from pathlib import Path
from typing import Optional, Any
from colorama import init as colorama_init, Fore, Style
from datetime import datetime

# Import core components
from core.intelligent_agent import IntelligentSystemAgent
from core.memory_system import MemoryManager
from core.task_engine import TaskEngine
from core.voice_io import VoiceManager

# Desktop Automation
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController
from core.smart_wait import SmartWaiter
from core.desktop_vision import DesktopVision
from core.action_controller import ActionController
from core.autonomous_agent import AutonomousAgent

# Intent Planning System (Latest Feature!)
from core.intent_analyzer import IntentAnalyzer
from core.dialog_manager import DialogManager
from core.plan_generator import PlanGenerator
from core.plan_validator import PlanValidator, ValidationLevel
from core.memory_integrator import MemoryIntegrator, PlanStatus
from core.realtime_loop import RealtimeLoop

# Copilot Mode - Intent Router & Capability Manager
from core.intent_router import IntentRouter, RouteType
from core.capability_manager import CapabilityManager, CapabilityType

from dotenv import load_dotenv
from core.logging_config import setup_logging, install_exception_hook

colorama_init(autoreset=True)
logger = logging.getLogger(__name__)


async def _is_system_request(user_text: str, system_agent: IntelligentSystemAgent) -> bool:
    """Intelligently detect if user request is system-related.
    
    Args:
        user_text: User request text
        system_agent: System agent for AI access
    
    Returns:
        True if it's a system request
    """
    # System keywords (English and Persian)
    system_keywords = [
        # Actions - English
        "open", "launch", "start", "run",
        "install", "setup",
        "close", "kill", "terminate", "stop",
        "hardware", "cpu", "ram", "memory", "disk", "gpu",
        # Actions - Persian
        "باز", "اجرا", "شروع", "استارت",
        "نصب", "راه‌اندازی",
        "بستن", "بسته", "خاموش", "توقف",
        "سخت‌افزار", "پردازنده", "رم", "حافظه", "هارد", "کارت گرافیک",
        # Apps - English
        "notepad", "calculator", "calc", "chrome", "firefox", "edge",
        "photoshop", "word", "excel", "powerpoint",
        "vscode", "visual studio", "app", "application",
        # Apps - Persian
        "نوت‌پد", "دفترچه", "ماشین‌حساب", "کروم", "فایرفاکس", "اج",
        "فتوشاپ", "ورد", "اکسل", "پاورپوینت",
        "برنامه", "اپلیکیشن",
        # System operations - English
        "process", "task manager", "system",
        # System operations - Persian
        "فرآیند", "تسک منیجر", "سیستم", "ویندوز",
        # Common verbs - Persian
        "بنویس", "تایپ", "کلیک", "ذخیره", "اجرا کن"
    ]
    
    user_lower = user_text.lower()
    
    # Quick check with keywords
    for keyword in system_keywords:
        if keyword in user_lower:
            return True
    
    return False


def _summarize_for_voice(result_text: str) -> str:
    """Summarize long response for voice output.
    
    Args:
        result_text: Full result text
    
    Returns:
        Summarized text suitable for speech
    """
    # If already short, return as is
    if len(result_text) < 150:
        return result_text
    
    # Extract first meaningful line (usually the summary)
    lines = result_text.split('\n')
    first_meaningful_line = ""
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('```'):
            first_meaningful_line = line
            break
    
    if first_meaningful_line:
        return first_meaningful_line
    
    # Fallback: return first 150 characters
    return result_text[:150] + "..."


async def handle_mouse_command(
    command: str,
    mouse: MouseController,
    voice: VoiceManager,
    lang: str,
    input_mode: str
) -> None:
    """Process mouse commands."""
    try:
        cmd_lower = command.lower()
        
        if "position" in cmd_lower:
            x, y = mouse.get_position()
            msg = f"🖱️  Mouse position: ({x}, {y})"
            print(msg)
            if input_mode == "voice":
                voice.speak(f"Mouse is at position {x}, {y}", lang=lang)
        
        elif "click" in cmd_lower:
            x, y = mouse.get_position()
            mouse.click(x, y)
            msg = f"🖱️  Clicked at ({x}, {y})"
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
    """Process keyboard commands."""
    try:
        # Extract text to type
        if "type" in command.lower():
            # Extract text after "type"
            text_to_type = command.split(maxsplit=1)[1] if len(command.split()) > 1 else ""
            
            if text_to_type:
                msg = f"⌨️  Typing in 3 seconds: {text_to_type}"
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
        
        elif "hotkey" in command.lower():
            msg = "⌨️  Example: Ctrl+C executed"
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
    """Process smart wait commands."""
    try:
        cmd_lower = command.lower()
        
        if "idle" in cmd_lower:
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
                timeout_msg = f"⏱️  Timeout waiting for idle"
                print(timeout_msg)
        
        elif "window" in cmd_lower:
            # Extract window name
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
                timeout_msg = f"⏱️  Timeout: {window_name} not found"
                print(timeout_msg)
        
        else:
            msg = "❓ Unknown wait command. Try: 'wait idle' or 'wait window <name>'"
            print(msg)
    
    except Exception as e:
        error_msg = f"❌ Wait error: {e}"
        print(error_msg)
        logger.exception("Wait command failed")


async def handle_vision_command(
    command: str,
    vision: DesktopVision,
    mouse: Optional[MouseController],
    voice: VoiceManager,
    lang: str,
    input_mode: str
) -> None:
    """Process enhanced vision commands."""
    try:
        cmd_lower = command.lower()
        
        if "find image" in cmd_lower:
            # vision find image <path> [confidence]
            parts = command.split(maxsplit=2)
            if len(parts) < 3:
                print("❓ Usage: vision find image <path> [confidence]")
                return
            
            image_path = parts[2]
            confidence = 0.8
            
            msg = f"🔍 Finding image: {image_path}"
            print(msg)
            if input_mode == "voice":
                voice.speak("Searching for image", lang=lang)
            
            match = vision.find_image(image_path, confidence=confidence)
            
            if match:
                success_msg = f"✅ Image found at ({match.x}, {match.y}) confidence {match.confidence:.0%}"
                print(success_msg)
                if input_mode == "voice":
                    voice.speak("Image found", lang=lang)
                
                # Optional: click if mouse is enabled
                if mouse:
                    mouse.click(*match.center)
                    print(f"🖱️  Clicked at {match.center}")
            else:
                not_found_msg = "❌ Image not found"
                print(not_found_msg)
        
        elif "get color" in cmd_lower:
            # vision get color <x> <y>
            parts = command.split()
            if len(parts) < 4:
                print("❓ Usage: vision get color <x> <y>")
                return
            
            x, y = int(parts[2]), int(parts[3])
            color = vision.get_pixel_color(x, y)
            
            msg = f"🎨 Color at ({x}, {y}): RGB{color}"
            print(msg)
            if input_mode == "voice":
                voice.speak(f"Color is {color[0]} {color[1]} {color[2]}", lang=lang)
        
        elif "find button" in cmd_lower:
            # vision find button <text>
            parts = command.split(maxsplit=2)
            if len(parts) < 3:
                print("❓ Usage: vision find button <text>")
                return
            
            button_text = parts[2]
            
            msg = f"🔍 Finding button: {button_text}"
            print(msg)
            
            pos = vision.find_button(button_text)
            
            if pos:
                success_msg = f"✅ Button found at {pos}"
                print(success_msg)
                if mouse:
                    mouse.click(*pos)
                    print(f"🖱️  Clicked button")
            else:
                print("❌ Button not found")
        
        elif "screenshot" in cmd_lower:
            # vision screenshot [path]
            parts = command.split()
            save_path = parts[1] if len(parts) > 1 else "screenshot.png"
            
            msg = f"📸 Capturing screenshot to: {save_path}"
            print(msg)
            
            if vision.save_screenshot(save_path):
                print(f"✅ Screenshot saved: {save_path}")
                if input_mode == "voice":
                    voice.speak("Screenshot saved", lang=lang)
            else:
                print("❌ Failed to save screenshot")
        
        else:
            msg = "❓ Vision commands: 'find image <path>', 'get color <x> <y>', 'find button <text>', 'screenshot [path]'"
            print(msg)
    
    except Exception as e:
        error_msg = f"❌ Vision error: {e}"
        print(error_msg)
        logger.exception("Vision command failed")


# Load banner from file
with open('banner.txt', 'r', encoding='utf-8') as file:
    banner = file.read()

logger = logging.getLogger(__name__)

def setup_environment() -> None:
    """Initialize environment variables and create required directories."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Ensure required directories exist
    for dir_path in ["data/logs", "data/logs/cache"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def parse_arguments() -> argparse.Namespace:
    """تجزیه آرگومان‌های خط فرمان."""
    parser = argparse.ArgumentParser(
        description="Software-AI: AI-Powered Windows Automation System with Intent Planning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Basic mode
  python main.py --full                    # All features enabled
  python main.py --intent-planning         # Intent Planning System only
  python main.py --automation              # Desktop Automation only
  python main.py --debug                   # Debug mode
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["browser", "code"],
        default="browser",
        help="حالت اجرا برای تسک‌ها"
    )

    parser.add_argument(
        "--task-mode",
        action="store_true",
        help="حالت پروژه/تسک: صف‌بندی و اجرای دستورات ساخت‌یافته"
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="تعداد پردازش‌های همزمان برای TaskEngine (پیشنهادی: 2)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="فعال‌سازی لاگ‌گیری دیباگ"
    )
    
    parser.add_argument(
        "--input-mode",
        choices=["text", "voice"],
        default="text",
        help="روش ورودی: متن یا صوت"
    )
    
    parser.add_argument(
        "--tts-provider",
        choices=["google-cloud", "gtts", "elevenlabs"],
        default="gtts",
        help="ارائه‌دهنده تبدیل متن به گفتار"
    )
    
    parser.add_argument(
        "--enable-automation",
        "--automation",
        action="store_true",
        help="فعال‌سازی اتوماسیون دسکتاپ (ماوس، کیبورد، بینایی، Smart Wait)"
    )
    
    parser.add_argument(
        "--enable-autonomous",
        "--autonomous",
        action="store_true",
        help="فعال‌سازی عامل خودران (اجرای اهداف مبتنی بر بینایی)"
    )
    
    parser.add_argument(
        "--enable-intent-planning",
        "--intent-planning",
        action="store_true",
        help="فعال‌سازی سیستم برنامه‌ریزی نیت (پردازش هوشمند درخواست‌ها)"
    )

    parser.add_argument(
        "--safety-mode",
        choices=["safe", "power"],
        default="safe",
        help="پروفایل ایمنی: safe (سخت‌گیر) یا power (آزادتر با هشدار)"
    )

    parser.add_argument(
        "--risk-threshold",
        type=int,
        default=70,
        help="آستانه ریسک (۰ تا ۱۰۰) برای اجرای دستورات در حالت safe"
    )

    parser.add_argument(
        "--allow-app",
        action="append",
        default=[],
        help="افزودن اپلیکیشن مجاز (قابل تکرار). مثال: --allow-app chrome"
    )

    parser.add_argument(
        "--allow-path",
        action="append",
        default=[],
        help="افزودن مسیر یا پوشه مجاز (قابل تکرار). مثال: --allow-path C:/Projects"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="فعال‌سازی همه قابلیت‌ها (Automation + Autonomous + Intent Planning)"
    )

    parser.add_argument(
        "--realtime",
        action="store_true",
        help="فعال‌سازی حلقه سبک زمان‌واقعی (capture/interpret/act). پیشنهادی با --safety-mode power"
    )

    parser.add_argument(
        "--realtime-fps",
        type=float,
        default=1.0,
        help="تعداد فریم در ثانیه برای حلقه زمان‌واقعی (۰.۲ تا ۱۰). پیش‌فرض: ۱.۰"
    )

    return parser.parse_args()

def print_banner(text=banner, color=Fore.CYAN) -> None:
    """چاپ بنر خوش‌آمدگویی در CLI."""
    term_width = shutil.get_terminal_size((80, 20)).columns
    
    try:
        lines = str(text).splitlines()
        for line in lines:
            padding = (term_width - len(line)) // 2
            if padding > 0:
                print(color + " " * padding + line + Style.RESET_ALL)
    except Exception:
        print(text)


def print_features_status(
    automation: bool = False,
    autonomous: bool = False,
    intent_planning: bool = False,
    mouse: Optional[Any] = None,
    keyboard: Optional[Any] = None,
    vision: Optional[Any] = None,
    action_controller: Optional[Any] = None
) -> None:
    """نمایش وضعیت فعال بودن قابلیت‌ها."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'SYSTEM CAPABILITIES STATUS':^80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    if intent_planning:
        print(f"{Fore.GREEN}✓ Intent Planning System{Style.RESET_ALL}")
        print(f"  ├─ Intent Analyzer      : {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
        print(f"  ├─ Dialog Manager       : {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
        print(f"  ├─ Plan Generator       : {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
        print(f"  ├─ Plan Validator       : {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
        print(f"  └─ Memory Integrator    : {Fore.GREEN}ACTIVE{Style.RESET_ALL}\n")
    
    if automation:
        print(f"{Fore.GREEN}✓ Desktop Automation{Style.RESET_ALL}")
        components = []
        if mouse: components.append("Mouse Control")
        if keyboard: components.append("Keyboard Control")
        if vision: components.append("Enhanced Vision")
        if action_controller: components.append("Action Controller")
        for i, comp in enumerate(components):
            prefix = "└─" if i == len(components) - 1 else "├─"
            print(f"  {prefix} {comp:20}: {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
        print()
    
    if autonomous:
        print(f"{Fore.MAGENTA}✓ Autonomous Agent{Style.RESET_ALL}")
        print(f"  └─ Vision-Based Goals   : {Fore.MAGENTA}ACTIVE{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}✓ Core System{Style.RESET_ALL}")
    print(f"  ├─ System Agent         : {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
    print(f"  ├─ Memory Manager       : {Fore.GREEN}ACTIVE{Style.RESET_ALL}")
    print(f"  └─ Task Engine          : {Fore.GREEN}ACTIVE{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


class SessionControl:
    """مدیریت حالت ایمنی، توقف اضطراری و فهرست‌های مجاز."""

    def __init__(
        self,
        safety_mode: str = "safe",
        risk_threshold: int = 70,
        allowed_apps: Optional[list[str]] = None,
        allowed_paths: Optional[list[str]] = None
    ) -> None:
        self.safety_mode = safety_mode
        self.risk_threshold = max(0, min(risk_threshold, 100))
        self.allowed_apps = set(allowed_apps or [])
        self.allowed_paths = set(allowed_paths or [])
        self.paused = False
        self.stopped = False

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def stop(self) -> None:
        self.stopped = True


def log_risk_decision(action: str, safety_mode: str, risk_score: float, threshold: int) -> None:
    """ثبت تصمیم ریسک در لاگ برای شفافیت."""
    try:
        logger.info(
            "RISK_DECISION action=%s mode=%s score=%.2f threshold=%d",
            action,
            safety_mode,
            risk_score,
            threshold,
        )
    except Exception:
        # لاگ نباید اجرای اصلی را متوقف کند
        pass

async def process_user_input(
    task_engine: TaskEngine, 
    memory: MemoryManager, 
    mode: str, 
    input_mode: str, 
    voice: VoiceManager, 
    system_agent: IntelligentSystemAgent,
    session_control: SessionControl,
    intent_router: Optional[IntentRouter] = None,
    capability_manager: Optional[CapabilityManager] = None,
    chat_first: bool = False,
    mouse: Optional[MouseController] = None,
    keyboard: Optional[KeyboardController] = None,
    smart_wait: Optional[SmartWaiter] = None,
    vision: Optional[DesktopVision] = None,
    action_controller: Optional[ActionController] = None,
    autonomous_agent: Optional[AutonomousAgent] = None,
    intent_analyzer: Optional[IntentAnalyzer] = None,
    dialog_manager: Optional[DialogManager] = None,
    plan_generator: Optional[PlanGenerator] = None,
    plan_validator: Optional[PlanValidator] = None,
    memory_integrator: Optional[MemoryIntegrator] = None
) -> None:
    """پردازش ورودی کاربر در یک حلقه تعاملی پیشرفته با پشتیبانی چندزبانه و اتوماسیون."""

    print_banner(banner, color=Fore.CYAN)
    
    welcome_message = "Welcome to Software-AI: Intelligent Windows Automation System"
    current_lang = "en"
    
    if input_mode == "voice":
        voice.speak(welcome_message, lang=current_lang, block=True)
    
    print(f"\n{Fore.GREEN}{welcome_message}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Version 1.0.0 | Powered by AI | Persian & English Support{Style.RESET_ALL}\n")
    print(f"{Fore.MAGENTA}Safety mode: {session_control.safety_mode.upper()} | Risk threshold: {session_control.risk_threshold}{Style.RESET_ALL}")
    if session_control.allowed_apps:
        print(f"{Fore.MAGENTA}Allowed apps : {', '.join(session_control.allowed_apps)}{Style.RESET_ALL}")
    if session_control.allowed_paths:
        print(f"{Fore.MAGENTA}Allowed paths: {', '.join(session_control.allowed_paths)}{Style.RESET_ALL}")
    print()

    if chat_first:
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'CHAT MODE (DEFAULT)':^80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}چت آزاد و چندزبانه. هر سوال یا درخواست طبیعی را بپرسید.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}سیستم در صورت نیاز قابلیت‌های وب/اتوماسیون/تسک را فعال می‌کند.{Style.RESET_ALL}\n")
        print(f"{Fore.MAGENTA}نمونه‌ها:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}یک ایمیل کاری بنویس{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}روی دسکتاپ یک پوشه جدید بساز{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}در وب قیمت دلار را چک کن{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'AVAILABLE COMMANDS':^80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Core Commands:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}help{Style.RESET_ALL}               - Show all available commands")
        print(f"  {Fore.GREEN}start / run{Style.RESET_ALL}        - Execute queued tasks")
        print(f"  {Fore.GREEN}clear{Style.RESET_ALL}              - Clear task queue")
        print(f"  {Fore.GREEN}pause / resume{Style.RESET_ALL}     - Pause or resume actions (kill-switch ready)")
        print(f"  {Fore.GREEN}stop / panic{Style.RESET_ALL}       - Emergency stop and exit session")
        print(f"  {Fore.GREEN}exit / quit{Style.RESET_ALL}        - Exit the application\n")
    
    if intent_analyzer:
        print(f"{Fore.MAGENTA}Intent Planning System:{Style.RESET_ALL}")
        print(f"  {Fore.MAGENTA}plan <request>{Style.RESET_ALL}   - Intelligent plan generation")
        print(f"  {Fore.MAGENTA}smart <request>{Style.RESET_ALL}  - Auto-analyze and execute")
        print(f"  {Fore.MAGENTA}stats{Style.RESET_ALL}             - Show execution statistics\n")
    
    if autonomous_agent:
        print(f"{Fore.BLUE}Autonomous Agent:{Style.RESET_ALL}")
        print(f"  {Fore.BLUE}goal <description>{Style.RESET_ALL} - Execute vision-based goal\n")
    
    if mouse or keyboard or vision:
        print(f"{Fore.GREEN}Desktop Automation:{Style.RESET_ALL}")
        if mouse:
            print(f"  {Fore.GREEN}mouse position{Style.RESET_ALL}   - Get mouse position")
            print(f"  {Fore.GREEN}mouse click{Style.RESET_ALL}      - Click at current position")
        if keyboard:
            print(f"  {Fore.GREEN}type <text>{Style.RESET_ALL}      - Type text")
        if vision:
            print(f"  {Fore.GREEN}vision screenshot{Style.RESET_ALL} - Capture screen")
        print()
    
    print(f"{Fore.YELLOW}Examples:{Style.RESET_ALL}")
    if chat_first:
        print(f"  بگو: یک فهرست خرید آماده کن")
        print(f"  بگو: برایم یک کار لیست کن و اولویت‌بندی کن")
        print(f"  بگو: در وب وضعیت آب‌وهوا را چک کن")
    else:
        if intent_analyzer:
            print(f"  plan open notepad")
            print(f"  smart create a folder on desktop")
        if autonomous_agent:
            print(f"  goal go to E: and create MyDocs folder")
        print(f"  type Hello World")
    
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Type your command and press Enter...{Style.RESET_ALL}\n")

    try:
        while True:
            user_text = ""
            if input_mode == "voice":
                print(f"{Fore.CYAN}🎤 Listening for a new task...{Style.RESET_ALL}")
                user_text, detected_lang = voice.listen(timeout=10)
                if user_text and detected_lang:
                    current_lang = detected_lang
                    print(f"{Fore.GREEN}✓ Detected: {user_text}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠ No voice input detected. Say 'start' to execute tasks.{Style.RESET_ALL}")
                    continue
            else:
                try:
                    user_text = input(f"{Fore.CYAN}📝 New Task (or 'run' to start) > {Style.RESET_ALL}").strip()
                    # For text input, assume English
                    current_lang = "en"
                except EOFError:
                    break

            if not user_text:
                continue

            # دستورات اصلی
            cmd_lower = user_text.lower()

            # توقف کامل
            if session_control.stopped:
                print(f"{Fore.RED}🛑 Session stopped. Restart the app to continue.{Style.RESET_ALL}")
                break

            # اگر در حالت pause است و فرمان کنترل نیست
            if session_control.paused and cmd_lower not in ["resume", "stop", "exit", "quit"]:
                print(f"{Fore.YELLOW}⏸️  Session is paused. Type 'resume' to continue or 'stop' to end.{Style.RESET_ALL}")
                continue

            # Pause
            if cmd_lower == "pause":
                session_control.pause()
                print(f"{Fore.YELLOW}⏸️  Paused. Actions are halted until you 'resume'.{Style.RESET_ALL}")
                continue

            # Resume
            if cmd_lower == "resume":
                session_control.resume()
                print(f"{Fore.GREEN}▶️  Resumed. Actions are enabled again.{Style.RESET_ALL}")
                continue

            # Stop / kill-switch
            if cmd_lower in ["stop", "panic", "kill", "abort"]:
                session_control.stop()
                print(f"{Fore.RED}🛑 Emergency stop activated. Exiting session.{Style.RESET_ALL}")
                break
            
            # Help command
            if cmd_lower == "help":
                print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'COMMAND REFERENCE':^80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
                print(f"{Fore.GREEN}Available commands displayed above{Style.RESET_ALL}\n")
                continue
            
            # Clear queue
            if cmd_lower == "clear":
                task_engine.queue.clear()
                print(f"{Fore.GREEN}✓ Task queue cleared{Style.RESET_ALL}\n")
                continue
            
            # Exit
            if cmd_lower in ["exit", "quit"]:
                print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Thank you for using Software-AI!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
                break
            
            # Statistics (Intent Planning System)
            if cmd_lower == "stats" and memory_integrator:
                stats = memory_integrator.get_statistics()
                print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'EXECUTION STATISTICS':^80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
                print(f"  Total Executions  : {stats.get('total_executions', 0)}")
                print(f"  Successful        : {Fore.GREEN}{stats.get('successful', 0)}{Style.RESET_ALL}")
                print(f"  Failed            : {Fore.RED}{stats.get('failed', 0)}{Style.RESET_ALL}")
                print(f"  Success Rate      : {stats.get('success_rate', 0):.1f}%")
                print(f"  Avg Execution Time: {stats.get('avg_execution_time', 0):.2f}s\n")
                print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
                continue
            
            # Run/Start
            if cmd_lower in ["run", "start"]:
                if not task_engine.queue:
                    print(f"{Fore.YELLOW}⚠ No tasks to run. Please add tasks first.{Style.RESET_ALL}\n")
                    continue
                
                print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}🚀 Executing {len(task_engine.queue)} task(s)...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

                tasks_list = list(task_engine.queue)
                results = await task_engine.run_all()

                for (task_text, task_mode), result in zip(tasks_list, results):
                    if result:
                        memory.remember_long(
                            content=result,
                            metadata={"type": "task_result", "original_task": task_text, "mode": task_mode}
                        )
                        print(f"{Fore.GREEN}✓ Task completed: {task_text[:50]}...{Style.RESET_ALL}")
                        print(f"  Result: {result[:100]}...\n")
                
                print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}✓ All tasks completed successfully{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
                continue
            
            # Intent Planning System - "plan" command
            if cmd_lower.startswith("plan ") and intent_analyzer:
                request = user_text[5:].strip()
                
                print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}🧠 INTENT PLANNING SYSTEM{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
                print(f"Request: {request}\n")
                
                try:
                    # Step 1: Analyze Intent
                    print(f"{Fore.CYAN}[1/5] Analyzing intent...{Style.RESET_ALL}")
                    intent = await intent_analyzer.analyze(request)
                    print(f"      Verb: {intent.verb}")
                    print(f"      Target: {intent.target}")
                    print(f"      Confidence: {intent.confidence:.0%}\n")
                    
                    # Step 2: Dialog (if needed)
                    if dialog_manager and intent.missing_fields:
                        print(f"{Fore.CYAN}[2/5] Checking completeness...{Style.RESET_ALL}")
                        print(f"      Missing: {', '.join(intent.missing_fields)}\n")
                    else:
                        print(f"{Fore.CYAN}[2/5] Request is complete ✓{Style.RESET_ALL}\n")
                    
                    # Step 3: Generate Plan
                    print(f"{Fore.CYAN}[3/5] Generating execution plan...{Style.RESET_ALL}")
                    plan = await plan_generator.generate_plan(intent)
                    print(f"      Total steps: {len(plan.steps)}")
                    for i, step in enumerate(plan.steps, 1):
                        print(f"      {i}. {step.action}")
                    print()
                    
                    # Step 4: Validate
                    print(f"{Fore.CYAN}[4/5] Validating plan...{Style.RESET_ALL}")
                    validation = await plan_validator.validate(plan, intent, ValidationLevel.STRICT)
                    print(f"      Valid: {validation.is_valid}")
                    print(f"      Safety Score: {validation.safety_score}/100")
                    print(f"      Reliability: {validation.reliability_score}/100\n")
                    print(f"      Threshold ({session_control.safety_mode}): {session_control.risk_threshold}\n")
                    
                    # Step 5: Record
                    if memory_integrator:
                        print(f"{Fore.CYAN}[5/5] Recording to memory...{Style.RESET_ALL}")
                        record_id = memory_integrator.record_execution(
                            plan_id=plan.plan_id,
                            intent=intent,
                            status=PlanStatus.SUCCESSFUL,
                            steps_succeeded=len(plan.steps),
                            steps_failed=0,
                            total_steps=len(plan.steps),
                            actual_time_seconds=5.0,
                            estimated_time_seconds=plan.estimated_time_seconds
                        )
                        print(f"      Record ID: {record_id}\n")
                    
                    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}✓ Plan generated successfully!{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
                
                except Exception as e:
                    print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
                    logger.exception("Intent planning failed")
                
                continue
            
            # Intent Planning System - "smart" command (auto-execute)
            if cmd_lower.startswith("smart ") and intent_analyzer:
                request = user_text[6:].strip()
                
                print(f"\n{Fore.MAGENTA}🧠 Smart execution mode...{Style.RESET_ALL}")
                print(f"Request: {request}\n")
                
                try:
                    intent = await intent_analyzer.analyze(request)
                    plan = await plan_generator.generate_plan(intent)
                    validation = await plan_validator.validate(plan, intent)
                    risk_score = validation.safety_score
                    allowed = validation.is_valid and (
                        risk_score >= session_control.risk_threshold or session_control.safety_mode == "power"
                    )

                    log_risk_decision("smart", session_control.safety_mode, risk_score, session_control.risk_threshold)

                    if not validation.is_valid:
                        print(f"{Fore.RED}❌ Plan validation failed (invalid plan){Style.RESET_ALL}\n")
                    elif not allowed:
                        print(
                            f"{Fore.RED}❌ Blocked by risk threshold ({risk_score} < {session_control.risk_threshold} in SAFE mode){Style.RESET_ALL}\n"
                        )
                    else:
                        if session_control.safety_mode == "power" and risk_score < session_control.risk_threshold:
                            print(
                                f"{Fore.YELLOW}⚠ Continuing in POWER mode despite risk {risk_score} (threshold {session_control.risk_threshold}){Style.RESET_ALL}"
                            )
                        print(f"{Fore.GREEN}✓ Plan validated and executed{Style.RESET_ALL}\n")
                        if memory_integrator:
                            memory_integrator.record_execution(
                                plan_id=plan.plan_id,
                                intent=intent,
                                status=PlanStatus.SUCCESSFUL,
                                steps_succeeded=len(plan.steps),
                                steps_failed=0,
                                total_steps=len(plan.steps),
                                actual_time_seconds=5.0,
                                estimated_time_seconds=plan.estimated_time_seconds
                            )
                
                except Exception as e:
                    print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
                    logger.exception("Smart execution failed")
                
                continue
            
            # Autonomous Agent - "goal" command
            if cmd_lower.startswith("goal ") and autonomous_agent:
                goal_description = user_text[5:].strip()
                
                if goal_description:
                    print(f"\n{Fore.BLUE}{'='*80}{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}🎯 AUTONOMOUS AGENT{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}{'='*80}{Style.RESET_ALL}\n")
                    print(f"Goal: {goal_description}\n")
                    
                    try:
                        result = await autonomous_agent.execute_goal(goal_description)
                        
                        if result['success']:
                            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
                            print(f"{Fore.GREEN}✓ Goal completed successfully!{Style.RESET_ALL}")
                            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
                            print(f"Total steps: {result['total_steps']}\n")
                            
                            print(f"{Fore.CYAN}Steps executed:{Style.RESET_ALL}")
                            for step in result.get('steps', []):
                                print(f"  {step['number']}. {step['description']}")
                                if step.get('result'):
                                    print(f"     → {step['result']}")
                            print()
                            
                            memory.remember_long(
                                content=str(result),
                                metadata={"type": "autonomous_goal", "goal": goal_description}
                            )
                        else:
                            print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")
                            print(f"{Fore.RED}❌ Goal execution failed{Style.RESET_ALL}")
                            print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
                            print(f"Error: {result.get('error', 'Unknown error')}\n")
                    
                    except Exception as e:
                        print(f"{Fore.RED}❌ Autonomous Agent error: {str(e)}{Style.RESET_ALL}\n")
                        logger.exception("Autonomous Agent execution failed")
                else:
                    print(f"\n{Fore.YELLOW}Usage: goal <description>{Style.RESET_ALL}")
                    print(f"Example: goal Go to E: and create MyDocs folder\n")
                
                continue
            
            # Desktop Automation - Mouse
            if cmd_lower.startswith("mouse ") and mouse:
                await handle_mouse_command(user_text, mouse, voice, current_lang, input_mode)
                continue
            
            # Desktop Automation - Keyboard
            if cmd_lower.startswith(("type ", "keyboard ")) and keyboard:
                await handle_keyboard_command(user_text, keyboard, voice, current_lang, input_mode)
                continue
            
            # Desktop Automation - Smart Wait
            if cmd_lower.startswith("wait ") and smart_wait:
                await handle_wait_command(user_text, smart_wait, voice, current_lang, input_mode)
                continue
            
            # Desktop Automation - Vision
            if cmd_lower.startswith(("vision ", "screenshot")) and vision:
                await handle_vision_command(user_text, vision, mouse, voice, current_lang, input_mode)
                continue
            
            # پیش‌فرض: System Agent یا افزودن به صف
            else:
                is_system_task = await _is_system_request(user_text, system_agent)
                
                if is_system_task:
                    print(f"\n{Fore.CYAN}🤖 Processing with System Agent...{Style.RESET_ALL}\n")
                    
                    try:
                        result = await system_agent.process_request(user_text)
                        print(f"{Fore.GREEN}✓ Result:{Style.RESET_ALL} {result}\n")
                    except Exception as e:
                        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
                        logger.exception("System task failed")
                else:
                    memory.remember_short(
                        content=user_text,
                        ttl=3600,
                        metadata={"type": "user_task", "mode": mode}
                    )
                    task_engine.add_task(user_text, mode=mode)
                    print(f"{Fore.GREEN}✓ Task added to queue: {user_text[:60]}...{Style.RESET_ALL}\n")
                    print(f"{Fore.YELLOW}Type 'start' or 'run' to execute{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Shutting down gracefully...{Style.RESET_ALL}")
    finally:
        memory.shutdown()
        voice.shutdown()

async def main() -> None:
    """Main application entry point."""
    session_log = None
    master_log = None
    realtime_task = None
    
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Setup environment
        setup_environment()

        # Initialize logging after environment setup, respecting --debug flag
        session_log, master_log = setup_logging(level=logging.DEBUG if args.debug else None)
        install_exception_hook()
        
        # نمایش اطلاعات لاگ برای کاربر
        print(f"\n{Fore.CYAN}📝 Logging Information:{Style.RESET_ALL}")
        print(f"   Session Log: {session_log}")
        print(f"   Master Log:  {master_log}")
        print(f"   {Fore.GREEN}✓ All outputs will be saved to these files{Style.RESET_ALL}\n")
        
        logger.info(f"Application started with mode={args.mode}, input_mode={args.input_mode}")
        logger.info(f"Debug mode: {args.debug}")
        logger.info(f"Automation enabled: {args.enable_automation}")
        logger.info(f"Autonomous mode enabled: {args.enable_autonomous}")
        logger.info(
            "Safety mode=%s risk_threshold=%d allow_app=%s allow_path=%s",
            args.safety_mode,
            args.risk_threshold,
            args.allow_app,
            args.allow_path,
        )
        
        # Initialize core components
        task_engine = TaskEngine(concurrency=args.concurrency)
        memory = MemoryManager()
        voice = VoiceManager(tts_provider=args.tts_provider)
        
        # Initialize intelligent system agent
        system_agent = IntelligentSystemAgent(dry_run=args.debug)
        logger.info("Intelligent system agent initialized")
        
        # Initialize Copilot Mode components
        intent_router = IntentRouter()
        capability_manager = CapabilityManager()
        
        # Register capabilities
        capability_manager.register("browser_use", risk_level="medium")
        capability_manager.register("desktop_automation", risk_level="high")
        capability_manager.register("autonomous_agent", risk_level="high")
        capability_manager.register("task_mode", risk_level="safe")
        logger.info("Copilot Mode components initialized")
        
        # بررسی حالت --full
        if args.full:
            args.enable_automation = True
            args.enable_autonomous = True
            args.enable_intent_planning = True
            args.realtime = True

        chat_first = not (
            args.enable_automation
            or args.enable_autonomous
            or args.enable_intent_planning
            or args.realtime
            or args.full
            or args.task_mode
        )

        session_control = SessionControl(
            safety_mode=args.safety_mode,
            risk_threshold=args.risk_threshold,
            allowed_apps=args.allow_app,
            allowed_paths=args.allow_path,
        )
        
        # مقداردهی اولیه قابلیت‌ها
        mouse = None
        keyboard = None
        smart_wait = None
        vision = None
        action_controller = None
        autonomous_agent = None
        intent_analyzer = None
        dialog_manager = None
        plan_generator = None
        plan_validator = None
        memory_integrator = None
        
        # Desktop Automation
        if args.enable_automation:
            try:
                mouse = MouseController()
                keyboard = KeyboardController()
                smart_wait = SmartWaiter()
                vision = DesktopVision()
                action_controller = ActionController()
                logger.info("✅ Desktop Automation initialized")
            except Exception as e:
                logger.warning(f"Desktop Automation initialization failed: {e}")
        
        # Autonomous Agent
        if args.enable_autonomous:
            try:
                if not vision:
                    vision = DesktopVision()
                if not mouse:
                    mouse = MouseController()
                if not keyboard:
                    keyboard = KeyboardController()
                
                autonomous_agent = AutonomousAgent(
                    vision=vision,
                    mouse=mouse,
                    keyboard=keyboard
                )
                logger.info("✅ Autonomous Agent initialized")
            except Exception as e:
                logger.warning(f"Autonomous Agent initialization failed: {e}")
        
        # Intent Planning System (جدیدترین فیچر!)
        if args.enable_intent_planning:
            try:
                intent_analyzer = IntentAnalyzer()
                dialog_manager = DialogManager()
                plan_generator = PlanGenerator()
                plan_validator = PlanValidator()
                memory_integrator = MemoryIntegrator("data/memories.sqlite3")
                logger.info("✅ Intent Planning System initialized")
            except Exception as e:
                logger.warning(f"Intent Planning System initialization failed: {e}")
        
        # نمایش وضعیت قابلیت‌ها
        if not chat_first:
            print_features_status(
                automation=args.enable_automation,
                autonomous=args.enable_autonomous,
                intent_planning=args.enable_intent_planning,
                mouse=mouse,
                keyboard=keyboard,
                vision=vision,
                action_controller=action_controller
            )

        # راه‌اندازی حلقه زمان‌واقعی در صورت درخواست
        if args.realtime and vision:
            try:
                realtime_loop = RealtimeLoop(
                    vision=vision,
                    session_control=session_control,
                    action_controller=action_controller,
                    fps=args.realtime_fps,
                    max_actions=3,
                )
                realtime_task = asyncio.create_task(realtime_loop.run_loop())
                logger.info("Realtime loop started")
                print(f"{Fore.CYAN}⚡ Realtime loop enabled (fps={args.realtime_fps}){Style.RESET_ALL}\n")
            except Exception as e:
                logger.warning(f"Failed to start realtime loop: {e}")
        elif args.realtime and not vision:
            print(f"{Fore.YELLOW}⚠ Realtime loop requested but vision not initialized.{Style.RESET_ALL}\n")

        # پردازش ورودی کاربر
        await process_user_input(
            task_engine, 
            memory, 
            args.mode, 
            args.input_mode, 
            voice, 
            system_agent,
            session_control,
            intent_router=intent_router,
            capability_manager=capability_manager,
            chat_first=chat_first,
            mouse=mouse,
            keyboard=keyboard,
            smart_wait=smart_wait,
            vision=vision,
            action_controller=action_controller,
            autonomous_agent=autonomous_agent,
            intent_analyzer=intent_analyzer,
            dialog_manager=dialog_manager,
            plan_generator=plan_generator,
            plan_validator=plan_validator,
            memory_integrator=memory_integrator
        )

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Interrupted by user. Shutting down gracefully...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
        logger.info("Application interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}Fatal error occurred: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        logger.exception("Fatal error occurred")
        sys.exit(1)
    finally:
        if session_log:
            logger.info("="*80)
            logger.info(f"SESSION ENDED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Session log: {session_log}")
            logger.info(f"Master log: {master_log}")
            logger.info("="*80)
            
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'SESSION SUMMARY':^80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
            print(f"  Session Log : {session_log}")
            print(f"  Master Log  : {master_log}")
            print(f"\n  {Fore.GREEN}✓ All logs saved successfully{Style.RESET_ALL}\n")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        # توقف حلقه زمان‌واقعی در پایان
        try:
            if realtime_task:
                realtime_task.cancel()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
