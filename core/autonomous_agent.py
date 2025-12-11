# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""Vision-Based Autonomous Agent - مثل browser-use اما برای Windows

این Agent می‌تونه:
- با پرامپت‌های ساده کار کنه ("برو E: فولدر بساز")
- خودش تصمیم بگیره چی کلیک کنه
- با بازخورد بینایی کار کنه
- هدف‌محور باشه (نه Action‌محور)

مثال:
    تو: "برو This PC، باز کن E:, فولدر MyDocs بساز"
    
    Agent:
    1. Screenshot می‌گیره
    2. This PC رو پیدا می‌کنه
    3. کلیک می‌کنه
    4. E: رو پیدا می‌کنه
    5. کلیک می‌کنه
    6. Right Click → New Folder
    7. اسم تایپ می‌کنه
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

from core.desktop_vision import DesktopVision
from core.ai_brain import AIBrain
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController
from core.smart_wait import SmartWaiter

logger = logging.getLogger(__name__)


@dataclass
class AgentStep:
    """یک قدم از برنامه Agent."""
    step_number: int
    description: str  # "Click on This PC"
    action_type: str  # "click", "type", "wait", "screenshot"
    target: Optional[str] = None  # "This PC button"
    completed: bool = False
    result: Optional[str] = None


@dataclass
class AgentGoal:
    """هدف نهایی Agent."""
    description: str  # "Create folder MyDocs in E:"
    current_step: int = 0
    steps: list[AgentStep] = None
    completed: bool = False
    max_attempts: int = 10
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []


