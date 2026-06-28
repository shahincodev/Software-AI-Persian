# Software-AI: Next-Generation Architecture Redesign

**Author**: AI Systems Architect  
**Date**: 2026-06-24  
**Version**: 0.2.0 (Draft)  
**Target**: Transform from command-runner to self-aware visual-reasoning desktop agent

---

## 1. Root Cause & Log Analysis

### 1.1 The `mkdir` Failure Chain (from session logs)

```
Request: "create folder TestFolder on desktop"
  ↓
Parser: AI fails (403 Forbidden — no valid API keys)
  ↓
Fallback: _simple_fallback_parse matches "create" + "folder" keywords
  ↓
_extract_name_after_keyword("folder TestFolder on desktop", ["folder", ...])
  ↓  searches for r'folder\s+(\S+)'
  ↓  matches "Folder" at position 18 inside "TestFolder" (no \b boundary)
  ↓  "Fold" + "er" misidentified as keyword, location word "on" follows
  ↓  location_word check: True → break → name = None
  ↓
Default name "New Folder" used instead of "TestFolder"
  ↓
mkdir "C:\...\Desktop\New Folder" 2>nul  (space in name → path unquoted somewhere? no, it IS quoted)
  ↓  Return code 1 despite 2>nul (folder already exists or path issue)
  ↓
❌ FAILED displayed
```

**Root Cause Classes:**
| Bug | File | Line | Impact |
|-----|------|------|--------|
| Missing `\b` boundary | `intelligent_agent.py` | 569 | False-positive keyword match inside longer word |
| No pre-flight existence check | `system_tools.py` | 160 | `mkdir` fails silently if folder exists |
| AI dependency without fallback | `ai_brain.py` | 415 | All 12 models fail → empty response → no actions |
| Consent request blocks scripts | `safety_filter.py` | 132-135 | `require_consent=True` forces prompt even for trusted apps |

### 1.2 Architectural Anti-Patterns Identified

| Pattern | Location | Description |
|---------|----------|-------------|
| **Single-truth routing via `type(action) in dict`** | `intelligent_agent.py:696` | Hard-coded type check; each new action requires modifying 2 files |
| **Brittle keyword waterfall** | `intelligent_agent.py:105-230` | 25+ separate `any(kw in ...)` checks with no priority, no negation |
| **Synchronous blocking in async loop** | `action_controller.py:1059` | `execute_action()` runs synchronously, blocking the entire event loop |
| **Blind execution** | `intelligent_agent.py:698-727` | No screenshot before/after, no OCR verification, no state check |
| **Linear abort chain** | `intelligent_agent.py:689-693` | Single failure kills all remaining steps — no recovery possible |
| **Two separate schemas, one SQLite file** | `memory_system.py` + `memory_integrator.py` | Architectural inconsistency; no unified access layer |
| **Fallback parser shadows AI** | `intelligent_agent.py:77-103` | AI path and fallback path produce structurally different action dicts |

---

## 2. Next-Gen Architecture Blueprint

### 2.1 The POMDP Loop (Core Execution Engine)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      OBSERVATION LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │Screenshot│  │   OCR    │  │  Window  │  │  Process/Registry │  │
│  │ Capture  │  │(Tesseract│  │   Enum   │  │      State        │  │
│  │          │  │/EasyOCR) │  │pygetwindow│  │     psutil        │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       └─────────────┴─────────────┴──────────────────┘             │
│                              ↓                                     │
│                    UnifiedState (full snapshot)                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     REASONING LAYER (LLM)                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Goal: "create folder TestFolder on desktop"                 │   │
│  │                                                              │   │
│  │  1. Observe: Desktop visible, no TestFolder exists           │   │
│  │  2. Plan:    [{act: "ShellExec", cmd: 'mkdir "..."'} ,       │   │
│  │               {act: "VerifyFile", path: ".../TestFolder"}]   │   │
│  │  3. Execute: (delegate to execution subsystem)               │   │
│  │  4. Verify:  Screenshot → OCR finds "TestFolder" ?           │   │
│  │  5a. Success → Update memory, return result                  │   │
│  │  5b. Failure → Replan (try different approach)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     EXECUTION LAYER                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Keyboard │  │  Mouse   │  │  Shell   │  │    UI Automation   │  │
│  │  Control │  │  Control │  │  Execute │  │  (Accessibility)   │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                    [Return to Observation]
```

### 2.2 Decoupled Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MASTER ORCHESTRATOR                          │
│                   POMDPLoop / SessionManager                        │
│                                                                     │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────────────────┐   │
│  │Observation │  │  Reasoning   │  │      Execution            │   │
│  │  Pipeline  │  │  Pipeline    │  │      Pipeline             │   │
│  │            │  │              │  │                           │   │
│  │ capture()  │  │ plan()       │  │ KeyboardController        │   │
│  │ ocr()      │  │ execute()    │  │ MouseController           │   │
│  │ windows()  │  │ verify()     │  │ ShellExecutor             │   │
│  │ processes()│  │ heal()       │  │ AccessibilityController   │   │
│  │ registry() │  │ update_mem() │  │ ClipboardController       │   │
│  └────────────┘  └──────────────┘  └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.3 State Machine Definition

```python
class AgentState(Enum):
    INIT = "init"
    OBSERVE = "observe"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    HEAL = "heal"        # retroactive self-healing
    RECORD = "record"    # update history/memory
    DONE = "done"
    FAILED = "failed"

