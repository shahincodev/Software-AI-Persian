# Bug Fix Report — Software-AI

## Overview

This report documents all bugs identified and fixed in the Software-AI Persian Windows Control System during the debugging session. The primary goal was to fix architectural flaws that caused conversational queries to be typed into Notepad instead of printed to the terminal, misrouting of requests, and a broken AI fallback chain.

---

## Bug 1: Conversational Queries Routed to Desktop Automation

**Severity:** Critical  
**File:** `main.py`, `core/intent_analyzer.py`, `core/intent_router.py`

### Root Cause

When a user typed a greeting or chitchat (e.g., `"سلام"`, `"how are you"`, `"چطوری"`), the request fell through to the `else` branch in `main.py`, which called `system_agent.process_request()`. This routed through `ActionController.process_request()` → `SystemActionParser.parse_request()` → `AIBrain.interpret_system_request()`. The AI model, lacking a conversational verb, returned a `DesktopType` action that typed the text into the foreground window (typically Notepad if it was the active window).

### Fix

1. **`core/intent_analyzer.py`:** Added `"converse"` and `"گفتگو"` to `known_verbs` so conversational intents are recognized as valid verbs.

2. **`core/intent_router.py`:** Added a confidence gate in `_classify_intent()`: when `intent.confidence < 0.75` and the request contains question markers (e.g., `"?"`, `"چی"`, `"کی"`), the route is forced to `CHAT_RESPONSE`.

3. **`core/intent_router.py`:** Added raw-request keyword pattern matching as a fallback for web, desktop, and task routing when AI models fail and the verb/target are both `"unknown"`.

4. **`main.py`:** Added a dedicated `CHAT_RESPONSE` handler that calls `AIBrain.ask()` directly and prints the AI response to terminal, bypassing `ActionController` entirely.

---

## Bug 2: Verb Extraction False Positives

**Severity:** Medium  
**File:** `core/intent_analyzer.py`

### Root Cause

The `_extract_verb()` method used `str.lower()` + `in` checks for English verb aliases. This caused false positives: e.g., `"ask"` matched inside `"task"`, and `"open"` matched inside `"openai"`.

### Fix

Switched English verb alias matching to `\b` word-boundary regex in `_extract_verb()`. This ensures that `"ask"` only matches the standalone word `"ask"`, not as a substring of `"task"`.

---

## Bug 3: System Action Results Not Displayed

**Severity:** Low  
**File:** `core/action_controller.py`

### Root Cause

When `ActionController.process_request()` executed system actions (e.g., hardware queries), the action's output was computed but never printed to the console, making the system appear unresponsive.

### Fix

Captured `result.output` in `process_request()` and appended it to the returned summary string, so action outputs appear in the terminal.

---

## Bug 4: AIBrain Hangs on Unresponsive Models

**Severity:** Medium  
**File:** `core/ai_brain.py`

### Root Cause

The `AIBrain.ask()` method called `model.ainvoke()` and `model.invoke()` without a timeout. If a model became unresponsive (e.g., Ollama without `langchain_community` installed), the call would hang indefinitely.

### Fix

Added `import asyncio` and wrapped both `model.ainvoke()` and `model.invoke()` with `asyncio.wait_for(timeout=60.0)`. A 60-second timeout is applied, after which a `TimeoutError` is raised and handled gracefully.

---

## Bug 5: PlanGenerator Crash on IntentAnalysisResult

**Severity:** High  
**File:** `core/plan_generator.py`

### Root Cause

`PlanGenerator.generate_plan()` had a type annotation of `Intent` but was called with `IntentAnalysisResult` objects (which wrap an `Intent` in `.intent`) by several integration tests. The method accessed `intent.verb` and `intent.target` directly, causing `AttributeError` when called with `IntentAnalysisResult`.

### Fix

Added an `isinstance` check at the top of `generate_plan()`:

```python
if isinstance(intent, IntentAnalysisResult):
    intent = intent.intent
```

This unwraps the result transparently. Also imported `IntentAnalysisResult` from `core.intent_analyzer`.

---

## Bug 6: MemoryIntegrator Crash on IntentAnalysisResult

**Severity:** High  
**File:** `core/memory_integrator.py`

### Root Cause

`MemoryIntegrator._hash_intent()` accessed `intent.verb`, `intent.target`, and `intent.language` directly but was called with `IntentAnalysisResult` objects (via `record_execution()` and `find_similar_plans()`). This caused `AttributeError`.

### Fix

Added an `isinstance` check at the top of `_hash_intent()`:

```python
if isinstance(intent, IntentAnalysisResult):
    intent = intent.intent
```

Also imported `IntentAnalysisResult` from `core.intent_analyzer`.

---

## Files Modified

| File | Changes |
|------|---------|
| `main.py` | Added `CHAT_RESPONSE` handler, switched to `ActionController` directly, removed `IntelligentSystemAgent` import, added `AIBrain` import |
| `core/intent_analyzer.py` | Added `"converse"` / `"گفتگو"` verbs, added `import re`, switched `_extract_verb` to word-boundary regex |
| `core/intent_router.py` | Added confidence gate (<0.75 → check question markers), added raw-request keyword fallback for web/desktop/task routing |
| `core/action_controller.py` | Captured `result.output` in `process_request()` |
| `core/ai_brain.py` | Added `import asyncio`, wrapped `ainvoke`/`invoke` with `asyncio.wait_for(timeout=60.0)` |
| `core/plan_generator.py` | Imported `IntentAnalysisResult`, added unwrap in `generate_plan()` |
| `core/memory_integrator.py` | Imported `IntentAnalysisResult`, added unwrap in `_hash_intent()` |
| `tests/test_intent_system_integration.py` | Fixed 6 pre-existing test bugs: missing `await` on coroutines, `IntentAnalysisResult` vs `Intent` access patterns, dead `generate_dialog()` call, assertion values |

---

## Test Results

| Test File | Result | Notes |
|-----------|--------|-------|
| `test_plan_generator.py` | **32/32 PASSED** | Unchanged |
| `test_intent_system_integration.py` | **20/20 PASSED** | Was 0/20 before source code + test fixes |
| `test_system.py` | **5/5 PASSED** | Unchanged |
| `test_dialog_manager.py` | 14/40 PASSED, 26 FAILED | Pre-existing: deprecated module, methods removed during consolidation |
| `test_intent_analyzer.py` | 0/41 ERROR | Pre-existing: async fixtures used by sync tests missing `@pytest.mark.asyncio` |
| `test_intelligent_agent.py` | 0/1 FAILED | Pre-existing: missing `@pytest.mark.asyncio` decorator |

---

## Pre-existing Issues Not Fixed

The following issues are pre-existing and were not caused by this session's changes:

1. **`test_dialog_manager.py` (26 failures):** The `DialogManager` module has been deprecated and its internal methods (`_generate_question`, `_calculate_response_confidence`, `_confirm_understanding`, `_merge_responses_with_intent`) were removed during consolidation into `IntentAnalyzer`. The test file still references these removed methods.

2. **`test_intent_analyzer.py` (41 errors):** The test file uses async fixtures (`analyzer`) but the test methods are synchronous and missing the `@pytest.mark.asyncio` decorator. This is a test framework configuration issue.

3. **`test_intelligent_agent.py` (1 failure):** The `test_basic_functionality` test is an async function but missing the `@pytest.mark.asyncio` decorator.

4. **`langchain_community` not installed:** The Ollama model fallback requires `langchain_community`, which is not in the project dependencies. This is a pre-existing environment issue.

5. **`test_system.py` encoding errors on Windows:** The `charmap` codec errors are a Windows console environment limitation, not a code bug.
