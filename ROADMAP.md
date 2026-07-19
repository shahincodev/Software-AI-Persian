# ROADMAP.md — Software-AI Architectural Redesign & Module Cleanup

> **Last Updated**: 2026-07-19
> **Current Version**: 1.1.0
> **Target Version**: 2.0.0

---

## Vision Statement

Transform Software-AI from a traditional automation framework into an **autonomous desktop AI agent** — a reasoning-based system capable of interacting with Windows naturally, safely, and intelligently, comparable to OpenAI's Operator/Atlas or similar AI computer-use systems.

---

## Current Status

| Item | Value |
|------|-------|
| Phases 1-11 (Legacy) | Completed |
| Phase 12 — Architectural Redesign | Completed |
| Phase 13 — Module Cleanup | In Progress (13.1–13.4 Done) |
| Phase 14 — Integration & Migration | Pending |
| Phase 15 — Testing & Release | Pending |

---

## Phase 12 — Architectural Redesign (COMPLETED)

The following new modules have been built to replace the old architecture:

### New Modules Created

| Module | File | Purpose | Lines |
|--------|------|---------|-------|
| MouseEngine | `core/mouse_engine.py` | Vision-guided clicks with observe→locate→move→click→verify→retry | 530 |
| KeyboardEngine | `core/keyboard_engine.py` | Focus-aware typing with retry, instant/human modes, verification | 520 |
| SecurityEngine | `core/security_engine.py` | Risk-based execution with trust levels, session permissions | 580 |
| ReasoningPipeline | `core/reasoning_pipeline.py` | Agent intelligence: understand→think→plan→observe→execute→verify→recover | 450 |
| UIAProvider | `core/uia_provider.py` | Windows accessibility tree integration | 310 |
| ReliabilityManager | `core/reliability.py` | Checkpoints, rollback, diagnostics, health monitoring | 300 |

### Architecture Comparison

| Aspect | Old Architecture | New Architecture |
|--------|-----------------|-----------------|
| Mouse | pyautogui wrapper, no verification | Vision-guided, click verification, retry strategies |
| Keyboard | Blind typing, no focus check | Focus detection, retry on focus loss, mode selection |
| Security | Hardcoded whitelist, repeated confirmations | Risk-based, trust levels, session permissions |
| Intelligence | No reasoning pipeline | 8-stage mandatory pipeline |
| Desktop Understanding | OCR-only, coordinates primary | UIA accessibility tree + OCR |
| Reliability | No rollback, no diagnostics | Checkpoints, rollback, structured diagnostics |

---

## Phase 13 — Module Cleanup

### Overview

Analysis identified **17 modules** across 3 tiers that can be removed, totaling approximately **4,337 lines** of dead or redundant code.

---

### Tier 1 — Safe to Remove Immediately

These modules are dead code, deprecated wrappers, or completely unused. They have **zero runtime value** and can be deleted without affecting any functionality.

#### 13.1 — Remove Deprecated Wrapper Modules

| # | Module | Lines | Reason |
|---|--------|-------|--------|
| 1 | `core/master_controller.py` | 209 | Explicitly deprecated. Redirects to `intent_router.py`. Only imported in 3 test files. |
| 2 | `core/dialog_manager.py` | 50 | Explicitly deprecated. Redirects to `intent_analyzer.py`. Only imported in 2 test files. |
| 3 | `core/memory_system.py` | 27 | Explicitly deprecated. Redirects to `memory_integrator.py`. Only imported in 1 test file. |

**Tasks:**
- [x] Delete `core/master_controller.py`
- [x] Delete `core/dialog_manager.py`
- [x] Delete `core/memory_system.py`
- [x] Remove imports from `tests/test_master_controller.py`
- [x] Remove imports from `tests/test_master_controller_complete.py`
- [x] Remove imports from `tests/quick_test_master.py`
- [x] Remove imports from `tests/test_dialog_manager.py`
- [x] Remove imports from `tests/test_intent_system_integration.py`
- [x] Remove import from `tests/test_bug_fixes.py`

#### 13.2 — Remove Completely Unused Modules

