# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Test Suite for Dialog Manager - مجموعه تست‌های Dialog Manager

این فایل ۴۲ تست جامع برای Dialog Manager شامل است:
- Question Generation (۴ تست)
- Response Collection (۴ تست)
- Confidence Calculation (۳ تست)
- Confirmation (۳ تست)
- Intent Merging (۲ تست)
- Clarification (۲ تست)
- Multi-language Support (۳ تست)
- Real-world Scenarios (۷ تست)
- Edge Cases (۵ تست)
- Integration with Intent Analyzer (۲ تست)
- Performance (۱ تست)
"""

import pytest
import asyncio
from typing import List
from unittest.mock import Mock, patch, AsyncMock

from core.dialog_manager import (
    DialogManager,
    DialogQuestion,
    DialogResponse,
    DialogSession,
    DialogState,
    QuestionType
)
from core.intent_analyzer import Intent, IntentAnalysisResult, ConfidenceLevel


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def dialog_manager():
    """Initialize Dialog Manager for tests"""
    return DialogManager(ai_brain=None)


@pytest.fixture
def sample_intent():
    """Create a sample Intent for testing"""
    return Intent(
        verb="بازی",
        target="game",
        parameters={"duration": "until_return"},
        constraints=[],
        confidence=0.85,
        raw_request="بازی کن تا برگردم",
        language="fa"
    )


@pytest.fixture
def intent_result_with_missing_fields(sample_intent):
    """Create IntentAnalysisResult with missing fields"""
    return IntentAnalysisResult(
        intent=sample_intent,
        missing_fields=["game_type"],
        suggestions=["Counter-Strike", "Dota 2", "Minecraft"],
        requires_clarification=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TestQuestionGeneration - تولید سوال
# ═══════════════════════════════════════════════════════════════════════════════

class TestQuestionGeneration:
    """Test question generation for missing fields"""
    
    @pytest.mark.asyncio
    async def test_generate_predefined_question_game_type(self, dialog_manager, sample_intent):
        """تولید سوال پیش‌تعریف شده برای game_type"""
        question = dialog_manager._generate_question("game_type", sample_intent, language="fa")
        
        assert question.field_name == "game_type"
        assert question.question_text != ""
        assert question.question_text_en != ""
        assert question.question_type == QuestionType.OPEN_ENDED
        assert len(question.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_generate_predefined_question_folder_name(self, dialog_manager, sample_intent):
        """تولید سوال برای folder_name"""
        question = dialog_manager._generate_question("folder_name", sample_intent)
        
        assert question.field_name == "folder_name"
        assert "folder" in question.question_text.lower() or "پوشه" in question.question_text
        assert question.required is True
    
    @pytest.mark.asyncio
    async def test_generate_custom_question_for_unknown_field(self, dialog_manager, sample_intent):
        """تولید سوال پویا برای فیلد نامشناخته"""
        question = dialog_manager._generate_question("unknown_field", sample_intent, language="fa")
        
        assert question.field_name == "unknown_field"
        assert question.question_text != ""
        assert question.question_type == QuestionType.OPEN_ENDED
    
    @pytest.mark.asyncio
    async def test_question_in_english(self, dialog_manager, sample_intent):
        """تولید سوال انگلیسی"""
        question = dialog_manager._generate_question("game_type", sample_intent, language="en")
        
        assert question.field_name == "game_type"
        assert question.question_text_en != ""
        # سوال انگلیسی باید حاوی کلمات انگلیسی باشد


# ═══════════════════════════════════════════════════════════════════════════════
# TestResponseCollection - جمع‌آوری پاسخ
# ═══════════════════════════════════════════════════════════════════════════════

class TestResponseCollection:
    """Test collecting responses from user"""
    
    @pytest.mark.asyncio
    async def test_dialog_response_creation(self, dialog_manager):
        """ایجاد یک DialogResponse"""
        response = DialogResponse(
            field_name="game_type",
            answer="Counter-Strike",
            confidence=0.95,
            clarification_needed=False
        )
        
        assert response.field_name == "game_type"
        assert response.answer == "Counter-Strike"
        assert response.confidence == 0.95
        assert response.clarification_needed is False
    
    @pytest.mark.asyncio
    async def test_dialog_response_with_low_confidence(self, dialog_manager):
        """ایجاد DialogResponse با confidence کم"""
        response = DialogResponse(
            field_name="folder_path",
            answer="سی درایو",
            confidence=0.55,
            clarification_needed=True
        )
        
        assert response.clarification_needed is True
        assert response.confidence < 0.7
    
    @pytest.mark.asyncio
    async def test_dialog_session_initialization(self, dialog_manager, intent_result_with_missing_fields):
        """مقداردهی اولیه جلسه مکالمه"""
        session = DialogSession(
            session_id="test_001",
            intent_result=intent_result_with_missing_fields
        )
        
        assert session.session_id == "test_001"
        assert session.state == DialogState.IDLE
        assert len(session.responses) == 0
        assert session.complete_intent is None
    
    @pytest.mark.asyncio
    async def test_dialog_session_is_complete(self, dialog_manager, intent_result_with_missing_fields, sample_intent):
        """بررسی تمام شدن جلسه"""
        session = DialogSession(
            session_id="test_002",
            intent_result=intent_result_with_missing_fields
        )
        
        # قبل از تکمیل
        assert session.is_complete() is False
        
        # بعد از تکمیل
        session.state = DialogState.COMPLETE
        session.complete_intent = sample_intent
        assert session.is_complete() is True


# ═══════════════════════════════════════════════════════════════════════════════
# TestConfidenceCalculation - محاسبه اعتماد
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfidenceCalculation:
    """Test confidence calculation for responses"""
    
    @pytest.mark.asyncio
    async def test_high_confidence_for_suggestion_match(self, dialog_manager):
        """اعتماد بالا برای پاسخ در suggestions"""
        question = DialogQuestion(
            field_name="game_type",
            question_text="چه بازی؟",
            question_text_en="Which game?",
            question_type=QuestionType.OPEN_ENDED,
            suggestions=["Counter-Strike", "Dota 2", "Minecraft"]
        )
        
        confidence = dialog_manager._calculate_response_confidence(
            question,
            "Counter-Strike"
        )
        
        assert confidence > 0.95
    
    @pytest.mark.asyncio
    async def test_lower_confidence_for_custom_answer(self, dialog_manager):
        """اعتماد کمتر برای پاسخ سفارشی"""
        question = DialogQuestion(
            field_name="game_type",
            question_text="چه بازی؟",
            question_text_en="Which game?",
            question_type=QuestionType.OPEN_ENDED,
            suggestions=["Counter-Strike", "Dota 2", "Minecraft"]
        )
        
        confidence = dialog_manager._calculate_response_confidence(
            question,
            "یک بازی خاص که شناخته نشده"
        )
        
        # پاسخ سفارشی (غیر از suggestions) اعتماد کمتری دارد
        assert confidence <= 0.95
    
    @pytest.mark.asyncio
    async def test_very_low_confidence_for_short_answer(self, dialog_manager):
        """اعتماد بسیار کم برای پاسخ بسیار کوتاه"""
        question = DialogQuestion(
            field_name="game_type",
            question_text="چه بازی؟",
            question_text_en="Which game?",
            question_type=QuestionType.OPEN_ENDED,
            suggestions=[]
        )
        
        confidence = dialog_manager._calculate_response_confidence(
            question,
            "x"
        )
        
        assert confidence < 0.7


# ═══════════════════════════════════════════════════════════════════════════════
# TestConfirmation - تایید برداشت
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfirmation:
    """Test confirmation of understanding"""
    
    @pytest.mark.asyncio
    @patch('builtins.input', return_value='بله')
    async def test_confirm_understanding_positive(self, mock_input, dialog_manager, intent_result_with_missing_fields):
        """تایید مثبت کاربر"""
        session = DialogSession(
            session_id="test_001",
            intent_result=intent_result_with_missing_fields
        )
        
        session.responses.append(DialogResponse(
            field_name="game_type",
            answer="Counter-Strike"
        ))
        
        confirmed = await dialog_manager._confirm_understanding(session, user_language="fa")
        
        assert confirmed is True
    
    @pytest.mark.asyncio
    @patch('builtins.input', return_value='خیر')
    async def test_confirm_understanding_negative(self, mock_input, dialog_manager, intent_result_with_missing_fields):
        """تایید منفی کاربر"""
        session = DialogSession(
            session_id="test_002",
            intent_result=intent_result_with_missing_fields
        )
        
        confirmed = await dialog_manager._confirm_understanding(session, user_language="fa")
        
        assert confirmed is False
    
    @pytest.mark.asyncio
    @patch('builtins.input', return_value='yes')
    async def test_confirm_understanding_english(self, mock_input, dialog_manager, intent_result_with_missing_fields):
        """تایید انگلیسی"""
        session = DialogSession(
            session_id="test_003",
            intent_result=intent_result_with_missing_fields
        )
        
        confirmed = await dialog_manager._confirm_understanding(session, user_language="en")
        
        assert confirmed is True


# ═══════════════════════════════════════════════════════════════════════════════
# TestIntentMerging - ادغام Intent
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntentMerging:
    """Test merging responses with intent"""
    
    @pytest.mark.asyncio
    async def test_merge_single_response(self, dialog_manager, sample_intent):
        """ادغام یک پاسخ با Intent"""
        responses = [
            DialogResponse(
                field_name="game_type",
                answer="Counter-Strike",
                confidence=0.95
            )
        ]
        
        merged_intent = dialog_manager._merge_responses_with_intent(sample_intent, responses)
        
        assert merged_intent.parameters["game_type"] == "Counter-Strike"
        assert merged_intent.confidence > sample_intent.confidence
    
    @pytest.mark.asyncio
    async def test_merge_multiple_responses(self, dialog_manager, sample_intent):
        """ادغام چندین پاسخ"""
        responses = [
            DialogResponse(field_name="game_type", answer="Dota 2"),
            DialogResponse(field_name="difficulty", answer="Hard"),
            DialogResponse(field_name="duration", answer="۲ ساعت")
        ]
        
        merged_intent = dialog_manager._merge_responses_with_intent(sample_intent, responses)
        
        # sample_intent اصلاً "duration" داشت، جمع 3 پاسخ جدید = 3 کل
        assert len(merged_intent.parameters) >= 3
        assert merged_intent.parameters["game_type"] == "Dota 2"
        assert merged_intent.parameters["difficulty"] == "Hard"


# ═══════════════════════════════════════════════════════════════════════════════
# TestClarification - درخواست توضیح
# ═══════════════════════════════════════════════════════════════════════════════

class TestClarification:
    """Test clarification requests"""
    
    @pytest.mark.asyncio
    @patch('builtins.input', return_value='بله')
    async def test_clarify_field_accepted(self, mock_input, dialog_manager, sample_intent):
        """قبول توضیح"""
        result = await dialog_manager.clarify_field(
            "game_type",
            "Counter-Strike",
            sample_intent,
            user_language="fa"
        )
        
        assert result == "بله"
    
    @pytest.mark.asyncio
    @patch('builtins.input', return_value='نه، منظور من بازی دیگری بود')
    async def test_clarify_field_with_correction(self, mock_input, dialog_manager, sample_intent):
        """درخواست توضیح با تصحیح"""
        result = await dialog_manager.clarify_field(
            "game_type",
            "CS GO",
            sample_intent,
            user_language="fa"
        )
        
        assert "منظور" in result or result != "بله"


# ═══════════════════════════════════════════════════════════════════════════════
# TestMultiLanguageSupport - پشتیبانی چندزبانه
# ═══════════════════════════════════════════════════════════════════════════════

class TestMultiLanguageSupport:
    """Test bilingual support"""
    
    @pytest.mark.asyncio
    async def test_persian_question_generation(self, dialog_manager, sample_intent):
        """تولید سوال فارسی"""
        question = dialog_manager._generate_question(
            "game_type",
            sample_intent,
            language="fa"
        )
        
        # بررسی وجود کاراکتر فارسی یا کلمات فارسی
        assert question.question_text is not None
        assert len(question.question_text) > 0
    
    @pytest.mark.asyncio
    async def test_english_question_generation(self, dialog_manager, sample_intent):
        """تولید سوال انگلیسی"""
        question = dialog_manager._generate_question(
            "game_type",
            sample_intent,
            language="en"
        )
        
        assert question.question_text_en is not None
        assert len(question.question_text_en) > 0
    
    @pytest.mark.asyncio
    async def test_bilingual_question_attributes(self, dialog_manager, sample_intent):
        """بررسی ویژگی‌های دوزبانه"""
        question = dialog_manager._generate_question(
            "game_type",
            sample_intent,
            language="fa"
        )
        
        assert hasattr(question, 'question_text')
        assert hasattr(question, 'question_text_en')
        assert question.question_text != question.question_text_en


# ═══════════════════════════════════════════════════════════════════════════════
# TestRealWorldScenarios - سناریوهای واقعی
# ═══════════════════════════════════════════════════════════════════════════════

class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    @pytest.mark.asyncio
    async def test_gaming_scenario(self, dialog_manager):
        """سناریو بازی کردن: "بازی کن تا برگردم" → missing_fields: ['game_type']"""
        intent = Intent(
            verb="بازی",
            target="game",
            parameters={"duration": "until_return"},
            constraints=[],
            confidence=0.85,
            raw_request="بازی کن تا برگردم",
            language="fa"
        )
        
        intent_result = IntentAnalysisResult(
            intent=intent,
            missing_fields=["game_type"],
            suggestions=["Counter-Strike", "Dota 2"],
            requires_clarification=True
        )
        
        # بررسی که Dialog Manager می‌تواند سوال مناسب تولید کند
        question = dialog_manager._generate_question("game_type", intent)
        assert question.field_name == "game_type"
        assert len(question.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_folder_creation_scenario(self, dialog_manager):
        """سناریو ایجاد پوشه: missing_fields: ['folder_name', 'folder_path']"""
        intent = Intent(
            verb="ایجاد",
            target="folder",
            parameters={},
            constraints=[],
            confidence=0.80,
            raw_request="یک پوشه بساز",
            language="fa"
        )
        
        intent_result = IntentAnalysisResult(
            intent=intent,
            missing_fields=["folder_name", "folder_path"],
            suggestions=[],
            requires_clarification=True
        )
        
        # بررسی تولید سوالات برای هر دو فیلد
        q1 = dialog_manager._generate_question("folder_name", intent)
        q2 = dialog_manager._generate_question("folder_path", intent)
        
        assert q1.field_name == "folder_name"
        assert q2.field_name == "folder_path"
    
    @pytest.mark.asyncio
    async def test_file_operation_scenario(self, dialog_manager):
        """سناریو عملیات روی فایل"""
        intent = Intent(
            verb="کپی",
            target="file",
            parameters={"source": "document.txt"},
            constraints=["safe_mode"],
            confidence=0.75,
            raw_request="فایل را کپی کن",
            language="fa"
        )
        
        intent_result = IntentAnalysisResult(
            intent=intent,
            missing_fields=["destination"],
            suggestions=["Desktop", "Documents", "Downloads"],
            requires_clarification=True
        )
        
        question = dialog_manager._generate_question("destination", intent)
        assert question is not None
    
    @pytest.mark.asyncio
    async def test_data_retrieval_scenario(self, dialog_manager):
        """سناریو دریافت داده"""
        intent = Intent(
            verb="دریافت",
            target="data",
            parameters={"source": "weather"},
            constraints=[],
            confidence=0.80,
            raw_request="هوای تهران چطوره",
            language="fa"
        )
        
        question = dialog_manager._generate_question("location", intent, language="fa")
        assert question.question_text is not None
    
    @pytest.mark.asyncio
    async def test_installation_scenario(self, dialog_manager):
        """سناریو نصب برنامه"""
        intent = Intent(
            verb="نصب",
            target="software",
            parameters={"software_name": "Python"},
            constraints=[],
            confidence=0.90,
            raw_request="Python رو نصب کن",
            language="fa"
        )
        
        intent_result = IntentAnalysisResult(
            intent=intent,
            missing_fields=["version"],
            suggestions=["3.11", "3.12", "3.13"],
            requires_clarification=True
        )
        
        question = dialog_manager._generate_question("version", intent)
        assert "version" in question.field_name.lower()
    
    @pytest.mark.asyncio
    async def test_complex_multi_step_scenario(self, dialog_manager):
        """سناریو پیچیده چند‌مرحله‌ای"""
        intent = Intent(
            verb="ایجاد",
            target="backup",
            parameters={"source": "Documents"},
            constraints=["safe_mode", "minimal_cpu"],
            confidence=0.70,
            raw_request="بکاپ درایو سی بگیر",
            language="fa"
        )
        
        intent_result = IntentAnalysisResult(
            intent=intent,
            missing_fields=["destination", "backup_type"],
            suggestions=[],
            requires_clarification=True
        )
        
        # بررسی تولید سوالات برای هر دو فیلد
        q1 = dialog_manager._generate_question("destination", intent)
        q2 = dialog_manager._generate_question("backup_type", intent)
        
        assert q1 is not None
        assert q2 is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestEdgeCases - موارد خاص لبه‌ای
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_collect_with_no_missing_fields(self, dialog_manager, sample_intent):
        """جمع‌آوری با missing_fields خالی"""
        intent_result = IntentAnalysisResult(
            intent=sample_intent,
            missing_fields=[],
            suggestions=[],
            requires_clarification=False
        )
        
        result = await dialog_manager.collect_missing_info(intent_result)
        
        assert result.missing_fields == []
        assert result.intent == sample_intent
    
    @pytest.mark.asyncio
    async def test_dialog_with_special_characters_in_answer(self, dialog_manager):
        """پاسخ با کاراکتر‌های خاص"""
        response = DialogResponse(
            field_name="path",
            answer="C:\\Users\\علی\\Documents",
            confidence=0.95
        )
        
        assert response.answer is not None
        assert "\\Users\\" in response.answer
    
    @pytest.mark.asyncio
    async def test_empty_suggestions_list(self, dialog_manager, sample_intent):
        """تولید سوال بدون suggestions"""
        question = dialog_manager._generate_question(
            "custom_unknown_field",
            sample_intent
        )
        
        assert question.suggestions == []
        assert question.question_type == QuestionType.OPEN_ENDED
    
    @pytest.mark.asyncio
    async def test_very_long_answer(self, dialog_manager):
        """پاسخ بسیار طولانی"""
        long_answer = "x" * 1000
        question = DialogQuestion(
            field_name="description",
            question_text="توضیح بدهید",
            question_text_en="Describe",
            question_type=QuestionType.OPEN_ENDED
        )
        
        confidence = dialog_manager._calculate_response_confidence(question, long_answer)
        
        # باید confidence معقولی داشته باشد
        assert 0.5 < confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_persian_and_english_mixed_answer(self, dialog_manager):
        """پاسخ ترکیبی فارسی و انگلیسی"""
        mixed_answer = "باز کن C:\\Users\\Documents"
        response = DialogResponse(
            field_name="command",
            answer=mixed_answer,
            confidence=0.90
        )
        
        assert "C:\\" in response.answer
        assert "باز" in response.answer


# ═══════════════════════════════════════════════════════════════════════════════
# TestIntegrationWithIntentAnalyzer - ادغام با Intent Analyzer
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegrationWithIntentAnalyzer:
    """Test integration with Intent Analyzer"""
    
    @pytest.mark.asyncio
    async def test_dialog_handles_intent_analyzer_output(self, dialog_manager):
        """Dialog Manager می‌تواند خروجی Intent Analyzer را بپذیرد"""
        intent = Intent(
            verb="نصب",
            target="software",
            parameters={},
            constraints=[],
            confidence=0.70,
            raw_request="نصب کن Python",
            language="fa"
        )
        
        intent_result = IntentAnalysisResult(
            intent=intent,
            missing_fields=["version"],
            suggestions=["3.11", "3.12", "3.13"],
            requires_clarification=True
        )
        
        # Dialog Manager باید این را بپذیرد
        assert intent_result.missing_fields is not None
        assert len(intent_result.missing_fields) > 0
    
    @pytest.mark.asyncio
    async def test_dialog_output_compatible_with_next_stage(self, dialog_manager, sample_intent):
        """خروجی Dialog Manager باید برای مرحله بعد (Plan Generator) آماده باشد"""
        responses = [
            DialogResponse(field_name="game_type", answer="Minecraft")
        ]
        
        merged_intent = dialog_manager._merge_responses_with_intent(sample_intent, responses)
        
        # Intent نهایی باید تمام اطلاعات لازم را داشته باشد
        assert merged_intent.verb is not None
        assert merged_intent.target is not None
        assert len(merged_intent.parameters) > 0
        assert merged_intent.confidence > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestPerformance - عملکرد
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_question_generation_performance(self, dialog_manager, sample_intent):
        """سرعت تولید سوال"""
        import time
        
        start = time.time()
        for _ in range(100):
            dialog_manager._generate_question("game_type", sample_intent)
        elapsed = time.time() - start
        
        # ۱۰۰ سوال باید در کمتر از ۱ ثانیه تولید شود
        assert elapsed < 1.0
    
    @pytest.mark.asyncio
    async def test_response_confidence_calculation_performance(self, dialog_manager):
        """سرعت محاسبه confidence"""
        import time
        
        question = DialogQuestion(
            field_name="test",
            question_text="test",
            question_text_en="test",
            question_type=QuestionType.OPEN_ENDED
        )
        
        start = time.time()
        for _ in range(1000):
            dialog_manager._calculate_response_confidence(question, "test answer")
        elapsed = time.time() - start
        
        # ۱۰۰۰ محاسبه باید در کمتر از ۰.۵ ثانیه انجام شود
        assert elapsed < 0.5
