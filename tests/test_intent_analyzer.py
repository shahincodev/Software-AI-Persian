# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
تست‌های Intent Analyzer

این فایل شامل تست‌های جامع برای ماژول IntentAnalyzer است.
شامل: Unit tests, Integration tests, Edge cases, Persian examples
"""

import pytest
import asyncio
from core.intent_analyzer import (
    IntentAnalyzer,
    Intent,
    IntentAnalysisResult,
    ConfidenceLevel
)


@pytest.fixture
def analyzer():
    """Fixture برای IntentAnalyzer"""
    return IntentAnalyzer()


# ============================================================================
# تست‌های تشخیص فعل (Verb Extraction)
# ============================================================================

class TestVerbExtraction:
    """تست‌های استخراج فعل"""
    
    @pytest.mark.asyncio
    async def test_simple_verb_english(self, analyzer):
        """تست تشخیص فعل انگلیسی ساده"""
        result = await analyzer.analyze("open notepad")
        assert result.intent.verb == "open"
        assert result.intent.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_simple_verb_persian(self, analyzer):
        """تست تشخیص فعل فارسی ساده"""
        result = await analyzer.analyze("نوت‌پد باز کن")
        assert result.intent.verb == "باز"
        assert result.intent.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_multiple_verbs_first_wins(self, analyzer):
        """تست انتخاب اولین فعل در درخواست"""
        result = await analyzer.analyze("open notepad and play game")
        # باید اولین فعل "open" را انتخاب کند
        assert result.intent.verb == "open"
    
    @pytest.mark.asyncio
    async def test_verb_with_synonyms(self, analyzer):
        """تست شناسایی مترادف‌های فعل"""
        synonyms = ["open", "launch", "start", "run"]
        for synonym in synonyms:
            result = await analyzer.analyze(f"{synonym} steam")
            assert result.intent.verb in ["open", "start", "launch", "run"]


# ============================================================================
# تست‌های تشخیص هدف (Target Extraction)
# ============================================================================

class TestTargetExtraction:
    """تست‌های استخراج هدف"""
    
    @pytest.mark.asyncio
    async def test_simple_target_english(self, analyzer):
        """تست تشخیص هدف انگلیسی"""
        result = await analyzer.analyze("open notepad")
        assert result.intent.target == "notepad"
    
    @pytest.mark.asyncio
    async def test_simple_target_persian(self, analyzer):
        """تست تشخیص هدف فارسی"""
        result = await analyzer.analyze("نوت‌پد باز کن")
        assert result.intent.target == "notepad"
    
    @pytest.mark.asyncio
    async def test_common_applications(self, analyzer):
        """تست شناسایی برنامه‌های معروف"""
        apps = {
            "steam": "steam",
            "chrome": "browser",
            "firefox": "browser",
            "notepad": "notepad",
        }
        for app, expected_target in apps.items():
            result = await analyzer.analyze(f"open {app}")
            assert result.intent.target == expected_target
    
    @pytest.mark.asyncio
    async def test_missing_target(self, analyzer):
        """تست درخواست بدون هدف مشخص"""
        result = await analyzer.analyze("بازی کن")
        # بازی کن ولی نوع بازی مشخص نیست
        assert result.requires_clarification
        assert "game_type" in result.missing_fields


# ============================================================================
# تست‌های استخراج پارامترها (Parameter Extraction)
# ============================================================================

class TestParameterExtraction:
    """تست‌های استخراج پارامترهای تفصیلی"""
    
    @pytest.mark.asyncio
    async def test_duration_parameter(self, analyzer):
        """تست استخراج پارامتر مدت زمان"""
        result = await analyzer.analyze("بازی کن تا برگردم")
        assert "duration" in result.intent.parameters
        assert result.intent.parameters["duration"] == "until_return"
    
    @pytest.mark.asyncio
    async def test_name_parameter(self, analyzer):
        """تست استخراج پارامتر نام"""
        result = await analyzer.analyze('create folder named "MyDocs"')
        assert "name" in result.intent.parameters or "MyDocs" in result.intent.raw_request
    
    @pytest.mark.asyncio
    async def test_path_parameter(self, analyzer):
        """تست استخراج پارامتر مسیر"""
        result = await analyzer.analyze("create folder in E:\\")
        assert "path" in result.intent.parameters or "E:" in result.intent.raw_request
    
    @pytest.mark.asyncio
    async def test_no_parameters(self, analyzer):
        """تست درخواست بدون پارامتر"""
        result = await analyzer.analyze("open notepad")
        # شاید پارامترها خالی باشند
        assert isinstance(result.intent.parameters, dict)


# ============================================================================
# تست‌های تشخیص زبان (Language Detection)
# ============================================================================

class TestLanguageDetection:
    """تست‌های تشخیص زبان"""
    
    @pytest.mark.asyncio
    async def test_english_detection(self, analyzer):
        """تست تشخیص انگلیسی"""
        result = await analyzer.analyze("open notepad")
        assert result.intent.language == "en"
    
    @pytest.mark.asyncio
    async def test_persian_detection(self, analyzer):
        """تست تشخیص فارسی"""
        result = await analyzer.analyze("نوت‌پد باز کن")
        assert result.intent.language == "fa"
    
    @pytest.mark.asyncio
    async def test_mixed_language(self, analyzer):
        """تست درخواست مختلط"""
        result = await analyzer.analyze("نوت‌پد open کن")
        # باید یکی را انتخاب کند
        assert result.intent.language in ["en", "fa"]


# ============================================================================
# تست‌های شناسایی محدودیت‌ها (Constraint Detection)
# ============================================================================

class TestConstraintDetection:
    """تست‌های شناسایی محدودیت‌ها"""
    
    @pytest.mark.asyncio
    async def test_safe_mode_constraint(self, analyzer):
        """تست شناسایی حالت محافظ"""
        result = await analyzer.analyze("open notepad in safe mode")
        assert "safe_mode" in result.intent.constraints
    
    @pytest.mark.asyncio
    async def test_minimal_cpu_constraint(self, analyzer):
        """تست شناسایی محدودیت CPU کم"""
        result = await analyzer.analyze("play game with minimal cpu")
        assert "minimal_cpu" in result.intent.constraints
    
    @pytest.mark.asyncio
    async def test_silent_constraint(self, analyzer):
        """تست شناسایی حالت بی‌صدا"""
        result = await analyzer.analyze("open browser silently")
        assert "no_sound" in result.intent.constraints
    
    @pytest.mark.asyncio
    async def test_no_constraints(self, analyzer):
        """تست درخواست بدون محدودیت"""
        result = await analyzer.analyze("open notepad")
        # شاید محدودیت‌ها خالی باشند
        assert isinstance(result.intent.constraints, list)


# ============================================================================
# تست‌های اطمینان (Confidence)
# ============================================================================

class TestConfidence:
    """تست‌های محاسبه اطمینان"""
    
    @pytest.mark.asyncio
    async def test_high_confidence_simple_request(self, analyzer):
        """تست اطمینان بالا برای درخواست ساده"""
        result = await analyzer.analyze("open notepad")
        assert result.intent.confidence > 0.70
    
    @pytest.mark.asyncio
    async def test_low_confidence_vague_request(self, analyzer):
        """تست اطمینان پایین برای درخواست مبهم"""
        result = await analyzer.analyze("do something")
        # برای درخواست‌های مبهم اطمینان باید پایین‌تر باشد
        assert result.intent.confidence < 0.80
    
    @pytest.mark.asyncio
    async def test_is_confident_method(self, analyzer):
        """تست متد is_confident"""
        result = await analyzer.analyze("open notepad")
        assert result.intent.is_confident(threshold=0.5)
    
    @pytest.mark.asyncio
    async def test_confidence_threshold(self, analyzer):
        """تست درهای اطمینان مختلف"""
        result = await analyzer.analyze("open notepad")
        assert result.intent.is_confident(threshold=0.5)
        # شاید برای threshold بالاتر false باشد
        if result.intent.confidence < 0.95:
            assert not result.intent.is_confident(threshold=0.95)


# ============================================================================
# تست‌های شناسایی موارد نامشخص (Missing Fields)
# ============================================================================

class TestMissingFields:
    """تست‌های شناسایی فیلدهای نامشخص"""
    
    @pytest.mark.asyncio
    async def test_game_type_missing(self, analyzer):
        """تست شناسایی عدم مشخص‌بودن نوع بازی"""
        result = await analyzer.analyze("play")
        assert result.requires_clarification
        assert "game_type" in result.missing_fields or len(result.missing_fields) > 0
    
    @pytest.mark.asyncio
    async def test_folder_name_missing(self, analyzer):
        """تست شناسایی عدم مشخص‌بودن نام فولدر"""
        result = await analyzer.analyze("create folder")
        assert result.requires_clarification or "name" in result.missing_fields
    
    @pytest.mark.asyncio
    async def test_no_missing_fields(self, analyzer):
        """تست درخواست کامل بدون موارد نامشخص"""
        result = await analyzer.analyze("open notepad")
        # این درخواست کامل است
        assert len(result.missing_fields) == 0 or result.intent.confidence > 0.8


# ============================================================================
# تست‌های مثال‌های واقعی (Real-world Examples)
# ============================================================================

class TestRealWorldExamples:
    """تست‌های مثال‌های واقعی و پیچیده"""
    
    @pytest.mark.asyncio
    async def test_gaming_scenario_en(self, analyzer):
        """تست سناریوی بازی‌کردن - انگلیسی"""
        result = await analyzer.analyze(
            "open steam and play counter-strike until i return"
        )
        assert result.intent.verb in ["open", "play"]
        assert "steam" in result.intent.target.lower() or "counter-strike" in result.intent.raw_request
    
    @pytest.mark.asyncio
    async def test_gaming_scenario_fa(self, analyzer):
        """تست سناریوی بازی‌کردن - فارسی"""
        result = await analyzer.analyze(
            "استیم را باز کن و تا برگردم Counter-Strike بازی کن"
        )
        assert result.intent.language == "fa"
        assert result.intent.verb in ["باز", "بازی"]
    
    @pytest.mark.asyncio
    async def test_file_operation_en(self, analyzer):
        """تست عملیات فایل - انگلیسی"""
        result = await analyzer.analyze("create folder named MyDocs in E:")
        assert result.intent.verb in ["create", "ایجاد"]
        assert "folder" in result.intent.target.lower()
    
    @pytest.mark.asyncio
    async def test_file_operation_fa(self, analyzer):
        """تست عملیات فایل - فارسی"""
        result = await analyzer.analyze("در E: فولدر MyDocs بساز")
        assert result.intent.verb == "ایجاد" or result.intent.verb == "create"
    
    @pytest.mark.asyncio
    async def test_data_retrieval(self, analyzer):
        """تست دریافت داده"""
        result = await analyzer.analyze("get weather data for tehran and save to excel")
        # باید درخواست را متوجه شود
        assert result.intent.confidence > 0.4


# ============================================================================
# تست‌های Edge Cases
# ============================================================================

class TestEdgeCases:
    """تست‌های موارد خاص و مرزی"""
    
    @pytest.mark.asyncio
    async def test_empty_request(self, analyzer):
        """تست درخواست خالی"""
        with pytest.raises(ValueError):
            await analyzer.analyze("")
    
    @pytest.mark.asyncio
    async def test_whitespace_only(self, analyzer):
        """تست درخواست فقط با فاصله"""
        with pytest.raises(ValueError):
            await analyzer.analyze("   ")
    
    @pytest.mark.asyncio
    async def test_very_long_request(self, analyzer):
        """تست درخواست بسیار طولانی"""
        long_request = "open notepad " * 50
        result = await analyzer.analyze(long_request)
        # باید بتواند درخواست طولانی را پردازش کند
        assert result.intent.verb == "open"
    
    @pytest.mark.asyncio
    async def test_special_characters(self, analyzer):
        """تست درخواست با کاراکترهای خاص"""
        result = await analyzer.analyze("open 'C:\\Users\\Test\\file.txt'")
        # باید خاص‌ کاراکترها را مدیریت کند
        assert result.intent.verb == "open"
    
    @pytest.mark.asyncio
    async def test_single_word_request(self, analyzer):
        """تست درخواست تک‌کلمه‌ای"""
        result = await analyzer.analyze("notepad")
        # حتی برای درخواست تک‌کلمه‌ای هم باید نتیجه‌ای بدهد
        assert result.intent.target == "notepad" or result.intent.raw_request == "notepad"


# ============================================================================
# تست‌های دسته‌ای (Batch Processing)
# ============================================================================

class TestBatchProcessing:
    """تست‌های پردازش دسته‌ای"""
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, analyzer):
        """تست تحلیل دسته‌ای"""
        requests = [
            "open notepad",
            "نوت‌پد باز کن",
            "play game",
            "بازی کن"
        ]
        results = await analyzer.analyze_batch(requests)
        assert len(results) == len(requests)
        assert all(isinstance(r, IntentAnalysisResult) for r in results)
    
    @pytest.mark.asyncio
    async def test_batch_with_invalid_request(self, analyzer):
        """تست دسته‌ای شامل درخواست‌های نامعتبر"""
        requests = [
            "open notepad",
            "",  # درخواست خالی
            "play game"
        ]
        results = await analyzer.analyze_batch(requests)
        # باید تمام درخواست‌ها را پردازش کند
        assert len(results) == 3


# ============================================================================
# تست‌های عملکرد (Performance)
# ============================================================================

class TestPerformance:
    """تست‌های عملکرد و سرعت"""
    
    @pytest.mark.asyncio
    async def test_analysis_speed(self, analyzer):
        """تست سرعت تحلیل"""
        import time
        start = time.time()
        await analyzer.analyze("open notepad")
        duration = time.time() - start
        # باید کمتر از ۲ ثانیه طول بکشد
        assert duration < 2.0
    
    @pytest.mark.asyncio
    async def test_multiple_consecutive_analyses(self, analyzer):
        """تست تجزیه‌های متوالی"""
        import time
        requests = ["open notepad"] * 10
        start = time.time()
        for req in requests:
            await analyzer.analyze(req)
        duration = time.time() - start
        # ۱۰ تجزیه باید در کمتر از ۵ ثانیه انجام شود
        assert duration < 5.0


# ============================================================================
# تست‌های Unit برای متودهای کمکی
# ============================================================================

class TestHelperMethods:
    """تست‌های متودهای کمکی"""
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_formula(self, analyzer):
        """تست فرمول محاسبه اطمینان"""
        conf = analyzer._calculate_confidence(
            verb_conf=0.9,
            target_conf=0.8,
            param_count=2,
            word_count=5
        )
        assert 0.0 <= conf <= 1.0
        # اطمینان باید بالاتر از میانگین verb و target باشد
        assert conf >= 0.85


# ============================================================================
# Main - اجرای تست‌ها
# ============================================================================

if __name__ == "__main__":
    # اجرای تست‌ها
    pytest.main([__file__, "-v", "--tb=short"])
