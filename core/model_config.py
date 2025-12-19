# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
لایه‌ی پیکربندی مدل‌های LLM - پشتیبانی از هزاران مدل مختلف
مانند Microsoft Copilot و GitHub Copilot

دارای قابلیت fallback خودکار و انتخاب ذکی مدل‌ها
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
    name: str                    # نام مدل (مثلاً: gpt-4o, gemini-pro, claude-3-opus)
    provider: str                # ارائه‌دهنده (openai, google, anthropic, groq, openrouter)
    api_key_env: str            # متغیر محیطی کلید API
    base_url: Optional[str]     = None  # آدرس پایه برای OpenRouter و سایرین
    temperature: float          = 0.5   # دمای مدل
    max_tokens: int            = 4000   # حداکثر tokens
    priority: int              = 0      # اولویت (بالاتر = اولی‌تر)
    description: str           = ""     # توضیح مدل


class ModelRegistry:
    """ثبت‌نام مرکزی برای مدل‌های LLM.
    
    این سیستم مانند Microsoft Copilot و GitHub Copilot کار می‌کند:
    - هزاران مدل مختلف در دسترس
    - اگر یک مدل موفق نبود، خودکار به مدل بعدی می‌رود
    - هر مدل دارای اولویت و ویژگی‌های خاص است
    """
    
    def __init__(self):
        self.models: dict[str, ModelConfig] = {}
        self._load_default_models()
    
    def _load_default_models(self):
        """بارگذاری مدل‌های پیش‌فرض"""
        
        # ================== OpenRouter (OpenAI Models) ==================
        # OpenRouter درگذر برای OpenAI - مدل‌های بسیاری در دسترس
        
        self.register_model(ModelConfig(
            name="openrouter-gpt-4o",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=100,
            description="OpenAI GPT-4o via OpenRouter"
        ))
        
        self.register_model(ModelConfig(
            name="openrouter-gpt-4-turbo",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=99,
            description="OpenAI GPT-4 Turbo via OpenRouter"
        ))
        
        self.register_model(ModelConfig(
            name="openrouter-gpt-3.5-turbo",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=4000,
            priority=90,
            description="OpenAI GPT-3.5 Turbo via OpenRouter"
        ))
        
        self.register_model(ModelConfig(
            name="openrouter-claude-3-opus",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=98,
            description="Anthropic Claude 3 Opus via OpenRouter"
        ))
        
        self.register_model(ModelConfig(
            name="openrouter-mistral-large",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=85,
            description="Mistral Large via OpenRouter"
        ))
        
        # ================== Google AI Studio (رایگان) ==================
        # Google AI Studio برای Gemini - رایگان، بدون سهمیه‌ی کم
        
        self.register_model(ModelConfig(
            name="google-gemini-3-pro-preview",
            provider="google",
            api_key_env="GOOGLE_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=95,
            description="Google Gemini 3 Pro Preview (experimental)"
        ))
        
        self.register_model(ModelConfig(
            name="google-gemini-2-flash",
            provider="google",
            api_key_env="GOOGLE_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=80,
            description="Google Gemini 2.5 Flash (fast)"
        ))
        
        self.register_model(ModelConfig(
            name="google-gemini-2-pro",
            provider="google",
            api_key_env="GOOGLE_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=88,
            description="Google Gemini 2.5 Pro"
        ))
        
        # ================== Groq (سریع و رایگان) ==================
        
        self.register_model(ModelConfig(
            name="groq-mixtral-8x7b",
            provider="groq",
            api_key_env="GROQ_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=75,
            description="Groq Mixtral 8x7B (very fast)"
        ))
        
        self.register_model(ModelConfig(
            name="groq-llama-3.1-70b",
            provider="groq",
            api_key_env="GROQ_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=78,
            description="Groq Llama 3.1 70B"
        ))
        
        # ================== Ollama (محلی) ==================
        # اگر Ollama نصب است
        
        self.register_model(ModelConfig(
            name="ollama-neural-chat",
            provider="ollama",
            api_key_env="",
            base_url="http://localhost:11434",
            temperature=0.5,
            max_tokens=4000,
            priority=50,
            description="Ollama Neural Chat (local)"
        ))
        
        # ================== HuggingFace Inference ==================
        
        self.register_model(ModelConfig(
            name="huggingface-mistral-7b",
            provider="huggingface",
            api_key_env="HUGGINGFACE_API_KEY",
            temperature=0.5,
            max_tokens=2000,
            priority=60,
            description="HuggingFace Mistral 7B"
        ))
        
        logger.info("✅ Loaded %d models from default registry", len(self.models))
    
    def register_model(self, config: ModelConfig):
        """ثبت یک مدل جدید"""
        self.models[config.name] = config
        logger.debug(f"📌 Registered model: {config.name}")
    
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
            "available_models": len(self.get_available_models()),
            "models": [
                {
                    "name": m.name,
                    "provider": m.provider,
                    "priority": m.priority,
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
