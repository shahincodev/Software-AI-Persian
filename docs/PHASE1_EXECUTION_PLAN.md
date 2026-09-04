# Phase 1 Execution Plan

Status: approved architecture; implementation not started

This plan covers only bootstrap, contracts, persistence, and the first safe vertical slice. It does not implement or reserve runtime behavior for identity, experience learning, skills, reflection, plugins, vision, browser automation, or unrestricted shell execution.

## Phase 1 Goal

Prove this complete path with a deterministic local workflow:

```text
request
  -> Agent Brain
  -> typed tool
  -> security decision
  -> sandboxed execution
  -> verification
  -> persisted result
```

The first tool is `filesystem.create_directory@1`. It may create directories only below a configured temporary sandbox root. The verification tool is `filesystem.directory_exists@1`.

## 1. Exact Files and Folders

Create only the following Phase 1 files and folders:

```text
pyproject.toml
README.md
.gitignore
src/
└── software_ai/
    ├── __init__.py
    ├── app.py
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    ├── agent/
    │   ├── __init__.py
    │   └── brain.py
    ├── security/
    │   ├── __init__.py
    │   └── authorizer.py
    ├── tasks/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── manager.py
    │   └── state_machine.py
    ├── tools/
    │   ├── __init__.py
    │   ├── contracts.py
    │   ├── registry.py
    │   ├── dispatcher.py
    │   └── builtin/
    │       ├── __init__.py
    │       └── filesystem.py
    ├── storage/
    │   ├── __init__.py
    │   ├── database.py
    │   ├── migrations.py
    │   └── migrations/
    │       └── 001_initial.sql
    └── verification/
        ├── __init__.py
        └── filesystem.py
tests/
├── conftest.py
├── unit/
│   ├── test_models.py
│   ├── test_state_machine.py
│   ├── test_settings.py
│   ├── test_security.py
│   ├── test_tool_registry.py
│   └── test_migrations.py
└── integration/
    └── test_directory_vertical_slice.py
```

Do not create `identity/`, `memory/`, `skills/`, `reflection/`, `plugins/`, `windows/`, `vision/`, `browser/`, or provider adapter modules in Phase 1. Their future boundaries remain documented in the approved architecture but are not implementation work.

### File Ownership

| File | Responsibility |
| --- | --- |
| `config/settings.py` | Typed configuration, sandbox path validation, runtime data paths |
| `agent/brain.py` | Convert a request into a direct typed tool request for this slice; no OS calls |
| `security/authorizer.py` | Decide whether a typed action is allowed; no execution |
| `tasks/models.py` | Task, action, authorization, result, and event domain models |
| `tasks/state_machine.py` | Legal task transitions and cancellation rules |
| `tasks/manager.py` | Create, transition, persist, and retrieve task state |
| `tools/contracts.py` | Tool protocol, definitions, schemas, and result status values |
| `tools/registry.py` | Register and resolve typed tools |
| `tools/dispatcher.py` | Validate and dispatch an already-authorized tool request |
| `tools/builtin/filesystem.py` | Sandboxed directory creation implementation |
| `storage/database.py` | SQLite connection, pragmas, transaction boundary |
| `storage/migrations.py` | Ordered, idempotent migration runner |
| `verification/filesystem.py` | Independent directory existence verification |
| `app.py` | Compose dependencies and expose one application-service entry point |

## 2. Initial Dependencies

Phase 1 uses the smallest practical dependency set.

### Runtime

No third-party runtime dependency is required for the first slice.

- `dataclasses`, `enum`, `pathlib`, `sqlite3`, `asyncio`, `json`, and `logging` are sufficient for the domain and local execution path.
- Avoiding a runtime validation framework keeps the first contract layer easy to test and reduces bootstrap risk.
- Pydantic and FastAPI remain planned stack components for the API boundary, but are not needed before the first local application service is proven.

### Development

```text
pytest>=8.0
pytest-asyncio>=0.24
ruff>=0.8
pyright>=1.1
```

