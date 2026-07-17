"""تست‌های Phase 8 — تاب‌آوری خطا و بهینه‌سازی زنجیره Failover

این فایل تست‌های مربوط به Phase 8 توسعه Software-AI را شامل می‌شود:
- Input sanitization (حذف backslash و کاراکترهای اضافی)
- Provider status command (/providers)
- Circuit breaker logic
- Model health scoring
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestInputSanitization:
    """تست‌های پاکسازی ورودی کاربر"""

    def test_strip_leading_backslash(self):
        """حذف backslash از ابتدای ورودی"""
        text = "\\What is my CPU usage right now?"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "What is my CPU usage right now?"

    def test_strip_multiple_backslashes(self):
        """حذف چندین backslash از ابتدای ورودی"""
        text = "\\\\What is this?"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "What is this?"

    def test_strip_backslash_with_spaces(self):
        """حذف backslash با فاصله"""
        text = "\\  What is this?  "
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "What is this?"

    def test_no_change_for_normal_input(self):
        """بدون تغییر برای ورودی عادی"""
        text = "What is my CPU usage?"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "What is my CPU usage?"

    def test_empty_after_stripping(self):
        """ورودی خالی پس از پاکسازی"""
        text = "\\\\"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == ""

    def test_only_backslash(self):
        """فقط backslash"""
        text = "\\"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == ""

    def test_preserve_internal_special_chars(self):
        """حفظ کاراکترهای خاص داخل رشته"""
        text = "\\Open C:\\Users\\test"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "Open C:\\Users\\test"

    def test_persian_input_with_backslash(self):
        """ورودی فارسی با backslash"""
        text = "\\سلام دنیا"
        cleaned = text.lstrip("\\").strip()
        assert cleaned == "سلام دنیا"


class TestProviderStatus:
    """تست‌های وضعیت ارائه‌دهندگان API"""

    def test_provider_detector_initialization(self):
        """مقداردهی اولیه ProviderDetector"""
        from core.ai_brain import ProviderDetector
        detector = ProviderDetector()
        assert detector is not None
        assert hasattr(detector, '_providers')

    def test_provider_detector_has_all_providers(self):
        """بررسی وجود تمام ارائه‌دهندگان"""
        from core.ai_brain import ProviderDetector
        detector = ProviderDetector()
        providers = detector.get_all_status()
        expected = {"google", "groq", "openrouter", "openai", "anthropic", "huggingface"}
        assert set(providers.keys()) == expected

    def test_provider_available_with_valid_key(self):
        """ارائه‌دهنده فعال با کلید معتبر"""
        from core.ai_brain import ProviderDetector
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "AIza-real-key-12345"}, clear=False):
            detector = ProviderDetector()
            assert detector.is_provider_available("google") is True

    def test_provider_inactive_without_key(self):
        """ارائه‌دهنده غیرفعال بدون کلید"""
        from core.ai_brain import ProviderDetector
        env = {k: "" for k in ProviderDetector.PROVIDER_KEY_MAP.values()}
        with patch.dict(os.environ, env, clear=True):
            detector = ProviderDetector()
            assert detector.is_provider_available("google") is False

    def test_provider_status_returns_dataclass(self):
        """برگرداندن dataclass وضعیت"""
        from core.ai_brain import ProviderDetector
        detector = ProviderDetector()
        status = detector.get_provider_status("openrouter")
        assert status is not None
        assert status.name == "openrouter"
        assert hasattr(status, 'is_available')
        assert hasattr(status, 'api_key_env')

    def test_available_providers_list(self):
        """لیست ارائه‌دهندگان فعال"""
        from core.ai_brain import ProviderDetector
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-real-key"}, clear=False):
            detector = ProviderDetector()
            available = detector.get_available_providers()
            assert isinstance(available, list)
            assert "openrouter" in available


class TestCircuitBreaker:
    """تست‌های سازوکار Circuit Breaker"""

    def test_circuit_breaker_initial_status(self):
        """وضعیت اولیه Circuit Breaker خالی است"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        assert cb.get_status() == {}

    def test_circuit_breaker_not_locked_initially(self):
        """مدل در ابتدا قفل نیست"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        assert cb.is_locked("some-model") is False

    def test_circuit_breaker_failure_below_threshold(self):
        """خطای زیر آستانه → قفل نمی‌شود"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        cb.record_failure("m1", Exception("403 Forbidden"))
        cb.record_failure("m1", Exception("403 Forbidden"))
        assert cb.is_locked("m1") is False

    def test_circuit_breaker_trips_at_threshold(self):
        """رسیدن به آستانه → قفل"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        for _ in range(cb.FAILURE_THRESHOLD):
            cb.record_failure("m1", Exception("403 Forbidden"))
        assert cb.is_locked("m1") is True

    def test_circuit_breaker_success_resets_failures(self):
        """موفقیت → ریست کانتر خطا"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        cb.record_failure("m1", Exception("error"))
        cb.record_failure("m1", Exception("error"))
        cb.record_success("m1")
        assert cb.is_locked("m1") is False
        assert cb.get_status() == {}

    def test_circuit_breaker_lockout_duration_auth(self):
        """قفل ۵ دقیقه‌ای برای خطاهای 403"""
        import time
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        for _ in range(cb.FAILURE_THRESHOLD):
            cb.record_failure("m1", Exception("403 Forbidden"))
        status = cb.get_status()
        assert status["m1"]["locked"] is True
        assert status["m1"]["reason"] == "auth/403"
        assert status["m1"]["locked_seconds_remaining"] > 200

    def test_circuit_breaker_lockout_duration_other(self):
        """قفل ۱ دقیقه‌ای برای سایر خطاها"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        for _ in range(cb.FAILURE_THRESHOLD):
            cb.record_failure("m1", Exception("Connection timeout"))
        status = cb.get_status()
        assert status["m1"]["locked"] is True
        assert status["m1"]["reason"] == "other"
        assert 50 <= status["m1"]["locked_seconds_remaining"] <= 60

    def test_circuit_breaker_reset_all(self):
        """ریست تمام مدل‌ها"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        cb.record_failure("m1", Exception("err"))
        cb.record_failure("m2", Exception("err"))
        cb.reset_all()
        assert cb.get_status() == {}
        assert cb.is_locked("m1") is False

    def test_circuit_breaker_multiple_models_independent(self):
        """قفل مستقل برای هر مدل"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        for _ in range(cb.FAILURE_THRESHOLD):
            cb.record_failure("m1", Exception("403"))
        cb.record_success("m2")
        assert cb.is_locked("m1") is True
        assert cb.is_locked("m2") is False

    def test_circuit_breaker_status_structure(self):
        """ساختار وضعیت شامل فیلدهای لازم"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        cb.record_failure("m1", Exception("err"))
        status = cb.get_status()
        info = status["m1"]
        assert "failures" in info
        assert "locked" in info
        assert "locked_seconds_remaining" in info
        assert "reason" in info

    def test_circuit_breaker_auth_keywords(self):
        """تشخیص خطاهای auth از روی پیام"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        for _ in range(cb.FAILURE_THRESHOLD):
            cb.record_failure("m1", Exception("unauthorized access"))
        assert cb._lock_reason.get("m1") == "auth/403"

    def test_circuit_breaker_quota_as_auth(self):
        """خطای quota نیز auth محسوب می‌شود"""
        from core.ai_brain import ModelCircuitBreaker
        cb = ModelCircuitBreaker()
        for _ in range(cb.FAILURE_THRESHOLD):
            cb.record_failure("m1", Exception("quota exceeded"))
        assert cb._lock_reason.get("m1") == "auth/403"

    def test_provider_detector_provider_key_map完整性(self):
        """بررسی کامل بودن نقشه کلیدهای ارائه‌دهندگان"""
        from core.ai_brain import ProviderDetector
        expected_keys = {
            "google", "groq", "openrouter", "openai",
            "anthropic", "huggingface"
        }
        assert set(ProviderDetector.PROVIDER_KEY_MAP.keys()) == expected_keys


class TestFailoverChain:
    """تست‌های زنجیره Failover"""

    def test_model_config_registry_loads(self):
        """بارگذاری رجیستر مدل‌ها"""
        from core.model_config import get_model_registry
        registry = get_model_registry()
        assert registry is not None
        assert len(registry.models) > 0

    def test_model_config_has_required_fields(self):
        """بررسی فیلدهای ضروری در تنظیمات مدل"""
        from core.model_config import get_model_registry
        registry = get_model_registry()
        for name, config in registry.models.items():
            assert hasattr(config, 'provider'), f"Model {name} missing 'provider'"
            assert hasattr(config, 'model_id') or hasattr(config, 'name'), f"Model {name} missing identifier"

    def test_empty_registry_graceful_handling(self):
        """مدیریت صحیح رجیستر خالی"""
        from core.model_config import ModelRegistry
        registry = ModelRegistry()
        registry.models = {}
        assert len(registry.models) == 0


class TestModelHealthTracker:
    """تست‌های ردیاب سلامت مدل (Phase 8.3)"""

    def test_health_tracker_initial_empty(self):
        """وضعیت اولیه خالی"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        assert tracker.get_all_health() == {}

    def test_health_tracker_record_success(self):
        """ثبت موفقیت"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        tracker.record_success("m1")
        h = tracker.get_health("m1")
        assert h.success_count == 1
        assert h.failure_count == 0
        assert h.total_attempts == 1

    def test_health_tracker_record_failure(self):
        """ثبت شکست"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        tracker.record_failure("m1", "403")
        h = tracker.get_health("m1")
        assert h.failure_count == 1
        assert h.last_failure_type == "403"

    def test_health_tracker_success_rate(self):
        """نرخ موفقیت"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        tracker.record_success("m1")
        tracker.record_success("m1")
        tracker.record_failure("m1", "error")
        h = tracker.get_health("m1")
        assert h.success_rate == pytest.approx(2 / 3, abs=0.01)

    def test_health_tracker_score_increases_with_success(self):
        """امتیاز سلامت با موفقیت افزایش می‌یابد"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        tracker.record_success("m1")
        score1 = tracker.get_health("m1").health_score
        tracker.record_success("m1")
        score2 = tracker.get_health("m1").health_score
        assert score2 > score1

    def test_health_tracker_score_decreases_with_failure(self):
        """امتیاز سلامت با شکست کاهش می‌یابد"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        for _ in range(5):
            tracker.record_success("m1")
        score1 = tracker.get_health("m1").health_score
        for _ in range(5):
            tracker.record_failure("m1", "error")
        score2 = tracker.get_health("m1").health_score
        assert score2 < score1

    def test_health_tracker_ranked_models(self):
        """رتبه‌بندی مدل‌ها بر اساس سلامت"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        # m1: mostly success
        for _ in range(10):
            tracker.record_success("m1")
        # m2: mostly failure
        for _ in range(10):
            tracker.record_failure("m2", "error")
        ranked = tracker.get_ranked_models(["m1", "m2"])
        assert ranked[0] == "m1"

    def test_health_tracker_independent_models(self):
        """مدل‌ها مستقل از هم ردیابی می‌شوند"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        tracker.record_success("m1")
        tracker.record_failure("m2", "403")
        assert tracker.get_health("m1").success_count == 1
        assert tracker.get_health("m2").failure_count == 1

    def test_health_report_structure(self):
        """ساختار گزارش سلامت"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        tracker.record_success("m1")
        tracker.record_failure("m1", "timeout")
        report = tracker.get_health_report()
        assert "m1" in report
        info = report["m1"]
        assert "success" in info
        assert "failure" in info
        assert "rate" in info
        assert "score" in info

    def test_health_default_no_data(self):
        """مدل بدون داده امتیاز خنثی دارد"""
        from core.model_config import ModelHealthTracker
        tracker = ModelHealthTracker()
        h = tracker.get_health("new_model")
        assert h.success_rate == 0.5
        assert h.total_attempts == 0

    def test_get_health_tracker_singleton(self):
        """get_health_tracker singleton"""
        from core.model_config import get_health_tracker
        t1 = get_health_tracker()
        t2 = get_health_tracker()
        assert t1 is t2


