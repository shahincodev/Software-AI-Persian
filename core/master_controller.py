"""
Master AI Controller - کنترلر اصلی هوش مصنوعی

این ماژول مغز اصلی سیستم است که:
1. درخواست کاربر را عمیقاً درک می‌کند
2. تصمیم می‌گیرد کدام ابزار باید استفاده شود
3. اجرا را هماهنگ می‌کند
4. پاسخ‌ها را انسانی و گویا می‌کند
"""

import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
import psutil

from core.ai_brain import AIBrain

if TYPE_CHECKING:
    from core.intelligent_agent import IntelligentSystemAgent
    from core.autonomous_agent import AutonomousAgent

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """انواع ابزارهای موجود"""
    CHAT = "chat"  # گفتگوی ساده
    SYSTEM = "system"  # اقدامات سیستمی (CPU, RAM, etc.)
    DESKTOP = "desktop"  # کنترل دسکتاپ (mouse, keyboard)
    BROWSER = "browser"  # اتوماسیون وب (browser-use)
    FILE = "file"  # عملیات فایل
    AUTONOMOUS = "autonomous"  # عامل خودمختار


@dataclass
class RoutingDecision:
    """تصمیم مسیریابی درخواست"""
    tool: ToolType
    confidence: float  # 0.0 - 1.0
    reasoning: str  # دلیل انتخاب
    parameters: Dict[str, Any]  # پارامترهای مورد نیاز


@dataclass
class ExecutionResult:
    """نتیجه اجرای درخواست"""
    success: bool
    raw_output: Any  # خروجی خام از ابزار
    human_response: str  # پاسخ انسانی شده
    tool_used: ToolType
    execution_time: float


