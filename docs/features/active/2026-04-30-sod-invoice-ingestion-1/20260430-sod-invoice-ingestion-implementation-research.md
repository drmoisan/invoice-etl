<!-- markdownlint-disable-file -->

# Task Research Notes: SOD Invoice Ingestion Implementation

## Research Executed

### File Analysis

- `docs/features/active/2026-04-30-sod-invoice-ingestion-1/issue.md`
  - Authoritative feature spec. Issue #1. Work mode: full-feature. Status: Promoted.
  - Defines 8 acceptance criteria, 5 test conditions, key constraints (no new dependencies, no migration framework).
- `docs/features/active/2026-04-30-sod-invoice-ingestion-1/spec.md`
  - Status: Draft v0.1. Partially filled. Behavior and constraints sections are populated; Implementation Strategy and API/CLI Surface are stubs.
- `docs/features/active/2026-04-30-sod-invoice-ingestion-1/user-story.md`
  - Status: Draft. Story statement stubs not filled. Acceptance criteria and problem statement match issue.md.
- `src/invoice_etl/models/invoice.py`
  - `LineItem` has 4 fields: `description: str | None`, `quantity: Decimal | None`, `unit_price: Decimal | None`, `line_total: Decimal | None`.
  - `Invoice` has 13 fields: `invoice_number` (required), `invoice_date`, `due_date`, `vendor_name`, `vendor_address`, `customer_name`, `customer_address`, `currency`, `subtotal`, `tax_amount`, `total_amount`, `line_items: list[LineItem]`, `source_file`. Missing: `customer_number`.
  - Both are Pydantic v2 `BaseModel` subclasses. All optional fields use `| None = None`.
- `src/invoice_etl/extract/pdf_extractor.py`
  - `extract_text_from_pdf(pdf_path: Path) -> list[str]` — uses `pdfplumber.open().pages[n].extract_text()`. Returns one string per page. No table extraction.
- `src/invoice_etl/transform/invoice_transformer.py`
  - 4 module-level regexes:
    - `_INVOICE_NUMBER_RE`: `r"(?i)invoice\s*[#no.:]+\s*([A-Z0-9\-]+")`  — matches `Invoice No. INV-2024-001` but NOT `Invoice Number: SOD00093649` (colon-label format).
    - `_DATE_RE`: `r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"` — defined but **never used** in `transform_pages()`.
    - `_AMOUNT_RE`: `r"(?i)(subtotal|tax|total)[^\d]*([\d,]+\.\d{2})"` — captures TOTAL but the SOD format uses `TOTAL: $17,865.06` which this matches via the `total` label.
    - `_CURRENCY_RE`: `r"\b(USD|EUR|CAD|GBP)\b"` — no currency code present in SOD format; will produce `None`.
  - `transform_pages()` does NOT create any `LineItem` objects. The `line_items` list is always empty.
  - `invoice_date`, `due_date`, `vendor_name`, `customer_name`, `customer_number` are never populated.
- `src/invoice_etl/load/db_loader.py`
  - `load_invoice(invoice: Invoice, engine: Engine | None = None) -> int`
  - Invoices INSERT: 12 named columns, parameters supplied by `invoice.model_dump(exclude={"line_items"})`. SQLAlchemy silently ignores extra dict keys not referenced in SQL — so adding new fields to `Invoice` is safe until the SQL itself is updated.
  - Line items INSERT: `invoice_id` + 4 columns, parameters supplied by `{"invoice_id": ..., **item.model_dump()}`. Same SQLAlchemy behaviour — new `LineItem` fields are silently ignored until SQL is updated.
  - `ON CONFLICT (invoice_number) DO NOTHING RETURNING id` — returns `-1` when invoice already exists.
