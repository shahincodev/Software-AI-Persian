# Repository Structure

This is the target repository layout for the rebuild. It is intentionally a modular monolith. A new package or abstraction requires a concrete ownership or testability benefit.

```text
software-ai/
├── pyproject.toml
├── README.md
├── ARCHITECTURE.md
├── docs/
│   ├── REPOSITORY_STRUCTURE.md
│   ├── ROADMAP.md
│   ├── SECURITY_MODEL.md
│   ├── TOOL_CONTRACT.md
│   ├── COMPUTER_USE.md
│   ├── MEMORY_MODEL.md
│   ├── PLUGIN_DEVELOPMENT.md
│   ├── PROVIDER_COMPATIBILITY.md
│   ├── CONFIGURATION.md
│   └── TESTING.md
├── src/software_ai/
│   ├── app.py
│   ├── api/
│   │   ├── http.py
│   │   └── events.py
│   ├── agent/
│   │   ├── brain.py
│   │   ├── router.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── verifier.py
│   │   └── recovery.py
│   ├── config/
│   │   ├── settings.py
│   │   └── secrets.py
│   ├── context/
│   │   ├── manager.py
│   │   └── models.py
│   ├── identity/
│   │   ├── models.py
│   │   └── capabilities.py
│   ├── memory/
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── experiences.py
│   │   ├── learning.py
│   │   └── migrations/
│   ├── skills/
│   │   ├── models.py
│   │   ├── validator.py
│   │   └── registry.py
│   ├── reflection/
│   │   ├── evaluator.py
│   │   └── signals.py
│   ├── plugins/
│   │   ├── loader.py
│   │   ├── manifest.py
│   │   └── permissions.py
│   ├── providers/
│   │   ├── protocol.py
│   │   ├── registry.py
│   │   └── adapters/
│   ├── security/
│   │   ├── policy.py
│   │   ├── authorizer.py
│   │   ├── confirmation.py
│   │   └── audit.py
│   ├── tasks/
│   │   ├── models.py
│   │   ├── manager.py
│   │   ├── state_machine.py
│   │   └── cancellation.py
│   ├── tools/
│   │   ├── contracts.py
│   │   ├── registry.py
│   │   ├── dispatcher.py
│   │   └── builtin/
│   └── windows/
│       ├── filesystem.py
│       ├── processes.py
│       ├── windows.py
│       ├── uia.py
│       ├── input.py
│       ├── display.py
│       └── perception.py
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   ├── windows/
│   └── fixtures/
└── ui/
    ├── package.json
    └── src/
```

## Dependency Rules

- `config`, domain models, and contracts have no dependency on API, UI, or concrete providers.
- `tools` may depend on Windows adapters, storage interfaces, and cancellation, but never on the Agent Brain.
- `security` may inspect typed action requests and policy state; it never calls the model.
- `agent` may coordinate all interfaces but must not contain Windows API details.
- `memory` is accessed through the Context Manager by the agent; tools cannot use it to authorize themselves.
- `identity` describes ownership and capability grants; `security` remains the authority for individual actions.
- `memory.experiences` and `reflection` may influence planning evidence but cannot modify authorization or audit history.
- `skills` compose tools but cannot execute around the dispatcher or grant themselves capabilities.
- `plugins` register tools through the same registry and authorizer as built-ins.
- `api` translates transport messages to application commands and events; it contains no execution policy.
- `ui` communicates only through the API/event contract.

## Data Areas

Runtime data is kept outside source code and separated into configuration, database, task artifacts, audit logs, and temporary screenshots. Sensitive values are references to the secret store, never plaintext database fields or logs.

## Naming and Interface Rules

- Public interfaces use typed dataclasses or Pydantic models.
- Tool IDs are versionable, for example `filesystem.create_directory@1`.
- Tool results always contain status, error category, retryability, side-effect certainty, and correlation identifiers.
- Modules do not expose mutable global registries except through an owned application container.
- Compatibility wrappers are not part of the rebuild unless an external consumer is identified.

The `identity`, `experiences`, `skills`, and `reflection` directories are future reserved boundaries. They are not Phase 1 deliverables and should not be created in the implementation until their phase begins.
