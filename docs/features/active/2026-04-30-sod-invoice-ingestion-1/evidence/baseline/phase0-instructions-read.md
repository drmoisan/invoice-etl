# Phase 0 — Policy Instructions Read Evidence

Timestamp: 2026-04-30T11:30:00Z

Policy Order:
1. `.github/copilot-instructions.md` — Read. Stack: Python 3.12+, Poetry, Black, Ruff, Pyright strict, PostgreSQL 16, SQLAlchemy 2.x, Pydantic v2, pytest.
2. `.github/instructions/general-code-change.instructions.md` — Read. Covers design principles, error handling, module structure, naming, toolchain loop (format → lint → type-check → test).
3. `.github/instructions/general-unit-test.instructions.md` — Read. Covers independence, isolation, fast execution, determinism, ≥80% line coverage, Arrange–Act–Assert.
4. `.github/instructions/python-code-change.instructions.md` — Read. Black, Ruff, Pyright strict, full type annotations, no `Any` without justification.
5. `.github/instructions/python-unit-test.instructions.md` — Read. pytest, focused unit tests, mocking sparingly, descriptive `test_...` names.
6. `.github/instructions/python-suppressions.instructions.md` — Read. Pre-authorized `# noqa S603` only; all others require explicit user approval.
7. `.github/instructions/self-explanatory-code-commenting.instructions.md` — Read. Mandatory docstrings on all classes and functions (Google-style), intent-level inline comments for control flow.

All seven files listed above were read successfully prior to any implementation work.
