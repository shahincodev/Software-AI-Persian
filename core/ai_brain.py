# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""لایه هوشمند برای مدیریت و انتخاب مدل‌های LLM.

این ماژول به‌صورت خودکار کلیدهای API موجود در محیط را شناسایی کرده
و فقط از ارائه‌دهندگانی که کلید API دارند استفاده می‌کند.

ویژگی‌های کلیدی:
- شناسایی خودکار ارائه‌دهندگان فعال (Google, Groq, OpenRouter, etc.)
- انتخاب هوشمند مدل بر اساس تسک و ارائه‌دهنده موجود
- fallback خودکار بین ارائه‌دهندگان فعال
- بدون تلاش برای ارائه‌دهندگانی که کلید API ندارند
"""

from __future__ import annotations

import asyncio
import os
import logging
import json
from typing import Any, Optional
from dataclasses import dataclass

from core.model_config import get_model_registry, ModelConfig, get_health_tracker
from core.tool_schema import (
    validate_tool_call, get_tool_prompt_block, get_all_tool_names
)

logger = logging.getLogger(__name__)

MAX_SCHEMA_RETRIES = 2


@dataclass
class ProviderStatus:
    """وضعیت یک ارائه‌دهنده API"""
    name: str
    api_key_env: str
    is_available: bool = False
    api_key_set: bool = False
    models_count: int = 0


class ProviderDetector:
    """شناسایی خودکار ارائه‌دهندگان API موجود در محیط.
    
    این کلاس متغیرهای محیطی را بررسی کرده و مشخص می‌کند کدام ارائه‌دهندگان
    دارای کلید API معتبر هستند.
    """
    
    # نقشه ارائه‌دهندگان به متغیرهای محیطی کلید API
    PROVIDER_KEY_MAP: dict[str, str] = {
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
    }
    
    def __init__(self):
        self._providers: dict[str, ProviderStatus] = {}
        self._detect_providers()
    
    def _detect_providers(self) -> None:
        """شناسایی ارائه‌دهندگان فعال"""
        for provider_name, env_var in self.PROVIDER_KEY_MAP.items():
            api_key = os.getenv(env_var, "").strip()
            is_valid = bool(api_key and not api_key.startswith("your-") and not api_key.startswith("AIza-your-"))
            
            status = ProviderStatus(
                name=provider_name,
                api_key_env=env_var,
                is_available=is_valid,
                api_key_set=bool(api_key),
            )
            self._providers[provider_name] = status
            
            if is_valid:
                logger.info(f"✅ Provider detected: {provider_name} (key: {env_var})")
            elif api_key:
                logger.debug(f"⚠️ Provider {provider_name}: key appears placeholder")
    
    def is_provider_available(self, provider: str) -> bool:
        """بررسی در دسترس بودن یک ارائه‌دهنده"""
        status = self._providers.get(provider)
        return status.is_available if status else False
    
    def get_available_providers(self) -> list[str]:
        """دریافت لیست ارائه‌دهندگان فعال"""
        return [name for name, status in self._providers.items() if status.is_available]
    
    def get_provider_status(self, provider: str) -> Optional[ProviderStatus]:
        """دریافت وضعیت یک ارائه‌دهنده"""
        return self._providers.get(provider)
    
    def get_all_status(self) -> dict[str, ProviderStatus]:
        """دریافت وضعیت تمام ارائه‌دهندگان"""
        return self._providers.copy()
    
    def log_summary(self) -> None:
        """نمایش خلاصه وضعیت ارائه‌دهندگان"""
        available = self.get_available_providers()
        total = len(self._providers)
        
        if available:
            logger.info(f"🔍 Available providers ({len(available)}/{total}): {', '.join(available)}")
        else:
            logger.warning("❌ No API providers detected! Check your .env file")
            logger.info("📋 Required environment variables:")
            for name, env_var in self.PROVIDER_KEY_MAP.items():
                logger.info(f"   - {env_var} (for {name})")


# نمونه سراسری_detector
_provider_detector: Optional[ProviderDetector] = None


def get_provider_detector() -> ProviderDetector:
    """دریافت نمونه سراسری شناسایی ارائه‌دهندگان"""
    global _provider_detector
    if _provider_detector is None:
        _provider_detector = ProviderDetector()
    return _provider_detector


class ModelCircuitBreaker:
    """Circuit Breaker برای جلوگیری از retry storm روی مدل‌های ۴۰۳.

    وقتی یک مدل چند بار متوالی خطا بدهد (مثلاً 403 Forbidden)،
    این کلاس آن مدل را برای مدت مشخصی "قفل" می‌کند تا در fallback chain
    دوباره تلاش نشود. بعد از انقضای مهلت، مدل دوباره در دسترس می‌شود.

    - خطا‌های 403/Auth → قفل ۵ دقیقه‌ای
    - سایر خطاها → قفل ۱ دقیقه‌ای
    - درخواست موفق → ریست کانتر خطا
    """

    # آستانه خطا برای قفل کردن یک مدل
    FAILURE_THRESHOLD = 3
    # مهلت قفل برای خطاهای 403/Auth (ثانیه)
    LOCKOUT_SECONDS_AUTH = 300  # 5 minutes
    # مهلت قفل برای سایر خطاها (ثانیه)
    LOCKOUT_SECONDS_OTHER = 60  # 1 minute

    def __init__(self):
        self._failures: dict[str, int] = {}          # شمارنده خطا به ازای هر مدل
        self._locked_until: dict[str, float] = {}     # زمان انقضای قفل (epoch)
        self._lock_reason: dict[str, str] = {}        # دلیل قفل

    def is_locked(self, model_name: str) -> bool:
        """بررسی آیا مدل قفل است یا نه."""
        import time
        until = self._locked_until.get(model_name, 0)
        if time.time() < until:
            return True
        # قفل منقضی شده → پاکسازی
        if until > 0:
            self._reset(model_name)
        return False

    def record_success(self, model_name: str) -> None:
        """ثبت موفقیت → ریست کانتر خطا."""
        self._reset(model_name)

    def record_failure(self, model_name: str, error: Exception) -> None:
        """ثبت خطا → افزایش کانتر و قفل در صورت رسیدن به آستانه."""
        import time
        count = self._failures.get(model_name, 0) + 1
        self._failures[model_name] = count

        # تشخیص نوع خطا
        error_str = str(error).lower()
        is_auth_error = any(kw in error_str for kw in [
            "403", "forbidden", "unauthorized", "auth",
            "permission", "access denied", "quota"
        ])

        if count >= self.FAILURE_THRESHOLD:
            lockout = self.LOCKOUT_SECONDS_AUTH if is_auth_error else self.LOCKOUT_SECONDS_OTHER
            self._locked_until[model_name] = time.time() + lockout
            self._lock_reason[model_name] = "auth/403" if is_auth_error else "other"
            logger.warning(
                f"🔒 Circuit breaker TRIPPED for {model_name} "
                f"(failures={count}, locked for {lockout}s, reason={self._lock_reason[model_name]})"
            )
        else:
            logger.debug(f"⚠️ Failure {count}/{self.FAILURE_THRESHOLD} for {model_name}")

    def _reset(self, model_name: str) -> None:
        """ریست وضعیت یک مدل."""
        self._failures.pop(model_name, None)
        self._locked_until.pop(model_name, None)
        self._lock_reason.pop(model_name, None)

    def get_status(self) -> dict[str, dict[str, Any]]:
        """دریافت وضعیت تمام مدل‌ها (برای /providers و debug)."""
        import time
        now = time.time()
        result = {}
        for model in set(list(self._failures.keys()) + list(self._locked_until.keys())):
            until = self._locked_until.get(model, 0)
            is_locked = now < until
            result[model] = {
                "failures": self._failures.get(model, 0),
                "locked": is_locked,
                "locked_seconds_remaining": max(0, int(until - now)) if is_locked else 0,
                "reason": self._lock_reason.get(model, ""),
            }
        return result

    def reset_all(self) -> None:
        """ریست تمام مدل‌ها (برای دستی)."""
        self._failures.clear()
        self._locked_until.clear()
        self._lock_reason.clear()


class ResponseCache:
    """کش ساده برای پاسخ‌های AI تکراری.

    درخواست‌های تکراری (یا بسیار مشابه) را caching می‌کند تا از فراخوانی
    مجدد مدل جلوگیری شود. TTL پیش‌فرض: ۱۰ دقیقه.
    """

    DEFAULT_TTL = 600  # 10 minutes

    def __init__(self, ttl: int = DEFAULT_TTL, max_size: int = 100):
        self._cache: dict[str, tuple[str, float]] = {}  # key → (response, expiry)
        self._ttl = ttl
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def _make_key(self, prompt: str, mode: str) -> str:
        """ساخت کلید کش از prompt و mode.

        Extracts the user message from the prompt template to build a unique key.
        Falls back to full prompt hash if extraction fails.
        """
        import hashlib
        # Extract user message between markers in the prompt template
        user_msg = ""
        marker = "## User Request:\n"
        if marker in prompt:
            start = prompt.index(marker) + len(marker)
            # Find the next section marker (## or end of prompt)
            end = len(prompt)
            for next_marker in ["\n\n## ", "\n\n{context_block}", "\n\n{screen_block}"]:
                idx = prompt.find(next_marker, start)
                if idx != -1 and idx < end:
                    end = idx
            user_msg = prompt[start:end].strip()

        if not user_msg:
            # Fallback: use the full prompt (no caching for unparseable prompts)
            user_msg = prompt

        raw = f"{mode}:{user_msg}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, prompt: str, mode: str) -> str | None:
        """دریافت پاسخ از کش (اگر موجود و منقضی نشده باشد)."""
        import time
        key = self._make_key(prompt, mode)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        response, expiry = entry
        if time.time() > expiry:
            del self._cache[key]
            self._misses += 1
            return None
        self._hits += 1
        logger.debug(f"Cache HIT for mode={mode}")
        return response

    def set(self, prompt: str, mode: str, response: str) -> None:
        """ذخیره پاسخ در کش."""
        import time
        if len(self._cache) >= self._max_size:
            # حذف قدیمی‌ترین entry
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        key = self._make_key(prompt, mode)
        self._cache[key] = (response, time.time() + self._ttl)

    def get_stats(self) -> dict[str, Any]:
        """آمار کش."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self._hits / total * 100:.1f}%" if total > 0 else "0%",
        }

    def clear(self) -> None:
        """پاکسازی کامل کش."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0


class AIBrain:
    """کلاس هوشمند برای مدیریت و انتخاب مدل بر اساس ارائه‌دهندگان فعال.
    
    ویژگی‌های کلیدی:
    1. شناسایی خودکار ارائه‌دهندگان فعال
    2. انتخاب مدل بر اساس نوع تسک و ارائه‌دهنده موجود
    3. fallback هوشمند بین ارائه‌دهندگان فعال
    4. بدون تلاش برای ارائه‌دهندگان بدون کلید API
    5. Circuit Breaker برای جلوگیری از retry storm
    """

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}
        self._detector = get_provider_detector()
        self._circuit_breaker = ModelCircuitBreaker()
        self._response_cache = ResponseCache()
        self._detector.log_summary()
        
        # بارگذاری مدل‌های دردسترس
        self._available_providers = self._detector.get_available_providers()
        logger.info(f"🧠 AIBrain initialized with providers: {self._available_providers}")

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
            logger.info("Task type detected: system")
            return "system"
        elif any(kw in task_lower for kw in browser_keywords):
            logger.info("Task type detected: browser_use")
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
        """بارگذاری مدل با نام منطقی. این توابع importهای سنگین را محصور می‌کند.
        
        پشتیبانی برای OpenRouter (OpenAI)، Google AI Studio، Groq و سایرین.
        فقط از ارائه‌دهندگانی که کلید API دارند استفاده می‌کند.
        """
        try:
            # دریافت پیکربندی مدل
            registry = get_model_registry()
            model_config = registry.get_model(name)
            
            if not model_config:
                logger.warning(f"Model config not found for {name}, using legacy mode")
                # Fallback به سیستم قدیمی
                return self._load_model_legacy(name)
            
            # بررسی کلید API و در دسترس بودن ارائه‌دهنده
            if not self._detector.is_provider_available(model_config.provider):
                logger.warning(f"❌ Provider '{model_config.provider}' not available (no API key)")
                raise ValueError(f"Provider '{model_config.provider}' not available")
            
            # بارگذاری بر اساس ارائه‌دهنده
            if model_config.provider == "openrouter":
                return self._load_openrouter_model(model_config)
            elif model_config.provider == "google":
                return self._load_google_model(model_config)
            elif model_config.provider == "groq":
                return self._load_groq_model(model_config)
            elif model_config.provider == "ollama":
                return self._load_ollama_model(model_config)
            elif model_config.provider == "huggingface":
                return self._load_huggingface_model(model_config)
            else:
                logger.warning(f"Unknown provider: {model_config.provider}, using legacy mode")
                return self._load_model_legacy(name)
            
        except Exception as exc:
            logger.exception("Error loading model %s: %s", name, exc)
            raise
    
    def _load_openrouter_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق OpenRouter"""
        try:
            from browser_use.llm.openai.chat import ChatOpenAI
            
            api_key = os.getenv(config.api_key_env)
            
            # OpenRouter به عنوان OpenAI compatible endpoint
            model = ChatOpenAI(
                model=config.name,
                temperature=config.temperature,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            logger.info(f"✅ Loaded OpenRouter model: {config.name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load OpenRouter model {config.name}: {e}")
            raise
    
    def _load_google_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق Google AI Studio"""
        try:
            from browser_use.llm.google.chat import ChatGoogle
            
            # نام مدل برای Google (مثلاً: gemini-3-pro-preview)
            model_name = config.name.replace("google-", "")
            
            model = ChatGoogle(
                model=model_name,
                temperature=config.temperature
            )
            logger.info(f"✅ Loaded Google model: {model_name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load Google model {config.name}: {e}")
            raise
    
    def _load_groq_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق Groq"""
        try:
            from browser_use.llm.groq.chat import ChatGroq
            
            model_name = config.name.replace("groq-", "")
            
            model = ChatGroq(
                model=model_name,
                temperature=config.temperature
            )
            logger.info(f"✅ Loaded Groq model: {model_name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load Groq model {config.name}: {e}")
            raise
    
    def _load_ollama_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل محلی Ollama"""
        try:
            from langchain_community.llms import Ollama
            
            model_name = config.name.replace("ollama-", "")
            
            model = Ollama(
                model=model_name,
                base_url=config.base_url or "http://localhost:11434",
                temperature=config.temperature
            )
            logger.info(f"✅ Loaded Ollama model: {model_name}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load Ollama model {config.name}: {e}")
            raise
    
    def _load_huggingface_model(self, config: ModelConfig) -> Any:
        """بارگذاری مدل از طریق HuggingFace Inference"""
        try:
            from langchain_huggingface import HuggingFaceEndpoint
            
            api_key = os.getenv(config.api_key_env)
            repo_id = config.name.replace("huggingface-", "")
            
            model = HuggingFaceEndpoint(
                repo_id=repo_id,
                huggingfacehub_api_token=api_key,
                temperature=config.temperature,
                model_kwargs={"max_length": config.max_tokens}
            )
            logger.info(f"✅ Loaded HuggingFace model: {repo_id}")
            return model
        except Exception as e:
            logger.exception(f"Failed to load HuggingFace model {config.name}: {e}")
            raise
    
    def _load_model_legacy(self, name: str) -> Any:
        """سیستم قدیمی برای compatibility
        
        این متد فقط از ارائه‌دهندگان فعال استفاده می‌کند.
        """
        # بررسی ارائه‌دهندگان فعال
        has_google = self._detector.is_provider_available("google")
        has_groq = self._detector.is_provider_available("groq")
        has_openrouter = self._detector.is_provider_available("openrouter")
        has_openai = self._detector.is_provider_available("openai")
        
        if name == "reasoning":
            if has_google:
                from browser_use.llm.google.chat import ChatGoogle
                model = ChatGoogle(model=os.getenv("GOOGLE_REASONING_MODEL", "gemini-2.5-flash"),
                                   temperature=float(os.getenv("MODEL_TEMPERATURE", "0.5")))
            else:
                raise ValueError("No Google API key for reasoning model")
        elif name == "system":
            if has_google:
                from browser_use.llm.google.chat import ChatGoogle
                model = ChatGoogle(model=os.getenv("GOOGLE_SYSTEM_MODEL", "gemini-2.5-flash"),
                                   temperature=float(os.getenv("SYSTEM_MODEL_TEMPERATURE", "0.3")))
            else:
                raise ValueError("No Google API key for system model")
        elif name == "browser_use":
            from browser_use.llm.browser_use.chat import ChatBrowserUse
            model = ChatBrowserUse()
        elif name == "fast":
            if has_groq:
                from browser_use.llm.groq.chat import ChatGroq
                model = ChatGroq(model=os.getenv("GROQ_MODEL", "groq-1"),
                                  temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")))
            else:
                raise ValueError("No Groq API key for fast model")
        elif name == "normal":
            if has_openrouter or has_openai:
                from browser_use.llm.openai.chat import ChatOpenAI
                api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
                model = ChatOpenAI(
                    model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                    temperature=float(os.getenv("MODEL_TEMPERATURE", "0")),
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                )
            else:
                raise ValueError("No OpenRouter/OpenAI API key for normal model")
        else:
            logger.warning("Invalid model name: %s - use default model", name)
            if has_openrouter or has_openai:
                from browser_use.llm.openai.chat import ChatOpenAI
                api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
                model = ChatOpenAI(
                    model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
                    temperature=float(os.getenv("MODEL_TEMPERATURE", "0")),
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                )
            else:
                raise ValueError("No API key available for default model")
        
        logger.info("Artificial intelligence model opened (legacy): %s", name)
        return model

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
        
        این متد فقط از ارائه‌دهندگان فعال (دارای کلید API) استفاده می‌کند
        و هرگز برای ارائه‌دهندگان بدون کلید تلاش نمی‌کند.
        
        Args:
            prompt: سوال یا دستور
            mode: نوع مدل اولیه ('system', 'normal', 'reasoning', 'fast')
            max_tokens: حداکثر طول پاسخ
        
        Returns:
            پاسخ متنی AI (از اولین مدل موفق)
        """
        registry = get_model_registry()
        available_models = registry.get_available_models()
        
        if not available_models:
            logger.error("❌ No available models found! Check your API keys.")
            logger.info("📋 Available models: %s", json.dumps(registry.export_config(), indent=2))
            return ""
        
        # لاگ مدل‌های دردسترس (DEBUG level to reduce noise on every request)
        logger.debug(f"Available models ({len(available_models)}): {', '.join(m.name for m in available_models[:3])}...")

        # Response Cache: check for cached response first
        # Skip cache entirely for "system" mode (agent_chat) — every user
        # request is unique and caching leads to stale/wrong tool calls.
        if mode == "system":
            pass  # bypass cache completely
        else:
            cached = self._response_cache.get(prompt, mode)
            if cached is not None:
                logger.info("⚡ Serving cached response for mode=%s", mode)
                return cached
        
        # سعی اول: از registry استفاده کن
        for i, model_config in enumerate(available_models):
            # Circuit Breaker: skip models that are locked
            if self._circuit_breaker.is_locked(model_config.name):
                logger.info(f"⏭️ Skipping {model_config.name} (circuit breaker locked)")
                continue

            try:
                logger.info(f"🤖 Trying model {i+1}/{len(available_models)}: {model_config.name}")
                
                # بارگذاری مدل
                if model_config.name not in self._models:
                    self._models[model_config.name] = self._load_model(model_config.name)
                
                _ = self._models[model_config.name]
                result = await self.ask(prompt, mode=model_config.name, max_tokens=max_tokens)
                
                if result and result.strip():
                    self._circuit_breaker.record_success(model_config.name)
                    get_health_tracker().record_success(model_config.name)
                    # Don't cache "system" mode responses (agent_chat — always unique)
                    if mode != "system":
                        self._response_cache.set(prompt, mode, result)
                    if i > 0:
                        logger.info(f"✅ Success with fallback model: {model_config.name}")
                    return result
                else:
                    logger.warning(f"⚠️ Model {model_config.name} returned empty response")
                    
            except Exception as e:
                self._circuit_breaker.record_failure(model_config.name, e)
                error_type = "403" if "403" in str(e) or "forbidden" in str(e).lower() else "error"
                get_health_tracker().record_failure(model_config.name, error_type)
                logger.warning(f"❌ Model {model_config.name} failed: {e}")
                continue
        
        logger.error("💥 All %d available models failed. Check your API keys in .env", len(available_models))
        return ""
    
    
    async def ask(self, prompt: str, mode: str = "normal", max_tokens: int = 500) -> str:
        """پرسش ساده از AI و دریافت پاسخ متنی.
        
        Args:
            prompt: سوال یا دستور
            mode: نام مدل (می‌تواند نام registry یا نام قدیمی باشد)
            max_tokens: حداکثر طول پاسخ
        
        Returns:
            پاسخ متنی AI
        """
        try:
            # اگر mode یک نام registry است، به‌طور مستقیم لاد کن
            registry = get_model_registry()
            model_config = registry.get_model(mode)
            
            if model_config:
                # نام مدل registry
                if mode not in self._models:
                    self._models[mode] = self._load_model(mode)
                model = self._models[mode]
                logger.debug(f"Using registry model: {mode} ({model_config.provider})")
            else:
                # فرض کن که mode یک نام قدیمی است
                if mode not in self._models:
                    self._models[mode] = self._load_model(mode)
                model = self._models[mode]
                logger.debug(f"Using legacy model: {mode}")
            
            # فراخوانی مدل - ساخت پیام بر اساس provider (OpenAI/Groq/Google)
            module_name = getattr(model, "__module__", "").lower()

            def _build_provider_message(p):
                try:
                    if "openai" in module_name:
                        from browser_use.llm.openai.serializer import UserMessage  # type: ignore
                        return [UserMessage(content=p)]
                    if "groq" in module_name:
                        from browser_use.llm.groq.serializer import UserMessage  # type: ignore
                        return [UserMessage(content=p)]
                    if "google" in module_name:
                        from browser_use.llm.google.serializer import UserMessage  # type: ignore
                        return [UserMessage(content=p)]
                except Exception:
                    logger.exception("Failed to build provider-specific message; falling back to raw prompt")
                return p  # fallback: raw string

            payload = _build_provider_message(prompt)

            if hasattr(model, 'ainvoke'):
                response = await asyncio.wait_for(
                    model.ainvoke(payload),
                    timeout=60.0
                )
            elif hasattr(model, 'invoke'):
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, model.invoke, payload),
                    timeout=60.0
                )
            else:
                raise ValueError("Model does not support invoke or ainvoke")

            # Extract string content from response
            if isinstance(response, str):
                return response.strip()
            if hasattr(response, 'content'):
                return str(response.content).strip()
            if hasattr(response, 'completion'):
                return str(response.completion).strip()
            logger.warning("Unexpected response type from invoke/ainvoke: %s", type(response))
            return str(response).strip()
        
        except Exception as e:
            logger.exception("AI ask failed: %s", e)
            raise  # Re-raise برای fallback
    
    def _sanitize_ai_response(self, response: str) -> str:
        """پاکسازی پاسخ AI از داده‌های مشکوک.
        
        Args:
            response: پاسخ خام AI
            
        Returns:
            پاسخ پاکسازی شده
        """
        # حذف completion= و thinking= که در لاگ‌ها دیده شده
        import re
        
        # الگوهای مشکوک - به ترتیب اولویت
        suspicious_patterns = [
            # Pattern 1: completion='app.exe'
            (r"completion\s*=\s*['\"]([^'\"]+\.exe)['\"]?", 1),
            # Pattern 2: completion=app.exe (without quotes)
            (r"completion\s*=\s*(\w+\.exe)", 1),
            # Pattern 3: thinking='...'
            (r"thinking\s*=\s*['\"]([^'\"]+)['\"]?", 0),  # 0 = remove completely
            # Pattern 4: thinking=... (without quotes)
            (r"thinking\s*=\s*(\S+)", 0),
        ]
        
        cleaned = response
        for pattern, extract_group in suspicious_patterns:
            if extract_group > 0:
                # استخراج مقدار
                matches = re.findall(pattern, cleaned, re.IGNORECASE)
                if matches:
                    logger.warning(f"⚠️ Suspicious pattern detected: {pattern[:30]}...")
                    # جایگزینی کل pattern با فقط مقدار استخراج شده
                    for match in matches:
                        if match.endswith('.exe'):
                            cleaned = match
                            logger.info(f"✅ Extracted clean app name: {cleaned}")
                            break
            else:
                # حذف کامل
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
                if cleaned != response:
                    logger.info(f"✅ Removed suspicious pattern: {pattern[:30]}...")
        
        return cleaned.strip()
    
    async def interpret_system_request(self, user_request: str) -> list[dict[str, Any]]:
        """تفسیر درخواست کاربر و تبدیل به لیست اقدامات.
        
        Args:
            user_request: درخواست طبیعی کاربر (فارسی یا انگلیسی)
        
        Returns:
            لیست اقدامات در قالب JSON
        """
        user_request = self._sanitize_ai_response(user_request)
        
        prompt = f"""You are a Windows automation system. Convert the user's natural language request into structured actions.

User Request: {user_request}

IMPORTANT NOTES:
- Windows Notepad (notepad.exe) is a SIMPLE text editor with NO tabs, NO "+" button
- To create new file in Notepad: just start typing (it's already a new file)
- To save in Notepad: use Ctrl+S shortcut, NOT clicking menus
- For .bat files, save with double quotes: "filename.bat" to preserve extension
- Only use applications from the allowed list (check safety_filter.py)

Supported Actions:
1. LaunchApp: Open an application
   {{"type": "LaunchApp", "params": {{"app_name": "app.exe", "arguments": []}}, "priority": "normal", "description": "Open app"}}

2. DesktopClick: Click on UI element (use sparingly - prefer keyboard shortcuts)
   {{"type": "DesktopClick", "params": {{"target": "button text", "button": "left", "clicks": 1}}, "priority": "normal", "description": "Click button"}}

3. DesktopType: Type text or use keyboard shortcuts
   {{"type": "DesktopType", "params": {{"text": "hello", "target": null}}, "priority": "normal", "description": "Type hello"}}
   For shortcuts: {{"text": "^s"}} for Ctrl+S, {{"text": "^o"}} for Ctrl+O

4. InstallPackage: Install software
   {{"type": "InstallPackage", "params": {{"package_name": "git", "package_manager": "winget", "silent": true}}, "priority": "normal", "description": "Install git"}}

5. TerminateProcess: Close application
   {{"type": "TerminateProcess", "params": {{"process_name": "app.exe", "force": false}}, "priority": "normal", "description": "Close app"}}

6. QueryHardware: Get system info
   {{"type": "QueryHardware", "params": {{"query_type": "all"}}, "priority": "normal", "description": "Get hardware info"}}

7. ExecuteCommand: Run shell command (requires approval)
   {{"type": "ExecuteCommand", "params": {{"command": "dir", "shell": "cmd"}}, "priority": "normal", "description": "List files"}}

BEST PRACTICES:
- Use keyboard shortcuts instead of clicking menus (faster + more reliable)
- For Notepad: Ctrl+S to save, Ctrl+O to open, Ctrl+N for new
- Keep actions simple and atomic
- Avoid clicking on elements that might not exist

Return ONLY a valid JSON array of actions, nothing else. Example:
[{{"type": "LaunchApp", "params": {{"app_name": "notepad.exe", "arguments": []}}, "priority": "normal", "description": "Open Notepad"}},
 {{"type": "DesktopType", "params": {{"text": "echo hello world", "target": null}}, "priority": "normal", "description": "Type code"}},
 {{"type": "DesktopType", "params": {{"text": "^s", "target": null}}, "priority": "normal", "description": "Save (Ctrl+S)"}}]

JSON Array:"""

        try:
            response = await self.ask_with_fallback(prompt, mode="system", max_tokens=500)
            logger.debug("Raw AI response: %s", response[:500])
            
            actions = self._extract_json_actions(response)
            if actions:
                logger.info("AI parsed %d actions successfully", len(actions))
                return actions
            
            logger.warning("AI response is not valid JSON: %s", response[:200])
            return []
        
        except Exception as e:
            logger.exception("AI interpretation failed: %s", e)
            return []

    def _extract_json_actions(self, response: str) -> list[dict[str, Any]]:
        """Extract JSON actions from AI response with multiple fallback strategies."""
        import json as _json
        import re as _re
        
        if not response or not response.strip():
            return []
        
        # Strategy 1: Find JSON array in the response
        json_match = _re.search(r'\[[\s\S]*?\]', response)
        if json_match:
            json_str = json_match.group(0)
            for attempt in [json_str, _re.sub(r'```json|```|json', '', json_str).strip()]:
                if attempt:
                    try:
                        result = _json.loads(attempt)
                        if isinstance(result, list):
                            return result
                    except _json.JSONDecodeError:
                        continue
        
        # Strategy 2: Try to find individual JSON objects and combine
        obj_matches = _re.findall(r'\{[^{}]*\}', response)
        if obj_matches:
            items = []
            for obj_str in obj_matches:
                try:
                    obj = _json.loads(obj_str)
                    if isinstance(obj, dict) and ("type" in obj or "tool" in obj):
                        items.append(obj)
                except _json.JSONDecodeError:
                    continue
            if items:
                return items
        
        # Strategy 3: Fix common JSON issues
        cleaned = response.strip()
        # Remove markdown code blocks
        cleaned = _re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = _re.sub(r'\s*```$', '', cleaned)
        # Fix trailing commas
        cleaned = _re.sub(r',\s*([}\]])', r'\1', cleaned)
        # Fix single quotes to double quotes
        cleaned = cleaned.replace("'", '"')
        
        try:
            result = _json.loads(cleaned)
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return [result]
        except _json.JSONDecodeError:
            pass
        
        return []

    async def agent_chat(self, user_message: str, system_context: str = "",
                         last_actions: list[dict[str, Any]] | None = None,
                         screen_context: str = "",
                         memory_context: str = "") -> dict[str, Any]:
        """Agent-mode chat: AI with full system access decides what to do.

        Uses unified tool schema with validation and auto-retry.

        Args:
            user_message: The user's request
            system_context: System context (files, drives, etc.)
            last_actions: Recent actions taken
            screen_context: Current screen state from VisionLoopManager
            memory_context: Conversation history and recalled memories (Phase 5)

        Returns dict with:
            - "action": "tool_call" | "chat_reply" | "none"
            - "tool_calls": list of tool call dicts (if action == "tool_call")
            - "response": text response (if action == "chat_reply")
        """
        context_block = ""
        if system_context:
            context_block = f"\n## Current System Context:\n{system_context}\n"

        screen_block = ""
        if screen_context:
            screen_block = f"\n## Current Screen State:\n{screen_context}\n"

        memory_block = ""
        if memory_context:
            memory_block = f"\n## Memory & Conversation History:\n{memory_context}\n"

        actions_block = ""
        if last_actions:
            actions_block = "\n## Recent Actions Taken:\n"
            for a in last_actions[-5:]:
                status = a.get("status", "unknown")
                desc = a.get("description", a.get("command", "unknown"))
                actions_block += f"- [{status}] {desc}\n"

        tools_block = get_tool_prompt_block()
        tool_names = ", ".join(get_all_tool_names())

        prompt = f"""You are Software-AI, an intelligent Windows desktop agent with FULL system access.

Your job is to convert natural language requests into structured tool calls or chat replies.
You can OBSERVE the screen using vision tools to understand what is currently visible.
You can REMEMBER and RECALL information across conversations using memory tools.

## User Request:
{user_message}

{context_block}
{screen_block}
{memory_block}
{actions_block}

## Available Tools:
{tools_block}

## Response Format:
You MUST respond with ONE of the following JSON formats:

### Option A: Tool calls (for actions on the system)
```json
{{
  "action": "tool_call",
  "tool_calls": [
    {{"tool": "tool_name", "params": {{"param1": "value1"}}, "description": "what this does"}}
  ]
}}
```

### Option B: Chat reply (for questions/information)
```json
{{
  "action": "chat_reply",
  "response": "your helpful response here"
}}
```

## Rules:
1. ALWAYS return valid JSON - no extra text before or after
2. Tool names MUST be one of: {tool_names}
3. Every required parameter MUST be included
4. For file operations, use FULL paths (e.g., D:\\\\folder\\\\file.txt)
5. Respond in the same language as the user
6. Multiple tool_calls execute in sequence

Return ONLY the JSON:"""

        # Retry loop with schema validation
        last_error = None
        for attempt in range(MAX_SCHEMA_RETRIES + 1):
            try:
                # Build prompt with error context if retrying
                current_prompt = prompt
                if last_error:
                    current_prompt += f"\n\n## PREVIOUS ERROR (attempt {attempt + 1}):\n{last_error}\nPlease fix and return valid JSON."

                response = await self.ask_with_fallback(current_prompt, mode="system", max_tokens=800)
                logger.debug("Agent chat raw response (attempt %d): %s", attempt + 1, response[:500])

                parsed = self._parse_agent_response(response)
                if not parsed:
                    last_error = "Response is not valid JSON. Return a JSON object with 'action' field."
                    logger.warning("Attempt %d: Failed to parse JSON", attempt + 1)
                    continue

                # If it's a chat reply, return immediately (no validation needed)
                if parsed.get("action") == "chat_reply":
                    return parsed

                # If it's a tool_call, validate each tool call against schema
                if parsed.get("action") == "tool_call":
                    tool_calls = parsed.get("tool_calls", [])
                    if not tool_calls:
                        last_error = "tool_calls array is empty. Provide at least one tool call."
                        logger.warning("Attempt %d: Empty tool_calls", attempt + 1)
                        continue

                    all_valid = True
                    errors = []
                    for i, tc in enumerate(tool_calls):
                        is_valid, msg = validate_tool_call(tc)
                        if not is_valid:
                            all_valid = False
                            errors.append(f"Tool call {i+1}: {msg}")

                    if all_valid:
                        logger.info("Agent parsed %d valid tool calls", len(tool_calls))
                        return parsed
                    else:
                        last_error = "Invalid tool calls:\n" + "\n".join(errors)
                        logger.warning("Attempt %d: Schema validation failed: %s", attempt + 1, last_error)
                        continue

                # Unknown action type
                last_error = f"Unknown action type: {parsed.get('action')}. Use 'tool_call' or 'chat_reply'."
                logger.warning("Attempt %d: Unknown action type", attempt + 1)

            except Exception as e:
                logger.exception("Agent chat attempt %d failed: %s", attempt + 1, e)
                last_error = f"Exception: {str(e)}"

        # All retries exhausted - return error as chat reply
        logger.error("All %d attempts exhausted for agent_chat", MAX_SCHEMA_RETRIES + 1)
        return {
            "action": "chat_reply",
            "response": "I had trouble processing that request. Could you please rephrase it?"
        }

    def _parse_agent_response(self, response: str) -> dict[str, Any] | None:
        """Parse agent response as JSON action."""
        import json as _json
        import re as _re
        
        if not response or not response.strip():
            return None
        
        # Try to extract JSON object
        json_match = _re.search(r'\{[\s\S]*\}', response)
        if json_match:
            json_str = json_match.group(0)
            for attempt in [json_str, _re.sub(r'```json|```|json', '', json_str).strip()]:
                if attempt:
                    try:
                        result = _json.loads(attempt)
                        if isinstance(result, dict) and "action" in result:
                            return result
                    except _json.JSONDecodeError:
                        continue
        
        # Try cleaning common issues
        cleaned = response.strip()
        cleaned = _re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = _re.sub(r'\s*```$', '', cleaned)
        cleaned = _re.sub(r',\s*([}\]])', r'\1', cleaned)
        
        try:
            result = _json.loads(cleaned)
            if isinstance(result, dict) and "action" in result:
                return result
        except _json.JSONDecodeError:
            pass
        
        return None
    
    def get_provider_info(self) -> dict[str, Any]:
        """دریافت اطلاعات ارائه‌دهندگان فعال
        
        Returns:
            دیکشنری حاوی اطلاعات ارائه‌دهندگان
        """
        detector = get_provider_detector()
        all_status = detector.get_all_status()
        
        return {
            "available_providers": detector.get_available_providers(),
            "total_providers": len(all_status),
            "providers": {
                name: {
                    "available": status.is_available,
                    "key_env": status.api_key_env,
                    "key_set": status.api_key_set,
                }
                for name, status in all_status.items()
            }
        }
