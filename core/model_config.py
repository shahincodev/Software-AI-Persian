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
            name="openai/gpt-oss-120b:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=100,
            description="OpenAI GPT-OSS 120B (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="meta-llama/llama-3.3-70b-instruct:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=95,
            description="Meta Llama 3.3 70B (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="qwen/qwen3-235b-a22b:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=90,
            description="Qwen3 235B MoE (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="nvidia/nemotron-3-ultra-550b-a55b:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=85,
            description="NVIDIA Nemotron 3 Ultra 550B (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="qwen/qwen3-coder:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=4000,
            priority=80,
            description="Qwen3 Coder (Free on OpenRouter)",
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

        logger.info("✅ Loaded %d FREE models from default registry", len(self.models))

    def register_model(self, config: ModelConfig):
        """ثبت یک مدل جدید"""
        self.models[config.name] = config
        logger.debug(f"📌 Registered model: {config.name} (Free: {config.is_free})")

    def get_model(self, name: str) -> Optional[ModelConfig]:
        """دریافت تنظیمات یک مدل"""
        return self.models.get(name)

    def get_available_models(self) -> list[ModelConfig]:
        """دریافت تمام مدل‌های دردسترس (آن‌هایی که کلید API دارند)"""
        available = []
        for model in self.models.values():
            if model.api_key_env:
                if os.getenv(model.api_key_env):
                    available.append(model)
            else:
                # مدل‌های محلی یا بدون نیاز به کلید
                available.append(model)

        # مرتب‌سازی بر اساس اولویت
        available.sort(key=lambda m: m.priority, reverse=True)
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
