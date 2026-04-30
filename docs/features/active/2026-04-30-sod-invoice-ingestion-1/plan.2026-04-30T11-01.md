# 2026-04-30-sod-invoice-ingestion — Plan

- **Issue:** #1
- **Issue URL:** https://github.com/drmoisan/invoice-etl/issues/1
- **Requirements Source:** `docs/features/active/2026-04-30-sod-invoice-ingestion-1/issue.md`
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-04-30T11-01
- **Status:** Ready
- **Version:** 1.0
- **Work Mode:** full-feature

## Overview

Extend the Invoice ETL pipeline to fully parse and persist SOD (HEB Store Order Deal) invoice fields: five new `LineItem` columns (`item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure`) and one new `Invoice` column (`customer_number`). A SOD-format detection and dispatch path is added to `invoice_transformer.py`. The SQL INSERT statements in `db_loader.py` are updated to reference the new columns, and `docker/init.sql` is updated to declare them in the schema. All changes are covered by new unit tests and must pass the full Black → Ruff → Pyright strict → pytest ≥ 70% toolchain. Acceptance criteria are drawn from `docs/features/active/2026-04-30-sod-invoice-ingestion-1/issue.md`.

## Required References

- Copilot Instructions: [`.github/copilot-instructions.md`](../../../../.github/copilot-instructions.md)
- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Code Change Policy: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)
- Python Suppressions Policy: [`.github/instructions/python-suppressions.instructions.md`](../../../../.github/instructions/python-suppressions.instructions.md)
- Self-Explanatory Code Commenting: [`.github/instructions/self-explanatory-code-commenting.instructions.md`](../../../../.github/instructions/self-explanatory-code-commenting.instructions.md)

**All work must comply with these policies; do not duplicate their content here.**

---

### Phase 0 — Context, Policy Compliance & Baseline

- [x] [P0-T1] Read all seven required policy documents in the mandated order and record a policy-read evidence artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/phase0-instructions-read.md`
  - Policy read order: (1) `.github/copilot-instructions.md`, (2) `.github/instructions/general-code-change.instructions.md`, (3) `.github/instructions/general-unit-test.instructions.md`, (4) `.github/instructions/python-code-change.instructions.md`, (5) `.github/instructions/python-unit-test.instructions.md`, (6) `.github/instructions/python-suppressions.instructions.md`, (7) `.github/instructions/self-explanatory-code-commenting.instructions.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/phase0-instructions-read.md` exists and contains `Timestamp:`, `Policy Order:`, and an explicit list of all seven files read.

- [x] [P0-T2] Run `poetry run black src tests --check` to capture baseline formatting state and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-black.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-black.md` exists and contains `Timestamp:`, `Command: poetry run black src tests --check`, `EXIT_CODE: <int>`, and `Output Summary:` stating whether any files would be reformatted.

- [x] [P0-T3] Run `poetry run ruff check src tests` to capture baseline linting state and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-ruff.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-ruff.md` exists and contains `Timestamp:`, `Command: poetry run ruff check src tests`, `EXIT_CODE: <int>`, and `Output Summary:` stating the violation count or confirming no violations.

- [x] [P0-T4] Run `poetry run pyright` to capture baseline type-check state and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-pyright.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-pyright.md` exists and contains `Timestamp:`, `Command: poetry run pyright`, `EXIT_CODE: <int>`, and `Output Summary:` stating the error and warning counts.

- [x] [P0-T5] Run `poetry run pytest --cov=invoice_etl --cov-report=term-missing` to capture baseline test and coverage state and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-pytest.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-pytest.md` exists and contains `Timestamp:`, `Command: poetry run pytest --cov=invoice_etl --cov-report=term-missing`, `EXIT_CODE: <int>`, and `Output Summary:` recording the numeric total coverage percentage for `invoice_etl` and the test pass/fail counts.

- [x] [P0-T6] Run `poetry run coverage report --fail-under=70` to verify the baseline coverage threshold and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-coverage-threshold.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-coverage-threshold.md` exists and contains `Timestamp:`, `Command: poetry run coverage report --fail-under=70`, `EXIT_CODE: <int>`, and `Output Summary:` stating the total coverage percentage and whether the threshold was met.