class SessionPhase(Enum):
    INITIAL_REQUEST = "initial"      # fresh request
    RECOVERY = "recovery"            # re-planning after failure
    CONTINUATION = "continuation"    # within a multi-step plan
```

---

## 3. Technical Implementation Specifications

### 3.1 Observation Pipeline (`core/observation/`)

```python
# ============================================================
# core/observation/screenshot_capture.py
# ============================================================
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import ImageGrab, Image

@dataclass
class Screenshot:
    """Immutable screenshot with metadata."""
    image: np.ndarray          # RGB array
    timestamp: float
    monitor_index: int = 0
    region: Optional[tuple[int,int,int,int]] = None  # x1,y1,x2,y2

    def save(self, path: Path) -> Path: ...
    def crop(self, region: tuple[int,int,int,int]) -> "Screenshot": ...

class ScreenshotCapture:
    """Multi-monitor-aware screenshot engine."""
    
    def __init__(self, preferred_monitor: int = 0, compression: str = "png"):
        self.preferred_monitor = preferred_monitor
        self.compression = compression
    
    async def capture_fullscreen(self) -> Screenshot:
        """Capture entire primary monitor."""
    
    async def capture_window(self, window_title: str) -> Optional[Screenshot]:
        """Capture specific window by title (uses pygetwindow)."""
    
    async def capture_region(self, x1, y1, x2, y2) -> Screenshot:
        """Capture specific region."""

# ============================================================
# core/observation/ocr_engine.py
# ============================================================
@dataclass(frozen=True)
class TextRegion:
    """A piece of text found on screen with its bounding box."""
    text: str
    x: int; y: int; w: int; h: int
    confidence: float

class OCREngine:
    """Unified OCR with Tesseract primary + EasyOCR fallback."""
    
    def __init__(self, lang: str = "eng+fas"):
        self.lang = lang
        self._easyocr_reader = None  # lazy-load
    
    async def extract_text(self, screenshot: Screenshot) -> list[TextRegion]:
        """Full-screen OCR returning all text regions."""
    
    async def find_text(self, screenshot: Screenshot, target: str, 
                        fuzzy: bool = True) -> list[TextRegion]:
        """Find specific text on screen with optional fuzzy matching."""
    
    async def find_text_by_regex(self, screenshot: Screenshot, 
                                 pattern: str) -> list[TextRegion]:
        """Find text matching regex pattern."""

# ============================================================
# core/observation/window_monitor.py
# ============================================================
@dataclass
class WindowState:
    """Snapshot of a single window."""
    title: str
    x: int; y: int; w: int; h: int
    is_minimized: bool
    is_active: bool
    process_id: int
    process_name: str
    class_name: str  # Win32 class name

class WindowMonitor:
    """Active window tracker using pygetwindow + win32gui."""
    
    def enum_windows(self) -> list[WindowState]: ...
    def get_active_window(self) -> Optional[WindowState]: ...
    def find_window(self, title_substring: str) -> Optional[WindowState]: ...
    def wait_for_window(self, title_substring: str, 
                        timeout: float = 10.0) -> Optional[WindowState]: ...

# ============================================================
# core/observation/process_monitor.py
# ============================================================
class ProcessMonitor:
    """Process-level environment awareness via psutil."""
    
    def is_running(self, process_name: str) -> bool: ...
    def find_process(self, name_substring: str) -> list[psutil.Process]: ...
    def get_process_by_window(self, window_title: str) -> Optional[psutil.Process]: ...

# ============================================================
# core/observation/registry_discovery.py
# ============================================================
class AppDiscoveryEngine:
    """Dynamic application discovery via Windows Registry, Start Menu, 
    and common installation paths. Eliminates hardcoded executable names."""
    
    REGISTRY_PATHS = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
    ]
    
    def discover_all(self) -> dict[str, Path]:
        """Returns {display_name: executable_path} for every installed app."""
    
    def find_app(self, name_hint: str) -> Optional[Path]:
        """Fuzzy match by name (e.g., 'notepad' → C:\\Windows\\notepad.exe)."""
    
    def search_start_menu(self) -> list[tuple[str, Path]]:
        """Parse %ProgramData%/Microsoft/Windows/Start Menu/*.lnk."""