class MasterAIController:
    """کنترلر اصلی هوش مصنوعی - مغز سیستم"""
    
    def __init__(
        self,
        system_agent: Optional['IntelligentSystemAgent'] = None,
        autonomous_agent: Optional['AutonomousAgent'] = None
    ):
        """
        مقداردهی اولیه کنترلر مادر
        
        Args:
            system_agent: عامل سیستمی (Desktop Actions)
            autonomous_agent: عامل خودمختار
        """
        self.ai_brain = AIBrain()
        self.system_agent = system_agent
        self.autonomous_agent = autonomous_agent
        logger.info("🧠 Master AI Controller initialized")
    
    async def process_request(
        self, 
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        پردازش کامل یک درخواست کاربر
        
        Args:
            user_request: درخواست کاربر به زبان طبیعی
            context: اطلاعات زمینه‌ای (history, user preferences, etc.)
        
        Returns:
            ExecutionResult با پاسخ انسانی نهایی
        """
        logger.info(f"🎯 Processing user request: {user_request[:50]}...")
        
        try:
            # مرحله 1: تشخیص نوع درخواست و انتخاب ابزار
            routing = await self._route_request(user_request, context)
            logger.info(f"📍 Routing: {routing.tool.value} (confidence: {routing.confidence:.2f})")
            logger.debug(f"💭 Reasoning: {routing.reasoning}")
            
            # مرحله 2: اجرای درخواست با ابزار مناسب
            raw_result = await self._execute_with_tool(routing, user_request)
            
            # مرحله 3: انسانی‌سازی پاسخ
            human_response = await self._humanize_response(
                user_request=user_request,
                tool_used=routing.tool,
                raw_output=raw_result,
                context=context
            )
            
            return ExecutionResult(
                success=True,
                raw_output=raw_result,
                human_response=human_response,
                tool_used=routing.tool,
                execution_time=0.0  # TODO: اضافه کردن timing
            )
            
        except Exception as e:
            logger.exception(f"❌ Error processing request: {e}")
            error_response = await self._create_error_response(user_request, str(e))
            return ExecutionResult(
                success=False,
                raw_output=None,
                human_response=error_response,
                tool_used=ToolType.CHAT,
                execution_time=0.0
            )
    
    async def _route_request(
        self, 
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        تشخیص هوشمند نوع درخواست و انتخاب ابزار مناسب
        
        این متد از AI برای درک عمیق درخواست استفاده می‌کند
        """
        prompt = f"""تو یک سیستم هوشمند مسیریابی درخواست هستی.
درخواست کاربر را تحلیل کن و تشخیص بده کدام ابزار مناسب است:

ابزارهای موجود:
1. CHAT - گفتگوی ساده، پرسش و پاسخ، توضیح مفاهیم
   مثال: "هوش مصنوعی چیست؟", "چطور برنامه‌نویسی یاد بگیرم؟"

2. SYSTEM - اطلاعات سیستم، وضعیت سخت‌افزار
   مثال: "CPU چقدره؟", "RAM آزاد چقدر دارم؟", "فضای دیسک"

3. DESKTOP - کنترل دسکتاپ، باز کردن برنامه، تایپ، کلیک
   مثال: "نوت‌پد باز کن", "روی دکمه OK کلیک کن"

4. BROWSER - جستجو در وب، اطلاعات آنلاین
   مثال: "هوا چطوره؟", "قیمت بیت‌کوین", "اخبار امروز"

5. FILE - عملیات فایل و پوشه
   مثال: "فایل test.txt بساز", "پوشه Documents رو باز کن"

6. AUTONOMOUS - کارهای پیچیده چند مرحله‌ای
   مثال: "برو به سایت X و فرم رو پر کن", "دانلود و نصب برنامه Y"

درخواست کاربر: "{user_request}"

پاسخ را به صورت JSON بده:
{{
    "tool": "CHAT|SYSTEM|DESKTOP|BROWSER|FILE|AUTONOMOUS",
    "confidence": 0.0-1.0,
    "reasoning": "دلیل انتخاب به فارسی",
    "parameters": {{"key": "value"}}
}}
"""
        
        try:
            response = await self.ai_brain.ask_with_fallback(
                prompt=prompt,
                mode="smart",
                max_tokens=500
            )
            
            # پارس کردن JSON از پاسخ AI
            import json
            import re
            
            # استخراج JSON از پاسخ
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                return RoutingDecision(
                    tool=ToolType(data.get("tool", "CHAT").lower()),
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", "No reasoning provided"),
                    parameters=data.get("parameters", {})
                )
            else:
                # Fallback: تشخیص ساده بر اساس کلمات کلیدی
                return self._fallback_routing(user_request)
                
        except Exception as e:
            logger.warning(f"AI routing failed, using fallback: {e}")
            return self._fallback_routing(user_request)
    
    def _fallback_routing(self, user_request: str) -> RoutingDecision:
        """مسیریابی ساده بر اساس کلمات کلیدی (fallback)"""
        request_lower = user_request.lower()
        
        # کلمات کلیدی برای هر ابزار
        if any(word in request_lower for word in ["باز کن", "open", "launch", "start", "اجرا"]):
            return RoutingDecision(
                tool=ToolType.DESKTOP,
                confidence=0.7,
                reasoning="کلمات کلیدی مربوط به باز کردن برنامه",
                parameters={}
            )
        
        if any(word in request_lower for word in ["cpu", "ram", "memory", "disk", "حافظه", "پردازنده"]):
            return RoutingDecision(
                tool=ToolType.SYSTEM,
                confidence=0.8,
                reasoning="درخواست اطلاعات سیستم",
                parameters={}
            )
        
        if any(word in request_lower for word in ["weather", "news", "price", "هوا", "خبر", "قیمت"]):
            return RoutingDecision(
                tool=ToolType.BROWSER,
                confidence=0.7,
                reasoning="نیاز به جستجوی اطلاعات آنلاین",
                parameters={}
            )
        
        # پیش‌فرض: گفتگو
        return RoutingDecision(
            tool=ToolType.CHAT,
            confidence=0.5,
            reasoning="درخواست گفتگویی عادی",
            parameters={}
        )
    
    async def _execute_with_tool(
        self, 
        routing: RoutingDecision,
        user_request: str
    ) -> Any:
        """اجرای درخواست با ابزار انتخاب شده"""
        
        if routing.tool == ToolType.CHAT:
            # گفتگوی ساده با AI
            return await self.ai_brain.ask_with_fallback(
                prompt=user_request,
                mode="smart",
                max_tokens=1000
            )
        
        elif routing.tool == ToolType.SYSTEM:
            # اطلاعات سیستم (CPU, RAM, Disk)
            return self._get_system_info(routing.parameters)
        
        elif routing.tool == ToolType.DESKTOP:
            # اقدامات دسکتاپ (باز کردن برنامه، تایپ، کلیک)
            if self.system_agent:
                result = await self.system_agent.process_request(user_request)
                return result
            else:
                return {"error": "System agent not initialized"}
        
        elif routing.tool == ToolType.BROWSER:
            # اتوماسیون وب - TODO: یکپارچه‌سازی با browser-use
            return {
                "status": "Browser automation not yet integrated",
                "message": "این قابلیت به زودی اضافه می‌شود"
            }
        
        elif routing.tool == ToolType.FILE:
            # عملیات فایل
            return {"status": "File operations not yet implemented"}
        
        elif routing.tool == ToolType.AUTONOMOUS:
            # عامل خودمختار
            if self.autonomous_agent:
                result = await self.autonomous_agent.execute_goal(user_request)
                return result
            else:
                return {"error": "Autonomous agent not initialized"}
        
        else:
            return {"status": "Unknown tool type"}
    
    def _get_system_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """دریافت اطلاعات سیستم"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # RAM
            memory = psutil.virtual_memory()
            ram_total_gb = memory.total / (1024 ** 3)
            ram_available_gb = memory.available / (1024 ** 3)
            ram_percent = memory.percent
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024 ** 3)
            disk_free_gb = disk.free / (1024 ** 3)
            disk_percent = disk.percent
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": cpu_count
                },
                "ram": {
                    "total_gb": round(ram_total_gb, 2),
                    "available_gb": round(ram_available_gb, 2),
                    "used_percent": ram_percent
                },
                "disk": {
                    "total_gb": round(disk_total_gb, 2),
                    "free_gb": round(disk_free_gb, 2),
                    "used_percent": disk_percent
                }
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
    
    async def _humanize_response(
        self,
        user_request: str,
        tool_used: ToolType,
        raw_output: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        تبدیل خروجی خام به پاسخ انسانی و گویا
        
        این متد از AI برای خلق پاسخ‌های طبیعی استفاده می‌کند
        """
        prompt = f"""تو یک دستیار هوشمند هستی که باید خروجی‌های فنی را به زبان انسانی تبدیل کنی.

درخواست کاربر: "{user_request}"
ابزار استفاده شده: {tool_used.value}
خروجی خام سیستم: {raw_output}

وظیفه تو:
1. خروجی خام را تحلیل کن
2. یک پاسخ کامل، واضح و دوستانه بساز
3. اگر درخواست به فارسی بود، پاسخ فارسی بده
4. اگر انگلیسی بود، پاسخ انگلیسی بده
5. اطلاعات را قابل فهم کن (نه فقط عدد و رقم خام)

مثال:
خام: {{"cpu": 45.2, "ram_free": 8192}}
انسانی: "پردازنده شما ۴۵٪ مشغول است و ۸ گیگابایت رم آزاد دارید. وضعیت سیستم خوب است!"

حالا پاسخ انسانی برای کاربر بساز (فقط متن پاسخ، بدون توضیحات اضافه):
"""
        
        try:
            response = await self.ai_brain.ask_with_fallback(
                prompt=prompt,
                mode="smart",
                max_tokens=500
            )
            return response.strip()
            
        except Exception as e:
            logger.warning(f"Humanization failed: {e}, using raw output")
            # Fallback: بازگشت خروجی خام
            if isinstance(raw_output, dict):
                return str(raw_output)
            elif isinstance(raw_output, str):
                return raw_output
            else:
                return f"نتیجه: {raw_output}"
    
    async def _create_error_response(self, user_request: str, error: str) -> str:
        """ساخت پاسخ انسانی برای خطا"""
        prompt = f"""یک خطا رخ داده است. باید یک پاسخ مودبانه و راهنما به کاربر بدهی.

درخواست کاربر: "{user_request}"
خطا: {error}

یک پاسخ دوستانه بساز که:
1. معذرت‌خواهی کند
2. مشکل را به زبان ساده توضیح دهد
3. پیشنهاد راه‌حل بدهد (اگر ممکن است)

پاسخ (فقط متن، بدون توضیحات):
"""
        
        try:
            response = await self.ai_brain.ask_with_fallback(
                prompt=prompt,
                mode="fast",
                max_tokens=300
            )
            return response.strip()
        except:
            return f"متأسفم، خطایی رخ داد: {error}"