---

### Phase 1 — Model Extension (`src/invoice_etl/models/invoice.py`)

- [x] [P1-T1] Add five new optional fields to the `LineItem` class in `src/invoice_etl/models/invoice.py`: `item: str | None = None`, `store_number: str | None = None`, `order_date: datetime.date | None = None`, `offer_number: str | None = None`, `unit_of_measure: str | None = None`, each with a one-line docstring per the self-explanatory-code-commenting policy
  - Preconditions: P0-T1 through P0-T6 are complete.
  - Acceptance: Running `python -c "from invoice_etl.models.invoice import LineItem; li = LineItem(); assert li.item is None; assert li.store_number is None; assert li.order_date is None; assert li.offer_number is None; assert li.unit_of_measure is None; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P1-T2] Add one new optional field to the `Invoice` class in `src/invoice_etl/models/invoice.py`: `customer_number: str | None = None`, with a one-line docstring per the self-explanatory-code-commenting policy
  - Preconditions: P1-T1 is complete.
  - Acceptance: Running `python -c "from invoice_etl.models.invoice import Invoice; inv = Invoice(invoice_number='X'); assert inv.customer_number is None; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

---

### Phase 2 — Transformer Extension + Tests (`src/invoice_etl/transform/invoice_transformer.py`, `tests/test_transform.py`)

#### Implementation

