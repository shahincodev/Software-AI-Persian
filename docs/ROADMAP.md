# Implementation Roadmap

Status: approved baseline; extension review complete; implementation has not started.

Each phase ends with a working, testable increment. The team should implement vertical slices and avoid building broad infrastructure without an exercising workflow.

## Phase 1: Bootstrap and Contracts

**Objective:** Create an installable Python package with stable domain contracts.

**Dependencies:** None.

**Deliverables:** `pyproject.toml`, `src/` package, settings loader, structured logging, correlation IDs, tool/action/result models, task models, SQLite migration runner, pytest configuration, lint/type-check configuration.

**Tests:** Settings validation, migration creation, task state transition rules, tool result serialization, cancellation token behavior.

**Risks:** Choosing libraries that cannot be installed consistently on Windows.

**Exit criteria:** Clean environment installation succeeds and deterministic unit tests run without API keys or desktop access.

## Phase 2: First Vertical Slice

**Objective:** Prove the complete safe execution path.

**Dependencies:** Phase 1.

**Deliverables:** Agent Brain direct-action path, filesystem tool registry, `filesystem.create_directory@1`, `filesystem.directory_exists@1`, task manager, security authorizer, persisted task/action events, local application service.

**Tests:** A request creates a directory only inside a temporary configured sandbox, is authorized, executes, verifies existence, persists the result, and returns a user-safe response. Test path traversal, cancellation, duplicate request, and permission denial.

**Risks:** Accidental access outside the sandbox; bypassing authorization through a direct handler.

**Exit criteria:** The slice works with a fake model and no LLM dependency. No tool can execute without authorization.

## Phase 3: Conversation and Provider Abstraction

**Objective:** Add lightweight chat and model-backed structured decisions.

**Dependencies:** Phase 2.

**Deliverables:** Async provider protocol, provider registry, OpenAI-compatible adapter, Google adapter if required, capability discovery, structured-output parser, fallback policy, response streaming contract.

**Tests:** Fake provider tests, malformed output, unsupported capability, timeout, authentication failure, fallback, context-limit handling.

**Risks:** `opencode.json` points at a Tooken OpenAI-compatible endpoint, but tool calling, structured outputs, streaming, multimodal input, context limits, and reasoning behavior remain unverified.

**Exit criteria:** Provider behavior is selected from tested capabilities rather than assumed API compatibility.

## Phase 4: Adaptive Tasks and Planning

**Objective:** Support direct actions, short workflows, and complex persisted tasks.

**Dependencies:** Phases 1-3.

**Deliverables:** Complexity router, planner/executor separation, dependency-aware plan steps, progress events, `WAITING_FOR_USER`, resume/retry commands.

**Tests:** Direct action avoids heavy planning; short workflow verifies important steps; complex task persists and resumes; cancellation prevents new actions; partial completion is reported correctly.

**Risks:** Planning overhead, invalid model plans, and state drift.

**Exit criteria:** Plans are validated before execution and can be replanned after observation changes.

## Phase 5: Security Hardening

**Objective:** Enforce authorization as an independent authority.

**Dependencies:** Tool contracts and task manager.

**Deliverables:** Risk policy, task/session/persistent scopes, grouped confirmation requests, audit repository, emergency stop, fail-closed critical policy.

**Tests:** Dangerous tools cannot bypass policy through the Agent Brain, plugins, memory, tool output, API, or UI. Emergency stop blocks new actions and interrupts cancellable active actions.

**Risks:** Unsafe defaults and confirmation fatigue.

**Exit criteria:** Security decisions are deterministic, auditable, and covered by negative tests.

## Phase 6: Windows Core Tools

**Objective:** Add reliable filesystem, process, application, clipboard, and keyboard capabilities.

**Dependencies:** Phase 5.

**Deliverables:** Windows adapters, active-window checks, application discovery, process inspection, clipboard-safe Unicode input, cancellation-aware handlers.

**Tests:** Temporary filesystem operations, Notepad launch/detection, Persian clipboard round trip, process policy, cleanup after failures.

**Risks:** Real desktop input can affect the user’s active session; privilege and UAC boundaries vary.

**Exit criteria:** Controlled Windows integration tests pass and no test requires an uncontrolled user desktop.

## Phase 7: Perception and Computer Use

**Objective:** Add semantic UI interaction and bounded visual fallback.

**Dependencies:** Phase 6.

**Deliverables:** UI Automation provider, screenshot capture, OCR adapter, observation model, DPI/multi-monitor coordinate mapping, strategy selector, confidence handling.

**Tests:** UIA discovery, OCR fixture recognition, active-window validation, coordinate transforms, low-confidence re-observation, popup/scroll handling.

**Risks:** Application-specific accessibility behavior, DPI virtualization, permissions, and OCR uncertainty.

**Exit criteria:** One unknown-app workflow completes with observe-act-verify behavior and bounded actions.

## Phase 8: Recovery and Reliability

**Objective:** Recover safely from ordinary failures.

**Dependencies:** Phases 4-7.

**Deliverables:** Error taxonomy, bounded retry/backoff, alternative strategies, replanning, watchdog, integration circuit breaker, crash recovery checks.

**Tests:** Timeout after side effect, uncertain external result, missing target, permanent permission error, partial workflow, restart/resume, repeated integration failure.

**Risks:** Duplicate side effects and infinite recovery loops.

**Exit criteria:** Recovery is observable, bounded, and never blindly repeats uncertain side effects.

## Phase 9: Sessions and Memory

**Objective:** Add useful persistence without storing everything automatically.

