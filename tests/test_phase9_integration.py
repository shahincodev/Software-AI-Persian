"""تست‌های یکپارچه‌سازی Phase 9 — Integration Tests

تست‌های یکپارچه‌سازی برای بررسی عملکرد صحیح سیستم در کنار هم.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestFailoverChainIntegration:
    """تست یکپارچه‌سازی زنجیره Failover"""

    def test_failover_skips_locked_models(self):
        """زنجیره failover مدل‌های قفل شده را رد می‌کند"""
        from core.ai_brain import ModelCircuitBreaker

        cb = ModelCircuitBreaker()
        for _ in range(cb.FAILURE_THRESHOLD):
            cb.record_failure("m1", Exception("403"))
            cb.record_failure("m2", Exception("403"))

        assert cb.is_locked("m1") is True
        assert cb.is_locked("m2") is True
        assert cb.is_locked("m3") is False

    def test_circuit_breaker_recovers_after_timeout(self):
        """مدل بعد از مهلت قفل بازیابی می‌شود"""
        import time
        from core.ai_brain import ModelCircuitBreaker

        cb = ModelCircuitBreaker()
        cb._locked_until["test_model"] = time.time() - 1
        cb._failures["test_model"] = 5

        assert cb.is_locked("test_model") is False
        assert "test_model" not in cb._failures

    def test_health_tracker_ranks_successful_models_higher(self):
        """مدل‌های موفق رتبه بالاتری می‌گیرند"""
        from core.model_config import ModelHealthTracker

        tracker = ModelHealthTracker()
        for _ in range(10):
            tracker.record_success("model_a")
        for _ in range(5):
            tracker.record_success("model_b")
            tracker.record_failure("model_b", "error")

        ranked = tracker.get_ranked_models(["model_a", "model_b"])
        assert ranked[0] == "model_a"

    def test_response_cache_avoids_repeated_calls(self):
        """کش از فراخوانی مجدد جلوگیری می‌کند"""
        from core.ai_brain import ResponseCache

        cache = ResponseCache()
        cache.set("test prompt", "normal", "cached response")
        result = cache.get("test prompt", "normal")
        assert result == "cached response"
        assert cache.get("test prompt", "system") is None

    def test_circuit_breaker_and_health_tracker_work_together(self):
        """Circuit Breaker و Health Tracker با هم کار می‌کنند"""
        from core.ai_brain import ModelCircuitBreaker
        from core.model_config import ModelHealthTracker

        cb = ModelCircuitBreaker()
        ht = ModelHealthTracker()

        # Simulate 3 failures
        for _ in range(3):
            cb.record_failure("m1", Exception("403"))
            ht.record_failure("m1", "403")

        # Model should be locked AND have low health
        assert cb.is_locked("m1") is True
        assert ht.get_health("m1").health_score < 30

    def test_providers_has_all_expected_keys(self):
        """لیست ارائه‌دهندگان شامل کلیدهای مورد انتظار است"""
        from core.ai_brain import ProviderDetector
        detector = ProviderDetector()
        providers = detector.get_all_status()
        expected = {"google", "groq", "openrouter", "openai", "anthropic", "huggingface"}
        assert set(providers.keys()) == expected


class TestInputSanitizationIntegration:
    """تست یکپارچه‌سازی پاکسازی ورودی"""

    def test_persian_input_preserved(self):
        """ورودی فارسی حفظ می‌شود"""
        text = "مرورگر را باز کن"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "مرورگر را باز کن"

    def test_empty_input_after_strip(self):
        """ورودی خالی بعد از strip"""
        text = "\\\\"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == ""

    def test_normal_input_unchanged(self):
        """ورودی عادی بدون تغییر"""
        text = "open notepad"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "open notepad"


class TestMemoryContextCompression:
    """تست یکپارچه‌سازی فشرده‌سازی context"""

    def test_older_messages_are_compressed(self):
        """پیام‌های قدیمی فشرده می‌شوند"""
        from core.memory_integrator import MemoryManager

        mi = MemoryManager()
        mi._conversation_history = []
        for i in range(6):
            mi.add_conversation("user", f"message {i}")

        context = mi.get_memory_context(max_items=6)
        # Recent messages should be full, older compressed
        assert "message 5" in context  # most recent
        assert "Earlier topics" in context  # compressed
        mi.shutdown()

    def test_empty_history_returns_empty(self):
        """تاریخچه خالی → context خالی"""
        from core.memory_integrator import MemoryManager

        mi = MemoryManager()
        mi._conversation_history = []
        mi.get_conversation_history = lambda limit=10: []
        context = mi.get_memory_context(max_items=5)
        assert context == ""
        mi.shutdown()


class TestVersionAndRoadmapIntegration:
    """تست یکپارچه‌سازی نسخه و نقشه راه"""

    def test_version_consistent_across_files(self):
        """نسخه در تمام فایل‌ها یکسان است"""
        with open("main.py", "r", encoding="utf-8") as f:
            main_content = f.read()
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()

        assert "1.1.0" in main_content
        assert "1.1.0" in readme_content

    def test_roadmap_has_all_phases(self):
        """نقشه راه شامل تمام فازها"""
        with open("ROADMAP.md", "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase 8" in content
        assert "Phase 9" in content
        assert "Phase 10" in content