- `docker/init.sql`
  - `invoices` table: 14 columns — `id SERIAL PK`, `invoice_number TEXT UNIQUE NOT NULL`, `invoice_date DATE`, `due_date DATE`, `vendor_name TEXT`, `vendor_address TEXT`, `customer_name TEXT`, `customer_address TEXT`, `currency CHAR(3)`, `subtotal NUMERIC(18,2)`, `tax_amount NUMERIC(18,2)`, `total_amount NUMERIC(18,2)`, `source_file TEXT`, `created_at TIMESTAMPTZ DEFAULT NOW()`.
  - `line_items` table: 7 columns — `id SERIAL PK`, `invoice_id INTEGER FK→invoices`, `description TEXT`, `quantity NUMERIC(18,4)`, `unit_price NUMERIC(18,4)`, `line_total NUMERIC(18,2)`, `created_at TIMESTAMPTZ DEFAULT NOW()`.
  - Schema is a fresh-init `CREATE TABLE IF NOT EXISTS` script; no migration framework. New columns must be added directly to the `CREATE TABLE` statements.
- `tests/test_transform.py`
  - 4 tests: invoice number parsing, total parsing, unknown invoice fallback, source_file propagation. None test SOD format, line items, or `customer_number`.
- `tests/test_load.py`
  - 2 tests via mocked `Engine`: returns correct invoice id, returns -1 on duplicate. Neither verifies specific column parameters passed to execute.
- `tests/test_extract.py`
  - 2 tests via mocked pdfplumber: FileNotFoundError on missing file, correct page text list on success.
- `pyproject.toml`
  - Python 3.12+, Pydantic v2, pdfplumber ^0.11, SQLAlchemy 2.x, psycopg2-binary. No new dependencies may be added per issue constraints.
  - Pyright `typeCheckingMode = "strict"` — full annotations and no `Any` without justification.
  - Black line-length 100, Ruff selects `E, F, I, UP, B, SIM`.

### Code Search Results

- `_INVOICE_NUMBER_RE` usage in `invoice_transformer.py`
  - Used once in `transform_pages()`. Does NOT match `Invoice Number: SOD00093649` because the SOD format uses `Invoice Number:` (with colon and no `#/no.` prefix), while the regex requires `[#no.:]+`.
- `model_dump` usage in `db_loader.py`
  - Two call sites: `invoice.model_dump(exclude={"line_items"})` and `item.model_dump()`. Both pass dict to SQLAlchemy `text()` named parameters. Extra keys in the dict are silently ignored.
- `extract_text` usage in `pdf_extractor.py`
  - Single call: `page.extract_text() or ""`. No table extraction (`extract_tables()`, `extract_table()`) is used anywhere in the codebase.

### Project Conventions

- Standards referenced: `general-code-change.instructions.md`, `python-code-change.instructions.md`, `python-unit-test.instructions.md`, `self-explanatory-code-commenting.instructions.md`, `general-unit-test.instructions.md`.
- Instructions followed:
  - No new third-party dependencies (confirmed by issue.md constraint).
  - All public functions and helpers require full docstrings (Google-style).
  - Type annotations required on all functions/methods. Pyright strict enforced.
  - Tests must be pure in-memory — no file I/O, no temp files.
  - Max 500 lines per production file.
  - `poetry run black . → poetry run ruff check → poetry run pyright → poetry run pytest` toolchain sequence required.
  - Coverage: new modules target ≥ 90%; repo-wide ≥ 80%.
  - New unit tests must achieve ≥ 80% branch coverage on new SOD parser logic (per issue.md).

---

## Key Discoveries

### Project Structure

- All ETL source code is under `src/invoice_etl/` with `extract/`, `transform/`, `load/`, `models/` sub-packages.
- Tests mirror source layout: `tests/test_extract.py`, `tests/test_transform.py`, `tests/test_load.py`.
- No test fixtures directory exists; test data is inline in test functions. All existing tests use in-memory mocks or literal strings — consistent with the no-temp-files constraint.
- `docker/init.sql` is the only schema definition. It is a create-if-not-exists script with no versioning.
- The existing `transform_pages()` function is the sole public transform entry point and is referenced in `tests/test_transform.py`. The acceptance criteria require it to handle SOD format, so it must be extended or dispatch to a SOD-specific parser.

