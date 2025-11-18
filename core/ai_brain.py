# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

"""لایهٔ ساده برای انتخاب مدل‌های LLM.

اینجا از lazy-loading استفاده می‌کنیم تا بارگذاری ماژول‌های سنگین تنها هنگام نیاز انجام شود.
همچنین امکان پیکربندی از طریق متغیرهای محیطی فراهم است.
"""

from __future__ import annotations

import os
import logging
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
        if any(kw in task_lower for kw in browser_keywords):
            logger.info("Task type detection: browser_use")
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
                logger.warning("نام مدل نامعتبر: %s - استفاده از مدل پیش‌فرض", name)
                from browser_use.llm.openai.chat import ChatOpenAI

                model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                                    temperature=float(os.getenv("MODEL_TEMPERATURE", "0")))
            logger.info("Model Hoshe Masnoii Load Shod: %s", name)
            return model
        except Exception as exc:
            logger.exception("Khataye dar load kardan model %s: %s", name, exc)
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
        }.get(purpose, "normal")

        # lazy-loading: فقط در صورت نیاز مدل را بارگذاری کن
        if key not in self._models:
            self._models[key] = self._load_model(key)

        return self._models[key]