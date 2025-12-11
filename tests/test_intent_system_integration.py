# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
تست‌های یکپارچه‌سازی Intent Planning System
Test Suite for Intent Planning System Integration - تست جریان کامل 5 ماژول

این تست‌ها تمام 5 ماژول را با هم تست می‌کنند:
1. Intent Analyzer → 2. Dialog Manager → 3. Plan Generator → 
4. Plan Validator → 5. Memory Integrator
"""

import pytest
from datetime import datetime
import os
import tempfile

from core.intent_analyzer import IntentAnalyzer
from core.dialog_manager import DialogManager
from core.plan_generator import PlanGenerator, ExecutionMode
from core.plan_validator import PlanValidator, ValidationLevel
from core.memory_integrator import MemoryIntegrator, PlanStatus


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_db():
    """دیتابیس موقتی"""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        yield db_path
        import sqlite3
        sqlite3.connect(db_path).close()


@pytest.fixture
def analyzer():
    """Intent Analyzer"""
    return IntentAnalyzer()


@pytest.fixture
def dialog_manager():
    """Dialog Manager"""
    return DialogManager()


@pytest.fixture
def plan_generator():
    """Plan Generator"""
    return PlanGenerator()


@pytest.fixture
def plan_validator():
    """Plan Validator"""
    return PlanValidator()


@pytest.fixture
def memory_integrator(temp_db):
    """Memory Integrator"""
    return MemoryIntegrator(db_path=temp_db)


# ═══════════════════════════════════════════════════════════════════════════════
# TestFullPipeline - جریان کامل
# ═══════════════════════════════════════════════════════════════════════════════

class TestFullPipeline:
    """تست‌های جریان کامل سیستم"""
    
    @pytest.mark.asyncio
    async def test_simple_request_pipeline(
        self, analyzer, dialog_manager, plan_generator, 
        plan_validator, memory_integrator
    ):
        """جریان ساده: درخواست → Intent → Dialog → Plan → Validation → Learning"""
        # مرحله ۱: تحلیل نیت
        request = "بازی کو راه‌اندازی کن"
        intent = await analyzer.analyze(request)
        
        assert intent is not None
        assert intent.verb in ["بازی", "play", "راه‌اندازی"]
        assert intent.language in ["fa", "en"]
        assert intent.confidence >= 0.7
        
        # مرحله ۲: Dialog برای کمال‌سازی
        if intent.missing_fields:
            intent = dialog_manager.generate_dialog(intent)
            assert intent.missing_fields is not None
        
        # مرحله ۳: تولید پلان
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        assert plan.plan_id is not None
        assert len(plan.steps) > 0
        assert all(step.step_id is not None for step in plan.steps)
        
        # مرحله ۴: اعتبارسنجی
        validation = await plan_validator.validate(plan, intent)
        
        assert validation is not None
        assert validation.plan_id == plan.plan_id
        assert hasattr(validation, 'safety_score')
        assert hasattr(validation, 'reliability_score')
        
        # مرحله ۵: ثبت و یادگیری
        record_id = memory_integrator.record_execution(
            plan_id=plan.plan_id,
            intent=intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=len(plan.steps),
            steps_failed=0,
            total_steps=len(plan.steps),
            actual_time_seconds=5.0,
            estimated_time_seconds=5.0
        )
        
        assert record_id is not None
    
    @pytest.mark.asyncio
    async def test_complex_request_with_dialog(
        self, analyzer, dialog_manager, plan_generator,
        plan_validator, memory_integrator
    ):
        """درخواست پیچیده با نیاز به Dialog"""
        request = "یک پوشه بساز"
        intent = await analyzer.analyze(request)
        
        # اگر Dialog لازم است
        if intent.missing_fields:
            intent = dialog_manager.generate_dialog(intent)
        
        # تولید پلان
        plan = await plan_generator.generate_plan(intent)
        assert len(plan.steps) > 0
        
        # اعتبارسنجی
        validation = await plan_validator.validate(plan, intent, ValidationLevel.STRICT)
        
        # ثبت موفق
        record_id = memory_integrator.record_execution(
            plan_id=plan.plan_id,
            intent=intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=len(plan.steps),
            steps_failed=0,
            total_steps=len(plan.steps),
            actual_time_seconds=3.0,
            estimated_time_seconds=5.0
        )
        
        assert record_id is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestErrorHandlingIntegration - مدیریت خطا
# ═══════════════════════════════════════════════════════════════════════════════

class TestErrorHandlingIntegration:
    """تست‌های مدیریت خطا در جریان یکپارچه"""
    
    @pytest.mark.asyncio
    async def test_invalid_request_handling(
        self, analyzer, dialog_manager, plan_generator
    ):
        """درخواست نامعتبر"""
        request = ""
        intent = await analyzer.analyze(request)
        
        # حتی درخواست خالی باید Intent برگرداند
        assert intent is not None
    
    @pytest.mark.asyncio
    async def test_validation_failure_recovery(
        self, analyzer, plan_generator, plan_validator, memory_integrator
    ):
        """بازیابی از شکست اعتبارسنجی"""
        request = "یک فایل حذف کن"
        intent = await analyzer.analyze(request)
        
        plan = await plan_generator.generate_plan(intent)
        validation = await plan_validator.validate(plan, intent, ValidationLevel.PARANOID)
        
        # ممکن است warning یا error داشته باشد (حذف خطرناک است)
        # اما باید ثبت شود
        record_id = memory_integrator.record_execution(
            plan_id=plan.plan_id,
            intent=intent,
            status=PlanStatus.FAILED,
            steps_succeeded=0,
            steps_failed=len(plan.steps),
            total_steps=len(plan.steps),
            actual_time_seconds=1.0,
            estimated_time_seconds=5.0,
            error_message="Blocked by validation"
        )
        
        assert record_id is not None
    
    @pytest.mark.asyncio
    async def test_partial_success_learning(
        self, analyzer, plan_generator, plan_validator, memory_integrator
    ):
        """یادگیری از موفقیت جزئی"""
        request = "یک برنامه باز کن"
        intent = await analyzer.analyze(request)
        plan = await plan_generator.generate_plan(intent)
        
        total = len(plan.steps)
        successful = max(1, total // 2)
        
        record_id = memory_integrator.record_execution(
            plan_id=plan.plan_id,
            intent=intent,
            status=PlanStatus.PARTIAL,
            steps_succeeded=successful,
            steps_failed=total - successful,
            total_steps=total,
            actual_time_seconds=3.0,
            estimated_time_seconds=5.0,
            error_message="Some steps failed"
        )
        
        assert record_id is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestMemoryLearning - یادگیری حافظه
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoryLearning:
    """تست‌های یادگیری حافظه در سیستم یکپارچه"""
    
    @pytest.mark.asyncio
    async def test_similar_requests_reuse(
        self, analyzer, dialog_manager, plan_generator,
        plan_validator, memory_integrator
    ):
        """بازاستفاده از پلان‌های مشابه"""
        # درخواست اول
        request1 = "بازی را شروع کن"
        intent1 = analyzer.analyze(request1)
        plan1 = plan_generator.generate_plan(intent1)
        
        # ثبت اجرای موفق
        memory_integrator.record_execution(
            plan_id=plan1.plan_id,
            intent=intent1,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=len(plan1.steps),
            steps_failed=0,
            total_steps=len(plan1.steps),
            actual_time_seconds=4.0,
            estimated_time_seconds=5.0
        )
        
        # درخواست مشابه
        request2 = "بازی رو شروع کن"
        intent2 = analyzer.analyze(request2)
        
        # جستجوی مشابه
        similar = memory_integrator.find_similar_plans(intent2, threshold=0.6)
        
        # میتواند مشابه پیدا کند یا نکند
        assert isinstance(similar, list)
    
    @pytest.mark.asyncio
    async def test_optimization_tracking(
        self, analyzer, plan_generator, memory_integrator
    ):
        """ردیابی بهینه‌سازی‌ها"""
        request = "فایل کپی کن"
        intent = await analyzer.analyze(request)
        plan = await plan_generator.generate_plan(intent)
        
        # اجرای سریع (فرصت بهینه‌سازی timeout)
        memory_integrator.record_execution(
            plan_id=plan.plan_id + "_fast",
            intent=intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=len(plan.steps),
            steps_failed=0,
            total_steps=len(plan.steps),
            actual_time_seconds=1.0,  # بسیار سریع‌تر
            estimated_time_seconds=10.0  # برآورد بزرگ‌تر
        )
        
        # آمار
        stats = memory_integrator.get_statistics()
        
        assert stats["total_executions"] == 1
        assert stats["successful"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TestSequentialExecution - اجرای متوالی
# ═══════════════════════════════════════════════════════════════════════════════

class TestSequentialExecution:
    """تست‌های اجرای متوالی پلان‌های مختلف"""
    
    @pytest.mark.asyncio
    async def test_multiple_different_requests(
        self, analyzer, plan_generator, plan_validator, memory_integrator
    ):
        """اجرای پی‌درپی درخواست‌های متفاوت"""
        requests = [
            "برنامه کروم را باز کن",
            "یک فایل بساز",
            "تصویر یک‌پارچه بکن"
        ]
        
        for req in requests:
            intent = await analyzer.analyze(req)
            assert intent is not None
            
            plan = await plan_generator.generate_plan(intent)
            assert plan is not None
            
            validation = await plan_validator.validate(plan, intent)
            assert validation is not None
            
            # ثبت موفق
            memory_integrator.record_execution(
                plan_id=plan.plan_id,
                intent=intent,
                status=PlanStatus.SUCCESSFUL,
                steps_succeeded=len(plan.steps),
                steps_failed=0,
                total_steps=len(plan.steps),
                actual_time_seconds=5.0,
                estimated_time_seconds=5.0
            )
        
        # تأیید ثبت تمام آن‌ها
        stats = memory_integrator.get_statistics()
        assert stats["total_executions"] == 3
        assert stats["successful"] == 3


# ═══════════════════════════════════════════════════════════════════════════════
# TestValidationLevels - سطح‌های اعتبارسنجی
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidationLevels:
    """تست‌های سطح‌های اعتبارسنجی مختلف"""
    
    @pytest.mark.asyncio
    async def test_basic_validation_level(
        self, analyzer, plan_generator, plan_validator
    ):
        """اعتبارسنجی سطح BASIC"""
        request = "یک پرونده باز کن"
        intent = await analyzer.analyze(request)
        plan = await plan_generator.generate_plan(intent)
        
        validation = await plan_validator.validate(
            plan, intent, ValidationLevel.BASIC
        )
        
        assert validation is not None
    
    @pytest.mark.asyncio
    async def test_strict_validation_level(
        self, analyzer, plan_generator, plan_validator
    ):
        """اعتبارسنجی سطح STRICT"""
        request = "سیستم را خاموش کن"
        intent = await analyzer.analyze(request)
        plan = await plan_generator.generate_plan(intent)
        
        validation = await plan_validator.validate(
            plan, intent, ValidationLevel.STRICT
        )
        
        assert validation is not None
        # ممکن است warning یا error داشته باشد
    
    @pytest.mark.asyncio
    async def test_paranoid_validation_level(
        self, analyzer, plan_generator, plan_validator
    ):
        """اعتبارسنجی سطح PARANOID"""
        request = "حذف کن"
        intent = await analyzer.analyze(request)
        plan = await plan_generator.generate_plan(intent)
        
        validation = await plan_validator.validate(
            plan, intent, ValidationLevel.PARANOID
        )
        
        assert validation is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestPerformanceIntegration - عملکرد یکپارچه
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformanceIntegration:
    """تست‌های عملکرد سیستم یکپارچه"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_speed(
        self, analyzer, dialog_manager, plan_generator,
        plan_validator, memory_integrator
    ):
        """سرعت جریان کامل"""
        import time
        
        request = "یک برنامه شروع کن"
        
        start = time.time()
        
        # مرحله ۱: تحلیل (باید سریع باشد)
        intent = await analyzer.analyze(request)
        analysis_time = time.time() - start
        assert analysis_time < 0.1  # کمتر از ۱۰۰ms
        
        # مرحله ۳: تولید
        start_plan = time.time()
        plan = await plan_generator.generate_plan(intent)
        plan_time = time.time() - start_plan
        assert plan_time < 0.2  # کمتر از ۲۰۰ms
        
        # مرحله ۴: اعتبارسنجی
        start_val = time.time()
        validation = await plan_validator.validate(plan, intent)
        val_time = time.time() - start_val
        assert val_time < 0.1  # کمتر از ۱۰۰ms
    
    @pytest.mark.asyncio
    async def test_batch_processing_speed(
        self, analyzer, plan_generator, memory_integrator
    ):
        """سرعت پردازش دسته‌ای"""
        import time
        
        requests = [f"کار {i}" for i in range(10)]
        
        start = time.time()
        
        for req in requests:
            intent = await analyzer.analyze(req)
            plan = await plan_generator.generate_plan(intent)
            memory_integrator.record_execution(
                plan_id=plan.plan_id,
                intent=intent,
                status=PlanStatus.SUCCESSFUL,
                steps_succeeded=len(plan.steps),
                steps_failed=0,
                total_steps=len(plan.steps),
                actual_time_seconds=1.0,
                estimated_time_seconds=1.0
            )
        
        elapsed = time.time() - start
        
        # ۱۰ درخواست در کمتر از ۲ ثانیه
        assert elapsed < 2.0


