# Software-AI: Project Migration & AI Context Document

**Version**: 2.0  
**Last Updated**: 2026-06-27  
**Maintainer**: Shahin (shahincodev)  
**License**: Proprietary (All Rights Reserved)  
**Companion Document**: [`AI_PROJECT_RULES.md`](AI_PROJECT_RULES.md) — permanent engineering rules

---

## AI Onboarding

### How a New AI Assistant Should Approach This Project

This section is for any AI model encountering Software-AI for the first time. Follow these steps before making any suggestions or changes.

#### Step 1: Read This Document First

Read `PROJECT_MIGRATION_CONTEXT.md` from beginning to end before forming any opinions about the architecture. The project has undergone significant refactoring, and surface-level assumptions will be wrong.

#### Step 2: Understand the Project Vision

Section 1 (Project Vision) explains what Software-AI is and what it is intended to become. Every architectural decision in this project traces back to these principles. If a proposed change contradicts the vision, it will be rejected.

#### Step 3: Review the Architectural Decision Records (ADR)

Section 6 (Major Architectural Decisions) contains the reasoning behind every significant change. Do not propose reversing an ADR without understanding why it was made in the first place. If you believe an ADR should be revisited, provide specific technical evidence.

#### Step 4: Understand the Current Architecture

Section 2 (Current Architecture) describes the exact state of the system. Do not assume the architecture matches the original design. Many modules have been merged, renamed, or converted to wrappers.

#### Step 5: Read the Companion Rules File

`AI_PROJECT_RULES.md` contains permanent engineering principles that must never be violated. Treat these as binding constraints.

#### Step 6: Check the Technical Debt

Section 7 (Current Technical Debt) lists known problems. Do not propose changes that duplicate existing technical debt or introduce new instances of known anti-patterns.

#### Step 7: Understand the Build History

Section 4 (Build Session History) shows what has already been done. Do not propose work that has already been completed or rejected.

#### Core Principles for AI Collaboration

- **Preserve architectural consistency.** Every change should make the architecture more coherent, not less.
- **Challenge existing decisions only when there are strong technical reasons.** Preference for the status quo unless you can demonstrate a clear problem.
- **Avoid architectural fragmentation.** Do not introduce new patterns that compete with existing ones. If a pattern exists, use it.
- **Prefer improving the existing architecture over replacing it.** The project has chosen consolidation over creation. Respect this choice.
- **Never increase complexity without measurable benefit.** Every abstraction, module, or pattern must justify its existence.
- **Document why, not just what.** Every change should include the reasoning. Future AI models will need to understand the intent.

---

## 1. Project Vision

### What Software-AI Is

Software-AI is an **autonomous Windows automation system** that accepts natural language commands (in Persian and English) and executes them through vision-based decision-making, intent analysis, and multi-stage planning. It is designed to be a general-purpose AI assistant for the Windows desktop.

### What It Is Intended to Become

The long-term vision is a **single-entry, capability-driven AI copilot for Windows** that:

- Accepts natural language input (text or voice) without mode flags or explicit command prefixes
- **Auto-detects** the user's intent and lazily activates only the required capabilities
- Handles any request through the correct pipeline — chat, web browsing, desktop automation, file operations, system management, or complex multi-step goals
- Learns from past executions to improve future performance
- Operates safely through risk assessment and user consent gates

### Design Philosophy

1. **Capability-Driven Architecture**: The system, not the user, decides which internal components to activate based on intent analysis. No mode flags (`--enable-automation`, `--task-mode`, etc.). One entry point, smart routing.

2. **Lazy Initialization**: Expensive components (DesktopVision, BrowserCore, LLM models) are created only when first requested, not at startup. This keeps the base footprint small.

3. **Consolidation over Creation**: When architectural problems emerge, the solution is to merge and refactor existing modules, not add new ones. File count should stay approximately constant or decrease.

4. **Backward Compatibility During Refactors**: Every migration stage leaves the project in a working state. Old modules are preserved as re-export wrappers with `DeprecationWarning` until all consumers have been updated.

5. **Safety First**: All actions go through risk assessment (0-100 scale). High-risk actions (score ≥ 70) require explicit user consent. The system never deletes system files, modifies BIOS, or accesses protected areas.

---

## 2. Current Architecture (as of 2026-06-27)

### Layered Stack

```
LAYER 5 [UI]             main.py — single conversational entry point
LAYER 4 [ORCHESTRATION]  IntentRouter → CapabilityManager
LAYER 3 [PLANNING]       IntentAnalyzer (with DialogManager merged) → PlanGenerator → PlanValidator → MemoryIntegrator
LAYER 2 [EXECUTION]      ActionController (with IntelligentSystemAgent merged) → ExecutionManager
LAYER 1 [CAPABILITIES]   DesktopVision, MouseControl, KeyboardControl, SmartWait, BrowserCore, VoiceIO, SystemTools
```

### Execution Flow