### Implementation Patterns

- **Pydantic v2 optional fields**: All optional fields use `FieldType | None = None` syntax (not `Optional[FieldType]`), matching existing model style.
- **Date parsing**: Pydantic v2 accepts `datetime.date` objects directly. Date strings in `MM/DD/YYYY` format must be pre-converted to `datetime.date` using `datetime.datetime.strptime(s, "%m/%d/%Y").date()` before being assigned to model fields.
- **Decimal parsing**: The existing `_parse_decimal()` helper strips commas and converts to `Decimal`. It returns `None` on failure. Reuse this for all numeric fields in the SOD parser.
- **Logger pattern**: Each module uses `logger = logging.getLogger(__name__)` at module level. `logger.debug()` for transform details, `logger.warning()` for skipped/partial records, `logger.info()` for load completion.
- **SQLAlchemy named parameters**: `text()` SQL with `:param_name` syntax. Dict keys not referenced in SQL are silently ignored. Keys referenced in SQL but missing from the dict raise `sqlalchemy.exc.CompileError`.
- **model_dump() behavior**: With the new fields added to models, `model_dump()` and `model_dump(exclude={"line_items"})` will include the new fields automatically. The SQL INSERT statements must be updated to reference the new `:param` names.

### Complete Examples

```python
# SOD line item row format (from PDF facts):
# "5 01553 RGF POPCORN CHICKEN 00562 03/13/2026 545039 1 EA 5.9400 5.94"
# "6 60461 RGF DINO NUGGETS 20 OZ 00052 03/08/2026 545038 1 EA 4.9800 4.98"
#
# Column header: Item  Description  Store No  Str Ord Dt  Offer#  Qty  UOM  Unit Price  Amount
# Field mapping (9 columns):
#   col 1 (Item)         → item:             "01553"  (5-digit item/SKU code)
#   col 2 (Description)  → description:      "RGF POPCORN CHICKEN"
#   col 3 (Store No)     → store_number:     "00562"  (5-digit, zero-padded)
#   col 4 (Str Ord Dt)   → order_date:       date(2026, 3, 13)
#   col 5 (Offer#)       → offer_number:     "545039"
#   col 6 (Qty)          → quantity:         Decimal("1")
#   col 7 (UOM)          → unit_of_measure:  "EA"
#   col 8 (Unit Price)   → unit_price:       Decimal("5.9400")
#   col 9 (Amount)       → line_total:       Decimal("5.94")
#
# NOTE: the leading "5" / "6" is a per-page sequence counter (not in column header).
# It is consumed and discarded by the regex (matched but not captured).

_SOD_LINE_ITEM_RE = re.compile(
    r"^\d+\s+"                   # sequence counter (consumed, not captured)
    r"(\d{5})\s+"                # group 1: item code (5-digit)
    r"(.+?)\s+"                  # group 2: description (non-greedy, stops before store+date)
    r"(\d{5})\s+"                # group 3: store number (5-digit)
    r"(\d{2}/\d{2}/\d{4})\s+"   # group 4: order date MM/DD/YYYY
    r"(\d+)\s+"                  # group 5: offer number
    r"([\d.]+)\s+"               # group 6: quantity
    r"([A-Z]+)\s+"               # group 7: UOM (uppercase alpha)
    r"([\d.]+)\s+"               # group 8: unit price
    r"([\d.]+)\s*$",             # group 9: line total
    re.MULTILINE,
)

# Anchoring rationale: the MM/DD/YYYY date is the unambiguous anchor that separates
# the variable-length description from the fixed-suffix fields. The non-greedy (.+?)
# stops at the earliest (\d{5})\s+(\d{2}/\d{2}/\d{4}) match, which is the
# store_number + order_date pair. Numbers within descriptions (e.g., "20 OZ") will not
# be misidentified as store numbers because a 5-digit code followed immediately by a
# date is a distinguishing combination.
```

