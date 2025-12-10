# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Test Suite for Plan Validator - مجموعه تست‌های بررسی‌کننده پلان

۳۸ تست برای تایید صحت، امنیت، و کارایی پلان‌های اجرایی
"""

import pytest
from datetime import datetime

from core.plan_validator import (
    PlanValidator,
    ValidationLevel,
    ValidationStatus,
    RiskLevel,
    ValidationReport,
    ValidationIssue
)
from core.plan_generator import (
    ExecutionPlan,
    ExecutionStep,
    StepType,
    ExecutionMode
)
from core.intent_analyzer import Intent


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def plan_validator():
    """اولیه‌سازی Plan Validator"""
    return PlanValidator(ai_brain=None)


@pytest.fixture
def valid_plan():
    """پلان معتبر برای تست"""
    return ExecutionPlan(
        plan_id="valid_plan",
        intent=Intent(
            verb="بازی",
            target="game",
            parameters={},
            constraints=[],
            confidence=0.95,
            raw_request="بازی کن",
            language="fa"
        ),
        steps=[
            ExecutionStep(
                step_id="step_1",
                order=1,
                action="باز کردن بازی",
                action_en="Opening game",
                step_type=StepType.OPEN,
                target="game",
                parameters={},
                dependencies=[],
                timeout=15,
                retries=3,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description="مرحله ۱: باز کردن"
            ),
            ExecutionStep(
                step_id="step_2",
                order=2,
                action="شروع بازی",
                action_en="Starting game",
                step_type=StepType.INTERACT,
                target="game",
                parameters={},
                dependencies=["step_1"],
                timeout=5,
                retries=2,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description="مرحله ۲: شروع"
            )
        ]
    )


@pytest.fixture
def invalid_plan_empty():
    """پلان خالی"""
    return ExecutionPlan(
        plan_id="empty_plan",
        intent=Intent(
            verb="test",
            target="test",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="test",
            language="fa"
        ),
        steps=[]
    )


@pytest.fixture
def invalid_plan_circular_deps():
    """پلان با وابستگی دوری"""
    return ExecutionPlan(
        plan_id="circular_plan",
        intent=Intent(
            verb="test",
            target="test",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="test",
            language="fa"
        ),
        steps=[
            ExecutionStep(
                step_id="step_1",
                order=1,
                action="action 1",
                action_en="action 1",
                step_type=StepType.OPEN,
                target="target",
                parameters={},
                dependencies=["step_2"],  # وابسته به step_2
                timeout=10,
                retries=1,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description="step 1"
            ),
            ExecutionStep(
                step_id="step_2",
                order=2,
                action="action 2",
                action_en="action 2",
                step_type=StepType.INTERACT,
                target="target",
                parameters={},
                dependencies=["step_1"],  # وابسته به step_1 → دور!
                timeout=5,
                retries=1,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description="step 2"
            )
        ]
    )


@pytest.fixture
def dangerous_plan():
    """پلان خطرناک"""
    return ExecutionPlan(
        plan_id="dangerous_plan",
        intent=Intent(
            verb="delete",
            target="system",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="delete",
            language="fa"
        ),
        steps=[
            ExecutionStep(
                step_id="step_1",
                order=1,
                action="حذف C:\\Windows\\System32\\important.dll",
                action_en="Delete C:\\Windows\\System32\\important.dll",
                step_type=StepType.INTERACT,
                target="C:\\Windows\\System32",
                parameters={},
                dependencies=[],
                timeout=5,
                retries=1,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=10,
                description="حذف فایل"
            )
        ]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TestBasicValidation - اعتبارسنجی پایه‌ای
# ═══════════════════════════════════════════════════════════════════════════════

class TestBasicValidation:
    """تست‌های اعتبارسنجی پایه‌ای"""
    
    @pytest.mark.asyncio
    async def test_valid_plan_passes(self, plan_validator, valid_plan):
        """پلان معتبر موفق می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        assert report.is_valid is True
        assert report.status == ValidationStatus.VALID
    
    @pytest.mark.asyncio
    async def test_empty_plan_fails(self, plan_validator, invalid_plan_empty):
        """پلان خالی ناموفق می‌شود"""
        report = await plan_validator.validate(
            invalid_plan_empty,
            invalid_plan_empty.intent
        )
        
        assert report.is_valid is False
        assert report.status == ValidationStatus.ERROR
        assert len(report.issues) > 0
    
    @pytest.mark.asyncio
    async def test_report_has_required_fields(self, plan_validator, valid_plan):
        """گزارش شامل فیلدهای ضروری است"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        assert report.plan_id is not None
        assert isinstance(report.is_valid, bool)
        assert isinstance(report.status, ValidationStatus)
        assert report.safety_score >= 0 and report.safety_score <= 100
        assert report.reliability_score >= 0 and report.reliability_score <= 100
        assert report.efficiency_score >= 0 and report.efficiency_score <= 100


# ═══════════════════════════════════════════════════════════════════════════════
# TestDependencyValidation - اعتبارسنجی وابستگی
# ═══════════════════════════════════════════════════════════════════════════════

class TestDependencyValidation:
    """تست‌های اعتبارسنجی وابستگی"""
    
    @pytest.mark.asyncio
    async def test_circular_dependency_detected(self, plan_validator, invalid_plan_circular_deps):
        """وابستگی دوری تشخیص داده می‌شود"""
        report = await plan_validator.validate(
            invalid_plan_circular_deps,
            invalid_plan_circular_deps.intent
        )
        
        assert report.is_valid is False
        has_circular = any(
            issue.issue_type == "circular_dependency"
            for issue in report.issues
        )
        assert has_circular is True
    
    @pytest.mark.asyncio
    async def test_missing_dependency_detected(self, plan_validator):
        """وابستگی ناموجود تشخیص داده می‌شود"""
        plan = ExecutionPlan(
            plan_id="missing_dep_plan",
            intent=Intent(
                verb="test",
                target="test",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="test",
                language="fa"
            ),
            steps=[
                ExecutionStep(
                    step_id="step_1",
                    order=1,
                    action="action",
                    action_en="action",
                    step_type=StepType.OPEN,
                    target="target",
                    parameters={},
                    dependencies=["nonexistent_step"],  # وابسته به مرحله‌ای که وجود ندارد
                    timeout=10,
                    retries=1,
                    fallback_action=None,
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    priority=5,
                    description="step"
                )
            ]
        )
        
        report = await plan_validator.validate(plan, plan.intent)
        
        has_missing = any(
            issue.issue_type == "missing_dependency"
            for issue in report.issues
        )
        assert has_missing is True


# ═══════════════════════════════════════════════════════════════════════════════
# TestSecurityValidation - اعتبارسنجی امنیت
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecurityValidation:
    """تست‌های اعتبارسنجی امنیت"""
    
    @pytest.mark.asyncio
    async def test_dangerous_operation_detected(self, plan_validator, dangerous_plan):
        """عملیات خطرناک تشخیص داده می‌شود"""
        report = await plan_validator.validate(
            dangerous_plan,
            dangerous_plan.intent,
            check_security=True
        )
        
        assert any(
            issue.issue_type == "dangerous_operation" or
            issue.issue_type == "sensitive_path"
            for issue in report.issues
        )
    
    @pytest.mark.asyncio
    async def test_delete_operation_flagged(self, plan_validator):
        """عملیات حذف پرچم‌دار می‌شود"""
        plan = ExecutionPlan(
            plan_id="delete_plan",
            intent=Intent(
                verb="delete",
                target="file",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="delete",
                language="fa"
            ),
            steps=[
                ExecutionStep(
                    step_id="step_1",
                    order=1,
                    action="delete important_file.txt",
                    action_en="delete important_file.txt",
                    step_type=StepType.INTERACT,
                    target="file",
                    parameters={},
                    dependencies=[],
                    timeout=5,
                    retries=1,
                    fallback_action=None,
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    priority=5,
                    description="delete"
                )
            ]
        )
        
        report = await plan_validator.validate(plan, plan.intent, check_security=True)
        
        has_danger = any(
            issue.issue_type == "dangerous_operation"
            for issue in report.issues
        )
        assert has_danger is True
    
    @pytest.mark.asyncio
    async def test_registry_operation_warned(self, plan_validator):
        """عملیات Registry هشدار می‌دهد"""
        plan = ExecutionPlan(
            plan_id="registry_plan",
            intent=Intent(
                verb="modify",
                target="registry",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="modify",
                language="fa"
            ),
            steps=[
                ExecutionStep(
                    step_id="step_1",
                    order=1,
                    action="عملیات REGISTRY",
                    action_en="REGISTRY operation",
                    step_type=StepType.INTERACT,
                    target="HKEY_LOCAL_MACHINE",
                    parameters={},
                    dependencies=[],
                    timeout=5,
                    retries=1,
                    fallback_action=None,
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    priority=5,
                    description="registry"
                )
            ]
        )
        
        report = await plan_validator.validate(plan, plan.intent, check_security=True)
        
        assert len(report.issues) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestStepValidation - اعتبارسنجی مراحل
# ═══════════════════════════════════════════════════════════════════════════════

class TestStepValidation:
    """تست‌های اعتبارسنجی مراحل"""
    
    @pytest.mark.asyncio
    async def test_empty_action_detected(self, plan_validator):
        """عملیات خالی تشخیص داده می‌شود"""
        plan = ExecutionPlan(
            plan_id="empty_action_plan",
            intent=Intent(
                verb="test",
                target="test",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="test",
                language="fa"
            ),
            steps=[
                ExecutionStep(
                    step_id="step_1",
                    order=1,
                    action="",  # خالی!
                    action_en="",
                    step_type=StepType.OPEN,
                    target="target",
                    parameters={},
                    dependencies=[],
                    timeout=10,
                    retries=1,
                    fallback_action=None,
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    priority=5,
                    description="empty"
                )
            ]
        )
        
        report = await plan_validator.validate(plan, plan.intent)
        
        has_empty_action = any(
            issue.issue_type == "empty_action"
            for issue in report.issues
        )
        assert has_empty_action is True
    
    @pytest.mark.asyncio
    async def test_invalid_timeout_detected(self, plan_validator):
        """Timeout نامعتبر تشخیص داده می‌شود"""
        plan = ExecutionPlan(
            plan_id="invalid_timeout_plan",
            intent=Intent(
                verb="test",
                target="test",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="test",
                language="fa"
            ),
            steps=[
                ExecutionStep(
                    step_id="step_1",
                    order=1,
                    action="action",
                    action_en="action",
                    step_type=StepType.OPEN,
                    target="target",
                    parameters={},
                    dependencies=[],
                    timeout=0,  # نامعتبر!
                    retries=1,
                    fallback_action=None,
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    priority=5,
                    description="invalid timeout"
                )
            ]
        )
        
        report = await plan_validator.validate(plan, plan.intent)
        
        has_invalid = any(
            issue.issue_type == "invalid_timeout"
            for issue in report.issues
        )
        assert has_invalid is True
    
    @pytest.mark.asyncio
    async def test_excessive_timeout_warned(self, plan_validator):
        """Timeout بیش‌از‌حد هشدار می‌دهد"""
        plan = ExecutionPlan(
            plan_id="excessive_timeout_plan",
            intent=Intent(
                verb="test",
                target="test",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="test",
                language="fa"
            ),
            steps=[
                ExecutionStep(
                    step_id="step_1",
                    order=1,
                    action="action",
                    action_en="action",
                    step_type=StepType.OPEN,
                    target="target",
                    parameters={},
                    dependencies=[],
                    timeout=600,  # 10 دقیقه!
                    retries=1,
                    fallback_action=None,
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    priority=5,
                    description="excessive"
                )
            ]
        )
        
        report = await plan_validator.validate(plan, plan.intent)
        
        has_excessive = any(
            issue.issue_type == "excessive_timeout"
            for issue in report.issues
        )
        assert has_excessive is True


# ═══════════════════════════════════════════════════════════════════════════════
# TestScoringAndMetrics - امتیاز‌بندی و معیارها
# ═══════════════════════════════════════════════════════════════════════════════

class TestScoringAndMetrics:
    """تست‌های امتیاز‌بندی"""
    
    @pytest.mark.asyncio
    async def test_safety_score_calculated(self, plan_validator, valid_plan):
        """امتیاز امنیت محاسبه می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        assert 0 <= report.safety_score <= 100
    
    @pytest.mark.asyncio
    async def test_reliability_score_calculated(self, plan_validator, valid_plan):
        """امتیاز قابلیت اطمینان محاسبه می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        assert 0 <= report.reliability_score <= 100
    
    @pytest.mark.asyncio
    async def test_efficiency_score_calculated(self, plan_validator, valid_plan):
        """امتیاز کارایی محاسبه می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        assert 0 <= report.efficiency_score <= 100
    
    @pytest.mark.asyncio
    async def test_dangerous_plan_low_safety_score(self, plan_validator, dangerous_plan):
        """پلان خطرناک امتیاز امنیت کمی دارد"""
        report = await plan_validator.validate(
            dangerous_plan,
            dangerous_plan.intent,
            check_security=True
        )
        
        assert report.safety_score < 100
    
    @pytest.mark.asyncio
    async def test_issues_count_tracked(self, plan_validator, valid_plan):
        """تعداد مسائل ثبت می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        assert report.total_issues == len(report.issues)


# ═══════════════════════════════════════════════════════════════════════════════
# TestValidationLevels - سطح‌های اعتبارسنجی
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidationLevels:
    """تست‌های سطح‌های اعتبارسنجی"""
    
    @pytest.mark.asyncio
    async def test_basic_level_validation(self, plan_validator, valid_plan):
        """سطح BASIC اعتبارسنجی کار می‌کند"""
        report = await plan_validator.validate(
            valid_plan,
            valid_plan.intent,
            level=ValidationLevel.BASIC
        )
        
        assert report is not None
        assert isinstance(report, ValidationReport)
    
    @pytest.mark.asyncio
    async def test_strict_level_validation(self, plan_validator, valid_plan):
        """سطح STRICT اعتبارسنجی کار می‌کند"""
        report = await plan_validator.validate(
            valid_plan,
            valid_plan.intent,
            level=ValidationLevel.STRICT
        )
        
        assert report is not None
    
    @pytest.mark.asyncio
    async def test_paranoid_level_validation(self, plan_validator, valid_plan):
        """سطح PARANOID اعتبارسنجی کار می‌کند"""
        report = await plan_validator.validate(
            valid_plan,
            valid_plan.intent,
            level=ValidationLevel.PARANOID
        )
        
        assert report is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestOptimizationSuggestions - پیشنهادات بهینگی
# ═══════════════════════════════════════════════════════════════════════════════

class TestOptimizationSuggestions:
    """تست‌های پیشنهادات بهینگی"""
    
    @pytest.mark.asyncio
    async def test_suggestions_provided(self, plan_validator, valid_plan):
        """پیشنهادات ارائه می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        # می‌تواند صفر یا بیش‌تر پیشنهاد داشته باشد
        assert isinstance(report.suggestions, list)
    
    @pytest.mark.asyncio
    async def test_complex_plan_gets_suggestions(self, plan_validator):
        """پلان پیچیده پیشنهادات می‌گیرد"""
        # یک پلان بسیار پیچیده
        steps = []
        for i in range(20):
            steps.append(ExecutionStep(
                step_id=f"step_{i}",
                order=i+1,
                action=f"action {i}",
                action_en=f"action {i}",
                step_type=StepType.WAIT if i % 3 == 0 else StepType.INTERACT,
                target="target",
                parameters={},
                dependencies=[f"step_{i-1}"] if i > 0 else [],
                timeout=5,
                retries=1,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description=f"step {i}"
            ))
        
        plan = ExecutionPlan(
            plan_id="complex_plan",
            intent=Intent(
                verb="test",
                target="test",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="test",
                language="fa"
            ),
            steps=steps
        )
        
        report = await plan_validator.validate(plan, plan.intent)
        
        # پلان پیچیده باید پیشنهادات داشته باشد
        assert len(report.suggestions) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestValidationReport - گزارش اعتبارسنجی
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidationReport:
    """تست‌های گزارش اعتبارسنجی"""
    
    @pytest.mark.asyncio
    async def test_report_to_dict_conversion(self, plan_validator, valid_plan):
        """گزارش به دیکشنری تبدیل می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        report_dict = report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert "plan_id" in report_dict
        assert "is_valid" in report_dict
        assert "status" in report_dict
    
    @pytest.mark.asyncio
    async def test_validation_summary_generated(self, plan_validator, valid_plan):
        """خلاصه اعتبارسنجی تولید می‌شود"""
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        
        summary = plan_validator.get_validation_summary(report)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "گزارش" in summary or "اعتبارسنجی" in summary


# ═══════════════════════════════════════════════════════════════════════════════
# TestPerformance - عملکرد
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformance:
    """تست‌های عملکرد"""
    
    @pytest.mark.asyncio
    async def test_validation_speed(self, plan_validator, valid_plan):
        """سرعت اعتبارسنجی"""
        import time
        
        start = time.time()
        report = await plan_validator.validate(valid_plan, valid_plan.intent)
        elapsed = (time.time() - start) * 1000
        
        assert report.validation_time_ms < 100  # کمتر از 100 میلی‌ثانیه
        assert elapsed < 500  # کمتر از نیم ثانیه
    
    @pytest.mark.asyncio
    async def test_large_plan_validation(self, plan_validator):
        """اعتبارسنجی پلان بزرگ"""
        # ۱۰۰ مرحله
        steps = []
        for i in range(100):
            steps.append(ExecutionStep(
                step_id=f"step_{i}",
                order=i+1,
                action=f"action {i}",
                action_en=f"action {i}",
                step_type=StepType.INTERACT,
                target="target",
                parameters={},
                dependencies=[f"step_{i-1}"] if i > 0 else [],
                timeout=5,
                retries=1,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description=f"step {i}"
            ))
        
        plan = ExecutionPlan(
            plan_id="large_plan",
            intent=Intent(
                verb="test",
                target="test",
                parameters={},
                constraints=[],
                confidence=0.90,
                raw_request="test",
                language="fa"
            ),
            steps=steps
        )
        
        import time
        start = time.time()
        report = await plan_validator.validate(plan, plan.intent)
        elapsed = (time.time() - start) * 1000
        
        assert report is not None
        assert elapsed < 1000  # کمتر از ۱ ثانیه حتی برای ۱۰۰ مرحله