```
User Input (text/voice)
    ↓
main.py → IntentRouter.route()
    ├─ IntentAnalyzer.analyze() — extracts Intent{verb, target, params, confidence}
    │
    ├─ CapabilityManager.activate() — lazily creates required resources
    │   └─ Dependency resolution: activates prerequisites first
    │
    ├─ SafetyConsentManager — risk assessment + user consent
    │
    └─ RouteType dispatch:
         ├─ CHAT_RESPONSE → AIBrain.ask() → plain text response
         ├─ BROWSER_USE  → BrowserCore (Playwright)
         ├─ DESKTOP_AUTOMATION → ActionController (vision + mouse + keyboard)
         ├─ AUTONOMOUS_AGENT → AutonomousAgent (goal-driven)
         ├─ TASK_MODE → TaskEngine (queued batch)
         ├─ CLARIFICATION_NEEDED → dialog with user
         └─ (fallback) → system_agent.process_request()
    ↓
MemoryIntegrator.record_execution() — learn from outcome
```

### Important Modules and Responsibilities

| Module | Responsibility |
|--------|---------------|
| `main.py` | Single entry point. Argument parsing, capability registration, `process_capability_loop()`. |
| `capability_manager.py` | Factory registration, lazy activation (`activate()`), resource lifecycle (`get()`, `is_active()`, `deactivate()`), dependency resolution. |
| `intent_router.py` | Determines RouteType from user text. Uses IntentAnalyzer internally. Returns Route with risk level, required capabilities, consent flag. |
| `intent_analyzer.py` | Contains `IntentAnalyzer` (intent extraction from NL) + `SystemActionParser` (regex-based action extraction) + merged `DialogManager` (clarifying questions). |
| `plan_generator.py` | Creates multi-step `ExecutionPlan` from `Intent`. Hard limit of 50 steps. |
| `plan_validator.py` | Scores plans on safety, reliability, efficiency. Three levels: BASIC, STRICT, PARANOID. |
| `memory_integrator.py` | SQLite persistence for `execution_history`, `learned_patterns`, `optimizations`. Also contains merged `ShortTermMemory`, `LongTermMemory`, `MemoryManager`. |
| `master_controller.py` | Backward-compatible re-export wrapper (deprecated). |
| `dialog_manager.py` | Backward-compatible re-export wrapper (deprecated, merged into intent_analyzer). |
| `memory_system.py` | Backward-compatible re-export wrapper (deprecated, merged into memory_integrator). |
| `action_controller.py` | Executes desktop and system actions. Contains `create_action()` factory, `process_request()` orchestrator, `click_on_text()`, `fill_form()`, etc. |
| `execution_manager.py` | System action executor (LaunchApp, InstallPackage, etc.) with safety filter, consent, adapter pattern. |
| `autonomous_agent.py` | Goal-driven executor with vision feedback loop. |
| `intelligent_agent.py` | Backward-compatible re-export wrapper (deprecated, parser → intent_analyzer, executor → action_controller). |
| `ai_brain.py` | LLM communication layer. Priority: Groq → Gemini → OpenRouter → Ollama. |
| `desktop_vision.py` | Screenshot capture, OCR (Tesseract), element detection (OpenCV). |
| `mouse_control.py` / `keyboard_control.py` | Direct input automation via Windows API. |
| `system_tools.py` | OS-level operations (app launch, process management). |
| `browser_core.py` | Playwright-based web automation. |
| `voice_io.py` | Speech-to-text (SpeechRecognition), text-to-speech (gTTS/ElevenLabs). |

### Capability System

- `CapabilityManager` is the central registry.
- Capabilities are registered with a **factory function** (or None for flag-only capabilities).
- `activate(name)` creates the resource lazily, resolves dependencies recursively, caches the resource.
- `get(name)` returns the resource if active, None otherwise.
- `deactivate(name)` calls cleanup/shutdown on the resource and removes it.
- Backward-compatible `enable()`/`disable()` methods are preserved.

### Routing

- `IntentRouter` analyzes user input via `IntentAnalyzer`, classifies it into a `RouteType`, determines which capabilities to activate, assesses risk level, and (if in SAFE mode) flags high-risk routes for user consent.
- RouteType values: `CHAT_RESPONSE`, `BROWSER_USE`, `DESKTOP_AUTOMATION`, `AUTONOMOUS_AGENT`, `TASK_MODE`, `REQUIRES_CONSENT`, `CLARIFICATION_NEEDED`.

### Memory

Two schemas share `data/memories.sqlite3`:
1. `MemorySystem` (`memory_system.py` wrapper) — content memory, single `memories` table.
2. `MemoryIntegrator` (`memory_integrator.py`) — `execution_history`, `learned_patterns`, `optimizations` tables.

This is a known architectural inconsistency that should be unified.

### Safety

- Risk scores 0-100.
- Score ≥ 70: HIGH RISK → requires explicit user consent.
- Score 40-69: MEDIUM → warning shown.
- Score < 40: LOW → auto-approved.
- Blocked operations: delete system files, modify BIOS, access protected areas.

---

## 3. Architectural History

### Phase 0: Monolithic Mode-Based Architecture (Original)

**Design**: Single `main.py` with CLI mode flags (`--enable-automation`, `--intent-planning`, `--task-mode`, `--full`). Users selected a mode at startup and the system activated corresponding components. Different modes had different entry points and command sets.

