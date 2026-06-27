# Software-AI — AI-Powered Windows Automation System

**Version**: 0.1.0 (pre-release, active refactoring)  
**Platform**: Windows 10/11 — Python 3.11+  
**Languages**: Persian (primary), English  
**License**: Proprietary (All Rights Reserved)

---

## Project Overview

Software-AI is an autonomous Windows automation system that accepts natural language commands (Persian/English) and routes them through intent analysis, capability-driven planning, and multi-stage execution.

Unlike traditional automation tools that require scripting or explicit mode selection, Software-AI attempts to **understand the user's intent** first, then activates only the required capabilities to fulfill the request.

This project is currently undergoing a **major architectural refactor** — transitioning from a mode-based design (where users selected `--enable-automation` or `--task-mode` flags) to a capability-driven design (where the system auto-detects requirements from natural language). Some legacy flags still exist as silent no-ops for backward compatibility.

---

## Current Features

### What Works Today

| Capability | Status | Notes |
|-----------|--------|-------|
| **Conversational entry** | ✅ Working | Single `python main.py` — no mode flags needed |
| **Intent routing** | ✅ Working | `IntentRouter` classifies requests into 7 route types |
| **Intent analysis** | ✅ Working | `IntentAnalyzer` extracts verb/target/confidence from NL |
| **Plan generation** | ✅ Working | `PlanGenerator` creates multi-step execution plans (up to 50 steps) |
| **Plan validation** | ✅ Working | `PlanValidator` scores safety, reliability, efficiency |
| **Desktop vision** | ✅ Working | Screenshot capture, OCR (Tesseract), element detection (OpenCV) |
| **Mouse control** | ✅ Working | Move, click, drag, scroll via Windows API |
| **Keyboard control** | ✅ Working | Type text, press keys, hotkeys |
| **Smart waiting** | ✅ Working | Wait for idle CPU, window, element appearance, screen change |
| **Action controller** | ✅ Working | High-level desktop actions (click_on_text, fill_form, etc.) |
| **Execution history** | ✅ Working | SQLite persistence for execution records |
| **Memory system** | ✅ Working | Short-term (TTL-based) and long-term (SQLite) content memory |
| **Multi-provider AI** | ✅ Working | Groq → Gemini → OpenRouter → Ollama failover chain |
| **System actions** | ✅ Working | Launch app, install package, query hardware, terminate process |
| **Safety & consent** | ✅ Working | Risk scoring (0-100), user consent gates for high-risk actions |
| **Voice input/output** | ⚠️ Partial | Text-to-speech works; speech-to-text depends on provider |
| **Browser automation** | ⚠️ Partial | Playwright integration exists, not fully integrated into routing |
| **Autonomous agent** | ⚠️ Partial | Goal-driven execution with vision feedback, limited in practice |
| **Realtime loop** | ⚠️ Partial | Monitoring loop exists, not widely used in current flow |

### Limitations (Honest Assessment)

- **Full end-to-end execution** from NL → analyzed → planned → executed is still being validated. The components exist but the pipeline has not been tested as a complete system.
- **AI model reliability** depends on API key availability. Without valid keys for Groq/Gemini/OpenRouter, the system falls back to keyword matching, which is significantly less capable.
- **OCR quality** depends on Tesseract installation and screen resolution. Mixed-language text (Persian + English) can produce unreliable results.
- **Autonomous agent** vision-based execution is slow (~2-5 seconds per screenshot + LLM analysis) and prone to errors on complex UIs.
- **No CI/CD pipeline** — tests must be run manually.
- **Windows only** — no cross-platform support planned.

---

## Architecture Overview

### Five-Layer Stack

```
LAYER 5 [UI]             main.py — single conversational entry point
LAYER 4 [ORCHESTRATION]  IntentRouter → CapabilityManager
LAYER 3 [PLANNING]       IntentAnalyzer → PlanGenerator → PlanValidator → MemoryIntegrator
LAYER 2 [EXECUTION]      ActionController → ExecutionManager
LAYER 1 [CAPABILITIES]   DesktopVision, MouseControl, KeyboardControl, SmartWait,
                         BrowserCore, VoiceIO, SystemTools
```

### Execution Flow