- `pytest`: deterministic unit and integration tests.
- `pytest-asyncio`: validates async application boundaries and cancellation behavior.
- `ruff`: linting and import/style checks.
- `pyright`: static type checking for the typed contracts.

Pin or lock versions after the first clean Windows installation. Do not add Windows automation, OCR, browser, model SDK, or database-driver dependencies in Phase 1.

## 3. Database Migration Plan

Use one SQLite database for Phase 1, configured under the runtime data root. Tests use a temporary database for every test session or test case as appropriate.

### Connection Rules

- Create parent directories before opening the database.
- Enable foreign keys on every connection.
- Enable WAL mode for the application database.
- Use parameterized SQL only.
- Commit each domain operation transactionally.
- Store JSON payloads only for opaque metadata, not for fields needed in queries.
- Never store secrets or raw environment values.

### Migration Tracking

`schema_migrations` records a migration filename or monotonically increasing version and applied timestamp. The runner:

1. Opens the database.
2. Applies connection pragmas.
3. Creates `schema_migrations` if absent.
4. Reads migrations in lexical order.
5. Applies each unapplied migration in a transaction.
6. Records the version only after successful commit.
7. Fails closed if a migration is missing, duplicated, or partially applied.

### Migration `001_initial.sql`

The initial migration creates:

- `tasks`: task ID, goal, state, created/updated timestamps, cancellation marker, serialized constraints.
- `actions`: action ID, task ID, ordinal, tool ID, input JSON, state, timestamps, authorization state.
- `authorization_requests`: request ID, task/action IDs, risk, decision, scope, reason, timestamp.
- `execution_results`: result ID, task/action IDs, status, error category, retryability, side-effect certainty, output JSON, timestamp.
- `events`: event ID, task/action IDs, event type, safe payload JSON, timestamp, correlation ID.

Foreign keys must use restrictive or cascade behavior deliberately: deleting a task is not part of the first vertical slice, so destructive cleanup is test-only and explicit.

### Migration Tests

- Fresh database reaches the expected schema.
- Running migrations twice is a no-op.
- A failed migration does not record its version.
- Foreign-key violations fail.
- Persisted task, action, authorization, result, and event records can be read after reopening the database.

## 4. Core Domain Models

Use immutable or validation-controlled typed models. Models contain data and invariants; they do not call the OS, model provider, database, or UI.

### Task

```text
Task
  id: str
  goal: str
  state: TaskState
  constraints: dict[str, JSON]
  current_action_id: str | None
  cancellation_requested: bool
  created_at: datetime
  updated_at: datetime
  correlation_id: str
```

Phase 1 states are the minimum required subset: `PENDING`, `READY`, `RUNNING`, `VERIFYING`, `COMPLETED`, `FAILED`, and `CANCELLED`. The full approved state list may be added when those workflows are implemented.

Invariants:

- Goal is non-empty.
- Task ID and correlation ID are stable for its lifetime.
- Terminal tasks cannot transition to running.
- Cancellation cannot be rewritten as failure.

### Action

```text
Action
  id: str
  task_id: str
  tool_id: str
  input: dict[str, JSON]
  ordinal: int
  state: ActionState
  expected_outcome: str
  created_at: datetime
```

An Action is a request to a registered tool, not an implementation object. Inputs are validated against the Tool definition before authorization and dispatch.

### Tool

```text
Tool
  id: str                         # filesystem.create_directory@1
  name: str
  description: str
  input_schema: JSON schema
  output_schema: JSON schema
  risk_level: RiskLevel
  side_effect: bool
  handler: callable               # held by registry, not serialized
```

Tool definitions are versioned and registered explicitly. A tool handler receives a typed request plus cancellation context and returns an Execution Result. It cannot access the Agent Brain or authorize itself.

### Authorization Request

```text
AuthorizationRequest
  id: str
  task_id: str
  action_id: str
  tool_id: str
  target: str
  risk_level: RiskLevel
  requested_scope: AuthorizationScope
  consequence: str
  decision: AuthorizationDecision
  reason: str
  created_at: datetime
```

