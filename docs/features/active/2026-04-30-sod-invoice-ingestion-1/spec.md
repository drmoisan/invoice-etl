# 2026-04-30-sod-invoice-ingestion — Spec

- **Issue:** #1
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-04-30T11-01
- **Status:** Draft
- **Version:** 0.1

## Overview

The existing ETL pipeline extracts a generic set of invoice fields (invoice number, dates, totals, basic line item description/qty/price). The sample document `artifacts/SOD00093649.pdf` is a 40-page HEB Store Order Deal invoice with a fixed-width columnar line-item format that includes domain-specific fields not currently modelled: Item code, Store Number, Order Date, Offer Number, and Unit of Measure. Additionally, Customer Number is present in the invoice header but not extracted or stored. Without this work the pipeline silently discards these fields, making the stored data incomplete for downstream reconciliation.


## Behavior

- Parse header fields from the SOD invoice format: Invoice Number, Invoice Date, Customer Name, Customer Number.
- Parse every line item row across all 40 pages with the following columns: Item (item code), Description, Store Number, Store Order Date, Offer Number, Quantity, Unit of Measure (UOM), Unit Price, Amount.
- Extend the `LineItem` Pydantic model to carry the new line-item fields.
- Extend the `Invoice` Pydantic model to carry `customer_number`.
- Update `docker/init.sql` (schema migration): add new columns to `line_items`; add `customer_number` to `invoices`.
- Update `db_loader.py` to persist all new fields.
- Update `invoice_transformer.py` with a SOD-format parser that handles the multi-page, fixed-width line-item layout produced by pdfplumber text extraction.
- All changes must pass the full toolchain: Black → Ruff → Pyright strict → pytest ≥ 70% coverage.


## Inputs / Outputs

- **Input**: `pages: list[str]` — raw text extracted per page by `pdfplumber.page.extract_text()`, one element per PDF page. No additional CLI flags or environment variables are required; the calling interface is unchanged.
- **Output**: An `Invoice` model instance with all header fields populated (`invoice_number`, `invoice_date`, `customer_number`, `total_amount`, `customer_name`) and `line_items` containing one `LineItem` per parsed row across all pages. Each `LineItem` carries all 9 fields: `description`, `quantity`, `unit_price`, `line_total`, `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure`.
- **Config keys and defaults**: No new environment variables or configuration keys. Existing `DATABASE_URL` and `PDF_PATH` environment variables are unchanged.
- **Versioning / backward-compatibility**: `transform_pages()` is extended in-place via format detection. Non-SOD inputs continue to follow the existing generic code path. All new model fields default to `None`, so existing callers that do not supply them produce valid model instances without modification.

## API / CLI Surface

The CLI entry point (`src/invoice_etl/main.py`) and its flags are unchanged. All new behavior is internal to the transform sub-package.

**`transform_pages()` — extended public function**

```python
def transform_pages(pages: list[str], source_file: str | None = None) -> Invoice:
    """Transform a list of raw PDF page strings into a structured Invoice.

    Detects SOD format by checking for the "Customer Number:" label in the
    combined page text. If detected, delegates to _transform_sod_pages();
    otherwise, follows the existing generic parsing path.
    """
```

**New private helpers in `invoice_transformer.py`**

```python
def _transform_sod_pages(pages: list[str], source_file: str | None) -> Invoice:
    """Orchestrate SOD header and line-item parsing across all pages."""

def _parse_sod_header(text: str) -> dict[str, object]:
    """Apply SOD-specific header regexes; return extracted fields as a dict."""

def _parse_sod_line_item(line: str) -> LineItem | None:
    """Match one text line against _SOD_LINE_ITEM_RE; return LineItem or None."""

def _merge_truncated_lines(lines: list[str]) -> list[str]:
    """Merge line-item rows split at PDF page boundaries."""
```

**New module-level regexes in `invoice_transformer.py`**

| Name | Pattern | Purpose |
|------|---------|--------|
| `_SOD_INVOICE_NUMBER_RE` | `r"Invoice Number:\s*(\S+)"` | Matches `Invoice Number: SOD00093649` |
| `_SOD_INVOICE_DATE_RE` | `r"Invoice Date:\s*(\d{1,2}/\d{1,2}/\d{4})"` | Matches `Invoice Date: 03/16/2026` |
| `_SOD_CUSTOMER_NUMBER_RE` | `r"Customer Number:\s*(\S+)"` | Matches `Customer Number: 081997` |
| `_SOD_LINE_ITEM_RE` | Multiline regex with 9 capture groups (sequence counter + item code + description + store number + MM/DD/YYYY date + offer number + quantity + UOM + unit price + amount) | Matches complete line item rows |

**Example invocations with expected outputs**

