# AGENTS.md

# Software-AI Development Constitution

## 1. Project Identity

Software-AI is a Windows-first, local-first AI Agent platform.

The goal is NOT to build a chatbot.

The goal is to build a reliable AI Agent runtime capable of:

- understanding user goals
- planning tasks when required
- selecting appropriate tools
- executing controlled actions
- verifying outcomes
- recovering from failures

The project prioritizes:

1. Correctness
2. Security
3. Maintainability
4. Testability
5. Extensibility

Feature quantity is not a success metric.

A small reliable system is better than a large unstable system.


---

# 2. Architecture Principles

Software-AI follows a modular monolith architecture.

The system must maintain clear boundaries between:

- Agent Brain
- Task Management
- Planning
- Security Authorization
- Tool Execution
- Verification
- Persistence
- User Interface

Do not introduce unnecessary distributed systems.

Do not introduce microservices unless explicitly approved.

Avoid premature architectural complexity.


---

# 3. Core Agent Rules

The Agent Brain is responsible for:

- understanding user intent
- selecting strategies
- creating plans when required
- deciding required capabilities


The Agent Brain MUST NOT:

- directly execute system operations
- directly access filesystem APIs
- directly control Windows
- bypass security
- grant permissions
- execute tools without authorization


The required execution flow:

User Request

↓

Agent Brain

↓

Task / Action

↓

Security Authorization

↓

Tool Execution

↓

Verification

↓

Persistence

↓

User Response


---

# 4. Tool System Rules

Tools represent deterministic capabilities.

Every tool must have:

- clear contract
- defined inputs
- defined outputs
- predictable behavior
- structured results
- verification strategy


Tools MUST NOT:

- decide authorization
- interpret user intent
- modify security policies
- bypass Agent Brain
- access unrestricted resources


New capabilities must be implemented as tools.

Do not add special-case logic inside Agent Brain.


Bad:

if user_wants_excel:
    open_excel()


Good:

Excel Tool

with defined contract


---

# 5. Security Rules

Security is a first-class system boundary.

Every side effect requires authorization.

Examples:

- filesystem changes
- deletion
- installation
- external communication
- system modification
- command execution


Important rules:

Memory does NOT grant permission.

Experience does NOT grant permission.

Successful history does NOT grant permission.

Only explicit authorization policies can allow actions.


Dangerous operations must fail closed.


---

# 6. Memory and Learning Rules

Memory provides context.

Memory does NOT provide authority.


Never implement:

Memory → Permission


or:


Past Success → Automatic Trust


Future systems such as:

- Experience Memory
- Reflection Loop
- Skill Evolution

must remain separated from security decisions.


---

# 7. Future Architecture Boundaries

The architecture is designed to support:

- Agent Identity Model
- Experience Memory
- Skill System
- Reflection Loop
- Plugin Architecture


However:

Do not implement these systems unless explicitly requested.

Do not create placeholder complexity.

Future capabilities must integrate through existing contracts.


---

# 8. MVP Development Rules

The MVP goal is reliability.

The first success criteria:

request

↓

Agent Brain

↓

typed tool request

↓

security authorization

↓

execution

↓

verification

↓

persisted result


A simple working system is preferred over an incomplete advanced system.


---

# 9. Phase Restrictions

Unless explicitly requested, do not implement:

- LLM providers
- OpenAI integration
- Gemini integration
- React UI
- FastAPI layer
- Browser automation
- Vision systems
- OCR
- Plugins
- Skill loader
- Experience learning
- Reflection engine
- Vector databases
- Knowledge graphs
- Autonomous memory capture


Focus on the approved development phase only.

Do not expand scope without approval.


---

# 10. Documentation Synchronization Rules

Documentation is part of the implementation.

A code change is not complete until documentation impact has been evaluated.


For every meaningful change, check whether these documents require updates:

- README.md
- Architecture documentation
- Security documentation
- API documentation
- Tool contracts
- Database documentation
- Development guides
- Roadmap documents


Examples:


## Adding a new module

Evaluate:

- Architecture documentation
- Module documentation
- README structure


## Changing security behavior

Update:

