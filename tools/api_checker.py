#!/usr/bin/env python3
"""
Smart API Checker - بررسی‌کننده هوشمند API
==========================================

برنامه‌ای هوشمند برای بررسی وضعیت APIها و انتخاب خودکار مدل‌های رایگان
مانند سیستم OpenCode - شما API را وارد می‌کنید، ما مدل را انتخاب می‌کنیم.

Usage:
    python tools/api_checker.py                    # بررسی کامل
    python tools/api_checker.py --provider google   # بررسی یک ارائه‌دهنده
    python tools/api_checker.py --auto-configure    # پیکربندی خودکار
    python tools/api_checker.py --available-only    # فقط مدل‌های دردسترس
    python tools/api_checker.py --test-model gemini-2.5-flash  # تست مدل خاص
"""

from __future__ import annotations

import os
import sys
import time
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


@dataclass
class ProviderStatus:
    """وضعیت یک ارائه‌دهنده API"""
    name: str
    api_key_env: str
    api_key_set: bool = False
    is_valid: bool = False
    response_time_ms: float = 0.0
    available_models: list[str] = None
    error_message: str = ""

    def __post_init__(self):
        if self.available_models is None:
            self.available_models = []


@dataclass
class ModelTestResult:
    """نتیجه تست یک مدل"""
    model_name: str
    provider: str
    success: bool
    response_time_ms: float = 0.0
    response_preview: str = ""
    error_message: str = ""


