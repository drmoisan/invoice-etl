# flet-ui (Issue #9)

- Date captured: 2026-05-08
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/flet-ui/ (Issue #9)

- Issue: #9
- Issue URL: https://github.com/drmoisan/invoice-etl/issues/9
- Last Updated: 2026-05-08
- Work Mode: minor-audit

## Problem / Why

The invoice-etl pipeline currently has no graphical interface. Users must invoke it via Python scripts or CLI,
requiring knowledge of the codebase. A desktop GUI would make the tool accessible to non-technical operators.

## Proposed Behavior

Add a Flet-based desktop UI that exposes the full ETL pipeline through a simple window:
- A file picker to select an input PDF invoice.
- A toggle to choose between Excel export and PostgreSQL export modes.
- An Export button that, in Excel mode, opens a save-file dialog; in DB mode, loads directly to PostgreSQL.
- A status/feedback area that displays success or error messages.
All business logic is isolated in a `UIController` class with no Flet dependencies, making it fully testable.

## Acceptance Criteria

- [x] AC1: New sub-package `src/invoice_etl/ui/` exists with `__init__.py`, `controller.py`, and `app.py`.
- [x] AC2: `UIController` in `controller.py` has zero Flet imports and exposes `set_input_file`, `set_output_mode`, and `run_export` methods matching the required signatures.
- [x] AC3: `run_export` with Excel mode and a confirmed save path invokes the ETL pipeline and returns a success message.
- [x] AC4: `run_export` with Excel mode and a cancelled save dialog (output_path=None) returns a cancelled message without running the pipeline.
- [x] AC5: `run_export` with DB mode runs the ETL pipeline directly (no file-picker path required) and returns a success message.
- [x] AC6: `run_export` with no input file set returns an error message without running the pipeline.
- [x] AC7: `run_export` propagates ETL errors as a descriptive error message string rather than raising.
- [x] AC8: `tests/test_ui_controller.py` exists covering all AC2–AC7 scenarios using only mocks (no real I/O, no real DB).
- [x] AC9: `flet` is added as a Poetry dependency in `pyproject.toml`.
- [x] AC10: All four toolchain steps pass in a single clean pass: black → ruff → pyright → pytest (≥80% repo-wide, ≥90% on new modules).

## Constraints & Risks

- Flet must be added as a Poetry dependency.
- The Flet view (app.py) cannot be headlessly tested; it must be omitted from coverage requirements.
- The UIController must have zero Flet imports for testability.
- No file may exceed 500 lines.

## Test Conditions to Consider

- [ ] UIController: Excel mode positive path (file dialog confirms path, ETL runs, success result returned)
- [ ] UIController: DB mode positive path (ETL runs, no file dialog, success result returned)
- [ ] UIController: Excel mode cancel path (file dialog returns None, no ETL run, cancelled result returned)
- [ ] UIController: no input file set (returns invalid-state result, no ETL run)
- [ ] UIController: ETL failure (underlying pipeline raises, error result returned with message)

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/flet-ui/` folder from the template