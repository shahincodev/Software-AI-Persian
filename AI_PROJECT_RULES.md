# AI_PROJECT_RULES.md

## Permanent Engineering Principles for Software-AI

**Version**: 1.0  
**Last Updated**: 2026-06-27  
**Status**: Ratified — rarely changed

---

This file contains permanent engineering principles that govern all development on Software-AI.

Unlike `PROJECT_MIGRATION_CONTEXT.md` (which evolves with every Build session), this file represents foundational decisions that should not be revisited without strong justification.

Every contributor — human or AI — must follow these rules.

---

## Rule 1: Preserve the Capability-Driven Architecture

The system must always determine which capabilities to activate based on user intent analysis. The user should never need to specify a mode, flag, or capability set at startup.

**Do not** reintroduce mode flags (`--enable-automation`, `--task-mode`, etc.) or require the user to pre-select functionality.

**Do** route all requests through `IntentRouter` → `RouteType` → `CapabilityManager.activate()`.

---

## Rule 2: Prefer Refactoring over Rewriting

When the architecture has problems, refactor the existing code. Do not propose rewrites from scratch.

Rewriting discards years of bug fixes, edge-case handling, and domain knowledge embedded in the existing code.

Refactoring preserves tested behavior while improving structure.

---

## Rule 3: Prefer Consolidation over Adding New Files

Before creating a new module, verify that the functionality cannot be added to an existing module.

Criteria for a new file:
- The new code has no logical relationship to any existing module AND
- Adding it to an existing module would violate single responsibility AND
- The module would exceed ~1500 lines after addition

If in doubt, add to the most closely related existing module.

---

## Rule 4: Avoid Duplicated Execution Paths

There must be exactly one way to execute an action.

**Do not** bypass `ActionController.process_request()` or route actions through legacy paths.

If you need a new execution behavior, extend the existing pipeline with a strategy or plugin, not a new parallel path.

---

## Rule 5: Avoid Creating God Objects

No single module should hold responsibility for multiple unrelated concerns.

Indicators of a God Object:
- The module imports from many unrelated parts of the system
- The module has many public methods that serve different purposes
- The module's name is generic (e.g., "Manager", "Controller", "System")

If a module exceeds ~1500 lines, extract cohesive subsets into separate methods within the same class first, then into separate classes/modules if justified.

---

## Rule 6: Keep Responsibilities Well Defined

Every module must have a clear, documented responsibility.

- **Parsers** produce data structures. They never access hardware, execute actions, or call system APIs.
- **Executors** perform actions. They never parse natural language or contain regex patterns.
- **Routers** determine execution paths. They never execute actions.
- **Validators** assess plans. They never generate plans.
- **Memory modules** persist data. They never execute actions or analyze intents.

Violating these boundaries is the most common source of architectural drift.

---

## Rule 7: Prefer Composition over Large Conditional Logic

When dispatch logic grows beyond 5-10 branches, use strategy pattern, visitor pattern, or a registry of handlers instead of a `if/elif/else` chain.

Large conditionals:
- Are hard to extend (requires modifying the existing function)
- Are hard to test (all branches must be exercised through one function)
- Often accumulate unrelated concerns

---

## Rule 8: Minimize Coupling

Modules should depend on abstractions, not concrete implementations.

- Use `CapabilityManager.get()` / `CapabilityManager.activate()` instead of importing specific capability classes directly
- Use dependency injection where practical
- A module should import from no more than 3-4 other project modules (exceptions: orchestration modules like `action_controller` and `main.py`)

---

## Rule 9: Maximize Cohesion

The contents of a module should be strongly related. If a module contains code that serves two distinct purposes, split it.

Exception: During active consolidation refactors, temporarily larger modules are acceptable if the long-term plan is to refactor them into cohesive units.

---

## Rule 10: Every Architectural Change Must Have a Clear Technical Justification

All changes must be justified by at least one of:
- Reducing complexity
- Reducing coupling
- Increasing cohesion
- Eliminating duplication
- Improving testability
- Fixing a bug
- Enabling a required feature that cannot be added within the current architecture

"I prefer a different style" is not a valid justification.

---

## Rule 11: Every Major Architectural Decision Should Be Documented as an ADR

Significant decisions must be recorded in `PROJECT_MIGRATION_CONTEXT.md` section 6.

An ADR must include:
- **Decision**: What was decided
- **Context**: What problem was being solved
- **Alternatives considered**: What other options were evaluated
- **Why chosen**: The reasoning behind the selection
- **Consequences**: What trade-offs were accepted

If it is not worth writing an ADR, the decision was probably not significant enough to change the architecture.

---

## Rule 12: Never Increase Complexity without Measurable Benefit

Every abstraction, design pattern, module, or dependency must justify its existence with a concrete benefit:

- Fewer bugs
- Faster development
- Better testability
- Clearer code
- Reduced duplication

If a pattern makes the code harder to understand without providing one of these benefits, remove it.

---

## Rule 13: Maintain Backward Compatibility Pragmatically

Backward compatibility should be preserved when:
- It costs little to maintain (a re-export wrapper, a deprecated parameter)
- Breaking the API provides minimal benefit
- Consumers exist outside the project (unlikely for this project, but possible)

Backward compatibility should be broken when:
- It prevents meaningful architectural improvement
- The compatibility layer perpetuates a bad design
- All consumers have been migrated

**Pattern**: Convert old modules to re-export wrappers with `DeprecationWarning`. Remove them after all consumers have been updated.

---

## Rule 14: Keep the CLI Simple

The command-line interface must remain simple. A single command (`python main.py`) should be sufficient for normal use.

- No mode flags
- No required arguments beyond the user's natural language input
- Advanced options (debug logging, safety thresholds, dry-run) are configuration, not modes

The complexity belongs inside the architecture, not in the user interface.

---

## Rule 15: Integrate Naturally

Every new feature should integrate naturally into the existing architecture instead of creating isolated systems.

- A new capability registers in `CapabilityManager`
- A new route type is added to `RouteType` enum in `intent_router.py`
- A new execution path goes through `ActionController.process_request()`
- A new data store goes through `MemoryIntegrator`

If a feature cannot integrate naturally, the architecture may need refactoring — but first verify the feature is truly incompatible, not just inconvenient.

---

## Appendix: How to Apply These Rules

When starting a new task, ask:

1. Does this change violate any of the 15 rules?
2. If yes, can the change be made differently to comply?
3. If compliance is impossible, which rule should be overridden and why?
4. Does the override justify an ADR?

No rule is absolute, but every exception must be documented and justified.

---

*These rules are the permanent engineering constitution of Software-AI.  
They should be revised rarely and only with full consensus.*
