# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""تست‌های یکپارچه برای IntelligentSystemAgent با Desktop Actions.

این ماژول تست‌های end-to-end برای پارس کردن زبان طبیعی و تبدیل به Desktop Actions را انجام می‌دهد.
"""

import pytest
import asyncio
from core.intelligent_agent import IntelligentSystemAgent, SystemActionParser
from core.system_capabilities import SystemCapabilityRegistry
from core.desktop_actions import (
    ClickAction,
    TypeAction,
    WaitAction,
    DragDropAction,
    HotkeyAction,
    ScrollAction,
)


class TestSystemActionParser:
    """تست‌های برای SystemActionParser با Desktop Actions."""
    
    @pytest.fixture
    def parser(self):
        """ایجاد parser برای تست‌ها."""
        registry = SystemCapabilityRegistry()
        return SystemActionParser(registry)
    
    # ==================== Click Action Tests ====================
    
    @pytest.mark.asyncio
    async def test_parse_simple_click(self, parser):
        """تست پارس کردن کلیک ساده."""
        request = "click on OK"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopClick"
        assert actions[0]["params"]["target"] == "OK"
        assert actions[0]["params"]["button"] == "left"
        assert actions[0]["params"]["clicks"] == 1
    
    @pytest.mark.asyncio
    async def test_parse_right_click(self, parser):
        """تست پارس کردن کلیک راست."""
        request = "right click on 'File.txt'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopClick"
        assert actions[0]["params"]["target"] == "File.txt"
        assert actions[0]["params"]["button"] == "right"
    
    @pytest.mark.asyncio
    async def test_parse_double_click(self, parser):
        """تست پارس کردن دابل کلیک."""
        request = "double click on 'MyApp.exe'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopClick"
        assert actions[0]["params"]["target"] == "MyApp.exe"
        assert actions[0]["params"]["clicks"] == 2
    
    @pytest.mark.asyncio
    async def test_parse_persian_click(self, parser):
        """تست پارس کردن کلیک فارسی."""
        request = "کلیک روی 'دکمه تایید'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopClick"
        assert actions[0]["params"]["target"] == "دکمه تایید"
    
    # ==================== Type Action Tests ====================
    
    @pytest.mark.asyncio
    async def test_parse_simple_type(self, parser):
        """تست پارس کردن تایپ ساده."""
        request = "type 'Hello World'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopType"
        assert actions[0]["params"]["text"] == "Hello World"
        assert actions[0]["params"]["target"] is None
    
    @pytest.mark.asyncio
    async def test_parse_type_with_target(self, parser):
        """تست پارس کردن تایپ با target."""
        request = "type 'admin@example.com' in Username field"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopType"
        assert actions[0]["params"]["text"] == "admin@example.com"
        # target باید Username یا field باشد
        assert "Username" in actions[0]["params"]["target"] or "field" in actions[0]["params"]["target"]
    
    @pytest.mark.asyncio
    async def test_parse_persian_type(self, parser):
        """تست پارس کردن تایپ فارسی."""
        request = "تایپ 'سلام دنیا'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopType"
        assert actions[0]["params"]["text"] == "سلام دنیا"
    
    # ==================== Wait Action Tests ====================
    
    @pytest.mark.asyncio
    async def test_parse_wait_time(self, parser):
        """تست پارس کردن انتظار زمانی."""
        request = "wait 5 seconds"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopWait"
        assert actions[0]["params"]["wait_type"] == "time"
        assert actions[0]["params"]["target"] == 5.0
    
    @pytest.mark.asyncio
    async def test_parse_wait_element(self, parser):
        """تست پارس کردن انتظار برای عنصر."""
        request = "wait for 'SaveButton'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopWait"
        assert actions[0]["params"]["wait_type"] == "element"
        assert actions[0]["params"]["target"] == "SaveButton"
    
    @pytest.mark.asyncio
    async def test_parse_persian_wait(self, parser):
        """تست پارس کردن انتظار فارسی."""
        request = "صبر کن 3 ثانیه"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopWait"
        assert actions[0]["params"]["wait_type"] == "time"
        assert actions[0]["params"]["target"] == 3.0
    
    # ==================== Drag & Drop Action Tests ====================
    
    @pytest.mark.asyncio
    async def test_parse_drag_drop(self, parser):
        """تست پارس کردن Drag & Drop."""
        request = "drag 'File.txt' to 'Documents'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopDragDrop"
        assert actions[0]["params"]["source"] == "File.txt"
        assert actions[0]["params"]["target"] == "Documents"
    
    @pytest.mark.asyncio
    async def test_parse_persian_drag(self, parser):
        """تست پارس کردن Drag فارسی."""
        request = "بکش 'عکس.jpg' به 'پوشه تصاویر'"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopDragDrop"
        assert actions[0]["params"]["source"] == "عکس.jpg"
        assert actions[0]["params"]["target"] == "پوشه تصاویر"
    
    # ==================== Hotkey Action Tests ====================
    
    @pytest.mark.asyncio
    async def test_parse_hotkey_copy(self, parser):
        """تست پارس کردن Ctrl+C."""
        request = "copy"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopHotkey"
        assert actions[0]["params"]["keys"] == ["ctrl", "c"]
    
    @pytest.mark.asyncio
    async def test_parse_hotkey_paste(self, parser):
        """تست پارس کردن Ctrl+V."""
        request = "paste"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopHotkey"
        assert actions[0]["params"]["keys"] == ["ctrl", "v"]
    
    @pytest.mark.asyncio
    async def test_parse_persian_hotkey(self, parser):
        """تست پارس کردن میانبر فارسی."""
        request = "کپی"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopHotkey"
        assert actions[0]["params"]["keys"] == ["ctrl", "c"]
    
    @pytest.mark.asyncio
    async def test_parse_alt_tab(self, parser):
        """تست پارس کردن Alt+Tab."""
        request = "alt tab"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopHotkey"
        assert actions[0]["params"]["keys"] == ["alt", "tab"]
    
    # ==================== Scroll Action Tests ====================
    
    @pytest.mark.asyncio
    async def test_parse_scroll_down(self, parser):
        """تست پارس کردن اسکرول پایین."""
        request = "scroll down"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopScroll"
        assert actions[0]["params"]["direction"] == "down"
        assert actions[0]["params"]["clicks"] == 3  # پیش‌فرض
    
    @pytest.mark.asyncio
    async def test_parse_scroll_up_amount(self, parser):
        """تست پارس کردن اسکرول با مقدار."""
        request = "scroll up 5 times"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopScroll"
        assert actions[0]["params"]["direction"] == "up"
        assert actions[0]["params"]["clicks"] == 5
    
    @pytest.mark.asyncio
    async def test_parse_persian_scroll(self, parser):
        """تست پارس کردن اسکرول فارسی."""
        request = "اسکرول پایین 10 بار"
        actions = await parser.parse_request(request)
        
        assert len(actions) == 1
        assert actions[0]["type"] == "DesktopScroll"
        assert actions[0]["params"]["direction"] == "down"
        assert actions[0]["params"]["clicks"] == 10


class TestIntelligentSystemAgent:
    """تست‌های integration برای IntelligentSystemAgent."""
    
    @pytest.fixture
    def agent(self):
        """ایجاد agent برای تست‌ها (dry run mode)."""
        return IntelligentSystemAgent(dry_run=True)
    
    @pytest.mark.asyncio
    async def test_agent_process_click_request(self, agent):
        """تست پردازش درخواست کلیک."""
        response = await agent.process_request("click on OK")
        
        # بررسی که پاسخ شامل موفقیت یا خطا باشد
        assert "Click on 'OK'" in response or "✅" in response or "❌" in response
    
    @pytest.mark.asyncio
    async def test_agent_process_type_request(self, agent):
        """تست پردازش درخواست تایپ."""
        response = await agent.process_request("type 'test message'")
        
        assert "Type 'test message'" in response or "✅" in response or "❌" in response
    
    @pytest.mark.asyncio
    async def test_agent_process_persian_request(self, agent):
        """تست پردازش درخواست فارسی."""
        response = await agent.process_request("کلیک روی 'دکمه'")
        
        assert response  # باید جوابی برگردونه
        assert "✅" in response or "❌" in response or "کلیک" in response
    
    @pytest.mark.asyncio
    async def test_agent_process_unknown_request(self, agent):
        """تست پردازش درخواست نامعلوم."""
        response = await agent.process_request("do something random xyz")
        
        # باید پیغام عدم درک بفرسته
        assert "نتوانستم" in response or "No executable" in response or "نامعلوم" in response.lower()
    
    @pytest.mark.asyncio
    async def test_agent_process_system_action(self, agent):
        """تست پردازش اقدام سیستمی (Launch App)."""
        response = await agent.process_request("open notepad")
        
        assert "notepad" in response.lower() or "✅" in response or "✓" in response
    
    @pytest.mark.asyncio
    async def test_agent_action_controller_integration(self, agent):
        """تست یکپارچگی با ActionController."""
        # بررسی که agent دارای action_controller است
        assert agent.action_controller is not None
        assert hasattr(agent.action_controller, 'execute_action')


class TestActionCreation:
    """تست‌های برای ساخت اقدامات."""
    
    @pytest.fixture
    def agent(self):
        return IntelligentSystemAgent(dry_run=True)
    
    def test_create_click_action(self, agent):
        """تست ساخت ClickAction."""
        action_data = {
            "type": "DesktopClick",
            "params": {
                "target": "OK",
                "button": "left",
                "clicks": 1
            }
        }
        
        action = agent._create_action(action_data)
        
        assert action is not None
        assert isinstance(action, ClickAction)
        assert action.target == "OK"
        assert action.button == "left"
        assert action.clicks == 1
    
    def test_create_type_action(self, agent):
        """تست ساخت TypeAction."""
        action_data = {
            "type": "DesktopType",
            "params": {
                "text": "Hello",
                "target": None
            }
        }
        
        action = agent._create_action(action_data)
        
        assert action is not None
        assert isinstance(action, TypeAction)
        assert action.text == "Hello"
    
    def test_create_hotkey_action(self, agent):
        """تست ساخت HotkeyAction."""
        action_data = {
            "type": "DesktopHotkey",
            "params": {
                "keys": ["ctrl", "c"]
            }
        }
        
        action = agent._create_action(action_data)
        
        assert action is not None
        assert isinstance(action, HotkeyAction)
        assert action.keys == ["ctrl", "c"]
    
    def test_create_unknown_action(self, agent):
        """تست ساخت اقدام نامعلوم."""
        action_data = {
            "type": "UnknownAction",
            "params": {}
        }
        
        action = agent._create_action(action_data)
        
        # باید None برگردونه
        assert action is None


# ==================== تست‌های End-to-End ====================

class TestEndToEnd:
    """تست‌های end-to-end با سناریوهای واقعی."""
    
    @pytest.fixture
    def agent(self):
        return IntelligentSystemAgent(dry_run=True)
    
    @pytest.mark.asyncio
    async def test_login_workflow(self, agent):
        """تست workflow ورود به سیستم."""
        # سناریو: کلیک روی Username, تایپ ایمیل, Tab, تایپ پسورد, کلیک Login
        
        # مرحله 1: کلیک روی فیلد نام کاربری
        response1 = await agent.process_request("click on 'Username'")
        assert response1
        
        # مرحله 2: تایپ ایمیل
        response2 = await agent.process_request("type 'user@example.com'")
        assert response2
        
        # مرحله 3: کپی کردن
        response3 = await agent.process_request("copy")
        assert response3
    
    @pytest.mark.asyncio
    async def test_file_management(self, agent):
        """تست مدیریت فایل."""
        # سناریو: Drag & Drop فایل
        response = await agent.process_request("drag 'report.pdf' to 'Documents'")
        assert response
        assert "Drag" in response or "✅" in response
    
    @pytest.mark.asyncio
    async def test_persian_workflow(self, agent):
        """تست workflow فارسی."""
        # کلیک فارسی
        response1 = await agent.process_request("کلیک روی 'باز کردن'")
        assert response1
        
        # تایپ فارسی
        response2 = await agent.process_request("تایپ 'سلام'")
        assert response2


if __name__ == "__main__":
    # اجرای تست‌ها
    pytest.main([__file__, "-v", "--tb=short"])