```python
# SOD header regex patterns (labeled fields in header table cell):
_SOD_INVOICE_NUMBER_RE = re.compile(r"Invoice Number:\s*(\S+)")
_SOD_INVOICE_DATE_RE   = re.compile(r"Invoice Date:\s*(\d{1,2}/\d{1,2}/\d{4})")
_SOD_CUSTOMER_NUMBER_RE = re.compile(r"Customer Number:\s*(\S+)")
_SOD_TOTAL_RE           = re.compile(r"TOTAL:\s*\$?([\d,]+\.\d{2})")

# Customer name: page 1 only — appears as two consecutive all-caps lines
# (contact person on first line, company on second). Capture the company name.
# Strategy: match two consecutive all-caps lines; second line is customer_name.
_SOD_CUSTOMER_NAME_BLOCK_RE = re.compile(
    r"^([A-Z][A-Z\s]+)\n([A-Z][A-Z\s]+(?:LLC|INC|CORP|CO|COMPANY)[A-Z\s]*)\s*$",
    re.MULTILINE,
)
# If the block regex fails (company suffix varies), fall back to extracting all
# consecutive all-caps lines and using the last one as customer_name.
```

```python
# Truncated-line merging (page boundary continuation):
# When a row is split across a page end, the partial row appears at end of page N
# (no date/amount) and the continuation appears at start of page N+1 (no item/SKU prefix).
#
# Detection heuristic:
#   - A line that starts with \d+\s+\d{5}\s+ (item counter + item code) but does NOT
#     contain a MM/DD/YYYY date pattern is a candidate truncated line.
#   - The next line that does NOT start with a digit is the continuation.
# Merge: concatenate with a single space.

def _merge_truncated_lines(lines: list[str]) -> list[str]:
    """Merge line-item rows split across PDF page boundaries.

    A row is identified as truncated when it begins with the item-counter
    and item-code prefix (``\\d+ \\d{5}``) but contains no date field.
    The immediately following line that does not start with a digit is
    treated as the continuation and is joined with a space.
    """
    _PARTIAL_ROW_RE = re.compile(r"^\d+\s+\d{5}\s+")
    _DATE_IN_LINE_RE = re.compile(r"\d{2}/\d{2}/\d{4}")
    merged: list[str] = []
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        stripped = line.strip()
        if not stripped:
            merged.append(stripped)
            continue
        # Check if this line is a truncated item row (has prefix but no date)
        is_partial = bool(_PARTIAL_ROW_RE.match(stripped)) and not bool(
            _DATE_IN_LINE_RE.search(stripped)
        )
        if is_partial and i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            # Continuation lines do not start with a digit (no item counter)
            if next_stripped and not next_stripped[0].isdigit():
                merged.append(stripped + " " + next_stripped)
                skip_next = True
                continue
        merged.append(stripped)
    return merged
```

```python
# transform_pages() dispatch strategy:
# Detect SOD format by checking for the labeled "Customer Number:" field,
# which is specific to this invoice template. Fall back to existing generic parsing
# if not detected.

def transform_pages(pages: list[str], source_file: str | None = None) -> Invoice:
    full_text = "\n".join(pages)
    if "Customer Number:" in full_text:
        return _transform_sod_pages(pages, source_file=source_file)
    # ... existing generic logic unchanged ...
```

### API and Schema Documentation

**New `LineItem` fields** (Pydantic v2 declaration):

```python
class LineItem(BaseModel):
    # Existing fields (unchanged)
    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    line_total: Decimal | None = None
    # New fields for SOD format
    item: str | None = None                   # 5-digit item/SKU code (zero-padded string)
    store_number: str | None = None           # 5-digit store code (zero-padded string)
    order_date: datetime.date | None = None   # store order date
    offer_number: str | None = None           # deal/offer identifier
    unit_of_measure: str | None = None        # e.g. "EA", "CS"
```

