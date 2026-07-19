# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Plan Validator - بررسی صحت و امنیت پلان اجرایی

این ماژول مسئول تایید صحت پلان‌های ایجاد شده توسط Plan Generator است و اطمینان حاصل می‌کند
که تمام مراحل:
- آرمان‌شناسانه معتبر هستند (وابستگی‌ها درست هستند)
- امن هستند (هیچ عملیات خطرناک نیست)
- اجرا‌پذیر هستند (تمام منابع موجود هستند)
- بهینه هستند (کارایی بالا)
"""

from dataclasses import dataclass, field
from typing import Optional, Any, List
from enum import Enum
from datetime import datetime
import logging

from core.plan_generator import ExecutionPlan, ExecutionStep, StepType
from core.intent_analyzer import Intent


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes and Enums
# ═══════════════════════════════════════════════════════════════════════════════

class ValidationLevel(Enum):
    """سطح‌های اعتبارسنجی"""
    BASIC = "basic"           # بررسی پایه‌ای (ساختار و وابستگی)
    STRICT = "strict"         # بررسی دقیق (نیاز به منابع و امنیت)
    PARANOID = "paranoid"     # بررسی کامل (تمام جزئیات)


class ValidationStatus(Enum):
    """وضعیت اعتبارسنجی"""
    VALID = "valid"           # معتبر
    WARNING = "warning"       # هشدار (قابل اجرا اما توصیه می‌شود)
    ERROR = "error"           # خطا (نمی‌شود اجرا کرد)
    CRITICAL = "critical"     # بحرانی (خطر امنیتی)


class RiskLevel(Enum):
    """سطح‌های ریسک"""
    LOW = "low"               # ریسک کم
    MEDIUM = "medium"         # ریسک متوسط
    HIGH = "high"             # ریسک بالا
    CRITICAL = "critical"     # خطر حیات


@dataclass
class ValidationIssue:
    """یک مشکل در اعتبارسنجی"""
    issue_type: str            # نوع مشکل
    severity: ValidationStatus # شدت مشکل
    message_fa: str            # پیغام فارسی
    message_en: str            # پیغام انگلیسی
    step_id: Optional[str] = None  # شناسه مرحله اگر مربوط به مرحله خاصی باشد
    recommendation_fa: Optional[str] = None  # توصیه اصلاح
    recommendation_en: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW

    def to_dict(self) -> dict:
        """تبدیل به دیکشنری"""
        return {
            "type": self.issue_type,
            "severity": self.severity.value,
            "message": self.message_fa,
            "message_en": self.message_en,
            "step_id": self.step_id,
            "recommendation": self.recommendation_fa,
            "risk_level": self.risk_level.value
        }


@dataclass
class ValidationReport:
    """گزارش کامل اعتبارسنجی"""
    plan_id: str
    is_valid: bool
    status: ValidationStatus
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    # آمار و معیارها
    total_issues: int = 0
    total_critical: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    
    # معیارهای کیفی
    safety_score: float = 100.0  # 0-100 (امنیت)
    reliability_score: float = 100.0  # 0-100 (قابلیت اطمینان)
    efficiency_score: float = 100.0  # 0-100 (کارایی)
    
    created_at: datetime = field(default_factory=datetime.now)
    validation_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """تبدیل به دیکشنری"""
        return {
            "plan_id": self.plan_id,
            "is_valid": self.is_valid,
            "status": self.status.value,
            "issues": [issue.to_dict() for issue in self.issues],
            "total_issues": self.total_issues,
            "total_critical": self.total_critical,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "safety_score": self.safety_score,
            "reliability_score": self.reliability_score,
            "efficiency_score": self.efficiency_score
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Plan Validator Class
# ═══════════════════════════════════════════════════════════════════════════════

class PlanValidator:
    """
    بررسی صحت پلان‌های اجرایی
    
    مسئولیت‌های اصلی:
    1. بررسی ساختار - وابستگی‌ها، ترتیب، پیکربندی
    2. بررسی امنیت - هیچ عمل خطرناک نیست
    3. بررسی اجرا‌پذیری - منابع موجود هستند
    4. بررسی بهینگی - کدام مرحله‌ها را می‌توان بهبود داد
    """

    def __init__(self, ai_brain: Optional[Any] = None):
        """سازنده Plan Validator"""
        self.ai_brain = ai_brain
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    async def validate(
        self,
        plan: ExecutionPlan,
        intent: Intent,
        level: ValidationLevel = ValidationLevel.STRICT,
        check_resources: bool = True,
        check_security: bool = True
    ) -> ValidationReport:
        """
        اعتبارسنجی کامل یک پلان
        
        پارامترها:
        - plan: پلان برای بررسی
        - intent: Intent اصلی
        - level: سطح بررسی
        - check_resources: بررسی دسترسی به منابع
        - check_security: بررسی امنیت
        
        بازگشت: گزارش اعتبارسنجی
        """
        import time
        start_time = time.time()

        report = ValidationReport(
            plan_id=plan.plan_id,
            is_valid=True,
            status=ValidationStatus.VALID
        )

        # بررسی‌های اساسی
        await self._validate_structure(plan, report)
        
        # بررسی وابستگی‌ها
        await self._validate_dependencies(plan, report)
        
        # بررسی مراحل
        await self._validate_steps(plan, report)
        
        # بررسی امنیت اگر فعال باشد
        if check_security:
            await self._validate_security(plan, report)
        
        # بررسی منابع اگر فعال باشد
        if check_resources and level in (ValidationLevel.STRICT, ValidationLevel.PARANOID):
            await self._validate_resources(plan, report)
        
        # بررسی بهینگی
        await self._validate_optimization(plan, report)
        
        # محاسبه امتیازها
        self._calculate_scores(report)
        
        # تعیین وضعیت نهایی
        self._finalize_status(report)
        
        report.validation_time_ms = (time.time() - start_time) * 1000
        return report

    async def _validate_structure(self, plan: ExecutionPlan, report: ValidationReport) -> None:
        """بررسی ساختار پلان"""
        
        # بررسی خالی نبودن پلان
        if not plan.steps:
            report.issues.append(ValidationIssue(
                issue_type="empty_plan",
                severity=ValidationStatus.ERROR,
                message_fa="پلان هیچ مرحله‌ای ندارد",
                message_en="Plan has no steps",
                risk_level=RiskLevel.HIGH
            ))
            return

        # بررسی شناسه‌های منحصر
        step_ids = set()
        for step in plan.steps:
            if step.step_id in step_ids:
                report.issues.append(ValidationIssue(
                    issue_type="duplicate_step_id",
                    severity=ValidationStatus.ERROR,
                    message_fa=f"شناسه مرحله تکراری: {step.step_id}",
                    message_en=f"Duplicate step ID: {step.step_id}",
                    step_id=step.step_id,
                    risk_level=RiskLevel.MEDIUM
                ))
            step_ids.add(step.step_id)

        # بررسی ترتیب مراحل
        for i, step in enumerate(plan.steps):
            if step.order != i + 1:
                report.issues.append(ValidationIssue(
                    issue_type="incorrect_order",
                    severity=ValidationStatus.WARNING,
                    message_fa=f"ترتیب مرحله‌ها صحیح نیست: انتظار {i+1}، حاصل {step.order}",
                    message_en=f"Step order incorrect: expected {i+1}, got {step.order}",
                    step_id=step.step_id,
                    recommendation_fa="ترتیب مراحل را دوباره محاسبه کنید",
                    recommendation_en="Recalculate step ordering",
                    risk_level=RiskLevel.LOW
                ))

    async def _validate_dependencies(self, plan: ExecutionPlan, report: ValidationReport) -> None:
        """بررسی وابستگی‌ها"""
        
        step_ids = {step.step_id for step in plan.steps}
        
        for step in plan.steps:
            # بررسی وجود وابستگی‌های مشروع
            for dep_id in step.dependencies:
                if dep_id not in step_ids:
                    report.issues.append(ValidationIssue(
                        issue_type="missing_dependency",
                        severity=ValidationStatus.ERROR,
                        message_fa=f"وابستگی ناموجود: {dep_id}",
                        message_en=f"Missing dependency: {dep_id}",
                        step_id=step.step_id,
                        risk_level=RiskLevel.HIGH
                    ))
        
        # بررسی وابستگی‌های دوری
        if self._has_circular_dependency(plan.steps):
            report.issues.append(ValidationIssue(
                issue_type="circular_dependency",
                severity=ValidationStatus.ERROR,
                message_fa="وابستگی دوری در پلان وجود دارد",
                message_en="Circular dependency detected in plan",
                recommendation_fa="پلان را دوباره تولید کنید",
                recommendation_en="Regenerate the plan",
                risk_level=RiskLevel.CRITICAL
            ))
        
        # بررسی وابستگی‌های منطقی
        for step in plan.steps:
            # INTERACT باید بعد از OPEN باشد
            if step.step_type == StepType.INTERACT:
                has_open_dependency = any(
                    s.step_id in step.dependencies
                    for s in plan.steps
                    if s.step_type == StepType.OPEN
                )
                if not has_open_dependency and not any(
                    s.step_type == StepType.OPEN for s in plan.steps
                ):
                    report.issues.append(ValidationIssue(
                        issue_type="missing_logical_dependency",
                        severity=ValidationStatus.WARNING,
                        message_fa="INTERACT بدون OPEN قبلی",
                        message_en="INTERACT without prior OPEN",
                        step_id=step.step_id,
                        recommendation_fa="یک مرحله OPEN اضافه کنید",
                        recommendation_en="Add an OPEN step",
                        risk_level=RiskLevel.MEDIUM
                    ))

    async def _validate_steps(self, plan: ExecutionPlan, report: ValidationReport) -> None:
        """بررسی خود مراحل"""
        
        for step in plan.steps:
            # بررسی متن اقدام
            if not step.action or len(step.action.strip()) == 0:
                report.issues.append(ValidationIssue(
                    issue_type="empty_action",
                    severity=ValidationStatus.ERROR,
                    message_fa="متن اقدام خالی است",
                    message_en="Action text is empty",
                    step_id=step.step_id,
                    risk_level=RiskLevel.MEDIUM
                ))
            
            # بررسی timeout معقول
            if step.timeout <= 0:
                report.issues.append(ValidationIssue(
                    issue_type="invalid_timeout",
                    severity=ValidationStatus.ERROR,
                    message_fa=f"Timeout نامعتبر: {step.timeout}",
                    message_en=f"Invalid timeout: {step.timeout}",
                    step_id=step.step_id,
                    risk_level=RiskLevel.MEDIUM
                ))
            elif step.timeout > 300:  # 5 دقیقه
                report.issues.append(ValidationIssue(
                    issue_type="excessive_timeout",
                    severity=ValidationStatus.WARNING,
                    message_fa=f"Timeout بسیار بالا: {step.timeout}s",
                    message_en=f"Very high timeout: {step.timeout}s",
                    step_id=step.step_id,
                    recommendation_fa="مقدار timeout را کاهش دهید",
                    recommendation_en="Reduce timeout value",
                    risk_level=RiskLevel.LOW
                ))
            
            # بررسی retry معقول
            if step.retries > 10:
                report.issues.append(ValidationIssue(
                    issue_type="excessive_retries",
                    severity=ValidationStatus.WARNING,
                    message_fa=f"تعداد تلاش‌های مجدد زیاد: {step.retries}",
                    message_en=f"Excessive retries: {step.retries}",
                    step_id=step.step_id,
                    recommendation_fa="تعداد تلاش‌های مجدد را کاهش دهید",
                    recommendation_en="Reduce retry attempts",
                    risk_level=RiskLevel.LOW
                ))
            
            # بررسی priority معقول
            if not (1 <= step.priority <= 10):
                report.issues.append(ValidationIssue(
                    issue_type="invalid_priority",
                    severity=ValidationStatus.WARNING,
                    message_fa=f"اولویت نامعتبر: {step.priority}",
                    message_en=f"Invalid priority: {step.priority}",
                    step_id=step.step_id,
                    risk_level=RiskLevel.LOW
                ))

    async def _validate_security(self, plan: ExecutionPlan, report: ValidationReport) -> None:
        """بررسی امنیت"""
        
        dangerous_keywords = {
            "delete": "حذف",
            "rm -rf": "حذف بازگشتی",
            "format": "فرمت کردن",
            "system32": "سیستم32",
            "registry": "رجیستری",
            "/system": "پوشه سیستم"
        }
        
        for step in plan.steps:
            action_lower = (step.action or "").lower()
            
            for keyword, desc in dangerous_keywords.items():
                if keyword in action_lower:
                    report.issues.append(ValidationIssue(
                        issue_type="dangerous_operation",
                        severity=ValidationStatus.ERROR,
                        message_fa=f"عملیات خطرناک: {desc}",
                        message_en=f"Dangerous operation: {keyword}",
                        step_id=step.step_id,
                        recommendation_fa="این عملیات نیاز به تأیید اضافی دارد",
                        recommendation_en="This operation requires additional confirmation",
                        risk_level=RiskLevel.CRITICAL
                    ))
        
        # بررسی سیستم فایل‌های حساس
        sensitive_paths = {
            r"C:\\Windows": "Windows System",
            r"C:\\Program Files": "Program Files",
            r"HKEY_LOCAL_MACHINE": "Registry",
        }
        
        for step in plan.steps:
            target = (step.target or "").upper()
            for path, desc in sensitive_paths.items():
                if path.upper() in target:
                    report.issues.append(ValidationIssue(
                        issue_type="sensitive_path",
                        severity=ValidationStatus.WARNING,
                        message_fa=f"مسیر حساس: {desc}",
                        message_en=f"Sensitive path: {desc}",
                        step_id=step.step_id,
                        recommendation_fa="مطمئن شوید که این عملیات امن است",
                        recommendation_en="Ensure this operation is safe",
                        risk_level=RiskLevel.HIGH
                    ))

    async def _validate_resources(self, plan: ExecutionPlan, report: ValidationReport) -> None:
        """بررسی دسترسی به منابع"""
        
        # بررسی برنامه‌های مورد نیاز
        required_programs = set()
        for step in plan.steps:
            if step.step_type == StepType.OPEN:
                # استخراج نام برنامه از action
                required_programs.add(step.target or "unknown")
        
        # در محیط واقعی این‌جا باید از WMI یا Registry استفاده کنید
        # فعلاً فقط هشدار می‌دهیم
        if required_programs:
            report.suggestions.append(
                f"برنامه‌های مورد نیاز: {', '.join(required_programs)}"
            )

    async def _validate_optimization(self, plan: ExecutionPlan, report: ValidationReport) -> None:
        """بررسی بهینگی"""
        
        # بررسی فرصت‌های parallelization
        steps_without_deps = [s for s in plan.steps if not s.dependencies]
        if len(steps_without_deps) > 1:
            report.suggestions.append(
                f"می‌توان {len(steps_without_deps)} مرحله را موازی اجرا کرد"
            )
        
        # بررسی WAIT مراحل بیش‌از‌حد
        wait_steps = [s for s in plan.steps if s.step_type == StepType.WAIT]
        if len(wait_steps) > plan.total_estimated_time * 0.3:  # بیش‌از 30%
            report.suggestions.append(
                "تعداد WAIT مراحل زیاد است - می‌توان به هوش‌مندی بیشتری فکر کرد"
            )
        
        # بررسی complexity
        if plan.complexity == "COMPLEX":
            report.suggestions.append(
                "این پلان پیچیده است - تقسیم به زیر-پلان‌ها می‌تواند کمک کند"
            )

    def _has_circular_dependency(self, steps: List[ExecutionStep]) -> bool:
        """تشخیص وابستگی دوری"""
        step_map = {step.step_id: step for step in steps}
        visited = set()
        rec_stack = set()

        def has_cycle(step_id: str) -> bool:
            if step_id in rec_stack:
                return True
            if step_id in visited:
                return False

            visited.add(step_id)
            rec_stack.add(step_id)

            step = step_map.get(step_id)
            if step:
                for dep in step.dependencies:
                    if has_cycle(dep):
                        return True

            rec_stack.remove(step_id)
            return False

        for step in steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id):
                    return True

        return False

    def _calculate_scores(self, report: ValidationReport) -> None:
        """محاسبه امتیازهای کیفیت"""
        
        # امتیاز امنیت
        critical_issues = sum(1 for i in report.issues if i.risk_level == RiskLevel.CRITICAL)
        high_issues = sum(1 for i in report.issues if i.risk_level == RiskLevel.HIGH)
        report.safety_score = max(0, 100 - (critical_issues * 20 + high_issues * 10))
        
        # امتیاز قابلیت اطمینان
        error_issues = sum(1 for i in report.issues if i.severity == ValidationStatus.ERROR)
        warning_issues = sum(1 for i in report.issues if i.severity == ValidationStatus.WARNING)
        report.reliability_score = max(0, 100 - (error_issues * 15 + warning_issues * 5))
        
        # امتیاز کارایی
        # بر اساس تعداد پیشنهادات بهینگی
        report.efficiency_score = min(100, 100 - len(report.suggestions) * 5)

    def _finalize_status(self, report: ValidationReport) -> None:
        """تعیین وضعیت نهایی"""
        
        # شمارش مسائل
        report.total_issues = len(report.issues)
        report.total_critical = sum(1 for i in report.issues if i.severity == ValidationStatus.CRITICAL)
        report.total_errors = sum(1 for i in report.issues if i.severity == ValidationStatus.ERROR)
        report.total_warnings = sum(1 for i in report.issues if i.severity == ValidationStatus.WARNING)
        
        # تعیین وضعیت
        if report.total_critical > 0:
            report.status = ValidationStatus.CRITICAL
            report.is_valid = False
        elif report.total_errors > 0:
            report.status = ValidationStatus.ERROR
            report.is_valid = False
        elif report.total_warnings > 0:
            report.status = ValidationStatus.WARNING
            report.is_valid = True  # هشدار اما قابل اجرا
        else:
            report.status = ValidationStatus.VALID
            report.is_valid = True

    def get_validation_summary(self, report: ValidationReport) -> str:
        """خلاصه متنی اعتبارسنجی"""
        summary = []
        summary.append(f"\n{'='*60}")
        summary.append(f"📋 گزارش اعتبارسنجی پلان {report.plan_id}")
        summary.append(f"{'='*60}")
        
        # وضعیت کلی
        status_emoji = {
            ValidationStatus.VALID: "✅",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.ERROR: "❌",
            ValidationStatus.CRITICAL: "🚨"
        }
        summary.append(f"\nوضعیت: {status_emoji.get(report.status, '❓')} {report.status.value.upper()}")
        
        # امتیازها
        summary.append(f"\n📊 امتیازها:")
        summary.append(f"  🔒 امنیت: {report.safety_score:.1f}/100")
        summary.append(f"  🛡️ قابلیت اطمینان: {report.reliability_score:.1f}/100")
        summary.append(f"  ⚡ کارایی: {report.efficiency_score:.1f}/100")
        
        # مسائل
        if report.issues:
            summary.append(f"\n⚠️ مسائل ({report.total_issues}):")
            for issue in report.issues[:5]:  # نمایش ۵ مسئله اول
                summary.append(f"  • [{issue.severity.value}] {issue.message_fa}")
                if issue.recommendation_fa:
                    summary.append(f"    💡 {issue.recommendation_fa}")
            if len(report.issues) > 5:
                summary.append(f"  ... و {len(report.issues)-5} مسئله دیگر")
        
        # پیشنهادات
        if report.suggestions:
            summary.append(f"\n💡 پیشنهادات:")
            for suggestion in report.suggestions[:3]:
                summary.append(f"  • {suggestion}")
        
        summary.append(f"\n⏱️ زمان اعتبارسنجی: {report.validation_time_ms:.2f}ms")
        summary.append(f"{'='*60}\n")
        
        return "\n".join(summary)
