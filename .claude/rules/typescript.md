---
paths:
  - "**/*.ts"
description: TypeScript-specific toolchain and coding standards.
---

# TypeScript Code Standards

This rule file summarizes the TypeScript-specific policies for this repository.

## Toolchain

1. **Formatting — Prettier**: All TypeScript must be formatted with the repository Prettier configuration. Command: `npm run format`
2. **Linting — ESLint**: TypeScript must pass ESLint using the repository configuration. Command: `npm run lint`
3. **Type Checking — TSC**: TypeScript must pass the compiler type-check. Avoid `any`; prefer `unknown` plus narrowing. Command: `npm run typecheck`
4. **Testing — Jest**: All TypeScript unit tests must use Jest. Command: `npm run test:unit`

Run the toolchain in order: format → lint → type-check → test. Restart from step 1 if any step fails or changes files.

## Coding Standards

- New user-invocable workflows belong under `.claude/skills/` rather than `.claude/commands/`.
- **Strong typing**: Public functions, methods, and exported APIs must have clear, intentional types. Avoid type assertions (`as X`) unless justified.
- **ES modules**: Use ES module syntax. Do not introduce CommonJS patterns (`require`, `module.exports`).
- **Domain types**: Model domain concepts with interfaces/types that encode invariants. Prefer discriminated unions for state machines.
- **Naming**: `PascalCase` for classes, interfaces, enums, and type aliases. `camelCase` for functions, methods, variables, and object properties. No `I` prefix on interfaces.
- **File naming**: Prefer kebab-case filenames (e.g., `user-session.ts`, `task-runner.ts`).
- **Separation of concerns**: Keep pure logic separate from VS Code extension APIs, filesystem/network I/O, and UI wiring.
- **Error handling**: Fail fast with clear errors. Avoid catch-all `catch (e)` without rethrowing or adding context.
- **Dependencies**: Do not add new runtime dependencies unless explicitly approved.

## Testing Standards

- Use **Jest** as the test framework.
- Name test files `*.test.ts`.
- Unit tests must not require the VS Code extension host.
- Follow Arrange–Act–Assert structure.
- Each test targets one behavior.
- Use `jest.spyOn` or `jest.mock` for targeted mocking; reset mocks with `afterEach(() => { jest.resetAllMocks(); })`.
- No external dependencies (network, filesystem temp files, external processes) in unit tests.
- Avoid snapshot tests unless stable and intentional.
- Repository-wide line coverage must remain >= 80%.
- Any new module, class, or method must reach >= 90% coverage.
- Coverage command: `npm run test:unit:coverage`
- Coverage regression on changed lines is a blocking finding.
