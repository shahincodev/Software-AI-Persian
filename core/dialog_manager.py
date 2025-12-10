# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Dialog Manager - مدیر گفت‌و‌گوی دوطرفه

Dialog Manager پاسخ‌گوی جمع‌آوری اطلاعات گمشده است. زمانی که Intent Analyzer
از کاربر نمی‌تواند اطلاعات کاملی استخراج کند، Dialog Manager با مکالمه و پرسش‌های
هوشمند این اطلاعات ناگزیر را جمع‌آوری می‌کند.

مثال:
    >>> intent_result = analyzer.analyze("بازی کن تا برگردم")
    >>> # missing_fields = ["game_type"]
    >>> 
    >>> dialog = DialogManager()
    >>> complete_intent = await dialog.collect_missing_info(intent_result)
    >>> # Dialog: "چه بازی رو دوست دارید؟"
    >>> # User: "Counter-Strike"
    >>> # Result: Intent with game_type filled

Core Responsibilities:
    1. سوال‌گذاری هوشمند (Smart Questioning)
    2. تایید برداشت (Confirmation)
    3. اصلاح اطلاعات (Clarification)
    4. پیشنهادهای هوشمند (Smart Suggestions)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from core.intent_analyzer import Intent, IntentAnalysisResult
from core.ai_brain import AIBrain

# ═══════════════════════════════════════════════════════════════════════════════

logger = logging.getLogger(__name__)


class DialogState(Enum):
    """وضعیت‌های مختلف مکالمه
    
    IDLE: آماده شروع مکالمه
    QUESTIONING: در حال پرسش
    CONFIRMING: در حال تایید
    COMPLETE: مکالمه تمام شده
    ERROR: خطا در مکالمه
    """
    IDLE = "idle"
    QUESTIONING = "questioning"
    CONFIRMING = "confirming"
    CLARIFYING = "clarifying"
    COMPLETE = "complete"
    ERROR = "error"


class QuestionType(Enum):
    """انواع سوالات
    
    OPEN_ENDED: سوالات باز (چه بازی؟)
    MULTIPLE_CHOICE: انتخاب از گزینه‌ها
    YES_NO: بله/خیر
    CONFIRMATION: تایید برداشت
    CLARIFICATION: درخواست توضیح
    """
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    CONFIRMATION = "confirmation"
    CLARIFICATION = "clarification"


@dataclass
class DialogQuestion:
    """یک سوال در مکالمه
    
    Attributes:
        field_name: نام فیلد مورد نیاز (game_type, name, path)
        question_text: متن سوال فارسی
        question_text_en: متن سوال انگلیسی
        question_type: نوع سوال
        suggestions: پیشنهادهای هوشمند (برای multiple_choice)
        required: آیا پاسخ اجباری است
        retries_allowed: تعداد تلاش‌های مجدد
    """
    field_name: str
    question_text: str
    question_text_en: str
    question_type: QuestionType
    suggestions: List[str] = field(default_factory=list)
    required: bool = True
    retries_allowed: int = 3
    
    def __str__(self) -> str:
        """نمایش سوال برای کاربر"""
        return self.question_text


@dataclass
class DialogResponse:
    """پاسخ کاربر به سوال
    
    Attributes:
        field_name: نام فیلد
        answer: پاسخ کاربر
        confidence: اعتماد به پاسخ (0.0-1.0)
        clarification_needed: آیا توضیح بیشتری لازم است
    """
    field_name: str
    answer: str
    confidence: float = 0.95
    clarification_needed: bool = False


@dataclass
class DialogSession:
    """یک جلسه مکالمه کامل
    
    Attributes:
        session_id: شناسه یکتای جلسه
        intent_result: نتیجه اولیه Intent Analyzer
        questions_asked: لیست سوالات پرسیده شده
        responses: لیست پاسخ‌های کاربر
        state: وضعیت کنونی مکالمه
        complete_intent: Intent نهایی (پس از مکالمه)
    """
    session_id: str
    intent_result: IntentAnalysisResult
    questions_asked: List[DialogQuestion] = field(default_factory=list)
    responses: List[DialogResponse] = field(default_factory=list)
    state: DialogState = DialogState.IDLE
    complete_intent: Optional[Intent] = None
    
    def is_complete(self) -> bool:
        """بررسی تمام شدن مکالمه"""
        return (
            self.state == DialogState.COMPLETE and
            self.complete_intent is not None
        )


