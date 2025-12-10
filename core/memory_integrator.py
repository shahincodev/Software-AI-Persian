# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Memory Integrator - یکپارچه‌سازی حافظه و یادگیری

این ماژول مسئول ذخیره، بازیابی و بهبود پلان‌های اجرایی بر اساس تجربیات قبلی است.
سیستم حافظه یادگیری از موفقیت‌ها و شکست‌ها برای بهبود مستمر استفاده می‌کند.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json
import logging
import sqlite3
from pathlib import Path

from core.plan_generator import ExecutionPlan, ExecutionStep
from core.plan_validator import ValidationReport, ValidationStatus
from core.intent_analyzer import Intent


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes and Enums
# ═══════════════════════════════════════════════════════════════════════════════

class PlanStatus(Enum):
    """وضعیت پلان"""
    SUCCESSFUL = "successful"     # اجرا موفق
    FAILED = "failed"             # شکست در اجرا
    PARTIAL = "partial"           # موفقیت جزئی
    CANCELLED = "cancelled"       # لغو شده
    TIMEOUT = "timeout"           # Timeout
    UNKNOWN = "unknown"           # نامشخص


class LearningType(Enum):
    """نوع‌های یادگیری"""
    SUCCESS = "success"           # یادگیری از موفقیت
    FAILURE = "failure"           # یادگیری از شکست
    PATTERN = "pattern"           # شناخت الگو
    OPTIMIZATION = "optimization" # بهینه‌سازی


@dataclass
class ExecutionHistory:
    """سابقه اجرای یک پلان"""
    plan_id: str
    intent_hash: str               # Hash اختصاری Intent
    start_time: datetime
    end_time: Optional[datetime] = None
    status: PlanStatus = PlanStatus.UNKNOWN
    
    steps_succeeded: int = 0       # تعداد مراحل موفق
    steps_failed: int = 0          # تعداد مراحل ناموفق
    total_steps: int = 0           # کل مراحل
    
    actual_time_seconds: float = 0.0  # زمان واقعی اجرا
    estimated_time_seconds: float = 0.0  # زمان برآورد شده
    
    error_message: Optional[str] = None  # پیغام خطا
    performance_score: float = 100.0    # امتیاز عملکرد (0-100)
    
    feedback: Optional[str] = None  # بازخورد کاربر


@dataclass
class PatternMatch:
    """تطابق الگو"""
    pattern_id: str
    similarity: float              # درجه شباهت (0-1)
    matched_steps: List[int]       # شماره‌های مراحل منطبق
    execution_history: ExecutionHistory


@dataclass
class OptimizationSuggestion:
    """پیشنهاد بهینه‌سازی"""
    suggestion_type: str           # نوع پیشنهاد
    description_fa: str
    description_en: str
    affected_steps: List[int]      # مراحل تأثیرپذیر
    expected_improvement: float    # بهبود مورد انتظار (%)
    confidence: float              # اعتماد به پیشنهاد (0-1)


