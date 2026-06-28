# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Plan Generator - تولید کننده پلان اجرایی

Plan Generator مسئول تبدیل Intent کامل (از Dialog Manager) به یک ExecutionPlan
قابل اجرا است. این پلان شامل مراحل مرتب شده، وابستگی‌ها، و منطق اجرا است.

مثال:
    >>> intent = Intent(verb="بازی", target="game", parameters={...})
    >>> generator = PlanGenerator()
    >>> plan = await generator.generate_plan(intent)
    >>> # plan.steps = [Step(action="باز کن Steam"), Step(action="پیدا کن CS"), ...]

Core Responsibilities:
    1. تولید مراحل (Step Generation)
    2. ترتیب‌بندی مراحل (Step Ordering)
    3. تشخیص وابستگی‌ها (Dependency Detection)
    4. بهینه‌سازی اجرا (Execution Optimization)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import uuid
from datetime import datetime

from core.intent_analyzer import Intent, IntentAnalysisResult
from core.ai_brain import AIBrain

# ═══════════════════════════════════════════════════════════════════════════════

logger = logging.getLogger(__name__)


class StepType(Enum):
    """انواع مراحل
    
    ACQUIRE: دریافت اطلاعات (جستجو، پرس و جو)
    OPEN: باز کردن برنامه یا فایل
    INTERACT: تعامل با برنامه (کلیک، تایپ)
    PROCESS: پردازش داده‌ها
    SAVE: ذخیره نتایج
    VERIFY: تایید موفقیت
    WAIT: انتظار برای شرایط
    CLEANUP: پاکسازی و پایان
    """
    ACQUIRE = "acquire"
    OPEN = "open"
    INTERACT = "interact"
    PROCESS = "process"
    SAVE = "save"
    VERIFY = "verify"
    WAIT = "wait"
    CLEANUP = "cleanup"


class ExecutionMode(Enum):
    """حالت‌های اجرا
    
    SEQUENTIAL: اجرای متوالی (یک‌ به‌یک)
    PARALLEL: اجرای موازی (همزمان)
    CONDITIONAL: اجرای شرطی
    """
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class ExecutionStep:
    """یک مرحله در برنامه اجرایی
    
    Attributes:
        step_id: شناسه یکتای مرحله
        order: ترتیب اجرا (۱، ۲، ۳، ...)
        action: متن عمل (فارسی)
        action_en: متن عمل (انگلیسی)
        step_type: نوع مرحله (OPEN, INTERACT, ...)
        target: هدف مرحله (برنامه، فایل، متغیر)
        parameters: پارامترهای مرحله
        dependencies: مراحل وابسته‌ی قبلی
        timeout: حداکثر زمان اجرا (ثانیه)
        retries: تعداد تلاش‌های مجدد
        fallback_action: عمل در صورت شکست
        execution_mode: حالت اجرا (SEQUENTIAL, PARALLEL, ...)
        priority: اولویت (1-10)
        description: توضیح مفصل
    """
    step_id: str
    order: int
    action: str
    action_en: str
    step_type: StepType
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # step_ids
    timeout: int = 30
    retries: int = 3
    fallback_action: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    priority: int = 5
    description: str = ""
    
    def __str__(self) -> str:
        """نمایش مختصر مرحله"""
        return f"[{self.order}] {self.action}"


@dataclass
class ExecutionPlan:
    """برنامه اجرایی کامل
    
    Attributes:
        plan_id: شناسه یکتای پلان
        intent: Intent اصلی
        steps: لیست مراحل
        total_estimated_time: تخمین کل زمان (ثانیه)
        complexity: پیچیدگی (SIMPLE, MEDIUM, COMPLEX)
        created_at: زمان ایجاد
        description: توضیح پلان
    """
    plan_id: str
    intent: Intent
    steps: List[ExecutionStep]
    total_estimated_time: int = 0
    complexity: str = "MEDIUM"
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    
    def get_step_by_id(self, step_id: str) -> Optional[ExecutionStep]:
        """دریافت مرحله با شناسه"""
        return next((s for s in self.steps if s.step_id == step_id), None)
    
    def get_parallel_steps(self, order: int) -> List[ExecutionStep]:
        """دریافت مراحلی که می‌توانند به‌صورت موازی اجرا شوند"""
        return [s for s in self.steps if s.order == order and s.execution_mode == ExecutionMode.PARALLEL]
    
    def get_sequential_order(self) -> List[ExecutionStep]:
        """دریافت ترتیب اجرای متوالی مراحل"""
        return sorted(self.steps, key=lambda s: s.order)


