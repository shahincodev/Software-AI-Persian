# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Intent Analyzer - تشخیص هدف و نیت کاربر

این ماژول درخواست‌های کاربر را تحلیل می‌کند و intent (نیت/هدف)
مقصود کاربر را شناسایی می‌کند. این اولین مرحله در Intent Planning System است.

مثال:
    >>> analyzer = IntentAnalyzer()
    >>> intent = await analyzer.analyze("بازی کن تا برگردم")
    >>> print(intent.verb)  # "play"
    >>> print(intent.target)  # "game"
    >>> print(intent.parameters)  # {"duration": "until_return"}
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from core.ai_brain import AIBrain
from core.system_capabilities import SystemCapabilityRegistry

logger = logging.getLogger(__name__)


class DialogState(Enum):
    IDLE = "idle"
    QUESTIONING = "questioning"
    CONFIRMING = "confirming"
    CLARIFYING = "clarifying"
    COMPLETE = "complete"
    ERROR = "error"


class QuestionType(Enum):
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    CONFIRMATION = "confirmation"
    CLARIFICATION = "clarification"


@dataclass
class DialogQuestion:
    field_name: str
    question_text: str
    question_text_en: str
    question_type: QuestionType
    suggestions: List[str] = field(default_factory=list)
    required: bool = True
    retries_allowed: int = 3

    def __str__(self) -> str:
        return self.question_text


@dataclass
class DialogResponse:
    field_name: str
    answer: str
    confidence: float = 0.95
    clarification_needed: bool = False


@dataclass
class DialogSession:
    session_id: str
    intent_result: "IntentAnalysisResult"
    questions_asked: List[DialogQuestion] = field(default_factory=list)
    responses: List[DialogResponse] = field(default_factory=list)
    state: DialogState = DialogState.IDLE
    complete_intent: Optional["Intent"] = None

    def is_complete(self) -> bool:
        return (
            self.state == DialogState.COMPLETE and
            self.complete_intent is not None
        )


class ConfidenceLevel(Enum):
    """سطح اطمینان تشخیص Intent"""
    VERY_HIGH = 0.95  # خیلی بالا (95%+)
    HIGH = 0.85       # بالا (85-95%)
    MEDIUM = 0.70     # متوسط (70-85%)
    LOW = 0.50        # پایین (50-70%)
    VERY_LOW = 0.00   # خیلی پایین (<50%)


@dataclass
class Intent:
    """نمایش Intent (نیت/هدف) کاربر
    
    Attributes:
        verb: فعل اصلی (open, play, create, delete, etc.)
        target: هدف اصلی (notepad, game, folder, etc.)
        parameters: پارامترهای تفصیلی (Dict)
        constraints: محدودیت‌ها (safe_mode, minimal_cpu, etc.)
        confidence: اطمینان تشخیص (0.0 - 1.0)
        raw_request: درخواست اصلی کاربر
        language: زبان شناسایی شده (en, fa)
    """
    verb: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_request: str = ""
    language: str = "en"
    
    def is_confident(self, threshold: float = 0.70) -> bool:
        """بررسی اینکه آیا اطمینان به اندازه کافی بالاست
        
        Args:
            threshold: حداقل اطمینان مورد نیاز (پیش‌فرض: 0.70)
            
        Returns:
            True اگر confidence >= threshold
        """
        return self.confidence >= threshold
    
    def __str__(self) -> str:
        """نمایش انسانی Intent"""
        return (
            f"Intent(verb={self.verb}, target={self.target}, "
            f"confidence={self.confidence:.0%})"
        )


@dataclass
class IntentAnalysisResult:
    """نتیجه تحلیل Intent
    
    Attributes:
        intent: Intent تشخیص داده شده
        missing_fields: فیلدهای نامشخص و نیازمند سؤال
        suggestions: پیشنهادهای سیستم
        requires_clarification: آیا نیاز به سؤال از کاربر هست
    """
    intent: Intent
    missing_fields: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    requires_clarification: bool = False


