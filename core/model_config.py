# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
LLM Model Configuration Layer - Free Model Support
Like Microsoft Copilot and GitHub Copilot

With automatic fallback and smart model selection
All models in this file are free (2026 verified)
"""

from __future__ import annotations

import os
import logging
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for an LLM model"""
    name: str                    # Model name (e.g., gemini-2.5-flash, llama-3.3-70b)
    provider: str                # Provider (openrouter, google, groq, ollama, huggingface)
    api_key_env: str            # Environment variable for API key
    base_url: Optional[str]     = None  # Base URL for OpenRouter and others
    temperature: float          = 0.5   # Model temperature
    max_tokens: int            = 4000   # Maximum tokens
    priority: int              = 0      # Priority (higher = tried first)
    description: str           = ""     # Model description
    is_free: bool              = True   # Whether the model is free


class ModelRegistry:
    """Central registry for free LLM models.

    This system works like Microsoft Copilot and GitHub Copilot:
    - Free models are available
    - If one model fails, it automatically moves to the next
    - Each model has priority and specific features
    """

    def __init__(self):
        self.models: dict[str, ModelConfig] = {}
        self._load_default_models()

    def _load_default_models(self):
        """Load default free models"""

        # ================== OpenRouter (Free Models) ==================
        # Free OpenRouter models - no payment required

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
            name="nvidia/nemotron-3-super-120b-a12b:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=95,
            description="NVIDIA Nemotron 3 Super 120B (Free on OpenRouter)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="poolside/laguna-xs-2.1:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
            max_tokens=4000,
            priority=90,
            description="Poolside Laguna XS 2.1 (Free on OpenRouter)",
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
            name="qwen/qwen3-coder:free",
            provider="openrouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            temperature=0.5,
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
        # Google AI Studio for Gemini - free, 250 requests per day

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
        # Groq - fastest free inference

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
            name="qwen/qwen3-32b",
            provider="groq",
            api_key_env="GROQ_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=75,
            description="Groq Qwen3 32B (Fast, Free)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="qwen2.5-coder:14b",
            provider="groq",
            api_key_env="GROQ_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=73,
            description="Groq Qwen2.5 Coder 14B (Fast, Free)",
            is_free=True
        ))

        self.register_model(ModelConfig(
            name="llama3.3:70b",
            provider="groq",
            api_key_env="GROQ_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=71,
            description="Groq Llama 3.3 70B (Fast, Free)",
            is_free=True
        ))

        # ================== HuggingFace Inference (Free Tier) ==================

        self.register_model(ModelConfig(
            name="Qwen/Qwen3-Coder-480B-A35B-Instruct",
            provider="huggingface",
            api_key_env="HUGGINGFACE_API_KEY",
            temperature=0.5,
            max_tokens=4000,
            priority=60,
            description="HuggingFace Qwen3 Coder 480B (Free Tier)",
            is_free=True
        ))

        logger.info("✅ Loaded %d FREE models from default registry", len(self.models))

    def register_model(self, config: ModelConfig):
        """Register a new model"""
        self.models[config.name] = config
        logger.debug(f"📌 Registered model: {config.name} (Free: {config.is_free})")

    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get configuration for a model"""
        return self.models.get(name)

    def get_available_models(self) -> list[ModelConfig]:
        """Get all available models (those with API keys)"""
        available = []
        for model in self.models.values():
            if model.api_key_env:
                if os.getenv(model.api_key_env):
                    available.append(model)
            else:
                # Local models or those without keys
                available.append(model)

        # Sort by priority
        available.sort(key=lambda m: m.priority, reverse=True)
        return available

    def get_free_models(self) -> list[ModelConfig]:
        """Get all free models"""
        return [m for m in self.models.values() if m.is_free]

    def get_fallback_chain(self, primary_model: str) -> list[str]:
        """Get fallback chain for a primary model.

        Without considering priority, returns all available models.
        """
        available = self.get_available_models()
        model_names = [m.name for m in available]

        # If primary model is in the list, put it first
        if primary_model in model_names:
            model_names.remove(primary_model)
            model_names.insert(0, primary_model)

        logger.info(f"🔗 Fallback chain for {primary_model}: {model_names}")
        return model_names

    def export_config(self) -> dict:
        """Export configuration for logging and debugging"""
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
    """Get global model registry instance"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
