---
paths:
  - "**/*.cs"
  - "**/*.csproj"
description: C#-specific toolchain and coding standards.
---

# C# Code Standards

This rule file summarizes the C#-specific policies for this repository.

## Toolchain

1. **Formatting — CSharpier**: All C# source files must be formatted with CSharpier. Do not use `dotnet format`. Command: `dotnet tool run csharpier .` or `csharpier .`
2. **Linting — .NET Analyzers**: C# code must pass Roslyn/.NET analyzer diagnostics. Command: `msbuild TaskMaster.sln /t:Build /p:Configuration=Debug /p:Platform="Any CPU" /p:EnableNETAnalyzers=true /p:EnforceCodeStyleInBuild=true`
3. **Type Checking — Nullable Analysis**: Enable nullable reference types and fail on warnings. Command: `msbuild TaskMaster.sln /t:Build /p:Configuration=Debug /p:Platform="Any CPU" /p:Nullable=enable /p:TreatWarningsAsErrors=true`
4. **Testing — MSTest + Moq + FluentAssertions**: Run tests with: `vstest.console.exe <test-assembly-paths> /EnableCodeCoverage`

Run the toolchain in order: format → lint → type-check → test. Restart from step 1 if any step fails or changes files.

## Coding Standards

- **Naming**: `PascalCase` for types and public members. `camelCase` for locals and private fields/parameters.
- **Null safety**: Keep nullable reference types enabled. Model optional values with nullable annotations and guard clauses.
- **Composition over inheritance**: Keep classes cohesive and scoped to one responsibility. Favor composition unless polymorphism is a clear requirement.
- **Async/await**: Use `async`/`await` for I/O-bound operations. Prefer `using`/`await using` for disposable resources.
- **Exceptions**: Fail fast with explicit exceptions. Avoid broad `catch (Exception)` unless at a defined boundary with added context.
- **Public surface**: Keep public API surface intentional and minimal. Prefer `internal` for non-public APIs.
- **XML docs**: Public APIs should include XML documentation comments when behavior or contract is non-obvious.

## Testing Standards

- Use **MSTest** (`Microsoft.VisualStudio.TestTools.UnitTesting`) as the test framework.
- Use **Moq** for mocking.
- Prefer **FluentAssertions** for assertions; use MSTest `Assert` only when FluentAssertions is not practical.
- Use `[TestClass]` and `[TestMethod]` attributes.
- Follow Arrange–Act–Assert structure.
- No external dependencies in unit tests.
- Repository-wide line coverage must remain >= 80%.
- Any new module, class, or method must reach >= 90% coverage.
- Coverage regression on changed lines is a blocking finding.

## Deterministic Test Rules

Unit tests must not depend on network, mutable machine PATH or profile state, implicit working-directory assumptions, or external services. Use seam-based mocking for all external boundaries (processes, HTTP, filesystem, clocks). Tests must produce identical results in the IDE test runner and in CLI runs so local and CI behavior agree.

## DI Seams

Introduce the smallest seam that enables reliable unit testing. Apply in this order of preference:

1. **Interface seam (preferred)** — extract boundary calls into narrow purpose-specific interfaces (for example, `IProcessRunner`, `IFileSystem`, `IClock`). Keep interfaces minimal.
2. **Injectable delegate seam** — use a narrow `Func<>`/`Action<>` delegate for a single call path when a full interface is excessive. Default behavior must remain safe and deterministic.
3. **Adapter seam for static or third-party APIs** — wrap the static or third-party call behind a small adapter so tests can mock the adapter with Moq.

## Prohibited Behaviors

- Broad refactors across unrelated projects or files.
- Introducing heavy generic abstraction frameworks without need.
- Creating analyzer debt and deferring cleanup.
- Weakening assertions or relaxing test expectations to make tests pass.
- Adding sleeps, retries, or timing hacks to mask flaky behavior.
- Reporting success without running the required toolchain.
