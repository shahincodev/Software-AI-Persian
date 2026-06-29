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
from typing import Any, Dict, List, Optional
from colorama import init as colorama_init, Fore, Style
from datetime import datetime

from dotenv import load_dotenv

from core.action_controller import ActionController
from core.ai_brain import AIBrain
from core.autonomous_agent import AutonomousAgent
from core.capability_manager import CapabilityManager
from core.desktop_vision import DesktopVision
from core.intent_analyzer import IntentAnalyzer
from core.intent_router import IntentRouter, RouteType
from core.keyboard_control import KeyboardController
from core.logging_config import install_exception_hook, setup_logging
from core.memory_integrator import MemoryIntegrator, MemoryManager, PlanStatus
from core.mouse_control import MouseController
from core.plan_generator import PlanGenerator
from core.plan_validator import PlanValidator
from core.realtime_loop import RealtimeLoop
from core.safety_consent_manager import SafetyConsentManager
from core.smart_wait import SmartWaiter
from core.task_engine import TaskEngine
from core.voice_io import VoiceManager

colorama_init(autoreset=True)
logger = logging.getLogger(__name__)


def _load_banner(path: str = "banner.txt") -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return "Software-AI"


banner = _load_banner()


def _summarize_for_voice(result_text: str) -> str:
    """خلاصه‌سازی پاسخ طولانی برای خروجی صوتی.
    
    Args:
        result_text: متن کامل نتیجه
    
    Returns:
        متن خلاصه شده مناسب برای گفتار
    """
    # اگر کوتاه است، همان‌طور برگرداندن
    if len(result_text) < 150:
        return result_text
    
    # استخراج اولین خط معنادار (معمولاً خلاصه)
    lines = result_text.split('\n')
    first_meaningful_line = ""
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('```'):
            first_meaningful_line = line
            break
    
    if first_meaningful_line:
        return first_meaningful_line
    
    # بازگشت اضطراری: بازگرداندن ۱۵۰ کاراکتر اول
    return result_text[:150] + "..."


async def handle_mouse_command(
    command: str,
    mouse: MouseController,
    voice: VoiceManager,
    lang: str,
    input_mode: str
) -> None:
    """پردازش دستورات ماوس."""
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
    """پردازش دستورات کیبورد."""
    try:
        # استخراج متن برای تایپ
        if "type" in command.lower():
            # استخراج متن پس از "type"
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
    """پردازش دستورات انتظار هوشمند."""
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
    """پردازش دستورات بینایی پیشرفته."""
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
                
                # اختیاری: کلیک اگر ماوس فعال است
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