**Problems**:
- Users had to know which mode they needed before starting
- 17+ optional parameters passed through `process_user_input()`
- Components were created eagerly at startup regardless of need
- Mode-specific code paths diverged, duplicating logic
- New capabilities required new flags and new conditional branches

### Phase 1: Capability-Driven Architecture (Current)

**Design**: The system understands user intent first, then activates only the required capabilities. Single entry point (`python main.py`), no mode flags.

**Key Decisions**:
- `CapabilityManager` with factory registration and lazy activation replaced eager component creation
- `IntentRouter` with `RouteType` enum replaced mode-based dispatch
- `process_user_input()` with 17 parameters replaced by `process_capability_loop()` with 8 parameters using CapabilityManager

**Advantages**:
- Simpler UX: users just type what they want
- Lower memory footprint: components created only when needed
- Cleaner dispatch: RouteType enum instead of boolean flags
- Extensible: new capabilities register a factory, no new flags needed

**Trade-offs**:
- More complex routing logic (intent must be analyzed before execution)
- Dependency on AI model for routing (falls back to keyword matching if model unavailable)
- Backward-compat wrappers add indirection during migration

### Phase 2: Consolidation Refactor (Ongoing)

**Design**: Merge related modules instead of adding new ones. Address architectural inconsistencies by consolidating.

**Completed Merges**:
- `dialog_manager.py` → `intent_analyzer.py` (PlanGenerator and PlanValidator use the merged IntentAnalyzer)
- `master_controller.py` → `intent_router.py` + `system_tools.py` (routing logic moved, MC is a re-export wrapper)
- `memory_system.py` → `memory_integrator.py` (two memory schemas now in one file, still separated logically)
- `intelligent_agent.py` → `intent_analyzer.py` (parser) + `action_controller.py` (executor)

**Advantages**:
- Fewer files to navigate
- Reduced import complexity
- Related logic lives together
- Backward compatibility maintained through wrappers

**Trade-offs**:
- Some files became large (action_controller.py ~1400 lines)
- Cross-module dependencies increased (action_controller now imports intent_analyzer)
- Wrappers add a small runtime cost (import redirection + deprecation warning)

---

## 4. Build Session History

### Session 1: Phase 1 — Enhanced CapabilityManager (Date: ~2026-06-23)

**Objective**: Transition from eager mode-based architecture to lazy capability-driven architecture.

**Completed Work**:
- Added factory registration to `CapabilityManager`
- Added `activate()` for lazy resource creation
- Added `get()`, `is_active()`, `deactivate()` for resource lifecycle
- Added dependency resolution (recursive activation of prerequisites)
- Added new `CapabilityType` values (DESKTOP_MOUSE, DESKTOP_KEYBOARD, SCREEN_OBSERVATION, SYSTEM_OPERATIONS, VOICE_IO, INTENT_ANALYSIS, PLANNING, PLAN_VALIDATION, EXECUTION_HISTORY, CHAT, WEB_BROWSING)
- Preserved backward-compatible `enable()`/`disable()` API

**Modified Files**: `core/capability_manager.py`

**Validation**: Syntax verified.

### Session 2: Phase 2 — Merge DialogManager into IntentAnalyzer (Date: ~2026-06-23)

**Objective**: Consolidate dialog management into the intent analysis module.

**Completed Work**:
- Added `DialogState`, `QuestionType`, `DialogQuestion`, `DialogResponse`, `DialogSession` dataclasses/enums to `intent_analyzer.py`
- Added `collect_missing_info()`, `_generate_question()`, `_ask_user()`, `_get_user_input()`, `_confirm_understanding()`, `_calculate_response_confidence()`, `_merge_responses_with_intent()`, `clarify_field()`, `get_suggestions()` methods to `IntentAnalyzer`
- Made `dialog_manager.py` a backward-compatible re-export wrapper with `DeprecationWarning`

**Modified Files**: `core/intent_analyzer.py`, `core/dialog_manager.py`

**Validation**: Syntax verified, existing tests unchanged.

### Session 3: Phase 3 — Merge MasterController Routing (Date: ~2026-06-23)

**Objective**: Consolidate routing logic from MasterController into IntentRouter/SystemTools.

**Completed Work**:
- Added `get_system_info()` to `system_tools.py`
- Made `master_controller.py` a backward-compatible re-export wrapper preserving `MasterAIController`, `ToolType`, `RoutingDecision`, `ExecutionResult` classes

**Modified Files**: `core/system_tools.py`, `core/master_controller.py`

**Validation**: Syntax verified.

### Session 4: Phase 4 — Merge MemorySystem into MemoryIntegrator (Date: ~2026-06-23)

**Objective**: Consolidate two parallel memory systems.

**Completed Work**:
- Added `MemoryItem`, `ShortTermMemory`, `LongTermMemory`, `MemoryManager` classes from `memory_system.py` into `memory_integrator.py`
- Made `memory_system.py` a backward-compatible re-export wrapper with `DeprecationWarning`

**Modified Files**: `core/memory_integrator.py`, `core/memory_system.py`

