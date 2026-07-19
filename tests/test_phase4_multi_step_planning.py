# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
Test Suite for Phase 4 - Multi-Step Planning

Tests for StepTracker, WorkflowEngine, and ToolExecutor plan integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from core.step_tracker import StepTracker, StepStatus
from core.plan_generator import (
    PlanGenerator, ExecutionPlan, ExecutionStep, StepType
)
from core.plan_validator import PlanValidator, ValidationStatus
from core.intent_analyzer import Intent


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_intent():
    return Intent(
        verb="create",
        target="folder",
        parameters={"name": "TestFolder"},
        confidence=0.9,
        raw_request="Create a folder called TestFolder on desktop",
        language="en",
    )


@pytest.fixture
def sample_steps():
    return [
        ExecutionStep(
            step_id="step_1", order=1,
            action="Create folder", action_en="Create folder",
            step_type=StepType.INTERACT, target="TestFolder",
            dependencies=[], timeout=10,
        ),
        ExecutionStep(
            step_id="step_2", order=2,
            action="Create file", action_en="Create file",
            step_type=StepType.INTERACT, target="hello.py",
            dependencies=["step_1"], timeout=10,
        ),
        ExecutionStep(
            step_id="step_3", order=3,
            action="Run script", action_en="Run script",
            step_type=StepType.PROCESS, target="hello.py",
            dependencies=["step_2"], timeout=15,
        ),
        ExecutionStep(
            step_id="step_4", order=4,
            action="Verify result", action_en="Verify result",
            step_type=StepType.VERIFY, target="output",
            dependencies=["step_3"], timeout=10,
        ),
    ]


@pytest.fixture
def sample_plan(sample_intent, sample_steps):
    return ExecutionPlan(
        plan_id="plan_test_1",
        intent=sample_intent,
        steps=sample_steps,
        total_estimated_time=45,
        complexity="MEDIUM",
        description="Test plan",
    )


@pytest.fixture
def mock_tool_executor():
    executor = Mock()
    executor.execute = AsyncMock(return_value=[
        {"status": "success", "description": "test", "output": "done"}
    ])
    return executor


# ═══════════════════════════════════════════════════════════════════════════════
# StepTracker Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestStepTracker:

    def test_create_tracker(self):
        tracker = StepTracker(plan_id="p1", total_steps=5)
        assert tracker.plan_id == "p1"
        assert tracker.total_steps == 5
        assert tracker.progress_percent == 0.0
        assert not tracker.is_complete

    def test_start_and_finish(self):
        tracker = StepTracker(plan_id="p1", total_steps=2)
        tracker.start()
        assert tracker.started_at is not None
        tracker.finish()
        assert tracker.finished_at is not None
        assert tracker.elapsed_ms >= 0

    def test_complete_step_success(self):
        tracker = StepTracker(plan_id="p1", total_steps=2)
        tracker.start()
        tracker.start_step("s1", 1, "Do something")
        result = tracker.complete_step("s1", output="done")
        assert result.status == StepStatus.SUCCESS
        assert result.output == "done"
        assert tracker.completed_count == 1
        assert tracker.success_count == 1

    def test_complete_step_failure(self):
        tracker = StepTracker(plan_id="p1", total_steps=2)
        tracker.start()
        tracker.start_step("s1", 1, "Do something")
        result = tracker.complete_step("s1", error="failed")
        assert result.status == StepStatus.FAILED
        assert result.error == "failed"
        assert tracker.failed_count == 1

    def test_skip_step(self):
        tracker = StepTracker(plan_id="p1", total_steps=3)
        tracker.start()
        result = tracker.skip_step("s1", "Not needed")
        assert result.status == StepStatus.SKIPPED

    def test_retry_step(self):
        tracker = StepTracker(plan_id="p1", total_steps=1)
        tracker.start()
        tracker.start_step("s1", 1, "Action")
        tracker.fail_step("s1", "error")
        tracker.retry_step("s1")
        result = next(r for r in tracker.results if r.step_id == "s1")
        assert result.status == StepStatus.RETRYING
        assert result.attempts == 2

    def test_progress_percent(self):
        tracker = StepTracker(plan_id="p1", total_steps=4)
        tracker.start()
        tracker.start_step("s1", 1, "A")
        tracker.complete_step("s1")
        assert tracker.progress_percent == 25.0
        tracker.start_step("s2", 2, "B")
        tracker.complete_step("s2")
        assert tracker.progress_percent == 50.0

    def test_is_complete(self):
        tracker = StepTracker(plan_id="p1", total_steps=2)
        tracker.start()
        tracker.start_step("s1", 1, "A")
        tracker.complete_step("s1")
        assert not tracker.is_complete
        tracker.start_step("s2", 2, "B")
        tracker.complete_step("s2")
        assert tracker.is_complete

    def test_has_failures(self):
        tracker = StepTracker(plan_id="p1", total_steps=2)
        tracker.start()
        tracker.start_step("s1", 1, "A")
        tracker.complete_step("s1")
        assert not tracker.has_failures
        tracker.start_step("s2", 2, "B")
        tracker.complete_step("s2", error="oops")
        assert tracker.has_failures

    def test_get_summary(self):
        tracker = StepTracker(plan_id="p1", total_steps=2, description="Test")
        tracker.start()
        tracker.start_step("s1", 1, "A")
        tracker.complete_step("s1")
        tracker.finish()
        summary = tracker.get_summary()
        assert summary["plan_id"] == "p1"
        assert summary["total_steps"] == 2
        assert summary["completed"] == 1
        assert summary["is_complete"] is False

    def test_get_status_line(self):
        tracker = StepTracker(plan_id="p1", total_steps=3)
        tracker.start()
        line = tracker.get_status_line()
        assert "p1" in line
        assert "0/3" in line

    def test_get_failed_steps(self):
        tracker = StepTracker(plan_id="p1", total_steps=3)
        tracker.start()
        tracker.start_step("s1", 1, "A")
        tracker.complete_step("s1")
        tracker.start_step("s2", 2, "B")
        tracker.complete_step("s2", error="fail")
        tracker.start_step("s3", 3, "C")
        tracker.complete_step("s3")
        failed = tracker.get_failed_steps()
        assert len(failed) == 1
        assert failed[0].step_id == "s2"