| # | Module | Lines | Reason |
|---|--------|-------|--------|
| 4 | `core/agent_core.py` | 85 | **NOT IMPORTED ANYWHERE** in the entire codebase. Dead code. |
| 5 | `core/browser_core.py` | 38 | **NOT IMPORTED ANYWHERE** in the entire codebase. Dead code. |
| 6 | `core/model_orchestrator.py` | 89 | **NOT IMPORTED ANYWHERE** in the entire codebase. Dead code. |

**Tasks:**
- [x] Delete `core/agent_core.py`
- [x] Delete `core/browser_core.py`
- [x] Delete `core/model_orchestrator.py`

#### 13.3 — Remove Isolated Realtime Modules

| # | Module | Lines | Reason |
|---|--------|-------|--------|
| 7 | `core/realtime_loop.py` | 175 | Only imported by `realtime_interpreter.py` (also being removed). Not used in main.py. |
| 8 | `core/realtime_interpreter.py` | ~200 | Only imported by `realtime_loop.py` (also being removed). Not used in main.py. |

**Tasks:**
- [x] Delete `core/realtime_loop.py`
- [x] Delete `core/realtime_interpreter.py`
- [x] Remove imports from `tests/test_realtime_loop.py`
- [x] Remove imports from `tests/test_realtime_interpreter.py`

**Tier 1 Total: 8 modules, ~873 lines**

---

### Tier 2 — Safe to Remove (Test/Example-Only)

These modules are **not imported by main.py or any core runtime module**. They exist only in tests and examples. Removing them eliminates maintenance burden without affecting runtime.

#### 13.4 — Remove Test/Example-Only Modules

| # | Module | Lines | Import Locations |
|---|--------|-------|-----------------|
| 9 | `core/advanced_logging.py` | ~100 | `examples/logging_demo.py`, `tests/test_kill_persistence.py`, `tests/test_system.py` |
| 10 | `core/logging_decorators.py` | ~80 | Same 3 files as above |
| 11 | `core/intelligent_agent.py` | ~300 | Only in `tests/` (8 files) and `examples/` — NOT in main.py |
| 12 | `core/autonomous_agent.py` | 460 | Only in `tests/test_autonomous_agent.py` and `examples/` — NOT in main.py |
| 13 | `core/context_aware_actions.py` | 483 | Only in `tests/` (2 files) — NOT in main.py |
| 14 | `core/multi_monitor.py` | ~150 | Only in `tests/` (2 files) — NOT in main.py |

**Tasks:**
- [x] Delete `core/advanced_logging.py`
- [x] Delete `core/logging_decorators.py`
- [x] Delete `core/intelligent_agent.py`
- [x] Delete `core/autonomous_agent.py`
- [x] Delete `core/context_aware_actions.py`
- [x] Delete `core/multi_monitor.py`
- [x] Update or remove affected test files
- [x] Update or remove affected example files

**Tier 2 Total: 6 modules, ~1,573 lines**

---

### Tier 3 — Fully Replaced (Requires Migration First)

These modules are **functionally superseded** by the new architecture but are still imported by `main.py` or `action_controller.py`. They can only be removed **after migrating their consumers**.

#### 13.5 — Migrate action_controller.py

`action_controller.py` is the central nexus that imports `mouse_control`, `keyboard_control`, and `execution_manager`. It must be migrated first.

**Current Dependencies:**
```python
from core.mouse_control import MouseController, MouseButton
from core.keyboard_control import KeyboardController
from core.execution_manager import ExecutionManager
```

**Migration Tasks:**
- [ ] Add `MouseEngine` and `KeyboardEngine` as constructor parameters (dependency injection)
- [ ] Maintain backward compatibility via optional legacy parameter support
- [ ] Replace internal `self.mouse = MouseController()` with `MouseEngine`
- [ ] Replace internal `self.keyboard = KeyboardController()` with `KeyboardEngine`
- [ ] Update `click_on_text()`, `type_in_field()`, etc. to use new engines
- [ ] Run all existing tests to verify backward compatibility

#### 13.6 — Migrate main.py

**Current Dependencies:**
```python
from core.mouse_control import MouseController
from core.keyboard_control import KeyboardController
from core.safety_consent_manager import SafetyConsentManager
```