**New `Invoice` field** (Pydantic v2 declaration):

```python
class Invoice(BaseModel):
    # ... all existing fields unchanged ...
    customer_number: str | None = None        # e.g. "081997"
```

**Rationale for `str | None` over `int | None` for code fields**: `item`, `store_number`, `offer_number`, `customer_number` are identifier codes that carry zero-padding and must be preserved exactly (e.g., `"00562"` ≠ `562`). Storing as strings avoids silent precision loss and is consistent with how `invoice_number` is typed.

**Rationale for `datetime.date | None` for `order_date`**: Matches the type used by `invoice_date` and `due_date` in `Invoice`. Enables date arithmetic downstream. The MM/DD/YYYY string from the PDF is converted before model construction via `datetime.strptime(s, "%m/%d/%Y").date()`.

### Configuration Examples

**`docker/init.sql` — required column additions** (add to existing `CREATE TABLE IF NOT EXISTS` statements):

```sql
-- invoices table: add after customer_address column
customer_number TEXT,

-- line_items table: add after line_total column (before created_at)
item            TEXT,
store_number    TEXT,
order_date      DATE,
offer_number    TEXT,
unit_of_measure TEXT,
```

**`db_loader.py` — required SQL and dict additions**:

Invoices INSERT — add `customer_number` to column list and VALUES:
```sql
INSERT INTO invoices (
    invoice_number, invoice_date, due_date,
    vendor_name, vendor_address,
    customer_name, customer_address, customer_number,
    currency, subtotal, tax_amount, total_amount, source_file
) VALUES (
    :invoice_number, :invoice_date, :due_date,
    :vendor_name, :vendor_address,
    :customer_name, :customer_address, :customer_number,
    :currency, :subtotal, :tax_amount, :total_amount, :source_file
)
```
The parameter dict (`invoice.model_dump(exclude={"line_items"})`) automatically includes `customer_number` once the field is added to `Invoice` — no dict change required.

Line items INSERT — add 5 new columns and parameters:
```sql
INSERT INTO line_items (
    invoice_id, description, quantity, unit_price, line_total,
    item, store_number, order_date, offer_number, unit_of_measure
) VALUES (
    :invoice_id, :description, :quantity, :unit_price, :line_total,
    :item, :store_number, :order_date, :offer_number, :unit_of_measure
)
```
The parameter dict (`{"invoice_id": invoice_id, **item.model_dump()}`) automatically includes all new `LineItem` fields once they are added to the model — no dict change required.

### Technical Requirements

- **SOD invoice number regex**: The existing `_INVOICE_NUMBER_RE` (`r"(?i)invoice\s*[#no.:]+\s*([A-Z0-9\-]+"`) does NOT match `Invoice Number: SOD00093649` because `Number` is not in the `[#no.:]` character class. A SOD-specific regex `r"Invoice Number:\s*(\S+)"` is required.
- **`invoice_date` currently unpopulated**: The existing `_DATE_RE` is defined but never assigned in `transform_pages()`. The SOD parser must explicitly extract and assign `invoice_date` from `Invoice Date: MM/DD/YYYY`.
- **`total_amount` will parse from SOD text**: The existing `_AMOUNT_RE` matches `total` label. The SOD format has `TOTAL: $17,865.06`. The regex `r"(?i)(subtotal|tax|total)[^\d]*([\d,]+\.\d{2})"` will match `TOTAL: $17,865.06` via the `total` branch (the `$` is consumed by `[^\d]*`). So `total_amount` will be populated by the generic path if the SOD parser delegates appropriately.
- **No new dependencies**: All regex, `datetime`, `Decimal`, `re` stdlib usage. Pydantic v2, SQLAlchemy, pdfplumber are all already in `pyproject.toml`.
- **Pyright strict**: New function signatures, helper return types, and all Pydantic field additions must be fully annotated. `datetime.date` import already available via `import datetime` in `invoice.py`; must be added to `invoice_transformer.py` imports.
- **500-line file limit**: `invoice_transformer.py` is currently 62 lines. Adding the SOD parser (estimated ~100 lines including docstrings) stays well within the limit.

