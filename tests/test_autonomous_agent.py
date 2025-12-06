# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""تست Autonomous Agent - Vision-Based Windows Control

این فایل تست می‌کنه که Agent می‌تونه:
- پرامپت‌های ساده رو بفهمه
- برنامه‌ریزی کنه
- با بینایی کار کنه
- هدف‌محور باشه
"""

import asyncio
import pytest
from pathlib import Path

from core.autonomous_agent import AutonomousAgent, AgentGoal, AgentStep
from core.desktop_vision import DesktopVision
from core.ai_brain import AIBrain


class TestAutonomousAgent:
    """تست‌های Autonomous Agent."""
    
    @pytest.mark.asyncio
    async def test_agent_creation(self):
        """تست ساخت Agent."""
        agent = AutonomousAgent()
        
        assert agent is not None
        assert agent.vision is not None
        assert agent.ai_brain is not None
        assert agent.mouse is not None
        assert agent.keyboard is not None
    
    @pytest.mark.asyncio
    async def test_create_plan_simple(self):
        """تست برنامه‌ریزی ساده."""
        agent = AutonomousAgent()
        
        # هدف ساده
        goal = "Open Notepad"
        plan = await agent._create_plan(goal)
        
        assert len(plan) > 0
        assert all(isinstance(step, AgentStep) for step in plan)
        
        # حداقل باید screenshot و launch app داشته باشه
        action_types = [step.action_type for step in plan]
        assert "screenshot" in action_types or "find_and_click" in action_types
    
    @pytest.mark.asyncio
    async def test_create_plan_complex(self):
        """تست برنامه‌ریزی پیچیده."""
        agent = AutonomousAgent()
        
        # هدف پیچیده
        goal = "Open This PC and navigate to E: drive"
        plan = await agent._create_plan(goal)
        
        assert len(plan) > 2  # حداقل 2 مرحله
        
        # باید شامل کلیک روی This PC و E: باشه
        descriptions = " ".join([step.description.lower() for step in plan])
        assert "this pc" in descriptions or "file explorer" in descriptions
        assert "e:" in descriptions or "drive" in descriptions
    
    @pytest.mark.asyncio
    async def test_take_screenshot(self):
        """تست گرفتن اسکرین‌شات."""
        agent = AutonomousAgent()
        
        screenshot_path = await agent._take_screenshot()
        
        assert screenshot_path is not None
        assert Path(screenshot_path).exists()
        assert Path(screenshot_path).suffix == ".png"
    
    @pytest.mark.asyncio
    async def test_find_element_desktop(self):
        """تست پیدا کردن عنصر روی Desktop."""
        agent = AutonomousAgent()
        
        # جستجوی عنصری که احتمالاً روی Desktop هست
        # (این تست ممکنه فیل کنه اگه Desktop خالی باشه)
        position = await agent._find_element("This PC")
        
        # اگه پیدا شد، باید tuple باشه
        if position:
            assert isinstance(position, tuple)
            assert len(position) == 2
            assert position[0] > 0 and position[1] > 0
    
    @pytest.mark.asyncio
    async def test_describe_screen(self):
        """تست توضیح صفحه."""
        agent = AutonomousAgent()
        
        description = await agent.describe_screen()
        
        assert description is not None
        assert len(description) > 10  # حداقل یه توضیح معقول
        assert isinstance(description, str)
    
    @pytest.mark.asyncio
    async def test_execute_screenshot_step(self):
        """تست اجرای مرحله اسکرین‌شات."""
        agent = AutonomousAgent()
        
        step = AgentStep(
            step_number=1,
            description="Take screenshot",
            action_type="screenshot"
        )
        
        goal = AgentGoal(description="Test goal")
        success = await agent._execute_step(step, goal)
        
        assert success is True
        assert step.result is not None
        assert "Screenshot saved" in step.result
    
    @pytest.mark.asyncio
    async def test_execute_wait_step(self):
        """تست اجرای مرحله انتظار."""
        agent = AutonomousAgent()
        
        step = AgentStep(
            step_number=1,
            description="Wait 1 second",
            action_type="wait",
            target="1.0"
        )
        
        goal = AgentGoal(description="Test goal")
        
        import time
        start = time.time()
        success = await agent._execute_step(step, goal)
        duration = time.time() - start
        
        assert success is True
        assert duration >= 0.9  # حداقل 1 ثانیه صبر کرده
    
    @pytest.mark.asyncio
    async def test_execute_type_step(self):
        """تست اجرای مرحله تایپ."""
        agent = AutonomousAgent()
        
        step = AgentStep(
            step_number=1,
            description="Type test text",
            action_type="type_text",
            target="Hello Test"
        )
        
        goal = AgentGoal(description="Test goal")
        success = await agent._execute_step(step, goal)
        
        assert success is True
        assert step.result is not None
        assert "Typed" in step.result
    
    @pytest.mark.asyncio
    async def test_execute_press_key_step(self):
        """تست اجرای مرحله فشار کلید."""
        agent = AutonomousAgent()
        
        step = AgentStep(
            step_number=1,
            description="Press Enter",
            action_type="press_key",
            target="enter"
        )
        
        goal = AgentGoal(description="Test goal")
        success = await agent._execute_step(step, goal)
        
        assert success is True
        assert step.result is not None
        assert "Pressed key" in step.result
    
    @pytest.mark.asyncio
    async def test_goal_structure(self):
        """تست ساختار هدف."""
        goal = AgentGoal(description="Test goal")
        
        assert goal.description == "Test goal"
        assert goal.current_step == 0
        assert goal.completed is False
        assert goal.max_attempts == 10
        assert goal.steps == []
    
    @pytest.mark.asyncio
    async def test_step_structure(self):
        """تست ساختار مرحله."""
        step = AgentStep(
            step_number=1,
            description="Test step",
            action_type="screenshot",
            target=None
        )
        
        assert step.step_number == 1
        assert step.description == "Test step"
        assert step.action_type == "screenshot"
        assert step.target is None
        assert step.completed is False
        assert step.result is None


class TestAutonomousAgentIntegration:
    """تست‌های یکپارچگی - نیاز به UI واقعی."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_execute_simple_goal(self):
        """تست اجرای هدف ساده (نیاز به Desktop)."""
        agent = AutonomousAgent()
        
        # هدف ساده: اسکرین‌شات
        result = await agent.execute_goal("Take a screenshot of the desktop")
        
        assert result is not None
        assert "success" in result
        # این تست ممکنه فیل کنه اگه AI درست برنامه‌ریزی نکنه
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_execute_notepad_goal(self):
        """تست باز کردن نوت‌پد (نیاز به Desktop)."""
        agent = AutonomousAgent()
        
        result = await agent.execute_goal("Open Notepad application")
        
        assert result is not None
        assert "success" in result
        
        # اگه موفق شد، نوت‌پد باید باز باشه
        if result["success"]:
            import time
            time.sleep(2)
            
            # بستن نوت‌پد
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_persian_command(self):
        """تست دستور فارسی."""
        agent = AutonomousAgent()
        
        result = await agent.execute_goal("نوت‌پد رو باز کن")
        
        assert result is not None
        assert "success" in result
        
        # cleanup
        if result["success"]:
            import time
            time.sleep(2)
            import pyautogui
            pyautogui.hotkey('alt', 'f4')


# نحوه اجرا:
# pytest tests/test_autonomous_agent.py -v
# pytest tests/test_autonomous_agent.py -v -m integration  # فقط تست‌های یکپارچگی
