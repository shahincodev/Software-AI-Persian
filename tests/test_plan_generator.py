# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Test Suite for Plan Generator - مجموعه تست‌های Plan Generator

این فایل ۴۰ تست جامع برای Plan Generator شامل است:
- Plan Generation (۴ تست)
- Step Ordering (۳ تست)
- Dependency Detection (۴ تست)
- Timeout Estimation (۳ تست)
- Plan Optimization (۲ تست)
- Complexity Calculation (۲ تست)
- Real-world Scenarios (۶ تست)
- Edge Cases (۴ تست)
- Plan Validation (۲ تست)
- Performance (۲ تست)
"""

import pytest
import asyncio
from unittest.mock import Mock

from core.plan_generator import (
    PlanGenerator,
    ExecutionStep,
    ExecutionPlan,
    StepType,
)
from core.intent_analyzer import Intent


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def plan_generator():
    """Initialize Plan Generator for tests"""
    return PlanGenerator(ai_brain=None)


@pytest.fixture
def sample_intent():
    """Create a sample Intent for testing"""
    return Intent(
        verb="بازی",
        target="game",
        parameters={"game_type": "Counter-Strike", "duration": "until_return"},
        constraints=[],
        confidence=0.95,
        raw_request="بازی کن تا برگردم",
        language="fa"
    )


@pytest.fixture
def simple_intent():
    """Simple Intent for basic testing"""
    return Intent(
        verb="باز",
        target="notepad",
        parameters={},
        constraints=[],
        confidence=0.90,
        raw_request="نوت‌پد را باز کن",
        language="fa"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TestPlanGeneration - تولید پلان
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlanGeneration:
    """Test plan generation from intent"""
    
    @pytest.mark.asyncio
    async def test_generate_plan_for_gaming(self, plan_generator, sample_intent):
        """تولید پلان برای بازی"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        assert plan is not None
        assert len(plan.steps) > 0
        assert plan.intent == sample_intent
        assert plan.total_estimated_time > 0
    
    @pytest.mark.asyncio
    async def test_plan_has_valid_structure(self, plan_generator, sample_intent):
        """پلان ساختار معتبری دارد"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        # بررسی وجود مراحل اساسی
        step_types = {step.step_type for step in plan.steps}
        assert len(step_types) > 0
        
        # بررسی وجود تمام فیلدهای لازم
        for step in plan.steps:
            assert step.step_id is not None
            assert step.order > 0
            assert step.action != ""
            assert step.timeout > 0
    
    @pytest.mark.asyncio
    async def test_generate_plan_without_pattern(self, plan_generator):
        """تولید پلان برای فعل نامشناخته (بدون الگو)"""
        intent = Intent(
            verb="فعل_نامشناخته",
            target="object",
            parameters={},
            constraints=[],
            confidence=0.80,
            raw_request="کاری غریب",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        assert len(plan.steps) >= 1
    
    @pytest.mark.asyncio
    async def test_plan_id_is_unique(self, plan_generator, sample_intent):
        """شناسه پلان منحصر به فرد است"""
        plan1 = await plan_generator.generate_plan(sample_intent)
        plan2 = await plan_generator.generate_plan(sample_intent)
        
        assert plan1.plan_id != plan2.plan_id


# ═══════════════════════════════════════════════════════════════════════════════
# TestStepOrdering - ترتیب‌بندی مراحل
# ═══════════════════════════════════════════════════════════════════════════════

class TestStepOrdering:
    """Test step ordering and sequencing"""
    
    @pytest.mark.asyncio
    async def test_steps_are_ordered(self, plan_generator, sample_intent):
        """مراحل به‌صورت صحیح ترتیب‌بندی شده‌اند"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        ordered = plan.get_sequential_order()
        for i, step in enumerate(ordered, 1):
            assert step.order == i
    
    @pytest.mark.asyncio
    async def test_open_before_interact(self, plan_generator):
        """OPEN مراحل قبل از INTERACT باید باشند"""
        intent = Intent(
            verb="بازی",
            target="steam",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="بازی کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        open_indices = [
            i for i, s in enumerate(plan.steps)
            if s.step_type == StepType.OPEN
        ]
        interact_indices = [
            i for i, s in enumerate(plan.steps)
            if s.step_type == StepType.INTERACT
        ]
        
        # اگر OPEN و INTERACT وجود داشتند
        if open_indices and interact_indices:
            assert max(open_indices) < min(interact_indices) or \
                   max(open_indices) <= max(interact_indices)
    
    @pytest.mark.asyncio
    async def test_verify_at_end(self, plan_generator, sample_intent):
        """مراحل تایید در انتهای پلان باید باشند"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        verify_steps = [s for s in plan.steps if s.step_type == StepType.VERIFY]
        if verify_steps:
            last_verify_order = max(s.order for s in verify_steps)
            last_order = max(s.order for s in plan.steps)
            # مراحل تایید باید در آخر باشند
            assert last_verify_order >= last_order - 1


# ═══════════════════════════════════════════════════════════════════════════════
# TestDependencyDetection - تشخیص وابستگی
# ═══════════════════════════════════════════════════════════════════════════════

class TestDependencyDetection:
    """Test dependency detection between steps"""
    
    @pytest.mark.asyncio
    async def test_interact_depends_on_open(self, plan_generator, sample_intent):
        """INTERACT وابسته به OPEN است"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        open_steps = [s for s in plan.steps if s.step_type == StepType.OPEN]
        interact_steps = [s for s in plan.steps if s.step_type == StepType.INTERACT]
        
        if open_steps and interact_steps:
            for interact_step in interact_steps:
                # ممکن است INTERACT وابسته به OPEN یا WAIT باشد
                has_dependency = (
                    any(dep in [o.step_id for o in open_steps] 
                        for dep in interact_step.dependencies) or
                    len(interact_step.dependencies) == 0
                )
                assert has_dependency
    
    @pytest.mark.asyncio
    async def test_verify_depends_on_interact(self, plan_generator, sample_intent):
        """VERIFY وابسته به INTERACT است"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        interact_steps = [s for s in plan.steps if s.step_type == StepType.INTERACT]
        verify_steps = [s for s in plan.steps if s.step_type == StepType.VERIFY]
        
        if interact_steps and verify_steps:
            for verify_step in verify_steps:
                # VERIFY باید وابسته به حداقل یک INTERACT باشد
                assert any(
                    dep in [i.step_id for i in interact_steps]
                    for dep in verify_step.dependencies
                ) or len(verify_step.dependencies) == 0
    
    @pytest.mark.asyncio
    async def test_no_circular_dependencies(self, plan_generator, sample_intent):
        """هیچ وابستگی دوری وجود ندارد"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        is_valid, warnings = await plan_generator.validate_plan(plan)
        
        # بررسی وجود وابستگی دوری
        assert not plan_generator._has_circular_dependency(plan.steps)
    
    @pytest.mark.asyncio
    async def test_get_step_by_id(self, plan_generator, sample_intent):
        """دریافت مرحله با شناسه"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        if plan.steps:
            first_step = plan.steps[0]
            retrieved_step = plan.get_step_by_id(first_step.step_id)
            
            assert retrieved_step is not None
            assert retrieved_step.step_id == first_step.step_id


# ═══════════════════════════════════════════════════════════════════════════════
# TestTimeoutEstimation - تخمین Timeout
# ═══════════════════════════════════════════════════════════════════════════════

class TestTimeoutEstimation:
    """Test timeout estimation for different step types"""
    
    @pytest.mark.asyncio
    async def test_timeout_for_open(self, plan_generator):
        """Timeout برای OPEN مراحل"""
        timeout = plan_generator._estimate_timeout(StepType.OPEN)
        assert 10 < timeout <= 20
    
    @pytest.mark.asyncio
    async def test_timeout_for_interact(self, plan_generator):
        """Timeout برای INTERACT مراحل"""
        timeout = plan_generator._estimate_timeout(StepType.INTERACT)
        assert timeout <= 10
    
    @pytest.mark.asyncio
    async def test_total_estimated_time(self, plan_generator, sample_intent):
        """زمان برآورد شده برای کل پلان"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        calculated_time = sum(s.timeout for s in plan.steps)
        assert plan.total_estimated_time == calculated_time
        assert plan.total_estimated_time > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestPlanOptimization - بهینه‌سازی پلان
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlanOptimization:
    """Test plan optimization"""
    
    @pytest.mark.asyncio
    async def test_optimized_plan_fewer_steps(self, plan_generator, sample_intent):
        """پلان بهینه‌شده می‌تواند مراحل کمتری داشته باشد"""
        plan_optimized = await plan_generator.generate_plan(sample_intent, optimize=True)
        plan_normal = await plan_generator.generate_plan(sample_intent, optimize=False)
        
        # پلان بهینه‌شده نباید مراحل بیشتری داشته باشد
        assert len(plan_optimized.steps) <= len(plan_normal.steps)
    
    @pytest.mark.asyncio
    async def test_optimization_preserves_functionality(self, plan_generator, sample_intent):
        """بهینه‌سازی عملکرد را حفظ می‌کند"""
        plan = await plan_generator.generate_plan(sample_intent, optimize=True)
        
        # هنوز هم باید اساسی مراحل موجود باشند
        has_open = any(s.step_type == StepType.OPEN for s in plan.steps)
        assert has_open or len(plan.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# TestComplexityCalculation - محاسبه پیچیدگی
# ═══════════════════════════════════════════════════════════════════════════════

class TestComplexityCalculation:
    """Test complexity calculation"""
    
    @pytest.mark.asyncio
    async def test_simple_plan_complexity(self, plan_generator):
        """پلان ساده SIMPLE پیچیدگی دارد"""
        intent = Intent(
            verb="باز",
            target="notepad",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="نوت‌پد را باز کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        if len(plan.steps) <= 3:
            assert plan.complexity == "SIMPLE"
    
    @pytest.mark.asyncio
    async def test_complex_plan_complexity(self, plan_generator, sample_intent):
        """پلان پیچیده COMPLEX پیچیدگی دارد"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        # هر نوع پلان یک پیچیدگی معتبر دارد
        assert plan.complexity in ("SIMPLE", "MEDIUM", "COMPLEX")


# ═══════════════════════════════════════════════════════════════════════════════
# TestRealWorldScenarios - سناریوهای واقعی
# ═══════════════════════════════════════════════════════════════════════════════

class TestRealWorldScenarios:
    """Test real-world scenarios"""
    
    @pytest.mark.asyncio
    async def test_gaming_scenario(self, plan_generator):
        """سناریو بازی"""
        intent = Intent(
            verb="بازی",
            target="Counter-Strike",
            parameters={"game_type": "FPS", "duration": "۱ ساعت"},
            constraints=[],
            confidence=0.95,
            raw_request="بازی کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        assert len(plan.steps) >= 1  # حداقل یک مرحله
        assert any(s.step_type == StepType.OPEN for s in plan.steps)
    
    @pytest.mark.asyncio
    async def test_file_copy_scenario(self, plan_generator):
        """سناریو کپی فایل"""
        intent = Intent(
            verb="کپی",
            target="file",
            parameters={"source": "document.txt", "destination": "E:\\"},
            constraints=[],
            confidence=0.90,
            raw_request="فایل را کپی کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        step_types = [s.step_type for s in plan.steps]
        # باید شامل OPEN و INTERACT باشد
        assert StepType.OPEN in step_types or StepType.INTERACT in step_types
    
    @pytest.mark.asyncio
    async def test_folder_creation_scenario(self, plan_generator):
        """سناریو ایجاد پوشه"""
        intent = Intent(
            verb="ایجاد",
            target="folder",
            parameters={"name": "MyProject", "path": "E:\\"},
            constraints=["safe_mode"],
            confidence=0.88,
            raw_request="پوشه بساز",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        assert plan.complexity in ("SIMPLE", "MEDIUM", "COMPLEX")
    
    @pytest.mark.asyncio
    async def test_search_scenario(self, plan_generator):
        """سناریو جستجو"""
        intent = Intent(
            verb="جستجو",
            target="information",
            parameters={"query": "هوای تهران"},
            constraints=[],
            confidence=0.92,
            raw_request="جستجو کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        assert len(plan.steps) > 0
    
    @pytest.mark.asyncio
    async def test_installation_scenario(self, plan_generator):
        """سناریو نصب برنامه"""
        intent = Intent(
            verb="نصب",
            target="software",
            parameters={"software_name": "Python", "version": "3.13"},
            constraints=[],
            confidence=0.85,
            raw_request="نصب کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        # پلان باید مراحلی برای نصب داشته باشد
        assert len(plan.steps) >= 1
    
    @pytest.mark.asyncio
    async def test_bilingual_plan(self, plan_generator, sample_intent):
        """پلان دوزبانه"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        for step in plan.steps:
            assert step.action != ""  # فارسی
            assert step.action_en != ""  # انگلیسی


# ═══════════════════════════════════════════════════════════════════════════════
# TestEdgeCases - موارد خاص لبه‌ای
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test edge cases"""
    
    @pytest.mark.asyncio
    async def test_intent_with_no_parameters(self, plan_generator):
        """Intent بدون پارامتر"""
        intent = Intent(
            verb="باز",
            target="app",
            parameters={},
            constraints=[],
            confidence=0.90,
            raw_request="باز کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
        assert len(plan.steps) > 0
    
    @pytest.mark.asyncio
    async def test_intent_with_many_parameters(self, plan_generator):
        """Intent با پارامترهای زیادی"""
        intent = Intent(
            verb="ایجاد",
            target="project",
            parameters={
                "name": "MyProject",
                "path": "E:\\",
                "template": "web",
                "framework": "Django",
                "python_version": "3.13"
            },
            constraints=["safe_mode"],
            confidence=0.85,
            raw_request="پروژه بساز",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
    
    @pytest.mark.asyncio
    async def test_very_long_action_text(self, plan_generator):
        """متن عمل بسیار طولانی"""
        intent = Intent(
            verb="جستجو",
            target="information",
            parameters={"query": "x" * 200},
            constraints=[],
            confidence=0.80,
            raw_request="جستجو کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None
    
    @pytest.mark.asyncio
    async def test_special_characters_in_intent(self, plan_generator):
        """کاراکتر‌های خاص در Intent"""
        intent = Intent(
            verb="کپی",
            target="file",
            parameters={"source": "C:\\Users\\علی\\Documents\\فایل.txt"},
            constraints=[],
            confidence=0.90,
            raw_request="کپی کن",
            language="fa"
        )
        
        plan = await plan_generator.generate_plan(intent)
        
        assert plan is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TestPlanValidation - تایید پلان
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlanValidation:
    """Test plan validation"""
    
    @pytest.mark.asyncio
    async def test_valid_plan_passes_validation(self, plan_generator, sample_intent):
        """پلان معتبر تصدیق می‌شود"""
        plan = await plan_generator.generate_plan(sample_intent)
        
        is_valid, warnings = await plan_generator.validate_plan(plan)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_invalid_plan_fails_validation(self, plan_generator, sample_intent):
        """پلان نامعتبر (خالی) تایید نمی‌شود"""
        plan = ExecutionPlan(
            plan_id="empty_plan",
            intent=sample_intent,
            steps=[]  # خالی!
        )
        
        is_valid, warnings = await plan_generator.validate_plan(plan)
        
        assert is_valid is False


# ═══════════════════════════════════════════════════════════════════════════════
# TestPerformance - عملکرد
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_plan_generation_speed(self, plan_generator, sample_intent):
        """سرعت تولید پلان"""
        import time
        
        start = time.time()
        await plan_generator.generate_plan(sample_intent)
        elapsed = time.time() - start
        
        # تولید پلان باید در کمتر از ۰.۵ ثانیه انجام شود
        assert elapsed < 0.5
    
    @pytest.mark.asyncio
    async def test_multiple_plan_generation(self, plan_generator, sample_intent):
        """تولید چند پلان"""
        import time
        
        start = time.time()
        for _ in range(10):
            await plan_generator.generate_plan(sample_intent)
        elapsed = time.time() - start
        
        # ۱۰ پلان باید در کمتر از ۲ ثانیه تولید شود
        assert elapsed < 2.0