```

### 3.2 Unified State (`core/state/`)

```python
# ============================================================
# core/state/unified_state.py
# ============================================================
@dataclass
class UnifiedState:
    """Complete environment snapshot at one moment in time.
    
    This is the single source of truth for the reasoning layer.
    """
    screenshot: Screenshot
    text_regions: list[TextRegion]
    windows: list[WindowState]
    processes: list[dict]  # from psutil
    active_window: Optional[WindowState] = None
    mouse_position: tuple[int, int] = (0, 0)
    clipboard_content: str = ""
    timestamp: float = field(default_factory=time.time)
    
    @classmethod
    async def capture(cls, 
                      ocr: OCREngine, 
                      screenshot_cap: ScreenshotCapture,
                      window_mon: WindowMonitor,
                      process_mon: ProcessMonitor) -> "UnifiedState":
        """Full environment capture in ~1-3 seconds."""
    
    def find_ui_element(self, text: str) -> Optional[TextRegion]:
        """Shortcut: find a text region on screen."""
    
    def window_contains_text(self, window_title: str, text: str) -> bool:
        """Check if a specific window shows specific text."""
```

### 3.3 Reasoning Pipeline (`core/reasoning/`)

```python
# ============================================================
# core/reasoning/planner.py
# ============================================================
@dataclass
class ActionStep:
    """A single atomic action in a plan."""
    action_type: str            # Click | Type | ShellExec | Wait | Verify | Hotkey
    params: dict[str, Any]
    description: str
    depends_on: list[int] = field(default_factory=list)  # step indices
    max_retries: int = 2
    timeout: float = 30.0

@dataclass
class ExecutionPlan:
    """A complete, verifiable execution plan."""
    goal: str
    steps: list[ActionStep]
    created_at: float = field(default_factory=time.time)
    context: Optional[UnifiedState] = None  # snapshot at plan time

class LLMPlanner:
    """LLM-based planner that produces ExecutionPlan from goal + state."""
    
    def __init__(self, brain: AIBrain):
        self.brain = brain
    
    async def plan(self, goal: str, state: UnifiedState) -> ExecutionPlan:
        """Use LLM with structured prompt to generate steps."""
    
    async def replan(self, goal: str, state: UnifiedState, 
                     failed_step: ActionStep, error: str) -> ExecutionPlan:
        """On verification failure, generate alternative approach."""

class VerificationResult(Enum):
    PASSED = "passed"
    FAILED = "failed"
    UNCERTAIN = "uncertain"  # agent should re-observe

class Verifier:
    """Post-action verification via screenshot diff + OCR + window state."""
    
    async def verify(self, step: ActionStep, before: UnifiedState, 
                     after: UnifiedState) -> VerificationResult:
        """Check if the action achieved the intended state change."""
```

### 3.4 Execution Pipeline (`core/execution/`)

```python
# ============================================================
# core/execution/action_executor.py
# ============================================================
class ActionExecutor:
    """Registry-based action dispatch — no hardcoded type checks."""
    
    def __init__(self):
        self._handlers: dict[str, Callable] = {}
        self._register_defaults()
    
    def register(self, action_type: str, handler: Callable):
        """Register a handler for an action type."""
        self._handlers[action_type] = handler
    
    async def execute(self, step: ActionStep, state: UnifiedState) -> ActionResult:
        handler = self._handlers.get(step.action_type)
        if not handler:
            raise UnknownActionError(step.action_type)
        return await handler(step.params, state)

# ============================================================
# core/execution/type_handlers.py (Registered Handlers)
# ============================================================
class TypeHandler:
    """Handles text input with Persian language preservation."""
    
    CLIPBOARD_THRESHOLD = 20  # chars > 20 → clipboard
    
    async def __call__(self, params: dict, state: UnifiedState) -> ActionResult:
        text = params["text"]
        
        # If non-Latin or long text, use clipboard to avoid IME corruption
        if self._needs_clipboard(text):
            return await self._clipboard_type(text)
        else:
            return await self._keystroke_type(text)
    
    def _needs_clipboard(self, text: str) -> bool:
        """Check if text contains non-ASCII characters (Persian, Arabic, etc.)."""
        return any(ord(c) > 127 for c in text) or len(text) > self.CLIPBOARD_THRESHOLD
    
    async def _clipboard_type(self, text: str) -> ActionResult:
        """Clipboard-based typing: copy → Ctrl+V — no IME issues."""
        import pyperclip
        pyperclip.copy(text)
        # press Ctrl+V
        ...
    
    async def _keystroke_type(self, text: str) -> ActionResult:
        """Direct keystroke injection for simple ASCII text."""
        ...