- [x] [P2-T1] Add five module-level SOD regex constants to `src/invoice_etl/transform/invoice_transformer.py`: `_SOD_INVOICE_NUMBER_RE` (`r"Invoice Number:\s*(\S+)"`), `_SOD_INVOICE_DATE_RE` (`r"Invoice Date:\s*(\d{1,2}/\d{1,2}/\d{4})"`), `_SOD_CUSTOMER_NUMBER_RE` (`r"Customer Number:\s*(\S+)"`), `_SOD_TOTAL_RE` (`r"TOTAL:\s*\$?([\d,]+\.\d{2})"`), and `_SOD_LINE_ITEM_RE` (the 9-group multiline pattern specified in `artifacts/research/20260430-sod-invoice-ingestion-implementation-research.md`), each preceded by an inline comment explaining its purpose
  - Preconditions: P1-T2 is complete.
  - Acceptance: Running `python -c "from invoice_etl.transform.invoice_transformer import _SOD_INVOICE_NUMBER_RE, _SOD_INVOICE_DATE_RE, _SOD_CUSTOMER_NUMBER_RE, _SOD_TOTAL_RE, _SOD_LINE_ITEM_RE; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P2-T2] Implement `_parse_sod_header(text: str) -> dict[str, object]` in `src/invoice_etl/transform/invoice_transformer.py` applying `_SOD_INVOICE_NUMBER_RE`, `_SOD_INVOICE_DATE_RE`, `_SOD_CUSTOMER_NUMBER_RE`, and `_SOD_TOTAL_RE` to extract `invoice_number` (str), `invoice_date` (`datetime.date` converted from MM/DD/YYYY), `customer_number` (str), `customer_name` (str or None), and `total_amount` (`Decimal` or None) from the provided page-1 text; include a complete Google-style docstring
  - Preconditions: P2-T1 is complete.
  - Acceptance: Running `python -c "from invoice_etl.transform.invoice_transformer import _parse_sod_header; r = _parse_sod_header('Invoice Number: SOD00093649\nInvoice Date: 03/16/2026\nCustomer Number: 081997\nJOHN DOE\nHEB GROCERY COMPANY'); assert r['invoice_number'] == 'SOD00093649'; assert str(r['invoice_date']) == '2026-03-16'; assert r['customer_number'] == '081997'; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P2-T3] Implement `_merge_truncated_lines(lines: list[str]) -> list[str]` in `src/invoice_etl/transform/invoice_transformer.py` that detects partial item rows (lines matching the item-counter + 5-digit-item-code prefix with no MM/DD/YYYY date present) and concatenates each such line with the immediately following continuation line using a single space; include a complete Google-style docstring
  - Preconditions: P2-T1 is complete.
  - Acceptance: Running `python -c "from invoice_etl.transform.invoice_transformer import _merge_truncated_lines; result = _merge_truncated_lines(['5 01553 RGF POPCORN CHIC', 'KEN 00562 03/13/2026 545039 1 EA 5.9400 5.94']); assert len(result) == 1; assert '00562' in result[0]; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P2-T4] Implement `_parse_sod_line_item(line: str) -> LineItem | None` in `src/invoice_etl/transform/invoice_transformer.py` that matches the line against `_SOD_LINE_ITEM_RE` and, when matched, constructs and returns a `LineItem` with all 9 fields populated (`item`, `description`, `store_number`, `order_date` as `datetime.date`, `offer_number`, `quantity` via `_parse_decimal`, `unit_of_measure`, `unit_price` via `_parse_decimal`, `line_total` via `_parse_decimal`), returning `None` for any non-matching line; include a complete Google-style docstring
  - Preconditions: P2-T1 and P1-T1 are complete.
  - Acceptance: Running `python -c "from invoice_etl.transform.invoice_transformer import _parse_sod_line_item; li = _parse_sod_line_item('5 01553 RGF POPCORN CHICKEN 00562 03/13/2026 545039 1 EA 5.9400 5.94'); assert li is not None; assert li.item == '01553'; assert li.store_number == '00562'; assert str(li.order_date) == '2026-03-13'; assert li.offer_number == '545039'; assert li.unit_of_measure == 'EA'; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P2-T5] Implement `_transform_sod_pages(pages: list[str], source_file: str | None) -> Invoice` in `src/invoice_etl/transform/invoice_transformer.py` that calls `_parse_sod_header` on the first-page text, then iterates all pages applying `_merge_truncated_lines` followed by `_parse_sod_line_item` on each resulting line, accumulating non-None results into `line_items`, and returns a fully populated `Invoice`; include a complete Google-style docstring
  - Preconditions: P2-T2, P2-T3, and P2-T4 are complete.
  - Acceptance: Running `python -c "from invoice_etl.transform.invoice_transformer import _transform_sod_pages; inv = _transform_sod_pages(['Invoice Number: SOD00093649\nInvoice Date: 03/16/2026\nCustomer Number: 081997\nHEB GROCERY COMPANY\n5 01553 RGF POPCORN CHICKEN 00562 03/13/2026 545039 1 EA 5.9400 5.94'], None); assert inv.invoice_number == 'SOD00093649'; assert len(inv.line_items) == 1; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P2-T6] Extend `transform_pages()` in `src/invoice_etl/transform/invoice_transformer.py` to check for the substring `"Customer Number:"` in the joined page text and, when found, return `_transform_sod_pages(pages, source_file=source_file)`; the existing generic parsing block must remain unchanged for all other inputs; update the function's docstring to document the SOD dispatch condition
  - Preconditions: P2-T5 is complete.
  - Acceptance: Running `python -c "from invoice_etl.transform.invoice_transformer import transform_pages; inv = transform_pages(['Invoice Number: SOD00093649\nInvoice Date: 03/16/2026\nCustomer Number: 081997\nHEB GROCERY COMPANY\n5 01553 RGF POPCORN CHICKEN 00562 03/13/2026 545039 1 EA 5.9400 5.94']); assert inv.customer_number == '081997'; assert len(inv.line_items) == 1; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

#### Tests