```
User Input (text/voice)
    ↓
IntentRouter.route()
    ├─ IntentAnalyzer.analyze() — extracts Intent{verb, target, params, confidence}
    │
    ├─ CapabilityManager.activate() — lazily creates required resources
    │   └─ Resolves dependencies (prerequisites activated first)
    │
    ├─ SafetyConsentManager — risk assessment + optional user consent
    │
    └─ RouteType dispatch:
         ├─ CHAT_RESPONSE      → AIBrain.ask() → text response
         ├─ BROWSER_USE        → BrowserCore (Playwright)
         ├─ DESKTOP_AUTOMATION → ActionController (vision + mouse + keyboard)
         ├─ AUTONOMOUS_AGENT   → AutonomousAgent (goal-driven)
         ├─ TASK_MODE          → TaskEngine (queued batch execution)
         ├─ CLARIFICATION_NEEDED → dialog with user
         └─ (fallback)         → ActionController.process_request()
    ↓
MemoryIntegrator.record_execution() — persist outcome
```

### Key Design Decisions

- **Capability-driven**: The system, not the user, decides which components to activate.
- **Lazy initialization**: Expensive components (DesktopVision, BrowserCore) are created only when first requested.
- **Consolidated modules**: Multiple legacy modules have been merged into their nearest logical relatives (DialogManager → IntentAnalyzer, MemorySystem → MemoryIntegrator, MasterController → IntentRouter, IntelligentSystemAgent → ActionController).
- **Backward-compatible wrappers**: Deprecated modules still exist as re-export wrappers with `DeprecationWarning` to avoid breaking existing imports.

---

## Project Structure

```
Software-AI/
├── main.py                 # Single entry point
├── core/
│   ├── ai_brain.py         # LLM communication (multi-provider)
│   ├── action_controller.py # Desktop + system action execution (~1500 lines)
│   ├── action_recovery.py  # Error handling and retry
│   ├── action_safety.py    # Pre-execution safety checks
│   ├── agent_core.py       # Core agent utilities
│   ├── autonomous_agent.py # Goal-driven executor with vision feedback
│   ├── browser_core.py     # Playwright-based web automation
│   ├── capability_manager.py # Central registry, factories, lazy activation
│   ├── context_aware_actions.py # Context-dependent behavior
│   ├── desktop_actions.py  # High-level desktop action definitions
│   ├── desktop_vision.py   # Screenshot, OCR, element detection
│   ├── dialog_manager.py   # [DEPRECATED] Re-exports from intent_analyzer
│   ├── execution_manager.py # System action executor (launch, install, etc.)
│   ├── intelligent_agent.py # [DEPRECATED] Re-exports from intent_analyzer + action_controller
│   ├── intent_analyzer.py  # Intent extraction + dialog + action parsing (~1400 lines)
│   ├── intent_router.py    # Route classification, risk assessment
│   ├── keyboard_control.py # Keyboard automation
│   ├── logging_config.py   # Logging infrastructure
│   ├── master_controller.py # [DEPRECATED] Re-exports from intent_router + system_tools
│   ├── memory_integrator.py # Execution history + learned patterns + content memory
│   ├── memory_system.py    # [DEPRECATED] Re-exports from memory_integrator
│   ├── model_config.py     # Model parameters, context limits
│   ├── model_orchestrator.py # Multi-provider fallback logic
│   ├── monitoring_service.py # System health monitoring
│   ├── mouse_control.py    # Mouse operations
│   ├── multi_monitor.py    # Multi-display support
│   ├── plan_generator.py   # Multi-step execution plan creation
│   ├── plan_validator.py   # Plan safety/reliability scoring
│   ├── realtime_interpreter.py # Execution state interpretation
│   ├── realtime_loop.py    # Real-time execution with feedback
│   ├── safety_consent_manager.py # Risk assessment + consent
│   ├── safety_filter.py    # Content filtering
│   ├── smart_wait.py       # Intelligent polling (CPU idle, window, etc.)
│   ├── system_actions.py   # System action definitions
│   ├── system_capabilities.py # System capability registry
│   ├── system_tools.py     # OS-level operations
│   ├── task_engine.py      # Task mode engine
│   └── voice_io.py         # Speech-to-text, text-to-speech
├── tests/                  # 35 test files
├── docs/                   # Documentation (~30 files)
├── data/                   # Runtime data (logs, SQLite DB, screenshots)
├── AI_PROJECT_RULES.md     # Permanent engineering principles
├── PROJECT_MIGRATION_CONTEXT.md  # Architectural evolution record
├── AGENTS.md               # AI agent operational memory
└── requirements.txt        # Python dependencies
```

---

## Installation

### Prerequisites

- **OS**: Windows 10 or 11
- **Python**: 3.11 or later
- **RAM**: 4 GB minimum
- **Internet**: Required for AI model API access

### Setup