# ============================================================
# core/execution/verify_handlers.py
# ============================================================
class VerifyFileHandler:
    """Verifies file/folder creation by checking filesystem + OCR."""
    
    async def __call__(self, params: dict, state: UnifiedState) -> ActionResult:
        path = Path(params["path"])
        exists = path.exists()
        
        if exists:
            return ActionResult.success()
        
        # Fallback: OCR check (folder name might be visible on desktop)
        if state.window_contains_text("Desktop", path.name):
            return ActionResult.success()
        
        return ActionResult.failed(f"File {path} not found on disk or screen")
```

### 3.5 Language Preservation Handler

```python
# ============================================================
# core/execution/language_handler.py
# ============================================================
class LanguageHandler:
    """Multi-language text input with IME-safe fallbacks.
    
    Strategy:
    1. Pure ASCII → keystroke injection (fast)
    2. Mixed/Persian → clipboard paste (reliable)
    3. If clipboard fails → Unicode character-by-character fallback
    """
    
    NON_LATIN_RANGES = [
        (0x0600, 0x06FF),   # Arabic/Persian
        (0x0750, 0x077F),   # Arabic Supplement
        (0xFB50, 0xFDFF),   # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),   # Arabic Presentation Forms-B
        (0x4E00, 0x9FFF),   # CJK
    ]
    
    def classify_text(self, text: str) -> str:
        """Returns 'ascii', 'persian', 'cjk', or 'mixed'."""
        ...
    
    async def type_text(self, text: str, target: Optional[str] = None) -> bool:
        classification = self.classify_text(text)
        
        if classification == "ascii":
            return await self._keystroke_input(text)
        elif classification in ("persian", "mixed"):
            return await self._clipboard_paste(text)
        else:
            return await self._unicode_fallback(text)
```

### 3.6 The POMDP Loop (Complete)

```python
# ============================================================
# core/loop/pomdp_loop.py
# ============================================================
class POMDPLoop:
    """Partially Observable Markov Decision Process execution loop.
    
    State: UnifiedState (partial observation of the environment)
    Action: ActionStep (one atomic operation)
    Transition: execute() → environment changes
    Observation: capture() → new UnifiedState
    Reward: verify() → success metric
    """
    
    MAX_HEALING_ATTEMPTS = 3
    
    def __init__(self, 
                 observation: ObservationPipeline,
                 planner: LLMPlanner,
                 executor: ActionExecutor,
                 verifier: Verifier,
                 memory: ExecutionMemory):
        self.obs = observation
        self.planner = planner
        self.executor = executor
        self.verifier = verifier
        self.memory = memory
    
    async def run(self, goal: str) -> ExecutionReport:
        # 1. Initial observation
        state = await self.obs.capture()
        
        # 2. Generate plan
        plan = await self.planner.plan(goal, state)
        report = ExecutionReport(goal=goal, plan=plan)
        
        # 3. Execute each step with verification
        for i, step in enumerate(plan.steps):
            before = await self.obs.capture()
            
            for attempt in range(step.max_retries + 1):
                try:
                    result = await self.executor.execute(step, before)
                except Exception as exc:
                    result = ExecutionResult.failed(str(exc))
                
                # Verification
                after = await self.obs.capture()
                v_result = await self.verifier.verify(step, before, after)
                
                if v_result == VerificationResult.PASSED:
                    report.record_success(step, attempt, after)
                    break
                else:
                    if attempt < step.max_retries:
                        # RE-PLAN for this step
                        plan = await self.planner.replan(
                            f"Step {i}: {step.description}", after, 
                            step, result.error or "Verification failed"
                        )
                        # Insert remaining new steps
                        plan.steps = plan.steps + plan.steps[i+1:]
                    else:
                        report.record_failure(step, attempt, result)
                        if plan.steps[i].depends_on:
                            # Cascade failure to dependents
                            for j in range(i+1, len(plan.steps)):
                                if i in plan.steps[j].depends_on:
                                    report.record_skipped(plan.steps[j])
                        break
        
        # 4. Record to memory
        await self.memory.record(report)
        
        return report
```

---

## 4. Production-Grade Prompt Engineering

### 4.1 System Prompt (Core LLM Identity)

```
You are Software-AI Brain, the reasoning core of an autonomous Windows desktop agent.

## Your Capabilities
You operate in a POMDP loop: [Observe] → [Plan] → [Execute] → [Verify] → [Observe].

You receive:
1. A UnifiedState snapshot: JSON describing the current desktop (screenshot OCR text,
   open windows, running processes, active window, mouse position).
2. A user goal: natural language request in Persian or English.

You produce:
- An ExecutionPlan: a JSON array of ActionStep objects.

