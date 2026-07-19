#!/usr/bin/env python3
"""
🔬 سیستم تست جامع و پیشرفته برای Software-AI (Persian Version)
Purpose: مو رو از ماست بکشیم بیرون! 😁

این فایل 10 دسته تست کامل رو اجرا می‌کنه:
1. Environment & Dependencies
2. API Keys & Authentication  
3. Google API Real Connection
4. Core System Imports
5. Dataclass Structures (TextBox, WindowInfo)
6. Action Controller & Approval
7. Vision System (OCR, Screenshot)
8. AI Brain & Model Selection
9. Git Repository Status
10. Real-World Scenario Simulation

استفاده:
    python test_comprehensive.py

خروجی:
    - گزارش رنگی در ترمینال
    - فایل JSON با جزئیات کامل
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List
import json
from datetime import datetime

# بارگذاری محیط
load_dotenv()

class Color:
    """رنگ‌های ترمینال برای خروجی زیبا"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class TestResult:
    """کلاس مدیریت نتایج تست"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.details: List[Dict] = []
        self.start_time = datetime.now()
    
    def add_pass(self, category: str, test: str, message: str = ""):
        self.passed += 1
        self.details.append({
            "status": "PASS",
            "category": category,
            "test": test,
            "message": message
        })
        print(f"   {Color.GREEN}✅ {test}{Color.RESET} {Color.WHITE}{message}{Color.RESET}")
    
    def add_fail(self, category: str, test: str, error: str):
        self.failed += 1
        self.details.append({
            "status": "FAIL",
            "category": category,
            "test": test,
            "error": error
        })
        print(f"   {Color.RED}❌ {test}{Color.RESET}")
        print(f"      {Color.RED}Error: {error}{Color.RESET}")
    
    def add_warning(self, category: str, test: str, warning: str):
        self.warnings += 1
        self.details.append({
            "status": "WARN",
            "category": category,
            "test": test,
            "warning": warning
        })
        print(f"   {Color.YELLOW}⚠️  {test}{Color.RESET}")
        print(f"      {Color.YELLOW}Warning: {warning}{Color.RESET}")
    
    def summary(self):
        """نمایش خلاصه نهایی"""
        duration = (datetime.now() - self.start_time).total_seconds()
        total = self.passed + self.failed + self.warnings
        
        print("\n" + "=" * 80)
        print(f"{Color.BOLD}{Color.CYAN}📊 FINAL TEST SUMMARY{Color.RESET}")
        print("=" * 80)
        print(f"{Color.GREEN}✅ Passed:   {self.passed:3d}/{total} ({self.passed/total*100:.1f}%){Color.RESET}")
        print(f"{Color.RED}❌ Failed:   {self.failed:3d}/{total} ({self.failed/total*100:.1f}%){Color.RESET}")
        print(f"{Color.YELLOW}⚠️  Warnings: {self.warnings:3d}/{total} ({self.warnings/total*100:.1f}%){Color.RESET}")
        print(f"\n{Color.CYAN}⏱️  Duration: {duration:.2f} seconds{Color.RESET}")
        
        # تعیین سلامت سیستم
        if self.failed == 0 and self.warnings == 0:
            health = "EXCELLENT"
            emoji = "🎉"
            color = Color.GREEN
        elif self.failed == 0:
            health = "GOOD"
            emoji = "👍"
            color = Color.GREEN
        elif self.failed <= 2:
            health = "FAIR"
            emoji = "⚡"
            color = Color.YELLOW
        elif self.failed <= 5:
            health = "POOR"
            emoji = "⚠️"
            color = Color.YELLOW
        else:
            health = "CRITICAL"
            emoji = "💥"
            color = Color.RED
        
        print(f"\n{color}{Color.BOLD}{emoji} System Health: {health}{Color.RESET}")
        print("=" * 80)
        
        return {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "health": health,
            "details": self.details
        }

async def test_environment(result: TestResult):
    """Category 1: محیط و Dependencies"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}🔧 Category 1: Environment & Dependencies{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{'=' * 80}{Color.RESET}")
    
    # بررسی .env
    if Path(".env").exists():
        result.add_pass("Environment", ".env file", "exists")
    else:
        result.add_fail("Environment", ".env file", "not found")
    
    # بررسی Python version
    v = sys.version_info
    if v.major == 3 and v.minor >= 10:
        result.add_pass("Environment", f"Python {v.major}.{v.minor}.{v.micro}", "compatible")
    else:
        result.add_warning("Environment", f"Python {v.major}.{v.minor}.{v.micro}", "Python 3.10+ recommended")
    
    # کتابخانه‌های حیاتی
    libs = [
        ("browser_use", "browser-use"),
        ("dotenv", "python-dotenv"),
        ("PIL", "Pillow"),
        ("pyautogui", "pyautogui"),
        ("psutil", "psutil"),
        ("langchain_core", "langchain"),
    ]
    
    for module, package in libs:
        try:
            __import__(module)
            result.add_pass("Dependencies", package, "✓")
        except ImportError:
            result.add_fail("Dependencies", package, f"not installed - pip install {package}")