---

## Recommended Approach

**Extend `invoice_transformer.py` with a SOD-format sub-parser dispatched from the existing `transform_pages()` entry point.**

### Architecture

1. Add a `_transform_sod_pages(pages: list[str], source_file: str | None) -> Invoice` private function that handles all SOD-specific parsing.
2. At the top of `transform_pages()`, detect SOD format via `"Customer Number:" in "\n".join(pages)` and delegate to `_transform_sod_pages()` if detected.
3. The existing generic parsing path is unchanged — no regressions to existing tests.

### New private helpers in `invoice_transformer.py`

- `_parse_sod_header(text: str) -> dict[str, object]`: Applies SOD-specific header regexes; returns a dict of extracted fields (`invoice_number`, `invoice_date`, `customer_number`, `total_amount`, optionally `customer_name`).
- `_merge_truncated_lines(lines: list[str]) -> list[str]`: Merges page-boundary-split line item rows (see example above).
- `_parse_sod_line_item(line: str) -> LineItem | None`: Applies `_SOD_LINE_ITEM_RE` to one line; returns a `LineItem` or `None` if the line does not match (skips headers, blank lines, etc.).
- `_transform_sod_pages(pages: list[str], source_file: str | None) -> Invoice`: Orchestrates header parse from the first page, line collection from all pages, truncation merge, and line item parse.

### Change surface (files and required changes)

| File | Change |
|------|--------|
| `src/invoice_etl/models/invoice.py` | Add 5 fields to `LineItem`; add `customer_number` to `Invoice` |
| `src/invoice_etl/transform/invoice_transformer.py` | Add 4 new SOD-specific module-level regexes; add 4 private helper functions; add SOD dispatch to `transform_pages()` |
| `src/invoice_etl/load/db_loader.py` | Update invoices INSERT SQL (add `customer_number`); update line_items INSERT SQL (add 5 new columns) |
| `docker/init.sql` | Add `customer_number TEXT` to `invoices` CREATE TABLE; add 5 new columns to `line_items` CREATE TABLE |
| `tests/test_transform.py` | Add 5+ new test functions for SOD header, line item row, multi-page, truncation; existing 4 tests unchanged |
| `tests/test_load.py` | Add 1 new test asserting that `execute` is called with the new `customer_number` and line item column parameters |

### Rejected alternatives

- **pdfplumber table extraction (`extract_tables()`)**: The PDF facts describe line items as fused into a single table cell, meaning even table mode does not yield individual per-row cells. Table extraction would add complexity to `pdf_extractor.py` (a new return type or separate function) without enabling cleaner parsing. Regex on `extract_text()` output is sufficient and avoids changing the extractor interface or adding a parallel extraction path.
- **Separate `transform_sod_pages()` public function**: Adding a new public entry point would require callers to know which function to call, complicating the interface. Dispatching from `transform_pages()` via format detection keeps the public API stable and satisfies the acceptance criterion that `transform_pages()` itself handles SOD format.

---

## Implementation Guidance

- **Objectives**:
  - Populate `Invoice.customer_number` and all 5 new `LineItem` fields from SOD PDF text.
  - Persist all new fields to the database via `load_invoice()`.
  - All 8 acceptance criteria in `issue.md` must pass.
  - Full toolchain (Black → Ruff → Pyright strict → pytest) must pass without errors.

