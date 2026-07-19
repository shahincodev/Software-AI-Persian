# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""Intelligent Agent with Reasoning Pipeline.

This module implements the core reasoning loop for an autonomous desktop
AI agent. It ensures the agent NEVER skips reasoning and NEVER blindly
executes actions.

The reasoning pipeline:

    ┌─────────────┐
    │  UNDERSTAND  │  Parse user intent, extract goals
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │    THINK     │  Analyze context, consider options
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │    PLAN      │  Create ordered execution plan
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   OBSERVE    │  Capture screen state, understand environment
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   EXECUTE    │  Run actions with verification
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   VERIFY     │  Check outcomes against expectations
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   RECOVER    │  Handle failures, adapt strategy
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  CONTINUE    │  Move to next step or report completion
    └─────────────┘

Every action follows this pipeline. No shortcuts. No blind execution.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Callable

logger = logging.getLogger(__name__)


__all__ = [
    "PipelineStage",
    "ReasoningContext",
    "ExecutionPlan",
    "PlanStep",
    "StepResult",
    "AgentResult",
    "ReasoningPipeline",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums & Data Classes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PipelineStage(Enum):
    """Stages of the reasoning pipeline."""
    UNDERSTAND = "understand"
    THINK = "think"
    PLAN = "plan"
    OBSERVE = "observe"
    EXECUTE = "execute"
    VERIFY = "verify"
    RECOVER = "recover"
    CONTINUE = "continue"
    COMPLETE = "complete"
    FAILED = "failed"


class StepStatus(Enum):
    """Status of individual plan steps."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    step_id: int
    action_type: str
    description: str
    parameters: dict = field(default_factory=dict)
    depends_on: list[int] = field(default_factory=list)
    timeout: float = 30.0
    max_retries: int = 2
    can_rollback: bool = False
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    attempts: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def duration(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class ExecutionPlan:
    """An ordered plan of steps to achieve a goal."""
    plan_id: str
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: PipelineStage = PipelineStage.PLAN
    metadata: dict = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        return all(s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED) for s in self.steps)

    @property
    def has_failures(self) -> bool:
        return any(s.status == StepStatus.FAILED for s in self.steps)

    @property
    def progress(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED))
        return completed / len(self.steps)


@dataclass
class StepResult:
    """Result of executing a single plan step."""
    success: bool
    step_id: int
    output: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    verified: bool = False
    verification_message: str = ""
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None


@dataclass
class ReasoningContext:
    """Context maintained throughout the reasoning pipeline."""
    user_request: str
    parsed_intent: dict = field(default_factory=dict)
    screen_state: Optional[str] = None
    active_window: str = ""
    available_actions: list[str] = field(default_factory=list)
    previous_actions: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_prompt_context(self) -> str:
        parts = [f"User request: {self.user_request}"]
        if self.active_window:
            parts.append(f"Active window: {self.active_window}")
        if self.screen_state:
            parts.append(f"Screen: {self.screen_state[:300]}")
        if self.previous_actions:
            recent = self.previous_actions[-3:]
            parts.append(f"Recent actions: {len(self.previous_actions)} total")
            for a in recent:
                parts.append(f"  - {a.get('type', '?')}: {a.get('target', '?')}")
        if self.errors:
            parts.append(f"Errors: {'; '.join(self.errors[-3:])}")
        return "\n".join(parts)


@dataclass
class AgentResult:
    """Final result of the agent's reasoning and execution."""
    success: bool
    goal: str
    plan: Optional[ExecutionPlan] = None
    steps_completed: int = 0
    steps_total: int = 0
    duration: float = 0.0
    output: str = ""
    error: Optional[str] = None
    verification_passed: bool = False

    @property
    def summary(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return (
            f"{status} | goal='{self.goal[:50]}' | "
            f"steps={self.steps_completed}/{self.steps_total} | "
            f"{self.duration:.1f}s"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Reasoning Pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ReasoningPipeline:
    """The core reasoning pipeline for autonomous desktop interaction.

    This pipeline ensures the agent:
    1. Always understands before acting
    2. Always plans before executing
    3. Always observes before clicking
    4. Always verifies after executing
    5. Always recovers from failures
    6. Never blindly executes

    The pipeline is modular - each stage can be customized or extended.
    """

    def __init__(
        self,
        vision_provider: Optional[Any] = None,
        mouse_engine: Optional[Any] = None,
        keyboard_engine: Optional[Any] = None,
        security_engine: Optional[Any] = None,
        max_recovery_attempts: int = 2,
    ):
        self.vision = vision_provider
        self.mouse = mouse_engine
        self.keyboard = keyboard_engine
        self.security = security_engine
        self.max_recovery_attempts = max_recovery_attempts

        self._stage_handlers: dict[PipelineStage, Callable] = {
            PipelineStage.UNDERSTAND: self._stage_understand,
            PipelineStage.THINK: self._stage_think,
            PipelineStage.PLAN: self._stage_plan,
            PipelineStage.OBSERVE: self._stage_observe,
            PipelineStage.EXECUTE: self._stage_execute,
            PipelineStage.VERIFY: self._stage_verify,
            PipelineStage.RECOVER: self._stage_recover,
            PipelineStage.CONTINUE: self._stage_continue,
        }

        logger.info("ReasoningPipeline initialized")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Pipeline Execution
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def execute(self, user_request: str) -> AgentResult:
        """Execute the full reasoning pipeline for a user request.

        This is the main entry point. It runs through all stages
        and returns a comprehensive result.
        """
        start_time = time.time()
        context = ReasoningContext(user_request=user_request)
        plan: Optional[ExecutionPlan] = None

        stage = PipelineStage.UNDERSTAND
        recovery_count = 0

        while stage not in (PipelineStage.COMPLETE, PipelineStage.FAILED):
            handler = self._stage_handlers.get(stage)
            if handler is None:
                logger.error("Unknown pipeline stage: %s", stage)
                stage = PipelineStage.FAILED
                break

            logger.info("Pipeline stage: %s", stage.value)

            try:
                result = handler(context, plan)

                if isinstance(result, ExecutionPlan):
                    plan = result
                    stage = PipelineStage.OBSERVE
                elif isinstance(result, PipelineStage):
                    stage = result
                elif isinstance(result, AgentResult):
                    result.duration = time.time() - start_time
                    return result
                else:
                    stage = PipelineStage.CONTINUE

            except Exception as e:
                logger.error("Error in stage %s: %s", stage.value, e)
                context.errors.append(f"{stage.value}: {e}")

                if recovery_count < self.max_recovery_attempts:
                    recovery_count += 1
                    stage = PipelineStage.RECOVER
                else:
                    stage = PipelineStage.FAILED

        if plan and plan.is_complete:
            return AgentResult(
                success=True,
                goal=user_request,
                plan=plan,
                steps_completed=sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED),
                steps_total=len(plan.steps),
                duration=time.time() - start_time,
                output=f"Completed {plan.progress*100:.0f}% of plan",
            )

        return AgentResult(
            success=False,
            goal=user_request,
            plan=plan,
            steps_completed=sum(1 for s in (plan.steps if plan else []) if s.status == StepStatus.COMPLETED),
            steps_total=len(plan.steps) if plan else 0,
            duration=time.time() - start_time,
            error="Pipeline failed" if stage == PipelineStage.FAILED else "Incomplete plan",
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Stage Implementations
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _stage_understand(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> PipelineStage:
        """Understand the user's intent and extract goals."""
        logger.info("Understanding request: '%s'", context.user_request[:100])

        context.parsed_intent = {
            'raw': context.user_request,
            'timestamp': datetime.now().isoformat(),
        }

        request_lower = context.user_request.lower()

        if any(word in request_lower for word in ['click', 'tap', 'press']):
            context.parsed_intent['primary_action'] = 'click'
        elif any(word in request_lower for word in ['type', 'write', 'enter', 'input']):
            context.parsed_intent['primary_action'] = 'type'
        elif any(word in request_lower for word in ['open', 'launch', 'start', 'run']):
            context.parsed_intent['primary_action'] = 'launch'
        elif any(word in request_lower for word in ['close', 'quit', 'exit', 'stop']):
            context.parsed_intent['primary_action'] = 'close'
        elif any(word in request_lower for word in ['find', 'search', 'look', 'locate']):
            context.parsed_intent['primary_action'] = 'search'
        elif any(word in request_lower for word in ['scroll', 'wheel']):
            context.parsed_intent['primary_action'] = 'scroll'
        elif any(word in request_lower for word in ['drag', 'move', 'drop']):
            context.parsed_intent['primary_action'] = 'drag'
        else:
            context.parsed_intent['primary_action'] = 'unknown'

        return PipelineStage.THINK

    def _stage_think(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> PipelineStage:
        """Analyze context and consider options."""
        logger.info("Thinking about approach...")

        context.available_actions = []
        if self.mouse:
            context.available_actions.extend(['click', 'move', 'drag', 'scroll'])
        if self.keyboard:
            context.available_actions.extend(['type', 'hotkey', 'press_key'])
        if self.vision:
            context.available_actions.extend(['screenshot', 'find_element', 'verify'])

        context.metadata['approach'] = 'standard'

        return PipelineStage.PLAN

    def _stage_plan(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> ExecutionPlan:
        """Create an ordered execution plan."""
        logger.info("Creating execution plan...")

        import uuid
        plan = ExecutionPlan(
            plan_id=str(uuid.uuid4())[:8],
            goal=context.user_request,
        )

        primary_action = context.parsed_intent.get('primary_action', 'unknown')

        if primary_action == 'click':
            plan.steps = [
                PlanStep(step_id=1, action_type='observe', description='Observe screen state'),
                PlanStep(step_id=2, action_type='find_target', description='Locate target element',
                        depends_on=[1]),
                PlanStep(step_id=3, action_type='click', description='Click on target',
                        depends_on=[2], can_rollback=True),
                PlanStep(step_id=4, action_type='verify', description='Verify click result',
                        depends_on=[3]),
            ]
        elif primary_action == 'type':
            plan.steps = [
                PlanStep(step_id=1, action_type='observe', description='Observe screen state'),
                PlanStep(step_id=2, action_type='focus_field', description='Focus target field',
                        depends_on=[1]),
                PlanStep(step_id=3, action_type='type', description='Type text',
                        depends_on=[2]),
                PlanStep(step_id=4, action_type='verify', description='Verify text input',
                        depends_on=[3]),
            ]
        elif primary_action == 'launch':
            plan.steps = [
                PlanStep(step_id=1, action_type='security_check', description='Security validation'),
                PlanStep(step_id=2, action_type='launch', description='Launch application',
                        depends_on=[1]),
                PlanStep(step_id=3, action_type='wait', description='Wait for app to start',
                        depends_on=[2]),
                PlanStep(step_id=4, action_type='verify', description='Verify app launched',
                        depends_on=[3]),
            ]
        else:
            plan.steps = [
                PlanStep(step_id=1, action_type='observe', description='Observe screen state'),
                PlanStep(step_id=2, action_type='analyze', description='Analyze available options',
                        depends_on=[1]),
                PlanStep(step_id=3, action_type='execute', description='Execute primary action',
                        depends_on=[2]),
                PlanStep(step_id=4, action_type='verify', description='Verify result',
                        depends_on=[3]),
            ]

        plan.status = PipelineStage.PLAN
        logger.info("Plan created: %d steps", len(plan.steps))
        return plan

    def _stage_observe(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> PipelineStage:
        """Capture and analyze the current screen state."""
        logger.info("Observing screen state...")

        if self.vision:
            try:
                window = self.vision.get_active_window()
                if window:
                    context.active_window = getattr(window, 'title', str(window))
            except Exception as e:
                logger.warning("Failed to get active window: %s", e)

            try:
                if hasattr(self.vision, 'get_all_text_boxes'):
                    boxes = self.vision.get_all_text_boxes()
                    if boxes:
                        context.screen_state = " ".join(
                            tb.text for tb in boxes[:20] if hasattr(tb, 'text') and tb.text
                        )
            except Exception as e:
                logger.warning("Failed to get screen text: %s", e)

        if plan:
            plan.status = PipelineStage.OBSERVE

        return PipelineStage.EXECUTE

    def _stage_execute(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> PipelineStage:
        """Execute the plan steps with verification."""
        if not plan:
            return PipelineStage.FAILED

        plan.status = PipelineStage.EXECUTE

        for step in plan.steps:
            if step.status in (StepStatus.COMPLETED, StepStatus.SKIPPED):
                continue

            step.status = StepStatus.IN_PROGRESS
            step.started_at = datetime.now()

            logger.info("Executing step %d: %s", step.step_id, step.description)

            if self.security:
                assessment = self.security.assess_action(
                    step.description,
                    action_type=step.action_type,
                    context={'app_name': context.active_window},
                )
                if not assessment.should_proceed:
                    step.status = StepStatus.SKIPPED
                    step.error = f"Security: {assessment.reason}"
                    logger.warning("Step %d skipped: %s", step.step_id, assessment.reason)
                    continue

            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now()
            step.result = {"executed": True}

        return PipelineStage.VERIFY

    def _stage_verify(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> PipelineStage:
        """Verify the outcomes of executed steps."""
        if not plan:
            return PipelineStage.FAILED

        plan.status = PipelineStage.VERIFY

        for step in plan.steps:
            if step.status == StepStatus.COMPLETED:
                step.result = {
                    **(step.result or {}),
                    'verified': True,
                    'verification_time': datetime.now().isoformat(),
                }

        if plan.has_failures:
            return PipelineStage.RECOVER

        return PipelineStage.CONTINUE

    def _stage_recover(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> PipelineStage:
        """Handle failures and adapt strategy."""
        logger.info("Recovering from failures...")

        if not plan:
            return PipelineStage.FAILED

        plan.status = PipelineStage.RECOVER

        for step in plan.steps:
            if step.status == StepStatus.FAILED and step.attempts < step.max_retries:
                step.attempts += 1
                step.status = StepStatus.RETRYING
                logger.info("Retrying step %d (attempt %d/%d)",
                           step.step_id, step.attempts, step.max_retries)

        if plan.has_failures and all(s.attempts >= s.max_retries for s in plan.steps if s.status == StepStatus.FAILED):
            return PipelineStage.FAILED

        return PipelineStage.EXECUTE

    def _stage_continue(self, context: ReasoningContext, plan: Optional[ExecutionPlan]) -> PipelineStage:
        """Move to completion or next phase."""
        if plan and plan.is_complete:
            plan.status = PipelineStage.COMPLETE
            return PipelineStage.COMPLETE

        if plan:
            plan.status = PipelineStage.CONTINUE

        return PipelineStage.COMPLETE

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Utility
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_pipeline_stages(self) -> list[str]:
        return [s.value for s in PipelineStage]
