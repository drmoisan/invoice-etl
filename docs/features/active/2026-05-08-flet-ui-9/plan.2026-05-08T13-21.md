# 2026-05-08-flet-ui - Plan

- **Issue:** #9
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-05-08T13-21
- **Status:** Complete
- **Version:** 0.1
- **Work Mode:** minor-audit

## Required References

- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Code Change: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)
- Self-Explanatory Commenting: [`.github/instructions/self-explanatory-code-commenting.instructions.md`](../../../../.github/instructions/self-explanatory-code-commenting.instructions.md)

**Requirements source: `docs/features/active/2026-05-08-flet-ui-9/issue.md` (AC section only). No spec.md or user-story.md.**

## Implementation Plan (Atomic Tasks)

### Phase 0 — Baseline Capture

- [x] [P0-T1] Read and confirm all required policy files (`general-code-change.instructions.md`, `python-code-change.instructions.md`, `general-unit-test.instructions.md`, `python-unit-test.instructions.md`, `self-explanatory-code-commenting.instructions.md`) before any code changes.
  - Acceptance: Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/baseline/phase0-instructions-read.md` created with timestamp and file list.
- [x] [P0-T2] Capture baseline branch state.
  - Command: `git branch --show-current`
  - Acceptance: Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/baseline/baseline-branch.md` created.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`
- [x] [P0-T3] Capture baseline Black formatting state.
  - Command: `poetry run black . --check`
  - Acceptance: Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/baseline/baseline-black.md` created.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`
- [x] [P0-T4] Capture baseline Ruff lint state.
  - Command: `poetry run ruff check`
  - Acceptance: Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/baseline/baseline-ruff.md` created.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`
- [x] [P0-T5] Capture baseline Pyright type-check state.
  - Command: `poetry run pyright`
  - Acceptance: Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/baseline/baseline-pyright.md` created.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`
- [x] [P0-T6] Capture baseline test and coverage state.
  - Command: `poetry run pytest --cov=invoice_etl --cov-report=term-missing`
  - Acceptance: Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/baseline/baseline-pytest.md` created with numeric coverage values.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:` (include overall coverage %, pass count)

### Phase 1 — Implementation

- [x] [P1-T1] Add `flet = ">=0.24"` to `[tool.poetry.dependencies]` in `pyproject.toml` and run `poetry lock --no-update && poetry install`.
  - Acceptance: `pyproject.toml` contains the flet dependency entry; `poetry.lock` updated; venv has flet installed.
- [x] [P1-T2] Create `src/invoice_etl/ui/` sub-package with `__init__.py` (empty or re-exports only).
  - Acceptance: File `src/invoice_etl/ui/__init__.py` exists.
- [x] [P1-T3] Implement `src/invoice_etl/ui/controller.py` containing the `UIController` class with zero Flet imports.
  - `UIController` must have: `set_input_file(path: Path) -> None`, `set_output_mode(mode: OutputMode) -> None`, `run_export(output_path: Path | None = None) -> str` methods.
  - `run_export` returns a descriptive status string (success message, cancelled message, or error message).
  - `OutputMode` alias imported from `invoice_etl.main`.
  - Acceptance: File exists, Pyright strict reports no errors on it, zero Flet imports.
- [x] [P1-T4] Implement `src/invoice_etl/ui/app.py` as the thin Flet wiring layer.
  - Wires `ft.FilePicker` (pick_files for input, save_file for Excel output), `ft.RadioGroup` (mode toggle), `ft.ElevatedButton` (Export), and a `ft.Text` status area to `UIController` methods.
  - Exposes a `main(page: ft.Page) -> None` function and a `run_app() -> None` entry point.
  - Acceptance: File exists; Pyright strict reports no errors; file is excluded from coverage.
- [x] [P1-T5] Create `tests/test_ui_controller.py` with full pytest coverage of `UIController`.
  - Must cover: AC3 (Excel mode positive), AC4 (Excel mode cancel), AC5 (DB mode positive), AC6 (no input file), AC7 (ETL failure propagated as string).
  - Uses `unittest.mock.patch` or `MagicMock` — no real files, no real DB, no real PDF parsing.
  - Acceptance: All tests pass; ≥90% line coverage on `src/invoice_etl/ui/controller.py`.
- [x] [P1-T6] Update `pyproject.toml` `[tool.coverage.run]` omit list to exclude `src/invoice_etl/ui/app.py` from coverage.
  - Acceptance: `pyproject.toml` contains the omit entry for `app.py`.

### Phase 2 — Final QC Loop

- [x] [P2-T1] Run Black formatter on all files.
  - Command: `poetry run black .`
  - Acceptance: Exit code 0; no reformatted files. Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/qa-gates/qa-black.md` created.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`
  - If any file is reformatted, restart QC loop from P2-T1 after applying format.
- [x] [P2-T2] Run Ruff linter.
  - Command: `poetry run ruff check`
  - Acceptance: Exit code 0; zero errors. Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/qa-gates/qa-ruff.md` created.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`
  - If any errors reported, fix and restart loop from P2-T1.
- [x] [P2-T3] Run Pyright type checker.
  - Command: `poetry run pyright`
  - Acceptance: Exit code 0; zero errors. Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/qa-gates/qa-pyright.md` created.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:`
  - If any errors, fix and restart loop from P2-T1.
- [x] [P2-T4] Run pytest with coverage.
  - Command: `poetry run pytest --cov=invoice_etl --cov-report=term-missing`
  - Acceptance: All tests pass; repo-wide coverage ≥80%; `invoice_etl/ui/controller` coverage ≥90%. Evidence artifact `docs/features/active/2026-05-08-flet-ui-9/evidence/qa-gates/qa-pytest.md` created with numeric coverage values.
  - Artifact fields: `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:` (include overall %, controller module %, pass/fail count)
  - If any test fails or coverage drops, fix and restart loop from P2-T1.

## Test Plan

- Unit: `tests/test_ui_controller.py` — all UIController scenarios via mocks.
- Integration: None (Flet view excluded from unit testing by design).
- Manual/CLI: `poetry run python -m invoice_etl.ui.app` or `poetry run flet run src/invoice_etl/ui/app.py` to verify visual wiring.
- Coverage evidence:
  - Baseline: `docs/features/active/2026-05-08-flet-ui-9/evidence/baseline/baseline-pytest.md`
  - Post-change: `docs/features/active/2026-05-08-flet-ui-9/evidence/qa-gates/qa-pytest.md`

## Open Questions / Notes

- `app.py` is excluded from pytest coverage because it requires a live Flet runtime. This is a justified exclusion documented in pyproject.toml.
- `OutputMode` is reused from `invoice_etl.main` — no duplicate type definition.
