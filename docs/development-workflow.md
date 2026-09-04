# Software-AI Development Workflow

## Purpose

This document defines the standard development process for Software-AI.

The goal is to ensure that every change is:

- planned
- documented
- tested
- reviewable
- maintainable

Code changes without proper validation and documentation are incomplete.

---

# 1. General Development Principles

Every development task must follow:

Understand → Plan → Implement → Test → Document → Review


Do not start coding immediately for unclear requirements.

Complex changes require design discussion before implementation.

---

# 2. Task Classification

Every requested change must first be classified.


## Type A: Small Change

Examples:

- bug fix
- documentation correction
- small refactor

May proceed directly if no architecture impact exists.


---

## Type B: Feature Change

Examples:

- new tool
- new module
- new workflow

Requires:

- implementation plan
- tests
- documentation review


---

## Type C: Architecture Change

Examples:

- changing Agent Brain behavior
- modifying security model
- changing database contracts
- changing execution flow

Requires:

- architecture review
- ADR document
- approval before implementation


---

# 3. Before Implementation

Before writing code:

The developer/Agent must identify:

## Problem

What problem are we solving?


## Scope

What is included?

What is explicitly not included?


## Impact

Which components are affected?


## Documentation Impact

Which documents need updates?


## Testing Strategy

How will correctness be verified?


---

# 4. Implementation Process

Implementation should follow:


## Step 1: Update Design If Required

If the change affects architecture:

Update relevant documentation first.


Examples:

- architecture.md
- security-model.md
- ADR


---

## Step 2: Implement Small Changes

Avoid large uncontrolled changes.

Prefer:

small commits

small modules

small reviews


---

## Step 3: Maintain Boundaries

During implementation:


Agent Brain:

Decision only.


Tools:

Execution only.


Security:

Authorization only.


Verification:

Validation only.


Persistence:

State storage only.


---

# 5. Testing Process

Every change must include appropriate testing.


Minimum requirements:

## Unit Tests

For:

- models
- business rules
- validation logic


## Integration Tests

For:

- component interaction
- execution flow
- persistence


## Regression Tests

For:

previously fixed problems.


---

# 6. Documentation Synchronization

Documentation must be updated together with code.


A change is incomplete if:

- code changed
- but architecture documentation is outdated


Examples:


New Tool:

Update:

- Tool documentation
- Contracts
- README if user-facing


Database Change:

Update:

- Schema documentation
- Migration notes


Security Change:

Update:

- Security model
- Threat documentation


---

# 7. Code Review Checklist

Before accepting a change:

Review:


## Architecture

- Does this follow existing boundaries?


## Security

- Can this create unsafe behavior?


## Testing

- Are tests included?


## Documentation

- Is knowledge synchronized?


## Maintainability

- Is the design simple?


---

# 8. Git Workflow

Every change should follow:


Create branch:

feature/name

or

fix/name


Implement:

↓

Test:

↓

Review:

↓

Commit:

↓

Push:


---

# 9. Commit Requirements

Every commit should:

- represent one logical change
- have meaningful message
- pass tests


Use Conventional Commits.


Examples:

feat(tools): add filesystem tool

fix(security): block unsafe path access

docs(architecture): update execution flow


---

# 10. Pull Request Standard

Important changes should include:


## Title

Clear summary.


## Description

Include:

- What changed?
- Why?
- How was it tested?
- Documentation updated?
- Risks?


---

# 11. Emergency Changes

For urgent fixes:

The process may be shortened.

However:

- tests are still required
- documentation must be updated afterward
- architecture impact must be reviewed


---

# 12. Completion Definition

A task is complete only when:


✓ Code implemented

✓ Tests passing

✓ Documentation synchronized

✓ Git history clean

✓ Architecture boundaries preserved


---

# 13. Software-AI Philosophy

The project values:

Reliable systems over fast demos.

Clear architecture over quick hacks.

Understanding over complexity.

Small verified steps over uncontrolled growth.