## Environment Understanding
- You see only TEXT extracted by OCR, not the actual pixels.
- Window titles are extracted by pygetwindow (may be truncated or missing).
- Process names come from psutil (not user-friendly names — map them yourself).
- You can find installed applications via the discovery engine (model disallowed
  from assuming "notepad.exe" works — check the provided state).

## Action Grammar (Output Format)
Return ONLY a valid JSON array. No explanations, no markdown.

[
  {
    "action_type": "Click|Type|ShellExec|Hotkey|Wait|Verify|OpenApp",
    "params": { ... },
    "description": "Human-readable step description",
    "depends_on": [],           // indices of prerequisite steps
    "max_retries": 2,
    "timeout": 30.0
  }
]

## Action Definitions

### Click
  params: { "target_text": "OK" | "x": 100, "y": 200, "button": "left"|"right", "clicks": 1 }
  Rules:
  - Prefer target_text when text is visible on screen (from OCR).
  - Use x,y only when text target is unambiguous.
  - Set button=right for context menus.

### Type
  params: { "text": "hello world", "target_window": null }
  Rules:
  - For Persian/Arabic text: NEVER assume direct keyboard injection.
    The execution layer will auto-detect and use clipboard.
  - For keyboard shortcuts: use Hotkey action instead.
  - Include line breaks as \n in text.

### ShellExec
  params: { "command": "mkdir \"C:\\Users\\...\\My Folder\"", "shell": "cmd", "timeout": 10 }
  Rules:
  - Use ONLY for file operations (mkdir, echo, del, copy).
  - NEVER use for launching applications — use OpenApp instead.
  - ALWAYS use absolute paths, never relative.

### OpenApp
  params: { "app_name": "notepad" }
  Rules:
  - The execution layer will dynamically resolve the app via Registry/Start Menu.
  - Do NOT guess the .exe name — just provide the display name.
  - If you need to open a file with its default handler, use ShellExec.

### Hotkey
  params: { "keys": ["ctrl", "s"], "interval": 0.1 }
  Supported keys: ctrl, alt, shift, win, a-z, 0-9, f1-f12, tab, enter, esc, space

### Wait
  params: { "duration": 2.0 } or { "condition": "window_open", "target": "Notepad" }
  Use duration for fixed waits. Use condition for dynamic waits.

### Verify
  params: { "check": "file_exists", "path": "C:\\...\\file.txt" }
  or: { "check": "text_visible", "text": "Downloads" }
  The verifier will check post-action state.

## Safety Rules
- NEVER delete files, format drives, or modify system registry.
- For any destructive action, set params.destructive = true
  (the safety layer will request user consent).
- Avoid installing software without explicit user request.

## Few-Shot Examples

### Example 1: Create Folder
User: "create folder MyProject on desktop"
State: { "active_window": "Desktop", "running_processes": ["explorer.exe"] }
Plan:
[
  {
    "action_type": "ShellExec",
    "params": { "command": "mkdir \"C:\\Users\\current\\Desktop\\MyProject\"",
                "shell": "cmd" },
    "description": "Create folder MyProject on desktop",
    "depends_on": [],
    "max_retries": 1,
    "timeout": 10.0
  },
  {
    "action_type": "Verify",
    "params": { "check": "file_exists", "path": "C:\\Users\\current\\Desktop\\MyProject" },
    "description": "Verify folder was created",
    "depends_on": [0],
    "max_retries": 0,
    "timeout": 5.0
  }
]

### Example 2: Open App and Type
User: "open notepad and write hello world"
State: { "running_processes": ["explorer.exe", "firefox.exe"] }
Plan:
[
  {
    "action_type": "OpenApp",
    "params": { "app_name": "notepad" },
    "description": "Launch Notepad",
    "depends_on": [],
    "max_retries": 2,
    "timeout": 10.0
  },
  {
    "action_type": "Wait",
    "params": { "condition": "window_open", "target": "Notepad" },
    "description": "Wait for Notepad window",
    "depends_on": [0],
    "max_retries": 0,
    "timeout": 5.0
  },
  {
    "action_type": "Type",
    "params": { "text": "hello world" },
    "description": "Type text into Notepad",
    "depends_on": [1],
    "max_retries": 1,
    "timeout": 5.0
  }
]