# ═══════════════════════════════════════════════════════════════════════════════


class PlanGenerator:
    """تولید کننده پلان اجرایی
    
    Plan Generator یک Intent کامل را می‌گیرد و یک ExecutionPlan دقیق
    تولید می‌کند که شامل مراحل مرتب شده و بهینه است.
    
    مثال:
        >>> generator = PlanGenerator(ai_brain=brain)
        >>> plan = await generator.generate_plan(intent)
        >>> print(f"تعداد مراحل: {len(plan.steps)}")
        >>> for step in plan.get_sequential_order():
        ...     print(f"{step.order}. {step.action}")
    """
    
    # الگوهای پیش‌تعریف شده برای اقدامات مختلف
    ACTION_PATTERNS = {
        "بازی": {
            "steps": [
                {"type": StepType.OPEN, "action": "باز کردن {target}"},
                {"type": StepType.WAIT, "action": "انتظار برای باز شدن"},
                {"type": StepType.INTERACT, "action": "شروع بازی"},
                {"type": StepType.WAIT, "action": "انتظار برای شروع"}
            ]
        },
        "ایجاد": {
            "steps": [
                {"type": StepType.ACQUIRE, "action": "تشخیص محل مورد نظر"},
                {"type": StepType.INTERACT, "action": "ایجاد {target}"},
                {"type": StepType.INTERACT, "action": "تنظیم نام: {name}"},
                {"type": StepType.VERIFY, "action": "تایید ایجاد"}
            ]
        },
        "کپی": {
            "steps": [
                {"type": StepType.OPEN, "action": "باز کردن مرورگر فایل"},
                {"type": StepType.INTERACT, "action": "پیدا کردن {source}"},
                {"type": StepType.INTERACT, "action": "کپی فایل"},
                {"type": StepType.INTERACT, "action": "رفتن به مقصد"},
                {"type": StepType.INTERACT, "action": "پیوند کردن فایل"},
                {"type": StepType.VERIFY, "action": "تایید کپی"}
            ]
        },
        "جستجو": {
            "steps": [
                {"type": StepType.OPEN, "action": "باز کردن مرورگر"},
                {"type": StepType.INTERACT, "action": "جستجوی: {query}"},
                {"type": StepType.WAIT, "action": "انتظار برای نتایج"},
                {"type": StepType.PROCESS, "action": "تحلیل نتایج"},
                {"type": StepType.SAVE, "action": "ذخیره نتایج"}
            ]
        },
        "نصب": {
            "steps": [
                {"type": StepType.ACQUIRE, "action": "دریافت بسته نرم‌افزار"},
                {"type": StepType.OPEN, "action": "اجرای نصب‌کننده"},
                {"type": StepType.INTERACT, "action": "تایید مجوزها"},
                {"type": StepType.WAIT, "action": "انتظار برای نصب"},
                {"type": StepType.INTERACT, "action": "تکمیل نصب"},
                {"type": StepType.VERIFY, "action": "تایید نصب"}
            ]
        }
    }
    
    def __init__(self, ai_brain: Optional[AIBrain] = None):
        """مقداردهی اولیه Plan Generator
        
        Args:
            ai_brain: نمونه AIBrain برای تولید پلان‌های پیشرفته
        """
        self.ai_brain = ai_brain
        self.logger = logging.getLogger(self.__class__.__name__)
        self._plan_counter = 0
        
        self.logger.info("Plan Generator initialized ✓")
    
    async def generate_plan(
        self,
        intent: Intent,
        context: Optional[Dict[str, Any]] = None,
        optimize: bool = True
    ) -> ExecutionPlan:
        """تولید پلان اجرایی برای یک Intent
        
        این متد کار اصلی Plan Generator است. Intent را تحلیل می‌کند
        و یک ExecutionPlan دقیق و بهینه تولید می‌کند.
        
        Args:
            intent: Intent کامل (از Dialog Manager) یا IntentAnalysisResult
            context: اطلاعات زمینه‌ای اضافی
            optimize: آیا پلان را بهینه‌سازی کنیم؟
        
        Returns:
            ExecutionPlan کامل و آماده‌ی اجرا
            
        مثال:
            >>> plan = await generator.generate_plan(intent, optimize=True)
        """
        if isinstance(intent, IntentAnalysisResult):
            intent = intent.intent
        self._plan_counter += 1
        plan_id = f"plan_{self._plan_counter}"
        
        self.logger.info(f"Generating plan {plan_id} for: {intent.verb} {intent.target}")
        
        try:
            # Step 1: تولید مراحل اولیه
            initial_steps = self._generate_initial_steps(intent)
            self.logger.info(f"Generated {len(initial_steps)} initial steps")
            
            # Step 2: تشخیص وابستگی‌ها
            steps_with_deps = self._detect_dependencies(initial_steps, intent)
            self.logger.info("Dependencies detected")
            
            # Step 3: ترتیب‌بندی مراحل
            ordered_steps = self._order_steps(steps_with_deps)
            self.logger.info("Steps ordered")
            
            # Step 4: اضافه کردن منطق retry و timeout
            enhanced_steps = self._enhance_steps(ordered_steps, intent)
            
            # Step 5: بهینه‌سازی (اختیاری)
            if optimize:
                enhanced_steps = self._optimize_plan(enhanced_steps, intent)
                self.logger.info("Plan optimized")
            
            # Step 6: محاسبه زمان و پیچیدگی
            total_time = sum(s.timeout for s in enhanced_steps)
            complexity = self._calculate_complexity(enhanced_steps)
            
            # ایجاد پلان نهایی
            plan = ExecutionPlan(
                plan_id=plan_id,
                intent=intent,
                steps=enhanced_steps,
                total_estimated_time=total_time,
                complexity=complexity,
                description=self._generate_description(intent, enhanced_steps)
            )
            
            self.logger.info(
                f"Plan generated: {len(plan.steps)} steps, "
                f"estimated time: {total_time}s, "
                f"complexity: {complexity}"
            )
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error generating plan: {str(e)}")
            raise
    
    def _generate_initial_steps(self, intent: Intent) -> List[ExecutionStep]:
        """تولید مراحل اولیه بر اساس Intent
        
        از الگوهای پیش‌تعریف شده استفاده می‌کند یا اگر الگو نیست،
        مراحل پویا تولید می‌کند.
        """
        steps = []
        step_counter = 0
        
        # بررسی وجود الگو برای این فعل
        pattern = self.ACTION_PATTERNS.get(intent.verb)
        
        if pattern:
            # استفاده از الگو
            for idx, pattern_step in enumerate(pattern["steps"], 1):
                step = ExecutionStep(
                    step_id=str(uuid.uuid4()),
                    order=idx,
                    action=self._format_action(pattern_step["action"], intent),
                    action_en=self._translate_action(
                        pattern_step["action"], intent, "en"
                    ),
                    step_type=pattern_step["type"],
                    target=intent.target,
                    parameters=intent.parameters.copy(),
                    timeout=self._estimate_timeout(pattern_step["type"]),
                    description=f"مرحله {idx}: {intent.verb} {intent.target}"
                )
                steps.append(step)
        else:
            # تولید پویا برای فعل نامشناخته
            steps.append(ExecutionStep(
                step_id=str(uuid.uuid4()),
                order=1,
                action=f"{intent.verb} {intent.target}",
                action_en=f"{intent.verb} {intent.target}",
                step_type=StepType.OPEN,
                target=intent.target,
                parameters=intent.parameters.copy(),
                timeout=30,
                description=f"اجرای: {intent.verb} {intent.target}"
            ))
        
        return steps
    
    def _detect_dependencies(
        self,
        steps: List[ExecutionStep],
        intent: Intent
    ) -> List[ExecutionStep]:
        """تشخیص وابستگی‌های بین مراحل
        
        مثال:
        - برای "بازی"، مرحله "شروع بازی" وابسته به "باز کردن بازی" است
        - برای "کپی"، مرحله "پیوند" وابسته به "رفتن به مقصد" است
        """
        for i, step in enumerate(steps):
            # قوانین وابستگی
            if step.step_type == StepType.INTERACT and i > 0:
                # INTERACT معمولاً وابسته به مرحله قبلی است
                prev_step = steps[i - 1]
                if prev_step.step_type in (StepType.OPEN, StepType.WAIT):
                    step.dependencies.append(prev_step.step_id)
            
            elif step.step_type == StepType.VERIFY and i > 0:
                # VERIFY وابسته به آخرین INTERACT است
                interact_steps = [
                    s.step_id for s in steps[:i]
                    if s.step_type == StepType.INTERACT
                ]
                if interact_steps:
                    step.dependencies = interact_steps
            
            elif step.step_type == StepType.SAVE and i > 0:
                # SAVE وابسته به PROCESS است
                process_steps = [
                    s.step_id for s in steps[:i]
                    if s.step_type == StepType.PROCESS
                ]
                if process_steps:
                    step.dependencies = process_steps
        
        return steps
    
    def _order_steps(self, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        """ترتیب‌بندی مراحل بر اساس وابستگی‌ها
        
        استفاده از Topological Sort برای تعیین ترتیب صحیح
        """
        ordered = []
        processed = set()
        
        while len(ordered) < len(steps):
            # پیدا کردن مراحلی که تمام وابستگی‌های آن‌ها حل شده
            for step in steps:
                if step.step_id in processed:
                    continue
                
                # بررسی اینکه تمام وابستگی‌ها حل شده‌اند
                if all(dep in processed for dep in step.dependencies):
                    step.order = len(ordered) + 1
                    ordered.append(step)
                    processed.add(step.step_id)
                    break
        
        return ordered
    
    def _enhance_steps(
        self,
        steps: List[ExecutionStep],
        intent: Intent
    ) -> List[ExecutionStep]:
        """بهبود مراحل با اضافه کردن timeout، retry، و fallback"""
        for step in steps:
            # timeout بر اساس نوع مرحله
            if step.timeout == 30:  # پیش‌فرض
                step.timeout = self._estimate_timeout(step.step_type)
            
            # retry برای مراحل مهم
            if step.step_type in (StepType.OPEN, StepType.ACQUIRE):
                step.retries = 3
            elif step.step_type == StepType.VERIFY:
                step.retries = 5  # بیشتر برای تایید
            
            # fallback برای مراحل خطرناک
            if "حذف" in step.action or "delete" in step.action_en:
                step.fallback_action = "لغو عملیات"
        
        return steps
    
    def _optimize_plan(
        self,
        steps: List[ExecutionStep],
        intent: Intent
    ) -> List[ExecutionStep]:
        """بهینه‌سازی پلان برای سرعت و کارایی
        
        - حذف مراحل اضافی
        - تجمیع مراحل
        - فعال‌سازی اجرای موازی
        """
        optimized = []
        
        for i, step in enumerate(steps):
            # بررسی اینکه آیا این مرحله می‌تواند با مرحله قبل ترکیب شود
            can_merge = (
                i > 0 and
                step.step_type in (StepType.INTERACT, StepType.WAIT) and
                optimized[-1].step_type in (StepType.OPEN, StepType.INTERACT)
            )
            
            if can_merge and len(optimized[-1].action) < 100:
                # ترکیب مراحل
                optimized[-1].action += f"; {step.action}"
                optimized[-1].action_en += f"; {step.action_en}"
            else:
                # اضافه کردن مرحله جدید
                optimized.append(step)
        
        # بروزرسانی ترتیب
        for i, step in enumerate(optimized, 1):
            step.order = i
        
        return optimized
    
    def _calculate_complexity(self, steps: List[ExecutionStep]) -> str:
        """محاسبه پیچیدگی پلان"""
        num_steps = len(steps)
        has_parallel = any(s.execution_mode == ExecutionMode.PARALLEL for s in steps)
        has_conditional = any(s.execution_mode == ExecutionMode.CONDITIONAL for s in steps)
        
        if num_steps <= 3 and not (has_parallel or has_conditional):
            return "SIMPLE"
        elif num_steps <= 7:
            return "MEDIUM"
        else:
            return "COMPLEX"
    
    def _estimate_timeout(self, step_type: StepType) -> int:
        """تخمین timeout برای نوع مرحله"""
        timeouts = {
            StepType.OPEN: 15,
            StepType.ACQUIRE: 20,
            StepType.INTERACT: 5,
            StepType.PROCESS: 10,
            StepType.SAVE: 5,
            StepType.VERIFY: 10,
            StepType.WAIT: 5,
            StepType.CLEANUP: 3
        }
        return timeouts.get(step_type, 10)
    
    def _format_action(self, template: str, intent: Intent) -> str:
        """فرمت‌بندی متن عمل با پارامترهای Intent"""
        action = template
        action = action.replace("{target}", intent.target)
        action = action.replace("{verb}", intent.verb)
        
        for key, value in intent.parameters.items():
            action = action.replace(f"{{{key}}}", str(value))
        
        return action
    
    def _translate_action(self, text: str, intent: Intent, language: str) -> str:
        """ترجمه متن عمل (شبیه‌سازی)"""
        # در نسخه واقعی، از AI استفاده می‌شود
        translations = {
            "باز کردن": "Opening" if language == "en" else "باز کردن",
            "انتظار": "Waiting" if language == "en" else "انتظار",
            "شروع": "Starting" if language == "en" else "شروع",
            "پیدا کردن": "Finding" if language == "en" else "پیدا کردن",
            "ایجاد": "Creating" if language == "en" else "ایجاد",
            "کپی": "Copying" if language == "en" else "کپی",
            "پیوند": "Paste" if language == "en" else "پیوند",
            "جستجو": "Searching" if language == "en" else "جستجو",
            "نصب": "Installing" if language == "en" else "نصب"
        }
        
        result = text
        for fa, en in translations.items():
            if fa in text and language == "en":
                result = result.replace(fa, en)
        
        return result
    
    def _generate_description(
        self,
        intent: Intent,
        steps: List[ExecutionStep]
    ) -> str:
        """تولید توضیح برای پلان"""
        return (
            f"برنامه برای {intent.verb} {intent.target} "
            f"با {len(steps)} مرحله. "
            f"تخمین زمان: {sum(s.timeout for s in steps)} ثانیه. "
            f"درخواست اصلی: {intent.raw_request}"
        )
    
    async def validate_plan(self, plan: ExecutionPlan) -> Tuple[bool, List[str]]:
        """تایید صحت پلان
        
        Returns:
            (is_valid, list_of_warnings)
        """
        warnings = []
        
        # بررسی وجود حداقل یک مرحله
        if not plan.steps:
            return False, ["پلان بدون مرحله است"]
        
        # بررسی ترتیب
        for i, step in enumerate(plan.get_sequential_order(), 1):
            if step.order != i:
                warnings.append(f"ترتیب مرحله {step.step_id} غلط است")
        
        # بررسی وابستگی‌ها
        step_ids = {s.step_id for s in plan.steps}
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    warnings.append(f"وابستگی {dep} برای مرحله {step.step_id} وجود ندارد")
        
        # بررسی عدم وجود دور
        if self._has_circular_dependency(plan.steps):
            return False, ["وابستگی دوری تشخیص داده شد"]
        
        return True, warnings
    
    def _has_circular_dependency(self, steps: List[ExecutionStep]) -> bool:
        """بررسی عدم وجود وابستگی دوری"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = next((s for s in steps if s.step_id == step_id), None)
            if step:
                for dep in step.dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        for step in steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id):
                    return True
        
        return False