- [x] [P2-T7] Add `test_sod_header_parses_invoice_number` to `tests/test_transform.py` asserting that `_parse_sod_header("Invoice Number: SOD00093649\nInvoice Date: 03/16/2026\nCustomer Number: 081997\nHEB GROCERY COMPANY")` returns a dict where `result["invoice_number"] == "SOD00093649"`
  - Preconditions: P2-T2 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_sod_header_parses_invoice_number -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T8] Add `test_sod_header_parses_customer_number` to `tests/test_transform.py` asserting that `_parse_sod_header` called with the same representative SOD header text returns a dict where `result["customer_number"] == "081997"`
  - Preconditions: P2-T2 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_sod_header_parses_customer_number -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T9] Add `test_sod_header_parses_invoice_date` to `tests/test_transform.py` asserting that `_parse_sod_header` called with the same representative SOD header text returns a dict where `result["invoice_date"] == datetime.date(2026, 3, 16)`
  - Preconditions: P2-T2 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_sod_header_parses_invoice_date -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T10] Add `test_sod_line_item_parses_all_nine_fields` to `tests/test_transform.py` asserting that `_parse_sod_line_item("5 01553 RGF POPCORN CHICKEN 00562 03/13/2026 545039 1 EA 5.9400 5.94")` returns a `LineItem` where `item == "01553"`, `description` contains `"RGF POPCORN CHICKEN"`, `store_number == "00562"`, `order_date == datetime.date(2026, 3, 13)`, `offer_number == "545039"`, `quantity == Decimal("1")`, `unit_of_measure == "EA"`, `unit_price == Decimal("5.9400")`, and `line_total == Decimal("5.94")`
  - Preconditions: P2-T4 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_sod_line_item_parses_all_nine_fields -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T11] Add `test_sod_line_item_returns_none_for_non_matching_line` to `tests/test_transform.py` asserting that `_parse_sod_line_item("Item  Description  Store No  Str Ord Dt  Offer#  Qty  UOM  Unit Price  Amount")` returns `None`
  - Preconditions: P2-T4 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_sod_line_item_returns_none_for_non_matching_line -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T12] Add `test_merge_truncated_lines_merges_split_row` to `tests/test_transform.py` asserting that `_merge_truncated_lines(["5 01553 RGF POPCORN CHIC", "KEN 00562 03/13/2026 545039 1 EA 5.9400 5.94"])` returns a single-element list whose sole element contains both `"01553"` and `"00562"`
  - Preconditions: P2-T3 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_merge_truncated_lines_merges_split_row -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T13] Add `test_merge_truncated_lines_preserves_complete_rows` to `tests/test_transform.py` asserting that `_merge_truncated_lines(["5 01553 RGF POPCORN CHICKEN 00562 03/13/2026 545039 1 EA 5.9400 5.94", "6 60461 RGF DINO NUGGETS 20 OZ 00052 03/08/2026 545038 1 EA 4.9800 4.98"])` returns a two-element list where each element is identical to its corresponding input string
  - Preconditions: P2-T3 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_merge_truncated_lines_preserves_complete_rows -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T14] Add `test_transform_pages_sod_dispatches_and_sets_header_fields` to `tests/test_transform.py` asserting that `transform_pages(["Invoice Number: SOD00093649\nInvoice Date: 03/16/2026\nCustomer Number: 081997\nHEB GROCERY COMPANY"])` returns an `Invoice` where `invoice_number == "SOD00093649"` and `customer_number == "081997"`
  - Preconditions: P2-T6 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_transform_pages_sod_dispatches_and_sets_header_fields -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T15] Add `test_transform_pages_sod_accumulates_line_items_across_two_pages` to `tests/test_transform.py` using two SOD page strings each containing one valid line-item row (plus the header fields on page 1 only) and asserting that `transform_pages([page1, page2])` returns an `Invoice` with `len(line_items) == 2`
  - Preconditions: P2-T6 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_transform_pages_sod_accumulates_line_items_across_two_pages -v` exits with code 0 and the output contains `PASSED`.

- [x] [P2-T16] Add `test_transform_pages_non_sod_format_is_unchanged` to `tests/test_transform.py` asserting that `transform_pages(["Invoice No. INV-2024-001\nTotal: 1,200.00"])` returns an `Invoice` where `invoice_number == "INV-2024-001"` and `customer_number is None` (verifying the generic path is not disturbed by the SOD dispatch)
  - Preconditions: P2-T6 is complete.
  - Acceptance: `poetry run pytest tests/test_transform.py::test_transform_pages_non_sod_format_is_unchanged -v` exits with code 0 and the output contains `PASSED`.

---

### Phase 3 — Loader Extension + Tests (`src/invoice_etl/load/db_loader.py`, `tests/test_load.py`)

#### Implementation

- [x] [P3-T1] Update the `INSERT INTO invoices` SQL statement in `src/invoice_etl/load/db_loader.py` to include `customer_number` in the column list and `:customer_number` in the `VALUES` clause
  - Preconditions: P1-T2 is complete.
  - Acceptance: Running `python -c "text=open('src/invoice_etl/load/db_loader.py').read(); assert ':customer_number' in text, 'Missing :customer_number param'; assert text.count('customer_number') >= 2, 'Column must appear in both column list and VALUES'; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P3-T2] Update the `INSERT INTO line_items` SQL statement in `src/invoice_etl/load/db_loader.py` to include `item`, `store_number`, `order_date`, `offer_number`, and `unit_of_measure` in the column list and their corresponding `:param` names in the `VALUES` clause
  - Preconditions: P1-T1 is complete.
  - Acceptance: Running `python -c "text=open('src/invoice_etl/load/db_loader.py').read(); params=[':store_number',':order_date',':offer_number',':unit_of_measure']; assert all(p in text for p in params); assert ':item,' in text or ':item\n' in text or ':item)' in text; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

#### Tests

- [x] [P3-T3] Add `test_load_passes_customer_number_to_invoices_insert` to `tests/test_load.py` constructing an `Invoice` with `customer_number="081997"`, calling `load_invoice` with a mocked engine, and asserting that `mock_conn.execute.call_args_list[0].args[1]["customer_number"] == "081997"`
  - Preconditions: P3-T1 is complete.
  - Acceptance: `poetry run pytest tests/test_load.py::test_load_passes_customer_number_to_invoices_insert -v` exits with code 0 and the output contains `PASSED`.

- [x] [P3-T4] Add `test_load_passes_new_line_item_fields_to_insert` to `tests/test_load.py` constructing an `Invoice` that contains one `LineItem` with `item="01553"`, `store_number="00562"`, `offer_number="545039"`, and `unit_of_measure="EA"`, calling `load_invoice` with a mocked engine, and asserting that the second `mock_conn.execute` call's parameter dict contains all four of those field values
  - Preconditions: P3-T2 is complete.
  - Acceptance: `poetry run pytest tests/test_load.py::test_load_passes_new_line_item_fields_to_insert -v` exits with code 0 and the output contains `PASSED`.

---

### Phase 4 — Schema Update (`docker/init.sql`)

- [x] [P4-T1] Add `customer_number TEXT,` as a new column in the `CREATE TABLE IF NOT EXISTS invoices` block in `docker/init.sql`, placed after the `customer_address TEXT,` line
  - Acceptance: Running `python -c "text=open('docker/init.sql').read(); assert 'customer_number' in text; assert text.count('CREATE TABLE IF NOT EXISTS') == 2; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

