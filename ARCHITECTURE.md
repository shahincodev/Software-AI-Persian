# Software-AI Final Architecture

Status: approved engineering baseline; extension review complete

Software-AI is a Windows-first, local-first AI agent platform. The first release is a modular monolith: one Python process owns agent orchestration and Windows execution, with a local API/event boundary for the user interface. The design keeps the agent brain, tools, authorization, observation, and persistence separate without introducing distributed-system overhead.

## Stack

| Area | Decision |
| --- | --- |
| Agent runtime | Python 3.12+; validate on supported Windows Python versions before release |
| Type and packaging | `pyproject.toml`, typed public interfaces, `src/` layout |
| API boundary | FastAPI with typed request/response models and server-sent events for task updates |
| UI | React + TypeScript, built with Vite; UI never executes tools directly |
| Persistence | SQLite with explicit migrations and WAL mode |
| Model layer | Provider-neutral async protocol; adapters for OpenAI-compatible endpoints and Google initially |
| Windows control | Win32/UI Automation for semantic control; PyAutoGUI only as a controlled fallback |
| Screenshots/OCR | Pillow capture, Tesseract adapter, optional vision provider; lazy initialization |
| Browser | Playwright integration after the desktop core is stable |
| Secrets | Windows Credential Manager or DPAPI-backed storage; environment variables only for development |
| Testing | pytest, pytest-asyncio, contract tests, mocked providers, controlled Windows integration tests |
| Quality | Ruff, mypy or pyright, structured JSON logging, CI on Windows |

Python is the system of record because process, filesystem, UI Automation, input, and Windows security boundaries are first-class requirements. The React application is a client of the agent, not a second implementation of the agent.

## Runtime Boundaries

```text
UI / local API
    -> Task Manager
        -> Agent Brain
            -> Context Manager -> Memory Repository
            -> Router / Planner -> Model Provider
            -> Security Authorizer -> Confirmation Service
            -> Executor -> Tool Registry -> Tools / Plugins
            -> Observer -> Verifier
            -> Recovery Manager
```

The central loop is:

```text
observe -> understand -> plan when needed -> authorize -> act
-> observe -> verify -> continue / replan / recover
```

Simple conversation does not create a task or invoke expensive perception. Direct safe actions use a short path. Multi-step or uncertain work uses the persisted task state machine.

## Future Evolution Boundaries

The following extension points are part of the architecture but are deliberately deferred. They must integrate through the existing task, tool, security, context, and persistence contracts. They do not add MVP services, databases, or runtime behavior.

### Agent Identity and Capability Model

An agent identity represents the principal operating on behalf of a user or workspace. It is not the same as a model identity, process identity, Windows account, or plugin identity.

An identity should eventually contain:

- Stable agent ID and version
- Human owner or owning workspace
- Purpose and operating profile
- Enabled capability references
- Credential and data scopes
- Lifecycle and revocation status

Capabilities describe what an identity may request. Tools describe how a capability is technically performed. Authorization remains the authority that decides whether a specific action is allowed for a target and context.

The relationship is:

```text
Owner -> Agent Identity -> Capability Grant -> Tool Request -> Security Decision
```

Ownership does not imply unrestricted access. A plugin, skill, or model cannot acquire capabilities by declaring them. Capability grants must be explicit, scoped, revocable, auditable, and independent of memory or experience scores. The initial implementation uses one local user-owned agent identity and does not need a multi-tenant identity service.

### Experience Memory System

Experience memory stores task-level outcomes, not authority. An experience may include:

- Goal and normalized task category
- Relevant, non-sensitive context summary
- Chosen strategy and tool sequence
- Observations and verification outcomes
- Failures, recovery attempts, and final status
- Duration, cost, and user feedback
- Provenance, confidence, retention, and timestamps

Successful experiences may provide candidate plans, ordering hints, or strategy rankings for future planning. Failed experiences may identify fragile targets, unavailable tools, or approaches to avoid. Experiences must be treated as evidence, not truth: the current environment must be observed and the candidate plan must still be validated and authorized.

Experience retrieval belongs behind the Context Manager. Learning may change planner suggestions or confidence, but it must never change risk classification, bypass confirmation, expand capability grants, or authorize a tool. The MVP stores only explicit task history needed for persistence and recovery; similarity search, pattern mining, and optimization are future work.

### Skill System