**Migration Tasks:**
- [ ] Replace `MouseController()` with `MouseEngine()`
- [ ] Replace `KeyboardController()` with `KeyboardEngine()`
- [ ] Replace `SafetyConsentManager` with `SecurityEngine` session permissions
- [ ] Update `VisionLoopManager` initialization to use new vision providers

#### 13.7 — Migrate execution_manager.py

**Current Dependencies:**
```python
from core.safety_filter import SafetyFilter, UserConsentManager
```

**Migration Tasks:**
- [ ] Replace `SafetyFilter.validate()` with `SecurityEngine.assess_action()`
- [ ] Replace `UserConsentManager.request_consent()` with `SecurityEngine` session permissions
- [ ] Maintain the priority queue and audit logging functionality
- [ ] Run execution pipeline tests

#### 13.8 — Remove Old Replaced Modules

After migration is complete and all tests pass:

| # | Module | Lines | New Replacement |
|---|--------|-------|----------------|
| 15 | `core/mouse_control.py` | 744 | `core/mouse_engine.py` |
| 16 | `core/keyboard_control.py` | 771 | `core/keyboard_engine.py` |
| 17 | `core/safety_filter.py` | 376 | `core/security_engine.py` |

**Tasks:**
- [ ] Delete `core/mouse_control.py`
- [ ] Delete `core/keyboard_control.py`
- [ ] Delete `core/safety_filter.py`
- [ ] Remove exports from `core/__init__.py`
- [ ] Update all remaining test imports

**Tier 3 Total: 3 modules, 1,891 lines (removable after migration)**

---

### Tier 4 — Modules to KEEP (Still Actively Used)

These modules remain essential to the runtime and must NOT be removed:

| Module | Purpose | Used By |
|--------|---------|---------|
| `core/ai_brain.py` | Multi-provider LLM management | main.py |
| `core/action_controller.py` | Action orchestration (will be migrated) | main.py, tests |
| `core/action_factory.py` | Action creation | action_controller.py |
| `core/action_types.py` | Data models | action_controller.py |
| `core/desktop_vision.py` | OCR, screenshots, template matching | vision_loop.py, smart_wait.py |
| `core/desktop_actions.py` | Action definitions (Click, Type, etc.) | action_controller.py |
| `core/smart_wait.py` | Wait strategies (element, change, process) | action_controller.py |
| `core/vision_loop.py` | Observe-act-verify loop | main.py |
| `core/execution_manager.py` | Action queue with priority (will be migrated) | main.py, action_controller.py |
| `core/action_recovery.py` | Async retry with error classification | vision_loop.py |
| `core/system_actions.py` | System action types (Launch, Install, etc.) | execution_manager.py |
| `core/system_tools.py` | System tool adapter | execution_manager.py |
| `core/system_capabilities.py` | Capability registry | action_controller.py |
| `core/intent_router.py` | Request routing | main.py |
| `core/intent_analyzer.py` | Intent parsing (7-step pipeline) | intent_router.py |
| `core/intent_models.py` | Intent data classes | intent_analyzer.py |
| `core/session_manager.py` | SQLite conversation sessions | main.py |
| `core/memory_integrator.py` | Persistent memory with SQLite | main.py |
| `core/plan_generator.py` | Multi-step plan creation | main.py |
| `core/plan_validator.py` | Plan validation | main.py |
| `core/step_tracker.py` | Step execution tracking | main.py, workflow_engine.py |
| `core/workflow_engine.py` | Multi-step plan execution | main.py |
| `core/voice_io.py` | Voice I/O with 3 TTS providers | main.py |
| `core/windows_environment.py` | Windows path/app detection | main.py |
| `core/logging_config.py` | Logging setup | main.py |
| `core/model_config.py` | Model registry & health tracking | main.py |
| `core/monitoring_service.py` | CPU/RAM/Disk monitoring | main.py |
| `core/tool_schema.py` | 20+ tool definitions | main.py |
| `core/safety_consent_manager.py` | User consent (will be replaced) | main.py |
| `core/capability_manager.py` | System capability detection | main.py |

---

## Phase 14 — Integration & Migration

### 14.1 — Update core/__init__.py

- [ ] Remove all Tier 1 module exports
- [ ] Remove all Tier 2 module exports
- [ ] Remove Tier 3 module exports after migration
- [ ] Add new architecture module exports (already done)
- [ ] Verify all imports resolve correctly