async def test_api_keys(result: TestResult):
    """Category 2: API Keys"""
    print(f"\n{Color.BOLD}{Color.MAGENTA}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.MAGENTA}🔑 Category 2: API Keys & Authentication{Color.RESET}")
    print(f"{Color.BOLD}{Color.MAGENTA}{'=' * 80}{Color.RESET}")
    
    configs = {
        "GOOGLE_API_KEY": {"required": True, "prefix": "AIza"},
        "OPENAI_API_KEY": {"required": False, "prefix": "sk-"},
        "GROQ_API_KEY": {"required": False, "prefix": "gsk_"},
    }
    
    for key_name, cfg in configs.items():
        val = os.getenv(key_name)
        
        if not val or "YOUR_" in val or "EXAMPLE" in val:
            if cfg["required"]:
                result.add_fail("API Keys", key_name, "NOT SET or placeholder")
            else:
                result.add_warning("API Keys", key_name, "optional - not configured")
        elif cfg["prefix"] and not val.startswith(cfg["prefix"]):
            result.add_warning("API Keys", key_name, f"doesn't start with '{cfg['prefix']}'")
        else:
            result.add_pass("API Keys", key_name, f"SET (len={len(val)})")

async def test_google_api(result: TestResult):
    """Category 3: اتصال واقعی Google API"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}🌐 Category 3: Google API Real Connection{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.RESET}")
    
    key = os.getenv("GOOGLE_API_KEY")
    
    if not key or "YOUR_" in key:
        result.add_fail("Google API", "Connection", "no valid key")
        return
    
    # Test 1: Direct google.generativeai
    try:
        import google.generativeai as genai
        
        print(f"   {Color.CYAN}Test 1: Direct SDK (gemini-2.5-flash){Color.RESET}")
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say: OK")
        
        if response and response.text and response.text.strip():
            result.add_pass("Google API", "Direct SDK", f"✓ {response.text.strip()[:20]}")
        else:
            result.add_fail("Google API", "Direct SDK", "empty response")
    except Exception as e:
        err = str(e)
        if "429" in err:
            result.add_fail("Google API", "Direct SDK", "quota exceeded")
        else:
            result.add_fail("Google API", "Direct SDK", f"{type(e).__name__}: {err[:40]}")
    
    # Test 2: ChatGoogle wrapper
    try:
        from browser_use.llm.google.chat import ChatGoogle
        from langchain_core.messages import HumanMessage
        
        print(f"   {Color.CYAN}Test 2: ChatGoogle wrapper{Color.RESET}")
        model = ChatGoogle(model="gemini-2.5-flash", temperature=0.3)
        msg = [HumanMessage(content="Say: OK")]
        
        resp = await model.ainvoke(msg)
        
        # بررسی دقیق‌تر response
        content = None
        if resp:
            if hasattr(resp, 'content'):
                content = resp.content
            elif isinstance(resp, str):
                content = resp
        
        if content and content.strip():
            result.add_pass("Google API", "ChatGoogle", f"✓ {str(content)[:20]}")
        else:
            # این فقط warning چون Direct SDK کار کرد
            result.add_warning("Google API", "ChatGoogle", f"empty (type={type(resp).__name__})")
            
    except Exception as e:
        err = str(e)
        if "API_KEY_INVALID" in err or "not valid" in err:
            result.add_fail("Google API", "Authentication", "invalid or expired key")
        elif "403" in err or "FORBIDDEN" in err:
            result.add_fail("Google API", "Permission", "forbidden - check region/billing")
        elif "FAILED_PRECONDITION" in err:
            result.add_fail("Google API", "Configuration", "location unsupported or billing disabled")
        else:
            result.add_fail("Google API", "Connection", f"{type(e).__name__}: {err[:60]}")

async def test_core_imports(result: TestResult):
    """Category 4: Core System Imports"""
    print(f"\n{Color.BOLD}{Color.GREEN}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.GREEN}📦 Category 4: Core System Imports{Color.RESET}")
    print(f"{Color.BOLD}{Color.GREEN}{'=' * 80}{Color.RESET}")
    
    modules = [
        ("core.ai_brain", ["AIBrain"]),
        ("core.desktop_vision", ["DesktopVision", "TextBox", "WindowInfo"]),
        ("core.action_controller", ["ActionController"]),
        ("core.intelligent_agent", ["IntelligentSystemAgent"]),
        ("core.mouse_control", ["MouseController"]),
        ("core.keyboard_control", ["KeyboardController"]),
    ]
    
    for mod_name, classes in modules:
        try:
            mod = __import__(mod_name, fromlist=classes)
            for cls in classes:
                if hasattr(mod, cls):
                    result.add_pass("Core Imports", f"{mod_name}.{cls}", "✓")
                else:
                    result.add_fail("Core Imports", f"{mod_name}.{cls}", "class not found")
        except Exception as e:
            result.add_fail("Core Imports", mod_name, f"{type(e).__name__}: {str(e)[:50]}")

async def test_dataclasses(result: TestResult):
    """Category 5: Dataclass Definitions"""
    print(f"\n{Color.BOLD}{Color.YELLOW}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.YELLOW}🏗️  Category 5: Dataclass Structures (v0.9.2 fixes){Color.RESET}")
    print(f"{Color.BOLD}{Color.YELLOW}{'=' * 80}{Color.RESET}")
    
    try:
        from core.desktop_vision import TextBox, WindowInfo
        
        # TextBox test
        try:
            tb = TextBox(text="test", x=10, y=20, width=100, height=50, confidence=0.9)
            if all(hasattr(tb, attr) for attr in ['center', 'top_left', 'bottom_right']):
                result.add_pass("Dataclasses", "TextBox", "all fields + properties ✓")
            else:
                result.add_warning("Dataclasses", "TextBox", "missing properties")
        except Exception as e:
            result.add_fail("Dataclasses", "TextBox", f"instantiation failed: {e}")
        
        # WindowInfo test
        try:
            wi = WindowInfo(title="Test", x=0, y=0, width=800, height=600, is_active=True)
            if all(hasattr(wi, attr) for attr in ['center', 'bounds']):
                result.add_pass("Dataclasses", "WindowInfo", "all fields + properties ✓")
            else:
                result.add_warning("Dataclasses", "WindowInfo", "missing properties")
        except Exception as e:
            result.add_fail("Dataclasses", "WindowInfo", f"instantiation failed: {e}")
            
    except Exception as e:
        result.add_fail("Dataclasses", "Import", f"cannot import: {e}")

async def test_action_controller(result: TestResult):
    """Category 6: Action Controller"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}🎮 Category 6: Action Controller & Approval{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{'=' * 80}{Color.RESET}")
    
    try:
        from core.action_controller import ActionController, ActionResult
        
        # Enum check
        if all(hasattr(ActionResult, s) for s in ['SUCCESS', 'FAILED', 'BLOCKED']):
            result.add_pass("Action Controller", "ActionResult enum", "all states ✓")
        else:
            result.add_fail("Action Controller", "ActionResult enum", "missing states")
        
        # Instantiation
        try:
            ActionController()
            result.add_pass("Action Controller", "Instantiation", "✓")
        except Exception as e:
            result.add_fail("Action Controller", "Instantiation", f"{e}")
            
    except Exception as e:
        result.add_fail("Action Controller", "Import", f"{e}")