A tool is an atomic capability with a typed contract, one execution boundary, a risk declaration, and a verifiable result. A skill is a reusable workflow definition that composes tools and may include prerequisites, inputs, checkpoints, expected outcomes, and recovery guidance.

```text
Skill = validated workflow definition
Tool  = atomic capability implementation
```

Skills do not receive autonomous authority. Before execution, a skill must be expanded or interpreted into tool requests, and every request must pass normal validation and security authorization. Skill metadata should eventually include:

- Stable ID and version
- Required capabilities and input schema
- Allowed tools and data scopes
- Preconditions and postconditions
- Confirmation points and maximum bounds
- Owner, provenance, and compatibility requirements

Future skills may be built-in, user-created, or supplied by a trusted plugin. They must be schema-validated, statically checked for forbidden tool combinations, bounded for steps/time/retries, tested in a dry-run or sandbox where possible, versioned, and revocable. A skill cannot grant capabilities to itself or another skill.

The MVP has no skill loader or skill marketplace. Its plan model should remain compatible with a future `skill_id` reference without requiring the Agent Brain to be rewritten.

### Reflection Loop

Reflection is a post-task evaluation phase, not private chain-of-thought exposure and not a second unrestricted planning loop. After completion, partial completion, failure, or cancellation, a bounded evaluator may assess:

- Whether the stated goal was achieved
- Whether verification evidence was sufficient
- Which steps were effective or fragile
- Whether recovery was appropriate
- User correction or satisfaction signals
- Whether the experience is worth retaining

Reflection outputs are structured improvement signals, such as strategy success rates, tool reliability observations, clarification requirements, or a proposed skill candidate. They must include provenance and confidence and remain subject to retention and privacy policy.

Reflection may update experience and planner metadata only through a controlled learning writer. It cannot modify security policies, capability grants, tool implementations, audit history, or completed task results. Negative feedback must be able to reduce confidence or invalidate a learned pattern. The MVP records final task status and optional user feedback; automated reflection and skill synthesis are deferred.

## Non-Negotiable Rules

1. The Agent Brain chooses strategies; tools expose deterministic capabilities.
2. The Planner does not execute and the Executor does not parse natural language.
3. Every side effect passes through the Security Authorizer.
4. Memory supplies context and never grants authority.
5. External content and tool output are untrusted data, not instructions.
6. Computer Use perception cannot execute actions or bypass authorization.
7. Cancellation is distinct from failure and stops new actions immediately.
8. Side effects are verified where practical; uncertain timeouts are never blindly replayed.
9. Risk, confirmation, and audit decisions are explicit, testable, and persisted when needed.
10. New capabilities register tools instead of adding branches to the Agent Brain.

## Task Complexity

- Level 1: direct tool call, verification, response.
- Level 2: bounded sequence with important-step verification.
- Level 3: persisted plan, observation, adaptive execution, recovery, and possible user intervention.

Task states are limited to: `PENDING`, `PLANNING`, `READY`, `RUNNING`, `VERIFYING`, `WAITING_FOR_USER`, `RECOVERING`, `COMPLETED`, `PARTIALLY_COMPLETED`, `FAILED`, and `CANCELLED`.

## Security Baseline

Risk is derived from action, target, context, and consequence. Authorization scopes are task, session, and explicitly enabled persistent policy. Read-only inspection is normally automatic. Deletion, arbitrary command execution, credential access, installation, registry/system changes, and external side effects require policy-controlled confirmation; critical operations fail closed by default.

The initial shell surface is restricted. Typed filesystem, process, and application tools are preferred. Any later PowerShell tool must use an allowlisted command policy, bounded execution, working-directory restrictions, cancellation, and independent tests.

## Deferred Capabilities

The MVP does not include agent identity management beyond the local owner, an experience-learning service, a skill loader, automated reflection, a vector database, knowledge graph, autonomous memory capture, third-party in-process plugins, unrestricted shell execution, continuous vision, payments, or a multi-process distributed architecture. These can be added only after the core contracts demonstrate a need.

## Acceptance Standard

The architecture is considered viable only when a deterministic test can drive:

```text
request -> Agent Brain -> typed tool -> security -> execution
-> verification -> persisted result -> user-visible response
```

The first instance is creating a directory inside a configured temporary sandbox. Real desktop input and LLM calls follow only after this path is reliable.