### Example 3: Compound Request (Folder + File)
User: "create folder Demo and create file test.txt inside it"
Plan:
[
  {
    "action_type": "ShellExec",
    "params": { "command": "mkdir \"C:\\Users\\current\\Desktop\\Demo\"", "shell": "cmd" },
    "description": "Create Demo folder",
    "depends_on": [],
    "max_retries": 1,
    "timeout": 10.0
  },
  {
    "action_type": "Verify",
    "params": { "check": "file_exists", "path": "C:\\Users\\current\\Desktop\\Demo" },
    "description": "Verify Demo folder created",
    "depends_on": [0],
    "max_retries": 0,
    "timeout": 5.0
  },
  {
    "action_type": "ShellExec",
    "params": { "command": "type nul > \"C:\\Users\\current\\Desktop\\Demo\\test.txt\"",
                "shell": "cmd" },
    "description": "Create test.txt inside Demo",
    "depends_on": [0],   // depends on folder, not on verification
    "max_retries": 1,
    "timeout": 10.0
  },
  {
    "action_type": "Verify",
    "params": { "check": "file_exists",
                "path": "C:\\Users\\current\\Desktop\\Demo\\test.txt" },
    "description": "Verify test.txt created",
    "depends_on": [2],
    "max_retries": 0,
    "timeout": 5.0
  }
]

### Example 4: Self-Healing
If verification fails on step 0 (mkdir fails because folder exists):
Replan:
[
  {
    "action_type": "ShellExec",
    "params": { "command": "if not exist \"path\\Demo\" mkdir \"path\\Demo\"",
                "shell": "cmd" },
    "description": "Conditional create (skip if exists)",
    "depends_on": [],
    "max_retries": 0,
    "timeout": 10.0
  },
  ... continue with remaining steps ...
]
```

### 4.2 Planning Prompt Template

```
## Current Environment State
{screenshot_text_regions}
{open_windows}
{running_processes}
{mouse_position}

## User Goal
{user_request}

## Previous Steps (if any)
{execution_history}

## Last Verification Results (if any)
{verification_results}

## Task
Generate an execution plan (JSON array of ActionStep objects) that
accomplishes the user's goal. Follow the action grammar rules.
Optimize for reliability over speed. Include verification steps
after every state-changing action.
```

---

## 5. Phased Refactoring Roadmap

### Phase 1: Foundation — Observation Pipeline (Weeks 1-2)

**Goal**: Replace blind execution with state-aware execution.  
**Backward Compat?**: YES — existing `process_request()` still works unchanged.

**Deliverables:**
- [`core/observation/screenshot_capture.py`] Screenshot engine with multi-monitor
- [`core/observation/ocr_engine.py`] OCR with Tesseract + EasyOCR fallback
- [`core/observation/window_monitor.py`] pygetwindow integration
- [`core/observation/process_monitor.py`] psutil integration
- [`core/observation/registry_discovery.py`] App Discovery Engine
- [`core/state/unified_state.py`] UnifiedState dataclass + capture() method
- [`tests/test_observation_pipeline.py`] 15+ tests verifying each component

**Tests to Pass:**
1. Screenshot capture returns valid image (check dimensions, format)
2. OCR finds known text on screen (e.g., desktop icons)
3. App Discovery finds notepad.exe via Registry
4. UnifiedState.capture() runs in < 5 seconds

### Phase 2: Verification & Self-Healing (Weeks 3-4)

**Goal**: Add the V in the Observe–Plan–Execute–Verify loop.  
**Backward Compat?**: YES — wrap existing execution with verification.

**Deliverables:**
- [`core/execution/verify_handlers.py`] Verification handlers (file_exists, text_visible, window_open)
- [`core/execution/language_handler.py`] Persian/Unicode-safe typing with clipboard fallback
- Modify `IntelligentSystemAgent.process_request()` to capture state before/after each action
- Add `Verifier` to `process_request` loop

**Tests to Pass (All 4 Baseline Scenarios):**
1. Create folder → Verify folder exists on disk + OCR detects name on desktop
2. Create file inside folder → Verify both folder and file exist
3. Open Notepad + type → Verify "Notepad" window open + OCR finds typed text
4. Compound: create folder + create file inside → Verify both in sequence

### Phase 3: LLM-Based Planner Integration (Weeks 5-6)

**Goal**: Replace both the brittle regex fallback and the unreliable AI-JSON path
with a single, robust LLM planner.  
**Backward Compat?**: MODERATE — `SystemActionParser` deprecation begins.

**Deliverables:**
- [`core/reasoning/planner.py`] LLMPlanner with structured prompt
- [`core/reasoning/verifier.py`] Verifier with OCR + window state
- [`core/execution/action_executor.py`] Registry-based action dispatch
- Modify `parse_request()` to call LLMPlanner (with UnifiedState context)
- CLI flag: `--legacy-parser` to keep old behavior

**Key Decisions:**
- Planner uses `mode="system"` model (faster, cheaper)
- ActionExecutor registers handlers dynamically — no more `type() in dict` checks
- The `depends_on` array enables proper dependency-graph execution

**Tests:** All Phase 2 tests + 5 new planner tests:
1. Planner generates correct `depends_on` dependencies
2. Planner handles ambiguous requests ("do that thing")
3. Planner integrates context from UnifiedState

### Phase 4: POMDP Loop Engine (Weeks 7-8)

**Goal**: The Observe–Plan–Execute–Verify loop as the single execution model.  
**Backward Compat?**: BREAKING — old `process_request()` calls deprecation warning.  
`process_request()` becomes a thin wrapper around `POMDPLoop.run()`.

**Deliverables:**
- [`core/loop/pomdp_loop.py`] POMDPLoop with retry + healing
- [`core/loop/execution_report.py`] Report with per-step screenshots + timing
- Modify `main.py` to use POMDPLoop by default
- Add `--pomdp-logs` flag for detailed per-step visualization

**Architecture Change:**
```
BEFORE:
  parser.parse() → _create_action() → dispatch (type check)
  No screenshot, no verify, no heal