# ═══════════════════════════════════════════════════════════════════════════════


class DialogManager:
    """مدیر گفت‌و‌گو برای جمع‌آوری اطلاعات گمشده
    
    Dialog Manager با مکالمه هوشمند و سوال‌های موثر، اطلاعات ناگزیر برای
    تکمیل Intent را جمع‌آوری می‌کند.
    
    مثال:
        >>> dialog = DialogManager(ai_brain=brain)
        >>> result = await dialog.collect_missing_info(intent_result)
    """
    
    # سوالات پیش‌تعریف شده برای فیلدهای مختلف
    PREDEFINED_QUESTIONS = {
        "game_type": {
            "fa": "چه نوع بازی‌ای دوست دارید؟ (اکشن، مسابقه، RPG یا نام خاصی)",
            "en": "What type of game do you prefer? (Action, Racing, RPG, or specific name)",
            "suggestions": ["Counter-Strike", "Dota 2", "Minecraft", "FIFA", "Elden Ring"],
            "type": QuestionType.OPEN_ENDED
        },
        "folder_name": {
            "fa": "نام پوشه را چه بگذارید؟",
            "en": "What should be the folder name?",
            "suggestions": ["Documents", "MyProject", "Downloads", "Backup"],
            "type": QuestionType.OPEN_ENDED
        },
        "folder_path": {
            "fa": "این پوشه را در کجا بسازید؟ (مثال: E:\\, C:\\Users\\YourName)",
            "en": "Where should this folder be created? (e.g., E:\\, C:\\Users\\YourName)",
            "suggestions": ["C:\\", "D:\\", "E:\\", "C:\\Users"],
            "type": QuestionType.OPEN_ENDED
        },
        "file_name": {
            "fa": "نام فایل را چه بگذارید؟",
            "en": "What should be the file name?",
            "suggestions": ["MyFile", "Document1", "Report", "Backup"],
            "type": QuestionType.OPEN_ENDED
        },
        "duration": {
            "fa": "این کار را برای چند وقت انجام بدهم؟ (مثال: ۱۰ دقیقه، تا برگشتی)",
            "en": "For how long should this run? (e.g., 10 minutes, until you return)",
            "suggestions": ["۵ دقیقه", "۱۵ دقیقه", "تا برگشتم", "۱ ساعت"],
            "type": QuestionType.OPEN_ENDED
        },
        "browser_tab": {
            "fa": "در کدام مرورگر باز کنم؟",
            "en": "Which browser should I use?",
            "suggestions": ["Chrome", "Firefox", "Edge", "Safari"],
            "type": QuestionType.MULTIPLE_CHOICE
        }
    }
    
    def __init__(self, ai_brain: Optional[AIBrain] = None):
        """مقداردهی اولیه Dialog Manager
        
        Args:
            ai_brain: نمونه AIBrain برای پردازش هوشمند سوالات
        """
        self.ai_brain = ai_brain
        self.logger = logging.getLogger(self.__class__.__name__)
        self._session_counter = 0
        
        self.logger.info("Dialog Manager initialized ✓")
    
    async def collect_missing_info(
        self,
        intent_result: IntentAnalysisResult,
        user_language: str = "fa",
        max_clarifications: int = 3
    ) -> IntentAnalysisResult:
        """جمع‌آوری اطلاعات گمشده از طریق مکالمه
        
        این متد بخش اصلی Dialog Manager است. تمام فرایند مکالمه را
        مدیریت می‌کند و Intent کامل شده‌ای را برمی‌گرداند.
        
        Args:
            intent_result: نتیجه Intent Analyzer
            user_language: زبان کاربر (fa یا en)
            max_clarifications: حداکثر درخواست‌های توضیح
        
        Returns:
            IntentAnalysisResult تکمیل شده با missing_fields پر شده
            
        مثال:
            >>> result = await dialog.collect_missing_info(
            ...     intent_result,
            ...     user_language="fa"
            ... )
        """
        self._session_counter += 1
        session_id = f"dialog_{self._session_counter}"
        
        session = DialogSession(
            session_id=session_id,
            intent_result=intent_result
        )
        
        self.logger.info(f"Starting dialog session {session_id}")
        self.logger.info(f"Missing fields: {intent_result.missing_fields}")
        
        # اگر هیچ فیلد گمشده‌ای نیست، برگرد
        if not intent_result.missing_fields:
            self.logger.info("No missing fields - returning original intent")
            return intent_result
        
        try:
            session.state = DialogState.QUESTIONING
            
            # جمع‌آوری پاسخ برای هر فیلد گمشده
            for field_name in intent_result.missing_fields:
                self.logger.info(f"Asking for field: {field_name}")
                
                question = self._generate_question(
                    field_name,
                    intent_result.intent,
                    user_language
                )
                
                response = await self._ask_user(
                    question,
                    session,
                    max_retries=3,
                    user_language=user_language
                )
                
                if response:
                    session.responses.append(response)
                    self.logger.info(f"Received response: {response.answer}")
            
            # تایید فهم
            session.state = DialogState.CONFIRMING
            confirmed = await self._confirm_understanding(
                session,
                user_language
            )
            
            if not confirmed:
                self.logger.warning("Understanding not confirmed - retrying")
                # اگر تایید نشد، دوباره سوال بپرس
                return await self.collect_missing_info(
                    intent_result,
                    user_language,
                    max_clarifications - 1
                )
            
            # ساخت Intent کامل شده
            session.state = DialogState.COMPLETE
            complete_intent = self._merge_responses_with_intent(
                intent_result.intent,
                session.responses
            )
            
            session.complete_intent = complete_intent
            
            # ساخت نتیجه نهایی
            final_result = IntentAnalysisResult(
                intent=complete_intent,
                missing_fields=[],
                suggestions=intent_result.suggestions,
                requires_clarification=False
            )
            
            self.logger.info(f"Dialog session {session_id} complete ✓")
            return final_result
            
        except Exception as e:
            session.state = DialogState.ERROR
            self.logger.error(f"Dialog error: {str(e)}")
            # در صورت خطا، Intent اصلی را برگردان
            return intent_result
    
    def _generate_question(
        self,
        field_name: str,
        intent: Intent,
        language: str = "fa"
    ) -> DialogQuestion:
        """تولید سوال برای یک فیلد گمشده
        
        سوالات را بر اساس context و Intent تولید می‌کند.
        """
        lang_key = "fa" if language == "fa" else "en"
        
        # اگر سوال پیش‌تعریف شده‌ای وجود دارد
        if field_name in self.PREDEFINED_QUESTIONS:
            pred = self.PREDEFINED_QUESTIONS[field_name]
            return DialogQuestion(
                field_name=field_name,
                question_text=pred["fa"],
                question_text_en=pred["en"],
                question_type=pred.get("type", QuestionType.OPEN_ENDED),
                suggestions=pred.get("suggestions", []),
                required=True
            )
        
        # سوال‌های پویا برای فیلدهای نامشخص
        question_templates = {
            "fa": f"برای '{field_name}' چه مقداری مورد نیاز است؟",
            "en": f"What value would you like for '{field_name}'?"
        }
        
        return DialogQuestion(
            field_name=field_name,
            question_text=question_templates["fa"],
            question_text_en=question_templates["en"],
            question_type=QuestionType.OPEN_ENDED,
            suggestions=[],
            required=True
        )
    
    async def _ask_user(
        self,
        question: DialogQuestion,
        session: DialogSession,
        max_retries: int = 3,
        user_language: str = "fa"
    ) -> Optional[DialogResponse]:
        """پرسش از کاربر با تلاش مجدد در صورت عدم موفقیت
        
        Args:
            question: سوال مورد نظر
            session: جلسه مکالمه
            max_retries: حداکثر تلاش
            user_language: زبان کاربر
        
        Returns:
            DialogResponse یا None اگر نتوانست جواب بگیرد
        """
        session.questions_asked.append(question)
        
        # تعیین متن سوال بر اساس زبان
        question_text = (
            question.question_text if user_language == "fa"
            else question.question_text_en
        )
        
        # اگر suggestions وجود دارد، نمایش آن‌ها
        suggestions_text = ""
        if question.suggestions:
            suggestions_text = (
                f"\n💡 پیشنهادات: {', '.join(question.suggestions)}"
                if user_language == "fa"
                else f"\n💡 Suggestions: {', '.join(question.suggestions)}"
            )
        
        self.logger.info(f"Asking: {question_text}")
        
        for attempt in range(max_retries):
            try:
                # نمایش سوال برای کاربر
                print(f"\n❓ {question_text}{suggestions_text}")
                
                # دریافت پاسخ (شبیه‌سازی)
                user_answer = await self._get_user_input(
                    timeout=30,
                    user_language=user_language
                )
                
                if not user_answer or user_answer.strip() == "":
                    if attempt < max_retries - 1:
                        error_msg = (
                            "❌ لطفاً یک پاسخ معتبر وارد کنید"
                            if user_language == "fa"
                            else "❌ Please provide a valid answer"
                        )
                        print(error_msg)
                        continue
                    else:
                        return None
                
                # تقدیر اعتماد
                confidence = self._calculate_response_confidence(
                    question,
                    user_answer
                )
                
                response = DialogResponse(
                    field_name=question.field_name,
                    answer=user_answer,
                    confidence=confidence,
                    clarification_needed=(confidence < 0.7)
                )
                
                self.logger.info(
                    f"Response received: {user_answer} "
                    f"(confidence: {confidence:.2f})"
                )
                
                return response
                
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    timeout_msg = (
                        f"⏱️ زمان پاسخ تمام شد. دوباره سعی کنید ({attempt + 1}/{max_retries})"
                        if user_language == "fa"
                        else f"⏱️ Timeout. Try again ({attempt + 1}/{max_retries})"
                    )
                    print(timeout_msg)
                else:
                    return None
        
        return None
    
    async def _get_user_input(
        self,
        timeout: int = 30,
        user_language: str = "fa"
    ) -> str:
        """دریافت input از کاربر با timeout
        
        در تست‌ها، این متد شبیه‌سازی می‌شود.
        در عملکرد واقعی، از input() استفاده می‌شود.
        
        Args:
            timeout: زمان انتظار به ثانیه
            user_language: زبان کاربر
        
        Returns:
            پاسخ کاربر
        """
        try:
            # شبیه‌سازی برای تست
            prompt = "👤 شما: " if user_language == "fa" else "👤 You: "
            user_input = input(prompt)
            return user_input
        except (EOFError, KeyboardInterrupt):
            return ""
    
    async def _confirm_understanding(
        self,
        session: DialogSession,
        user_language: str = "fa"
    ) -> bool:
        """تایید درک صحیح از کاربر
        
        برای اطمینان از صحت فهم، یک تایید نهایی می‌خواهیم.
        
        Args:
            session: جلسه مکالمه
            user_language: زبان کاربر
        
        Returns:
            True اگر کاربر تایید کرد، False اگر خیر
        """
        # ساخت خلاصه
        summary_items = []
        for response in session.responses:
            summary_items.append(f"  • {response.field_name}: {response.answer}")
        
        if user_language == "fa":
            summary = "خلاصه پاسخ‌های شما:\n" + "\n".join(summary_items)
            confirm_msg = "\nآیا این پاسخ‌ها صحیح هستند؟ (بله/خیر)"
        else:
            summary = "Summary of your answers:\n" + "\n".join(summary_items)
            confirm_msg = "\nAre these answers correct? (yes/no)"
        
        print(f"\n📋 {summary}{confirm_msg}")
        
        try:
            confirmation = input("👤 شما: " if user_language == "fa" else "👤 You: ")
            confirmed = confirmation.lower() in (
                ["بله", "بخش", "آره", "yes", "y", "ok"] 
                if user_language == "fa"
                else ["yes", "y", "ok", "بله", "بخش", "آره"]
            )
            
            self.logger.info(f"User confirmation: {confirmed}")
            return confirmed
            
        except Exception as e:
            self.logger.warning(f"Confirmation error: {str(e)}")
            return False
    
    def _calculate_response_confidence(
        self,
        question: DialogQuestion,
        answer: str
    ) -> float:
        """محاسبه اعتماد به پاسخ کاربر
        
        بر اساس ماهیت سوال و پاسخ، اعتماد محاسبه می‌شود.
        """
        base_confidence = 0.95
        
        # کاهش اعتماد برای پاسخ‌های کوتاه
        if len(answer.strip()) < 2:
            base_confidence -= 0.3
        
        # اگر پاسخ در suggestions باشد، اعتماد بالاتر
        if question.suggestions and answer in question.suggestions:
            base_confidence = 0.98
        
        return min(base_confidence, 1.0)
    
    def _merge_responses_with_intent(
        self,
        intent: Intent,
        responses: List[DialogResponse]
    ) -> Intent:
        """ادغام پاسخ‌های کاربر با Intent اصلی
        
        Args:
            intent: Intent اصلی
            responses: لیست پاسخ‌های کاربر
        
        Returns:
            Intent تکمیل شده
        """
        # کپی Intent
        updated_intent = Intent(
            verb=intent.verb,
            target=intent.target,
            parameters=intent.parameters.copy(),
            constraints=intent.constraints.copy(),
            confidence=intent.confidence,
            raw_request=intent.raw_request,
            language=intent.language
        )
        
        # اضافه کردن پاسخ‌ها به parameters
        for response in responses:
            updated_intent.parameters[response.field_name] = response.answer
        
        # بهبود confidence بر اساس تعداد اطلاعات
        additional_confidence = min(len(responses) * 0.05, 0.15)
        updated_intent.confidence = min(
            updated_intent.confidence + additional_confidence,
            1.0
        )
        
        self.logger.info(
            f"Intent merged with {len(responses)} responses. "
            f"New confidence: {updated_intent.confidence:.2f}"
        )
        
        return updated_intent
    
    async def clarify_field(
        self,
        field_name: str,
        current_value: str,
        intent: Intent,
        user_language: str = "fa"
    ) -> str:
        """درخواست توضیح برای یک فیلد خاص
        
        اگر یک فیلد ابهام‌آمیز باشد، این متد توضیح بیشتری می‌خواهد.
        
        Args:
            field_name: نام فیلد
            current_value: مقدار فعلی
            intent: Intent کنونی
            user_language: زبان کاربر
        
        Returns:
            مقدار تصحیح‌شده
        """
        if user_language == "fa":
            msg = f"برای '{field_name}' که '{current_value}' گفتید، آیا منظورتان این است؟ (پاسخ: بله/خیر/توضیح)"
        else:
            msg = f"For '{field_name}' with value '{current_value}', is this correct? (yes/no/explain)"
        
        print(f"\n❓ {msg}")
        
        try:
            response = input("👤 شما: " if user_language == "fa" else "👤 You: ")
            return response if response.strip() else current_value
        except Exception:
            return current_value
    
    async def get_suggestions(
        self,
        field_name: str,
        intent: Intent,
        user_language: str = "fa"
    ) -> List[str]:
        """دریافت پیشنهادهای هوشمند برای یک فیلد
        
        اگر AI Brain در دسترس باشد، پیشنهادهای هوشمند ارائه می‌دهد.
        
        Args:
            field_name: نام فیلد
            intent: Intent کنونی
            user_language: زبان کاربر
        
        Returns:
            لیست پیشنهادها
        """
        # پیشنهادهای پیش‌تعریف شده
        if field_name in self.PREDEFINED_QUESTIONS:
            return self.PREDEFINED_QUESTIONS[field_name]["suggestions"]
        
        # اگر AI Brain وجود دارد
        if self.ai_brain:
            try:
                prompt = (
                    f"برای فیلد '{field_name}' در context '{intent.target}'، "
                    f"۵ پیشنهاد بدهید. فقط لیست بدهید."
                    if user_language == "fa"
                    else f"For field '{field_name}' in context '{intent.target}', "
                    f"provide 5 suggestions. Just list them."
                )
                response = await self.ai_brain.ask(prompt)
                # تجزیه پاسخ و استخراج پیشنهادها
                suggestions = [s.strip() for s in response.split('\n') if s.strip()]
                return suggestions[:5]
            except Exception as e:
                self.logger.warning(f"Failed to get AI suggestions: {str(e)}")
        
        return []