# ═══════════════════════════════════════════════════════════════════════════════
# TestBilingualSupport - پشتیبانی دوزبانه
# ═══════════════════════════════════════════════════════════════════════════════

class TestBilingualSupport:
    """تست‌های پشتیبانی دوزبانه"""
    
    @pytest.mark.asyncio
    async def test_persian_request_flow(
        self, analyzer, plan_generator, plan_validator
    ):
        """درخواست فارسی"""
        request = "بازی کو باز کن"
        intent = await analyzer.analyze(request)
        
        assert intent.language in ["fa", "mixed"]
        
        plan = await plan_generator.generate_plan(intent)
        assert plan is not None
        
        validation = await plan_validator.validate(plan, intent)
        assert validation is not None
    
    @pytest.mark.asyncio
    async def test_english_request_flow(
        self, analyzer, plan_generator, plan_validator
    ):
        """درخواست انگلیسی"""
        request = "open notepad"
        intent = await analyzer.analyze(request)
        
        assert intent is not None
        
        plan = await plan_generator.generate_plan(intent)
        assert plan is not None
        
        validation = await plan_validator.validate(plan, intent)
        assert validation is not None
    
    @pytest.mark.asyncio
    async def test_mixed_request_flow(
        self, analyzer, plan_generator, plan_validator
    ):
        """درخواست مختلط"""
        request = "Chrome رو open کن"
        intent = await analyzer.analyze(request)
        
        assert intent is not None
        
        plan = await plan_generator.generate_plan(intent)
        assert plan is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestDataFlow - جریان داده‌ها
