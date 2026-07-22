# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
لایه‌ی پیکربندی مدل‌های LLM - پشتیبانی از مدل‌های رایگان
مانند Microsoft Copilot و GitHub Copilot

دارای قابلیت fallback خودکار و انتخاب ذکی مدل‌ها
تمام مدل‌های این فایل رایگان هستند (2026 verified)
"""

from __future__ import annotations

import os
import logging
import time
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """تنظیمات یک مدل LLM"""
    name: str                    # نام مدل (مثلاً: gemini-2.5-flash, llama-3.3-70b)
    provider: str                # ارائه‌دهنده (openrouter, google, groq, ollama, huggingface)
    api_key_env: str            # متغیر محیطی کلید API
    base_url: Optional[str]     = None  # آدرس پایه برای OpenRouter و سایرین
    temperature: float          = 0.5   # دمای مدل
    max_tokens: int            = 4000   # حداکثر tokens
    priority: int              = 0      # اولویت (بالاتر = اولی‌تر)
    description: str           = ""     # توضیح مدل
    is_free: bool              = True   # آیا مدل رایگان است


@dataclass
class ModelHealth:
    """وضعیت سلامت یک مدل بر اساس تاریخچه موفقیت/شکست"""
    name: str
    success_count: int = 0
    failure_count: int = 0
    last_success: float = 0.0
    last_failure: float = 0.0
    last_failure_type: str = ""  # "403", "timeout", "error"

    @property
    def total_attempts(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        """نرخ موفقیت (0.0 - 1.0)"""
        if self.total_attempts == 0:
            return 0.5  # بدون داده → مقدار خنثی
        return self.success_count / self.total_attempts

    @property
    def health_score(self) -> int:
        """امتیاز سلامت برای مرتب‌سازی (0-100).

        ترکیب: 70% نرخ موفقیت + 30% تعداد تلاش‌ها (مدل‌های بیشتر = قابل‌اعتمادتر)
        """
        rate_score = self.success_rate * 70
        # مدل‌هایی که بیشتر تست شده‌اند امتیاز بیشتری می‌گیرند (حداکثر 30)
        volume_score = min(30, self.total_attempts * 3)
        return int(rate_score + volume_score)


class ModelHealthTracker:
    """ردیاب سلامت مدل‌ها بر اساس تاریخچه موفقیت/شکست.

    این کلاس به ModelRegistry متصل می‌شود و:
    - تعداد موفقیت/شکست هر مدل را ردیابی می‌کند
    - امتیاز سلامت محاسبه می‌کند
    - مدل‌ها را بر اساس سلامت رتبه‌بندی می‌کند
    """

    def __init__(self):
        self._health: dict[str, ModelHealth] = {}

    def record_success(self, model_name: str) -> None:
        """ثبت موفقیت مدل."""
        h = self._get_or_create(model_name)
        h.success_count += 1
        h.last_success = time.time()

    def record_failure(self, model_name: str, error_type: str = "error") -> None:
        """ثبت شکست مدل."""
        h = self._get_or_create(model_name)
        h.failure_count += 1
        h.last_failure = time.time()
        h.last_failure_type = error_type

    def get_health(self, model_name: str) -> ModelHealth:
        """دریافت وضعیت سلامت یک مدل."""
        return self._get_or_create(model_name)

    def get_all_health(self) -> dict[str, ModelHealth]:
        """دریافت وضعیت سلامت تمام مدل‌ها."""
        return dict(self._health)

    def get_ranked_models(self, model_names: list[str]) -> list[str]:
        """رتبه‌بندی مدل‌ها بر اساس امتیاز سلامت (بالاترین اول)."""
        scored = []
        for name in model_names:
            h = self._get_or_create(name)
            scored.append((name, h.health_score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in scored]

    def get_health_report(self) -> dict[str, dict[str, Any]]:
        """گزارش سلامت برای نمایش در /providers."""
        result = {}
        for name, h in self._health.items():
            result[name] = {
                "success": h.success_count,
                "failure": h.failure_count,
                "total": h.total_attempts,
                "rate": f"{h.success_rate * 100:.0f}%",
                "score": h.health_score,
                "last_failure_type": h.last_failure_type,
            }
        return result

    def _get_or_create(self, model_name: str) -> ModelHealth:
        """دریافت یا ایجاد وضعیت سلامت یک مدل."""
        if model_name not in self._health:
            self._health[model_name] = ModelHealth(name=model_name)
        return self._health[model_name]


# Global health tracker
_health_tracker: Optional[ModelHealthTracker] = None


def get_health_tracker() -> ModelHealthTracker:
    """دریافت نمونه سراسری ردیاب سلامت مدل‌ها"""
    global _health_tracker
    if _health_tracker is None:
        _health_tracker = ModelHealthTracker()
    return _health_tracker


class ModelRegistry:
    """ثبت‌نام مرکزی برای مدل‌های LLM رایگان.

    این سیستم مانند Microsoft Copilot و GitHub Copilot کار می‌کند:
    - مدل‌های رایگان در دسترس
    - اگر یک مدل موفق نبود، خودکار به مدل بعدی می‌رود
    - هر مدل دارای اولویت و ویژگی‌های خاص است
    """

    def __init__(self):
        self.models: dict[str, ModelConfig] = {}
        self._load_default_models()

    def _load_default_models(self):
        """بارگذاری مدل‌های پیش‌فرض رایگان"""

        # ================== OpenRouter (Free Models) ==================
        # مدل‌های رایگان OpenRouter - بدون نیاز به پرداخت

        self.register_model(ModelConfig(
            name="tencent/hy3:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=100,
            description="Tencent Hunyuan 120B (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="nvidia/nemotron-3-ultra-550b-a55b:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=95,
            description="NVIDIA Nemotron 3 Ultra 550B (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="poolside/laguna-m.1:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=90,
            description="Poolside Laguna M.1 (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="google/gemma-4-31b-it:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=85,
            description="Google Gemma 4 31B IT (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="cohere/north-mini-code:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=4000,
            priority=80,
            description="Cohere North Mini Code (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="openrouter/free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=70,
            description="OpenRouter Auto-Router (picks best free model)",
            is_free=True
        ))

        # ================== Google AI Studio (Free Tier) ==================
        # Google AI Studio برای Gemini - رایگان، 250 درخواست در روز

        self.register_model(ModelConfig(
            name="gemini-2.5-flash",
            provider="google",
            api_key_env="GOOGLE_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=88,
            description="Google Gemini 2.5 Flash (Free: 10 RPM, 250 RPD)",
            is_free=True
        ))

        # ================== Groq (Free Tier - Very Fast) ==================
        # Groq - سریع‌ترین inference رایگان

        self.register_model(ModelConfig(
            name="llama-3.3-70b-versatile",
            provider="groq",
            api_key_env="GROQ_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=78,
            description="Groq Llama 3.3 70B (Very Fast, Free)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="qwen-qwq-32b",
            provider="groq",
            api_key_env="GROQ_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=75,
            description="Groq Qwen QWQ 32B (Reasoning, Free)",
            is_free=True
        ))

        # ================== Ollama (Local - Unlimited) ==================
        # اگر Ollama نصب است - کاملاً رایگان و نامحدود

        self.register_model(ModelConfig(
            name="ollama-neural-chat",
            provider="ollama",
            api_key_env="",
            base_url="http://localhost:11434",
            temperature=0.5,
            max_tokens=4000,
            priority=50,
            description="Ollama Neural Chat (Local, Unlimited)",
            is_free=True
        ))

        # ================== HuggingFace Inference (Free Tier) ==================

        self.register_model(ModelConfig(
            name="deepseek-ai/DeepSeek-V3.2",
            provider="huggingface",
            api_key_env="HUGGINGFACE_API_KEY",
            temperature=0.5,
            max_tokens=2000,
            priority=60,
            description="HuggingFace DeepSeek-V3.2 (Free Tier)",
            is_free=True
        ))

        # ================== GapGPT (Dedicated Servers) ==================
        # GapGPT - سرورهای اختصاصی با مدل‌های رایگان و باکیفیت

        self.register_model(ModelConfig(
            name="gapgpt-qwen-3.6",
            provider="gapgpt",
            api_key_env="GAPGPT_API_KEY",
            base_url="https://api.gapgpt.com/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=92,
            description="GapGPT Qwen 3.6 (Dedicated Servers, Free & High Quality)",
            is_free=True
        ))

        logger.info("✅ Loaded %d FREE models from default registry", len(self.models))

    def register_model(self, config: ModelConfig):
        """ثبت یک مدل جدید"""
        self.models[config.name] = config
        logger.debug(f"📌 Registered model: {config.name} (Free: {config.is_free})")

    def get_model(self, name: str) -> Optional[ModelConfig]:
        """دریافت تنظیمات یک مدل"""
        return self.models.get(name)

    def get_available_models(self) -> list[ModelConfig]:
        """دریافت تمام مدل‌های دردسترس (آن‌هایی که کلید API دارند).

        مرتب‌سازی: ابتدا بر اساس امتیاز سلامت، سپس اولویت پیش‌فرض.
        """
        tracker = get_health_tracker()
        available = []
        for model in self.models.values():
            if model.api_key_env:
                if os.getenv(model.api_key_env):
                    available.append(model)
            else:
                # مدل‌های محلی یا بدون نیاز به کلید
                available.append(model)

        # مرتب‌سازی ترکیبی: 70% health_score + 30% priority
        def _sort_key(m: ModelConfig) -> tuple[int, int]:
            health = tracker.get_health(m.name)
            return (health.health_score, m.priority)

        available.sort(key=_sort_key, reverse=True)
        return available

    def get_free_models(self) -> list[ModelConfig]:
        """دریافت تمام مدل‌های رایگان"""
        return [m for m in self.models.values() if m.is_free]

    def get_fallback_chain(self, primary_model: str) -> list[str]:
        """دریافت زنجیر fallback برای یک مدل اولیه.

        بدون اولویت در نظر گرفتن، تمام مدل‌های دردسترس را برمی‌گرداند.
        """
        available = self.get_available_models()
        model_names = [m.name for m in available]

        # اگر مدل اولیه در لیست است، آن را برای اول قرار دهید
        if primary_model in model_names:
            model_names.remove(primary_model)
            model_names.insert(0, primary_model)

        logger.info(f"🔗 Fallback chain for {primary_model}: {model_names}")
        return model_names

    def export_config(self) -> dict:
        """صادرات پیکربندی برای log و debug"""
        return {
            "total_models": len(self.models),
            "free_models": len(self.get_free_models()),
            "available_models": len(self.get_available_models()),
            "models": [
                {
                    "name": m.name,
                    "provider": m.provider,
                    "priority": m.priority,
                    "is_free": m.is_free,
                    "description": m.description,
                    "has_api_key": bool(os.getenv(m.api_key_env) if m.api_key_env else True)
                }
                for m in sorted(self.models.values(), key=lambda x: x.priority, reverse=True)
            ]
        }


# Global registry
_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """دریافت نمونه global model registry"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
