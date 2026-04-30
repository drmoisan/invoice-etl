# sod-invoice-ingestion (Issue #1)

- Date captured: 2026-04-30
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/sod-invoice-ingestion/ (Issue #1)

- Issue: #1
- Issue URL: https://github.com/drmoisan/invoice-etl/issues/1
- Last Updated: 2026-04-30
- Work Mode: full-feature

## Problem / Why

The existing ETL pipeline extracts a generic set of invoice fields (invoice number, dates, totals, basic line item description/qty/price). The sample document `artifacts/SOD00093649.pdf` is a 40-page HEB Store Order Deal invoice with a fixed-width columnar line-item format that includes domain-specific fields not currently modelled: Item code, Store Number, Order Date, Offer Number, and Unit of Measure. Additionally, Customer Number is present in the invoice header but not extracted or stored. Without this work the pipeline silently discards these fields, making the stored data incomplete for downstream reconciliation.

## Proposed Behavior

- Parse header fields from the SOD invoice format: Invoice Number, Invoice Date, Customer Name, Customer Number.
- Parse every line item row across all 40 pages with the following columns: Item (item code), Description, Store Number, Store Order Date, Offer Number, Quantity, Unit of Measure (UOM), Unit Price, Amount.
- Extend the `LineItem` Pydantic model to carry the new line-item fields.
- Extend the `Invoice` Pydantic model to carry `customer_number`.
- Update `docker/init.sql` (schema migration): add new columns to `line_items`; add `customer_number` to `invoices`.
- Update `db_loader.py` to persist all new fields.
- Update `invoice_transformer.py` with a SOD-format parser that handles the multi-page, fixed-width line-item layout produced by pdfplumber text extraction.
- All changes must pass the full toolchain: Black → Ruff → Pyright strict → pytest ≥ 70% coverage.

## Acceptance Criteria (early draft)

- [x] `LineItem` model includes: `item`, `store_number`, `order_date`, `offer_number`, `unit_of_measure` fields with correct types.
- [x] `Invoice` model includes: `customer_number` field.
- [x] `transform_pages()` correctly parses line items from `SOD00093649.pdf` text, returning all per-row fields.
- [x] `load_invoice()` persists the new `LineItem` and `Invoice` fields to the database.
- [x] `docker/init.sql` schema includes updated `line_items` and `invoices` column definitions.
- [x] All existing tests continue to pass (zero regressions).
- [x] New unit tests cover the SOD transformer with ≥ 80% branch coverage on the new parser logic.
- [x] Full toolchain (Black + Ruff + Pyright strict + pytest) passes without errors.

## Constraints & Risks

- The line-item rows are fused into a single table cell by pdfplumber (not split into individual columns). The parser must use regex or positional splitting on the extracted text string.
- Page continuation: header fields repeat on every page; line items accumulate across all 40 pages. The parser must deduplicate header reads and concatenate line items.
- Existing `Invoice`/`LineItem` models are referenced by existing tests. Any schema change must be backward-compatible or all affected tests updated.
- `docker/init.sql` is a fresh-init script (no migration framework). If a live database exists, manual column addition is required.
- No new third-party dependencies should be introduced.

## Test Conditions to Consider

- [ ] Unit test: parse a representative 3-line SOD text block and assert all 9 fields per row.
- [ ] Unit test: header extraction returns correct Invoice Number, Invoice Date, Customer Number, Customer Name from SOD page 1 text.
- [ ] Unit test: multi-page accumulation — two pages of line items produce correct combined count.
- [ ] Unit test: `load_invoice()` with new fields calls execute with correct parameters.
- [ ] Edge case: last row on a page truncated mid-text (observed in PDF: "501553 RGF POPCORN CHIC") — parser handles gracefully.

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/sod-invoice-ingestion/` folder from the template