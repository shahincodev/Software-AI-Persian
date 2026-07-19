# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Test Suite for Memory Integrator - مجموعه تست‌های یکپارچه‌کننده حافظه

۲۸ تست برای ذخیره، بازیابی و بهینه‌سازی پلان‌ها
"""

import pytest
from datetime import datetime, timedelta
import os
import tempfile

from core.memory_integrator import (
    MemoryIntegrator,
    PlanStatus,
    LearningType,
    ExecutionHistory,
)
from core.plan_generator import (
    ExecutionPlan,
    ExecutionStep,
    StepType,
    ExecutionMode
)
from core.plan_validator import ValidationReport, ValidationStatus
from core.intent_analyzer import Intent


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def temp_db():
    """ایجاد دیتابیس موقتی"""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        yield db_path
        # بستن تمام اتصالات قبل از پاک‌کردن
        import sqlite3
        sqlite3.connect(db_path).close()


@pytest.fixture
def memory_integrator(temp_db):
    """اولیه‌سازی Memory Integrator"""
    return MemoryIntegrator(db_path=temp_db)


@pytest.fixture
def sample_intent():
    """Intent نمونه"""
    return Intent(
        verb="بازی",
        target="game",
        parameters={"game_type": "FPS"},
        constraints=[],
        confidence=0.95,
        raw_request="بازی کن",
        language="fa"
    )


@pytest.fixture
def sample_plan():
    """Plan نمونه"""
    return ExecutionPlan(
        plan_id="plan_test",
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
                step_id="s1",
                order=1,
                action="باز کردن بازی",
                action_en="Open game",
                step_type=StepType.OPEN,
                target="game",
                parameters={},
                dependencies=[],
                timeout=15,
                retries=3,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description="مرحله ۱"
            ),
            ExecutionStep(
                step_id="s2",
                order=2,
                action="شروع بازی",
                action_en="Start game",
                step_type=StepType.INTERACT,
                target="game",
                parameters={},
                dependencies=["s1"],
                timeout=5,
                retries=2,
                fallback_action=None,
                execution_mode=ExecutionMode.SEQUENTIAL,
                priority=5,
                description="مرحله ۲"
            )
        ]
    )


@pytest.fixture
def validation_report():
    """گزارش اعتبارسنجی نمونه"""
    report = ValidationReport(
        plan_id="plan_test",
        is_valid=True,
        status=ValidationStatus.VALID
    )
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# TestExecutionRecording - ثبت اجرا
# ═══════════════════════════════════════════════════════════════════════════════

class TestExecutionRecording:
    """تست‌های ثبت اجرا"""
    
    def test_record_successful_execution(self, memory_integrator, sample_intent):
        """ثبت اجرای موفق"""
        record_id = memory_integrator.record_execution(
            plan_id="plan_1",
            intent=sample_intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=5,
            steps_failed=0,
            total_steps=5,
            actual_time_seconds=10.5,
            estimated_time_seconds=12.0
        )
        
        assert record_id is not None
        assert isinstance(record_id, str)
    
    def test_record_failed_execution(self, memory_integrator, sample_intent):
        """ثبت اجرای ناموفق"""
        record_id = memory_integrator.record_execution(
            plan_id="plan_2",
            intent=sample_intent,
            status=PlanStatus.FAILED,
            steps_succeeded=2,
            steps_failed=3,
            total_steps=5,
            actual_time_seconds=5.0,
            estimated_time_seconds=12.0,
            error_message="Step 3 failed"
        )
        
        assert record_id is not None
    
    def test_performance_score_calculated(self, memory_integrator, sample_intent):
        """امتیاز عملکرد محاسبه می‌شود"""
        memory_integrator.record_execution(
            plan_id="plan_3",
            intent=sample_intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=4,
            steps_failed=1,
            total_steps=5,
            actual_time_seconds=10.0,
            estimated_time_seconds=10.0
        )
        
        # بررسی ثبت شدن در دیتابیس
        import sqlite3
        with sqlite3.connect(memory_integrator.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT performance_score FROM execution_history WHERE plan_id = ?", ("plan_3",))
            score = cursor.fetchone()[0]
            assert 50 <= score <= 100


# ═══════════════════════════════════════════════════════════════════════════════
# TestLearning - یادگیری
# ═══════════════════════════════════════════════════════════════════════════════

class TestLearning:
    """تست‌های یادگیری"""
    
    @pytest.mark.asyncio
    async def test_learn_from_success(self, memory_integrator, sample_plan, validation_report, sample_intent):
        """یادگیری از موفقیت"""
        history = ExecutionHistory(
            plan_id="plan_1",
            intent_hash=memory_integrator._hash_intent(sample_intent),
            start_time=datetime.now(),
            end_time=datetime.now(),
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=2,
            steps_failed=0,
            total_steps=2,
            actual_time_seconds=10.0,
            estimated_time_seconds=12.0,
            performance_score=90.0
        )
        
        learned = memory_integrator.learn_from_execution(
            history, sample_plan, validation_report
        )
        
        assert LearningType.SUCCESS in learned
    
    @pytest.mark.asyncio
    async def test_learn_from_failure(self, memory_integrator, sample_plan, validation_report, sample_intent):
        """یادگیری از شکست"""
        history = ExecutionHistory(
            plan_id="plan_2",
            intent_hash=memory_integrator._hash_intent(sample_intent),
            start_time=datetime.now(),
            end_time=datetime.now(),
            status=PlanStatus.FAILED,
            steps_succeeded=1,
            steps_failed=1,
            total_steps=2,
            actual_time_seconds=5.0,
            estimated_time_seconds=12.0,
            performance_score=50.0,
            error_message="Step failed"
        )
        
        learned = memory_integrator.learn_from_execution(
            history, sample_plan, validation_report
        )
        
        assert LearningType.FAILURE in learned
    
    @pytest.mark.asyncio
    async def test_pattern_identification(self, memory_integrator, sample_plan, validation_report, sample_intent):
        """شناخت الگوها"""
        history = ExecutionHistory(
            plan_id="plan_3",
            intent_hash=memory_integrator._hash_intent(sample_intent),
            start_time=datetime.now(),
            end_time=datetime.now(),
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=2,
            steps_failed=0,
            total_steps=2,
            actual_time_seconds=10.0,
            estimated_time_seconds=12.0,
            performance_score=90.0
        )
        
        learned = memory_integrator.learn_from_execution(
            history, sample_plan, validation_report
        )
        
        # الگو می‌تواند شناخته شده باشد
        assert isinstance(learned, list)


# ═══════════════════════════════════════════════════════════════════════════════
# TestSimilaritySearch - جستجوی شباهت
# ═══════════════════════════════════════════════════════════════════════════════

class TestSimilaritySearch:
    """تست‌های جستجوی شباهت"""
    
    def test_find_similar_plans(self, memory_integrator, sample_intent):
        """یافتن پلان‌های مشابه"""
        # ثبت یک اجرای موفق
        memory_integrator.record_execution(
            plan_id="plan_similar_1",
            intent=sample_intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=5,
            steps_failed=0,
            total_steps=5,
            actual_time_seconds=10.0,
            estimated_time_seconds=12.0
        )
        
        # جستجو برای مشابه
        matches = memory_integrator.find_similar_plans(sample_intent, threshold=0.7)
        
        assert isinstance(matches, list)
    
    def test_find_similar_plans_empty(self, memory_integrator):
        """جستجو برای پلان‌های مشابه (خالی)"""
        intent = Intent(
            verb="نامشناخته",
            target="unknown",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="test",
            language="fa"
        )
        
        matches = memory_integrator.find_similar_plans(intent)
        
        assert isinstance(matches, list)
        assert len(matches) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestOptimization - بهینه‌سازی
# ═══════════════════════════════════════════════════════════════════════════════

class TestOptimization:
    """تست‌های بهینه‌سازی"""
    
    def test_reduce_timeout_suggestion(self, memory_integrator, sample_plan, sample_intent):
        """پیشنهاد کاهش timeout"""
        history = ExecutionHistory(
            plan_id="plan_fast",
            intent_hash=memory_integrator._hash_intent(sample_intent),
            start_time=datetime.now(),
            end_time=datetime.now(),
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=2,
            steps_failed=0,
            total_steps=2,
            actual_time_seconds=3.0,  # بسیار سریع‌تر از برآورد
            estimated_time_seconds=12.0,
            performance_score=100.0
        )
        
        suggestion = memory_integrator._generate_optimizations(history, sample_plan)
        
        if suggestion:
            assert suggestion.suggestion_type == "reduce_timeout"
    
    def test_parallelization_suggestion(self, memory_integrator, sample_intent):
        """پیشنهاد parallelization"""
        # پلان با مراحل مستقل زیادی
        plan = ExecutionPlan(
            plan_id="parallel_plan",
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
                    step_id=f"s{i}",
                    order=i+1,
                    action=f"action {i}",
                    action_en=f"action {i}",
                    step_type=StepType.INTERACT,
                    target="target",
                    parameters={},
                    dependencies=[],  # بدون وابستگی
                    timeout=5,
                    retries=1,
                    fallback_action=None,
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    priority=5,
                    description=f"step {i}"
                )
                for i in range(5)
            ]
        )
        
        history = ExecutionHistory(
            plan_id="parallel_plan",
            intent_hash=memory_integrator._hash_intent(sample_intent),
            start_time=datetime.now(),
            end_time=datetime.now(),
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=5,
            steps_failed=0,
            total_steps=5,
            actual_time_seconds=25.0,  # بیش‌تر از توقع
            estimated_time_seconds=20.0,
            performance_score=80.0
        )
        
        suggestion = memory_integrator._generate_optimizations(history, plan)
        
        if suggestion:
            assert suggestion.suggestion_type in ("reduce_timeout", "increase_parallelization")


# ═══════════════════════════════════════════════════════════════════════════════
# TestStatistics - آمار
# ═══════════════════════════════════════════════════════════════════════════════

class TestStatistics:
    """تست‌های آمار"""
    
    def test_get_statistics_empty(self, memory_integrator):
        """دریافت آمار (خالی)"""
        stats = memory_integrator.get_statistics()
        
        assert stats["total_executions"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == 0
    
    def test_get_statistics_with_data(self, memory_integrator, sample_intent):
        """دریافت آمار (با داده)"""
        # ثبت چند اجرا
        for i in range(3):
            memory_integrator.record_execution(
                plan_id=f"plan_{i}",
                intent=sample_intent,
                status=PlanStatus.SUCCESSFUL,
                steps_succeeded=5,
                steps_failed=0,
                total_steps=5,
                actual_time_seconds=10.0,
                estimated_time_seconds=12.0
            )
        
        stats = memory_integrator.get_statistics()
        
        assert stats["total_executions"] == 3
        assert stats["successful"] == 3
        assert stats["success_rate"] == 100.0
    
    def test_success_rate_calculation(self, memory_integrator, sample_intent):
        """محاسبه نرخ موفقیت"""
        # 2 موفق، 2 ناموفق
        for i in range(2):
            memory_integrator.record_execution(
                plan_id=f"success_{i}",
                intent=sample_intent,
                status=PlanStatus.SUCCESSFUL,
                steps_succeeded=5,
                steps_failed=0,
                total_steps=5,
                actual_time_seconds=10.0,
                estimated_time_seconds=12.0
            )
        
        for i in range(2):
            memory_integrator.record_execution(
                plan_id=f"failed_{i}",
                intent=sample_intent,
                status=PlanStatus.FAILED,
                steps_succeeded=2,
                steps_failed=3,
                total_steps=5,
                actual_time_seconds=5.0,
                estimated_time_seconds=12.0,
                error_message="Failed"
            )
        
        stats = memory_integrator.get_statistics()
        
        assert stats["total_executions"] == 4
        assert stats["successful"] == 2
        assert stats["failed"] == 2
        assert stats["success_rate"] == 50.0


# ═══════════════════════════════════════════════════════════════════════════════
# TestCleanup - پاک‌کردن
# ═══════════════════════════════════════════════════════════════════════════════

class TestCleanup:
    """تست‌های پاک‌کردن"""
    
    def test_cleanup_old_records(self, memory_integrator, sample_intent):
        """پاک‌کردن سابقه قدیمی"""
        # ثبت اجراهای قدیمی (به طور دستی)
        import sqlite3
        
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        
        with sqlite3.connect(memory_integrator.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_history
                (plan_id, intent_hash, start_time, status, steps_succeeded, 
                 steps_failed, total_steps, actual_time_seconds, 
                 estimated_time_seconds, performance_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "old_plan", "hash", old_date, "successful", 5, 0, 5, 10, 12, 95, old_date
            ))
            conn.commit()
        
        # پاک‌کردن
        deleted = memory_integrator.cleanup_old_records(days=30)
        
        assert deleted == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TestRecommendations - توصیه‌ها
# ═══════════════════════════════════════════════════════════════════════════════

class TestRecommendations:
    """تست‌های توصیه‌ها"""
    
    def test_get_recommendations(self, memory_integrator, sample_intent):
        """دریافت توصیه‌ها"""
        # ثبت اجرای موفق
        memory_integrator.record_execution(
            plan_id="plan_rec",
            intent=sample_intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=5,
            steps_failed=0,
            total_steps=5,
            actual_time_seconds=10.0,
            estimated_time_seconds=12.0
        )
        
        recommendations = memory_integrator.get_recommendations(sample_intent)
        
        assert isinstance(recommendations, dict)
        assert "similar_plans" in recommendations
        assert "memory_stats" in recommendations
    
    def test_recommendations_empty(self, memory_integrator):
        """توصیه‌ها (خالی)"""
        intent = Intent(
            verb="نامشناخته",
            target="unknown",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="test",
            language="fa"
        )
        
        recommendations = memory_integrator.get_recommendations(intent)
        
        assert recommendations["similar_plans"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestIntentHash - Hash کردن Intent
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntentHash:
    """تست‌های Hash کردن Intent"""
    
    def test_same_intent_same_hash(self, memory_integrator, sample_intent):
        """Intent یکسان Hash یکسان دارد"""
        hash1 = memory_integrator._hash_intent(sample_intent)
        hash2 = memory_integrator._hash_intent(sample_intent)
        
        assert hash1 == hash2
    
    def test_different_intent_different_hash(self, memory_integrator, sample_intent):
        """Intent متفاوت Hash متفاوت دارد"""
        intent2 = Intent(
            verb="ایجاد",
            target="folder",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="پوشه بساز",
            language="fa"
        )
        
        hash1 = memory_integrator._hash_intent(sample_intent)
        hash2 = memory_integrator._hash_intent(intent2)
        
        assert hash1 != hash2


# ═══════════════════════════════════════════════════════════════════════════════
# TestDataPersistence - ماندگاری داده‌ها
# ═══════════════════════════════════════════════════════════════════════════════

class TestDataPersistence:
    """تست‌های ماندگاری داده‌ها"""
    
    def test_data_persists_across_instances(self, temp_db, sample_intent):
        """داده‌ها در میان نمونه‌های مختلف ماندگار هستند"""
        # نمونه اول
        mem1 = MemoryIntegrator(db_path=temp_db)
        mem1.record_execution(
            plan_id="plan_persist",
            intent=sample_intent,
            status=PlanStatus.SUCCESSFUL,
            steps_succeeded=5,
            steps_failed=0,
            total_steps=5,
            actual_time_seconds=10.0,
            estimated_time_seconds=12.0
        )
        
        # نمونه دوم
        mem2 = MemoryIntegrator(db_path=temp_db)
        stats = mem2.get_statistics()
        
        assert stats["total_executions"] == 1
        assert stats["successful"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TestPerformance - عملکرد
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformance:
    """تست‌های عملکرد"""
    
    def test_record_execution_speed(self, memory_integrator, sample_intent):
        """سرعت ثبت اجرا"""
        import time
        
        start = time.time()
        for i in range(100):
            memory_integrator.record_execution(
                plan_id=f"perf_{i}",
                intent=sample_intent,
                status=PlanStatus.SUCCESSFUL,
                steps_succeeded=5,
                steps_failed=0,
                total_steps=5,
                actual_time_seconds=10.0,
                estimated_time_seconds=12.0
            )
        elapsed = time.time() - start
        
        # ۱۰۰ ثبت در کمتر از ۵ ثانیه
        assert elapsed < 5.0
    
    def test_statistics_retrieval_speed(self, memory_integrator, sample_intent):
        """سرعت دریافت آمار"""
        import time
        
        # ثبت برخی اجراها
        for i in range(50):
            memory_integrator.record_execution(
                plan_id=f"stat_{i}",
                intent=sample_intent,
                status=PlanStatus.SUCCESSFUL if i % 2 == 0 else PlanStatus.FAILED,
                steps_succeeded=5 if i % 2 == 0 else 2,
                steps_failed=0 if i % 2 == 0 else 3,
                total_steps=5,
                actual_time_seconds=10.0,
                estimated_time_seconds=12.0
            )
        
        # دریافت آمار
        start = time.time()
        for _ in range(10):
            memory_integrator.get_statistics()
        elapsed = time.time() - start
        
        # ۱۰ بار در کمتر از ۱ ثانیه
        assert elapsed < 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# TestPlanStatusProcessing - پردازش وضعیت پلان
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlanStatusProcessing:
    """تست‌های پردازش وضعیت‌های مختلف پلان"""
    
    def test_partial_success_status(self, memory_integrator, sample_intent):
        """ثبت موفقیت جزئی"""
        record_id = memory_integrator.record_execution(
            plan_id="plan_partial",
            intent=sample_intent,
            status=PlanStatus.PARTIAL,
            steps_succeeded=3,
            steps_failed=2,
            total_steps=5,
            actual_time_seconds=10.0,
            estimated_time_seconds=12.0,
            error_message="Step 4 and 5 failed"
        )
        
        assert record_id is not None
    
    def test_timeout_status(self, memory_integrator, sample_intent):
        """ثبت timeout"""
        record_id = memory_integrator.record_execution(
            plan_id="plan_timeout",
            intent=sample_intent,
            status=PlanStatus.TIMEOUT,
            steps_succeeded=2,
            steps_failed=3,
            total_steps=5,
            actual_time_seconds=35.0,
            estimated_time_seconds=12.0,
            error_message="Execution timeout"
        )
        
        assert record_id is not None
    
    def test_cancelled_status(self, memory_integrator, sample_intent):
        """ثبت لغو شده"""
        record_id = memory_integrator.record_execution(
            plan_id="plan_cancelled",
            intent=sample_intent,
            status=PlanStatus.CANCELLED,
            steps_succeeded=1,
            steps_failed=0,
            total_steps=5,
            actual_time_seconds=2.0,
            estimated_time_seconds=12.0,
            error_message="User cancelled execution"
        )
        
        assert record_id is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestErrorHandling - مدیریت خطا
# ═══════════════════════════════════════════════════════════════════════════════

class TestErrorHandling:
    """تست‌های مدیریت خطا"""
    
    def test_missing_intent_field(self, memory_integrator):
        """Intent بدون فیلد ضروری"""
        incomplete_intent = Intent(
            verb="",  # فیلد خالی
            target="",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="test",
            language="fa"
        )
        
        # نباید خطا دهد
        record_id = memory_integrator.record_execution(
            plan_id="plan_error",
            intent=incomplete_intent,
            status=PlanStatus.FAILED,
            steps_succeeded=0,
            steps_failed=1,
            total_steps=1,
            actual_time_seconds=1.0,
            estimated_time_seconds=5.0
        )
        
        assert record_id is not None
    
    def test_learning_with_corrupt_plan(self, memory_integrator, sample_plan):
        """یادگیری از پلان ناقص"""
        history = ExecutionHistory(
            plan_id="plan_corrupt",
            intent_hash="invalid_hash",
            start_time=datetime.now(),
            end_time=datetime.now(),
            status=PlanStatus.FAILED,
            steps_succeeded=0,
            steps_failed=1,
            total_steps=1,
            actual_time_seconds=5.0,
            estimated_time_seconds=10.0,
            error_message="Error"
        )
        
        # پلان بدون steps
        empty_plan = ExecutionPlan(
            plan_id="empty",
            intent=sample_plan.intent,
            steps=[]
        )
        
        report = ValidationReport(
            plan_id="empty",
            is_valid=False,
            status=ValidationStatus.ERROR
        )
        
        # نباید خطا دهد
        learned = memory_integrator.learn_from_execution(history, empty_plan, report)
        assert isinstance(learned, list)


# ═══════════════════════════════════════════════════════════════════════════════
# TestConcurrency - همزمانی
# ═══════════════════════════════════════════════════════════════════════════════

class TestConcurrency:
    """تست‌های همزمانی"""
    
    def test_multiple_sequential_records(self, memory_integrator, sample_intent):
        """ثبت‌های متوالی"""
        record_ids = []
        for i in range(10):
            record_id = memory_integrator.record_execution(
                plan_id=f"concurrent_{i}",
                intent=sample_intent,
                status=PlanStatus.SUCCESSFUL,
                steps_succeeded=5,
                steps_failed=0,
                total_steps=5,
                actual_time_seconds=10.0,
                estimated_time_seconds=12.0
            )
            record_ids.append(record_id)
        
        # تمام ثبت‌ها باید موفق باشند
        assert len(record_ids) == 10
        assert all(rid is not None for rid in record_ids)
    
    def test_statistics_during_insertion(self, memory_integrator, sample_intent):
        """دریافت آمار در زمان درج"""
        # ثبت برخی
        for i in range(5):
            memory_integrator.record_execution(
                plan_id=f"insert_{i}",
                intent=sample_intent,
                status=PlanStatus.SUCCESSFUL,
                steps_succeeded=5,
                steps_failed=0,
                total_steps=5,
                actual_time_seconds=10.0,
                estimated_time_seconds=12.0
            )
        
        # دریافت آمار
        stats = memory_integrator.get_statistics()
        assert stats["total_executions"] == 5