class AutonomousAgent:
    """Agent خودمختار برای کنترل ویندوز با بینایی.
    
    این Agent مثل browser-use کار می‌کنه:
    - پرامپت ساده می‌گیره
    - خودش برنامه می‌ریزه
    - با بینایی کار می‌کنه
    - خودش اجرا می‌کنه
    
    Usage:
        agent = AutonomousAgent()
        result = await agent.execute_goal("برو E: فولدر MyDocs بساز")
    """
    
    def __init__(
        self,
        vision: Optional[DesktopVision] = None,
        ai_brain: Optional[AIBrain] = None,
        mouse: Optional[MouseController] = None,
        keyboard: Optional[KeyboardController] = None,
    ):
        self.vision = vision or DesktopVision()
        self.ai_brain = ai_brain or AIBrain()
        self.mouse = mouse or MouseController()
        self.keyboard = keyboard or KeyboardController()
        self.waiter = SmartWaiter()
        
        # تاریخچه برای یادگیری
        self.history: list[dict[str, Any]] = []
        
    async def execute_goal(self, goal_description: str) -> dict[str, Any]:
        """اجرای یک هدف با پرامپت ساده.
        
        Args:
            goal_description: توضیح ساده هدف ("برو E: فولدر بساز")
            
        Returns:
            نتیجه اجرا شامل موفقیت و مراحل
            
        Example:
            >>> result = await agent.execute_goal("برو This PC باز کن E:")
            >>> print(result["success"])  # True
        """
        logger.info(f"🎯 New Goal: {goal_description}")
        
        # ساخت هدف
        goal = AgentGoal(description=goal_description)
        
        try:
            # مرحله 1: برنامه‌ریزی با AI
            plan = await self._create_plan(goal_description)
            goal.steps = plan
            
            logger.info(f"📋 Plan created: {len(plan)} steps")
            for step in plan:
                logger.info(f"  Step {step.step_number}: {step.description}")
            
            # مرحله 2: اجرا با حلقه بازخورد
            for step in goal.steps:
                success = await self._execute_step(step, goal)
                
                if not success:
                    logger.warning(f"⚠️ Step {step.step_number} failed, retrying...")
                    # تلاش مجدد
                    success = await self._execute_step(step, goal)
                    
                if not success:
                    logger.error(f"❌ Step {step.step_number} failed after retry")
                    return {
                        "success": False,
                        "goal": goal_description,
                        "completed_steps": step.step_number - 1,
                        "total_steps": len(plan),
                        "error": f"Failed at step {step.step_number}: {step.description}"
                    }
                
                step.completed = True
                goal.current_step = step.step_number
                
            # موفقیت!
            goal.completed = True
            logger.info(f"✅ Goal completed: {goal_description}")
            
            return {
                "success": True,
                "goal": goal_description,
                "total_steps": len(plan),
                "steps": [
                    {
                        "number": s.step_number,
                        "description": s.description,
                        "result": s.result
                    }
                    for s in goal.steps
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Goal failed: {e}")
            return {
                "success": False,
                "goal": goal_description,
                "error": str(e)
            }
    
    async def _create_plan(self, goal: str) -> list[AgentStep]:
        """ساخت برنامه اجرا با AI.
        
        AI تحلیل می‌کنه هدف چیه و چه مراحلی لازمه.
        """
        prompt = f"""You are a Windows automation planner. Break down this goal into detailed steps.

Goal: {goal}

Create a step-by-step plan. Each step should be SIMPLE and ATOMIC.

Available Actions:
1. screenshot - Take screenshot to see current state
2. find_and_click - Find element by text and click (e.g., "This PC", "E:", "New Folder")
3. type_text - Type text (e.g., folder name)
4. press_key - Press key (e.g., "enter", "escape")
5. right_click - Right click at position
6. wait - Wait for window/element

Example Plan for "Open This PC and go to E:":
1. screenshot - See desktop
2. find_and_click - Click "This PC" icon
3. wait - Wait for File Explorer to open
4. find_and_click - Click "E:" drive
5. wait - Wait for E: to open

Now create a plan for: {goal}

Return JSON array of steps:
[
  {{"step": 1, "action": "screenshot", "description": "See current state"}},
  {{"step": 2, "action": "find_and_click", "target": "This PC", "description": "Open This PC"}},
  ...
]

IMPORTANT:
- Be SPECIFIC about what to click (exact text)
- Include screenshot steps to verify state
- Include wait steps between actions
- Keep steps simple and atomic
"""
        
        response = await self.ai_brain.ask_with_fallback(prompt, mode="smart", max_tokens=1000)
        
        # Parse JSON response
        import json
        import re
        
        # استخراج JSON از پاسخ
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if not json_match:
            logger.error("❌ AI didn't return valid JSON plan")
            # Fallback: برنامه پیش‌فرض
            return [
                AgentStep(1, "Take screenshot", "screenshot"),
                AgentStep(2, f"Execute goal: {goal}", "manual", target=goal)
            ]
        
        plan_data = json.loads(json_match.group())
        
        # تبدیل به AgentStep
        steps = []
        for item in plan_data:
            step = AgentStep(
                step_number=item["step"],
                description=item["description"],
                action_type=item["action"],
                target=item.get("target")
            )
            steps.append(step)
        
        return steps
    
    async def _execute_step(self, step: AgentStep, goal: AgentGoal) -> bool:
        """اجرای یک مرحله با بازخورد بینایی.
        
        Returns:
            True اگه موفق بود، False اگه فیل شد
        """
        logger.info(f"🔧 Executing Step {step.step_number}: {step.description}")
        
        try:
            if step.action_type == "screenshot":
                # اسکرین‌شات
                screenshot_path = await self._take_screenshot()
                step.result = f"Screenshot saved: {screenshot_path}"
                return True
                
            elif step.action_type == "find_and_click":
                # پیدا کردن و کلیک
                if not step.target:
                    logger.error("❌ No target specified for find_and_click")
                    return False
                
                position = await self._find_element(step.target)
                if position:
                    self.mouse.click(position[0], position[1])
                    step.result = f"Clicked {step.target} at {position}"
                    await self.waiter.wait(1.0)  # صبر کوتاه بعد کلیک
                    return True
                else:
                    logger.warning(f"⚠️ Element not found: {step.target}")
                    step.result = f"Element not found: {step.target}"
                    return False
                    
            elif step.action_type == "type_text":
                # تایپ متن
                if not step.target:
                    logger.error("❌ No text specified for type_text")
                    return False
                
                self.keyboard.type_text(step.target)
                step.result = f"Typed: {step.target}"
                return True
                
            elif step.action_type == "press_key":
                # فشار دادن کلید
                if not step.target:
                    logger.error("❌ No key specified for press_key")
                    return False
                
                self.keyboard.press_key(step.target)
                step.result = f"Pressed key: {step.target}"
                return True
                
            elif step.action_type == "right_click":
                # Right click
                if step.target:
                    # اگه target داره، اول پیداش کن
                    position = await self._find_element(step.target)
                    if position:
                        self.mouse.right_click(position[0], position[1])
                        step.result = f"Right clicked {step.target}"
                        return True
                    return False
                else:
                    # فقط right click در موقعیت فعلی
                    import pyautogui
                    x, y = pyautogui.position()
                    self.mouse.right_click(x, y)
                    step.result = "Right clicked at current position"
                    return True
                    
            elif step.action_type == "wait":
                # انتظار
                wait_time = float(step.target) if step.target else 2.0
                await self.waiter.wait(wait_time)
                step.result = f"Waited {wait_time}s"
                return True
                
            elif step.action_type == "manual":
                # اجرای دستی (fallback)
                logger.warning(f"⚠️ Manual step: {step.description}")
                step.result = "Manual execution required"
                return True
                
            else:
                logger.error(f"❌ Unknown action type: {step.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Step execution failed: {e}")
            step.result = f"Error: {e}"
            return False
    
    async def _take_screenshot(self) -> str:
        """گرفتن اسکرین‌شات و ذخیره.
        
        Returns:
            مسیر فایل ذخیره شده
        """
        screenshot = self.vision.capture_screen()
        
        # ذخیره
        from pathlib import Path
        import datetime
        
        screenshots_dir = Path("data/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = screenshots_dir / f"agent_{timestamp}.png"
        
        screenshot.save(str(filepath))
        logger.info(f"📸 Screenshot saved: {filepath}")
        
        return str(filepath)
    
    async def _find_element(self, text: str) -> Optional[tuple[int, int]]:
        """پیدا کردن عنصر با OCR.
        
        Args:
            text: متن عنصر (مثلاً "This PC", "E:")
            
        Returns:
            (x, y) اگه پیدا شد، None اگه نشد
        """
        logger.info(f"🔍 Searching for element: {text}")
        
        # اسکرین‌شات
        screenshot = self.vision.capture_screen()
        
        # OCR
        text_boxes = self.vision.read_screen_ocr()
        
        if not text_boxes:
            logger.warning("⚠️ No text found on screen")
            return None
        
        # جستجوی fuzzy
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        for box in text_boxes:
            box_text_lower = box.text.lower()
            
            # Exact match
            if text_lower == box_text_lower:
                logger.info(f"✅ Found exact match: {box.text} at ({box.x}, {box.y})")
                return (box.x + box.width // 2, box.y + box.height // 2)
            
            # Partial match
            if text_lower in box_text_lower or box_text_lower in text_lower:
                score = len(text_lower) / max(len(text_lower), len(box_text_lower))
                if score > best_score:
                    best_score = score
                    best_match = box
        
        if best_match and best_score > 0.5:
            logger.info(f"✅ Found partial match: {best_match.text} (score: {best_score:.2f})")
            return (best_match.x + best_match.width // 2, best_match.y + best_match.height // 2)
        
        logger.warning(f"❌ Element not found: {text}")
        logger.info(f"Available text on screen: {[box.text for box in text_boxes[:10]]}")
        
        return None
    
    async def describe_screen(self) -> str:
        """توضیح وضعیت فعلی صفحه با AI Vision.
        
        Returns:
            توضیح صفحه (مثلاً "I see File Explorer with drives C, D, E")
        """
        # گرفتن اسکرین‌شات
        screenshot_path = await self._take_screenshot()
        
        # OCR برای متن‌ها
        text_boxes = self.vision.read_screen_ocr()
        texts = [box.text for box in text_boxes[:20]]  # اول 20 تا
        
        # درخواست از AI
        prompt = f"""You are looking at a Windows desktop screenshot.

Visible text on screen:
{', '.join(texts)}

Describe what you see in 1-2 sentences. What window is open? What can the user do?

Example: "I see File Explorer with drives C:, D:, E: visible. User can click on any drive to open it."
"""
        
        description = await self.ai_brain.ask_with_fallback(prompt, mode="smart", max_tokens=500)
        logger.info(f"👁️ Screen description: {description}")
        
        return description


# مثال استفاده
async def example_usage():
    """مثال استفاده از Autonomous Agent."""
    agent = AutonomousAgent()
    
    # مثال 1: باز کردن This PC
    result = await agent.execute_goal("Open This PC and navigate to E: drive")
    print(f"Result: {result}")
    
    # مثال 2: ساخت فولدر
    result = await agent.execute_goal("Go to E: drive and create a new folder called MyDocs")
    print(f"Result: {result}")
    
    # مثال 3: فارسی
    result = await agent.execute_goal("برو This PC، باز کن E:، فولدر MyDocs بساز")
    print(f"Result: {result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