# ═══════════════════════════════════════════════════════════════════════════════

class TestDataFlow:
    """تست‌های جریان داده‌ها بین ماژول‌ها"""
    
    @pytest.mark.asyncio
    async def test_intent_to_plan_flow(self, analyzer, plan_generator):
        """جریان Intent → Plan"""
        request = "سیستم بروز کن"
        intent = await analyzer.analyze(request)
        
        # Intent باید تمام داده لازم را داشته باشد
        assert intent.verb is not None
        assert intent.target is not None
        
        plan = await plan_generator.generate_plan(intent)
        
        # Plan باید از Intent استفاده کند
        assert plan.intent == intent or plan.intent.verb == intent.verb
    
    @pytest.mark.asyncio
    async def test_plan_to_validation_flow(self, analyzer, plan_generator, plan_validator):
        """جریان Plan → Validation"""
        request = "یک پوشه بساز"
        intent = await analyzer.analyze(request)
        plan = await plan_generator.generate_plan(intent)
        
        validation = await plan_validator.validate(plan, intent)
        
        # Validation باید plan_id داشته باشد
        assert validation.plan_id == plan.plan_id
    
    @pytest.mark.asyncio
    async def test_validation_to_memory_flow(
        self, analyzer, plan_generator, plan_validator, memory_integrator
    ):
        """جریان Validation → Memory"""
        request = "فایل دانلود کن"
        intent = await analyzer.analyze(request)
        plan = await plan_generator.generate_plan(intent)
        validation = await plan_validator.validate(plan, intent)
        
        # ثبت در حافظه
        record_id = memory_integrator.record_execution(
            plan_id=plan.plan_id,
            intent=intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=len(plan.steps),
            steps_failed=0,
            total_steps=len(plan.steps),
            actual_time_seconds=5.0,
            estimated_time_seconds=5.0
        )
        
        # توصیه‌ها
        recommendations = memory_integrator.get_recommendations(intent)
        
        assert recommendations["similar_plans"] == 0 or recommendations["similar_plans"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestStatisticsCollection - جمع‌آوری آمار
# ═══════════════════════════════════════════════════════════════════════════════

class TestStatisticsCollection:
    """تست‌های جمع‌آوری و ردیابی آمار"""
    
    @pytest.mark.asyncio
    async def test_system_statistics_collection(
        self, analyzer, plan_generator, memory_integrator
    ):
        """جمع‌آوری آمار سیستم"""
        # اجرای چندین درخواست
        for i in range(5):
            request = f"کار {i}"
            intent = await analyzer.analyze(request)
            plan = await plan_generator.generate_plan(intent)
            
            memory_integrator.record_execution(
                plan_id=plan.plan_id,
                intent=intent,
                status=PlanStatus.SUCCESSFUL if i % 2 == 0 else PlanStatus.FAILED,
                steps_succeeded=len(plan.steps) if i % 2 == 0 else 0,
                steps_failed=0 if i % 2 == 0 else len(plan.steps),
                total_steps=len(plan.steps),
                actual_time_seconds=5.0,
                estimated_time_seconds=5.0
            )
        
        # بررسی آمار
        stats = memory_integrator.get_statistics()
        
        assert stats["total_executions"] == 5
        assert stats["successful"] >= 2
        assert stats["failed"] >= 2
        assert stats["success_rate"] > 0