**Validation**: Syntax verified.

### Session 5: Phase 5 — Refactor main.py (Date: 2026-06-27)

**Objective**: Replace the legacy mode-based entry point with a capability-driven conversation loop.

**Completed Work**:
- Updated imports to use consolidated modules (CapabilityManager, IntentRouter, IntentAnalyzer, MemoryIntegrator)
- Updated argument parser: suppressed mode flags from help (`argparse.SUPPRESS`), kept as no-op for backward compat
- Replaced 553-line `process_user_input()` (17 params, all individual component injections) with 350-line `process_capability_loop()` (8 params, uses `CapabilityManager.activate()` for lazy capability loading)
- Cleaner routing loop handling all `RouteType` values including `CLARIFICATION_NEEDED`
- Backward-compat explicit commands preserved (`plan`, `smart`, `goal`, `mouse`, `type`, `wait`, `vision`) — now lazily activate capabilities instead of relying on injected instances
- File reduced from 1286 to 1081 lines (16% reduction)

**Modified Files**: `main.py`

**Validation**: Syntax verified (`py_compile`). File reduction of ~200 lines.

### Session 6: Phase 6 — Merge intelligent_agent.py (Date: 2026-06-27)

**Objective**: Decompose 876-line IntelligentSystemAgent into intent_analyzer (parser) and action_controller (executor).

**Completed Work**:
- Moved `SystemActionParser` class (596 lines) to `core/intent_analyzer.py` — all regex-based action parsing logic
- Moved `_create_action()` factory method (114 lines) to `core/action_controller.py` as `ActionController.create_action()` — handles both desktop actions (Click, Type, Wait, DragDrop, Hotkey, Scroll) and system actions (LaunchApp, InstallPackage, QueryHardware, TerminateProcess, ExecuteCommand)
- Moved `process_request()` orchestrator (85 lines) to `core/action_controller.py` as `ActionController.process_request()` — parses user request, creates action objects, executes via ExecutionManager (system) or ActionController (desktop)
- Added `dry_run` parameter to `ActionController.__init__()` (default `False`)
- Added required imports to both target files (SystemCapabilityRegistry, ExecutionManager, system action classes)
- Made `core/intelligent_agent.py` a backward-compatible re-export wrapper (66 lines) with `DeprecationWarning`
- `SystemActionParser` is re-exported from `intelligent_agent` so existing imports still work

**Modified Files**: `core/intent_analyzer.py`, `core/action_controller.py`, `core/intelligent_agent.py`

**Validation**: Syntax verified on all 3 files. Smoke test: `IntelligentSystemAgent` instantiation, `ActionController.create_action()` for both desktop and system actions, `SystemActionParser` origin verified as `core.intent_analyzer`.

### Future Sessions

- **Session 7**: Remove dead stubs (`dialog_manager.py`, `memory_system.py` after import audit)
- **Session 8**: Update test files to use consolidated modules
- **Session 9**: Run full test suite
- **Session 10**: End-to-end validation with `python main.py`

---

## 5. Module Responsibility Map

### `main.py`

- **Why it exists**: Single entry point for the entire application.
- **What it owns**: Argument parsing, capability registration, the main interaction loop.
- **What it should never do**: Contain business logic for intent analysis, action execution, or module initialization. It should only wire components together.
- **Dependencies**: All core modules (for registration), CapabilityManager (for orchestration).
- **Future extension**: Should become thinner over time. The `process_capability_loop()` is already minimal but could be further simplified with a pluggable command handler system.

### `capability_manager.py`

- **Why it exists**: Central registry for all system capabilities. Enables lazy initialization and dependency resolution.
- **What it owns**: Factory registration, resource lifecycle (`activate`/`deactivate`/`get`), dependency graph, activation callbacks.
- **What it should never do**: Contain any business logic for specific capabilities. Should not know what a "MouseController" or "DesktopVision" does.
- **Dependencies**: None beyond standard library.
- **Future extension**: Add capability pooling, resource limits, health checks, automatic deactivation of unused resources.

### `intent_router.py`

- **Why it exists**: Determines the execution path for a user request. The bridge between user intent and system capabilities.
- **What it owns**: Route classification, risk assessment, capability requirement mapping.
- **What it should never do**: Execute actions. Its job ends when it returns a `Route`.
- **Dependencies**: `IntentAnalyzer` (for intent extraction), `SafetyConsentManager` (for risk levels).
- **Future extension**: Add confidence-weighted routing that consults multiple analysis strategies.

### `intent_analyzer.py`

- **Why it exists**: Understands what the user wants. Contains both high-level intent extraction (`IntentAnalyzer`) and low-level action parsing (`SystemActionParser`).
- **What it owns**: `Intent` data class, `IntentAnalyzer` class (verb/target/params extraction + dialog management), `SystemActionParser` class (regex-based desktop action parsing).
- **What it should never do**: Execute any action, access any hardware/OS resource, maintain session state beyond a single request.
- **Dependencies**: `AIBrain` (for LLM-based analysis), `SystemCapabilityRegistry` (for parser context).
- **Future extension**: Add more sophisticated intent classification (few-shot, RAG-enhanced, multi-intent decomposition).