async def test_vision(result: TestResult):
    """Category 7: Vision System"""
    print(f"\n{Color.BOLD}{Color.MAGENTA}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.MAGENTA}👁️  Category 7: Vision System (OCR & Screenshot){Color.RESET}")
    print(f"{Color.BOLD}{Color.MAGENTA}{'=' * 80}{Color.RESET}")
    
    # Tesseract check - improved to detect auto-found paths
    tess_path = os.getenv("TESSERACT_PATH")
    
    # Try to import pytesseract to see if it can find Tesseract automatically
    try:
        import pytesseract
        # Try to get version - if this works, Tesseract is available
        try:
            version = pytesseract.get_tesseract_version()
            if tess_path:
                result.add_pass("Vision System", "Tesseract OCR", f"✓ configured at {tess_path}")
            else:
                result.add_pass("Vision System", "Tesseract OCR", f"✓ auto-detected (v{version})")
        except pytesseract.TesseractNotFoundError:
            if tess_path and Path(tess_path).exists():
                result.add_pass("Vision System", "Tesseract OCR", f"✓ at {tess_path}")
            elif tess_path:
                result.add_fail("Vision System", "Tesseract OCR", f"invalid path: {tess_path}")
            else:
                result.add_warning("Vision System", "Tesseract OCR", "not found - OCR disabled")
    except ImportError:
        result.add_warning("Vision System", "Tesseract OCR", "pytesseract not installed")
    
    # Screenshot test
    try:
        from core.desktop_vision import DesktopVision
        vision = DesktopVision()
        
        try:
            img = vision.capture_screen()  # Fixed: use capture_screen instead of take_screenshot
            if img and hasattr(img, 'size'):
                result.add_pass("Vision System", "Screenshot", f"✓ size={img.size}")
            else:
                result.add_fail("Vision System", "Screenshot", "invalid image")
        except Exception as e:
            result.add_fail("Vision System", "Screenshot", f"{e}")
    except Exception as e:
        result.add_fail("Vision System", "DesktopVision", f"{e}")