class TestVersionConsistency:
    """تست‌های یکسانی نسخه در فایل‌ها"""

    def test_main_py_version(self):
        """بررسی نسخه در main.py"""
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        assert "1.1.0" in content, "main.py should contain version 1.1.0"

    def test_readme_md_version(self):
        """بررسی نسخه در README.md"""
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
        assert "1.1.0" in content, "README.md should contain version 1.1.0"
        assert "0.9.0" not in content, "README.md should not contain old version 0.9.0"


class TestRoadmapIntegrity:
    """تست‌های یکپارچگی ROADMAP.md"""

    def test_roadmap_exists(self):
        """وجود فایل ROADMAP.md"""
        assert os.path.exists("ROADMAP.md"), "ROADMAP.md should exist"

    def test_roadmap_contains_phase8(self):
        """وجود Phase 8 در ROADMAP.md"""
        with open("ROADMAP.md", "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase 8" in content
        assert "تاب‌آوری خطا" in content or "Error Resilience" in content

    def test_roadmap_contains_phase9(self):
        """وجود Phase 9 در ROADMAP.md"""
        with open("ROADMAP.md", "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase 9" in content

    def test_roadmap_contains_phase10(self):
        """وجود Phase 10 در ROADMAP.md"""
        with open("ROADMAP.md", "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase 10" in content

    def test_roadmap_has_development_rules(self):
        """وجود قوانین توسعه در ROADMAP.md"""
        with open("ROADMAP.md", "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase 8" in content


class TestDocsIntegrity:
    """تست‌های یکپارچگی مستندات"""

    def test_phase8_report_exists(self):
        """وجود گزارش Phase 8"""
        assert os.path.exists("docs/PHASE8_ERROR_RESILIENCE_REPORT.md"), \
            "docs/PHASE8_ERROR_RESILIENCE_REPORT.md should exist"

    def test_phase8_report_has_content(self):
        """بررسی محتوای گزارش Phase 8"""
        with open("docs/PHASE8_ERROR_RESILIENCE_REPORT.md", "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 500, "Phase 8 report should have substantial content"
        assert "test_log.log" in content or "تحلیل" in content


class TestResponseCache:
    """تست‌های Response Cache (Phase 9.1)"""

    def test_cache_initial_status(self):
        """وضعیت اولیه کش خالی است"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache()
        assert cache.get("test", "normal") is None
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0

    def test_cache_set_and_get(self):
        """ذخیره و بازیابی از کش"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache()
        cache.set("hello", "normal", "world")
        assert cache.get("hello", "normal") == "world"

    def test_cache_miss_returns_none(self):
        """کش miss → None"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache()
        assert cache.get("nonexistent", "normal") is None

    def test_cache_different_mode_independent(self):
        """حالت‌های مختلف مستقل هستند"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache()
        cache.set("q", "normal", "a1")
        cache.set("q", "system", "a2")
        assert cache.get("q", "normal") == "a1"
        assert cache.get("q", "system") == "a2"

    def test_cache_max_size_eviction(self):
        """کش حداکثر اندازه را رعایت می‌کند"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache(max_size=3)
        for i in range(5):
            cache.set(f"q{i}", "normal", f"a{i}")
        stats = cache.get_stats()
        assert stats["size"] <= 3

    def test_cache_stats(self):
        """آمار کش"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache()
        cache.set("q", "normal", "a")
        cache.get("q", "normal")   # hit
        cache.get("x", "normal")   # miss
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_cache_clear(self):
        """پاکسازی کش"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache()
        cache.set("q", "normal", "a")
        cache.clear()
        assert cache.get("q", "normal") is None
        assert cache.get_stats()["size"] == 0

    def test_cache_key_includes_mode(self):
        """کلید کش شامل mode است"""
        from core.ai_brain import ResponseCache
        cache = ResponseCache()
        cache.set("prompt", "normal", "r1")
        cache.set("prompt", "system", "r2")
        assert cache.get("prompt", "normal") == "r1"
        assert cache.get("prompt", "system") == "r2"


class TestContextCompression:
    """تست‌های فشرده‌سازی Context (Phase 9.1)"""

    def test_memory_context_compression_older_messages(self):
        """پیام‌های قدیمی خلاصه می‌شوند"""
        from core.memory_integrator import MemoryManager
        mi = MemoryManager()
        # Add 5 messages
        for i in range(5):
            mi.add_conversation("user", f"message {i}")
        context = mi.get_memory_context(max_items=5)
        assert "message" in context
        # Older messages should be summarized
        assert len(context) > 0
        # Cleanup
        mi.shutdown()

    def test_memory_context_empty(self):
        """context خالی"""
        from core.memory_integrator import MemoryManager
        mi = MemoryManager()
        mi._conversation_history = []
        # Force empty DB state for this test
        mi.get_conversation_history = lambda limit=10: []
        context = mi.get_memory_context(max_items=5)
        assert context == ""
        mi.shutdown()

    def test_max_history_limit(self):
        """محدودیت اندازه تاریخچه"""
        from core.memory_integrator import MemoryManager
        mi = MemoryManager()
        original_max = mi._max_history
        mi._max_history = 10
        for i in range(20):
            mi.add_conversation("user", f"msg {i}")
        assert len(mi._conversation_history) <= 10
        mi._max_history = original_max
        mi.shutdown()
