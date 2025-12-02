# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""لایهٔ ساده برای انتخاب مدل‌های LLM.

اینجا از lazy-loading استفاده می‌کنیم تا بارگذاری ماژول‌های سنگین تنها هنگام نیاز انجام شود.
همچنین امکان پیکربندی از طریق متغیرهای محیطی فراهم است.
"""

from __future__ import annotations

import os
import logging
import json
import re
from typing import Any

logger = logging.getLogger(__name__)


class AIBrain:
    """کلاس برای مدیریت و انتخاب مدل مناسب بر اساس منظور (purpose).

    روش کار: مدل‌ها هنگام نیاز ساخته می‌شوند تا زمان شروع برنامه سبک بماند.
    """

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}

    def _analyze_task_complexity(self, task: str) -> str:
        """تحلیل خودکار پیچیدگی تسک و انتخاب بهترین مدل.
        
        این متد بر اساس کلمات کلیدی و محتوای تسک، مناسب‌ترین مدل را انتخاب می‌کند.
        """
        if not task:
            return "normal"
        
        task_lower = task.lower()
        
        # کلمات کلیدی برای عملیات سیستمی
        system_keywords = [
            "install", "open app", "launch", "run program", "photoshop", "notepad",
            "system", "hardware", "cpu", "memory", "process", "kill", "terminate",
            "نصب", "برنامه", "باز کن", "اجرا", "فتوشاپ", "سیستم", "سخت‌افزار",
            "پردازنده", "حافظه", "فرآیند", "بستن"
        ]
        
        # کلمات کلیدی برای کارهای مرورگری
        browser_keywords = [
            "browse", "search", "web", "website", "google", "click", "open",
            "مرور", "جستجو", "وب", "سایت", "گوگل", "کلیک", "باز کن"
        ]
        
        # کلمات کلیدی برای تحلیل و استدلال عمیق
        reasoning_keywords = [
            "analyze", "compare", "explain", "why", "how does", "reason",
            "evaluate", "assess", "investigate", "deep",
            "تحلیل", "مقایسه", "توضیح", "چرا", "چگونه", "دلیل", 
            "ارزیابی", "بررسی", "تحقیق"
        ]
        
        # کلمات کلیدی برای پاسخ‌های سریع
        fast_keywords = [
            "quick", "fast", "simple", "short", "brief",
            "سریع", "ساده", "کوتاه", "خلاصه"
        ]
        
        # بررسی اولویت‌دار
        if any(kw in task_lower for kw in system_keywords):
            logger.info("تشخیص نوع تسک: system")
            return "system"
        elif any(kw in task_lower for kw in browser_keywords):
            logger.info("تشخیص نوع تسک: browser_use")
            return "browse"
        elif any(kw in task_lower for kw in reasoning_keywords):
            logger.info("Task type identification: reasoning")
            return "analyze"
        elif any(kw in task_lower for kw in fast_keywords):
            logger.info("Task type detection: fast")
            return "realtime"
        else:
            # برای تسک‌های طولانی‌تر از 100 کاراکتر از مدل reasoning استفاده کن
            if len(task) > 100:
                logger.info("Task type detection: reasoning (long)")
                return "analyze"
            logger.info("Task type detection: normal")
            return "normal"

    def _load_model(self, name: str) -> Any:
        """بارگذاری مدل با نام منطقی. این توابع importهای سنگین را محصور می‌کند."""
        try:
            if name == "reasoning":
                from browser_use.llm.google.chat import ChatGoogle

                model = ChatGoogle(model=os.getenv("GOOGLE_REASONING_MODEL", "gemini-2.5-flash"),
                                   temperature=float(os.getenv("MODEL_TEMPERATURE", "0.5")))
            elif name == "system":
                # برای عملیات سیستمی از مدل با دقت بالاتر استفاده کن
                from browser_use.llm.google.chat import ChatGoogle

                model = ChatGoogle(model=os.getenv("GOOGLE_SYSTEM_MODEL", "gemini-2.5-flash"),
                                   temperature=float(os.getenv("SYSTEM_MODEL_TEMPERATURE", "0.3")))
            elif name == "browser_use":
                from browser_use.llm.browser_use.chat import ChatBrowserUse

                model = ChatBrowserUse()
            elif name == "fast":
                from browser_use.llm.groq.chat import ChatGroq

                model = ChatGroq(model=os.getenv("GROQ_MODEL", "groq-1"),
                                  temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")))
            elif name == "normal":
                from browser_use.llm.openai.chat import ChatOpenAI

                model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                                    temperature=float(os.getenv("MODEL_TEMPERATURE", "0")))
            else:
                # fallback برای مقادیر نامعتبر
                logger.warning("Invalid model name: %s - use default model", name)
                from browser_use.llm.openai.chat import ChatOpenAI

                model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                                    temperature=float(os.getenv("MODEL_TEMPERATURE", "0")))
            logger.info("Artificial intelligence model opened: %s", name)
            return model
        except Exception as exc:
            logger.exception("Error loading model. %s: %s", name, exc)
            raise

    def get_model(self, purpose: str | None = None, task: str | None = None) -> Any:
        """انتخاب خودکار مدل بر اساس تسک یا منظور.

        پارامترها:
        - purpose: منظور دستی ('analyze', 'browse', 'realtime', 'normal')
        - task: متن تسک برای تحلیل خودکار (اگر purpose داده نشده باشد)

        اگر هیچ‌کدام داده نشود، از مدل 'normal' استفاده می‌شود.
        
        مثال:
        >>> brain.get_model(task="مرورگر را باز کن و گوگل را جستجو کن")  # auto: browse
        >>> brain.get_model(purpose="analyze")  # manual: reasoning
        >>> brain.get_model()  # default: normal
        """
        # اگر purpose داده نشده، از task تحلیل کن
        if purpose is None:
            if task:
                purpose = self._analyze_task_complexity(task)
                logger.info("Automatic model selection based on task: %s", purpose)
            else:
                purpose = "normal"
                logger.info("Use default model: normal")
        
        # تبدیل purpose به نام داخلی مدل
        key = {
            "analyze": "reasoning",
            "browse": "browser_use",
            "realtime": "fast",
            "normal": "normal",
            "system": "system",
        }.get(purpose, "normal")

        # lazy-loading: فقط در صورت نیاز مدل را بارگذاری کن
        if key not in self._models:
            self._models[key] = self._load_model(key)

        return self._models[key]
    
    async def ask_with_fallback(self, prompt: str, mode: str = "normal", max_tokens: int = 500) -> str:
        """پرسش هوشمند با fallback خودکار به مدل‌های دیگر.
        
        اگر یک مدل فیل شد، خودکار مدل بعدی را امتحان می‌کند.
        
        Args:
            prompt: سوال یا دستور
            mode: نوع مدل اولیه ('system', 'normal', 'reasoning', 'fast')
            max_tokens: حداکثر طول پاسخ
        
        Returns:
            پاسخ متنی AI (از اولین مدل موفق)
        """
        # لیست اولویت مدل‌ها برای fallback
        fallback_order = {
            "system": ["system", "normal", "fast", "reasoning"],  # Gemini → OpenAI → Groq → Gemini Reasoning
            "normal": ["normal", "fast", "system", "reasoning"],  # OpenAI → Groq → Gemini → Reasoning
            "fast": ["fast", "normal", "system", "reasoning"],    # Groq → OpenAI → Gemini → Reasoning
            "reasoning": ["reasoning", "system", "normal", "fast"] # Reasoning → Gemini → OpenAI → Groq
        }
        
        models_to_try = fallback_order.get(mode, ["normal", "fast", "system"])
        
        for i, model_mode in enumerate(models_to_try):
            try:
                logger.info(f"🤖 Trying model {i+1}/{len(models_to_try)}: {model_mode}")
                
                result = await self.ask(prompt, mode=model_mode, max_tokens=max_tokens)
                
                if result and result.strip():
                    if i > 0:
                        logger.info(f"✅ Success with fallback model: {model_mode}")
                    return result
                else:
                    logger.warning(f"⚠️ Model {model_mode} returned empty response")
                    
            except Exception as e:
                logger.warning(f"❌ Model {model_mode} failed: {e}")
                if i == len(models_to_try) - 1:
                    # آخرین مدل هم فیل شد
                    logger.error("💥 All models failed!")
                    return ""
                # ادامه به مدل بعدی
                continue
        
        return ""
    
    async def ask(self, prompt: str, mode: str = "normal", max_tokens: int = 500) -> str:
        """پرسش ساده از AI و دریافت پاسخ متنی.
        
        Args:
            prompt: سوال یا دستور
            mode: نوع مدل ('system', 'normal', 'reasoning', 'fast')
            max_tokens: حداکثر طول پاسخ
        
        Returns:
            پاسخ متنی AI
        """
        try:
            model = self.get_model(purpose=mode)
            
            # تبدیل prompt به فرمت مورد انتظار (Message object)
            # برای Google Gemini باید از langchain messages استفاده کنیم
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [HumanMessage(content=prompt)]
            
            # فراخوانی مدل - سازگار با APIهای مختلف
            if hasattr(model, 'ainvoke'):
                response = await model.ainvoke(messages)
                if hasattr(response, 'content'):
                    return response.content.strip()
                return str(response).strip()
            elif hasattr(model, 'invoke'):
                response = model.invoke(messages)
                if hasattr(response, 'content'):
                    return response.content.strip()
                return str(response).strip()
            else:
                logger.error("Model does not support invoke/ainvoke")
                return ""
        
        except Exception as e:
            logger.exception("AI ask failed: %s", e)
            raise  # Re-raise برای fallback
    
    async def interpret_system_request(self, user_request: str) -> list[dict[str, Any]]:
        """تفسیر درخواست کاربر و تبدیل به لیست اقدامات.
        
        Args:
            user_request: درخواست طبیعی کاربر (فارسی یا انگلیسی)
        
        Returns:
            لیست اقدامات در قالب JSON
        """
        prompt = f"""You are a Windows automation system. Convert the user's natural language request into structured actions.