### `action_controller.py`

- **Why it exists**: Executes actions on the system. The unified executor for both desktop and system actions.
- **What it owns**: `ActionController` class with high-level actions (`click_on_text`, `fill_form`, `select_menu_item`), action factory (`create_action`), request orchestrator (`process_request`).
- **What it should never do**: Parse user input (that's the intent_analyzer's job). Should receive parsed action objects or dicts.
- **Dependencies**: `MouseController`, `KeyboardController`, `DesktopVision`, `SmartWaiter`, `ExecutionManager`, `SystemActionParser`, system/desktop action classes.
- **Future extension**: Add undo/redo, action recording and replay, parallel action execution.

### `plan_generator.py`

- **Why it exists**: Creates structured, multi-step execution plans from intents.
- **What it owns**: `ExecutionPlan`, `ExecutionStep`, plan generation logic (LLM + template-based).
- **What it should never do**: Validate plans, execute actions, manage memory.
- **Dependencies**: `Intent` (from intent_analyzer), `AIBrain`.
- **Future extension**: Add plan templates for common workflows, plan caching.

### `plan_validator.py`

- **Why it exists**: Ensures plans are safe, reliable, and efficient before execution.
- **What it owns**: `ValidationLevel` (BASIC/STRICT/PARANOID), validation scoring (safety_score, reliability_score, efficiency_score).
- **What it should never do**: Generate plans, execute actions.
- **Dependencies**: `ExecutionPlan`, `Intent`.
- **Future extension**: Add plan simulation, cost estimation, time estimation.

### `memory_integrator.py`

- **Why it exists**: Persists execution history and learns patterns for future improvement.
- **What it owns**: `MemoryIntegrator` (execution_history, learned_patterns, optimizations), `MemoryManager` + `ShortTermMemory` + `LongTermMemory` (content memory).
- **What it should never do**: Execute actions, generate plans, analyze intents.
- **Dependencies**: `SQLite3` (persistence), `ExecutionPlan`, `Intent`, `ValidationReport`.
- **Future extension**: Unify the two schema systems, add vector-based similarity search for pattern matching.

### `ai_brain.py`

- **Why it exists**: Central LLM communication layer with multi-provider failover.
- **What it owns**: Model selection (Groq → Gemini → OpenRouter → Ollama), prompt management, response parsing.
- **What it should never do**: Contain business logic specific to any single feature.
- **Dependencies**: Provider SDKs (google-generativeai, groq, openai).
- **Future extension**: Add streaming, tool-use/function-calling, token budgeting.

---

## 6. Major Architectural Decisions (ADR)

### ADR-001: Abandon Mode-Based Architecture

- **Decision**: Replace CLI mode flags with capability-driven auto-detection.
- **Context**: Original architecture required users to specify `--enable-automation`, `--intent-planning`, `--task-mode`, etc. at startup. Components were created eagerly based on these flags.
- **Alternatives considered**:
  1. Keep modes but add auto-detection on top (complex, dual dispatch)
  2. Fully mode-less with ML routing (chosen)
  3. Plugin-based architecture (over-engineered for current scale)
- **Why chosen**: Better UX (type what you want), lower memory (lazy init), cleaner code (no boolean explosion).
- **Consequences**: New routing dependency on AI model; keyword fallback needed when model unavailable.

### ADR-002: Adopt Lazy Initialization via Factory Registration

- **Decision**: Capabilities register factory functions; resources are created only on first `activate()` call.
- **Context**: Components like DesktopVision (Tesseract + OpenCV) and BrowserCore (Playwright) are expensive to initialize. Creating all at startup was wasteful.
- **Alternatives considered**:
  1. Eager init (original — wasteful, slow startup)
  2. Lazy import at point of use (worked but no resource tracking)
  3. Factory registration pattern (chosen)
- **Why chosen**: Clean resource lifecycle, explicit dependencies, easy testing (mock factories), compatible with async/sync.
- **Consequences**: Slight complexity increase in CapabilityManager; resources are not pre-warmed.

### ADR-003: Consolidate, Don't Create

- **Decision**: When architectural problems emerge, merge modules rather than adding new ones.
- **Context**: The ARCHITECTURE_REDESIGN.md proposed adding 14+ new files in subdirectories. This was rejected in favor of consolidation.
- **Alternatives considered**:
  1. Add 14+ new files (proposed — created organizational complexity)
  2. Keep everything as-is (no improvement)
  3. Merge related modules into existing files (chosen)
- **Why chosen**: Reduces file count, keeps related logic together, avoids "God Object" risk by distributing across reasonable files, simpler navigation.
- **Consequences**: Some files grew (action_controller.py ~1400 lines). May need further splitting along clear boundaries.

### ADR-004: Backward-Compatible Wrappers During Migration

- **Decision**: Old modules become re-export wrappers with `DeprecationWarning` instead of being deleted immediately.
- **Context**: Tests, imports, and third-party consumers reference existing module paths. Breaking them would stall development.
- **Alternatives considered**:
  1. Delete immediately (breaking changes everywhere)
  2. Keep both implementations in parallel (maintenance burden)
  3. Re-export wrappers (chosen)