```python
# SOD format — returns populated Invoice
invoice = transform_pages(sod_pages, source_file="SOD00093649.pdf")
assert invoice.invoice_number == "SOD00093649"
assert invoice.customer_number == "081997"
assert len(invoice.line_items) > 0
assert invoice.line_items[0].item == "01553"
assert invoice.line_items[0].store_number == "00562"
assert invoice.line_items[0].order_date == date(2026, 3, 13)

# Generic format — unchanged behavior, no regression
invoice = transform_pages(["Invoice No. INV-2024-001\nTotal: 1,200.00"])
assert invoice.invoice_number == "INV-2024-001"
assert invoice.line_items == []
assert invoice.customer_number is None
```

**Contracts and validation rules**

- `pages` must be a `list[str]`; empty strings (from blank PDF pages) are tolerated and produce no line items.
- Format detection is performed once on the full joined text; the result governs parsing for all pages in the call.
- `_parse_sod_line_item` returns `None` for any line that does not fully match the 9-group regex — headers, blank lines, total rows, and unresolvable truncated rows are silently skipped.
- `_parse_sod_header` is called on the first-page text only. If `Invoice Number:` is not found, `invoice_number` defaults to `"UNKNOWN"`.
- `_merge_truncated_lines` must execute before `_parse_sod_line_item` is applied to each line.

## Data & State

### Model field additions

**`LineItem` (Pydantic v2, `src/invoice_etl/models/invoice.py`)**

| Field | Type | Default | Source |
|-------|------|---------|--------|
| `item` | `str \| None` | `None` | 5-digit SKU/item code, column 1 |
| `store_number` | `str \| None` | `None` | 5-digit store code, column 3 |
| `order_date` | `datetime.date \| None` | `None` | MM/DD/YYYY date from column 4, converted via `strptime` |
| `offer_number` | `str \| None` | `None` | Deal/offer identifier, column 5 |
| `unit_of_measure` | `str \| None` | `None` | Uppercase alpha UOM from column 7 (e.g., `"EA"`, `"CS"`) |

**`Invoice` (Pydantic v2, `src/invoice_etl/models/invoice.py`)**

| Field | Type | Default | Source |
|-------|------|---------|--------|
| `customer_number` | `str \| None` | `None` | Header label `Customer Number:` from page 1 |

### SQL schema changes (`docker/init.sql`)

**`invoices` table** — add one column after `customer_address`:
```sql
customer_number TEXT,
```

**`line_items` table** — add five columns after `line_total`:
```sql
item            TEXT,
store_number    TEXT,
order_date      DATE,
offer_number    TEXT,
unit_of_measure TEXT,
```

### DB INSERT SQL changes (`src/invoice_etl/load/db_loader.py`)

**Invoices INSERT** — `customer_number` added to the column list and VALUES clause. The parameter dict (`invoice.model_dump(exclude={"line_items"})`) includes `customer_number` automatically once the model field is added; no manual dict change is required.

**Line items INSERT** — `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure` added to the column list and VALUES clause. The parameter dict (`{"invoice_id": invoice_id, **item.model_dump()}`) includes all new fields automatically once they are added to `LineItem`.

### Data transformations and invariants

- Code fields (`item`, `store_number`, `offer_number`, `customer_number`) are typed as `str | None` to preserve zero-padding (e.g., `"00562"` must not be coerced to integer `562`).
- `order_date` is converted from the raw `MM/DD/YYYY` string to `datetime.date` before model construction using `datetime.strptime(s, "%m/%d/%Y").date()`.
- `quantity`, `unit_price`, and `line_total` use the existing `_parse_decimal()` helper, which strips commas and converts to `Decimal`, returning `None` on parse failure.
- Header fields repeat on every PDF page; the parser reads them from the first page only and does not overwrite with subsequent pages.

### Caching / persistence details

No caching layer is introduced. All data is written directly to PostgreSQL via a SQLAlchemy `Engine`. The PostgreSQL Docker container is the sole persistence target.

### Migration / backfill requirements

- `docker/init.sql` uses `CREATE TABLE IF NOT EXISTS`. New containers created after this change receive the updated schema automatically.
- For an existing live database, columns must be added manually:
  ```sql
  ALTER TABLE invoices ADD COLUMN customer_number TEXT;
  ALTER TABLE line_items ADD COLUMN item TEXT;
  ALTER TABLE line_items ADD COLUMN store_number TEXT;
  ALTER TABLE line_items ADD COLUMN order_date DATE;
  ALTER TABLE line_items ADD COLUMN offer_number TEXT;
  ALTER TABLE line_items ADD COLUMN unit_of_measure TEXT;
  ```
- Existing rows will have `NULL` in all new columns, consistent with the `| None` defaults on all new model fields.

## Constraints & Risks