User Request: {user_request}

Supported Actions:
1. LaunchApp: Open an application
   {{"type": "LaunchApp", "params": {{"app_name": "app.exe", "arguments": []}}, "priority": "normal", "description": "Open app"}}

2. DesktopClick: Click on UI element
   {{"type": "DesktopClick", "params": {{"target": "button text", "button": "left", "clicks": 1}}, "priority": "normal", "description": "Click button"}}

3. DesktopType: Type text
   {{"type": "DesktopType", "params": {{"text": "hello", "target": null}}, "priority": "normal", "description": "Type hello"}}

4. InstallPackage: Install software
   {{"type": "InstallPackage", "params": {{"package_name": "git", "package_manager": "winget", "silent": true}}, "priority": "normal", "description": "Install git"}}

5. TerminateProcess: Close application
   {{"type": "TerminateProcess", "params": {{"process_name": "app.exe", "force": false}}, "priority": "normal", "description": "Close app"}}

6. QueryHardware: Get system info
   {{"type": "QueryHardware", "params": {{"query_type": "all"}}, "priority": "normal", "description": "Get hardware info"}}

Return ONLY a valid JSON array of actions, nothing else. Example:
[{{"type": "LaunchApp", "params": {{"app_name": "steam.exe", "arguments": []}}, "priority": "normal", "description": "Open Steam"}}]

JSON Array:"""

        try:
            # استفاده از fallback برای اطمینان از دریافت پاسخ
            response = await self.ask_with_fallback(prompt, mode="system", max_tokens=500)
            
            # Log the raw response for debugging
            logger.debug(f"📋 Raw AI response: {response[:500]}")
            
            # تلاش برای parse کردن JSON
            import json
            import re
            
            # استخراج JSON از پاسخ
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.debug(f"📋 Extracted JSON: {json_str[:200]}")
                actions = json.loads(json_str)
                
                if isinstance(actions, list):
                    logger.info("✅ AI parsed %d actions successfully", len(actions))
                    return actions
            
            logger.warning("⚠️ AI response is not valid JSON: %s", response[:200])
            return []
        
        except Exception as e:
            logger.exception("❌ AI interpretation failed: %s", e)
            return []