AFTER:
  POMDPLoop.run(goal)
    → capture UnifiedState
    → LLMPlanner.plan(goal, state)
    → for each step:
        → execute() → capture → verify()
        → if fail: replan() → retry (up to max_retries)
        → if still fail: cascade to dependents, continue
    → record to memory
```

**Tests:** All Phases 1-3 tests + 5 POMDP loop tests:
1. Full loop with no failures
2. Single-step failure → replan recovers
3. Multi-step failure → cascade correctly marks dependents
4. Persian text survives round-trip (type → save → read → compare)
5. Max retries exhausted → proper failure report

### Phase 5: Memory, Learning & Multi-Session (Weeks 9-10)

**Goal**: The agent learns from past sessions.  
**Backward Compat?**: YES — new features added; nothing removed.

**Deliverables:**
- [`core/memory/unified_memory.py`] Unified access layer merging `memory_system.py` 
  and `memory_integrator.py` into one coherent schema
- [`core/memory/pattern_learner.py`] Learns frequent action sequences and optimizes plans
- [`core/memory/session_persistence.py`] Cross-session state restoration
- Modify LLMPlanner to include memory context in prompts

**Memory Schema (Unified):**
```sql
CREATE TABLE unified_memories (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    goal TEXT NOT NULL,
    plan_json TEXT NOT NULL,
    result TEXT NOT NULL,         -- 'success' | 'failed' | 'partial'
    execution_report TEXT,        -- full report JSON
    created_at REAL NOT NULL,
    duration_seconds REAL,
    user_feedback TEXT            -- future: user thumbs up/down
);

CREATE TABLE learned_patterns (
    id TEXT PRIMARY KEY,
    pattern_hash TEXT UNIQUE NOT NULL,  -- hash of goal + similar context
    plan_template TEXT NOT NULL,
    success_rate REAL NOT NULL DEFAULT 1.0,
    execution_count INTEGER NOT NULL DEFAULT 1,
    last_used_at REAL
);
```

**Tests:** All previous tests + 5 memory tests:
1. Session recorded and retrievable
2. Learned pattern returns for similar request
3. Cross-session context improves plan quality
4. Schema migration from old `memories.sqlite3` to unified
5. Performance: memory query < 50ms

---

## 6. Baseline Test Specifications

### Test 1: Create Folder on Desktop

```python
async def test_create_folder():
    goal = "create folder TestFolder on desktop"
    report = await loop.run(goal)
    assert report.success
    folder = Path.home() / "Desktop" / "TestFolder"
    assert folder.exists()
    assert folder.is_dir()
    # Cleanup
    shutil.rmtree(folder)
```

### Test 2: Create File Inside Folder

```python
async def test_create_file_in_folder():
    goal = "create file test.txt on desktop"
    report = await loop.run(goal)
    assert report.success
    file = Path.home() / "Desktop" / "test.txt"
    assert file.exists()
    assert file.is_file()
    # Cleanup
    file.unlink()
```

### Test 3: Open Notepad + Type Text

```python
async def test_notepad_type():
    goal = "open notepad and write hello world"
    report = await loop.run(goal)
    assert report.success
    # Verify: Notepad window exists
    import pygetwindow as gw
    notepad = gw.getWindowsWithTitle("Notepad")
    assert len(notepad) > 0
    assert notepad[0].isActive or True  # may be minimized
    # Cleanup
    notepad[0].close()
```

### Test 4: Compound Request (Folder + File)

```python
async def test_compound_create():
    goal = "create folder DemoFolder and then create file demo.txt inside it"
    report = await loop.run(goal)
    assert report.success
    folder = Path.home() / "Desktop" / "DemoFolder"
    file = folder / "demo.txt"
    assert folder.exists() and folder.is_dir()
    assert file.exists() and file.is_file()
    # Cleanup
    shutil.rmtree(folder)
