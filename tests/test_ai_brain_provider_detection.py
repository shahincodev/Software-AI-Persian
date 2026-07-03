"""تست‌های شناسایی هوشمند ارائه‌دهندگان API در ai_brain.py"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestProviderDetector:
    """تست‌های کلاس ProviderDetector"""

    def test_detect_providers_with_valid_google_key(self):
        """تشخیص ارائه‌دهنده Google با کلید معتبر"""
        from core.ai_brain import ProviderDetector

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "AIza-real-key-12345"}):
            detector = ProviderDetector()
            assert detector.is_provider_available("google") is True
            assert "google" in detector.get_available_providers()

    def test_detect_providers_with_invalid_key(self):
        """عدم تشخیص ارائه‌دهنده با کلید نامعتبر"""
        from core.ai_brain import ProviderDetector

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "your-google-api-key-here"}):
            detector = ProviderDetector()
            assert detector.is_provider_available("google") is False

    def test_detect_providers_with_empty_key(self):
        """عدم تشخیص ارائه‌دهنده با کلید خالی"""
        from core.ai_brain import ProviderDetector

        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}):
            detector = ProviderDetector()
            assert detector.is_provider_available("google") is False

    def test_detect_multiple_providers(self):
        """تشخیص چند ارائه‌دهنده به صورت همزمان"""
        from core.ai_brain import ProviderDetector

        env_vars = {
            "GOOGLE_API_KEY": "AIza-real-google-key",
            "GROQ_API_KEY": "gsk-real-groq-key",
            "OPENROUTER_API_KEY": "sk-or-v1-real-openrouter-key",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            detector = ProviderDetector()
            available = detector.get_available_providers()

            assert "google" in available
            assert "groq" in available
            assert "openrouter" in available

    def test_get_provider_status(self):
        """دریافت وضعیت یک ارائه‌دهنده"""
        from core.ai_brain import ProviderDetector

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "AIza-real-key"}):
            detector = ProviderDetector()
            status = detector.get_provider_status("google")

            assert status is not None
            assert status.name == "google"
            assert status.is_available is True
            assert status.api_key_env == "GOOGLE_API_KEY"

    def test_get_all_status(self):
        """دریافت وضعیت تمام ارائه‌دهندگان"""
        from core.ai_brain import ProviderDetector

        detector = ProviderDetector()
        all_status = detector.get_all_status()

        assert isinstance(all_status, dict)
        assert "google" in all_status
        assert "groq" in all_status
        assert "openrouter" in all_status

    def test_log_summary(self):
        """نمایش خلاصه وضعیت ارائه‌دهندگان"""
        from core.ai_brain import ProviderDetector

        detector = ProviderDetector()
        # فقط بررسی اینکه تابع خطا ندهد
        detector.log_summary()


class TestAIBrainProviderDetection:
    """تست‌های شناسایی ارائه‌دهندگان در AIBrain"""

    def test_ai_brain_initialization_with_providers(self):
        """مقداردهی اولیه AIBrain با ارائه‌دهندگان فعال"""
        from core.ai_brain import AIBrain

        env_vars = {
            "GOOGLE_API_KEY": "AIza-real-google-key",
            "GROQ_API_KEY": "gsk-real-groq-key",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            brain = AIBrain()
            info = brain.get_provider_info()

            assert "google" in info["available_providers"]
            assert "groq" in info["available_providers"]

    def test_get_provider_info(self):
        """دریافت اطلاعات ارائه‌دهندگان"""
        from core.ai_brain import AIBrain

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "AIza-real-key"}):
            brain = AIBrain()
            info = brain.get_provider_info()

            assert "available_providers" in info
            assert "total_providers" in info
            assert "providers" in info
            assert isinstance(info["providers"], dict)

    def test_task_complexity_analysis(self):
        """تحلیل پیچیدگی تسک"""
        from core.ai_brain import AIBrain

        brain = AIBrain()

        # تسک سیستمی
        assert brain._analyze_task_complexity("open notepad") == "system"
        assert brain._analyze_task_complexity("نصب برنامه") == "system"

        # تسک مرورگری
        assert brain._analyze_task_complexity("browse website") == "browse"
        assert brain._analyze_task_complexity("جستجو در گوگل") == "browse"

        # تسک تحلیلی
        assert brain._analyze_task_complexity("analyze this code") == "analyze"
        assert brain._analyze_task_complexity("این کد را تحلیل کن") == "analyze"

        # تسک سریع
        assert brain._analyze_task_complexity("quick search") == "realtime"

        # تسک عادی
        assert brain._analyze_task_complexity("hello") == "normal"


class TestAIBrainModelLoading:
    """تست‌های بارگذاری مدل در AIBrain"""

    def test_load_model_with_unavailable_provider(self):
        """خطا هنگام بارگذاری مدل از ارائه‌دهنده غیرفعال"""
        from core.ai_brain import AIBrain

        # بدون هیچ کلید API
        env_vars = {
            "GOOGLE_API_KEY": "",
            "GROQ_API_KEY": "",
            "OPENROUTER_API_KEY": "",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            brain = AIBrain()

            # تلاش برای بارگذاری مدل Google باید خطا دهد
            with pytest.raises(ValueError, match="not available"):
                brain._load_model("google-gemini-3-pro-preview")


class TestAIBrainSanitizeResponse:
    """تست‌های پاکسازی پاسخ AI"""

    def test_sanitize_removes_thinking_pattern(self):
        """حذف الگوی thinking از پاسخ"""
        from core.ai_brain import AIBrain

        brain = AIBrain()
        response = "thinking='some internal thought'Hello world"
        cleaned = brain._sanitize_ai_response(response)

        assert "thinking=" not in cleaned
        assert "Hello world" in cleaned

    def test_sanitize_extracts_exe_name(self):
        """استخراج نام فایل exe از completion"""
        from core.ai_brain import AIBrain

        brain = AIBrain()
        response = "completion='notepad.exe'"
        cleaned = brain._sanitize_ai_response(response)

        assert cleaned == "notepad.exe"

    def test_sanitize_no_change_for_clean_response(self):
        """بدون تغییر برای پاسخ تمیز"""
        from core.ai_brain import AIBrain

        brain = AIBrain()
        response = "Hello, how can I help you?"
        cleaned = brain._sanitize_ai_response(response)

        assert cleaned == response


class TestAIBrainJsonExtraction:
    """تست‌های استخراج JSON از پاسخ AI"""

    def test_extract_json_array(self):
        """استخراج آرایه JSON از پاسخ"""
        from core.ai_brain import AIBrain

        brain = AIBrain()
        response = '''Here are the actions:
        [{"type": "LaunchApp", "params": {"app_name": "notepad.exe"}}]
        '''
        actions = brain._extract_json_actions(response)

        assert isinstance(actions, list)
        assert len(actions) == 1
        assert actions[0]["type"] == "LaunchApp"

    def test_extract_json_with_markdown(self):
        """استخراج JSON از کد مارک‌داون"""
        from core.ai_brain import AIBrain

        brain = AIBrain()
        response = '''```json
        [{"type": "DesktopClick", "params": {"target": "OK"}}]
        ```'''
        actions = brain._extract_json_actions(response)

        assert isinstance(actions, list)
        assert len(actions) == 1

    def test_extract_empty_response(self):
        """استخراج از پاسخ خالی"""
        from core.ai_brain import AIBrain

        brain = AIBrain()
        actions = brain._extract_json_actions("")

        assert actions == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
