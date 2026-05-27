# Phase 0 — Policy Instructions Read

- Timestamp: 2026-05-08T13:21:00Z
- Task: P0-T1
- Status: Complete

## Files Read

1. `.github/copilot-instructions.md`
2. `.github/instructions/general-code-change.instructions.md`
3. `.github/instructions/general-unit-test.instructions.md`
4. `.github/instructions/python-code-change.instructions.md`
5. `.github/instructions/python-unit-test.instructions.md`
6. `.github/instructions/self-explanatory-code-commenting.instructions.md`
7. `.github/instructions/python-suppressions.instructions.md`
8. `.github/instructions/tonality.instructions.md`

## Key Constraints Noted

- Black line-length 100; Ruff + Pyright strict mode enforced.
- All new modules must target ≥90% coverage; repo-wide must stay ≥80%.
- No Flet imports allowed in `controller.py`.
- No temp files in tests; all I/O mocked.
- All classes and functions require robust docstrings per self-explanatory-code-commenting policy.
- No file may exceed 500 lines.
- `# type: ignore` and `# noqa` suppressions require pre-authorization or user approval.
