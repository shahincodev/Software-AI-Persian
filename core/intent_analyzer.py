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
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

from core.ai_brain import AIBrain
from core.system_action_parser import SystemActionParser
from core.intent_models import (
    DialogState, QuestionType, DialogQuestion,
    DialogResponse, DialogSession, ConfidenceLevel,
    Intent, IntentAnalysisResult
)

logger = logging.getLogger(__name__)


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
        # IMPORTANT: order matters — first-match-wins for English aliases.
        # Action verbs must come BEFORE converse/greeting verbs so that
        # imperative requests (e.g. "create folder", "write Hello World")
        # are not misclassified when the request content happens to contain
        # words like "hello", "how", "what" etc.
        self.known_verbs = {
            # === English action verbs (checked first) ===
            "create":     ["create", "make", "new", "build"],
            "open":       ["open", "launch", "start", "run"],
            "delete":     ["delete", "remove", "erase", "clear"],
            "type":       ["type", "write", "enter"],
            "search":     ["search", "find", "look", "browse", "check", "find out"],
            "click":      ["click", "tap", "press"],
            "install":    ["install", "setup", "deploy"],
            "play":       ["play", "begin"],
            # === English converse/greeting (last — prevents false positives) ===
            "converse":   ["say", "tell", "ask", "answer", "reply", "respond",
                           "greet", "hi", "hey",
                           "meaning", "define", "explain", "describe", "mean",
                           "question", "introduce", "introduction"],
            # === Persian action verbs (checked first) ===
            "ایجاد":      ["ایجاد", "ساخت", "درست", "بساز", "ایجاد کن"],
            "باز":        ["باز", "اجرا", "شروع", "لانچ", "اجرا کن"],
            "حذف":        ["حذف", "پاک", "حذفش کن"],
            "نوشتن":      ["نوشتن", "تایپ", "بنویس"],
            "جستجو":      ["جستجو", "پیدا", "جستجو کن", "نگاه کن", "ببین"],
            "کلیک":       ["کلیک", "ضربه", "فشار", "بزن"],
            "نصب":        ["نصب", "راه‌اندازی", "استقرار"],
            "بازی":       ["بازی", "آغاز"],
            # === Persian converse/greeting (last) ===
            "گفتگو":      ["بگو", "پرسش", "سوال", "جواب", "پاسخ", "سلام", "درود",
                           "معنی", "توضیح", "چیست", "چیه", "کیه", "کجاست", "یعنی",
                           "منظور", "تعریف", "معرفی", "چطور", "چرا", "چه", "چی"],
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
            
            # مرحله ۶.۵: بازبینی verb — اگر verb "converse" باشد ولی متن حاوی
            # کلمات کلیدی اکشن باشد، verb را اصلاح کن
            action_override = self._check_verb_override(request, verb, language)
            if action_override:
                intent.verb = action_override
                intent.confidence = min(intent.confidence + 0.05, 1.0)
                self.logger.debug(f"🔄 Verb overridden from '{verb}' to '{action_override}'")
            
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
        
        # جستجو در known_verbs — برای انگلیسی از word boundaries استفاده می‌شود
        # تا false positive مانند "ask" در "task" رخ ندهد
        candidates = []

        for canonical_verb, aliases in self.known_verbs.items():
            for alias in aliases:
                is_english = all(c.isascii() and c.isalpha() for c in alias)
                if is_english:
                    if re.search(r'\b' + re.escape(alias) + r'\b', request_lower):
                        return canonical_verb, 0.90
                else:
                    pos = request_lower.find(alias)
                    if pos != -1:
                        candidates.append((pos, len(alias), canonical_verb))

        if candidates:
            candidates.sort(key=lambda x: (x[0], -x[1]))
            return candidates[0][2], 0.90
        
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
            "browser": ["browser", "chrome", "firefox", "edge", "مرورگر", "کروم", "فایرفاکس"],
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
    
    def _check_verb_override(
        self,
        request: str,
        current_verb: str,
        language: str
    ) -> Optional[str]:
        """بازبینی verb — اگر verb "converse" باشد ولی متن حاوی کلمات کلیدی
        اکشن (create, open, write, ...) باشد، verb مناسب را برمی‌گرداند.
        
        این تابع از اینکه "Please do my requests..." به converse برود جلوگیری می‌کند
        وقتی که متن واقعاً درخواست عملیات سیستمی دارد.
        
        همچنین حالت معکوس: اگر verb اکشن باشد ولی متن سوال "how to/do/can/could"
        باشد (اطلاعاتی، نه دستوری)، به "converse" برمی‌گرداند.
        مثال: "Tell me how to create a folder" → known_verbs مستقیماً "create"
        را پیدا می‌کند، ولی قصد کاربر اطلاعاتی است، نه دستور اجرا.
        """
        request_lower = request.lower()
        how_to_match = re.search(r'\bhow\s+(to|do|can|could)\b', request_lower)
        
        # حالت ۱: verb اکشن است ولی متن سوال how-to است ← بازگشت به converse
        if current_verb in ("create", "open", "delete", "write", "search",
                           "click", "install", "type", "play") and how_to_match:
            self.logger.debug(
                f"🔍 Verb override: '{current_verb}' → 'converse' "
                f"(informational how-to question)"
            )
            return "converse"
        
        # حالت ۲ (قبلی): verb converse است — فقط در این صورت ادامه بده
        if current_verb != "converse" and current_verb not in ("گفتگو",):
            return None
        
        # اگر سوال how-to است، converse→action را لغو کن
        if how_to_match:
            self.logger.debug(
                f"🔍 Skipping verb override for informational question: '{request[:50]}'"
            )
            return None
        
        # مپ کردن کلمات کلیدی به verb‌های مناسب
        action_signals = {
            "create":  ["create", "make", "new folder", "new file", "build", "mkdir"],
            "open":    ["open", "launch", "start", "run"],
            "delete":  ["delete", "remove", "erase", "clear"],
            "write":   ["write", "type", "enter text"],
            "search":  ["search", "find", "look for", "browse", "check"],
            "click":   ["click", "tap", "press"],
            "install": ["install", "setup", "deploy"],
        }
        
        for action_verb, keywords in action_signals.items():
            if any(kw in request_lower for kw in keywords):
                self.logger.debug(
                    f"🔍 Verb override: '{current_verb}' → '{action_verb}' "
                    f"(signal: {[k for k in keywords if k in request_lower]})"
                )
                return action_verb
        
        return None
    
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
        play_verbs = ["play", "بازی"]
        if intent.verb in play_verbs and (
            "game" in intent.target.lower() or intent.target == "unknown"
        ):
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
        