- [x] [P4-T2] Add five new columns to the `CREATE TABLE IF NOT EXISTS line_items` block in `docker/init.sql`, placed after the `line_total NUMERIC(18, 2),` line: `item TEXT,`, `store_number TEXT,`, `order_date DATE,`, `offer_number TEXT,`, `unit_of_measure TEXT,`
  - Preconditions: P4-T1 is complete.
  - Acceptance: Running `python -c "import re; text=open('docker/init.sql').read(); cols=['store_number','order_date','offer_number','unit_of_measure']; assert all(c in text for c in cols); assert re.search(r'item\s+TEXT', text); assert text.count('CREATE TABLE IF NOT EXISTS') == 2; print('OK')"` (from workspace root) exits with code 0 and prints `OK`.

---

### Phase 5 — Final QC Loop

> All tasks in this phase are unconditional. `EXIT_CODE: SKIPPED` is not a valid outcome for any task. If any step changes files or exits non-zero, fix the reported issues and restart Phase 5 from P5-T1.

- [x] [P5-T1] Run `poetry run black src tests` and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-black.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-black.md` exists and contains `Timestamp:`, `Command: poetry run black src tests`, `EXIT_CODE: 0`, and `Output Summary:` confirming no files were reformatted. If `EXIT_CODE` is non-zero or files were changed, correct formatting and restart from P5-T1.

- [x] [P5-T2] Run `poetry run ruff check src tests` and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-ruff.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-ruff.md` exists and contains `Timestamp:`, `Command: poetry run ruff check src tests`, `EXIT_CODE: 0`, and `Output Summary:` confirming zero linting violations. If `EXIT_CODE` is non-zero, resolve all reported violations and restart from P5-T1.

