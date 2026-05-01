# 2026-04-30-excel-export-loader - Plan

- **Issue:** #6
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-04-30T19-52
- **Status:** Completed
- **Version:** 0.2

## Required References

- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Coding Standards: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)
- Self-Explanatory Code Commenting: [`.github/instructions/self-explanatory-code-commenting.instructions.md`](../../../../.github/instructions/self-explanatory-code-commenting.instructions.md)
- Python Suppressions: [`.github/instructions/python-suppressions.instructions.md`](../../../../.github/instructions/python-suppressions.instructions.md)

**Requirements source: `docs/features/active/2026-04-30-excel-export-loader-6/issue.md` — AC-1 through AC-6 only. No spec.md, user-story.md, or research.md required.**

**All work must comply with these policies; do not duplicate their content here.**

## Overview

Extend the invoice-ETL pipeline with an Excel export option. A new `excel_loader.py` module writes `.xlsx` output (two sheets: `Invoice` and `LineItems`). `main.py` gains an `--output` CLI flag (`db` | `excel`) that routes to the correct loader. The existing DB path must remain fully functional. All toolchain gates (Black → Ruff → Pyright → Pytest ≥ 70% coverage) must pass.

## Implementation Plan (Atomic Tasks)

### Phase 0 — Baseline Capture

- [x] [P0-T1] Read mandatory policy files in order: `general-code-change.instructions.md`, `python-code-change.instructions.md`, `general-unit-test.instructions.md`, `python-unit-test.instructions.md`, `self-explanatory-code-commenting.instructions.md`, `python-suppressions.instructions.md`
  - Acceptance: All six files confirmed read; write evidence artifact `docs/features/active/2026-04-30-excel-export-loader-6/evidence/baseline/phase0-instructions-read.md` containing `Timestamp:`, `Policy Order:` (listing all six files in order), and a confirmation that all files were successfully read.

- [x] [P0-T2] Capture baseline branch and HEAD commit state
  - Command: `git branch --show-current && git log -1 --oneline`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/baseline/baseline-branch.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:` (branch name and HEAD commit hash/message).

- [x] [P0-T3] Run baseline Black format check
  - Command: `poetry run black --check src tests`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/baseline/baseline-black.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:` (pass/fail and any reformatted-file list).

- [x] [P0-T4] Run baseline Ruff lint check
  - Command: `poetry run ruff check src tests`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/baseline/baseline-ruff.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:` (pass/fail and violation count).

- [x] [P0-T5] Run baseline Pyright type check
  - Command: `poetry run pyright`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/baseline/baseline-pyright.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:` (error/warning count and pass/fail status).

- [x] [P0-T6] Run baseline Pytest with coverage
  - Command: `poetry run pytest --cov=invoice_etl --cov-report=term-missing`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/baseline/baseline-pytest.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE:`, `Output Summary:` which MUST include a numeric coverage headline (e.g., `Total: 70%`) and overall pass/fail.

### Phase 1 — Constrained Small-Path Implementation

- [x] [P1-T1] Delegate implementation to `python-typed-engineer` with the following handoff:
  - **Feature folder:** `docs/features/active/2026-04-30-excel-export-loader-6/`
  - **Requirements source:** `docs/features/active/2026-04-30-excel-export-loader-6/issue.md` (AC-1 through AC-6 only)
  - **Plan path:** `docs/features/active/2026-04-30-excel-export-loader-6/plan.2026-04-30T19-52.md`
  - **Implementation scope:**
    - Create `src/invoice_etl/load/excel_loader.py`: fully typed, exports `load_invoice_to_excel(invoice: Invoice, output_path: Path) -> Path`, writes a `.xlsx` file with two sheets — `Invoice` (header fields) and `LineItems` (one row per line item) using `openpyxl`.
    - Update `src/invoice_etl/main.py`: add `--output` CLI flag with choices `db` (default) and `excel`; route to `load_invoice_to_excel` when `excel` is selected and log the written file path; leave the existing `db` path unchanged.
    - Add/update tests in `tests/test_load.py`: cover happy-path write (correct sheet names, column headers, return value) without touching the filesystem (use `unittest.mock` or in-memory verification only — no temporary files).
    - Add/update tests in `tests/test_main.py`: cover `--output excel` and `--output db` flag dispatch, verifying the correct loader is called in each case.
  - **Hard constraints:**
    - No temporary files in tests (policy-mandated).
    - Pyright strict mode enforced; all new code must be fully typed.
    - `openpyxl` must be added to `pyproject.toml` via `poetry add openpyxl`.
    - Do not break existing DB loader behaviour or any existing tests.
    - Black → Ruff → Pyright → Pytest (coverage ≥ 70%) must all pass with EXIT_CODE 0.
  - **Acceptance:** Implementation report confirms AC-1, AC-2, AC-3, AC-4, AC-5, and AC-6 all delivered; implementation report confirms all four toolchain gates passed with EXIT_CODE 0 and coverage ≥ 70%.

### Phase 2 — Final QC Loop

- [x] [P2-T1] Run final Black format check
  - Command: `poetry run black --check src tests`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/qa-gates/final-qc-black.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:`. If `EXIT_CODE` is non-zero, fix formatting and restart Phase 2 from P2-T1.

- [x] [P2-T2] Run final Ruff lint check
  - Command: `poetry run ruff check src tests`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/qa-gates/final-qc-ruff.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:`. If `EXIT_CODE` is non-zero, fix violations and restart Phase 2 from P2-T1.

- [x] [P2-T3] Run final Pyright type check
  - Command: `poetry run pyright`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/qa-gates/final-qc-pyright.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:` (error/warning count). If `EXIT_CODE` is non-zero, fix type errors and restart Phase 2 from P2-T1.

- [x] [P2-T4] Run final Pytest with coverage
  - Command: `poetry run pytest --cov=invoice_etl --cov-report=term-missing`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/qa-gates/final-qc-pytest.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:` which MUST include numeric post-change coverage headline values. If `EXIT_CODE` is non-zero, fix failing tests and restart Phase 2 from P2-T1.

- [x] [P2-T5] Run coverage threshold gate
  - Command: `poetry run coverage report --fail-under=70`
  - Acceptance: Artifact written to `docs/features/active/2026-04-30-excel-export-loader-6/evidence/qa-gates/final-qc-coverage-threshold.md` with fields `Timestamp:`, `Command:`, `EXIT_CODE: 0`, `Output Summary:` (reported coverage percentage). If `EXIT_CODE` is non-zero, add tests to raise coverage above 70% and restart Phase 2 from P2-T1.

- [x] [P2-T6] Delegate reduced small-path audit to `feature_code_review_agent`
  - Handoff parameters: `PRBaseBranch=main`, feature folder `docs/features/active/2026-04-30-excel-export-loader-6/`
  - Acceptance: `feature_code_review_agent` completes a reduced audit and returns a code-review artifact at `docs/features/active/2026-04-30-excel-export-loader-6/` confirming all AC-1 through AC-6 items are verified.

## Open Questions / Notes

- `openpyxl` is not currently in `pyproject.toml`; P1-T1 requires adding it via `poetry add openpyxl` before running toolchain checks.
- All Phase 2 command tasks are unconditional. No SKIPPED completion path is valid for P2-T1 through P2-T5.