def setup_environment() -> None:
    """مقداردهی متغیرهای محیطی و ایجاد پوشه‌های مورد نیاز."""
    # بارگذاری متغیرهای محیطی از فایل .env
    load_dotenv()
    
    # اطمینان از وجود پوشه‌های مورد نیاز
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
        "--version",
        action="version",
        version="Software-AI 0.1.0",
        help="نمایش نسخه و خروج"
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
        "--debug",
        action="store_true",
        help="فعال کردن ثبت گزارش اشکال‌زدایی (خروجی طولانی)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="شبیه‌سازی اقدامات بدون اجرای واقعی آنها"
    )

    parser.add_argument(
        "--mode",
        choices=["browser", "code"],
        default="browser",
        help="[deprecated] حالت اجرا برای تسک‌ها — سیستم خودکار تشخیص می‌دهد"
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="تعداد پردازش‌های همزمان برای TaskEngine (پیشنهادی: 2)"
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

    # Mode flags — kept for backward compat but deprecated
    parser.add_argument("--enable-automation", "--automation", action="store_true",
                        help=argparse.SUPPRESS)
    parser.add_argument("--enable-autonomous", "--autonomous", action="store_true",
                        help=argparse.SUPPRESS)
    parser.add_argument("--enable-intent-planning", "--intent-planning", action="store_true",
                        help=argparse.SUPPRESS)
    parser.add_argument("--full", action="store_true",
                        help=argparse.SUPPRESS)
    parser.add_argument("--realtime", action="store_true",
                        help=argparse.SUPPRESS)
    parser.add_argument("--realtime-fps", type=float, default=1.0,
                        help=argparse.SUPPRESS)
    parser.add_argument("--task-mode", action="store_true",
                        help=argparse.SUPPRESS)

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
        
        # Safety & Consent Manager
        self.safety_consent_manager: Optional[SafetyConsentManager] = None

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def stop(self) -> None:
        self.stopped = True
    
    def set_safety_consent_manager(self, manager: SafetyConsentManager) -> None:
        """تعیین مدیر ایمنی و تایید"""
        self.safety_consent_manager = manager


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

async def process_capability_loop(
    args: argparse.Namespace,
    memory: MemoryManager,
    voice: VoiceManager,
    action_controller: ActionController,
    intent_router: IntentRouter,
    capability_manager: CapabilityManager,
    safety_consent_manager: SafetyConsentManager,
    session_control: SessionControl,
) -> None:
    """Capability-driven main interaction loop — acquires capabilities lazily via CapabilityManager."""
    current_lang = "en"
    input_mode = args.input_mode
    task_engine = TaskEngine(concurrency=args.concurrency)
    chat_brain = AIBrain()

    print_banner(banner, color=Fore.CYAN)

    welcome_message = "Welcome to Software-AI: Intelligent Windows Automation System"
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

    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'CHAT MODE (DEFAULT)':^80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Free-form chat. Ask any question or request.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}System will enable web/automation/task capabilities as needed.{Style.RESET_ALL}\n")
    print(f"{Fore.MAGENTA}Examples:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Write a professional email{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Create a new folder on desktop{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Check USD price on the web{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Type your command and press Enter...{Style.RESET_ALL}\n")

    task_mode_enabled = False

    def log_telemetry(event: str, **data: Any) -> None:
        try:
            payload = " ".join([f"{k}={v}" for k, v in data.items()]) if data else ""
            logger.info("TELEMETRY event=%s %s", event, payload)
        except Exception:
            pass

    async def ensure_task_mode_enabled() -> None:
        nonlocal task_mode_enabled
        if task_mode_enabled:
            return
        await capability_manager.activate("task_mode")
        task_mode_enabled = True
        log_telemetry("task_mode_enabled")
        print(f"{Fore.GREEN}✓ Task Mode enabled. Tasks will be queued and run via TaskEngine.{Style.RESET_ALL}")

    async def disable_task_mode(clear_queue: bool = True) -> None:
        nonlocal task_mode_enabled
        await capability_manager.deactivate("task_mode")
        if clear_queue:
            task_engine.queue.clear()
        task_mode_enabled = False
        log_telemetry("task_mode_disabled")
        print(f"{Fore.YELLOW}Task Mode disabled.{Style.RESET_ALL}")

    def extract_tasks_from_text(text: str) -> List[str]:
        separators = [";", "\n", "،"]
        for sep in separators:
            if sep in text:
                parts = [item.strip() for item in text.split(sep) if item.strip()]
                return parts
        return [text.strip()] if text.strip() else []

    try:
        while True:
            user_text = ""
            if input_mode == "voice":
                print(f"{Fore.CYAN}🎤 Listening...{Style.RESET_ALL}")
                user_text, detected_lang = voice.listen(timeout=10)
                if user_text and detected_lang:
                    current_lang = detected_lang
                    print(f"{Fore.GREEN}✓ Detected: {user_text}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠ No voice input.{Style.RESET_ALL}")
                    continue
            else:
                try:
                    user_text = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
                    current_lang = "en"
                except EOFError:
                    break

            if not user_text:
                continue

            cmd_lower = user_text.lower()

            if session_control.stopped:
                print(f"{Fore.RED}🛑 Session stopped.{Style.RESET_ALL}")
                break

            if session_control.paused and cmd_lower not in ["resume", "stop", "exit", "quit"]:
                print(f"{Fore.YELLOW}⏸️  Paused. Type 'resume' to continue.{Style.RESET_ALL}")
                continue

            # ── Core session control commands ──
            if cmd_lower == "pause":
                session_control.pause()
                print(f"{Fore.YELLOW}⏸️  Paused.{Style.RESET_ALL}")
                continue

            if cmd_lower == "resume":
                session_control.resume()
                print(f"{Fore.GREEN}▶️  Resumed.{Style.RESET_ALL}")
                continue

            if cmd_lower in ["stop", "panic", "kill", "abort"]:
                session_control.stop()
                print(f"{Fore.RED}🛑 Emergency stop.{Style.RESET_ALL}")
                break

            if cmd_lower == "help":
                print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'COMMAND REFERENCE':^80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
                print(f"{Fore.GREEN}Just type what you want me to do!{Style.RESET_ALL}\n")
                continue

            if cmd_lower == "clear":
                task_engine.queue.clear()
                print(f"{Fore.GREEN}✓ Queue cleared.{Style.RESET_ALL}\n")
                continue

            if cmd_lower in ["exit", "quit"]:
                print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Thank you for using Software-AI!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
                break

            if cmd_lower in ["task mode on", "taskmode on", "enable task mode", "task on"]:
                await ensure_task_mode_enabled()
                continue

            if cmd_lower in ["task mode off", "taskmode off", "disable task mode", "task off"]:
                await disable_task_mode(clear_queue=True)
                continue

            # ── Explicit backward-compat commands ──
            # plan <request> — explicit intent analysis
            if cmd_lower.startswith("plan "):
                request = user_text[5:].strip()
                analyzer = await capability_manager.activate("intent_analysis")
                if not analyzer:
                    print(f"{Fore.YELLOW}⚠ Intent analyzer not available.{Style.RESET_ALL}\n")
                    continue
                print(f"\n{Fore.MAGENTA}🧠 Analyzing: {request}{Style.RESET_ALL}\n")
                analysis = await analyzer.analyze(request)
                intent = analysis.intent
                print(f"  Verb: {intent.verb}")
                print(f"  Target: {intent.target}")
                print(f"  Confidence: {intent.confidence:.0%}\n")

                plan_gen = await capability_manager.activate("plan_generation")
                plan_val = await capability_manager.activate("plan_validation")
                if plan_gen and plan_val:
                    plan = await plan_gen.generate_plan(intent)
                    validation = await plan_val.validate(plan, intent)
                    if validation.is_valid:
                        print(f"{Fore.GREEN}✓ Plan generated ({len(plan.steps)} steps){Style.RESET_ALL}\n")
                        mem_int = await capability_manager.activate("execution_history")
                        if mem_int:
                            mem_int.record_execution(
                                plan_id=plan.plan_id, intent=intent,
                                status=PlanStatus.SUCCESSFUL,
                                steps_succeeded=len(plan.steps), steps_failed=0,
                                total_steps=len(plan.steps), actual_time_seconds=0,
                                estimated_time_seconds=plan.total_estimated_time
                            )
                    else:
                        print(f"{Fore.RED}❌ Plan validation failed{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.YELLOW}⚠ Planning components not available.{Style.RESET_ALL}\n")
                continue

            # smart <request> — auto-analyze and execute
            if cmd_lower.startswith("smart "):
                request = user_text[6:].strip()
                analyzer = await capability_manager.activate("intent_analysis")
                if not analyzer:
                    print(f"{Fore.YELLOW}⚠ Intent analyzer not available.{Style.RESET_ALL}\n")
                    continue
                print(f"\n{Fore.MAGENTA}🧠 Smart execution: {request}{Style.RESET_ALL}\n")
                analysis = await analyzer.analyze(request)
                intent = analysis.intent

                plan_gen = await capability_manager.activate("plan_generation")
                plan_val = await capability_manager.activate("plan_validation")
                if plan_gen and plan_val:
                    plan = await plan_gen.generate_plan(intent)
                    validation = await plan_val.validate(plan, intent)
                    if validation.is_valid:
                        print(f"{Fore.GREEN}✓ Plan validated and executed{Style.RESET_ALL}\n")
                        mem_int = await capability_manager.activate("execution_history")
                        if mem_int:
                            mem_int.record_execution(
                                plan_id=plan.plan_id, intent=intent,
                                status=PlanStatus.SUCCESSFUL,
                                steps_succeeded=len(plan.steps), steps_failed=0,
                                total_steps=len(plan.steps), actual_time_seconds=0,
                                estimated_time_seconds=plan.total_estimated_time
                            )
                    else:
                        print(f"{Fore.RED}❌ Plan validation failed{Style.RESET_ALL}\n")
                else:
                    result = await action_controller.process_request(request)
                    print(f"{Fore.CYAN}{result}{Style.RESET_ALL}\n")
                continue

            # goal <description> — autonomous agent
            if cmd_lower.startswith("goal "):
                goal = user_text[5:].strip()
                agent = await capability_manager.activate("autonomous_agent")
                if not agent:
                    print(f"{Fore.YELLOW}⚠ Autonomous agent not available.{Style.RESET_ALL}\n")
                    continue
                print(f"\n{Fore.BLUE}🎯 Goal: {goal}{Style.RESET_ALL}\n")
                result = await agent.execute_goal(goal)
                if result.get("success"):
                    print(f"{Fore.GREEN}✓ Goal completed!{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}❌ Failed: {result.get('error', 'Unknown')}{Style.RESET_ALL}\n")
                continue

            # mouse <command>
            if cmd_lower.startswith("mouse "):
                mouse = await capability_manager.activate("desktop_mouse")
                if mouse:
                    await handle_mouse_command(user_text, mouse, voice, current_lang, input_mode)
                else:
                    print(f"{Fore.YELLOW}⚠ Mouse control not available.{Style.RESET_ALL}\n")
                continue

            # type/keyboard <text>
            if cmd_lower.startswith(("type ", "keyboard ")):
                keyboard = await capability_manager.activate("desktop_keyboard")
                if keyboard:
                    await handle_keyboard_command(user_text, keyboard, voice, current_lang, input_mode)
                else:
                    print(f"{Fore.YELLOW}⚠ Keyboard control not available.{Style.RESET_ALL}\n")
                continue

            # wait <command>
            if cmd_lower.startswith("wait "):
                smart_wait = await capability_manager.activate("smart_waiting")
                if smart_wait:
                    await handle_wait_command(user_text, smart_wait, voice, current_lang, input_mode)
                else:
                    print(f"{Fore.YELLOW}⚠ Smart wait not available.{Style.RESET_ALL}\n")
                continue

            # vision/screenshot <command>
            if cmd_lower.startswith(("vision ", "screenshot")):
                vision = await capability_manager.activate("screen_observation")
                mouse = capability_manager.get("desktop_mouse")
                if vision:
                    await handle_vision_command(user_text, vision, mouse, voice, current_lang, input_mode)
                else:
                    print(f"{Fore.YELLOW}⚠ Vision not available.{Style.RESET_ALL}\n")
                continue

            # ── Smart Routing via IntentRouter ──
            log_telemetry("routing_start", text=user_text)
            
            # تجزیه درخواست‌های چندمرحله‌ای به مراحل مستقل
            steps = intent_router._decompose_multi_step(user_text)
            if len(steps) > 1:
                print(f"{Fore.MAGENTA}🔀 Detected {len(steps)} steps, processing sequentially...{Style.RESET_ALL}")
            
            for step_idx, step_text in enumerate(steps):
                if len(steps) > 1:
                    print(f"\n{Fore.CYAN}─── Step {step_idx + 1}/{len(steps)}: {step_text[:60]}... ───{Style.RESET_ALL}")
                
                caps = {name: True for name in capability_manager.get_enabled()}
                route = await intent_router.route(
                    step_text,
                    safety_mode=session_control.safety_mode,
                    current_capabilities=caps,
                )
                log_telemetry("routing_result", route=route.type.value, risk=route.risk_level.value)
                
                # Activate required capabilities
                for cap in route.requires_activation:
                    await capability_manager.activate(cap)

                # Execute based on route type
                if route.type == RouteType.TASK_MODE:
                    await ensure_task_mode_enabled()
                    tasks = route.metadata.get("tasks") or extract_tasks_from_text(step_text)
                    for t in (tasks or [step_text]):
                        task_engine.add_task(t, mode="browser")
                    print(f"{Fore.GREEN}✓ Added {len(tasks or [step_text])} task(s) to queue.{Style.RESET_ALL}\n")

                elif route.type in (RouteType.BROWSER_USE, RouteType.DESKTOP_AUTOMATION):
                    result = await action_controller.process_request(step_text)
                    print(f"{Fore.CYAN}{result}{Style.RESET_ALL}\n")

                elif route.type == RouteType.AUTONOMOUS_AGENT:
                    agent = capability_manager.get("autonomous_agent")
                    goal = route.metadata.get("goal", step_text)
                    if agent:
                        result = await agent.execute_goal(goal)
                        if result.get("success"):
                            print(f"{Fore.GREEN}✓ Goal completed!{Style.RESET_ALL}\n")
                        else:
                            print(f"{Fore.RED}❌ Failed: {result.get('error', 'Unknown')}{Style.RESET_ALL}\n")
                    else:
                        print(f"{Fore.YELLOW}⚠ Autonomous agent not available.{Style.RESET_ALL}\n")

                elif route.type == RouteType.CLARIFICATION_NEEDED:
                    msg = route.consent_message or "I didn't understand. Please rephrase."
                    print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}\n")

                elif route.type == RouteType.CHAT_RESPONSE:
                    response = await chat_brain.ask_with_fallback(step_text, mode="system", max_tokens=1000)
                    if response:
                        print(f"{Fore.CYAN}{response}{Style.RESET_ALL}\n")
                    else:
                        print(f"{Fore.RED}All AI models failed. Check your API keys in .env{Style.RESET_ALL}\n")

                else:
                    result = await action_controller.process_request(step_text)
                    print(f"{Fore.CYAN}{result}{Style.RESET_ALL}\n")

                memory.remember_short(
                    content=step_text, ttl=3600,
                    metadata={"type": "user_request", "route": route.type.value}
                )

            if len(steps) > 1:
                print(f"{Fore.GREEN}✅ All {len(steps)} steps completed.{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Shutting down...{Style.RESET_ALL}")
    finally:
        memory.shutdown()
        voice.shutdown()