Phase 1 supports task scope and decisions `ALLOW`, `DENY`, and `REQUIRE_CONFIRMATION`. The sandbox policy allows the first directory tool only when its resolved target remains below the configured sandbox root. Authorization must occur immediately before dispatch.

### Execution Result

```text
ExecutionResult
  id: str
  task_id: str
  action_id: str
  tool_id: str
  status: ExecutionStatus
  output: JSON | None
  error_code: str | None
  error_message: str | None
  retryable: bool
  side_effect_state: SideEffectState
  started_at: datetime
  completed_at: datetime
```

Statuses include `SUCCESS`, `FAILED`, `PERMISSION_DENIED`, `VALIDATION_ERROR`, `CANCELLED`, and `UNKNOWN`. `side_effect_state` distinguishes `NONE`, `CONFIRMED`, and `UNCERTAIN` so a timeout cannot be mistaken for a safe replay.

### Event

```text
Event
  id: str
  task_id: str
  action_id: str | None
  event_type: EventType
  payload: JSON
  correlation_id: str
  occurred_at: datetime
```

Events are append-only operational history. Payloads contain safe summaries and identifiers, not secrets, full file contents, or private reasoning. Initial event types include task created, action authorized, action started, action completed, verification completed, task completed, task failed, and task cancelled.

## 5. Phase 1 Testing Strategy

### Unit Tests

- Model validation, serialization, stable IDs, and terminal-state invariants.
- State-machine legal and illegal transitions.
- Settings path normalization and sandbox containment, including traversal and case variations on Windows.
- Tool registration, duplicate rejection, lookup, input validation, and unknown-tool failure.
- Authorization allow/deny behavior and proof that the authorizer does not execute handlers.
- SQLite migration idempotence and transaction rollback.
- Cancellation prevents dispatch before execution begins.

### Integration Test

`test_directory_vertical_slice.py` uses a temporary sandbox and fake clock/provider where needed:

1. Submit a natural-language request to the application service.
2. Agent Brain creates a typed `filesystem.create_directory@1` action.
3. Tool input is validated.
4. Security authorizes the sandbox target.
5. Dispatcher executes the filesystem handler.
6. Independent verifier confirms the directory exists.
7. Task becomes `COMPLETED`.
8. Task, action, authorization, result, and events remain available after reopening SQLite.

Negative cases:

- Empty or ambiguous path is rejected.
- `..` traversal and symlink/junction escape are rejected or reported as denied.
- Target outside the sandbox is denied without invoking the handler.
- Duplicate tool registration fails.
- Cancellation before execution produces `CANCELLED` and no directory.
- Verification failure produces `FAILED` and never reports success.
- Reopening the database preserves the final state.

### Quality Commands

The Phase 1 project must define and pass:

```powershell
python -m pytest -q
ruff check .
pyright
```

Tests must not require API keys, network access, a real user Desktop, installed applications, or elevated privileges.

## 6. Definition of Done

Phase 1 and the first vertical slice are complete only when all conditions hold:

1. The exact Phase 1 tree is implemented with no deferred subsystem code.
2. A clean supported Windows Python environment installs the declared dependencies.
3. The application service accepts a request and returns a typed task result.
4. The Agent Brain produces a typed tool request and performs no OS operation itself.
5. The tool registry resolves only explicitly registered tools.
6. The security authorizer runs before every dispatch and denies out-of-sandbox targets.
7. Directory creation is restricted to the configured sandbox.
8. Verification independently checks the resulting filesystem state.
9. A failed or uncertain result is never reported as success.
10. Task cancellation prevents new actions and is persisted as `CANCELLED`.
11. Task, action, authorization, result, and event records survive process/database reopen.
12. Migrations are idempotent and transactional.
13. Unit and integration tests cover success, denial, traversal, cancellation, validation, persistence, and verification failure.
14. `pytest`, Ruff, and Pyright pass without network access or secrets.
15. Documentation identifies the slice as implemented and all other architecture extensions as deferred.

Phase 1 ends at this boundary. Real LLM providers, Windows desktop input, UI Automation, screenshots, browser control, memory retrieval, plugins, and learning systems begin only in later approved phases.