- The line-item rows are fused into a single table cell by pdfplumber (not split into individual columns). The parser must use regex or positional splitting on the extracted text string.
- Page continuation: header fields repeat on every page; line items accumulate across all 40 pages. The parser must deduplicate header reads and concatenate line items.
- Existing `Invoice`/`LineItem` models are referenced by existing tests. Any schema change must be backward-compatible or all affected tests updated.
- `docker/init.sql` is a fresh-init script (no migration framework). If a live database exists, manual column addition is required.
- No new third-party dependencies should be introduced.


## Implementation Strategy

### Changed files

| File | Specific changes |
|------|------------------|
| `src/invoice_etl/models/invoice.py` | Add `item: str \| None = None`, `store_number: str \| None = None`, `order_date: datetime.date \| None = None`, `offer_number: str \| None = None`, `unit_of_measure: str \| None = None` to `LineItem`; add `customer_number: str \| None = None` to `Invoice` |
| `src/invoice_etl/transform/invoice_transformer.py` | Add `import datetime` if not already present; add 4 module-level SOD regexes (`_SOD_INVOICE_NUMBER_RE`, `_SOD_INVOICE_DATE_RE`, `_SOD_CUSTOMER_NUMBER_RE`, `_SOD_LINE_ITEM_RE`); implement `_parse_sod_header`, `_merge_truncated_lines`, `_parse_sod_line_item`, `_transform_sod_pages`; add SOD format detection dispatch at the top of `transform_pages()` |
| `src/invoice_etl/load/db_loader.py` | Update invoices INSERT SQL to include `customer_number` in column list and `:customer_number` in VALUES; update line_items INSERT SQL to include the 5 new columns and their `:param` names |
| `docker/init.sql` | Add `customer_number TEXT,` to the `invoices` CREATE TABLE; add `item TEXT, store_number TEXT, order_date DATE, offer_number TEXT, unit_of_measure TEXT,` to the `line_items` CREATE TABLE |
| `tests/test_transform.py` | Add `test_sod_transform_parses_header`, `test_sod_transform_parses_line_items`, `test_sod_transform_multi_page_accumulation`, `test_sod_transform_truncated_row_handled_gracefully`, `test_sod_transform_does_not_regress_generic_path`; existing 4 tests unchanged |
| `tests/test_load.py` | Add `test_load_invoice_persists_new_fields` — verifies that `mock_conn.execute` first call SQL contains `:customer_number` and second call SQL contains `:item`, `:store_number`, `:order_date`, `:offer_number`, `:unit_of_measure` |

### New classes / functions

No new classes. New private functions added to `src/invoice_etl/transform/invoice_transformer.py`:
- `_parse_sod_header(text: str) -> dict[str, object]`
- `_merge_truncated_lines(lines: list[str]) -> list[str]`
- `_parse_sod_line_item(line: str) -> LineItem | None`
- `_transform_sod_pages(pages: list[str], source_file: str | None) -> Invoice`

### Dependency changes

None. All required stdlib (`re`, `datetime`, `decimal`) and project libraries (`pydantic`, `sqlalchemy`, `pdfplumber`) are already present in `pyproject.toml`.

### Logging additions

- `logger.debug()` in `_parse_sod_line_item()` when a line does not match `_SOD_LINE_ITEM_RE`, to provide visibility into skipped lines without polluting `info`-level output.
- `logger.warning()` in `_merge_truncated_lines()` when a candidate truncated line cannot be paired with a continuation line.
- `logger.info()` at the end of `_transform_sod_pages()` reporting the total number of line items parsed across all pages.

### Rollout plan

- No feature flags required. SOD detection is backward-compatible: non-SOD inputs follow the unmodified generic parsing path, producing no behavioral change for existing callers.
- The `docker/init.sql` schema change takes effect only for new container initializations. Existing containers require the manual `ALTER TABLE` statements documented in the Data & State section.
- No staged deployment is needed. This is a single-tenant local ETL pipeline.

## Definition of Done

- [ ] Acceptance criteria documented and mapped to tests or demos
- [ ] Behavior matches acceptance criteria in all documented environments
- [ ] Tests updated/added (unit/integration as applicable)
- [ ] Edge cases and error handling covered by tests
- [ ] Docs updated (README, docs/features/active/... links)
- [ ] Telemetry/logging added or updated (if applicable)
- [ ] Toolchain pass completed (format → lint → type-check → test)

## Seeded Test Conditions (from potential)
- [ ] Unit test: parse a representative 3-line SOD text block and assert all 9 fields per row.
- [ ] Unit test: header extraction returns correct Invoice Number, Invoice Date, Customer Number, Customer Name from SOD page 1 text.
- [ ] Unit test: multi-page accumulation — two pages of line items produce correct combined count.
- [ ] Unit test: `load_invoice()` with new fields calls execute with correct parameters.
- [ ] Edge case: last row on a page truncated mid-text (observed in PDF: "501553 RGF POPCORN CHIC") — parser handles gracefully.