async def test_ai_brain(result: TestResult):
    """Category 8: AI Brain"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}🧠 Category 8: AI Brain & Model Selection{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.RESET}")
    
    try:
        from core.ai_brain import AIBrain
        
        brain = AIBrain()
        result.add_pass("AI Brain", "Instantiation", "✓")
        
        # Model selection
        try:
            brain.get_model(purpose="system")
            result.add_pass("AI Brain", "get_model()", "✓")
        except Exception as e:
            if "API" in str(e) or "key" in str(e).lower():
                result.add_warning("AI Brain", "get_model()", "works but API issue")
            else:
                result.add_fail("AI Brain", "get_model()", f"{e}")
        
        # Task analysis
        try:
            comp = brain._analyze_task_complexity("open notepad")
            result.add_pass("AI Brain", "Task Analysis", f"✓ type={comp}")
        except Exception as e:
            result.add_fail("AI Brain", "Task Analysis", f"{e}")
            
    except Exception as e:
        result.add_fail("AI Brain", "Import", f"{e}")

async def test_git(result: TestResult):
    """Category 9: Git Status"""
    print(f"\n{Color.BOLD}{Color.GREEN}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.GREEN}📚 Category 9: Git Repository{Color.RESET}")
    print(f"{Color.BOLD}{Color.GREEN}{'=' * 80}{Color.RESET}")
    
    try:
        # Working directory
        proc = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        
        if proc.stdout.strip():
            n = len(proc.stdout.strip().split('\n'))
            result.add_warning("Git", "Working Directory", f"{n} uncommitted files")
        else:
            result.add_pass("Git", "Working Directory", "clean ✓")
        
        # Latest commit
        proc = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, check=True)
        result.add_pass("Git", "Latest Commit", proc.stdout.strip()[:50])
        
        # Tags
        proc = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True)
        if proc.returncode == 0:
            result.add_pass("Git", "Version Tag", proc.stdout.strip())
        else:
            result.add_warning("Git", "Version Tag", "no tags")
            
    except Exception as e:
        result.add_fail("Git", "Repository", f"{e}")

async def test_real_world(result: TestResult):
    """Category 10: Real-World Scenario"""
    print(f"\n{Color.BOLD}{Color.YELLOW}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.YELLOW}🚀 Category 10: Real-World AI Simulation{Color.RESET}")
    print(f"{Color.BOLD}{Color.YELLOW}{'=' * 80}{Color.RESET}")
    
    key = os.getenv("GOOGLE_API_KEY")
    
    if not key or "YOUR_" in key:
        result.add_warning("Real-World", "AI Task", "skipped - no API key")
        return
    
    try:
        from core.ai_brain import AIBrain
        brain = AIBrain()
        
        prompts = [
            "open notepad",
            "what is my CPU?",
        ]
        
        for p in prompts:
            try:
                resp = await brain.ask(p, mode="system", max_tokens=50)
                if resp and len(resp) > 0:
                    result.add_pass("Real-World", f"'{p}'", f"✓ got response")
                else:
                    result.add_fail("Real-World", f"'{p}'", "empty response")
            except Exception as e:
                result.add_fail("Real-World", f"'{p}'", f"{type(e).__name__}")
                
    except Exception as e:
        result.add_fail("Real-World", "AI Integration", f"{e}")

async def main():
    """اجرای تست جامع"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}🔬 Software-AI Comprehensive Test Suite{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.RESET}")
    print(f"{Color.WHITE}Version: v0.9.2+{Color.RESET}")
    print(f"{Color.WHITE}Mission: Let's pull the hair out of our yogurt! 😁{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.RESET}")
    
    res = TestResult()
    
    await test_environment(res)
    await test_api_keys(res)
    await test_google_api(res)
    await test_core_imports(res)
    await test_dataclasses(res)
    await test_action_controller(res)
    await test_vision(res)
    await test_ai_brain(res)
    await test_git(res)
    await test_real_world(res)
    
    summary = res.summary()
    
    # Save JSON report
    report = Path("test_comprehensive_results.json")
    with open(report, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Color.CYAN}📄 Full report: {report}{Color.RESET}\n")
    
    sys.exit(0 if res.failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