- Security model
- Threat documentation
- Related tests


## Changing database models

Update:

- Migration documentation
- Data model documentation


Documentation must evolve together with the codebase.


---

# 11. Code Quality Rules

Always:

- write maintainable code
- keep modules focused
- add tests for new behavior
- document important decisions
- use clear naming
- preserve architecture boundaries


Avoid:

- unnecessary abstractions
- duplicate logic
- hidden side effects
- unused dependencies
- premature optimization


---

# 12. Testing Requirements

Every meaningful change requires appropriate tests.


Before completing a change:

Run:

- unit tests
- integration tests when applicable
- linting
- type checking


Broken tests block completion.

Do not ignore failing tests.


---

# 13. Git and GitHub Workflow

## Branch Rules

Do not work directly on main.

Use meaningful branches.


Examples:

feature/task-state-machine

feature/tool-registry

fix/security-validation

docs/architecture-update


---

# 14. Commit Standards

Use Conventional Commits.


Format:

type(scope): description


Examples:

feat(tasks): add task lifecycle model

fix(security): prevent unsafe paths

docs(architecture): update tool contract

test(tasks): add task transition tests


Allowed types:

- feat
- fix
- docs
- test
- refactor
- perf
- build
- ci
- chore


Avoid vague commits:

update code

changes

fix stuff


---

# 15. Pre-Commit Checklist

Before creating a commit:


1. Check repository status.

2. Review changed files.

3. Review git diff.

4. Run tests.

5. Run linting.

6. Run type checking.

7. Verify documentation updates.

8. Verify no secrets are included.


---

# 16. Pre-Push Checklist

Before pushing:


Verify:

- current branch is correct
- tests pass
- documentation is synchronized
- no secrets exist
- migrations are valid
- architecture changes have documentation


Never push:

- API keys
- passwords
- tokens
- private credentials
- .env files


---

# 17. Architecture Change Rules

Changes affecting:

- architecture
- security model
- database schema
- core contracts
- execution flow

require an Architecture Decision Record (ADR).


ADR format:

Decision:

Context:

Alternatives:

Consequences:


Example:

docs/adr/0001-tool-registry-design.md


Do not silently change architecture.


---

# 18. Legacy Repository Rules

Previous Software-AI implementations are research material only.

Do not copy old architecture blindly.


Reuse only:

- validated ideas
- useful experiments
- lessons learned


Avoid repeating previous mistakes:

- building features before foundations
- excessive abstraction
- uncontrolled scope expansion
- mixing UI, Agent logic, and execution


---

# 19. Implementation Communication Rules

Before major changes explain:


1. What problem is being solved?

2. Which files will change?

3. Why this design?

4. What risks exist?

5. What documentation changes are required?


If a conflict with architecture appears:

Stop and explain before implementation.

Do not make hidden architectural decisions.


---

# 20. Quality Standard

Software-AI should be developed as a production-grade system.


The standard is:

- clean architecture
- explicit boundaries
- secure execution
- documented decisions
- tested behavior
- controlled evolution


Build slowly.

Build correctly.

Build for the long term.

---

# 21. Multi-Language Documentation Synchronization

Software-AI maintains documentation in multiple languages.

The following files must remain synchronized:

- README.md
- README_FA.md


## Primary Documentation Rule

README.md is the primary public documentation source.

Any meaningful change made to README.md must be reflected in README_FA.md.


Examples:

Changes requiring synchronization:

- Project description updates
- Vision changes
- Architecture overview changes
- Roadmap changes
- Feature status changes
- Installation instructions
- Development instructions
- Contribution guidelines


---

## Translation Rules

When updating README_FA.md:

- Preserve the original meaning of README.md.
- Do not remove technical information.
- Do not add unsupported claims.
- Keep technical terms consistent with the English version.


---

## Completion Requirement

A README.md change is not considered complete until:

1. README.md is updated.
2. README_FA.md is reviewed and updated if required.
3. Both documents describe the same project state.


---

## Forbidden Behavior

Never:

- update README.md without checking README_FA.md
- update README_FA.md with information that does not exist in README.md
- allow documentation versions to describe different project states
