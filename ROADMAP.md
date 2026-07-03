# Software-AI Improvement Roadmap

## Objective

The goal of this roadmap is to transform this project into a true AI-powered desktop agent capable of understanding natural language requests and autonomously controlling a Windows computer through mouse, keyboard, vision, browser automation, and system commands.

This document is the project's long-term implementation plan. Keep it updated as each phase is completed.

---

# Phase 1 — Stabilize the Execution Pipeline

## Goals

* Ensure desktop automation requests never fall back to chat because of routing issues.
* Verify the entire execution pipeline works end-to-end.
* Improve path resolution and command execution reliability.

## Tasks

* Verify the Intent → Router → ActionController → Execution pipeline.
* Remove any remaining routing downgrade logic.
* Clear obsolete caches if necessary.
* Improve Windows path parsing.
* Support:

  * Desktop
  * Downloads
  * Documents
  * Any drive (C:, D:, E:, ...)
  * Absolute and relative paths
* Improve file and folder creation reliability.
* Improve error reporting and logging.

**Completion Criteria**

* "Create a file on drive D"
* "Create a folder in Downloads"

should execute successfully without AI fallback failures.

---

# Phase 2 — Replace Chat Responses with Structured Tool Calling

## Goals

The AI must stop behaving like a chatbot and instead become an action planner.

## Tasks

* Redesign `AIBrain.interpret_system_request()`.
* Force structured tool outputs instead of conversational text.
* Introduce a strict tool schema.
* Validate every AI response.
* Retry automatically if invalid output is returned.
* Keep the existing fallback parser only as an emergency backup.

**Completion Criteria**

* Natural language requests are consistently converted into executable actions.
* ✅ Completed: Unified tool schema with 13 tools, validation, auto-retry (max 2), and emergency fallback.

---

# Phase 3 — Build an Autonomous Vision Loop

## Goals

Create a real autonomous desktop agent.

Instead of blindly executing commands, the agent should continuously observe the screen, reason, act, and verify.

Execution loop:

1. Capture the screen.
2. Analyze the current state.
3. Ask the AI for the next action.
4. Execute the action.
5. Capture the screen again.
6. Verify success.
7. Retry if necessary.
8. Continue until the goal is complete.

## Tasks

* Integrate DesktopVision into the execution loop.
* Implement visual verification.
* Improve OCR usage.
* Detect UI failures automatically.
* Retry with alternative actions when needed.

**Completion Criteria**

* ✅ Completed: VisionLoopManager with observe → act → verify → retry cycle, 5 vision tools, screen context in AI prompts.

---

# Phase 4 — Intelligent Multi-Step Planning

## Goals

Support complex user requests consisting of multiple dependent actions.

Example:

> Open Chrome, search for OpenAI, summarize the homepage, then save the summary into a text file.

## Tasks

* Break large requests into atomic actions.
* Maintain execution context between steps.
* Track progress.
* Recover from failures.
* Resume execution when possible.

**Completion Criteria**

The agent reliably completes long workflows with minimal user supervision.

---

# Phase 5 — Intelligent Windows Environment Understanding

## Goals

Allow the agent to understand the user's computer naturally.

## Tasks

* Resolve common Windows locations.
* Detect installed applications.
* Discover executable locations automatically.
* Support localized Windows folder names.
* Improve environment awareness.

The agent should understand requests like:

* "Save it to Downloads."
* "Open VS Code."
* "Create a project on drive D."
* "Move it into Documents."

without requiring explicit paths.

---

# Long-Term Vision

The final system should function as a true AI desktop agent rather than a traditional automation script.

It should be capable of:

* Understanding natural language.
* Planning complex workflows.
* Controlling the mouse and keyboard.
* Observing the screen.
* Interacting with desktop applications.
* Browsing the web autonomously.
* Recovering from errors.
* Verifying task completion.
* Executing multi-step goals.
* Continuously improving reliability while maintaining safe execution.

---

# Development Rules

* Prioritize reliability over adding new features.
* Never break existing functionality.
* Every phase must include testing before moving to the next.
* Update this roadmap whenever a phase is completed or significantly changed.
* Keep the implementation modular and maintainable.
* Favor structured tool execution over free-form AI responses whenever possible.
 