class SmartAPIChecker:
    """بررسی‌کننده هوشمند API - مانند OpenCode"""

    # نقشه ارائه‌دهندگان به متغیرهای محیطی
    PROVIDERS = {
        "google": {
            "env_key": "GOOGLE_API_KEY",
            "test_model": "gemini-2.5-flash",
            "free_models": ["gemini-2.5-flash"],
        },
        "groq": {
            "env_key": "GROQ_API_KEY",
            "test_model": "llama-3.3-70b-versatile",
            "free_models": ["llama-3.3-70b-versatile", "qwen-qwq-32b"],
        },
        "openrouter": {
            "env_key": "OPENROUTER_API_KEY",
            "test_model": "openrouter/free",
            "free_models": [
                "openai/gpt-oss-120b:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "qwen/qwen3-235b-a22b:free",
                "nvidia/nemotron-3-ultra-550b-a55b:free",
                "qwen/qwen3-coder:free",
                "openrouter/free",
            ],
        },
        "huggingface": {
            "env_key": "HUGGINGFACE_API_KEY",
            "test_model": "deepseek-ai/DeepSeek-V3.2",
            "free_models": ["deepseek-ai/DeepSeek-V3.2"],
        },
    }

    def __init__(self, env_file: Optional[Path] = None):
        self.env_file = env_file or PROJECT_ROOT / ".env"
        self._load_env()
        self.statuses: dict[str, ProviderStatus] = {}

    def _load_env(self):
        """بارگذاری متغیرهای محیطی از فایل .env"""
        if self.env_file.exists():
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and not value.startswith("your-"):
                            os.environ[key] = value

    def check_provider(self, provider_name: str) -> ProviderStatus:
        """بررسی وضعیت یک ارائه‌دهنده"""
        if provider_name not in self.PROVIDERS:
            return ProviderStatus(
                name=provider_name,
                api_key_env="UNKNOWN",
                error_message=f"Unknown provider: {provider_name}"
            )

        config = self.PROVIDERS[provider_name]
        env_key = config["env_key"]
        api_key = os.environ.get(env_key, "").strip()

        status = ProviderStatus(
            name=provider_name,
            api_key_env=env_key,
            api_key_set=bool(api_key),
            is_valid=False,
            available_models=config["free_models"] if api_key else []
        )

        if not api_key:
            status.error_message = "API key not set"
            return status

        if api_key.startswith("your-") or api_key.startswith("AIza-your-"):
            status.error_message = "API key appears to be placeholder"
            return status

        # Test the API
        start_time = time.time()
        try:
            success = self._test_provider_api(provider_name, api_key)
            status.response_time_ms = (time.time() - start_time) * 1000
            status.is_valid = success
            if not success:
                status.error_message = "API test failed"
        except Exception as e:
            status.response_time_ms = (time.time() - start_time) * 1000
            status.error_message = str(e)

        return status

    def _test_provider_api(self, provider: str, api_key: str) -> bool:
        """تست API یک ارائه‌دهنده"""
        try:
            if provider == "google":
                return self._test_google_api(api_key)
            elif provider == "groq":
                return self._test_groq_api(api_key)
            elif provider == "openrouter":
                return self._test_openrouter_api(api_key)
            elif provider == "huggingface":
                return self._test_huggingface_api(api_key)
            return False
        except Exception:
            return False

    def _test_google_api(self, api_key: str) -> bool:
        """تست Google AI Studio API"""
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def _test_groq_api(self, api_key: str) -> bool:
        """تست Groq API"""
        try:
            import requests
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def _test_openrouter_api(self, api_key: str) -> bool:
        """تست OpenRouter API"""
        try:
            import requests
            url = "https://openrouter.ai/api/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def _test_huggingface_api(self, api_key: str) -> bool:
        """تست HuggingFace Inference API"""
        try:
            import requests
            url = "https://huggingface.co/api/whoami-v2"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def check_all_providers(self) -> dict[str, ProviderStatus]:
        """بررسی تمام ارائه‌دهندگان"""
        results = {}
        for provider_name in self.PROVIDERS:
            results[provider_name] = self.check_provider(provider_name)
        self.statuses = results
        return results

    def get_available_providers(self) -> list[str]:
        """دریافت لیست ارائه‌دهندگان فعال"""
        if not self.statuses:
            self.check_all_providers()
        return [name for name, status in self.statuses.items() if status.is_valid]

    def get_recommended_model(self) -> Optional[str]:
        """انتخاب بهترین مدل رایگان بر اساس اولویت"""
        if not self.statuses:
            self.check_all_providers()

        # Priority order: Google > Groq > OpenRouter > HuggingFace
        priority_order = ["google", "groq", "openrouter", "huggingface"]

        for provider_name in priority_order:
            status = self.statuses.get(provider_name)
            if status and status.is_valid and status.available_models:
                return status.available_models[0]

        return None

    def display_status_table(self, available_only: bool = False):
        """نمایش جدول وضعیت"""
        if not self.statuses:
            self.check_all_providers()

        print("\n" + "=" * 70)
        print("🔍 Smart API Checker - بررسی‌کننده هوشمند API")
        print("=" * 70)

        # Header
        print(f"\n{'Provider':<15} {'Status':<10} {'Models':<10} {'Response':<12} {'Key Set':<10}")
        print("-" * 70)

        for name, status in self.statuses.items():
            if available_only and not status.is_valid:
                continue

            # Status icon
            if status.is_valid:
                status_icon = "✅"
            elif status.api_key_set:
                status_icon = "⚠️"
            else:
                status_icon = "❌"

            # Models count
            models_count = str(len(status.available_models)) if status.is_valid else "0"

            # Response time
            response_time = f"{status.response_time_ms:.0f}ms" if status.response_time_ms > 0 else "-"

            # Key set
            key_set = "Yes" if status.api_key_set else "No"

            print(f"{name:<15} {status_icon:<10} {models_count:<10} {response_time:<12} {key_set:<10}")

            if status.error_message and status.api_key_set:
                print(f"{'':>15} └─ {status.error_message}")

        print("-" * 70)

        # Summary
        available = self.get_available_providers()
        total_models = sum(len(s.available_models) for s in self.statuses.values() if s.is_valid)

        print(f"\n📊 Summary: {len(available)}/{len(self.statuses)} providers active, {total_models} free models available")

        if available:
            recommended = self.get_recommended_model()
            if recommended:
                print(f"🎯 Recommended model: {recommended}")
        else:
            print("\n⚠️  No providers active! Please set API keys in .env file")
            print("   Get free API keys:")
            print("   - Google: https://aistudio.google.com/app/apikeys")
            print("   - Groq: https://console.groq.com")
            print("   - OpenRouter: https://openrouter.ai")
            print("   - HuggingFace: https://huggingface.co/settings/tokens")

        print("=" * 70 + "\n")

    def auto_configure_env(self):
        """پیکربندی خودکار فایل .env با بهترین مدل‌ها"""
        if not self.statuses:
            self.check_all_providers()

        recommended = self.get_recommended_model()
        if not recommended:
            print("❌ Cannot auto-configure: No providers active")
            return False

        # Read current .env
        env_content = ""
        if self.env_file.exists():
            with open(self.env_file, "r", encoding="utf-8") as f:
                env_content = f.read()

        # Add or update RECOMMENDED_MODEL
        lines = env_content.split("\n")
        new_lines = []
        model_found = False

        for line in lines:
            if line.strip().startswith("RECOMMENDED_MODEL="):
                new_lines.append(f"RECOMMENDED_MODEL={recommended}")
                model_found = True
            else:
                new_lines.append(line)

        if not model_found:
            new_lines.append("\n# مدل پیشنهادی توسط Smart API Checker")
            new_lines.append(f"RECOMMENDED_MODEL={recommended}")

        # Write back
        with open(self.env_file, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        print(f"✅ Auto-configured .env with recommended model: {recommended}")
        return True

    def test_model(self, model_name: str) -> ModelTestResult:
        """تست یک مدل خاص"""
        # Find provider for this model
        for provider_name, config in self.PROVIDERS.items():
            if model_name in config["free_models"]:
                status = self.check_provider(provider_name)
                if status.is_valid:
                    return ModelTestResult(
                        model_name=model_name,
                        provider=provider_name,
                        success=True,
                        response_time_ms=status.response_time_ms
                    )
                else:
                    return ModelTestResult(
                        model_name=model_name,
                        provider=provider_name,
                        success=False,
                        error_message=status.error_message
                    )

        return ModelTestResult(
            model_name=model_name,
            provider="unknown",
            success=False,
            error_message="Model not found in any provider"
        )


def main():
    """تابع اصلی"""
    # Fix encoding for Windows console
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="Smart API Checker - بررسی‌کننده هوشمند API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/api_checker.py                    # Full check
  python tools/api_checker.py --provider google   # Check specific provider
  python tools/api_checker.py --auto-configure    # Auto-configure .env
  python tools/api_checker.py --available-only    # Show only available
  python tools/api_checker.py --test-model gemini-2.5-flash  # Test specific model
        """
    )

    parser.add_argument("--provider", "-p", help="Check specific provider")
    parser.add_argument("--auto-configure", "-a", action="store_true", help="Auto-configure .env")
    parser.add_argument("--available-only", action="store_true", help="Show only available providers")
    parser.add_argument("--test-model", "-t", help="Test specific model")
    parser.add_argument("--env-file", type=Path, help="Path to .env file")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )

    # Create checker
    checker = SmartAPIChecker(env_file=args.env_file)

    if args.provider:
        # Check specific provider
        status = checker.check_provider(args.provider)
        print(f"\n{args.provider}: {'✅ Active' if status.is_valid else '❌ Inactive'}")
        if status.error_message:
            print(f"  Error: {status.error_message}")
        if status.available_models:
            print(f"  Free models: {', '.join(status.available_models)}")

    elif args.test_model:
        # Test specific model
        result = checker.test_model(args.test_model)
        print(f"\nModel: {result.model_name}")
        print(f"Provider: {result.provider}")
        print(f"Status: {'✅ Success' if result.success else '❌ Failed'}")
        if result.error_message:
            print(f"Error: {result.error_message}")

    elif args.auto_configure:
        # Auto-configure
        checker.check_all_providers()
        checker.auto_configure_env()
        checker.display_status_table(available_only=args.available_only)

    else:
        # Full check
        checker.check_all_providers()
        checker.display_status_table(available_only=args.available_only)


if __name__ == "__main__":
    main()