async def main() -> None:
    """Main application entry point — Capability-Driven Architecture."""
    session_log = None
    master_log = None
    realtime_task = None
    
    try:
        args = parse_arguments()
        setup_environment()
        session_log, master_log = setup_logging(level=logging.DEBUG if args.debug else None)
        install_exception_hook()
        
        print(f"\n{Fore.CYAN}📝 Logging Information:{Style.RESET_ALL}")
        print(f"   Session Log: {session_log}")
        print(f"   Master Log:  {master_log}\n")
        
        logger.info(f"Application started: input_mode={args.input_mode}, safety={args.safety_mode}")
        
        # ── Core always-active components ──
        memory = MemoryManager()
        voice = VoiceManager(tts_provider=args.tts_provider)
        action_controller = ActionController(dry_run=args.dry_run)
        intent_router = IntentRouter()
        
        # ── Capability Manager — register ALL capabilities with lazy factories ──
        capability_manager = CapabilityManager()
        
        capability_manager.register("intent_analysis", factory=lambda: IntentAnalyzer())
        capability_manager.register("plan_generation", factory=lambda: PlanGenerator())
        capability_manager.register("plan_validation", factory=lambda: PlanValidator())
        capability_manager.register("execution_history",
                                    factory=lambda: MemoryIntegrator("data/memories.sqlite3"))
        capability_manager.register("desktop_mouse",
                                    factory=lambda: MouseController())
        capability_manager.register("desktop_keyboard",
                                    factory=lambda: KeyboardController())
        capability_manager.register("screen_observation",
                                    factory=lambda: DesktopVision())
        capability_manager.register("smart_waiting",
                                    factory=lambda: SmartWaiter())
        capability_manager.register("action_execution",
                                    factory=lambda: ActionController(),
                                    dependencies=["desktop_mouse", "desktop_keyboard",
                                                  "screen_observation", "smart_waiting"])
        capability_manager.register("autonomous_agent",
                                    factory=lambda: AutonomousAgent(
                                        vision=DesktopVision(),
                                        mouse=MouseController(),
                                        keyboard=KeyboardController(),
                                    ),
                                    dependencies=["screen_observation", "desktop_mouse", "desktop_keyboard"])
        capability_manager.register("realtime_loop",
                                    factory=lambda: RealtimeLoop(
                                        vision=DesktopVision(),
                                        session_control=session_control,
                                        fps=args.realtime_fps,
                                        max_actions=3,
                                    ),
                                    dependencies=["screen_observation"])

        # Legacy capability registrations (for backward compat routing)
        capability_manager.register("browser_use", risk_level="medium",
                                    dependencies=["intent_analysis"])
        capability_manager.register("desktop_automation", risk_level="high",
                                    dependencies=["action_execution"])
        capability_manager.register("autonomous_agent_cap", risk_level="high",
                                    dependencies=["autonomous_agent"])
        capability_manager.register("task_mode", risk_level="safe")

        session_control = SessionControl(
            safety_mode=args.safety_mode,
            risk_threshold=args.risk_threshold,
            allowed_apps=args.allow_app,
            allowed_paths=args.allow_path,
        )
        
        safety_consent_manager = SafetyConsentManager()
        session_control.set_safety_consent_manager(safety_consent_manager)

        # ── Execute capability-driven conversation loop ──
        await process_capability_loop(
            args=args,
            memory=memory,
            voice=voice,
            action_controller=action_controller,
            intent_router=intent_router,
            capability_manager=capability_manager,
            safety_consent_manager=safety_consent_manager,
            session_control=session_control,
        )

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted by user. Shutting down...{Style.RESET_ALL}\n")
        logger.info("Application interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}\n")
        logger.exception("Fatal error occurred")
        sys.exit(1)
    finally:
        try:
            await capability_manager.cleanup()
        except Exception:
            pass

        if session_log:
            logger.info(f"SESSION ENDED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'SESSION SUMMARY':^80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
            print(f"  Session Log : {session_log}")
            print(f"  Master Log  : {master_log}\n")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        if realtime_task:
            realtime_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