- **Why chosen**: Zero breakage for consumers, explicit deprecation signal, clear migration path.
- **Consequences**: Transient complexity — wrappers must be removed after all consumers are updated.

### ADR-005: Merge System and Desktop Execution into ActionController

- **Decision**: `ActionController` now handles both desktop actions (click, type) and system actions (launch app, install package) through `process_request()`.
- **Context**: Previously `IntelligentSystemAgent` was the orchestrator, routing desktop actions to `ActionController` and system actions to `ExecutionManager`. This split required developers to understand two dispatch paths.
- **Alternatives considered**:
  1. Keep dual dispatch (status quo — confusing)
  2. Create a new unified executor class (adds a file)
  3. Merge into ActionController (chosen)
- **Why chosen**: Single execution entry point, simpler mental model, reduces file count.
- **Consequences**: `ActionController` now imports `ExecutionManager` and `SystemActionParser`, adding cross-module dependencies.

### ADR-006: Single `memories.sqlite3` with Two Schema Systems

- **Decision**: Keep one SQLite file but accept that two unrelated schema systems coexist within it.
- **Context**: `memory_system.py` manages a `memories` table for content storage. `memory_integrator.py` manages `execution_history`, `learned_patterns`, and `optimizations` tables. Both target the same file.
- **Alternatives considered**:
  1. Separate files (simpler isolation but more files)
  2. Unified schema (best but requires significant refactor)
  3. Accept current state (chosen for now)
- **Why chosen**: Pragmatic — both systems work independently and don't conflict. Unification can happen later without breaking changes.
- **Consequences**: Technical debt. Uneven abstraction. Must be unified in a future phase.

---

## 7. Current Technical Debt

### Temporary Compatibility Wrappers
- `core/dialog_manager.py` — re-exports from `intent_analyzer`, shows DeprecationWarning
- `core/memory_system.py` — re-exports from `memory_integrator`, shows DeprecationWarning
- `core/master_controller.py` — re-exports from `intent_router` + `system_tools`, shows DeprecationWarning
- `core/intelligent_agent.py` — re-exports from `intent_analyzer` + `action_controller`, shows DeprecationWarning

### Deprecated Modules (to be removed)
- `core/master_controller.py` — all functionality migrated
- `core/dialog_manager.py` — all functionality merged into `intent_analyzer.py`
- `core/memory_system.py` — all functionality merged into `memory_integrator.py`
- `core/intelligent_agent.py` — all functionality migrated (parser → intent_analyzer, executor → action_controller)

### Unfinished Refactors
- `intelligent_agent.py` (876 lines originally) still has 3 internal methods (`_simple_fallback_parse`, `_parse_click_action`, etc.) — wait, these were part of `SystemActionParser` which was moved. Let me verify: yes, the full `SystemActionParser` class was moved. The `IntelligentSystemAgent` wrapper does NOT contain these methods — they were part of the parser class that moved. The wrapper is clean.

Actually, the intelligent_agent wrapper contains only:
- `__init__` (creates registry, parser, executor, action_controller)
- `process_request` (delegates)
- `get_system_summary` (delegates)
This is correct and minimal.

### Known Limitations
- Two SQLite schemas in one file without unified access layer (see ADR-006)
- `action_controller.py` at ~1400 lines is large; may need method extraction
- `intent_analyzer.py` at ~1500 lines is also large after SystemActionParser merge
- Some tests require `pytest-asyncio` which was not installed in the base environment
- `quick_test.bat` has a potential issue with `%datetime%` variable shadowing (uses `for` loop variable without `setlocal enabledelayedexpansion`)
- No CI/CD pipeline configured
- `.env` file with API keys required but setup not automated

### Duplicated Logic
- `extract_tasks_from_text` exists in both `intent_router.py` and `main.py` — should be consolidated
- System capability scanning logic exists in both `system_capabilities.py` and `intelligent_agent.py` wrapper's `__init__`

### Testing Gaps
- No unit tests for `CapabilityManager.activate()` with dependency chains
- No unit tests for `ActionController.create_action()` error cases
- No integration tests for `main.py` `process_capability_loop()`
- Test coverage metrics unknown

---

## 8. Future Roadmap

### Phase 7 — Remove Dead Stubs
- Audit all imports across the codebase
- Remove `dialog_manager.py`, `memory_system.py`, `master_controller.py` wrappers once all references are updated
- Update `__init__.py` or module `__all__` exports
- **Dependency**: None — standalone cleanup

### Phase 8 — Update Test Files
- Update test imports to use consolidated module paths
- Add tests for new `ActionController` methods (`create_action`, `process_request`)
- Add tests for `CapabilityManager` dependency resolution
- **Dependency**: Phase 7 (to avoid broken import chains)

### Phase 9 — Unify Memory Schema
- Create a single unified memory access layer
- Merge `memories`, `execution_history`, `learned_patterns`, `optimizations` into a coherent schema
- Remove the `memory_system.py` wrapper permanently
- **Dependency**: Phase 7 (memory_system.py removal)

