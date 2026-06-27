"""
Master AI Controller - Backward Compatible Wrapper

تذکر: این ماژول برای سازگاری با عقب حفظ شده است.
قابلیت‌های مسیریابی به core.intent_router منتقل شده است.
قابلیت‌های اطلاعات سیستم به core.system_tools منتقل شده است.

مثال جدید:
    >>> from core.intent_router import IntentRouter
    >>> router = IntentRouter()
    >>> route = await router.route("باز کن notepad")
"""

import logging
import warnings
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.ai_brain import AIBrain
from core.system_tools import get_system_info as _get_system_info

warnings.warn(
    "core.master_controller is deprecated. Use core.intent_router.IntentRouter for routing, "
    "core.system_tools.get_system_info for system info.",
    DeprecationWarning,
    stacklevel=2,
)

logger = logging.getLogger(__name__)


class ToolType(Enum):
    CHAT = "chat"
    SYSTEM = "system"
    DESKTOP = "desktop"
    BROWSER = "browser"
    FILE = "file"
    AUTONOMOUS = "autonomous"


@dataclass
class RoutingDecision:
    tool: ToolType
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]


@dataclass
class ExecutionResult:
    success: bool
    raw_output: Any
    human_response: str
    tool_used: ToolType
    execution_time: float


class MasterAIController:
    """کنترلر اصلی هوش مصنوعی (deprecated)."""

    def __init__(self, system_agent=None, autonomous_agent=None):
        self.ai_brain = AIBrain()
        self.system_agent = system_agent
        self.autonomous_agent = autonomous_agent
        logger.info("MasterAIController initialized (legacy mode)")

    async def process_request(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        return await self._legacy_process_request(user_request, context)

    async def _legacy_process_request(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        logger.info(f"Processing user request: {user_request[:50]}...")
        try:
            routing = await self._route_request(user_request, context)
            raw_result = await self._execute_with_tool(routing, user_request)
            human_response = await self._humanize_response(user_request, routing.tool, raw_result, context)
            return ExecutionResult(
                success=True, raw_output=raw_result, human_response=human_response,
                tool_used=routing.tool, execution_time=0.0,
            )
        except Exception as e:
            logger.exception(f"Error processing request: {e}")
            error_response = await self._create_error_response(user_request, str(e))
            return ExecutionResult(
                success=False, raw_output=None, human_response=error_response,
                tool_used=ToolType.CHAT, execution_time=0.0,
            )

    async def _route_request(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> RoutingDecision:
        prompt = f"""تو یک سیستم هوشمند مسیریابی درخواست هستی.
درخواست کاربر را تحلیل کن و تشخیص بده کدام ابزار مناسب است:

ابزارهای موجود:
1. CHAT - گفتگوی ساده، پرسش و پاسخ، توضیح مفاهیم
   مثال: \"هوش مصنوعی چیست؟\", \"چطور برنامه‌نویسی یاد بگیرم؟\"
2. SYSTEM - اطلاعات سیستم، وضعیت سخت‌افزار
   مثال: \"CPU چقدره؟\", \"RAM آزاد چقدر دارم؟\", \"فضای دیسک\"
3. DESKTOP - کنترل دسکتاپ، باز کردن برنامه، تایپ، کلیک
   مثال: \"نوت‌پد باز کن\", \"روی دکمه OK کلیک کن\"
4. BROWSER - جستجو در وب، اطلاعات آنلاین
   مثال: \"هوا چطوره؟\", \"قیمت بیت‌کوین\", \"اخبار امروز\"
5. FILE - عملیات فایل و پوشه
   مثال: \"فایل test.txt بساز\", \"پوشه Documents رو باز کن\"
6. AUTONOMOUS - کارهای پیچیده چند مرحله‌ای
   مثال: \"برو به سایت X و فرم رو پر کن\", \"دانلود و نصب برنامه Y\"

درخواست کاربر: "{user_request}"

پاسخ را به صورت JSON بده:
{{
    "tool": "CHAT|SYSTEM|DESKTOP|BROWSER|FILE|AUTONOMOUS",
    "confidence": 0.0-1.0,
    "reasoning": "دلیل انتخاب به فارسی",
    "parameters": {{"key": "value"}}
}}"""
        try:
            response = await self.ai_brain.ask_with_fallback(prompt=prompt, mode="smart", max_tokens=500)
            import json, re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return RoutingDecision(
                    tool=ToolType(data.get("tool", "CHAT").lower()),
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", "No reasoning provided"),
                    parameters=data.get("parameters", {}),
                )
            else:
                return self._fallback_routing(user_request)
        except Exception as e:
            logger.warning(f"AI routing failed, using fallback: {e}")
            return self._fallback_routing(user_request)

    def _fallback_routing(self, user_request: str) -> RoutingDecision:
        request_lower = user_request.lower()
        if any(word in request_lower for word in ["باز کن", "open", "launch", "start", "اجرا"]):
            return RoutingDecision(tool=ToolType.DESKTOP, confidence=0.7, reasoning="کلمات کلیدی مربوط به باز کردن برنامه", parameters={})
        if any(word in request_lower for word in ["cpu", "ram", "memory", "disk", "حافظه", "پردازنده"]):
            return RoutingDecision(tool=ToolType.SYSTEM, confidence=0.8, reasoning="درخواست اطلاعات سیستم", parameters={})
        if any(word in request_lower for word in ["weather", "news", "price", "هوا", "خبر", "قیمت"]):
            return RoutingDecision(tool=ToolType.BROWSER, confidence=0.7, reasoning="نیاز به جستجوی اطلاعات آنلاین", parameters={})
        return RoutingDecision(tool=ToolType.CHAT, confidence=0.5, reasoning="درخواست گفتگویی عادی", parameters={})

    async def _execute_with_tool(self, routing: RoutingDecision, user_request: str) -> Any:
        if routing.tool == ToolType.CHAT:
            return await self.ai_brain.ask_with_fallback(prompt=user_request, mode="smart", max_tokens=1000)
        elif routing.tool == ToolType.SYSTEM:
            return _get_system_info()
        elif routing.tool == ToolType.DESKTOP:
            if self.system_agent:
                return await self.system_agent.process_request(user_request)
            return {"error": "System agent not initialized"}
        elif routing.tool == ToolType.BROWSER:
            return {"status": "Browser automation not yet integrated"}
        elif routing.tool == ToolType.FILE:
            return {"status": "File operations not yet implemented"}
        elif routing.tool == ToolType.AUTONOMOUS:
            if self.autonomous_agent:
                return await self.autonomous_agent.execute_goal(user_request)
            return {"error": "Autonomous agent not initialized"}
        return {"status": "Unknown tool type"}

    async def _humanize_response(self, user_request: str, tool_used: ToolType, raw_output: Any, context: Optional[Dict[str, Any]] = None) -> str:
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

حالا پاسخ انسانی برای کاربر بساز (فقط متن پاسخ، بدون توضیحات اضافه):"""
        try:
            response = await self.ai_brain.ask_with_fallback(prompt=prompt, mode="smart", max_tokens=500)
            return response.strip()
        except Exception as e:
            logger.warning(f"Humanization failed: {e}, using raw output")
            if isinstance(raw_output, dict):
                return str(raw_output)
            elif isinstance(raw_output, str):
                return raw_output
            return f"نتیجه: {raw_output}"

    async def _create_error_response(self, user_request: str, error: str) -> str:
        prompt = f"""یک خطا رخ داده است. باید یک پاسخ مودبانه و راهنما به کاربر بدهی.

درخواست کاربر: "{user_request}"
خطا: {error}

یک پاسخ دوستانه بساز که:
1. معذرت‌خواهی کند
2. مشکل را به زبان ساده توضیح دهد
3. پیشنهاد راه‌حل بدهد (اگر ممکن است)

پاسخ (فقط متن، بدون توضیحات):"""
        try:
            response = await self.ai_brain.ask_with_fallback(prompt=prompt, mode="fast", max_tokens=300)
            return response.strip()
        except:
            return f"متأسفم، خطایی رخ داد: {error}"