- **Key Tasks**:
  1. Update `models/invoice.py` — add `customer_number` to `Invoice`; add `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure` to `LineItem`. Add `import datetime` if not already present (it is).
  2. Update `invoice_transformer.py` — add 4 module-level SOD regexes; implement `_parse_sod_header`, `_merge_truncated_lines`, `_parse_sod_line_item`, `_transform_sod_pages`; add SOD dispatch at top of `transform_pages()`.
  3. Update `db_loader.py` — update both INSERT SQL statements to include the new columns.
  4. Update `docker/init.sql` — add new columns to both CREATE TABLE statements.
  5. Add tests to `tests/test_transform.py` — cover SOD header parsing, 3-line item block, multi-page accumulation, truncated-row handling, format detection dispatch, unknown/non-SOD fallback regression.
  6. Add test to `tests/test_load.py` — verify `execute` receives correct new column parameters using `mock_conn.execute.call_args_list`.
  7. Run full toolchain and confirm all steps pass.

- **Dependencies**: None new. All required stdlib and project libraries are already present.

- **Success Criteria**:
  - `transform_pages([page1_sod_text])` returns `Invoice` with `invoice_number="SOD00093649"`, `customer_number="081997"`, `invoice_date=date(2026, 3, 16)`, and non-empty `line_items` with all 9 fields populated.
  - `transform_pages(["No structured data here."])` still returns `invoice_number="UNKNOWN"` (no regression).
  - `load_invoice(invoice_with_new_fields)` calls execute with `:customer_number` in the invoices statement and `:item`, `:store_number`, `:order_date`, `:offer_number`, `:unit_of_measure` in the line_items statement.
  - `docker/init.sql` `CREATE TABLE line_items` includes the 5 new columns; `CREATE TABLE invoices` includes `customer_number`.
  - `poetry run pytest --cov=src` reports ≥ 80% coverage on `invoice_transformer.py` and ≥ 70% overall.
  - `poetry run pyright` exits 0 with no errors.

- **Test cases** (all in-memory, no file I/O, no temp files):

  | Test name | Input | Expected output |
  |-----------|-------|-----------------|
  | `test_sod_transform_parses_header` | Page 1 text containing `Invoice Number: SOD00093649`, `Invoice Date: 03/16/2026`, `Customer Number: 081997` | `invoice.invoice_number == "SOD00093649"`, `invoice.customer_number == "081997"`, `invoice.invoice_date == date(2026, 3, 16)` |
  | `test_sod_transform_parses_line_items` | Single page with 3 complete line item rows | `len(invoice.line_items) == 3`; first item: `item="01553"`, `description="RGF POPCORN CHICKEN"`, `store_number="00562"`, `order_date=date(2026,3,13)`, `offer_number="545039"`, `quantity=Decimal("1")`, `unit_of_measure="EA"`, `unit_price=Decimal("5.9400")`, `line_total=Decimal("5.94")` |
  | `test_sod_transform_multi_page_accumulation` | Two pages each containing 2 line item rows | `len(invoice.line_items) == 4`; no duplicate header fields |
  | `test_sod_transform_truncated_row_handled_gracefully` | Page ending with `1 01553 RGF POPCORN CHIC` (no date), next page starting with `KEN 00562 03/13/2026 545039 1 EA 5.9400 5.94` | No exception raised; either 1 line item parsed (merged row) or 0 (graceful skip) depending on merge logic |
  | `test_sod_transform_does_not_regress_generic_path` | `["Invoice No. INV-2024-001\nTotal: 1,200.00"]` (existing test input) | `invoice.invoice_number == "INV-2024-001"`, `invoice.total_amount == Decimal("1200.00")` |
  | `test_load_invoice_persists_new_fields` | `Invoice` with `customer_number="081997"` and `LineItem` with all 5 new fields set | `mock_conn.execute` first call SQL contains `:customer_number`; second call SQL contains `:item`, `:store_number`, `:order_date`, `:offer_number`, `:unit_of_measure` |
