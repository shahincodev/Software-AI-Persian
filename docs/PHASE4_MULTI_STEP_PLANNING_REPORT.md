# Phase 4 — Intelligent Multi-Step Planning

**Version**: 0.6.0  
**Date**: 2026-07-04  
**Author**: Shahin (shahincodev)

---

## Overview

Phase 4 completes the multi-step planning system that was partially implemented in earlier phases. The existing `PlanGenerator` and `PlanValidator` modules are now fully integrated into the main agent loop via a new `WorkflowEngine`, enabling the agent to break down complex user requests into ordered steps, validate them for safety and correctness, and execute them end-to-end with progress tracking.

---

## What Was Already Implemented

| Module | Status | Description |
|--------|--------|-------------|
| `core/plan_generator.py` | Existed | Generates ExecutionPlan from Intent with dependency detection, topological sort, and optimization |
| `core/plan_validator.py` | Existed | Validates plans for structure, security, dependencies, and resources |

These modules were functional but **not wired into the main execution pipeline** in `main.py`.

---

## What Was Added

### 1. `core/step_tracker.py` (NEW)

Tracks real-time execution progress of a workflow.

**Key Features:**
- `StepStatus` enum: PENDING, RUNNING, SUCCESS, FAILED, SKIPPED, RETRYING
- `StepResult` dataclass: captures per-step output, error, duration, attempts
- `StepTracker` class:
  - `start()` / `finish()` — workflow lifecycle
  - `start_step()` / `complete_step()` / `fail_step()` / `skip_step()` / `retry_step()` — step lifecycle
  - `progress_percent` — real-time progress calculation
  - `get_summary()` — full execution summary dict
  - `get_failed_steps()` / `get_successful_steps()` — filtered results

**Lines:** ~180

### 2. `core/workflow_engine.py` (NEW)

Executes an `ExecutionPlan` end-to-end with dependency resolution and failure recovery.

**Key Features:**
- `WorkflowEngine.execute(plan)` — main entry point
- Dependency checking: skips steps whose dependencies haven't succeeded
- Retry logic with exponential backoff (configurable per-step and global max)
- `fail_fast` mode: abort remaining steps on first failure
- Step-to-tool-call mapping: converts each `ExecutionStep` type (OPEN, INTERACT, PROCESS, SAVE, VERIFY, WAIT, CLEANUP) to the appropriate tool call
- `on_step_complete` callback for real-time progress reporting
- Optional validation before execution via `PlanValidator`

**Lines:** ~280

### 3. `main.py` — ToolExecutor Updates

**New methods added to `ToolExecutor`:**
- `execute_plan(plan)` — execute a plan via WorkflowEngine
- `generate_and_execute_plan(user_text)` — generate + validate + execute in one call
- `_handle_execute_plan()` — dispatch for `execute_plan` tool call
- `_handle_list_plan_steps()` — dispatch for `list_plan_steps` tool call
- `_needs_powershell_wrapper()` — static method to detect PowerShell syntax

**Bugs Fixed:**
- PowerShell commands with variables (`$x = ...`) and here-strings (`@'...'@`) now auto-detected and wrapped with `powershell -NoProfile -Command`
- File read limit increased: large files (>100KB) now show first half instead of failing
- Output buffer increased from 5KB to 10KB

**New ToolExecutor constructor parameter:**
- `ai_brain: Optional[AIBrain]` — enables plan system initialization

### 4. `core/__init__.py` — New Exports

Added exports for: `PlanGenerator`, `ExecutionPlan`, `ExecutionStep`, `StepType`, `ExecutionMode`, `PlanValidator`, `ValidationLevel`, `ValidationStatus`, `StepTracker`, `StepStatus`, `StepResult`, `WorkflowEngine`, `WorkflowResult`.

---

## New Tools (Added to ToolExecutor)

| Tool | Description |
|------|-------------|
| `execute_plan` | Generate and execute a multi-step plan from a user request |
| `list_plan_steps` | List the steps of the current pending plan |

---

## Bug Fixes

### PowerShell Command Wrapping
**Before:** Commands like `$files = (Get-ChildItem ...)` failed because `subprocess.run(shell=True)` uses `cmd.exe` on Windows.

**After:** `_needs_powershell_wrapper()` detects PowerShell syntax (variables, here-strings, cmdlets) and auto-wraps with `powershell -NoProfile -Command`.

### File Read Limit
**Before:** Files >100KB returned "File too large" error.

**After:** Large files are read in chunks — first half is shown with a truncation notice. Output buffer increased to 10KB.

---

## Files Changed

| File | Action | Lines Changed |
|------|--------|---------------|
| `core/step_tracker.py` | CREATED | +180 |
| `core/workflow_engine.py` | CREATED | +280 |
| `main.py` | MODIFIED | ~80 lines changed |
| `core/__init__.py` | MODIFIED | +15 lines |
| `pyproject.toml` | MODIFIED | version 0.1.0 → 0.6.0 |
| `README.md` | MODIFIED | version + 0.6.0 section |
| `ROADMAP.md` | MODIFIED | Phase 4 marked complete |
| `tests/test_phase4_multi_step_planning.py` | CREATED | +350 |

---

## Test Coverage

`tests/test_phase4_multi_step_planning.py` — 30+ tests covering:

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestStepTracker` | 13 | Step lifecycle, progress, summary, failures |
| `TestPlanGeneratorPhase4` | 4 | Plan generation, ordering, complexity |
| `TestPlanValidatorPhase4` | 2 | Validation of valid/empty plans |
| `TestWorkflowEngine` | 8 | Execution, failures, dependencies, step mapping |
| `TestToolExecutorPlanIntegration` | 4 | PowerShell detection |
| `TestPhase4Integration` | 2 | Full workflow + tracker integration |

---

## Architecture

```
User Request
     │
     ▼
AIBrain.agent_chat()  ──→  Returns tool_calls
     │
     ▼
ToolExecutor._dispatch()
     │
     ├── execute_command, click, type_text, ...  (atomic tools)
     │
     ├── execute_plan  ──→  generate_and_execute_plan()
     │                          │
     │                          ▼
     │                    PlanGenerator.generate_plan(intent)
     │                          │
     │                          ▼
     │                    PlanValidator.validate(plan)
     │                          │
     │                          ▼
     │                    WorkflowEngine.execute(plan)
     │                          │
     │                          ├── StepTracker (progress)
     │                          ├── Dependency resolution
     │                          ├── Retry with backoff
     │                          └── ToolExecutor._execute_single_step()
     │
     └── list_plan_steps  ──→  Show pending plan steps
```

---

## Version History

| Version | Phase | Description |
|---------|-------|-------------|
| 0.1.0 | 1 | Stabilize execution pipeline |
| 0.2.0 | 2 | Structured tool calling |
| 0.3.0 | 2 | Tool schema with 13 tools |
| 0.4.0 | 3 | Autonomous vision loop with 5 vision tools |
| 0.5.0 | 3+ | Multi-provider API detection (6 providers) |
| **0.6.0** | **4** | **Intelligent multi-step planning with workflow engine** |

---

*Report generated for Software-AI v0.6.0*