### Phase 10 — Consolidate Execution into Strategy Pattern
- Define a common `ExecutionStrategy` interface
- Implement strategies: `DesktopStrategy`, `SystemStrategy`, `BrowserStrategy`, `AutonomousStrategy`
- `ActionController` becomes a strategy selector
- Merge `autonomous_agent.py` execution into this pattern
- **Dependency**: Phase 8 (test stability needed before refactoring execution)

### Phase 11 — Intelligent Agent Decomposition
- Currently `intelligent_agent.py` is a wrapper, but `SystemActionParser` and `process_request` are in their new homes
- The wrapper itself can be removed after all external consumers are migrated
- **Dependency**: Audit of external imports

### Phase 12 — CI/CD and Tooling
- Add GitHub Actions (or equivalent) for automated testing
- Add pre-commit hooks for linting
- Document setup process in README
- **Dependency**: Phase 8 (stable test suite needed first)

---

## 9. AI Collaboration Notes

### For Future AI Assistants

**This section is written for you — the next AI engineer to work on this project.**

### Important Conventions

1. **Never guess module structure.** Use `grep`, `glob`, and `read` to verify the current state of files. The codebase has been refactored multiple times and old assumptions may be wrong.

2. **Always check AGENTS.md first.** It contains the most up-to-date module map, context routing table, and change impact map.

3. **Every edit must be syntax-verified.** Run `python -c "import py_compile; py_compile.compile('path/to/file.py', doraise=True)"` after any change.

4. **Never delete a module before its replacement is validated.** Backward-compatible wrappers are the pattern used throughout this project.

### Coding Style

- **Indentation**: 4 spaces. No tabs.
- **Type hints**: Required on all function signatures. Use `from __future__ import annotations` at the top of every module.
- **Naming**: `snake_case` for functions and variables, `PascalCase` for classes, `SCREAMING_SNAKE` for constants and enum values.
- **Strings**: Double quotes for Python code. Single quotes for regex patterns and SQL.
- **Docstrings**: Persian descriptions for internal functions, English for public APIs. The project is bilingual.
- **Logging**: Use `logger` from the `logging` module, never `print()` for production code. Save `print()` for CLI output.
- **Async**: Use `async def` for any function calling LLMs, I/O, or capabilities. Use `await` when calling async capabilities.

### Architectural Principles (Do Not Violate)

1. **Parser never executes.** `IntentAnalyzer` and `SystemActionParser` produce data structures (Intent, action dicts). They never call mouse_control, keyboard_control, or any hardware API.

2. **Executor never parses.** `ActionController` receives action objects or structured dicts. It does not contain regex patterns or NL parsing.

3. **Safety always wins.** Every execution path must go through `SafetyConsentManager` or have an explicit bypass. Never add new execution paths without risk assessment.

4. **Lazy by default.** New capabilities MUST register factory functions in `CapabilityManager`, not create resources in `__init__`. The only exception is the `CapabilityManager` itself and `SessionControl`.

5. **Consolidate before creating.** If you need to change behavior that spans multiple modules, first check if the logic can be merged into an existing module. Adding a new file is the last resort.

6. **Wrappers are temporary.** Any `DeprecationWarning` wrapper should be tracked for removal. Do not add new wrappers without a planned removal date.

### Patterns That Must Be Preserved

- **RouteType dispatch**: All execution paths go through `IntentRouter.route()` → RouteType → CapabilityManager.activate() → execution. This chain is the backbone of the architecture.

- **Backward-compatible refactoring**: When moving code between modules, always leave a re-export wrapper with `DeprecationWarning` behind.

- **CapabilityManager as the single source of truth**: Components are never accessed directly; always through `capability_manager.get("name")` or `capability_manager.activate("name")`.

### Mistakes to Never Repeat

1. **Mode flags in CLI.** Old architecture had 7 mode flags (`--enable-automation`, `--task-mode`, etc.). These are now suppressed but still accepted as no-ops. Never add new mode flags.

2. **17-parameter functions.** `process_user_input()` had 17 parameters, all individually injected. Use CapabilityManager to resolve dependencies instead.

3. **Eager component creation.** Creating DesktopVision, BrowserCore, or ActionController at startup was wasteful. Always register factories and defer creation.

4. **Implicit dependency ordering.** Old code required components to be created in a specific order. CapabilityManager's dependency resolution now handles this explicitly.

5. **Adding files as the default solution.** The ARCHITECTURE_REDESIGN.md proposed 14 new files. The actual solution merged ~5 existing files instead. Always check if consolidation is possible first.

---

## 10. Statistics

| Metric | Value |
|--------|-------|
| Build sessions completed | 6 |
| Modules consolidated into existing files | 4 (dialog_manager, memory_system, master_controller, intelligent_agent) |
| Files reduced from original | ~5-6 (accounting for new wrappers) |
| Core files currently | 41 (unchanged net count — 4 modules became wrappers, but they still exist as files) |
| Lines removed from main.py | ~200 (16% reduction: 1286 → 1081) |
| Lines removed from intelligent_agent.py | ~810 (93% reduction: 876 → 66) |
| Largest file | `core/action_controller.py` (~1400 lines after Phase 6) |
| Remaining legacy wrapper modules | 4 (`dialog_manager.py`, `memory_system.py`, `master_controller.py`, `intelligent_agent.py`) |
| Total test files | 35 (unchanged) |
| Remaining mode flags in parser | 6 (suppressed, kept as no-ops for backward compat) |
| SQLite databases | 1 (`data/memories.sqlite3` with 2 schema systems) |

