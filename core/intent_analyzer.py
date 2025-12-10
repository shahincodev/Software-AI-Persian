# SPDX-License-Identifier: NOASSERTION
# Copyright (c) 2025 Shahin

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

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from core.ai_brain import AIBrain

logger = logging.getLogger(__name__)


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
        
        response = await self.ai_brain.think(prompt)
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
        
        response = await self.ai_brain.think(prompt)
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