### 14.2 — Update main.py

- [ ] Replace old controller instantiation with new engines
- [ ] Update agent loop to use ReasoningPipeline
- [ ] Integrate SecurityEngine for action approval
- [ ] Update VisionLoopManager to use new vision providers
- [ ] Test full agent loop end-to-end

### 14.3 — Update Test Suite

- [ ] Remove tests for deleted modules
- [ ] Create tests for new architecture modules (already have `test_new_architecture.py`)
- [ ] Update integration tests
- [ ] Verify all tests pass

---

## Phase 15 — Testing & Release

### 15.1 — Comprehensive Testing

- [ ] Run all unit tests
- [ ] Run all integration tests
- [ ] Test mouse engine with real desktop interaction
- [ ] Test keyboard engine with real typing
- [ ] Test security engine risk assessments
- [ ] Test reasoning pipeline end-to-end
- [ ] Test reliability checkpoints and rollback

### 15.2 — Documentation

- [ ] Update README.md with new architecture
- [ ] Update CHANGELOG.md with v2.0.0 changes
- [ ] Update CONVENTIONS.md with new patterns
- [ ] Create architecture diagram in docs/

### 15.3 — Release

- [ ] Bump version to 2.0.0
- [ ] Run final test suite
- [ ] Create Git tag v2.0.0
- [ ] Write release notes

---

## Expected Outcome

### Code Reduction

| Category | Modules Removed | Lines Saved |
|----------|----------------|-------------|
| Tier 1 — Dead/Deprecated | 8 | ~873 |
| Tier 2 — Test/Example Only | 6 | ~1,573 |
| Tier 3 — Replaced | 3 | ~1,891 |
| **Total** | **17** | **~4,337** |

### Architecture Quality

| Metric | Before | After |
|--------|--------|-------|
| Total modules | 50 | 33 |
| Dead code modules | 8 | 0 |
| Deprecated wrappers | 3 | 0 |
| Redundant modules | 6 | 0 |
| Core runtime modules | 33 | 33 (cleaner) |

### Reliability Improvements

| Capability | Before | After |
|------------|--------|-------|
| Click verification | None | Vision-guided verification with retry |
| Focus detection | None | Automatic focus check before typing |
| Risk assessment | Hardcoded whitelist | Dynamic risk-based with trust levels |
| Session permissions | None | Temporary elevated access |
| Reasoning pipeline | None | Mandatory 8-stage pipeline |
| Rollback support | None | Checkpoint-based rollback |
| Diagnostics | Basic logging | Structured diagnostic entries |
| UIA integration | None | Windows accessibility tree |

---

## Execution Order

```
Phase 13.1  →  Remove deprecated wrappers (master_controller, dialog_manager, memory_system)
Phase 13.2  →  Remove dead code (agent_core, browser_core, model_orchestrator)
Phase 13.3  →  Remove isolated modules (realtime_loop, realtime_interpreter)
Phase 13.4  →  Remove test-only modules (advanced_logging, logging_decorators, etc.)
Phase 13.5  →  Migrate action_controller.py to new engines
Phase 13.6  →  Migrate main.py to new engines
Phase 13.7  →  Migrate execution_manager.py to SecurityEngine
Phase 13.8  →  Remove old replaced modules (mouse_control, keyboard_control, safety_filter)
Phase 14    →  Integration and migration
Phase 15    →  Testing and release
```

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing tests | Medium | Remove tests for deleted modules, update imports |
| Breaking main.py runtime | High | Migrate main.py in Phase 13.6 before removing old modules |
| Losing backward compatibility | Medium | Keep old modules until migration is verified |
| UIA initialization failure | Low | Graceful degradation — falls back to OCR |
| Missing imports in tests | Low | Search and update all test imports |

---

## Development Rules

1. **Before each phase**: Read this ROADMAP.md to understand context
2. **After each phase**: Update status checkboxes in this file
3. **After each phase**: Run test suite to verify no regressions
4. **After each phase**: Commit with descriptive message
5. **Never remove a module** without first verifying no active runtime imports it
6. **Always test backward compatibility** before removing old modules