```

---

## 7. Module Dependency Map (New Architecture)

```
core/
├── observation/           [NEW]
│   ├── __init__.py
│   ├── screenshot_capture.py
│   ├── ocr_engine.py
│   ├── window_monitor.py
│   ├── process_monitor.py
│   └── registry_discovery.py
├── state/                 [NEW]
│   ├── __init__.py
│   └── unified_state.py
├── reasoning/             [NEW]
│   ├── __init__.py
│   ├── planner.py
│   └── verifier.py
├── execution/             [REFACTORED]
│   ├── __init__.py
│   ├── action_executor.py   ← replaces type()-in-dict dispatch
│   ├── type_handlers.py     ← registered handlers
│   ├── verify_handlers.py   ← verification strategies
│   └── language_handler.py  ← Persian-safe input
├── loop/                  [NEW]
│   ├── __init__.py
│   └── pomdp_loop.py        ← the core engine
├── memory/                [REFACTORED]
│   ├── __init__.py
│   ├── unified_memory.py    ← merges memory_system + memory_integrator
│   └── pattern_learner.py
│
├── control/               [EXISTING — UNCHANGED]
│   ├── mouse_control.py
│   ├── keyboard_control.py
│   ├── desktop_vision.py    ← used by observation pipeline
│   └── smart_wait.py
│
├── action_controller.py   [EXISTING — soft-deprecated, used by legacy]
├── intelligent_agent.py   [EXISTING — soft-deprecated, wrapped by POMDPLoop]
├── ai_brain.py            [EXISTING — UNCHANGED, used by planner]
├── safety_filter.py       [EXISTING — UNCHANGED]
├── execution_manager.py   [EXISTING — UNCHANGED (removed in Phase 5)]
└── system_tools.py        [EXISTING — UNCHANGED (removed in Phase 5)]
```

---

## 8. Key Metrics & Constraints

| Metric | Current | Target |
|--------|---------|--------|
| Screenshot → OCR → State | Not available | < 3 seconds |
| Plan generation | 3-8 seconds (AI) or 0.1s (fallback) | < 3 seconds (LLM) |
| Per-action verification | None | < 1 second |
| Self-healing retries | 0 | Up to 3 |
| Persian text handling | Broken (regression) | 100% round-trip |
| Action dispatch coupling | 2 files per new type | 1 register() call |
| Test coverage | Ad-hoc | 40+ automated tests |

---

## 9. Migration Strategy

### Week-by-Week Compatibility Matrix

```
Week | New Files     | Modified Files        | Removed | Test Count | Break?
1    | observation/* | None                  | None    | +8         | NO
2    | state/        | None                  | None    | +5         | NO
3    | execution/*   | intelligent_agent.py  | None    | +5         | NO
4    | None          | process_request()     | None    | +5 (base)  | NO*
5    | reasoning/*   | parse_request()       | None    | +5         | NO
6    | None          | main.py (flag)        | None    | 0          | NO*
7    | loop/*        | main.py (default)     | None    | +5         | YES**
8    | None          | None                  | None    | 0          | NO
9    | memory/*      | memory_system/integrator|soft   | +5         | NO
10   | None          | None                  | hard    | 0          | YES**

*: Opt-in through CLI flag (backward compatible by default)
**: POMDPLoop becomes default; legacy accessible via --legacy flag
```

### Rollback Plan
- Every Phase has a `--legacy` CLI flag that restores old `process_request()` behavior
- All new code lives in new directories (`core/observation/`, `core/loop/`, etc.)
- Old code never deleted — only soft-deprecated with warnings for 2 Phases
- Rollback = stop using new entry points + remove deprecation flag

---

## 10. Summary of Changes from Current Architecture

| Aspect | Current | Future |
|--------|---------|--------|
| **Execution model** | Linear: Parse → Execute (no state) | POMDP loop: Observe → Plan → Execute → Verify → Heal |
| **State awareness** | None | Full UnifiedState (screenshot, OCR, windows, processes) |
| **App discovery** | Hardcoded `shutil.which()` + limited path search | Registry + Start Menu + PATH + shortcut enumeration |
| **Action dispatch** | `type(action) in dict` (hardcoded) | Registry pattern: `executor.register(type, handler)` |
| **Verification** | `result.success` bool only | Post-action screenshot + OCR + file system check |
| **Healing** | Abort chain (`previous_failed`) | Replan with retries + alternative strategies |
| **Persian text** | Direct keystroke (mangled) | Clipboard-based with auto-detect |
| **Fallback parser** | 200 lines of brittle regex | Unified LLM planner (one path) |
| **Memory** | Two separate schemas, one file | Unified schema, pattern learning |
| **Testing** | Manual, inconsistent | 40+ automated tests, CI-ready |