---

## 11. AI Handoff

*This section describes the current state of the project for the next AI assistant. Updated every Build session.*

### Current Build Progress

| Session | Phase | Objective | Status |
|---------|-------|-----------|--------|
| 1 | Phase 1 | Enhanced CapabilityManager (factory registration, lazy activation, dependencies) | ✅ Complete |
| 2 | Phase 2 | Merge DialogManager into IntentAnalyzer | ✅ Complete |
| 3 | Phase 3 | Merge MasterController routing into IntentRouter/SystemTools | ✅ Complete |
| 4 | Phase 4 | Merge MemorySystem into MemoryIntegrator | ✅ Complete |
| 5 | Phase 5 | Refactor main.py (process_user_input → process_capability_loop) | ✅ Complete |
| 6 | Phase 6 | Decompose intelligent_agent.py (parser → intent_analyzer, executor → action_controller) | ✅ Complete |

### Current Architecture Status

- **Architecture type**: Capability-Driven (post-mode-based)
- **Entry point**: `python main.py` (single conversational entry, no mode flags)
- **Capability registration**: 13 registered capabilities in `CapabilityManager`
- **Routing**: IntentRouter with 7 RouteType values
- **Execution**: Unified in ActionController (desktop + system actions)
- **Memory**: Dual schema in single SQLite file (awaiting unification)
- **Consolidation**: 4 modules converted to backward-compatible wrappers

### Current Refactor Stage

**Consolidation Phase** (merging related modules, removing dead code). The project has moved from "capability-driven transition" to "consolidation and cleanup."

### Remaining Work

1. **Remove dead stubs**: Delete `dialog_manager.py`, `memory_system.py`, `master_controller.py` wrappers after import audit
2. **Update test files**: Point imports to consolidated modules
3. **Unify memory schema**: Merge two SQLite schemas into coherent access layer
4. **Consolidate execution into strategy pattern**: Unify ActionController + AutonomousAgent + BrowserCore
5. **CI/CD pipeline**: Automated testing, linting, pre-commit hooks

### Known Risks

- **Wrapper modules** (4 files) create indirection. They must be removed before they become permanent.
- **action_controller.py** (~1400 lines) is the largest file and may need method extraction.
- **intent_analyzer.py** (~1500 lines) is similarly large after Phase 6 merge.
- **pytest-asyncio** was not in the base environment; tests requiring async markers may fail without it.
- **No CI/CD**: Test suite is only run manually. No regression safety net.
- **Two memory schemas**: Risk of data inconsistency between content memory and execution history.

### Recommended Next Step

**Phase 7: Remove dead stubs.** Audit all imports across the project, update references to consolidated modules, and delete `dialog_manager.py`, `memory_system.py`, and `master_controller.py`. Keep `intelligent_agent.py` wrapper until its remaining consumers are migrated.

### Important Notes for the Next AI

- All 4 wrapper modules (`dialog_manager.py`, `memory_system.py`, `master_controller.py`, `intelligent_agent.py`) show `DeprecationWarning`. Prioritize removing these.
- The `SystemActionParser` class is now in `core/intent_analyzer.py`. If you see an import from `core.intelligent_agent` for the parser, it still works via re-export but should be updated.
- The `ActionController.process_request()` method is the unified entry point for request execution. New execution paths should integrate through it rather than bypassing it.
- If tests fail with async marker issues, install `pytest-asyncio` in the environment.
- Before adding any new file, verify the same functionality cannot be added to an existing module.

---

## Documentation Maintenance Policy

This document and its companion [`AI_PROJECT_RULES.md`](AI_PROJECT_RULES.md) are first-class project infrastructure. Every Build session must:

1. **Update `PROJECT_MIGRATION_CONTEXT.md`**:
   - Update the AI Handoff section (section 11)
   - Append to Build history (section 4) — never overwrite previous entries
   - Update Technical Debt (section 7) — add new debt, mark resolved debt
   - Update the Roadmap (section 8) — mark completed phases, adjust priorities
   - Add new ADRs (section 6) when important architectural decisions are made
   - Keep Statistics (section 10) current
   - Update Version and Last Updated in the header

2. **Update `AI_PROJECT_RULES.md`** only when engineering principles evolve (rare).

3. **Preserve history.** Never overwrite historical information. Append new knowledge while keeping older architectural decisions intact.

### Quality Goal

It should be possible for an experienced software engineer — or any advanced AI coding assistant — to understand the entire project by reading only:

1. `PROJECT_MIGRATION_CONTEXT.md`
2. `AI_PROJECT_RULES.md`

without needing access to previous Build conversations or chat history.

The documentation must remain clear, technically accurate, and continuously maintained as the project evolves. It is the single source of truth for all architectural knowledge.

---
