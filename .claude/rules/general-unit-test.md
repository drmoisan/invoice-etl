---
paths:
  - "**"
description: Cross-language unit test policy. Applies to all files.
---

# General Unit Test Policy

This rule file summarizes the cross-language unit test policy for this repository.

## Core Principles

Every unit test must satisfy all five of these properties:

1. **Independence** — Tests must be able to run in any order without impacting each other.
2. **Isolation** — Each unit test targets a single function, method, or unit of behavior so failures clearly identify the faulty unit.
3. **Fast execution** — Tests must be fast enough to support frequent runs and rapid feedback loops.
4. **Determinism** — Given the same inputs and environment, tests must produce the same results. Avoid flakiness.
5. **Readability and maintainability** — Test names, structure, and assertions must be clear and easy to understand.

## Coverage Requirements

- **Repository-wide line coverage must remain >= 80%.**
- **Any new module, class, or method must target >= 90% coverage.**
- Code changes or refactors must not reduce coverage for the lines that were changed.
- Coverage is a supporting metric, not the sole quality gate. Untested critical behavior is not acceptable even if the overall percentage looks good.
- Configure coverage tooling to exclude test files (e.g., `tests/`) so metrics reflect application code, not tests.

## Scenario Completeness

For each unit or behavior, tests must cover:

- Positive flows with valid inputs
- Negative flows for invalid or missing inputs
- Edge cases and boundary conditions
- Error-handling behavior
- Concurrency behavior when relevant
- State transitions for stateful components

## Test Structure — Arrange–Act–Assert

Organize each test into three sections:

- **Arrange** — set up inputs, environment, and dependencies
- **Act** — execute the behavior under test
- **Assert** — verify outcomes via assertions

Assertions must produce clear, actionable failure messages.

## External Dependencies

- Unit tests must not depend on external services (databases, networks, remote APIs, external processes).
- Use mocks, stubs, or fakes to isolate the unit under test when code interacts with external systems.
- **Creation and use of temporary files in tests is strictly prohibited.**
- Tests must not rely on mutable global state or external configuration that can change between runs.

## Documentation

- Each test must clearly communicate its purpose via a descriptive name and/or a short docstring or comment summarizing the scenario and expected outcome.
- Group related tests logically within the same file or test class.
