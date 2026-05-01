# excel-export-loader (Issue #6)

- Date captured: 2026-04-30
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/excel-export-loader/ (Issue #6)

- Issue: #6
- Issue URL: https://github.com/drmoisan/invoice-etl/issues/6
- Last Updated: 2026-04-30
- Work Mode: minor-audit

## Problem / Why

The current pipeline only loads extracted invoice data into PostgreSQL. Operators who do not have a database available, or who need a portable snapshot, cannot export results. An Excel output option would allow invoice data to be saved as a `.xlsx` file without requiring a live database connection.

## Proposed Behavior

`main.py` gains an `--output` flag (`db` or `excel`). When `--output excel` is supplied, the pipeline writes the transformed invoice data to a `.xlsx` file (one sheet for the invoice header, one for line items) via a new `excel_loader.py` module in `src/invoice_etl/load/`. The existing `db` path is the default and must remain fully functional.

## Acceptance Criteria

- [x] AC-1: A new `src/invoice_etl/load/excel_loader.py` module exists, is fully typed, and exports a `load_invoice_to_excel(invoice: Invoice, output_path: Path) -> Path` function that writes a `.xlsx` file with two sheets: `Invoice` (header fields) and `LineItems` (one row per line item).
- [x] AC-2: `main.py` accepts an `--output` CLI flag with choices `db` (default) and `excel`. When `--output excel` is passed, the pipeline calls `load_invoice_to_excel` instead of `load_invoice` and logs the written file path.
- [x] AC-3: The existing `db` load path in `main.py` is unchanged when `--output db` (default) is in effect.
- [x] AC-4: Unit tests for `excel_loader.py` cover the happy-path write (header sheet, line-items sheet, correct column names) without touching the filesystem (use `unittest.mock` or in-memory verification).
- [x] AC-5: Unit tests for the updated `main.py` cover `--output excel` and `--output db` flag dispatch, verifying the correct loader is called.
- [x] AC-6: Full toolchain (Black → Ruff → Pyright → Pytest with `--cov=invoice_etl`) passes with EXIT_CODE 0 and coverage ≥ 70%.

## Constraints & Risks

- Use `openpyxl` for `.xlsx` generation; it is the standard library used with pandas and is lightweight for this use case. Verify it can be added to `pyproject.toml` via `poetry add openpyxl`.
- Do not break existing DB loader behaviour or any existing tests.
- No temporary files in tests (policy-mandated).
- Pyright strict mode is enforced; all new code must be fully typed.

## Test Conditions to Consider

- [ ] `load_invoice_to_excel` writes correct sheet names and column headers.
- [ ] `load_invoice_to_excel` returns the output path.
- [ ] `main` routes to Excel loader when `--output excel` is provided.
- [ ] `main` routes to DB loader when `--output db` (or no flag) is provided.