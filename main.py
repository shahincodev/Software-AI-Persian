#!/usr/bin/env python3
# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""
Main entry point for the AI-Powered Windows Automation System.
This module provides a CLI interface for interacting with system capabilities.
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
from core.desktop_vision import DesktopVision
from core.action_controller import ActionController
from dotenv import load_dotenv
from core.logging_config import setup_logging, install_exception_hook

colorama_init(autoreset=True)  # Enable ANSI support on Windows

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
        # Actions
        "open", "launch", "start", "run",
        "install", "setup",
        "close", "kill", "terminate", "stop",
        "hardware", "cpu", "ram", "memory", "disk", "gpu",
        # Apps
        "notepad", "calculator", "chrome", "firefox", "edge",
        "photoshop", "word", "excel", "powerpoint",
        "vscode", "visual studio", "app", "application",
        # System operations
        "process", "task manager", "system"
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
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Windows Automation System - Intelligent Task Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--mode",
        choices=["browser", "code"],
        default="browser",
        help="Operation mode: 'browser' for web interaction, 'code' for code analysis"
    )
    
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Number of concurrent tasks (default: 3)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--input-mode",
        choices=["text", "voice"],
        default="voice",
        help="Input type: 'text' for keyboard, 'voice' for microphone"
    )
    
    parser.add_argument(
        "--tts-provider",
        choices=["google-cloud", "gtts", "elevenlabs"],
        default="gtts",
        help="Text-to-speech provider: 'google-cloud' (paid, high quality), 'gtts' (free), or 'elevenlabs' (paid, high quality)"
    )
    
    parser.add_argument(
        "--enable-automation",
        action="store_true",
        help="Enable desktop automation features (Mouse, Keyboard, Smart Wait, Enhanced Vision)"
    )

    return parser.parse_args()