**Dependencies:** Phase 1 and stable task models.

**Deliverables:** Conversation/session repository, working/task memory, explicit long-term memory, relevance-filtered Context Manager, forget operations, migrations.

**Tests:** Retrieval, explicit remember, forget one item, forget project scope, migration, access metadata, no authority changes from memory.

**Risks:** Sensitive data retention and irrelevant context injection.

**Exit criteria:** Context selection is explainable at a high level, scoped, and independent of authorization.

## Phase 10: User Interface

**Objective:** Provide natural chat and operational control.

**Dependencies:** API events, task manager, security model.

**Deliverables:** React/TypeScript client, chat, task progress, grouped confirmation, cancellation, retry, resume, intervention, safe error display.

**Tests:** API contracts, event ordering, confirmation/cancellation flows, reconnect behavior, responsive layouts.

**Risks:** UI showing private reasoning or implying success before verification.

**Exit criteria:** The first vertical slice is usable from the UI without direct tool access.

## Phase 11: Plugins and First Integration

**Objective:** Add modular external capabilities.

**Dependencies:** Stable tool contracts and security.

**Deliverables:** Manifest validation, scoped configuration, first-party plugin loader, one integration, authentication isolation, failure circuit breaker.

**Tests:** Registration/removal, schema validation, permission isolation, authentication failure, plugin timeout, tool audit.

**Risks:** Third-party code access and credentials.

**Exit criteria:** Adding/removing an integration does not modify the Agent Brain or security core.

## Phase 12: Packaging and Release

**Objective:** Produce a reproducible Windows distribution.

**Dependencies:** Stable core, UI, and integration tests.

**Deliverables:** Installer, secret-store integration, data migration, diagnostics bundle, signed build, update and rollback policy.

**Tests:** Clean-machine install, upgrade, rollback, uninstall, task/database migration, no-secret logging.

**Exit criteria:** A release can be installed and operated on a supported Windows environment with documented limitations.

## Future Phase 13: Agent Identity and Capability Grants

**Objective:** Support explicit ownership, agent profiles, and scoped capability grants.

**Dependencies:** Phases 5, 9, and stable plugin contracts.

**Deliverables:** Agent identity model, owner/workspace association, capability catalog, scoped grants, revocation, identity audit events, migration policy.

**Tests:** Grant scope, revocation, owner separation, plugin scope, persistence, and proof that identity or capability metadata cannot bypass per-action authorization.

**Exit criteria:** Every requested capability has an identifiable owner, scope, and revocation path.

## Future Phase 14: Experience Memory and Learning

**Objective:** Use prior task outcomes as bounded planning evidence.

**Dependencies:** Phases 4, 8, and 9.

**Deliverables:** Experience records, provenance/confidence, success and failure strategy metadata, retrieval through Context Manager, controlled learning writer, retention and deletion policy.

**Tests:** Successful strategy ranking, failed strategy suppression, stale-context rejection, privacy deletion, and proof that experience data cannot alter security decisions.

**Exit criteria:** Experience improves candidate planning while current observation and authorization remain mandatory.

## Future Phase 15: Skill System

**Objective:** Make validated multi-tool workflows reusable.

**Dependencies:** Stable tool contracts, task plans, security, and experience metadata.

**Deliverables:** Skill manifest/schema, validator, registry, bounded composition, dry-run support, versioning, provenance, revocation, and UI/API management.

**Tests:** Schema and dependency validation, forbidden tool combinations, bounds, rollback/cancellation, authorization of every expanded tool call, and plugin isolation.

**Exit criteria:** A skill can be installed, validated, revoked, and executed only through the normal task and security paths.

## Future Phase 16: Reflection and Improvement Signals

**Objective:** Evaluate outcomes and produce controlled learning signals.

**Dependencies:** Phases 8, 9, 14, and stable user feedback events.

**Deliverables:** Bounded post-task evaluator, structured reflection signals, feedback capture, confidence updates, retention controls, and optional skill-candidate reports.

**Tests:** Reflection after every terminal task state, no changes to immutable audit/task results, negative feedback lowering confidence, bounded evaluator cost, and no private reasoning exposure.

**Exit criteria:** Reflection can improve future planning evidence without changing security, capability grants, or historical truth.

## Phase 1 Readiness Checklist

Before writing implementation code, confirm:

1. Python version and Windows support policy are recorded.
2. `pyproject.toml` dependency set is minimal and installable on Windows.
3. Runtime data root and temporary sandbox root are explicitly configurable.
4. SQLite migration ownership and backup policy are defined.
5. Tool, action, result, task, authorization, and event contracts are agreed.
6. The first tool is sandboxed directory creation; unrestricted shell is excluded.
7. Fake provider and fake clock/cancellation seams are planned for deterministic tests.
8. CI will run formatting/lint/type checks and unit tests without API keys or desktop control.
9. The extension boundaries in `ARCHITECTURE.md` are recorded as deferred, not MVP work.
10. No historical implementation or simulator code is restored as part of bootstrap.

Phase 1 begins only after this checklist is satisfied. Its first coding task is package bootstrap and domain contracts, followed by the sandboxed directory vertical slice.

## First Implementation Order

The first coding sequence is deliberately narrow:

1. Bootstrap package and contracts.
2. Implement sandboxed directory creation and existence verification.
3. Add authorization and audit enforcement to that path.
4. Persist task/action state and return a local application result.
5. Add deterministic tests, including cancellation and traversal rejection.
6. Only then connect a real provider or Windows desktop side effects.