# ═══════════════════════════════════════════════════════════════════════════════
# PlanGenerator Tests (Phase 4 additions)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlanGeneratorPhase4:

    def test_generate_plan_from_intent(self):
        gen = PlanGenerator(ai_brain=None)
        intent = Intent(
            verb="create", target="folder",
            parameters={"name": "TestFolder"},
            confidence=0.9, raw_request="Create TestFolder",
        )
        plan = asyncio.get_event_loop().run_until_complete(
            gen.generate_plan(intent)
        )
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.steps) > 0
        assert plan.plan_id.startswith("plan_")

    def test_plan_has_ordered_steps(self):
        gen = PlanGenerator(ai_brain=None)
        intent = Intent(
            verb="بازی", target="game",
            confidence=0.9, raw_request="بازی game",
        )
        plan = asyncio.get_event_loop().run_until_complete(
            gen.generate_plan(intent)
        )
        orders = [s.order for s in plan.steps]
        assert orders == sorted(orders)

    def test_plan_complexity(self):
        gen = PlanGenerator(ai_brain=None)
        intent = Intent(
            verb="ایجاد", target="folder",
            confidence=0.9, raw_request="ایجاد folder",
        )
        plan = asyncio.get_event_loop().run_until_complete(
            gen.generate_plan(intent)
        )
        assert plan.complexity in ("SIMPLE", "MEDIUM", "COMPLEX")

    def test_plan_steps_have_ids(self):
        gen = PlanGenerator(ai_brain=None)
        intent = Intent(
            verb="جستجو", target="query",
            confidence=0.9, raw_request="search query",
        )
        plan = asyncio.get_event_loop().run_until_complete(
            gen.generate_plan(intent)
        )
        for step in plan.steps:
            assert step.step_id
            assert len(step.step_id) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# PlanValidator Tests (Phase 4 additions)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlanValidatorPhase4:

    def test_validate_valid_plan(self, sample_plan, sample_intent):
        validator = PlanValidator(ai_brain=None)
        report = asyncio.get_event_loop().run_until_complete(
            validator.validate(sample_plan, sample_intent)
        )
        assert report.is_valid
        assert report.status in (ValidationStatus.VALID, ValidationStatus.WARNING)

    def test_validate_empty_plan(self, sample_intent):
        validator = PlanValidator(ai_brain=None)
        plan = ExecutionPlan(
            plan_id="empty", intent=sample_intent, steps=[],
        )
        report = asyncio.get_event_loop().run_until_complete(
            validator.validate(plan, sample_intent)
        )
        assert not report.is_valid