- [x] [P5-T3] Run `poetry run pyright` and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-pyright.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-pyright.md` exists and contains `Timestamp:`, `Command: poetry run pyright`, `EXIT_CODE: 0`, and `Output Summary:` confirming zero type errors. If `EXIT_CODE` is non-zero, resolve all type errors and restart from P5-T1.

- [x] [P5-T4] Run `poetry run pytest --cov=invoice_etl --cov-report=term-missing` and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-pytest.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-pytest.md` exists and contains `Timestamp:`, `Command: poetry run pytest --cov=invoice_etl --cov-report=term-missing`, `EXIT_CODE: 0`, and `Output Summary:` recording the numeric post-change total coverage percentage for `invoice_etl`, the per-module coverage for `invoice_etl/transform/invoice_transformer`, and the test pass/fail counts. If `EXIT_CODE` is non-zero, fix failing tests and restart from P5-T1.

- [x] [P5-T5] Run `poetry run coverage report --fail-under=70` and record artifact at `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-coverage-threshold.md`
  - Acceptance: File `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-coverage-threshold.md` exists and contains `Timestamp:`, `Command: poetry run coverage report --fail-under=70`, `EXIT_CODE: 0`, and `Output Summary:` confirming total coverage meets or exceeds 70%. If `EXIT_CODE` is non-zero, add tests to increase coverage and restart from P5-T1.

- [x] [P5-T6] Verify that the `invoice_etl/transform/invoice_transformer` per-module coverage recorded in the P5-T4 artifact meets the ≥ 80% branch coverage threshold required by `docs/features/active/2026-04-30-sod-invoice-ingestion-1/issue.md`, and record the baseline-versus-post-change delta comparison in `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-coverage-threshold.md`
  - Preconditions: P5-T4 and P5-T5 are complete. The P0-T5 baseline artifact must exist to provide the baseline coverage figure.
  - Acceptance: `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-coverage-threshold.md` contains the baseline coverage percentage from P0-T5, the post-change coverage percentage from P5-T4, the per-module `invoice_transformer` coverage percentage, and a line stating `THRESHOLD MET` when that percentage is ≥ 80% or `THRESHOLD NOT MET — REMEDIATION REQUIRED` otherwise.

---

## Test Plan

- **Unit (new — `tests/test_transform.py`):** 10 new functions covering `_parse_sod_header` (invoice number, customer number, invoice date), `_parse_sod_line_item` (all-9-fields success, non-matching returns None), `_merge_truncated_lines` (split-row merge, complete-row preservation), and `transform_pages` (SOD dispatch with header fields, multi-page accumulation, non-SOD generic path unchanged).
- **Unit (new — `tests/test_load.py`):** 2 new functions verifying that `customer_number` is present in the invoices-insert parameter dict and that the 4 key new `LineItem` fields are present in the line-items-insert parameter dict.
- **Regression:** All 4 pre-existing tests in `tests/test_transform.py` and 2 pre-existing tests in `tests/test_load.py` must continue to pass with zero failures.
- **Integration:** Out of scope; `docker/init.sql` changes apply on container recreate and are verified by inspection.
- **Coverage evidence artifacts:**
  - Baseline: `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/baseline/baseline-pytest.md`
  - Post-change: `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-pytest.md`
  - Threshold and delta: `docs/features/active/2026-04-30-sod-invoice-ingestion-1/evidence/qa-gates/final-qc-coverage-threshold.md`

## Open Questions / Notes

- The `customer_name` extraction in `_parse_sod_header` uses a heuristic to identify consecutive all-caps lines. If the primary regex (`_SOD_CUSTOMER_NAME_BLOCK_RE`) does not match (e.g., due to company suffix variation), the implementation should fall back to selecting the last consecutive all-caps line. If all heuristics fail, `customer_name` defaults to `None`, which is acceptable per the spec. This behavior does not require a dedicated test task but should be documented in the function's docstring.
- `docker/init.sql` is a fresh-init script with no migration framework. If a live database container is running when this change is deployed, the container must be recreated or the new columns must be added manually. This constraint is documented in `docs/features/active/2026-04-30-sod-invoice-ingestion-1/issue.md` under Constraints & Risks.