class IntentAnalyzer:
    """تشخیص Intent از درخواست‌های طبیعی
    
    این کلاس درخواست‌های طبیعی را تحلیل می‌کند و:
    1. فعل اصلی (verb) را شناسایی می‌کند
    2. هدف (target) را تشخیص می‌دهد
    3. پارامترهای مربوطه را استخراج می‌کند
    4. موارد نامشخص را شناسایی می‌کند
    5. اطمینان تشخیص را محاسبه می‌کند
    
    Example:
        >>> analyzer = IntentAnalyzer()
        >>> result = await analyzer.analyze("بازی کن")
        >>> if result.intent.is_confident():
        ...     print(f"بازی: {result.intent.target}")
        ... else:
        ...     print(f"سوالات لازمة: {result.missing_fields}")
    """
    
    def __init__(self, ai_brain: Optional[AIBrain] = None):
        """مقداردهی اولیه Intent Analyzer
        
        Args:
            ai_brain: AI Brain برای پردازش (اگر None، خود ایجاد می‌کند)
        """
        self.ai_brain = ai_brain or AIBrain()
        self.logger = logger
        self._session_counter = 0
        
        # Dictionary از فعل‌های شناخته شده
        self.known_verbs = {
            # انگلیسی
            "open": ["open", "launch", "start", "run"],
            "play": ["play", "start", "begin"],
            "create": ["create", "make", "new", "build"],
            "delete": ["delete", "remove", "erase", "clear"],
            "search": ["search", "find", "look", "browse"],
            "type": ["type", "write", "enter"],
            "click": ["click", "tap", "press"],
            "install": ["install", "setup", "deploy"],
            # فارسی
            "باز": ["باز", "اجرا", "شروع", "لانچ"],
            "بازی": ["بازی", "شروع", "آغاز"],
            "ایجاد": ["ایجاد", "ساخت", "درست", "بساز"],
            "حذف": ["حذف", "پاک", "حذفش کن"],
            "جستجو": ["جستجو", "پیدا", "جستجو کن"],
            "نوشتن": ["نوشتن", "تایپ", "بنویس"],
            "کلیک": ["کلیک", "ضربه", "فشار"],
            "نصب": ["نصب", "راه‌اندازی", "استقرار"],
        }
        
        self.logger.info("✅ IntentAnalyzer initialized")
    
    async def analyze(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentAnalysisResult:
        """تحلیل درخواست کاربر
        
        Args:
            request: درخواست متنی کاربر
            context: اطلاعات زمینه‌ای (تاریخچه، preferences)
            
        Returns:
            IntentAnalysisResult شامل Intent و اطلاعات تفصیلی
            
        Raises:
            ValueError: اگر request خالی یا معتبر نباشد
        """
        if not request or not request.strip():
            raise ValueError("درخواست نمی‌تواند خالی باشد")
        
        self.logger.info(f"🔍 Analyzing request: {request[:50]}...")
        
        try:
            # مرحله ۱: تشخیص زبان
            language = await self._detect_language(request)
            self.logger.debug(f"📌 Language detected: {language}")
            
            # مرحله ۲: استخراج فعل اصلی
            verb, verb_confidence = await self._extract_verb(request, language)
            self.logger.debug(f"🔤 Verb: {verb} ({verb_confidence:.0%})")
            
            # مرحله ۳: استخراج هدف
            target, target_confidence = await self._extract_target(
                request, verb, language
            )
            self.logger.debug(f"🎯 Target: {target} ({target_confidence:.0%})")
            
            # مرحله ۴: استخراج پارامترهای تفصیلی
            parameters = await self._extract_parameters(
                request, verb, target, language
            )
            self.logger.debug(f"📋 Parameters: {parameters}")
            
            # مرحله ۵: شناسایی محدودیت‌ها
            constraints = await self._extract_constraints(request, language)
            self.logger.debug(f"⚠️ Constraints: {constraints}")
            
            # مرحله ۶: محاسبه اطمینان کلی
            overall_confidence = self._calculate_confidence(
                verb_confidence,
                target_confidence,
                len(parameters),
                len(request.split())
            )
            
            # ایجاد Intent
            intent = Intent(
                verb=verb,
                target=target,
                parameters=parameters,
                constraints=constraints,
                confidence=overall_confidence,
                raw_request=request,
                language=language
            )
            
            # مرحله ۷: شناسایی موارد نامشخص
            missing_fields = await self._identify_missing_fields(
                intent, context
            )
            
            # ایجاد نتیجه
            result = IntentAnalysisResult(
                intent=intent,
                missing_fields=missing_fields,
                requires_clarification=len(missing_fields) > 0
            )
            
            self.logger.info(f"✅ Analysis complete: {intent}")
            return result
            
        except Exception as e:
            self.logger.exception(f"❌ Error analyzing request: {e}")
            raise
    
    async def _detect_language(self, text: str) -> str:
        """تشخیص زبان درخواست
        
        Args:
            text: متن برای تشخیص
            
        Returns:
            'fa' برای فارسی، 'en' برای انگلیسی
        """
        # شمارش حروف فارسی و انگلیسی
        persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
        
        # اگر بیش از ۶۰٪ فارسی باشد، زبان فارسی است
        total_chars = persian_chars + english_chars
        if total_chars > 0 and persian_chars / total_chars > 0.6:
            return "fa"
        return "en"
    
    async def _extract_verb(
        self,
        request: str,
        language: str
    ) -> Tuple[str, float]:
        """استخراج فعل اصلی از درخواست
        
        Args:
            request: درخواست
            language: زبان شناسایی شده
            
        Returns:
            (verb, confidence)
        """
        request_lower = request.lower()
        
        # جستجو در known_verbs
        for canonical_verb, aliases in self.known_verbs.items():
            for alias in aliases:
                if alias in request_lower:
                    # یافت شد!
                    confidence = 0.90  # اطمینان بالا برای کلمات شناخته شده
                    return canonical_verb, confidence
        
        # اگر یافت نشد، از AI استفاده کنید
        prompt = f"""درخواست کاربر را تحلیل کن و فعل اصلی را شناسایی کن.
        
درخواست: "{request}"

فعل اصلی چیست؟ (مثال: open, play, create, delete, search)
فقط یک کلمه جواب بده."""
        
        # Use AI brain with fallback for robust verb extraction
        response = await self.ai_brain.ask_with_fallback(prompt, mode="analyze")
        verb = response.strip().lower().split()[0] if response else "unknown"
        
        return verb, 0.70  # اطمینان متوسط برای AI
    
    async def _extract_target(
        self,
        request: str,
        verb: str,
        language: str
    ) -> Tuple[str, float]:
        """استخراج هدف (target) از درخواست
        
        Args:
            request: درخواست
            verb: فعل اصلی
            language: زبان
            
        Returns:
            (target, confidence)
        """
        # دیکشنری اهداف شناخته شده
        common_targets = {
            "notepad": ["notepad", "نوت‌پد", "دفترچه"],
            "steam": ["steam", "استیم"],
            "game": ["game", "بازی", "گیم"],
            "folder": ["folder", "پوشه", "فولدر"],
            "file": ["file", "فایل", "فیل"],
            "browser": ["browser", "مرورگر", "کروم", "فایرفاکس"],
        }
        
        request_lower = request.lower()
        
        # جستجو در common_targets
        for canonical_target, aliases in common_targets.items():
            for alias in aliases:
                if alias in request_lower:
                    return canonical_target, 0.85
        
        # اگر یافت نشد، از AI استفاده کنید
        prompt = f"""درخواست کاربر را تحلیل کن.
        
فعل: {verb}
درخواست: "{request}"

کاربر چه چیزی را می‌خواهد {verb} کند؟ (مثال: notepad, steam, file)
فقط یک کلمه جواب بده."""
        
        # Use AI brain with fallback for robust target extraction
        response = await self.ai_brain.ask_with_fallback(prompt, mode="analyze")
        target = response.strip().lower().split()[0] if response else "unknown"
        
        return target, 0.65
    
    async def _extract_parameters(
        self,
        request: str,
        verb: str,
        target: str,
        language: str
    ) -> Dict[str, Any]:
        """استخراج پارامترهای تفصیلی
        
        Args:
            request: درخواست
            verb: فعل
            target: هدف
            language: زبان
            
        Returns:
            Dictionary شامل پارامترهای استخراج شده
        """
        parameters = {}
        request_lower = request.lower()
        
        # پارامتر: مدت زمان
        if "until" in request_lower or "برگردم" in request_lower or "برگردی" in request_lower:
            parameters["duration"] = "until_return"
        elif "minute" in request_lower or "دقیقه" in request_lower:
            # استخراج عدد
            import re
            match = re.search(r'(\d+)\s*(?:minute|دقیقه)', request_lower)
            if match:
                parameters["duration"] = f"{match.group(1)}_minutes"
        
        # پارامتر: نام
        if "name" in request_lower or "نام" in request_lower:
            import re
            # جستجو برای الگوی "name X" یا "اسم X"
            match = re.search(r'(?:name|اسم)\s+(["\']?)([^"\']+)\1', request)
            if match:
                parameters["name"] = match.group(2)
        
        # پارامتر: مسیر (path)
        if "path" in request_lower or "مسیر" in request_lower or ":" in request:
            import re
            match = re.search(r'([A-Z]:\\[^"]+|/[^"]+)', request)
            if match:
                parameters["path"] = match.group(1)
        
        return parameters
    
    async def _extract_constraints(
        self,
        request: str,
        language: str
    ) -> List[str]:
        """استخراج محدودیت‌ها و شرایط
        
        Args:
            request: درخواست
            language: زبان
            
        Returns:
            لیست محدودیت‌های شناسایی شده
        """
        constraints = []
        request_lower = request.lower()
        
        # محدودیت: امن (safe mode)
        if "safe" in request_lower or "محافظه" in request_lower:
            constraints.append("safe_mode")
        
        # محدودیت: کم CPU
        if "minimal" in request_lower or "کم" in request_lower:
            constraints.append("minimal_cpu")
        
        # محدودیت: بدون صدا
        if "silent" in request_lower or "بدون صدا" in request_lower:
            constraints.append("no_sound")
        
        # محدودیت: تنها (مجزا)
        if "only" in request_lower or "فقط" in request_lower:
            constraints.append("isolated")
        
        return constraints
    
    def _calculate_confidence(
        self,
        verb_conf: float,
        target_conf: float,
        param_count: int,
        word_count: int
    ) -> float:
        """محاسبه اطمینان کلی
        
        Args:
            verb_conf: اطمینان فعل
            target_conf: اطمینان هدف
            param_count: تعداد پارامترها
            word_count: تعداد کلمات
            
        Returns:
            confidence بین 0.0 و 1.0
        """
        # میانگین اطمینان‌های بخش‌ها
        base_confidence = (verb_conf + target_conf) / 2
        
        # تعداد کلمات کافی نشان دهنده درخواست واضح‌تر است
        clarity_boost = min(word_count / 10, 0.1)  # حداکثر 10% افزایش
        
        # پارامترهای تفصیلی افزایش اطمینان می‌دهند
        param_boost = min(param_count * 0.05, 0.15)  # حداکثر 15% افزایش
        
        confidence = min(base_confidence + clarity_boost + param_boost, 1.0)
        return confidence
    
    async def _identify_missing_fields(
        self,
        intent: Intent,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """شناسایی فیلدهای نامشخص که نیاز به سؤال دارند
        
        Args:
            intent: Intent تشخیص داده شده
            context: اطلاعات زمینه‌ای
            
        Returns:
            لیست فیلدهای نامشخص
        """
        missing = []
        
        # اگر فعل بازی است اما نوع بازی مشخص نیست
        if intent.verb == "play" and "game" in intent.target.lower():
            if "game_type" not in intent.parameters:
                missing.append("game_type")  # کدام بازی؟
        
        # اگر فعل ایجاد است اما نام مشخص نیست
        if intent.verb in ["ایجاد", "create"]:
            if "name" not in intent.parameters:
                missing.append("name")  # نام چه باشد؟
        
        # اگر مسیر نامشخص است
        if "folder" in intent.target.lower() or "file" in intent.target.lower():
            if "path" not in intent.parameters:
                missing.append("path")  # در کجا؟
        
        return missing
    
    async def analyze_batch(
        self,
        requests: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[IntentAnalysisResult]:
        """تحلیل دسته‌ای درخواست‌ها
        
        Args:
            requests: لیست درخواست‌ها
            context: اطلاعات زمینه‌ای
            
        Returns:
            لیست نتایج تحلیل
        """
        results = []
        for request in requests:
            try:
                result = await self.analyze(request, context)
                results.append(result)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to analyze '{request}': {e}")
                # درخواست ناموفق را با اطمینان پایین اضافه کن
                intent = Intent(
                    verb="unknown",
                    target="unknown",
                    confidence=0.0,
                    raw_request=request
                )
                result = IntentAnalysisResult(
                    intent=intent,
                    missing_fields=["entire_request"],
                    requires_clarification=True
                )
                results.append(result)
        
        return results
    
    # ═══════════════════════════════════════════════════════════
    # Dialog methods (merged from dialog_manager.py)
    # ═══════════════════════════════════════════════════════════
    
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
    
    async def collect_missing_info(
        self,
        intent_result: IntentAnalysisResult,
        user_language: str = "fa",
        max_clarifications: int = 3
    ) -> IntentAnalysisResult:
        """جمع‌آوری اطلاعات گمشده از طریق مکالمه."""
        self._session_counter += 1
        session_id = f"dialog_{self._session_counter}"
        
        session = DialogSession(
            session_id=session_id,
            intent_result=intent_result
        )
        
        self.logger.info(f"Starting dialog session {session_id}")
        self.logger.info(f"Missing fields: {intent_result.missing_fields}")
        
        if not intent_result.missing_fields:
            self.logger.info("No missing fields - returning original intent")
            return intent_result
        
        try:
            session.state = DialogState.QUESTIONING
            
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
            
            session.state = DialogState.CONFIRMING
            confirmed = await self._confirm_understanding(
                session,
                user_language
            )
            
            if not confirmed:
                self.logger.warning("Understanding not confirmed - retrying")
                return await self.collect_missing_info(
                    intent_result,
                    user_language,
                    max_clarifications - 1
                )
            
            session.state = DialogState.COMPLETE
            complete_intent = self._merge_responses_with_intent(
                intent_result.intent,
                session.responses
            )
            
            session.complete_intent = complete_intent
            
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
            return intent_result
    
    def _generate_question(
        self,
        field_name: str,
        intent: Intent,
        language: str = "fa"
    ) -> DialogQuestion:
        lang_key = "fa" if language == "fa" else "en"
        
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
        session.questions_asked.append(question)
        
        question_text = (
            question.question_text if user_language == "fa"
            else question.question_text_en
        )
        
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
                print(f"\n❓ {question_text}{suggestions_text}")
                
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
        try:
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
        base_confidence = 0.95
        
        if len(answer.strip()) < 2:
            base_confidence -= 0.3
        
        if question.suggestions and answer in question.suggestions:
            base_confidence = 0.98
        
        return min(base_confidence, 1.0)
    
    def _merge_responses_with_intent(
        self,
        intent: Intent,
        responses: List[DialogResponse]
    ) -> Intent:
        updated_intent = Intent(
            verb=intent.verb,
            target=intent.target,
            parameters=intent.parameters.copy(),
            constraints=intent.constraints.copy(),
            confidence=intent.confidence,
            raw_request=intent.raw_request,
            language=intent.language
        )
        
        for response in responses:
            updated_intent.parameters[response.field_name] = response.answer
        
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
        if field_name in self.PREDEFINED_QUESTIONS:
            return self.PREDEFINED_QUESTIONS[field_name]["suggestions"]
        
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
                suggestions = [s.strip() for s in response.split('\n') if s.strip()]
                return suggestions[:5]
            except Exception as e:
                self.logger.warning(f"Failed to get AI suggestions: {str(e)}")
        
        return []


class SystemActionParser:
    """تبدیل درخواست‌های طبیعی کاربر به اقدامات سیستمی و Desktop."""
    
    def __init__(self, registry: SystemCapabilityRegistry):
        self.registry = registry
        self.ai_brain = AIBrain()
        
        self.click_patterns = [
            r'click\s+(?:on\s+)?["\']([^"\']+)["\']',
            r'click\s+(?:on\s+)?(\w+)',
            r'کلیک\s+(?:روی\s+)?["\']([^"\']+)["\']',
            r'کلیک\s+(?:روی\s+)?(\S+)',
            r'press\s+(?:on\s+)?["\']([^"\']+)["\']',
            r'press\s+(?:on\s+)?(\w+)',
            r'بزن\s+(?:روی\s+)?["\']([^"\']+)["\']',
            r'بزن\s+(?:روی\s+)?(\S+)',
        ]
        
        self.type_patterns = [
            r'type\s+["\']([^"\']+)["\']',
            r'تایپ\s+["\']([^"\']+)["\']',
            r'write\s+["\']([^"\']+)["\']',
            r'بنویس\s+["\']([^"\']+)["\']',
            r'enter\s+["\']([^"\']+)["\']',
            r'type\s+(\S.+?)(?:\.|,| and | then |$)',
            r'write\s+(\S.+?)(?:\.|,| and | then |$)',
            r'enter\s+(\S.+?)(?:\.|,| and | then |$)',
        ]
        
        self.drag_patterns = [
            r'drag\s+["\']?([^"\']+?)["\']?\s+to\s+["\']?([^"\']+)["\']?',
            r'بکش\s+["\']?([^"\']+?)["\']?\s+به\s+["\']?([^"\']+)["\']?',
            r'move\s+["\']?([^"\']+?)["\']?\s+to\s+["\']?([^"\']+)["\']?',
        ]
    
    async def parse_request(self, user_request: str) -> list[dict[str, Any]]:
        logger.info("Processing request with AI: %s", user_request)
        try:
            ai_response = await self.ai_brain.interpret_system_request(user_request)
            if ai_response and isinstance(ai_response, list):
                logger.info("AI extracted %d actions", len(ai_response))
                return ai_response
            logger.warning("AI returned invalid response, trying fallback")
        except Exception as e:
            logger.error("AI interpretation failed: %s", e)
        
        actions = await self._simple_fallback_parse(user_request)
        logger.info("Extracted %d actions from fallback", len(actions))
        return actions
    
    async def _simple_fallback_parse(self, user_request: str) -> list[dict[str, Any]]:
        user_lower = user_request.lower()
        actions = []
        
        if any(kw in user_lower for kw in ['open', 'launch', 'start', 'run', 'باز', 'اجرا', 'شروع']):
            app_name = await self._ai_extract_app_name(user_request)
            if app_name:
                actions.append({
                    "type": "LaunchApp",
                    "params": {"app_name": app_name, "arguments": [], "require_consent": False},
                    "priority": "normal",
                    "description": f"Open {app_name}"
                })
        
        if any(kw in user_lower for kw in ['install', 'setup', 'نصب']):
            package = await self._ai_extract_package_name(user_request)
            if package:
                actions.append({
                    "type": "InstallPackage",
                    "params": {"package_name": package, "package_manager": "winget", "silent": True},
                    "priority": "normal",
                    "description": f"Install {package}"
                })
        
        if any(kw in user_lower for kw in ['close', 'kill', 'terminate', 'stop', 'بستن', 'توقف']):
            process = await self._ai_extract_app_name(user_request)
            if process:
                actions.append({
                    "type": "TerminateProcess",
                    "params": {"process_name": process, "force": False},
                    "priority": "normal",
                    "description": f"Close {process}"
                })
        
        if any(kw in user_lower for kw in ['create', 'make', 'new', 'build', 'ایجاد', 'ساخت', 'جدید']):
            folder_keywords = ['folder', 'directory', 'پوشه', 'دایرکتوری']
            file_keywords = ['file', 'document', 'text', 'فایل', 'متن']
            
            if any(kw in user_lower for kw in folder_keywords):
                folder_name = self._extract_name_after_keyword(user_request, ['folder', 'directory', 'پوشه', 'دایرکتوری called', 'named', 'نام'])
                if not folder_name:
                    folder_name = "New Folder"
                
                location = "desktop"
                if 'desktop' in user_lower or 'میز' in user_lower or 'دسکتاپ' in user_lower:
                    desktop = str(Path.home() / "Desktop")
                    folder_path = str(Path(desktop) / folder_name)
                else:
                    location_path = self._extract_path(user_request)
                    if location_path:
                        folder_path = str(Path(location_path) / folder_name)
                    else:
                        folder_path = str(Path.home() / "Desktop" / folder_name)
                
                actions.append({
                    "type": "ExecuteCommand",
                    "params": {
                        "command": f'mkdir "{folder_path}" 2>nul',
                        "shell": "cmd",
                        "timeout": 10
                    },
                    "priority": "normal",
                    "description": f"Create folder '{folder_name}' on {location}"
                })
            
            if any(kw in user_lower for kw in file_keywords):
                file_name = self._extract_name_after_keyword(user_request, ['file', 'document', 'فایل', 'document called', 'named', 'نام'])
                if not file_name:
                    file_name = "new_file.txt"
                
                if 'desktop' in user_lower or 'میز' in user_lower or 'دسکتاپ' in user_lower:
                    file_path = str(Path.home() / "Desktop" / file_name)
                else:
                    location_path = self._extract_path(user_request)
                    if location_path:
                        file_path = str(Path(location_path) / file_name)
                    else:
                        file_path = str(Path.home() / "Desktop" / file_name)
                
                actions.append({
                    "type": "ExecuteCommand",
                    "params": {
                        "command": f'type nul > "{file_path}" 2>nul',
                        "shell": "cmd",
                        "timeout": 10
                    },
                    "priority": "normal",
                    "description": f"Create file '{file_name}' on desktop"
                })
        
        if any(kw in user_lower for kw in ['hardware', 'سخت‌افزار', 'cpu', 'ram', 'memory', 'info']):
            actions.append({
                "type": "QueryHardware",
                "params": {"query_type": "all"},
                "priority": "normal",
                "description": "Get hardware information"
            })
        
        click_action = self._parse_click_action(user_request)
        if click_action:
            actions.append(click_action)
        
        type_action = self._parse_type_action(user_request)
        if type_action:
            actions.append(type_action)
        
        drag_action = self._parse_drag_action(user_request)
        if drag_action:
            actions.append(drag_action)
        
        wait_action = self._parse_wait_action(user_request)
        if wait_action:
            actions.append(wait_action)
        
        hotkey_action = self._parse_hotkey_action(user_request)
        if hotkey_action:
            actions.append(hotkey_action)
        
        scroll_action = self._parse_scroll_action(user_request)
        if scroll_action:
            actions.append(scroll_action)
        
        return actions
    
    def _parse_click_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['click', 'کلیک', 'press', 'بزن']):
            return None
        
        for pattern in self.click_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                target = match.group(1).strip()
                button = "left"
                if any(kw in request_lower for kw in ['right', 'راست']):
                    button = "right"
                elif any(kw in request_lower for kw in ['middle', 'وسط']):
                    button = "middle"
                clicks = 2 if any(kw in request_lower for kw in ['double', 'دوبار', 'دابل']) else 1
                return {
                    "type": "DesktopClick",
                    "params": {"target": target, "button": button, "clicks": clicks},
                    "priority": "normal",
                    "description": f"Click on '{target}'"
                }
        return None
    
    def _parse_type_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['type', 'تایپ', 'write', 'بنویس', 'enter']):
            return None
        
        for pattern in self.type_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                target = None
                target_pattern = r'(?:in|into|at|در|توی)\s+["\']?(.+?)["\']?(?:\s|$)'
                target_match = re.search(target_pattern, request, re.IGNORECASE)
                if target_match:
                    target = target_match.group(1).strip()
                return {
                    "type": "DesktopType",
                    "params": {"text": text, "target": target},
                    "priority": "normal",
                    "description": f"Type '{text[:30]}...'" if len(text) > 30 else f"Type '{text}'"
                }
        return None
    
    def _parse_drag_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['drag', 'بکش', 'move']):
            return None
        for pattern in self.drag_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                source = match.group(1).strip()
                target = match.group(2).strip()
                return {
                    "type": "DesktopDragDrop",
                    "params": {"source": source, "target": target},
                    "priority": "normal",
                    "description": f"Drag '{source}' to '{target}'"
                }
        return None
    
    def _parse_wait_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['wait', 'صبر', 'انتظار']):
            return None
        
        wait_type = "time"
        target = 3.0
        if any(kw in request_lower for kw in ['for', 'until', 'برای', 'تا']):
            element_pattern = r'(?:for|until|برای|تا)\s+["\']?(.+?)["\']?(?:\s|$)'
            match = re.search(element_pattern, request, re.IGNORECASE)
            if match:
                wait_type = "element"
                target = match.group(1).strip()
        else:
            time_pattern = r'(\d+(?:\.\d+)?)\s*(?:second|sec|ثانیه)?'
            match = re.search(time_pattern, request)
            if match:
                target = float(match.group(1))
        
        return {
            "type": "DesktopWait",
            "params": {"wait_type": wait_type, "target": target, "timeout": 30},
            "priority": "normal",
            "description": f"Wait for {target}"
        }
    
    def _parse_hotkey_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        hotkey_map = {
            'copy': ['ctrl', 'c'], 'کپی': ['ctrl', 'c'],
            'paste': ['ctrl', 'v'], 'پیست': ['ctrl', 'v'],
            'cut': ['ctrl', 'x'], 'برش': ['ctrl', 'x'],
            'undo': ['ctrl', 'z'], 'بازگشت': ['ctrl', 'z'],
            'redo': ['ctrl', 'y'],
            'save': ['ctrl', 's'], 'ذخیره': ['ctrl', 's'],
            'select all': ['ctrl', 'a'],
            'find': ['ctrl', 'f'], 'جستجو': ['ctrl', 'f'],
            'alt tab': ['alt', 'tab'], 'تعویض پنجره': ['alt', 'tab'],
        }
        for phrase, keys in hotkey_map.items():
            if phrase in request_lower:
                return {
                    "type": "DesktopHotkey",
                    "params": {"keys": keys},
                    "priority": "normal",
                    "description": f"Press {'+'.join(keys)}"
                }
        
        hotkey_pattern = r'(ctrl|alt|shift|win)[\s+]+(ctrl|alt|shift|win|[a-z0-9])'
        match = re.search(hotkey_pattern, request_lower)
        if match:
            keys = [match.group(1), match.group(2)]
            return {
                "type": "DesktopHotkey",
                "params": {"keys": keys},
                "priority": "normal",
                "description": f"Press {'+'.join(keys)}"
            }
        return None
    
    def _parse_scroll_action(self, request: str) -> Optional[dict[str, Any]]:
        request_lower = request.lower()
        if not any(kw in request_lower for kw in ['scroll', 'اسکرول']):
            return None
        
        direction = "down"
        if any(kw in request_lower for kw in ['up', 'بالا']):
            direction = "up"
        elif any(kw in request_lower for kw in ['down', 'پایین']):
            direction = "down"
        elif any(kw in request_lower for kw in ['left', 'چپ']):
            direction = "left"
        elif any(kw in request_lower for kw in ['right', 'راست']):
            direction = "right"
        
        clicks = 3
        amount_pattern = r'(\d+)\s*(?:time|times|بار)?'
        match = re.search(amount_pattern, request)
        if match:
            clicks = int(match.group(1))
        
        return {
            "type": "DesktopScroll",
            "params": {"direction": direction, "clicks": clicks},
            "priority": "normal",
            "description": f"Scroll {direction} {clicks} times"
        }
    
    async def _ai_extract_app_name(self, request: str) -> Optional[str]:
        try:
            prompt = f"""Extract the application name from this request and return ONLY the executable name with .exe extension.
If the app is common, use standard Windows executable names.

Request: {request}

Examples:
- "open steam" → steam.exe
- "باز کن استیم" → steam.exe
- "launch chrome" → chrome.exe
- "run notepad" → notepad.exe
- "اجرا کن فتوشاپ" → photoshop.exe

Return ONLY the .exe filename, nothing else:"""
            
            response = await self.ai_brain.ask(prompt, mode="system", max_tokens=50)
            
            if response:
                if isinstance(response, str):
                    exe_name = response.strip().lower()
                elif hasattr(response, 'content'):
                    exe_name = response.content.strip().lower()
                elif hasattr(response, 'completion'):
                    exe_name = response.completion.strip().lower()
                else:
                    logger.error("Unexpected response type: %s", type(response))
                    exe_name = str(response).strip().lower()
                
                exe_name = exe_name.strip("\"'` \n\t")
                if not exe_name.endswith('.exe'):
                    exe_name += '.exe'
                logger.info("AI extracted app name: %s", exe_name)
                return exe_name
        except Exception as e:
            logger.error("AI app extraction failed: %s", e)
        
        match = re.search(r'(?:open|launch|start|run|باز|اجرا|شروع)\s+(\w+)', request, re.IGNORECASE)
        if match:
            app_name = match.group(1).lower()
            if not app_name.endswith('.exe'):
                app_name += '.exe'
            logger.info("Regex fallback extracted app name: %s", app_name)
            return app_name
        return None
    
    async def _ai_extract_package_name(self, request: str) -> Optional[str]:
        try:
            prompt = f"""Extract the package/software name from this installation request.
Return ONLY the package name that can be used with winget or pip.

Request: {request}

Examples:
- "install git" → git
- "نصب پایتون" → python
- "setup nodejs" → nodejs
- "نصب کن docker" → docker

Return ONLY the package name:"""
            
            response = await self.ai_brain.ask(prompt, mode="system", max_tokens=30)
            if response:
                package = response.strip().lower()
                logger.info("AI extracted package: %s", package)
                return package
        except Exception as e:
            logger.error("AI package extraction failed: %s", e)
        return None
    
    def _extract_app_name(self, request: str) -> Optional[str]:
        exe_match = re.search(r'(\w+\.exe)', request, re.IGNORECASE)
        if exe_match:
            return exe_match.group(1)
        return None
    
    def _extract_package_name(self, request: str) -> Optional[str]:
        words = request.split()
        if words:
            return words[-1]
        return None
    
    def _extract_process_name(self, request: str) -> Optional[str]:
        return self._extract_app_name(request)
    
    def _extract_name_after_keyword(self, request: str, keywords: list[str]) -> Optional[str]:
        location_words = ['on', 'in', 'at', 'to', 'into', 'onto', 'under', 'روی', 'در', 'به', 'توی']
        for kw in keywords:
            quoted = re.search(rf"""\b{re.escape(kw)}\s+["'""]([^"'""]+)["'""]""", request, re.IGNORECASE)
            if quoted:
                return quoted.group(1).strip()
            called = re.search(rf'\b{re.escape(kw)}\s+(?:called|named|به\s+نام)\s+["\']?([^"\']+?)["\']?(?:\s+|$)', request, re.IGNORECASE)
            if called:
                name = called.group(1).strip()
                if name and len(name) < 100 and name.lower() not in location_words:
                    return name
            for loc in location_words:
                if re.search(rf'\b{re.escape(kw)}\s+{re.escape(loc)}\b', request, re.IGNORECASE):
                    break
            else:
                word_after = re.search(rf'\b{re.escape(kw)}\s+(\S+)', request, re.IGNORECASE)
                if word_after:
                    name = word_after.group(1).strip().rstrip('.,;:\'"')
                    if name and len(name) < 100 and name.lower() not in location_words:
                        return name
        return None

    def _extract_path(self, request: str) -> Optional[str]:
        path_patterns = [
            r'(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?(?:[A-Za-z]:\\[^\s"\']+)["\']?',
            r'(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?(?:\\\\[^\s"\']+)["\']?',
        ]
        for pattern in path_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                path = re.sub(r'^(?:in|on|at|to|into|در|روی|به|توی)\s+["\']?', '', match.group(0))
                path = path.strip().strip('"\'')
                if Path(path).exists():
                    return path
        return None