# ═══════════════════════════════════════════════════════════════════════════════
# WorkflowEngine Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestWorkflowEngine:

    def test_create_engine(self, mock_tool_executor):
        from core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        assert engine.tool_executor == mock_tool_executor
        assert not engine.validate_before_execute

    def test_execute_simple_plan(self, mock_tool_executor, sample_plan):
        from core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute(sample_plan)
        )
        assert result.plan_id == "plan_test_1"
        assert result.total_steps == 4
        assert result.completed_steps == 4

    def test_execute_plan_with_failure(self, mock_tool_executor, sample_plan):
        from core.workflow_engine import WorkflowEngine

        # Track which step IDs have been called
        call_count = 0
        async def mock_execute(calls):
            nonlocal call_count
            call_count += 1
            # Fail on the first attempt for any call
            if call_count == 1:
                return [{"status": "failed", "description": "step1", "error": "fail"}]
            return [{"status": "success", "description": "ok", "output": ""}]

        mock_tool_executor.execute = mock_execute
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
            max_retries_per_step=0,  # No retries so failure sticks
        )
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute(sample_plan)
        )
        assert result.failed_steps > 0

    def test_dependencies_satisfied(self, mock_tool_executor):
        from core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        tracker = StepTracker(plan_id="p1", total_steps=3)
        tracker.start()
        tracker.start_step("s1", 1, "A")
        tracker.complete_step("s1")

        step_with_dep = ExecutionStep(
            step_id="s2", order=2,
            action="B", action_en="B",
            step_type=StepType.INTERACT, target="x",
            dependencies=["s1"],
        )
        assert engine._dependencies_satisfied(step_with_dep, tracker)

        step_no_dep = ExecutionStep(
            step_id="s3", order=3,
            action="C", action_en="C",
            step_type=StepType.INTERACT, target="x",
            dependencies=["s1", "s2"],
        )
        assert not engine._dependencies_satisfied(step_no_dep, tracker)

    def test_step_to_tool_call_interact_type(self, mock_tool_executor):
        from core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        step = ExecutionStep(
            step_id="s1", order=1,
            action="type hello", action_en="type hello",
            step_type=StepType.INTERACT, target="field",
            parameters={"text": "hello"},
        )
        tool_call = engine._step_to_tool_call(step)
        assert tool_call is not None
        assert tool_call["tool"] == "type_text"
        assert tool_call["params"]["text"] == "hello"

    def test_step_to_tool_call_open(self, mock_tool_executor):
        from core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        step = ExecutionStep(
            step_id="s1", order=1,
            action="Open Chrome", action_en="Open Chrome",
            step_type=StepType.OPEN, target="chrome.exe",
        )
        tool_call = engine._step_to_tool_call(step)
        assert tool_call["tool"] == "launch_app"

    def test_step_to_tool_call_verify(self, mock_tool_executor):
        from core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        step = ExecutionStep(
            step_id="s1", order=1,
            action="Verify success", action_en="Verify success",
            step_type=StepType.VERIFY, target="output",
        )
        tool_call = engine._step_to_tool_call(step)
        assert tool_call["tool"] == "verify_action"

    def test_workflow_result_to_dict(self, mock_tool_executor, sample_plan):
        from core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute(sample_plan)
        )
        d = result.to_dict()
        assert "plan_id" in d
        assert "success" in d
        assert "total_steps" in d
        assert "step_results" in d


# ═══════════════════════════════════════════════════════════════════════════════
# ToolExecutor Plan Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestToolExecutorPlanIntegration:

    def test_needs_powershell_wrapper_variables(self):
        from main import ToolExecutor
        assert ToolExecutor._needs_powershell_wrapper("$x = Get-Date")
        assert ToolExecutor._needs_powershell_wrapper("Get-ChildItem -Path D:\\")
        assert not ToolExecutor._needs_powershell_wrapper("mkdir test")

    def test_needs_powershell_wrapper_here_string(self):
        from main import ToolExecutor
        assert ToolExecutor._needs_powershell_wrapper("Set-Content -Value @'\ntest\n'@")
        assert ToolExecutor._needs_powershell_wrapper('"@" content "@')

    def test_needs_powershell_wrapper_cmdlets(self):
        from main import ToolExecutor
        assert ToolExecutor._needs_powershell_wrapper("Set-Content -Path x -Value y")
        assert ToolExecutor._needs_powershell_wrapper("Get-ChildItem -Path .")
        assert ToolExecutor._needs_powershell_wrapper("New-Item -ItemType Directory")
        assert ToolExecutor._needs_powershell_wrapper("Test-Path 'C:\\'")

    def test_needs_powershell_wrapper_explicit(self):
        from main import ToolExecutor
        assert ToolExecutor._needs_powershell_wrapper("anything", shell_type="powershell")
        assert not ToolExecutor._needs_powershell_wrapper("anything", shell_type="cmd")


# ═══════════════════════════════════════════════════════════════════════════════
# Integration Test
# ═══════════════════════════════════════════════════════════════════════════════

class TestPhase4Integration:

    def test_full_workflow(self, mock_tool_executor, sample_intent):
        from core.workflow_engine import WorkflowEngine
        from core.plan_generator import PlanGenerator

        gen = PlanGenerator(ai_brain=None)
        plan = asyncio.get_event_loop().run_until_complete(
            gen.generate_plan(sample_intent)
        )

        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )
        result = asyncio.get_event_loop().run_until_complete(
            engine.execute(plan)
        )

        assert result.plan_id == plan.plan_id
        assert result.total_steps == len(plan.steps)
        assert result.completed_steps == result.total_steps

    def test_tracker_and_workflow_together(self, mock_tool_executor, sample_plan):
        from core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine(
            tool_executor=mock_tool_executor,
            validate_before_execute=False,
        )

        progress_updates = []
        def on_complete(info):
            progress_updates.append(info)

        result = asyncio.get_event_loop().run_until_complete(
            engine.execute(sample_plan, on_step_complete=on_complete)
        )

        assert len(progress_updates) == len(sample_plan.steps)
        assert result.success