```powershell
# 1. Clone
git clone https://github.com/shahincodev/Software-AI-Persian.git
cd Software-AI-Persian

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
Copy-Item .env.example .env
# Edit .env with your API keys (see Configuration section)

# 5. Install Tesseract OCR (optional, needed for desktop vision)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# 6. Run
python main.py
```

---

## Configuration

### `.env` File

```bash
# API Keys — at least one required
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Tesseract OCR path (if not in PATH)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Logging
LOGLEVEL=INFO
```

The system tries providers in this order: **Groq → Gemini → OpenRouter → Ollama (local)**. If all fail, it falls back to keyword-based matching (limited capability).

### CLI Arguments

```
python main.py [options]

  --input-mode {text,voice}     Input type (default: text)
  --tts-provider {gtts,google-cloud,elevenlabs}
  --debug                       Enable debug logging
  --dry-run                     Simulate actions without executing
  --safety-mode {safe,power}    Safety profile (default: safe)
  --risk-threshold INT          Risk threshold 0-100 (default: 70)
  --allow-app APP               Allow specific app (repeatable)
  --allow-path PATH             Allow specific path (repeatable)
  --concurrency INT             Concurrent tasks for TaskEngine (default: 2)
  --mode {browser,code}         [deprecated] Auto-detected
```

**Note**: Legacy mode flags (`--enable-automation`, `--enable-autonomous`, `--task-mode`, `--full`) are accepted as no-ops but have no effect. The system detects capability requirements automatically.

---

## Usage

### Basic Interaction

```powershell
python main.py
```

Type natural language requests. The system routes them automatically:

```
> what is the weather in Tehran?
(router determines: BROWSER_USE → web search)

> create a folder on my desktop called test
(router determines: DESKTOP_AUTOMATION → action execution)

> write a professional email requesting a meeting
(router determines: CHAT_RESPONSE → LLM response)

> open notepad and type hello
(router determines: DESKTOP_AUTOMATION → system + desktop actions)
```

### Explicit Command Shortcuts (Backward Compat)

For power users, explicit prefixes bypass routing:

```
plan <request>          → Force intent analysis + plan generation
smart <request>         → Force intent analysis + plan generation + execute
goal <description>      → Force autonomous agent execution
mouse <command>         → Direct mouse control
type <text>             → Direct keyboard input
wait <condition>        → Direct smart wait
vision <command>        → Direct vision operations
```

### Voice Input

```powershell
python main.py --input-mode voice
```

### Safety Modes

- **safe** (default): High-risk actions require explicit `y/n` confirmation. Threshold at 70.
- **power**: Fewer consent prompts, higher tolerance for automated actions.

---

## Current Limitations

1. **Refactoring in progress**: 4 modules are deprecated wrappers awaiting removal. The codebase has some duplication and inconsistency during the transition.
2. **Unified memory pending**: Two SQLite schemas (`memories` + `execution_history`) coexist in one file without a unified access layer.
3. **Execution pipeline still split**: Desktop actions go through `ActionController`, system actions through `ExecutionManager`. A strategy-pattern unification is planned.
4. **No CI/CD**: Tests must be run manually. No automated regression safety net.
5. **pytest-asyncio required**: Async tests require `pytest-asyncio` to be installed separately.
6. **Windows only**: Relies on Windows API (pywin32) for window management.
7. **AI model dependency**: Without valid API keys, the system degrades to keyword matching, which handles only simple system commands.

---

## Roadmap (Ordered)

1. **Remove deprecated wrappers**: Delete `dialog_manager.py`, `memory_system.py`, `master_controller.py`, then `intelligent_agent.py` after import audit.
2. **Update test files**: Point imports to consolidated modules, add missing test coverage.
3. **Unify memory schema**: Merge content memory and execution history into a coherent access layer.
4. **Strategy-pattern execution**: Unify `ActionController`, `AutonomousAgent`, and `BrowserCore` under a common execution strategy interface.
5. **CI/CD setup**: Automated testing, linting, pre-commit hooks.
6. **End-to-end validation**: Test the complete NL → route → execute → record pipeline.

---

## Documentation

| Document | Purpose |
|----------|---------|
| `AI_PROJECT_RULES.md` | Permanent engineering principles |
| `PROJECT_MIGRATION_CONTEXT.md` | Full architectural history, ADRs, technical debt |
| `AGENTS.md` | AI agent operational memory & context routing |
| `docs/` | ~30 markdown files covering individual modules |

---

## License

**Proprietary — All Rights Reserved.**

© 2025 Shahin (shahincodev)

This software is provided "AS IS" without warranty of any kind. See the [LICENSE](LICENSE) file for details. Contact `shahincodev@gmail.com` for licensing inquiries.