def print_banner(text=banner, color=Fore.CYAN) -> None:
    """Print welcome banner in CLI."""
    term_width = shutil.get_terminal_size((80, 20)).columns
    
    try:
        # If text is already ASCII art, display it directly
        lines = str(text).splitlines()
        for line in lines:
            # Calculate padding for centering
            padding = (term_width - len(line)) // 2
            if padding > 0:
                print(color + " " * padding + line + Style.RESET_ALL)
            else:
                print(color + line + Style.RESET_ALL)
    except Exception as e:
        logger.error(f"Error displaying banner: {str(e)}")
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
    smart_wait: Optional[SmartWaiter] = None,
    vision: Optional[DesktopVision] = None,
    action_controller: Optional[ActionController] = None
) -> None:
    """Process user input in an enhanced interactive loop with multilingual support and automation."""

    print_banner(banner, color=Fore.CYAN)
    welcome_message = "Hello! Welcome to the Artificial Intelligence System."
    current_lang = "en"  # Default language
    if input_mode == "voice":
        voice.speak(welcome_message, lang=current_lang, block=True)
    
    print(f"\n{welcome_message}")
    print("Please enter your tasks or ask questions. Type 'start' to execute tasks. Use Ctrl+C to exit.\n")
    
    # Display automation status
    automation_features = []
    if mouse:
        automation_features.append("Mouse Control")
    if keyboard:
        automation_features.append("Keyboard Control")
    if smart_wait:
        automation_features.append("Smart Wait")
    if vision:
        automation_features.append("Enhanced Vision")
    if action_controller:
        automation_features.append("Action Controller")
    
    if automation_features:
        automation_status = f"{Fore.GREEN}🤖 Desktop Automation: ENABLED{Style.RESET_ALL}"
        print(automation_status)
        print(f"   Features: {', '.join(automation_features)}\n")
    
    # Display available commands
    print(f"{Fore.YELLOW}📋 Available Commands:{Style.RESET_ALL}")
    print("   • start/run     - Execute queued tasks")
    print("   • exit/quit     - Exit the application")
    if mouse:
        print("   • mouse <cmd>   - Mouse commands (position, click)")
    if keyboard:
        print("   • type <text>   - Type text using keyboard")
    if smart_wait:
        print("   • wait <cmd>    - Smart wait commands (idle, window)")
    if vision:
        print("   • vision <cmd>  - Vision commands (screenshot, find image)")
    print()

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

            # Command keywords for execution or exit
            if user_text.lower() in ["run", "start"]:
                if not task_engine.queue:
                    message = "⚠ No tasks to run. Please add tasks first."
                    print(message)
                    if input_mode == "voice":
                        voice.speak(message, lang=current_lang)
                    continue
                
                # Execute tasks
                exec_message = "🚀 Executing tasks..."
                print(f"\n{exec_message}")
                if input_mode == "voice":
                    voice.speak(exec_message, lang=current_lang)

                tasks_list = list(task_engine.queue)
                results = await task_engine.run_all()

                # Process and save results
                for (task_text, task_mode), result in zip(tasks_list, results):
                    if result:
                        memory.remember_long(
                            content=result,
                            metadata={"type": "task_result", "original_task": task_text, "mode": task_mode}
                        )
                        result_message = f"✅ Task Result: {result}"
                        print(f"\n{result_message}\n")
                        if input_mode == "voice":
                            voice.speak(f"The task is complete. The result is: {result}", lang=current_lang, block=True)
                    else:
                        error_message = f"❌ Task '{task_text}' failed or had no result."
                        print(f"\n{error_message}\n")
                        if input_mode == "voice":
                            voice.speak(error_message, lang=current_lang, block=True)
                
                task_engine.queue.clear()
                print(f"\n{Fore.GREEN}✓ All tasks processed. You can add new tasks or exit.{Style.RESET_ALL}\n")

            elif user_text.lower() in ["exit", "quit"]:
                print(f"{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                break
            
            # Automation commands
            elif user_text.lower().startswith("mouse") and mouse:
                await handle_mouse_command(user_text, mouse, voice, current_lang, input_mode)
                continue
            
            elif user_text.lower().startswith(("type", "keyboard")) and keyboard:
                await handle_keyboard_command(user_text, keyboard, voice, current_lang, input_mode)
                continue
            
            elif user_text.lower().startswith("wait") and smart_wait:
                await handle_wait_command(user_text, smart_wait, voice, current_lang, input_mode)
                continue
            
            elif user_text.lower().startswith(("vision", "find", "screenshot")) and vision:
                await handle_vision_command(user_text, vision, mouse, voice, current_lang, input_mode)
                continue
            
            else:
                # Intelligent detection: Is this a system request?
                is_system_task = await _is_system_request(user_text, system_agent)
                
                if is_system_task:
                    # Direct processing with system agent
                    processing_msg = "🤖 Processing system request with AI..."
                    print(f"\n{processing_msg}")
                    if input_mode == "voice":
                        voice.speak("Processing your system request.", lang=current_lang)
                    
                    try:
                        # Intelligent execution with AI
                        system_result = await system_agent.process_request(user_text)
                        
                        # Save to memory
                        memory.remember_long(
                            content=system_result,
                            metadata={"type": "system_result", "original_request": user_text}
                        )
                        
                        # Display result
                        print(f"\n{system_result}\n")
                        if input_mode == "voice":
                            # Summarize response for voice
                            summary = _summarize_for_voice(system_result)
                            voice.speak(summary, lang=current_lang, block=True)
                    
                    except Exception as e:
                        error_msg = f"❌ Error executing system task: {str(e)}"
                        print(f"\n{error_msg}\n")
                        logger.exception("System task execution failed")
                        if input_mode == "voice":
                            voice.speak("Sorry, the system task failed.", lang=current_lang)
                else:
                    # Regular task (browser/code) - add to queue
                    memory.remember_short(
                        content=user_text,
                        ttl=3600,
                        metadata={"type": "user_task", "mode": mode, "lang": current_lang}
                    )
                    task_engine.add_task(user_text, mode=mode)
                    added_message = f"✅ Task added: {user_text}"
                    print(added_message)
                    if input_mode == "voice":
                        voice.speak(added_message, lang=current_lang)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Shutting down gracefully...{Style.RESET_ALL}")
    finally:
        memory.shutdown()
        voice.shutdown()

async def main() -> None:
    """Main application entry point."""
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Setup environment
        setup_environment()

        # Initialize logging after environment setup, respecting --debug flag
        setup_logging(level=logging.DEBUG if args.debug else None)
        install_exception_hook()
        
        # Initialize core components
        task_engine = TaskEngine(concurrency=args.concurrency)
        memory = MemoryManager()
        voice = VoiceManager(tts_provider=args.tts_provider)
        
        # Initialize intelligent system agent
        system_agent = IntelligentSystemAgent(dry_run=args.debug)
        logger.info("Intelligent system agent initialized")
        
        # Initialize automation capabilities (Week 2)
        mouse = None
        keyboard = None
        smart_wait = None
        vision = None
        action_controller = None
        
        if args.enable_automation:
            try:
                mouse = MouseController()
                keyboard = KeyboardController()
                smart_wait = SmartWaiter()
                vision = DesktopVision()
                action_controller = ActionController()
                logger.info("✅ Desktop automation enabled (Mouse, Keyboard, Smart Wait, Enhanced Vision, Action Controller)")
                print(f"{Fore.GREEN}✅ Desktop automation features enabled (including Action Controller){Style.RESET_ALL}")
            except Exception as e:
                logger.warning(f"Failed to initialize automation components: {e}")
                print(f"{Fore.YELLOW}⚠️ Error enabling automation: {e}{Style.RESET_ALL}")

        # Process user input and execute tasks
        await process_user_input(
            task_engine, 
            memory, 
            args.mode, 
            args.input_mode, 
            voice, 
            system_agent,
            mouse=mouse,
            keyboard=keyboard,
            smart_wait=smart_wait,
            vision=vision,
            action_controller=action_controller
        )

    except Exception as e:
        logger.exception("A fatal error occurred.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