# ═══════════════════════════════════════════════════════════════════════════════
# Memory Integrator Class
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryIntegrator:
    """
    یکپارچه‌کننده حافظه برای یادگیری مستمر
    
    مسئولیت‌های اصلی:
    1. ذخیره سابقه اجرای پلان‌ها
    2. یادگیری از موفقیت‌ها و شکست‌ها
    3. شناخت الگوهای مشترک
    4. ارائه پیشنهادات بهینه‌سازی
    5. بهبود مستمر کیفیت پلان‌ها
    """

    def __init__(self, db_path: str = "data/memories.sqlite3"):
        """سازنده Memory Integrator"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # اطمینان از وجود دیتابیس
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """اولیه‌سازی دیتابیس"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # جدول سابقه اجرا
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id TEXT NOT NULL,
                    intent_hash TEXT NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT,
                    steps_succeeded INTEGER,
                    steps_failed INTEGER,
                    total_steps INTEGER,
                    actual_time_seconds REAL,
                    estimated_time_seconds REAL,
                    error_message TEXT,
                    performance_score REAL,
                    feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول الگوهای یادگیری شده
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_hash TEXT UNIQUE,
                    pattern_type TEXT,
                    step_sequence TEXT,
                    success_rate REAL,
                    execution_count INTEGER,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # جدول بهبودهای بهینه‌سازی
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    optimization_type TEXT,
                    description_fa TEXT,
                    description_en TEXT,
                    affected_steps TEXT,
                    expected_improvement REAL,
                    confidence REAL,
                    applied_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()

    def record_execution(
        self,
        plan_id: str,
        intent: Intent,
        status: PlanStatus,
        steps_succeeded: int,
        steps_failed: int,
        total_steps: int,
        actual_time_seconds: float,
        estimated_time_seconds: float,
        error_message: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> str:
        """
        ثبت اجرای یک پلان
        
        بازگشت: شناسه سابقه
        """
        intent_hash = self._hash_intent(intent)
        start_time = datetime.now()
        end_time = datetime.now()
        
        # محاسبه امتیاز عملکرد
        success_rate = steps_succeeded / total_steps if total_steps > 0 else 0
        time_accuracy = 1 - abs(actual_time_seconds - estimated_time_seconds) / max(estimated_time_seconds, 1)
        performance_score = (success_rate * 70 + max(0, time_accuracy) * 30)
        
        history = ExecutionHistory(
            plan_id=plan_id,
            intent_hash=intent_hash,
            start_time=start_time,
            end_time=end_time,
            status=status,
            steps_succeeded=steps_succeeded,
            steps_failed=steps_failed,
            total_steps=total_steps,
            actual_time_seconds=actual_time_seconds,
            estimated_time_seconds=estimated_time_seconds,
            error_message=error_message,
            performance_score=min(100, max(0, performance_score)),
            feedback=feedback
        )
        
        # ذخیره در دیتابیس
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execution_history (
                    plan_id, intent_hash, start_time, end_time, status,
                    steps_succeeded, steps_failed, total_steps,
                    actual_time_seconds, estimated_time_seconds,
                    error_message, performance_score, feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id, intent_hash, start_time, end_time, status.value,
                steps_succeeded, steps_failed, total_steps,
                actual_time_seconds, estimated_time_seconds,
                error_message, history.performance_score, feedback
            ))
            conn.commit()
            
            cursor.execute("SELECT last_insert_rowid()")
            record_id = cursor.fetchone()[0]
        
        self.logger.info(f"ثبت اجرا: {plan_id} - وضعیت: {status.value}")
        return str(record_id)

    def learn_from_execution(
        self,
        history: ExecutionHistory,
        plan: ExecutionPlan,
        validation_report: ValidationReport
    ) -> List[LearningType]:
        """
        یادگیری از اجرای یک پلان
        
        بازگشت: لیست انواع یادگیری انجام شده
        """
        learned_types = []
        
        # یادگیری از موفقیت
        if history.status == PlanStatus.SUCCESSFUL:
            self._learn_from_success(history, plan)
            learned_types.append(LearningType.SUCCESS)
        
        # یادگیری از شکست
        elif history.status in (PlanStatus.FAILED, PlanStatus.TIMEOUT):
            self._learn_from_failure(history, plan, validation_report)
            learned_types.append(LearningType.FAILURE)
        
        # شناخت الگوهای مشترک
        pattern_found = self._identify_patterns(plan)
        if pattern_found:
            learned_types.append(LearningType.PATTERN)
        
        # پیشنهادات بهینه‌سازی
        optimization = self._generate_optimizations(history, plan)
        if optimization:
            learned_types.append(LearningType.OPTIMIZATION)
        
        self.logger.info(f"یادگیری انجام شد: {[t.value for t in learned_types]}")
        return learned_types

    def _learn_from_success(self, history: ExecutionHistory, plan: ExecutionPlan) -> None:
        """یادگیری از موفقیت"""
        step_sequence = "-".join([s.step_type.value for s in plan.steps])
        pattern_hash = hashlib.md5(step_sequence.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # بررسی اگر الگو قبلاً یادگیری شده
            cursor.execute(
                "SELECT id, execution_count, success_rate FROM learned_patterns WHERE pattern_hash = ?",
                (pattern_hash,)
            )
            result = cursor.fetchone()
            
            if result:
                # بروز‌رسانی الگو موجود
                pattern_id, exec_count, old_success_rate = result
                new_exec_count = exec_count + 1
                new_success_rate = (old_success_rate * exec_count + 100) / new_exec_count
                
                cursor.execute("""
                    UPDATE learned_patterns
                    SET execution_count = ?, success_rate = ?, last_seen = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_exec_count, new_success_rate, pattern_id))
            else:
                # ایجاد الگوی جدید
                cursor.execute("""
                    INSERT INTO learned_patterns
                    (pattern_hash, pattern_type, step_sequence, success_rate, execution_count, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (pattern_hash, "successful", step_sequence, 100.0, 1))
            
            conn.commit()

    def _learn_from_failure(
        self,
        history: ExecutionHistory,
        plan: ExecutionPlan,
        validation_report: ValidationReport
    ) -> None:
        """یادگیری از شکست"""
        # تحلیل مسائل
        if validation_report.issues:
            for issue in validation_report.issues[:3]:  # ۳ مسئله اول
                self.logger.warning(f"مسئله: {issue.message_fa}")

    def _identify_patterns(self, plan: ExecutionPlan) -> bool:
        """شناخت الگوهای مشترک"""
        if len(plan.steps) < 2:
            return False
        
        # جستجوی الگوهای تکراری
        step_sequence = "-".join([s.step_type.value for s in plan.steps])
        pattern_hash = hashlib.md5(step_sequence.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM learned_patterns WHERE pattern_hash = ?",
                (pattern_hash,)
            )
            count = cursor.fetchone()[0]
        
        return count > 0

    def _generate_optimizations(
        self,
        history: ExecutionHistory,
        plan: ExecutionPlan
    ) -> Optional[OptimizationSuggestion]:
        """تولید پیشنهادات بهینه‌سازی"""
        
        suggestions = []
        
        # پیشنهاد 1: کاهش timeout برای مراحل سریع
        if history.actual_time_seconds < history.estimated_time_seconds * 0.7:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="reduce_timeout",
                description_fa="زمان Timeout را برای مراحل سریع کاهش دهید",
                description_en="Reduce timeout for fast-executing steps",
                affected_steps=list(range(len(plan.steps))),
                expected_improvement=10.0,
                confidence=0.8
            ))
        
        # پیشنهاد 2: افزایش parallelization
        dependent_steps = sum(1 for s in plan.steps if s.dependencies)
        if dependent_steps < len(plan.steps) * 0.5:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="increase_parallelization",
                description_fa="مراحل مستقل را موازی اجرا کنید",
                description_en="Execute independent steps in parallel",
                affected_steps=[i for i, s in enumerate(plan.steps) if not s.dependencies],
                expected_improvement=20.0,
                confidence=0.7
            ))
        
        # پیشنهاد 3: کاهش retry برای مراحل موفق
        high_retry_steps = [i for i, s in enumerate(plan.steps) if s.retries > 3]
        if high_retry_steps and history.status == PlanStatus.SUCCESSFUL:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="reduce_retries",
                description_fa="تعداد تلاش‌های مجدد برای مراحل موفق کاهش یابد",
                description_en="Reduce retries for consistently successful steps",
                affected_steps=high_retry_steps,
                expected_improvement=5.0,
                confidence=0.6
            ))
        
        return suggestions[0] if suggestions else None

    def find_similar_plans(
        self,
        intent: Intent,
        threshold: float = 0.7
    ) -> List[PatternMatch]:
        """
        یافتن پلان‌های مشابه از تاریخچه
        
        پارامترها:
        - intent: Intent جدید
        - threshold: آستانه شباهت (0-1)
        
        بازگشت: لیست پلان‌های مشابه
        """
        intent_hash = self._hash_intent(intent)
        matches = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # جستجو در سابقه اجرا
            cursor.execute("""
                SELECT plan_id, status, performance_score, actual_time_seconds
                FROM execution_history
                WHERE intent_hash = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (intent_hash, PlanStatus.SUCCESSFUL.value))
            
            results = cursor.fetchall()
            
            for plan_id, status, performance_score, actual_time in results:
                similarity = 0.95 if status == PlanStatus.SUCCESSFUL.value else 0.8
                
                if similarity >= threshold:
                    history = ExecutionHistory(
                        plan_id=plan_id,
                        intent_hash=intent_hash,
                        start_time=datetime.now(),
                        status=PlanStatus.SUCCESSFUL,
                        performance_score=performance_score,
                        actual_time_seconds=actual_time
                    )
                    
                    match = PatternMatch(
                        pattern_id=plan_id,
                        similarity=similarity,
                        matched_steps=[],
                        execution_history=history
                    )
                    matches.append(match)
        
        return matches

    def get_statistics(self) -> Dict[str, Any]:
        """دریافت آمار کلی"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # تعداد کل اجراها
            cursor.execute("SELECT COUNT(*) FROM execution_history")
            total_executions = cursor.fetchone()[0]
            
            # موفقیت‌های کل
            cursor.execute(
                "SELECT COUNT(*) FROM execution_history WHERE status = ?",
                (PlanStatus.SUCCESSFUL.value,)
            )
            successful = cursor.fetchone()[0]
            
            # شکست‌های کل
            cursor.execute(
                "SELECT COUNT(*) FROM execution_history WHERE status = ?",
                (PlanStatus.FAILED.value,)
            )
            failed = cursor.fetchone()[0]
            
            # میانگین امتیاز عملکرد
            cursor.execute(
                "SELECT AVG(performance_score) FROM execution_history WHERE status = ?",
                (PlanStatus.SUCCESSFUL.value,)
            )
            avg_performance = cursor.fetchone()[0] or 0
            
            # تعداد الگوهای یادگیری شده
            cursor.execute("SELECT COUNT(*) FROM learned_patterns")
            patterns_learned = cursor.fetchone()[0]
            
            success_rate = (successful / total_executions * 100) if total_executions > 0 else 0
            
            return {
                "total_executions": total_executions,
                "successful": successful,
                "failed": failed,
                "success_rate": success_rate,
                "average_performance_score": avg_performance,
                "patterns_learned": patterns_learned
            }

    def _hash_intent(self, intent: Intent) -> str:
        """تولید Hash برای Intent"""
        intent_str = f"{intent.verb}:{intent.target}:{intent.language}"
        return hashlib.md5(intent_str.encode()).hexdigest()[:16]

    def cleanup_old_records(self, days: int = 30) -> int:
        """پاک‌کردن سابقه قدیمی‌تر از روز مشخص‌شده"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM execution_history WHERE created_at < ?",
                (cutoff_date,)
            )
            deleted_count = cursor.rowcount
            conn.commit()
        
        self.logger.info(f"{deleted_count} سابقه قدیمی حذف شد")
        return deleted_count

    def get_recommendations(self, intent: Intent) -> Dict[str, Any]:
        """
        دریافت توصیه‌ها برای یک Intent جدید بر اساس تاریخچه
        
        بازگشت: توصیه‌های بهینه‌سازی و الگوهای مشابه
        """
        similar_plans = self.find_similar_plans(intent, threshold=0.7)
        
        recommendations = {
            "similar_plans": len(similar_plans),
            "best_plan": None,
            "average_execution_time": 0,
            "success_rate": 0,
            "optimization_suggestions": []
        }
        
        if similar_plans:
            best = max(similar_plans, key=lambda x: x.execution_history.performance_score)
            recommendations["best_plan"] = best.pattern_id
            recommendations["average_execution_time"] = best.execution_history.actual_time_seconds
            recommendations["success_rate"] = 100.0
        
        stats = self.get_statistics()
        recommendations["memory_stats"] = stats
        
        return recommendations
